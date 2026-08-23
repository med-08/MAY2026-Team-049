import calendar
import json
from datetime import date, datetime
from flask import jsonify, request, session, send_from_directory, current_app
from student import student_bp
from database import db
from models import (
    Student, Parent, Tutor, Subject, StudentSubject, Session, SessionUpdate,
    SessionBooking, Quiz, QuizQuestion, QuizAttempt, Assignment,
    AssignmentSubmission, StudyTip, StudyResource, FAQ, LearningProgress,
    MeetingRequest, Notification, Doubt, Message, AttendanceRecord,
    FlashcardSet, Flashcard
)
from decorators import student_required
from utils import decode_jwt_token
from schedule import meeting_lifecycle, _local_now
from werkzeug.security import check_password_hash, generate_password_hash
from ai_service import AIConfigError, AIResponseError, AIServiceError, generate_text


def ok(data=None, message=None, status=200, meta=None):
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def fail(message, status=400):
    return jsonify({"success": False, "message": message}), status


def current_student():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        payload = decode_jwt_token(auth.split(" ", 1)[1])
        if payload and payload.get("role") == "Student":
            student = db.session.get(Student, payload.get("user_id"))
            if student:
                return student

    user_id = session.get("user_id")
    if user_id and session.get("role") == "Student":
        return db.session.get(Student, user_id)

    return None


def subject_name(subject_id):
    obj = db.session.get(Subject, subject_id)
    return obj.subject_name if obj else "General"


def enrolled_subject_ids(student_id):
    """Return the exact subjects selected by this student at registration."""
    return {
        row.subject_id
        for row in StudentSubject.query.filter_by(
            student_id=student_id
        ).all()
    }


def student_can_access_quiz(student_id, quiz):
    if not quiz:
        return False

    if quiz.assigned_student_id is not None:
        return quiz.assigned_student_id == student_id

    enrolled = StudentSubject.query.filter_by(
        student_id=student_id,
        subject_id=quiz.subject_id
    ).first()

    return enrolled is not None


def quiz_topic(quiz):
    return (getattr(quiz, "topic", None) or quiz.title or "General").strip()


def answer_label(question, option):
    return {
        "A": question.option_a,
        "B": question.option_b,
        "C": question.option_c,
        "D": question.option_d,
    }.get(str(option or "").strip().upper(), "")


