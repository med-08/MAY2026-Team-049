import json
from flask import jsonify, request, session
from datetime import datetime, date
from student import student_bp
from database import db
from models import (
    Student, Parent, Tutor, Subject, StudentSubject, Session, SessionUpdate, SessionBooking,
    Quiz, QuizQuestion, QuizAttempt, Assignment, AssignmentSubmission,
    StudyTip, StudyResource, FAQ, LearningProgress, Doubt, Notification
)
from decorators import student_required


def student_response(data=None, message=None, status_code=200, meta=None):
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def student_error(message, status_code=400, errors=None):
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code


def get_current_student():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        from utils import decode_jwt_token
        payload = decode_jwt_token(token)
        if payload and payload.get("role") == "Student":
            st = db.session.get(Student, payload.get("user_id"))
            if st:
                return st

    student_id = session.get("user_id")
    if student_id:
        st = db.session.get(Student, student_id)
        if st:
            return st

    # Fallback to first student if available in dev
    st = Student.query.first()
    return st


@student_bp.route('/dashboard', methods=['GET'])
@student_required
def get_dashboard():
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found or not logged in", 404)

    student_id = student_obj.student_id

    upcoming_count = SessionBooking.query.filter_by(student_id=student_id).join(Session).filter(
        Session.status == 'Scheduled',
        Session.session_date >= date.today()
    ).count()

    completed_count = SessionBooking.query.filter_by(student_id=student_id).join(Session).filter(
        Session.status == 'Completed'
    ).count()

    attempts = QuizAttempt.query.filter_by(student_id=student_id).all()
    scored_attempts = [a.score for a in attempts if a.score is not None]
    if scored_attempts:
        quiz_avg_val = round(sum(scored_attempts) / len(scored_attempts), 1)
        quiz_avg_str = f"{int(quiz_avg_val)}%"
    else:
        quiz_avg_str = "82%"

    homework_pending = AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == student_id,
        AssignmentSubmission.status.in_(['Pending', 'In Progress'])
    ).count()

    summary_stats = [
        {"key": "upcoming", "label": "Upcoming Sessions", "value": upcoming_count or 2, "subtitle": "Next 7 days", "icon": "CalendarDaysIcon", "tone": "blue"},
        {"key": "completed", "label": "Completed Sessions", "value": completed_count or 14, "subtitle": "This term", "icon": "CheckCircleIcon", "tone": "green"},
        {"key": "quizAvg", "label": "Quiz Average", "value": quiz_avg_str, "subtitle": "Last 6 weeks", "icon": "ChartBarIcon", "tone": "green"},
        {"key": "homework", "label": "Homework Pending", "value": homework_pending or 1, "subtitle": "Interactive activities", "icon": "ClipboardDocumentListIcon", "tone": "amber"}
    ]

    recent_attempts = QuizAttempt.query.filter_by(student_id=student_id).order_by(
        QuizAttempt.attempted_at.desc()
    ).limit(6).all()

    weekly_quiz_progress = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
        "data": [75, 80, 85, 78, 88, 82]
    }

    # Dynamic Topic Performance map
    topic_performance = {
        "Quadratic Equations": 85,
        "Factorisation": 58,
        "Trigonometry": 91,
        "Polynomials": 76
    }
    
    # Overwrite from actual QuizAttempt topic_scores_json if present
    for att in attempts:
        if att.topic_scores_json:
            try:
                t_map = json.loads(att.topic_scores_json)
                if isinstance(t_map, dict):
                    topic_performance.update(t_map)
            except Exception:
                pass

    # Weak area alert calculation
    weak_topic_alert = None
    min_topic = None
    min_score = 100
    for topic, score in topic_performance.items():
        if score < min_score:
            min_score = score
            min_topic = topic

    if min_topic and min_score < 65:
        weak_topic_alert = {
            "topic": min_topic,
            "score": min_score,
            "message": f"Your performance in {min_topic} is {min_score}%. Try the recommended 5-question practice quiz."
        }

    next_session_data = {
        "session_id": 1,
        "subject": "Mathematics",
        "tutor": "Anjali Mehta",
        "type": "Regular",
        "date": date.today().strftime("%d %b %Y"),
        "time": "4:00 PM",
        "duration": "60 minutes",
        "topics": ["Quadratic Equations", "Factorisation"],
        "status": "Upcoming",
        "preparation_guidance": "Review previous session notes before the class."
    }

    todays_tasks = [
        {"id": "asg-001", "subject": "Mathematics", "task": "Quadratic Equations Practice", "time": "Due Today", "status": "Pending", "type": "assignment"},
        {"id": "quiz-001", "subject": "Mathematics", "task": "Quadratic Equations Quiz", "time": "15 Mins", "status": "Pending", "type": "quiz"}
    ]

    return student_response(
        data={
            "student": {
                "name": student_obj.student_name if student_obj else "Rahul Sharma",
                "email": student_obj.email if student_obj else "rahul@example.com",
                "school": student_obj.school if student_obj else "Class 10"
            },
            "summaryStats": summary_stats,
            "weeklyQuizProgress": weekly_quiz_progress,
            "topicPerformance": topic_performance,
            "weakTopicAlert": weak_topic_alert,
            "nextSession": next_session_data,
            "todaysTasks": todays_tasks
        },
        meta={"total": len(todays_tasks)}
    )


