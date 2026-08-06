from flask import jsonify, request, session
from datetime import datetime, date
from student import student_bp
from database import db
from models import (
    Student, Parent, Tutor, Subject, StudentSubject, Session, SessionUpdate, SessionBooking,
    Quiz, QuizQuestion, QuizAttempt, Assignment, AssignmentSubmission,
    StudyTip, StudyResource, FAQ, LearningProgress
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

    return None


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
        quiz_avg_str = "0%"

    homework_pending = AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == student_id,
        AssignmentSubmission.status.in_(['Pending', 'In Progress'])
    ).count()

    summary_stats = [
        {"key": "upcoming", "label": "Upcoming Sessions", "value": upcoming_count, "subtitle": "Next 7 days", "icon": "CalendarDaysIcon", "tone": "blue"},
        {"key": "completed", "label": "Completed Sessions", "value": completed_count, "subtitle": "This term", "icon": "CheckCircleIcon", "tone": "green"},
        {"key": "quizAvg", "label": "Quiz Average", "value": quiz_avg_str, "subtitle": "Last 6 weeks", "icon": "ChartBarIcon", "tone": "green"},
        {"key": "homework", "label": "Homework Pending", "value": homework_pending, "subtitle": "Interactive activities", "icon": "ClipboardDocumentListIcon", "tone": "amber"}
    ]

    recent_attempts = QuizAttempt.query.filter_by(student_id=student_id).order_by(
        QuizAttempt.attempted_at.desc()
    ).limit(6).all()

    weekly_quiz_progress = {
        "labels": [f"Week {i+1}" for i in range(len(recent_attempts))][::-1],
        "data": [round(a.score) for a in recent_attempts if a.score is not None][::-1]
    }

    subject_quiz_scores = {"labels": [], "data": []}
    subject_score_map = {}
    for attempt in attempts:
        quiz = db.session.get(Quiz, attempt.quiz_id)
        if not quiz or attempt.score is None:
            continue
        subject = db.session.get(Subject, quiz.subject_id)
        subject_name = subject.subject_name if subject else "General"
        subject_score_map.setdefault(subject_name, []).append(attempt.score)

    if subject_score_map:
        subject_quiz_scores = {
            "labels": list(subject_score_map.keys()),
            "data": [round(sum(scores) / len(scores)) for scores in subject_score_map.values()]
        }

    next_booking = SessionBooking.query.filter_by(student_id=student_id).join(Session).filter(
        Session.status == 'Scheduled',
        Session.session_date >= date.today()
    ).order_by(Session.session_date.asc(), Session.start_time.asc()).first()

    next_session_data = {}
    if next_booking and next_booking.session_id:
        sess = db.session.get(Session, next_booking.session_id)
        if sess:
            tutor_obj = db.session.get(Tutor, sess.tutor_id)
            subj_obj = db.session.get(Subject, sess.subject_id)
            update_obj = SessionUpdate.query.filter_by(session_id=sess.session_id).first()
            topics_list = []
            if update_obj and update_obj.topics_covered:
                topics_list = [t.strip() for t in update_obj.topics_covered.split(',') if t.strip()]

            next_session_data = {
                "session_id": sess.session_id,
                "subject": subj_obj.subject_name if subj_obj else None,
                "tutor": tutor_obj.tutor_name if tutor_obj else None,
                "type": sess.session_type,
                "date": sess.session_date.strftime("%d %b %Y"),
                "time": sess.start_time.strftime("%I:%M %p"),
                "duration": "60 minutes",
                "topics": topics_list,
                "status": "Upcoming",
                "preparation_guidance": "Review previous session notes before the class."
            }

    todays_tasks = []
    pending_submissions = AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == student_id,
        AssignmentSubmission.status.in_(["Pending", "In Progress"])
    ).all()

    for sub in pending_submissions:
        assignment = db.session.get(Assignment, sub.assignment_id)
        if not assignment:
            continue
        sess = db.session.get(Session, assignment.session_id)
        subject = db.session.get(Subject, sess.subject_id) if sess else None
        due_text = assignment.due_date.strftime("%d %b %Y") if assignment.due_date else "No due date"

        todays_tasks.append({
            "id": f"task-{assignment.assignment_id}",
            "subject": subject.subject_name if subject else "General",
            "task": assignment.title,
            "time": due_text,
            "status": sub.status
        })

    return student_response(
        data={
            "student": {
                "name": student_obj.student_name,
                "email": student_obj.email,
                "school": student_obj.school
            },
            "summaryStats": summary_stats,
            "weeklyQuizProgress": weekly_quiz_progress,
            "subjectQuizScores": subject_quiz_scores,
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

    student_subjects = []
    subject_links = StudentSubject.query.filter_by(student_id=student_obj.student_id).all()
    for link in subject_links:
        subj = db.session.get(Subject, link.subject_id)
        if subj:
            student_subjects.append(subj.subject_name)

    parent_name = None
    if student_obj.parent_id:
        parent = db.session.get(Parent, student_obj.parent_id)
        parent_name = parent.parent_name if parent else None

    return student_response(
        data={
            "student": {
                "student_id": student_obj.student_id,
                "name": student_obj.student_name,
                "email": student_obj.email,
                "phone": student_obj.phone_no,
                "school": student_obj.school,
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
            student_id=student_obj.student_id if student_obj else 0
        ).order_by(QuizAttempt.attempted_at.desc()).first()
        
        result.append({
            "quiz_id": q.quiz_id,
            "title": q.title,
            "subject": subj.subject_name if subj else "General",
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
            "question": q.question,
            "options": [q.option_a or "", q.option_b or "", q.option_c or "", q.option_d or ""],
            "correctIndex": correct_idx,
            "correctOption": q.correct_option,
            "difficulty": q.difficulty or "medium"
        })
    return student_response(data={
        "quiz_id": quiz.quiz_id,
        "title": quiz.title,
        "subject": subj.subject_name if subj else "General",
        "weekNumber": quiz.week_number or 1,
        "questions": q_list
    })


@student_bp.route('/quizzes/<int:quiz_id>/attempt', methods=['POST'])
@student_required
def record_quiz_attempt(quiz_id):
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found", 404)
    data = request.get_json() or {}
    score_val = data.get("score", 0)
    
    attempt = QuizAttempt.query.filter_by(quiz_id=quiz_id, student_id=student_obj.student_id).first()
    if attempt:
        attempt.score = score_val
        attempt.attempted_at = datetime.utcnow()
    else:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_obj.student_id,
            score=score_val,
            attempted_at=datetime.utcnow()
        )
        db.session.add(attempt)
    db.session.commit()
    return student_response(message="Quiz attempt recorded successfully!")