def attempt_review(attempt):
    try:
        data = json.loads(attempt.review_json or "[]")
        return data if isinstance(data, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def assigned_student_quizzes(student_id):
    return [
        quiz
        for quiz in Quiz.query.order_by(Quiz.created_at.desc()).all()
        if student_can_access_quiz(student_id, quiz)
    ]


def build_performance_context(student):
    attempts = (
        QuizAttempt.query
        .filter_by(student_id=student.student_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )

    quiz_attempts = []
    topic_stats = {}
    missed = []

    for attempt in attempts:
        quiz = db.session.get(Quiz, attempt.quiz_id)
        if not quiz:
            continue
        topic = quiz_topic(quiz)
        subject = subject_name(quiz.subject_id)
        total = attempt.total_questions
        correct = attempt.correct_count
        if total is None:
            total = QuizQuestion.query.filter_by(quiz_id=quiz.quiz_id).count()
        if correct is None and attempt.score is not None and total:
            correct = round((float(attempt.score) / 100) * total)

        score = float(attempt.score or 0)
        stat = topic_stats.setdefault(topic, {
            "topic": topic,
            "subject": subject,
            "attempts": 0,
            "totalScore": 0,
            "correct": 0,
            "totalQuestions": 0,
            "missed": [],
        })
        stat["attempts"] += 1
        stat["totalScore"] += score
        stat["correct"] += int(correct or 0)
        stat["totalQuestions"] += int(total or 0)

        review = attempt_review(attempt)
        wrong = [item for item in review if not item.get("is_correct")]
        for item in wrong:
            missed_item = {
                "quiz": quiz.title,
                "subject": subject,
                "topic": topic,
                "question": item.get("question"),
                "studentAnswer": item.get("selected_label") or item.get("selected"),
                "correctAnswer": item.get("correct_label") or item.get("correct_option"),
                "concept": item.get("explanation") or topic,
            }
            missed.append(missed_item)
            stat["missed"].append(missed_item)

        quiz_attempts.append({
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "subject": subject,
            "topic": topic,
            "difficulty": quiz.difficulty,
            "score": score,
            "correctCount": correct,
            "totalQuestions": total,
            "attempted_at": attempt.attempted_at.isoformat() if attempt.attempted_at else None,
            "incorrect": wrong,
        })

    topic_performance = []
    for stat in topic_stats.values():
        avg = stat["totalScore"] / stat["attempts"] if stat["attempts"] else 0
        if stat["attempts"] < 1:
            status = "Not enough data"
        elif avg >= 80:
            status = "Strong"
        elif avg >= 55:
            status = "Needs Practice"
        else:
            status = "Needs Improvement"
        topic_performance.append({
            "topic": stat["topic"],
            "subject": stat["subject"],
            "attempts": stat["attempts"],
            "averageScore": round(avg, 2),
            "correctCount": stat["correct"],
            "totalQuestions": stat["totalQuestions"],
            "status": status,
            "missed": stat["missed"][:5],
        })

    topic_performance.sort(key=lambda item: item["averageScore"])
    scores = [item["score"] for item in quiz_attempts if item["score"] is not None]
    strong = [item for item in topic_performance if item["status"] == "Strong"]
    weak = [item for item in topic_performance if item["status"] == "Needs Improvement"]
    practice = [item for item in topic_performance if item["status"] == "Needs Practice"]

    recommendations = []
    for item in weak + practice:
        missed_concepts = [
            m["concept"]
            for m in item["missed"]
            if m.get("concept")
        ]
        recommendations.append({
            "topic": item["topic"],
            "subject": item["subject"],
            "nextStep": f"Review the flashcards for {item['topic']} and attempt another short quiz.",
            "revise": missed_concepts[:3] or [item["topic"]],
        })

    if not quiz_attempts:
        summary = "Not enough data yet - complete more quizzes to get a reliable insight."
    else:
        summary = (
            f"Your overall quiz average is {round(sum(scores) / len(scores))}% "
            f"across {len(scores)} completed quiz{'zes' if len(scores) != 1 else ''}."
        )

    return {
        "student_id": student.student_id,
        "overall": {
            "completedQuizzes": len(quiz_attempts),
            "averageScore": round(sum(scores) / len(scores), 2) if scores else None,
            "summary": summary,
        },
        "recentQuizPerformance": quiz_attempts[:5],
        "topicPerformance": topic_performance,
        "strongTopics": strong,
        "weakTopics": weak,
        "practiceTopics": practice,
        "missedQuestions": missed[:10],
        "recommendations": recommendations[:5],
        "hasEnoughData": bool(quiz_attempts),
    }


def render_performance_text(context):
    if not context["hasEnoughData"]:
        return context["overall"]["summary"]

    lines = [
        "Your Performance",
        f"Overall score: {round(context['overall']['averageScore'])}%",
        "",
    ]
    if context["strongTopics"]:
        lines.append("Topics you are strong in:")
        lines.extend([f"- {x['subject']} - {x['topic']} ({round(x['averageScore'])}%)" for x in context["strongTopics"]])
    if context["weakTopics"] or context["practiceTopics"]:
        lines.append("")
        lines.append("Topics to revise:")
        lines.extend([f"- {x['subject']} - {x['topic']}: {x['status']}" for x in context["weakTopics"] + context["practiceTopics"]])
    if context["missedQuestions"]:
        lines.append("")
        lines.append("What you got wrong:")
        for item in context["missedQuestions"][:4]:
            lines.append(f"- {item['topic']}: {item['question']} Correct answer: {item['correctAnswer']}")
    if context["recommendations"]:
        lines.append("")
        lines.append("Suggested next step:")
        lines.append(f"- {context['recommendations'][0]['nextStep']}")
    return "\n".join(lines)


def performance_chat_fallback(message, context):
    text = message.lower()
    if not context["hasEnoughData"]:
        return (
            "I do not have enough quiz data yet to say what you missed. "
            "Complete an assigned quiz first, then I can explain your score, "
            "wrong answers, and what to revise."
        )

    if "miss" in text or "wrong" in text:
        missed = context["missedQuestions"]
        if not missed:
            return "You did not miss any saved quiz questions in the latest data I can see. Nice work. Want to review your strongest topic?"
        first = missed[0]
        return (
            f"In {first['topic']}, you missed: {first['question']} "
            f"The correct answer was {first['correctAnswer']}. "
            f"Revise {first['concept']} and try one more short practice question."
        )

    if "weak" in text or "improve" in text or "study" in text:
        topic = (context["weakTopics"] or context["practiceTopics"] or context["topicPerformance"])[0]
        return (
            f"Focus on {topic['subject']} - {topic['topic']}. "
            f"Your average there is {round(topic['averageScore'])}%, marked as {topic['status']}. "
            f"Review the flashcards for {topic['topic']} and then attempt another quiz."
        )

    if "good" in text or "strong" in text:
        if not context["strongTopics"]:
            return "I do not have a strong-topic label yet. Complete a few more quizzes so I can be more reliable."
        topic = context["strongTopics"][0]
        return f"You are strongest in {topic['subject']} - {topic['topic']} with an average of {round(topic['averageScore'])}%."

    return render_performance_text(context)


def session_json(sess, booking_status=None):
    """
    Serialize an existing Session for the student dashboard.

    IMPORTANT:
    This function intentionally does NOT use MeetingRequest.
    A Session is already the source of truth for booked/scheduled
    class sessions.
    """

    tutor = (
        db.session.get(Tutor, sess.tutor_id)
        if sess.tutor_id
        else None
    )

    subject = (
        db.session.get(Subject, sess.subject_id)
        if sess.subject_id
        else None
    )

    update = SessionUpdate.query.filter_by(
        session_id=sess.session_id
    ).first()

    # Safe date formatting
    session_date = sess.session_date

    date_display = (
        session_date.strftime("%d %b %Y")
        if session_date
        else None
    )

    date_iso = (
        session_date.isoformat()
        if session_date
        else None
    )

    # Safe time formatting
    start_time = sess.start_time
    end_time = sess.end_time

    start_display = (
        start_time.strftime("%I:%M %p")
        if start_time
        else None
    )

    start_time_value = (
        start_time.strftime("%H:%M")
        if start_time
        else None
    )

    end_time_value = (
        end_time.strftime("%H:%M")
        if end_time
        else None
    )

    # Calculate duration safely
    duration = None

    if start_time and end_time:
        start_dt = datetime.combine(
            date.today(),
            start_time
        )

        end_dt = datetime.combine(
            date.today(),
            end_time
        )

        duration_seconds = (
            end_dt - start_dt
        ).total_seconds()

        # Handle sessions that cross midnight
        if duration_seconds < 0:
            duration_seconds += 24 * 60 * 60

        duration_minutes = max(
            1,
            int(duration_seconds // 60)
        )

        duration = f"{duration_minutes} min"

    return {
        "id": sess.session_id,
        "session_id": sess.session_id,

        "subject": (
            subject.subject_name
            if subject
            else "General"
        ),

        "tutor": (
            tutor.tutor_name
            if tutor
            else "Tutor"
        ),

        "tutor_id": sess.tutor_id,

        "type": (
            sess.session_type
            if sess.session_type
            else "Regular"
        ),

        "date": date_display,
        "date_iso": date_iso,

        "time": start_display,
        "start_time": start_time_value,
        "end_time": end_time_value,

        "duration": duration,

        "status": sess.status,

        "booking_status": booking_status,

        "meeting_url": sess.meeting_url,
        "meetingUrl": sess.meeting_url,

        # Keep the persisted Session status for backward compatibility, while
        # exposing the single authoritative meeting lifecycle used by the
        # Tutor/Parent flows.  This prevents stale "Meeting Not Started"
        # labels after the tutor has started the meeting.
        "meeting_lifecycle": meeting_lifecycle(sess)["status"],
        "can_join": meeting_lifecycle(sess)["can_join"],
        "can_start": meeting_lifecycle(sess)["can_start"],
        "can_end": meeting_lifecycle(sess)["can_end"],
        "meeting_started_at": (
            sess.meeting_started_at.isoformat()
            if sess.meeting_started_at else None
        ),
        "meeting_ended_at": (
            sess.meeting_ended_at.isoformat()
            if sess.meeting_ended_at else None
        ),
        "meeting_duration_seconds": sess.meeting_duration_seconds,

        "topics": (
            [
                x.strip()
                for x in (update.topics_covered or "").split(",")
                if x.strip()
            ]
            if update
            else []
        ),

        "homework": (
            update.homework_assigned
            if update
            else None
        ),
    }


def homework_status(submission, due_date):
    """
    Simple, meaningful homework status.

    Values:
      - Done
      - Due Passed
      - Due Today
      - Pending
    """

    if submission and submission.status in (
        "Completed",
        "Submitted",
        "Done"
    ):
        return "Done"

    today = date.today()

    if due_date:
        if due_date < today:
            return "Due Passed"

        if due_date == today:
            return "Due Today"

    return "Pending"


def assignment_json(assignment, student_id):
    sess = db.session.get(
        Session,
        assignment.session_id
    )

    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.assignment_id,
        student_id=student_id
    ).first()

    return {
        "id": assignment.assignment_id,
        "assignment_id": assignment.assignment_id,
        "title": assignment.title,
        "description": assignment.description or "",

        "subject": (
            subject_name(sess.subject_id)
            if sess
            else "General"
        ),

        "session_id": assignment.session_id,

        "dueDate": (
            assignment.due_date.strftime("%d %b %Y")
            if assignment.due_date
            else None
        ),

        "due_date": (
            assignment.due_date.isoformat()
            if assignment.due_date
            else None
        ),

        "status": (
            submission.status
            if submission
            else "Not Started"
        ),

        "homeworkStatus": homework_status(
            submission,
            assignment.due_date
        ),

        "progress": (
            submission.progress_percentage
            if submission
            else 0
        ),

        "submissionDate": (
            submission.submission_date.strftime(
                "%d %b %Y %I:%M %p"
            )
            if submission and submission.submission_date
            else None
        ),

        "feedback": (
            submission.tutor_feedback
            if submission
            else ""
        ),

        "canComplete": not (
            submission
            and submission.status in (
                "Completed",
                "Submitted",
                "Done"
            )
        ),
    }


@student_bp.route('/dashboard', methods=['GET'])
@student_required
def dashboard():
    student = current_student()

    if not student:
        return fail(
            "Student not found or not logged in",
            404
        )

    sid = student.student_id

    enrolled_subjects = enrolled_subject_ids(sid)

    bookings = SessionBooking.query.filter_by(
        student_id=sid
    ).join(Session).all()

    booking_rows = [
        (b, db.session.get(Session, b.session_id))
        for b in bookings
    ]

    booking_rows = [
        (b, sess)
        for b, sess in booking_rows
        if sess is not None
        and sess.subject_id in enrolled_subjects
    ]

    upcoming = [
        (b, sess)
        for b, sess in booking_rows
        if sess.status in ("Scheduled", "Rescheduled")
        and sess.session_date >= date.today()
    ]

    completed = [
        (b, sess)
        for b, sess in booking_rows
        if sess.status == "Completed"
    ]

    attempts = QuizAttempt.query.filter_by(
        student_id=sid
    ).all()

    scores = [
        float(a.score)
        for a in attempts
        if a.score is not None
    ]

    avg = (
        round(sum(scores) / len(scores))
        if scores
        else 0
    )

    pending = AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == sid,
        AssignmentSubmission.status.in_(
            ["Pending", "In Progress", "Late"]
        )
    ).count()

    recent = sorted(
        [
            a
            for a in attempts
            if a.attempted_at
        ],
        key=lambda x: x.attempted_at,
        reverse=True
    )[:6]

    weekly = {
        "labels": [
            f"Quiz {i + 1}"
            for i in range(len(recent))
        ][::-1],

        "data": [
            round(float(a.score))
            for a in recent
            if a.score is not None
        ][::-1],
    }

    subject_scores = {}

    for attempt in attempts:
        if attempt.score is None:
            continue

        quiz = db.session.get(
            Quiz,
            attempt.quiz_id
        )

        if quiz:
            subject_scores.setdefault(
                subject_name(quiz.subject_id),
                []
            ).append(float(attempt.score))

    next_booking = (
        sorted(
            upcoming,
            key=lambda row: (
                row[1].session_date,
                row[1].start_time
            )
        )[0]
        if upcoming
        else None
    )

    next_session = (
        session_json(
            next_booking[1],
            next_booking[0].booking_status
        )
        if next_booking
        else {}
    )

    tasks = []

    for sub in AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == sid,
        AssignmentSubmission.status.in_(
            ["Pending", "In Progress", "Late"]
        )
    ).all():

        assignment = db.session.get(
            Assignment,
            sub.assignment_id
        )

        if assignment:
            a = assignment_json(
                assignment,
                sid
            )

            tasks.append({
                "id": a["assignment_id"],
                "subject": a["subject"],
                "task": a["title"],
                "time": (
                    a["dueDate"]
                    or "No due date"
                ),
                "status": a["status"],
            })

    tasks.sort(
        key=lambda x: x["time"] or ""
    )

    meetings = []

    for m in MeetingRequest.query.filter_by(
        student_id=sid
    ).order_by(
        MeetingRequest.meeting_date.asc()
    ).limit(5).all():

        tutor = db.session.get(
            Tutor,
            m.tutor_id
        )

        sess = db.session.get(Session, m.session_id) if m.session_id else None
        lifecycle = meeting_lifecycle(sess) if sess else {
            "status": "Meeting Not Started", "can_join": False,
            "can_start": False, "can_end": False,
        }
        link = (sess.meeting_url if sess and sess.meeting_url else m.meeting_link)
        if m.status == "Pending Approval":
            lifecycle = {**lifecycle, "status": "Awaiting Tutor Approval", "can_join": False}
        elif (m.status == "Scheduled" and sess and sess.session_type == "One-to-One"
              and link and lifecycle["status"] == "Meeting Not Started"):
            lifecycle = {**lifecycle, "status": "Request Accepted", "can_join": True}
        meetings.append({
            "id": m.meeting_id,
            "meeting_id": m.meeting_id,
            "session_id": m.session_id,
            "date": m.meeting_date.isoformat() if m.meeting_date else None,
            "tutor": tutor.tutor_name if tutor else "Tutor",
            "tutor_id": m.tutor_id,
            "link": link,
            "reason": m.meeting_reason,
            "status": m.status,
            "meeting_lifecycle": lifecycle["status"],
            "can_join": lifecycle["can_join"],
            "meeting_type": sess.session_type if sess else "One-to-One",
        })

    return ok(
        {
            "student": {
                "student_id": sid,
                "name": student.student_name,
                "email": student.email,
                "school": student.school,
            },

            "summaryStats": [
                {
                    "key": "upcoming",
                    "label": "Upcoming Sessions",
                    "value": len(upcoming),
                    "subtitle": "Booked sessions",
                    "icon": "CalendarDaysIcon",
                    "tone": "blue",
                },
                {
                    "key": "completed",
                    "label": "Completed Sessions",
                    "value": len(completed),
                    "subtitle": "Your history",
                    "icon": "CheckCircleIcon",
                    "tone": "green",
                },
                {
                    "key": "quizAvg",
                    "label": "Quiz Average",
                    "value": f"{avg}%",
                    "subtitle": "All attempts",
                    "icon": "ChartBarIcon",
                    "tone": "green",
                },
                {
                    "key": "homework",
                    "label": "Homework Pending",
                    "value": pending,
                    "subtitle": "Assignments",
                    "icon": "ClipboardDocumentListIcon",
                    "tone": "amber",
                },
            ],

            "weeklyQuizProgress": weekly,

            "subjectQuizScores": {
                "labels": list(subject_scores),
                "data": [
                    round(sum(v) / len(v))
                    for v in subject_scores.values()
                ],
            },

            "nextSession": next_session,
            "todaysTasks": tasks,
            "meetings": meetings,
        },
        meta={"total": len(tasks)}
    )