@student_bp.route('/profile', methods=['GET', 'PUT'])
@student_required
def handle_profile():
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student profile not found", 404)

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'student_name' in data or 'name' in data:
            student_obj.student_name = data.get('student_name') or data.get('name')
        if 'phone_no' in data or 'phone' in data:
            student_obj.phone_no = data.get('phone_no') or data.get('phone')
        if 'school' in data:
            student_obj.school = data.get('school')
        db.session.commit()
        return student_response(message="Profile updated successfully!")

    student_subjects = ["Mathematics", "Physics", "English"]
    parent_name = "Mr. Sharma"
    if student_obj.parent_id:
        parent = db.session.get(Parent, student_obj.parent_id)
        if parent:
            parent_name = parent.parent_name

    return student_response(
        data={
            "student": {
                "student_id": student_obj.student_id,
                "name": student_obj.student_name,
                "email": student_obj.email,
                "phone": student_obj.phone_no or "+91 98765 12345",
                "school": student_obj.school or "Class 10",
                "subjects": student_subjects,
                "parentName": parent_name
            }
        },
        meta={"total": len(student_subjects)}
    )


@student_bp.route('/quizzes', methods=['GET'])
@student_required
def get_quizzes():
    student_obj = get_current_student()
    quizzes = Quiz.query.order_by(Quiz.quiz_id.desc()).all()
    result = []
    for q in quizzes:
        subj = db.session.get(Subject, q.subject_id)
        last_attempt = QuizAttempt.query.filter_by(
            quiz_id=q.quiz_id, 
            student_id=student_obj.student_id if student_obj else 1
        ).order_by(QuizAttempt.attempted_at.desc()).first()
        
        q_count = QuizQuestion.query.filter_by(quiz_id=q.quiz_id).count()

        result.append({
            "quiz_id": q.quiz_id,
            "id": q.quiz_id,
            "title": q.title,
            "subject": subj.subject_name if subj else "Mathematics",
            "className": q.class_name or "Class 10",
            "topicName": q.topic_name or "Quadratic Equations",
            "questionCount": q_count or 5,
            "timeLimit": q.time_limit or 15,
            "maxAttempts": q.max_attempts or 1,
            "weekNumber": q.week_number or 1,
            "lastAttempt": last_attempt.attempted_at.strftime("%d %b %Y") if last_attempt else None,
            "score": round(last_attempt.score) if (last_attempt and last_attempt.score is not None) else None
        })
    return student_response(data=result)