@student_bp.route('/progress', methods=['GET'])
@student_required
def progress():
    student = current_student()

    if not student:
        return fail(
            "Student not found",
            404
        )

    records = LearningProgress.query.filter_by(
        student_id=student.student_id
    ).all()

    completed = [
        r
        for r in records
        if r.session_completion_status == "Completed"
    ]

    pace_counts = {}

    for r in records:
        if r.learning_pace:
            pace_counts[r.learning_pace] = (
                pace_counts.get(
                    r.learning_pace,
                    0
                ) + 1
            )

    return ok(
        {
            "growthMetrics": [
                {
                    "label": k,
                    "value": v
                }
                for k, v in pace_counts.items()
            ],

            "completedTopics": [
                {
                    "id": r.progress_id,
                    "sessionId": r.session_id,
                    "status": r.session_completion_status,
                    "pace": r.learning_pace,
                    "remarks": r.tutor_remarks,
                }
                for r in records
            ],

            "completedCount": len(completed),
        },
        meta={"total": len(records)}
    )


@student_bp.route('/faqs', methods=['GET'])
@student_required
def faqs():
    q = (
        request.args.get("q")
        or ""
    ).strip().lower()

    query = FAQ.query.order_by(
        FAQ.faq_id.desc()
    )

    items = []

    for f in query.all():

        if (
            q
            and q not in f.question.lower()
            and q not in f.answer.lower()
        ):
            continue

        items.append({
            "id": f.faq_id,
            "faq_id": f.faq_id,
            "q": f.question,
            "a": f.answer,
            "category": f.category or "General",
        })

    return ok(
        {"faqs": items},
        meta={"total": len(items)}
    )


@student_bp.route('/quizzes', methods=['GET'])
@student_required
def quizzes():
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    enrolled = {
        x.subject_id
        for x in StudentSubject.query.filter_by(
            student_id=student.student_id
        ).all()
    }

    qs = assigned_student_quizzes(student.student_id)

    items = []

    for q in qs:

        if q.assigned_student_id is None and enrolled and q.subject_id not in enrolled:
            continue

        if not student_can_access_quiz(student.student_id, q):
            continue

        attempt = QuizAttempt.query.filter_by(
            quiz_id=q.quiz_id,
            student_id=student.student_id
        ).first()

        items.append({
            "quiz_id": q.quiz_id,
            "subject": subject_name(q.subject_id),
            "title": q.title,
            "topic": quiz_topic(q),
            "difficulty": q.difficulty or "Not set",
            "weekNumber": q.week_number,
            "lastAttempt": (
                attempt.attempted_at.strftime(
                    "%d %b %Y"
                )
                if attempt and attempt.attempted_at
                else None
            ),
            "score": (
                round(float(attempt.score))
                if attempt and attempt.score is not None
                else None
            ),
        })

    return ok(
        {"quizzes": items},
        meta={"total": len(items)}
    )


@student_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@student_required
def quiz_details(quiz_id):
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    quiz = db.session.get(
        Quiz,
        quiz_id
    )

    if not quiz:
        return fail(
            "Quiz not found",
            404
        )

    if not student_can_access_quiz(student.student_id, quiz):
        return fail(
            "You are not assigned to this quiz",
            403
        )

    questions = QuizQuestion.query.filter_by(
        quiz_id=quiz_id
    ).order_by(
        QuizQuestion.question_id
    ).all()

    attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        student_id=student.student_id
    ).first()

    return ok(
        {
            "quiz": {
                "quiz_id": quiz.quiz_id,
                "title": quiz.title,
                "subject": subject_name(
                    quiz.subject_id
                ),
                "topic": quiz_topic(quiz),
                "difficulty": quiz.difficulty or "Not set",
                "weekNumber": quiz.week_number,
            },

            "questions": [
                {
                    "id": q.question_id,
                    "question": q.question,
                    "options": [
                        q.option_a,
                        q.option_b,
                        q.option_c,
                        q.option_d,
                    ],
                }
                for q in questions
            ],

            "attempt": (
                {
                    "score": round(float(attempt.score or 0), 2),
                    "correctCount": attempt.correct_count,
                    "totalQuestions": attempt.total_questions,
                    "review": attempt_review(attempt),
                    "attemptedAt": attempt.attempted_at.isoformat() if attempt.attempted_at else None,
                }
                if attempt
                else None
            ),
        },
        meta={"total": len(questions)}
    )


@student_bp.route(
    '/quizzes/<int:quiz_id>/submit',
    methods=['POST']
)
@student_required
def submit_quiz(quiz_id):
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    quiz = db.session.get(
        Quiz,
        quiz_id
    )

    if not quiz:
        return fail(
            "Quiz not found",
            404
        )

    if not student_can_access_quiz(student.student_id, quiz):
        return fail(
            "You are not assigned to this quiz",
            403
        )

    if QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        student_id=student.student_id
    ).first():
        return fail(
            "You have already attempted this quiz",
            409
        )

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return fail("Invalid quiz submission payload", 400)
    answers = payload.get("answers") or {}

    questions = QuizQuestion.query.filter_by(
        quiz_id=quiz_id
    ).order_by(
        QuizQuestion.question_id
    ).all()

    if not questions:
        return fail(
            "This quiz has no questions yet",
            400
        )

    correct = 0
    review = []

    for q in questions:

        answer = answers.get(
            str(q.question_id),
            answers.get(q.question_id)
        )
        selected = str(answer or "").strip().upper()
        expected = str(q.correct_option or "").strip().upper()
        is_correct = bool(selected and selected == expected)

        if is_correct:
            correct += 1

        review.append({
            "id": q.question_id,
            "question": q.question,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d,
            },
            "selected": selected or None,
            "selected_label": answer_label(q, selected),
            "correct_option": expected,
            "correct_label": answer_label(q, expected),
            "is_correct": is_correct,
            "explanation": q.explanation or "",
        })

    score = round(
        (correct / len(questions)) * 100,
        2
    )

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student.student_id,
        score=score,
        correct_count=correct,
        total_questions=len(questions),
        answers_json=json.dumps(answers),
        review_json=json.dumps(review),
    )

    db.session.add(attempt)
    db.session.commit()

    return ok(
        {
            "score": score,
            "correctCount": correct,
            "totalQuestions": len(questions),
            "review": review,
        },
        message="Quiz submitted",
        meta={"total": len(questions)}
    )


@student_bp.route('/booking-slots', methods=['GET'])
@student_required
def booking_slots():
    student = current_student()

    if not student:
        return fail(
            "Student not found",
            404
        )

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    booked_ids = {
        b.session_id
        for b in SessionBooking.query.filter_by(
            student_id=student.student_id
        ).all()
        if b.booking_status != "Cancelled"
    }

    session_query = Session.query.filter(
        Session.session_date >= date.today(),
        Session.status.in_(
            ["Scheduled", "Rescheduled"]
        )
    )

    if enrolled_subjects:
        session_query = session_query.filter(
            Session.subject_id.in_(
                enrolled_subjects
            )
        )
    else:
        return ok(
            {
                "bookingSlots": {
                    "regular": [],
                    "oneToOne": [],
                }
            },
            meta={"total": 0}
        )

    sessions = session_query.order_by(
        Session.session_date,
        Session.start_time
    ).all()

    regular = []
    one = []

    for s in sessions:

        slot = session_json(
            s,
            "Confirmed"
            if s.session_id in booked_ids
            else None
        )

        slot.update({
            "id": s.session_id,
            "booked": (
                s.session_id in booked_ids
            ),
            "available": (
                s.session_id not in booked_ids
            ),
            "seats": (
                0
                if s.session_id in booked_ids
                else 1
            ),
        })

        if s.session_type == "One-to-One":
            one.append(slot)
        else:
            regular.append(slot)

    return ok(
        {
            "bookingSlots": {
                "regular": regular,
                "oneToOne": one,
            }
        },
        meta={
            "total": len(regular) + len(one)
        }
    )


@student_bp.route('/book-session', methods=['POST'])
@student_required
def book_session():
    student = current_student()

    data = request.get_json(
        silent=True
    ) or {}

    try:
        session_id = int(
            data.get("session_id")
        )
    except (TypeError, ValueError):
        return fail(
            "session_id is required",
            400
        )

    sess = db.session.get(
        Session,
        session_id
    )

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    if (
        not sess
        or sess.subject_id not in enrolled_subjects
    ):
        return fail(
            "You are not enrolled in this session's subject",
            403
        )

    if (
        sess.status not in (
            "Scheduled",
            "Rescheduled"
        )
        or sess.session_date < date.today()
    ):
        return fail(
            "Session is not available for booking",
            400
        )

    existing = SessionBooking.query.filter_by(
        session_id=session_id,
        student_id=student.student_id
    ).first()

    if (
        existing
        and existing.booking_status != "Cancelled"
    ):
        return fail(
            "You have already booked this session",
            409
        )

    if existing:
        existing.booking_status = "Confirmed"
    else:
        existing = SessionBooking(
            session_id=session_id,
            student_id=student.student_id,
            booking_status="Confirmed"
        )

        db.session.add(existing)

    db.session.commit()

    return ok(
        {
            "booked_session_id": session_id,
            "booking_id": existing.booking_id,
            "status": existing.booking_status,
        },
        message="Session booked"
    )


@student_bp.route(
    '/reschedule-session',
    methods=['POST']
)
@student_required
def reschedule_session():
    student = current_student()

    data = request.get_json(
        silent=True
    ) or {}

    try:
        current_id = int(
            data.get("current_session_id")
        )

        target_id = int(
            data.get("target_session_id")
        )

    except (TypeError, ValueError):
        return fail(
            "current_session_id and target_session_id are required"
        )

    current = SessionBooking.query.filter_by(
        session_id=current_id,
        student_id=student.student_id
    ).first()

    target = db.session.get(
        Session,
        target_id
    )

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    if (
        target
        and target.subject_id not in enrolled_subjects
    ):
        return fail(
            "You are not enrolled in the target session's subject",
            403
        )

    if (
        not current
        or current.booking_status == "Cancelled"
    ):
        return fail(
            "Current booking not found",
            404
        )

    if (
        not target
        or target.status not in (
            "Scheduled",
            "Rescheduled"
        )
        or target.session_date < date.today()
    ):
        return fail(
            "Target session is not available",
            400
        )

    if SessionBooking.query.filter_by(
        session_id=target_id,
        student_id=student.student_id
    ).first():
        return fail(
            "Target session is already booked",
            409
        )

    current.booking_status = "Cancelled"

    db.session.add(
        SessionBooking(
            session_id=target_id,
            student_id=student.student_id,
            booking_status="Confirmed"
        )
    )

    db.session.commit()

    return ok(
        message="Session rescheduled"
    )


@student_bp.route('/sessions', methods=['GET'])
@student_required
def sessions():
    student = current_student()

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    bookings = SessionBooking.query.filter_by(
        student_id=student.student_id
    ).join(Session).order_by(
        Session.session_date,
        Session.start_time
    ).all()

    upcoming = []
    completed = []

    for b in bookings:

        sess = db.session.get(
            Session,
            b.session_id
        )

        if (
            not sess
            or sess.subject_id not in enrolled_subjects
        ):
            continue

        item = session_json(
            sess,
            b.booking_status
        )

        # The session lifecycle is the authoritative display state. A meeting
        # that has already ended must never remain in "Upcoming Sessions"
        # merely because the persisted session status was not updated.
        lifecycle_status = item.get("meeting_lifecycle")
        if (
            sess.status == "Completed"
            or lifecycle_status == "Meeting Ended"
            or sess.session_date < date.today()
        ):
            completed.append(item)
        else:
            upcoming.append(item)

    return ok(
        {
            "upcoming": upcoming,
            "completed": completed,
            "sessions": upcoming + completed,
        },
        meta={
            "total": len(upcoming) + len(completed)
        }
    )


@student_bp.route(
    '/upcoming-sessions',
    methods=['GET']
)
@student_required
def upcoming_sessions():
    data, _, _ = _student_upcoming()

    return ok(
        {
            "upcoming_sessions": data
        },
        meta={
            "total": len(data)
        }
    )


def _student_upcoming():
    student = current_student()

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    bookings = SessionBooking.query.filter_by(
        student_id=student.student_id
    ).join(Session).all()

    items = []

    for b in bookings:

        sess = db.session.get(
            Session,
            b.session_id
        )

        if (
            sess
            and sess.subject_id in enrolled_subjects
            and sess.status in (
                "Scheduled",
                "Rescheduled"
            )
            and sess.session_date >= date.today()
        ):
            items.append(
                session_json(
                    sess,
                    b.booking_status
                )
            )

    items.sort(
        key=lambda x: (
            x["date_iso"],
            x["start_time"]
        )
    )

    return items, student, bookings


@student_bp.route('/sessions/<int:session_id>/join', methods=['POST'])
@student_required
def join_session(session_id):
    student = current_student()
    if not student:
        return fail('Student not logged in', 401)

    sess = db.session.get(Session, session_id)
    booking = SessionBooking.query.filter_by(
        session_id=session_id,
        student_id=student.student_id,
        booking_status='Confirmed'
    ).first()
    if not sess or not booking:
        return fail('You are not a participant in this session.', 403)

    lifecycle = meeting_lifecycle(sess)
    meeting = MeetingRequest.query.filter_by(session_id=session_id, student_id=student.student_id).first()
    meeting_link = sess.meeting_url or (meeting.meeting_link if meeting else None)

    # Regular sessions become joinable only after the tutor starts. Accepted
    # parent-created ONE-TO-ONE meetings may use their persisted link immediately.
    if not lifecycle['can_join']:
        if not (
            meeting and meeting.status == 'Scheduled'
            and sess.session_type == 'One-to-One'
            and meeting_link
        ):
            return fail('The meeting has not been started yet.', 409)

    if not meeting_link:
        return fail('No meeting link is available yet.', 409)

    progress = LearningProgress.query.filter_by(
        session_id=session_id,
        student_id=student.student_id
    ).first()
    if not progress:
        progress = LearningProgress(
            session_id=session_id,
            student_id=student.student_id,
            joined_at=_local_now()
        )
        db.session.add(progress)
    elif not progress.joined_at:
        progress.joined_at = _local_now()

    db.session.commit()
    return ok({
        'session_id': session_id,
        'meeting_url': meeting_link,
        'joined_at': progress.joined_at.isoformat() if progress.joined_at else None,
    }, 'Meeting join recorded')