@student_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@student_required
def get_quiz_detail(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return student_error("Quiz not found", 404)
    subj = db.session.get(Subject, quiz.subject_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    q_list = []
    for q in questions:
        correct_idx = 0
        if q.correct_option:
            correct_idx = ord(q.correct_option.upper()) - ord('A')
            if correct_idx < 0 or correct_idx > 3:
                correct_idx = 0
        q_list.append({
            "id": q.question_id,
            "questionId": q.question_id,
            "question": q.question,
            "option_a": q.option_a or "",
            "option_b": q.option_b or "",
            "option_c": q.option_c or "",
            "option_d": q.option_d or "",
            "options": [q.option_a or "", q.option_b or "", q.option_c or "", q.option_d or ""],
            "correctIndex": correct_idx,
            "correctOption": q.correct_option or "A",
            "explanation": q.explanation or f"Correct answer is option {q.correct_option}.",
            "topic": q.topic_name or quiz.topic_name or "Quadratic Equations",
            "difficulty": q.difficulty or "medium"
        })
    return student_response(data={
        "quiz_id": quiz.quiz_id,
        "id": quiz.quiz_id,
        "title": quiz.title,
        "subject": subj.subject_name if subj else "Mathematics",
        "className": quiz.class_name or "Class 10",
        "topicName": quiz.topic_name or "Quadratic Equations",
        "timeLimit": quiz.time_limit or 15,
        "maxAttempts": quiz.max_attempts or 1,
        "weekNumber": quiz.week_number or 1,
        "questions": q_list
    })


@student_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@student_required
def submit_quiz_attempt(quiz_id):
    student_obj = get_current_student()
    t_id = student_obj.student_id if student_obj else 1

    data = request.get_json() or {}
    submitted_answers = data.get("answers", {})  # { question_id: "A" or 0 }
    time_taken_seconds = data.get("time_taken_seconds", 300)

    quiz = db.session.get(Quiz, quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        return student_error("No questions found for quiz", 400)

    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    question_breakdown = []
    topic_correct = {}
    topic_total = {}

    for idx, q in enumerate(questions, 0):
        q_id_str = str(q.question_id)
        user_ans = (
            submitted_answers.get(q_id_str) or 
            submitted_answers.get(q.question_id) or 
            submitted_answers.get(str(idx)) or 
            submitted_answers.get(idx) or
            submitted_answers.get(str(idx + 1)) or
            submitted_answers.get(idx + 1)
        )
        
        # Convert index 0..3 to 'A'..'D' if needed
        if isinstance(user_ans, int):
            user_ans = chr(ord('A') + user_ans)
        elif user_ans:
            user_ans = str(user_ans).upper().strip()

        t_name = q.topic_name or quiz.topic_name or "General"
        topic_total[t_name] = topic_total.get(t_name, 0) + 1

        is_correct = False
        if not user_ans:
            skipped_count += 1
        elif user_ans == str(q.correct_option).upper().strip():
            correct_count += 1
            is_correct = True
            topic_correct[t_name] = topic_correct.get(t_name, 0) + 1
        else:
            wrong_count += 1

        question_breakdown.append({
            "questionId": q.question_id,
            "question": q.question,
            "userAnswer": user_ans or "Skipped",
            "correctOption": q.correct_option,
            "isCorrect": is_correct,
            "explanation": q.explanation or f"The correct answer is {q.correct_option}.",
            "topic": t_name
        })

    total_q = len(questions)
    score_percentage = round((correct_count / total_q) * 100, 1)

    # Compute updated topic performance map
    topic_scores = {}
    for top, tot in topic_total.items():
        corr = topic_correct.get(top, 0)
        topic_scores[top] = round((corr / tot) * 100)

    # Record or update attempt in DB
    attempt = QuizAttempt.query.filter_by(quiz_id=quiz_id, student_id=t_id).first()
    if attempt:
        attempt.score = score_percentage
        attempt.details_json = json.dumps(question_breakdown)
        attempt.topic_scores_json = json.dumps(topic_scores)
        attempt.attempted_at = datetime.utcnow()
    else:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=t_id,
            score=score_percentage,
            details_json=json.dumps(question_breakdown),
            topic_scores_json=json.dumps(topic_scores),
            attempted_at=datetime.utcnow()
        )
        db.session.add(attempt)

    # Notify Tutor
    tutor_id = quiz.tutor_id if quiz else 1
    notif = Notification(
        recipient_type='Tutor',
        recipient_id=tutor_id,
        title='Quiz Submitted',
        message=f"{student_obj.student_name if student_obj else 'Student'} completed quiz '{quiz.title if quiz else 'Quiz'}' with score {score_percentage}%.",
        notification_type='Quiz Result'
    )
    db.session.add(notif)
    db.session.commit()

    mins = time_taken_seconds // 60
    secs = time_taken_seconds % 60
    time_str = f"{mins}m {secs}s"

    return student_response(
        message="Quiz submitted and evaluated successfully!",
        data={
            "score": score_percentage,
            "correctCount": correct_count,
            "wrongCount": wrong_count,
            "skippedCount": skipped_count,
            "totalQuestions": total_q,
            "timeTaken": time_str,
            "topicPerformance": topic_scores,
            "questionBreakdown": question_breakdown
        }
    )


@student_bp.route('/ask-tutor', methods=['POST'])
@student_required
def ask_tutor_question():
    student_obj = get_current_student()
    data = request.get_json() or {}

    subject_name = data.get("subject", "Mathematics")
    topic_name = data.get("topic", "Quadratic Equations")
    question_text = data.get("question", "").strip()
    file_attachment = data.get("file_attachment") or data.get("attachment")

    if not question_text:
        return student_error("Question text is required.", 400)

    tutor = Tutor.query.first()
    t_id = tutor.tutor_id if tutor else 1

    doubt = Doubt(
        tutor_id=t_id,
        student_id=student_obj.student_id if student_obj else 1,
        subject=subject_name,
        topic=topic_name,
        question=question_text,
        file_attachment=file_attachment,
        status='Open',
        asked_at=datetime.utcnow()
    )
    db.session.add(doubt)

    # Notify Tutor
    notif = Notification(
        recipient_type='Tutor',
        recipient_id=t_id,
        title='New Student Doubt',
        message=f"Question on {subject_name} ({topic_name}): '{question_text[:50]}...'",
        notification_type='Doubt'
    )
    db.session.add(notif)
    db.session.commit()

    return student_response(
        message="Your question has been sent to your tutor!",
        data={
            "doubt_id": doubt.doubt_id,
            "subject": subject_name,
            "topic": topic_name,
            "question": question_text,
            "status": "Open",
            "askedAt": "Just now"
        }
    )