@student_bp.route('/meeting-request', methods=['POST'])
@student_required
def request_meeting():
    student = current_student()
    if not student:
        return fail('Student not found', 404)

    d = request.get_json(silent=True) or {}
    try:
        tutor_id = int(d.get('tutor_id'))
    except (TypeError, ValueError):
        return fail('tutor_id is required')

    tutor = db.session.get(Tutor, tutor_id)
    if not tutor:
        return fail('Tutor not found', 404)

    preferred_date = d.get('preferred_date')
    preferred_time = d.get('preferred_time')
    if not preferred_date or not preferred_time:
        return fail('preferred_date and preferred_time are required')
    try:
        start_dt = datetime.strptime(f'{preferred_date} {preferred_time}', '%Y-%m-%d %H:%M')
        end_time_value = d.get('preferred_end_time')
        if end_time_value:
            end_dt = datetime.strptime(f'{preferred_date} {end_time_value}', '%Y-%m-%d %H:%M')
        else:
            from datetime import timedelta
            end_dt = start_dt + timedelta(hours=1)
    except ValueError:
        return fail('Invalid date/time')
    if end_dt <= start_dt:
        return fail('End time must be later than start time')

    # Prevent duplicate requests for the same student/tutor/time, mirroring
    # the existing parent meeting-request duplicate check.
    duplicate_query = MeetingRequest.query.filter(
        MeetingRequest.student_id == student.student_id,
        MeetingRequest.tutor_id == tutor.tutor_id,
        MeetingRequest.meeting_date == start_dt,
        MeetingRequest.status.in_(['Pending Approval', 'Scheduled', 'Reschedule Requested'])
    )
    if duplicate_query.first():
        return fail('A meeting request for this tutor and time already exists.', 409)

    subject_row = StudentSubject.query.filter_by(student_id=student.student_id).first()
    if not subject_row:
        return fail('You have no registered subject')
    subject = db.session.get(Subject, subject_row.subject_id)

    # Requesting a meeting must use an existing tutor/student relationship or
    # a tutor who is configured for the student's enrolled subject.
    related = Session.query.join(SessionBooking, SessionBooking.session_id == Session.session_id).filter(
        Session.tutor_id == tutor.tutor_id, SessionBooking.student_id == student.student_id
    ).first()
    if not related:
        try:
            configured = {str(x).strip().lower() for x in json.loads(tutor.subjects_json or '[]')}
        except Exception:
            configured = set()
        if not subject or subject.subject_name.strip().lower() not in configured:
            return fail('This tutor is not associated with your enrolled subject', 403)

    conflicts = Session.query.filter(Session.tutor_id == tutor.tutor_id, Session.session_date == start_dt.date()).all()
    for existing in conflicts:
        if existing.status != 'Cancelled' and start_dt.time() < existing.end_time and end_dt.time() > existing.start_time:
            return fail('The tutor already has another session scheduled during this time.', 409)

    # Reuse the existing Session + SessionBooking system, same as the parent
    # meeting-request flow. A pending request has no Meet resource yet; the
    # tutor supplies or auto-generates the link on approval.
    session_obj = Session(
        tutor_id=tutor.tutor_id, subject_id=subject_row.subject_id,
        session_date=start_dt.date(), start_time=start_dt.time(), end_time=end_dt.time(),
        session_type='One-to-One', status='Scheduled'
    )
    db.session.add(session_obj)
    db.session.flush()
    db.session.add(SessionBooking(session_id=session_obj.session_id, student_id=student.student_id, booking_status='Confirmed'))

    m = MeetingRequest(
        tutor_id=tutor.tutor_id, student_id=student.student_id, parent_id=student.parent_id,
        meeting_date=start_dt, meeting_link=None, meeting_reason=d.get('notes', ''),
        session_id=session_obj.session_id, status='Pending Approval'
    )
    db.session.add(m)

    display_date = start_dt.strftime('%d %b %Y')
    display_start = start_dt.strftime('%I:%M %p')
    display_end = end_dt.strftime('%I:%M %p')
    db.session.add(Notification(
        recipient_type='Tutor', recipient_id=tutor.tutor_id,
        title=f'{subject.subject_name} meeting request',
        message=f'{student.student_name} requested a one-on-one {subject.subject_name} meeting for {display_date}, {display_start}–{display_end}.',
        notification_type='Meeting Request', action_url=f'/tutor/schedule?session_id={session_obj.session_id}'
    ))
    db.session.commit()
    return ok({
        'meeting_id': m.meeting_id, 'session_id': session_obj.session_id,
        'meeting_date': m.meeting_date.isoformat(), 'meeting_link': None, 'status': m.status
    }, 'Meeting scheduled', 201)


@student_bp.route(
    '/next-session',
    methods=['GET']
)
@student_required
def next_session():
    items, _, _ = _student_upcoming()

    return ok(
        {
            "nextSession": (
                items[0]
                if items
                else {}
            )
        }
    )


@student_bp.route(
    '/study-tips',
    methods=['GET']
)
@student_required
def study_tips():
    student = current_student()

    tips = StudyTip.query.filter_by(
        student_id=student.student_id
    ).order_by(
        StudyTip.created_at.desc()
    ).all()

    data = []

    for t in tips:

        sess = db.session.get(
            Session,
            t.session_id
        )

        data.append({
            "id": t.tip_id,
            "subject": (
                subject_name(sess.subject_id)
                if sess
                else "General"
            ),
            "tip": t.tip_text,
            "createdAt": (
                t.created_at.isoformat()
                if t.created_at
                else None
            ),
        })

    return ok(
        {"studyTips": data},
        meta={"total": len(data)}
    )


@student_bp.route(
    '/performance-insights',
    methods=['POST']
)
@student_required
def performance_insights():
    student = current_student()
    if not student:
        return fail("Student not found or not logged in", 404)

    context = build_performance_context(student)

    return ok(
        {
            "insights": render_performance_text(context),
            "performance": context,
            "sourceCounts": {
                "quizAttempts": context["overall"]["completedQuizzes"],
                "missedQuestions": len(context["missedQuestions"]),
                "topics": len(context["topicPerformance"]),
            },
        }
    )


@student_bp.route('/flashcards', methods=['GET'])
@student_required
def flashcards():
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    topic_filter = (request.args.get("topic") or "").strip().lower()
    cards = []

    for quiz in assigned_student_quizzes(student.student_id):
        topic = quiz_topic(quiz)
        if topic_filter and (topic_filter not in topic.lower() and topic.lower() not in topic_filter):
            continue
        questions = (
            QuizQuestion.query
            .filter_by(quiz_id=quiz.quiz_id)
            .order_by(QuizQuestion.question_id)
            .all()
        )
        if questions:
            for question in questions:
                correct = str(question.correct_option or "").strip().upper()
                cards.append({
                    "id": f"q-{question.question_id}",
                    "quiz_id": quiz.quiz_id,
                    "subject": subject_name(quiz.subject_id),
                    "topic": topic,
                    "front": question.question,
                    "back": answer_label(question, correct) or correct,
                    "explanation": question.explanation or "",
                })
        else:
            cards.extend([
                {
                    "id": f"quiz-{quiz.quiz_id}-topic",
                    "quiz_id": quiz.quiz_id,
                    "subject": subject_name(quiz.subject_id),
                    "topic": topic,
                    "front": f"What topic is this quiz about?",
                    "back": topic,
                    "explanation": f"Review the exact topic your tutor assigned: {subject_name(quiz.subject_id)} - {topic}.",
                },
                {
                    "id": f"quiz-{quiz.quiz_id}-next",
                    "quiz_id": quiz.quiz_id,
                    "subject": subject_name(quiz.subject_id),
                    "topic": topic,
                    "front": f"What should you revise before attempting {quiz.title}?",
                    "back": topic,
                    "explanation": "Your tutor has assigned this quiz for this specific concept.",
                },
            ])

    return ok({"flashcards": cards[:20]}, meta={"total": len(cards)})


def student_can_access_flashcard_set(student_id, fset):
    if not fset:
        return False
    if fset.assigned_student_id is not None:
        return fset.assigned_student_id == student_id
    enrolled = StudentSubject.query.filter_by(
        student_id=student_id,
        subject_id=fset.subject_id
    ).first()
    return enrolled is not None


@student_bp.route('/flashcard-sets', methods=['GET'])
@student_required
def flashcard_sets():
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    sets = FlashcardSet.query.order_by(FlashcardSet.created_at.desc()).all()
    accessible = [s for s in sets if student_can_access_flashcard_set(student.student_id, s)]

    return ok({
        "sets": [
            {
                "set_id": s.set_id,
                "subject": subject_name(s.subject_id),
                "title": s.title,
                "topic": s.topic,
                "class_level": s.class_level,
                "cardCount": Flashcard.query.filter_by(set_id=s.set_id).count(),
            }
            for s in accessible
        ]
    }, meta={"total": len(accessible)})


@student_bp.route('/flashcard-sets/<int:set_id>/cards', methods=['GET'])
@student_required
def flashcard_set_cards(set_id):
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    fset = db.session.get(FlashcardSet, set_id)
    if not fset:
        return fail("Flashcard set not found", 404)
    if not student_can_access_flashcard_set(student.student_id, fset):
        return fail("You are not assigned to this flashcard set", 403)

    cards = Flashcard.query.filter_by(set_id=set_id).order_by(Flashcard.card_id).all()

    return ok({
        "set": {
            "set_id": fset.set_id,
            "subject": subject_name(fset.subject_id),
            "title": fset.title,
            "topic": fset.topic,
            "class_level": fset.class_level,
        },
        "cards": [
            {"id": c.card_id, "front": c.front, "back": c.back, "explanation": c.explanation or ""}
            for c in cards
        ],
    }, meta={"total": len(cards)})


@student_bp.route('/flashcards/ai-generate', methods=['POST'])
@student_required
def student_flashcards_ai_generate():
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    data = request.get_json(silent=True) or {}
    subject = str(data.get("subject") or "").strip()
    topic = str(data.get("topic") or "").strip()
    class_level = str(data.get("class_level") or "").strip()
    context = str(data.get("context") or "").strip()
    try:
        count = int(data.get("count") or 10)
    except (TypeError, ValueError):
        count = 10
    count = max(1, min(count, 20))

    if not subject:
        return fail("subject is required")
    if not topic:
        return fail("topic is required")

    prompt = (
        "You are Student AI for LearnAtHome, helping a student self-practice. "
        "Generate flashcards using only the exact requested subject, topic, "
        "class level, and context below. Every flashcard must directly test "
        "or explain the requested topic; do not drift into adjacent topics. "
        "Do not invent content unrelated to what was provided. Return a "
        "JSON array of objects with exactly the keys front, back, and "
        "explanation. 'front' is a short question or term for the student "
        "to recall, 'back' is the concise answer or definition, "
        "'explanation' is one sentence giving context. Return exactly "
        f"{count} flashcards.\n\n"
        f"Subject: {subject}\n"
        f"Topic: {topic}\n"
        f"Class level: {class_level or 'Not specified'}\n"
        f"Context: {context or 'None provided'}"
    )

    try:
        raw_generated = generate_text(prompt, response_mime_type="application/json")
        json_text = raw_generated.strip()
        if json_text.startswith("```"):
            json_text = json_text.removeprefix("```json").removeprefix("```")
            json_text = json_text.removesuffix("```").strip()
        generated = json.loads(json_text)
        if not isinstance(generated, list) or not generated:
            raise AIResponseError("AI provider returned an invalid flashcard set.")
        required_fields = {"front", "back"}
        for item in generated:
            if not isinstance(item, dict) or not required_fields.issubset(item):
                raise AIResponseError("AI provider returned an invalid flashcard set.")
            if not str(item.get("front") or "").strip() or not str(item.get("back") or "").strip():
                raise AIResponseError("AI provider returned an invalid flashcard set.")
        generated = generated[:count]
    except AIConfigError as exc:
        return fail(str(exc), 503)
    except json.JSONDecodeError:
        return fail("AI flashcard generation failed: AI provider returned invalid flashcard JSON.", 502)
    except (AIServiceError, AIResponseError) as exc:
        return fail(f"AI flashcard generation failed: {exc}", 502)

    return ok({"flashcards": generated}, message="AI flashcards generated")


@student_bp.route('/flashcard-sets/self-generate', methods=['POST'])
@student_required
def student_create_flashcard_set():
    student = current_student()
    if not student:
        return fail("Student not found", 404)

    data = request.get_json(silent=True) or {}
    try:
        subject_id = int(data.get("subject_id"))
    except (TypeError, ValueError):
        return fail("subject_id is required")
    if not db.session.get(Subject, subject_id):
        return fail("Subject not found", 404)

    title = (data.get("title") or "").strip()
    if not title:
        return fail("title is required")

    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        return fail("At least one flashcard is required")

    fset = FlashcardSet(
        tutor_id=None,
        subject_id=subject_id,
        assigned_student_id=student.student_id,
        title=title,
        topic=(data.get("topic") or "").strip() or None,
        class_level=(data.get("class_level") or "").strip() or None,
        context=(data.get("context") or "").strip() or None,
    )
    db.session.add(fset)
    db.session.flush()

    saved = 0
    for card in cards:
        front = str((card or {}).get("front") or "").strip()
        back = str((card or {}).get("back") or "").strip()
        if not front or not back:
            continue
        explanation = str((card or {}).get("explanation") or "").strip()
        db.session.add(Flashcard(set_id=fset.set_id, front=front, back=back, explanation=explanation))
        saved += 1

    if not saved:
        db.session.rollback()
        return fail("At least one flashcard with front and back is required")

    db.session.commit()
    return ok({"set_id": fset.set_id, "cardCount": saved}, "Flashcard set created", 201)


@student_bp.route('/performance-chat', methods=['POST'])
@student_required
def performance_chat():
    student = current_student()
    if not student:
        return fail("Student not found or not logged in", 404)

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return fail("Invalid chat payload", 400)
    message = (payload.get("message") or "").strip()
    if not message:
        return fail("Message is required")

    context = build_performance_context(student)
    prompt = (
        "You are the existing LearnAtHome student helper inside Performance Insights. "
        "Answer in a simple, encouraging tutor style. Use only the provided backend "
        "performance context for factual claims. Do not invent scores, weak topics, "
        "completed quizzes, or missed answers. If the context has insufficient data, "
        "say that clearly. Keep the answer short and interactive.\n\n"
        f"PERFORMANCE_CONTEXT:\n{json.dumps(context, ensure_ascii=False, default=str)}\n\n"
        f"STUDENT_QUESTION: {message}"
    )

    try:
        reply = generate_text(prompt)
    except (AIConfigError, AIServiceError, AIResponseError):
        reply = performance_chat_fallback(message, context)

    return ok({"reply": reply})


@student_bp.route(
    '/assignments',
    methods=['GET']
)
@student_required
def assignments():
    student = current_student()

    rows = Assignment.query.join(
        Session
    ).filter(
        Session.tutor_id.isnot(None)
    ).order_by(
        Assignment.due_date
    ).all()

    data = []

    for a in rows:

        sess = db.session.get(
            Session,
            a.session_id
        )

        if not sess:
            continue

        booking = SessionBooking.query.filter_by(
            session_id=a.session_id,
            student_id=student.student_id
        ).first()

        enrollment = StudentSubject.query.filter_by(
            student_id=student.student_id,
            subject_id=sess.subject_id
        ).first()

        if booking or enrollment:
            data.append(
                assignment_json(
                    a,
                    student.student_id
                )
            )

    return ok(
        {"assignments": data},
        meta={"total": len(data)}
    )


@student_bp.route(
    '/assignments/<int:assignment_id>/update-progress',
    methods=['POST']
)
@student_required
def update_assignment_progress(assignment_id):
    student = current_student()

    assignment = db.session.get(
        Assignment,
        assignment_id
    )

    if not assignment:
        return fail(
            "Assignment not found",
            404
        )

    sess = db.session.get(
        Session,
        assignment.session_id
    )

    if (
        not sess
        or not StudentSubject.query.filter_by(
            student_id=student.student_id,
            subject_id=sess.subject_id
        ).first()
    ):
        return fail(
            "Assignment is not available to you",
            403
        )

    data = request.get_json(
        silent=True
    ) or {}

    try:
        progress = max(
            0,
            min(
                100,
                int(data.get("progress", 0))
            )
        )

    except (TypeError, ValueError):
        return fail(
            "progress must be a number"
        )

    sub = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=student.student_id
    ).first()

    if not sub:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student.student_id
        )

        db.session.add(sub)

    sub.progress_percentage = progress

    if progress >= 100:
        sub.status = "Completed"
    elif progress > 0:
        sub.status = "In Progress"
    else:
        sub.status = "Pending"

    sub.submission_date = datetime.utcnow()

    db.session.commit()

    return ok(
        {
            "assignment_id": assignment_id,
            "progress": progress,
            "status": sub.status,
        },
        meta={"total": 1}
    )


@student_bp.route(
    '/assignments/<int:assignment_id>/complete',
    methods=['POST']
)
@student_required
def mark_homework_completed(assignment_id):
    student = current_student()

    assignment = db.session.get(
        Assignment,
        assignment_id
    )

    if not assignment:
        return fail(
            "Assignment not found",
            404
        )

    sess = db.session.get(
        Session,
        assignment.session_id
    )

    if (
        not sess
        or not StudentSubject.query.filter_by(
            student_id=student.student_id,
            subject_id=sess.subject_id
        ).first()
    ):
        return fail(
            "Assignment is not available to you",
            403
        )

    sub = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=student.student_id
    ).first()

    if not sub:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student.student_id
        )

        db.session.add(sub)

    sub.status = "Completed"
    sub.progress_percentage = 100
    sub.submission_date = datetime.utcnow()

    db.session.commit()

    return ok(
        {
            "assignment_id": assignment_id,
            "status": sub.status,
            "homeworkStatus": "Done",
        },
        message="Homework marked as completed"
    )


@student_bp.route(
    '/assignments/<int:assignment_id>/submit',
    methods=['POST']
)
@student_required
def submit_assignment(assignment_id):
    student = current_student()

    assignment = db.session.get(
        Assignment,
        assignment_id
    )

    if not assignment:
        return fail(
            "Assignment not found",
            404
        )

    sess = db.session.get(
        Session,
        assignment.session_id
    )

    if (
        not sess
        or not StudentSubject.query.filter_by(
            student_id=student.student_id,
            subject_id=sess.subject_id
        ).first()
    ):
        return fail(
            "Assignment is not available to you",
            403
        )

    sub = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=student.student_id
    ).first()

    if not sub:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student.student_id
        )

        db.session.add(sub)

    sub.progress_percentage = 100
    sub.status = "Submitted"
    sub.submission_date = datetime.utcnow()

    db.session.commit()

    return ok(
        {
            "assignment_id": assignment_id,
            "status": sub.status,
            "progress": 100,
        },
        message="Assignment submitted"
    )


@student_bp.route(
    '/timetable',
    methods=['GET']
)
@student_required
def timetable():
    """
    Returns the student's booked sessions for a single calendar month.

    Sessions are keyed by their actual ISO date:
    YYYY-MM-DD.
    """

    student = current_student()

    today = date.today()

    try:
        year = int(
            request.args.get(
                'year',
                today.year
            )
        )

    except (TypeError, ValueError):
        year = today.year

    try:
        month = int(
            request.args.get(
                'month',
                today.month
            )
        )

    except (TypeError, ValueError):
        month = today.month

    if month < 1 or month > 12:
        month = today.month

    days_in_month = calendar.monthrange(
        year,
        month
    )[1]

    days_map = {}

    for d in range(
        1,
        days_in_month + 1
    ):

        iso = date(
            year,
            month,
            d
        ).isoformat()

        days_map[iso] = []

    enrolled_subjects = enrolled_subject_ids(
        student.student_id
    )

    bookings = SessionBooking.query.filter_by(
        student_id=student.student_id
    ).join(Session).all()

    for b in bookings:

        s = db.session.get(
            Session,
            b.session_id
        )

        if (
            not s
            or not s.session_date
            or s.subject_id not in enrolled_subjects
        ):
            continue

        if (
            s.session_date.year != year
            or s.session_date.month != month
        ):
            continue

        iso = s.session_date.isoformat()

        tutor = db.session.get(
            Tutor,
            s.tutor_id
        )

        days_map[iso].append({
            "subject": subject_name(
                s.subject_id
            ),

            "time": (
                f"{s.start_time.strftime('%I:%M %p')}"
                f" – "
                f"{s.end_time.strftime('%I:%M %p')}"
            ),

            "tutor": (
                tutor.tutor_name
                if tutor
                else "Tutor"
            ),

            "status": s.status,

            "session_id": s.session_id,

            "date": iso,
        })

    return ok(
        {
            "year": year,
            "month": month,
            "daysInMonth": days_in_month,
            "firstWeekday": date(
                year,
                month,
                1
            ).weekday(),
            "days": days_map,
        }
    )


@student_bp.route(
    '/resources',
    methods=['GET']
)
@student_required
def resources():
    student = current_student()

    rows = StudyResource.query.join(
        Session
    ).order_by(
        StudyResource.resource_id.desc()
    ).all()

    data = []

    for r in rows:

        sess = db.session.get(
            Session,
            r.session_id
        )

        if not sess:
            continue

        booking = SessionBooking.query.filter_by(
            session_id=sess.session_id,
            student_id=student.student_id
        ).first()

        enrollment = StudentSubject.query.filter_by(
            student_id=student.student_id,
            subject_id=sess.subject_id
        ).first()

        if not booking and not enrollment:
            continue

        data.append({
            "resource_id": r.resource_id,
            "session_id": r.session_id,
            "resource_title": r.resource_title,
            "resource_type": r.resource_type,
            "resource_link": r.resource_link,
            "subject": subject_name(
                sess.subject_id
            ),
        })

    return ok(
        {"resources": data},
        meta={"total": len(data)}
    )


@student_bp.route(
    '/profile',
    methods=['GET', 'PUT']
)
@student_required
def profile():
    student = current_student()

    if not student:
        return fail(
            "Student profile not found",
            404
        )

    if request.method == "PUT":

        data = request.get_json(
            silent=True
        ) or {}

        if (
            "name" in data
            or "student_name" in data
        ):
            student.student_name = (
                data.get("name")
                or data.get("student_name")
                or student.student_name
            ).strip()

        if (
            "phone" in data
            or "phone_no" in data
        ):
            student.phone_no = (
                data.get("phone")
                if "phone" in data
                else data.get("phone_no")
            )

        if "school" in data:
            student.school = data.get(
                "school"
            )

        db.session.commit()

        return ok(
            message="Profile updated successfully"
        )

    subjects = [
        subject_name(x.subject_id)
        for x in StudentSubject.query.filter_by(
            student_id=student.student_id
        ).all()
    ]

    parent = (
        db.session.get(
            Parent,
            student.parent_id
        )
        if student.parent_id
        else None
    )

    return ok({
        "student": {
            "student_id": student.student_id,
            "name": student.student_name,
            "email": student.email,
            "phone": student.phone_no,
            "school": student.school,
            "subjects": subjects,
            "parentName": (
                parent.parent_name
                if parent
                else None
            ),
            "parentId": student.parent_id,
        }
    })


@student_bp.route(
    '/meetings',
    methods=['GET']
)
@student_required
def meetings():
    student = current_student()

    rows = MeetingRequest.query.filter_by(
        student_id=student.student_id
    ).order_by(
        MeetingRequest.meeting_date.desc()
    ).all()

    result = []

    for m in rows:

        tutor = db.session.get(
            Tutor,
            m.tutor_id
        )

        sess = db.session.get(Session, m.session_id) if m.session_id else None
        lifecycle = meeting_lifecycle(sess) if sess else {
            "status": "Meeting Not Started", "can_join": False,
            "can_start": False, "can_end": False,
        }
        meeting_link = (sess.meeting_url if sess and sess.meeting_url else m.meeting_link)
        # Accepted parent-created ONE-TO-ONE meetings have a persisted link
        # and must be visible to authorised participants immediately. Regular
        # sessions retain the normal "join after tutor starts" lifecycle.
        if m.status == "Scheduled" and sess and sess.session_type == "One-to-One" and meeting_link:
            if lifecycle["status"] == "Meeting Not Started":
                lifecycle = {**lifecycle, "status": "Request Accepted", "can_join": True}

        result.append({
            "meeting_id": m.meeting_id,
            "session_id": m.session_id,
            "date": m.meeting_date.isoformat() if m.meeting_date else None,
            "meeting_link": meeting_link,
            "reason": m.meeting_reason,
            "status": m.status,
            "meeting_lifecycle": lifecycle["status"],
            "can_join": lifecycle["can_join"],
            "tutor_id": m.tutor_id,
            "tutor": tutor.tutor_name if tutor else "Tutor",
            "meeting_type": sess.session_type if sess else "One-to-One",
        })

    return ok({
        "meetings": result
    })


# =========================================================
# STUDENT <-> TUTOR MESSAGES
# =========================================================

@student_bp.route('/messages', methods=['GET', 'POST'])
@student_required
def student_messages():
    student = current_student()
    if not student:
        return fail('Student not logged in', 401)

    if request.method == 'GET':
        rows = Message.query.filter(
            (
                (Message.sender_type == 'Student') &
                (Message.sender_id == student.student_id)
            ) |
            (
                (Message.receiver_type == 'Student') &
                (Message.receiver_id == student.student_id)
            )
        ).order_by(Message.sent_at.asc()).all()

        conversations = {}
        for m in rows:
            if m.sender_type == 'Student':
                tutor_id = m.receiver_id if m.receiver_type == 'Tutor' else None
            else:
                tutor_id = m.sender_id if m.sender_type == 'Tutor' else None
            if tutor_id is None:
                continue

            tutor = db.session.get(Tutor, tutor_id)
            if not tutor:
                continue
            key = str(tutor_id)
            if key not in conversations:
                conversations[key] = {
                    'tutor_id': tutor_id,
                    'tutor_name': tutor.tutor_name,
                    'messages': []
                }
            conversations[key]['messages'].append({
                'message_id': m.message_id,
                'message': m.message,
                'sender_type': m.sender_type,
                'sent_at': m.sent_at.isoformat() if m.sent_at else None
            })

        # The tutor list is owned by the student's existing session/booking
        # relationship, not by message history. This makes a brand-new
        # conversation discoverable before the first message is sent.
        linked_rows = (
            Session.query
            .join(SessionBooking, SessionBooking.session_id == Session.session_id)
            .filter(
                SessionBooking.student_id == student.student_id,
                SessionBooking.booking_status != 'Cancelled',
                Session.tutor_id.isnot(None),
            )
            .order_by(Session.session_date.desc(), Session.session_id.desc())
            .all()
        )
        tutor_map = {}
        for sess in linked_rows:
            tutor = db.session.get(Tutor, sess.tutor_id)
            if tutor:
                tutor_map[str(tutor.tutor_id)] = {
                    'tutor_id': tutor.tutor_id,
                    'tutor_name': tutor.tutor_name,
                }

        return ok({
            'conversations': list(conversations.values()),
            'tutors': list(tutor_map.values()),
        })

    data = request.get_json(silent=True) or {}
    try:
        tutor_id = int(data.get('tutor_id'))
    except (TypeError, ValueError):
        return fail('tutor_id is required')

    text = str(data.get('message') or '').strip()
    if not text:
        return fail('Message is required')

    # Only tutors connected to this student's confirmed sessions may be
    # selected. This prevents arbitrary cross-user messaging.
    linked = (
        Session.query
        .join(SessionBooking, SessionBooking.session_id == Session.session_id)
        .filter(
            SessionBooking.student_id == student.student_id,
            SessionBooking.booking_status == 'Confirmed',
            Session.tutor_id == tutor_id
        )
        .first()
    )
    if not linked:
        return fail('This tutor is not linked to your active sessions.', 403)

    tutor = db.session.get(Tutor, tutor_id)
    message = Message(
        sender_type='Student',
        sender_id=student.student_id,
        receiver_type='Tutor',
        receiver_id=tutor_id,
        subject='Student Message',
        message=text
    )
    db.session.add(message)
    db.session.add(Notification(
        recipient_type='Tutor',
        recipient_id=tutor_id,
        title=f'New message from {student.student_name}',
        message=text,
        notification_type='New Message',
        action_url='/tutor/messages'
    ))
    db.session.commit()

    return ok({'message_id': message.message_id}, 'Message sent', 201)


@student_bp.route(
    '/notifications',
    methods=['GET']
)
@student_required
def notifications():
    student = current_student()

    rows = Notification.query.filter_by(
        recipient_type="Student",
        recipient_id=student.student_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return ok({
        "notifications": [
            {
                "id": n.notification_id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "isRead": n.is_read,
                "actionUrl": n.action_url,
                "createdAt": (
                    n.created_at.isoformat()
                    if n.created_at
                    else None
                ),
            }
            for n in rows
        ]
    })


@student_bp.route(
    '/notifications/<int:notification_id>/read',
    methods=['PATCH']
)
@student_required
def mark_notification(notification_id):
    student = current_student()

    n = Notification.query.filter_by(
        notification_id=notification_id,
        recipient_type="Student",
        recipient_id=student.student_id
    ).first()

    if not n:
        return fail(
            "Notification not found",
            404
        )

    n.is_read = True

    db.session.commit()

    return ok(
        message="Notification marked as read"
    )


def _student_tutor_ids(student_id):
    """
    Tutors relevant to this student based on real
    subject/session/booking data.
    """

    tutor_ids = set()

    subject_ids = {
        x.subject_id
        for x in StudentSubject.query.filter_by(
            student_id=student_id
        ).all()
    }

    if subject_ids:

        for s in Session.query.filter(
            Session.subject_id.in_(subject_ids)
        ).all():

            if s.tutor_id:
                tutor_ids.add(
                    s.tutor_id
                )

    for b in SessionBooking.query.filter_by(
        student_id=student_id
    ).all():

        sess = db.session.get(
            Session,
            b.session_id
        )

        if sess and sess.tutor_id:
            tutor_ids.add(
                sess.tutor_id
            )

    if not tutor_ids:

        tutor_ids = {
            t.tutor_id
            for t in Tutor.query.filter_by(
                status="Active"
            ).all()
        }

    return tutor_ids


@student_bp.route(
    '/tutors',
    methods=['GET']
)
@student_required
def student_tutors():
    """
    Real tutors the student can address a doubt to.
    """

    student = current_student()

    ids = _student_tutor_ids(
        student.student_id
    )

    tutors = (
        Tutor.query.filter(
            Tutor.tutor_id.in_(ids),
            Tutor.status == "Active"
        ).order_by(
            Tutor.tutor_name
        ).all()
        if ids
        else []
    )

    subjects = [
        subject_name(x.subject_id)
        for x in StudentSubject.query.filter_by(
            student_id=student.student_id
        ).all()
    ]

    return ok({
        "tutors": [
            {
                "tutor_id": t.tutor_id,
                "name": t.tutor_name,
                "email": t.email,
            }
            for t in tutors
        ],

        "subjects": subjects,
    })


def doubt_json(d):
    tutor = db.session.get(
        Tutor,
        d.tutor_id
    )

    return {
        "id": d.doubt_id,
        "doubt_id": d.doubt_id,
        "doubtId": d.doubt_id,

        "tutor_id": d.tutor_id,

        "tutor": (
            tutor.tutor_name
            if tutor
            else "Tutor"
        ),

        "subject": d.subject or "General",

        "question": d.question,

        "answer": d.answer,

        "status": d.status,

        "askedAt": (
            d.asked_at.isoformat()
            if d.asked_at
            else None
        ),

        "repliedAt": (
            d.replied_at.isoformat()
            if d.replied_at
            else None
        ),
    }


@student_bp.route(
    '/doubts',
    methods=['GET', 'POST']
)
@student_required
def doubts():
    student = current_student()

    if not student:
        return fail(
            "Student not found or not logged in",
            404
        )

    if request.method == 'POST':

        data = request.get_json(
            silent=True
        ) or {}

        question = (
            data.get("question")
            or ""
        ).strip()

        if not question:
            return fail(
                "Question is required"
            )

        subject = (
            data.get("subject")
            or ""
        ).strip() or None

        allowed_tutor_ids = _student_tutor_ids(
            student.student_id
        )

        tutor_id = data.get(
            "tutor_id"
        )

        if tutor_id is not None:

            try:
                tutor_id = int(tutor_id)

            except (
                TypeError,
                ValueError
            ):
                return fail(
                    "tutor_id must be a valid id"
                )

            tutor = db.session.get(
                Tutor,
                tutor_id
            )

            if (
                not tutor
                or tutor.status != "Active"
            ):
                return fail(
                    "Selected tutor is not available",
                    404
                )

        else:

            if not allowed_tutor_ids:
                return fail(
                    "No tutor is available to receive doubts right now",
                    404
                )

            tutor_id = sorted(
                allowed_tutor_ids
            )[0]

        doubt = Doubt(
            tutor_id=tutor_id,
            student_id=student.student_id,
            subject=subject,
            question=question,
            status="Open",
        )

        db.session.add(doubt)

        db.session.commit()

        db.session.add(
            Notification(
                recipient_type="Tutor",
                recipient_id=tutor_id,
                title="New doubt from a student",
                message=question,
                notification_type="Doubt",
            )
        )

        db.session.commit()

        return ok(
            {
                "doubt": doubt_json(doubt)
            },
            message="Doubt submitted",
            status=201
        )

    rows = Doubt.query.filter_by(
        student_id=student.student_id
    ).order_by(
        Doubt.asked_at.desc()
    ).all()

    return ok(
        {
            "doubts": [
                doubt_json(d)
                for d in rows
            ]
        },
        meta={
            "total": len(rows)
        }
    )


@student_bp.route(
    '/profile/password',
    methods=['PUT']
)
@student_required
def change_password():
    student = current_student()

    data = request.get_json(
        silent=True
    ) or {}

    current = data.get(
        'currentPassword',
        ''
    )

    new = data.get(
        'newPassword',
        ''
    )

    confirm = data.get(
        'confirmPassword',
        ''
    )

    if not current or not new or not confirm:
        return fail(
            'All password fields are required'
        )

    if not check_password_hash(
        student.password_hash,
        current
    ):
        return fail(
            'Current password is incorrect',
            400
        )

    if len(new) < 8:
        return fail(
            'New password must contain at least 8 characters'
        )

    if new != confirm:
        return fail(
            'New passwords do not match'
        )

    student.password_hash = (
        generate_password_hash(new)
    )

    db.session.commit()

    return ok(
        message='Password changed successfully'
    )
