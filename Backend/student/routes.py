from datetime import date, datetime
from flask import jsonify, request, session, send_from_directory, current_app
from student import student_bp
from database import db
from models import (
    Student, Parent, Tutor, Subject, StudentSubject, Session, SessionUpdate,
    SessionBooking, Quiz, QuizQuestion, QuizAttempt, Assignment,
    AssignmentSubmission, StudyTip, StudyResource, FAQ, LearningProgress,
    MeetingRequest, Notification
)
from decorators import student_required
from utils import decode_jwt_token
from werkzeug.security import check_password_hash, generate_password_hash


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


def session_json(sess, booking_status=None):
    tutor = db.session.get(Tutor, sess.tutor_id)
    subject = db.session.get(Subject, sess.subject_id)
    update = SessionUpdate.query.filter_by(session_id=sess.session_id).first()
    return {
        "id": sess.session_id,
        "session_id": sess.session_id,
        "subject": subject.subject_name if subject else "General",
        "tutor": tutor.tutor_name if tutor else "Tutor",
        "tutor_id": sess.tutor_id,
        "type": sess.session_type or "Regular",
        "date": sess.session_date.strftime("%d %b %Y"),
        "date_iso": sess.session_date.isoformat(),
        "time": sess.start_time.strftime("%I:%M %p"),
        "start_time": sess.start_time.strftime("%H:%M"),
        "end_time": sess.end_time.strftime("%H:%M"),
        "duration": f"{max(1, int((datetime.combine(date.today(), sess.end_time) - datetime.combine(date.today(), sess.start_time)).seconds // 60))} min",
        "status": sess.status,
        "booking_status": booking_status,
        "meeting_url": sess.meeting_url,
        "meetingUrl": sess.meeting_url,
        "topics": [x.strip() for x in (update.topics_covered or "").split(",") if x.strip()] if update else [],
        "homework": update.homework_assigned if update else None,
    }


def assignment_json(assignment, student_id):
    sess = db.session.get(Session, assignment.session_id)
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.assignment_id, student_id=student_id
    ).first()
    return {
        "id": assignment.assignment_id,
        "assignment_id": assignment.assignment_id,
        "title": assignment.title,
        "description": assignment.description or "",
        "subject": subject_name(sess.subject_id) if sess else "General",
        "session_id": assignment.session_id,
        "dueDate": assignment.due_date.strftime("%d %b %Y") if assignment.due_date else None,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "status": submission.status if submission else "Not Started",
        "progress": submission.progress_percentage if submission else 0,
        "submissionDate": submission.submission_date.strftime("%d %b %Y %I:%M %p") if submission and submission.submission_date else None,
        "feedback": submission.tutor_feedback if submission else "",
    }


@student_bp.route('/dashboard', methods=['GET'])
@student_required
def dashboard():
    student = current_student()
    if not student:
        return fail("Student not found or not logged in", 404)
    sid = student.student_id

    bookings = SessionBooking.query.filter_by(student_id=sid).join(Session).all()
    # SessionBooking does not define a SQLAlchemy relationship named `session`,
    # so always resolve the linked Session explicitly by its foreign key.
    booking_rows = [(b, db.session.get(Session, b.session_id)) for b in bookings]
    booking_rows = [(b, sess) for b, sess in booking_rows if sess is not None]
    upcoming = [(b, sess) for b, sess in booking_rows if sess.status in ("Scheduled", "Rescheduled") and sess.session_date >= date.today()]
    completed = [(b, sess) for b, sess in booking_rows if sess.status == "Completed"]

    attempts = QuizAttempt.query.filter_by(student_id=sid).all()
    scores = [float(a.score) for a in attempts if a.score is not None]
    avg = round(sum(scores) / len(scores)) if scores else 0
    pending = AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == sid,
        AssignmentSubmission.status.in_(["Pending", "In Progress", "Late"])
    ).count()

    recent = sorted([a for a in attempts if a.attempted_at], key=lambda x: x.attempted_at, reverse=True)[:6]
    weekly = {"labels": [f"Quiz {i + 1}" for i in range(len(recent))][::-1], "data": [round(float(a.score)) for a in recent if a.score is not None][::-1]}
    subject_scores = {}
    for attempt in attempts:
        if attempt.score is None:
            continue
        quiz = db.session.get(Quiz, attempt.quiz_id)
        if quiz:
            subject_scores.setdefault(subject_name(quiz.subject_id), []).append(float(attempt.score))

    next_booking = sorted(upcoming, key=lambda row: (row[1].session_date, row[1].start_time))[0] if upcoming else None
    next_session = session_json(next_booking[1], next_booking[0].booking_status) if next_booking else {}

    tasks = []
    for sub in AssignmentSubmission.query.filter(
        AssignmentSubmission.student_id == sid,
        AssignmentSubmission.status.in_(["Pending", "In Progress", "Late"])
    ).all():
        assignment = db.session.get(Assignment, sub.assignment_id)
        if assignment:
            a = assignment_json(assignment, sid)
            tasks.append({"id": a["assignment_id"], "subject": a["subject"], "task": a["title"], "time": a["dueDate"] or "No due date", "status": a["status"]})
    tasks.sort(key=lambda x: x["time"] or "")
    meetings = []
    for m in MeetingRequest.query.filter_by(student_id=sid).order_by(MeetingRequest.meeting_date.asc()).limit(5).all():
        tutor = db.session.get(Tutor, m.tutor_id)
        meetings.append({"id": m.meeting_id, "date": m.meeting_date.isoformat(), "tutor": tutor.tutor_name if tutor else "Tutor", "link": m.meeting_link, "reason": m.meeting_reason, "status": m.status})

    return ok({
        "student": {"student_id": sid, "name": student.student_name, "email": student.email, "school": student.school},
        "summaryStats": [
            {"key": "upcoming", "label": "Upcoming Sessions", "value": len(upcoming), "subtitle": "Booked sessions", "icon": "CalendarDaysIcon", "tone": "blue"},
            {"key": "completed", "label": "Completed Sessions", "value": len(completed), "subtitle": "Your history", "icon": "CheckCircleIcon", "tone": "green"},
            {"key": "quizAvg", "label": "Quiz Average", "value": f"{avg}%", "subtitle": "All attempts", "icon": "ChartBarIcon", "tone": "green"},
            {"key": "homework", "label": "Homework Pending", "value": pending, "subtitle": "Assignments", "icon": "ClipboardDocumentListIcon", "tone": "amber"},
        ],
        "weeklyQuizProgress": weekly,
        "subjectQuizScores": {"labels": list(subject_scores), "data": [round(sum(v) / len(v)) for v in subject_scores.values()]},
        "nextSession": next_session,
        "todaysTasks": tasks,
        "meetings": meetings,
    }, meta={"total": len(tasks)})


@student_bp.route('/progress', methods=['GET'])
@student_required
def progress():
    student = current_student()
    if not student:
        return fail("Student not found", 404)
    records = LearningProgress.query.filter_by(student_id=student.student_id).all()
    completed = [r for r in records if r.session_completion_status == "Completed"]
    pace_counts = {}
    for r in records:
        if r.learning_pace:
            pace_counts[r.learning_pace] = pace_counts.get(r.learning_pace, 0) + 1
    return ok({
        "growthMetrics": [{"label": k, "value": v} for k, v in pace_counts.items()],
        "completedTopics": [{"id": r.progress_id, "sessionId": r.session_id, "status": r.session_completion_status, "pace": r.learning_pace, "remarks": r.tutor_remarks} for r in records],
        "completedCount": len(completed),
    }, meta={"total": len(records)})


@student_bp.route('/faqs', methods=['GET'])
@student_required
def faqs():
    q = (request.args.get("q") or "").strip().lower()
    query = FAQ.query.order_by(FAQ.faq_id.desc())
    items = []
    for f in query.all():
        if q and q not in f.question.lower() and q not in f.answer.lower():
            continue
        items.append({"id": f.faq_id, "faq_id": f.faq_id, "q": f.question, "a": f.answer, "category": f.category or "General"})
    return ok({"faqs": items}, meta={"total": len(items)})


@student_bp.route('/quizzes', methods=['GET'])
@student_required
def quizzes():
    student = current_student()
    enrolled = {x.subject_id for x in StudentSubject.query.filter_by(student_id=student.student_id).all()}
    qs = Quiz.query.order_by(Quiz.created_at.desc()).all()
    items = []
    for q in qs:
        if enrolled and q.subject_id not in enrolled:
            continue
        attempt = QuizAttempt.query.filter_by(quiz_id=q.quiz_id, student_id=student.student_id).first()
        items.append({"quiz_id": q.quiz_id, "subject": subject_name(q.subject_id), "title": q.title, "weekNumber": q.week_number, "lastAttempt": attempt.attempted_at.strftime("%d %b %Y") if attempt and attempt.attempted_at else None, "score": round(float(attempt.score)) if attempt and attempt.score is not None else None})
    return ok({"quizzes": items}, meta={"total": len(items)})


@student_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@student_required
def quiz_details(quiz_id):
    student = current_student()
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return fail("Quiz not found", 404)
    enrolled = StudentSubject.query.filter_by(student_id=student.student_id, subject_id=quiz.subject_id).first()
    if not enrolled:
        return fail("You are not enrolled in this subject", 403)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.question_id).all()
    return ok({"quiz": {"quiz_id": quiz.quiz_id, "title": quiz.title, "subject": subject_name(quiz.subject_id), "weekNumber": quiz.week_number}, "questions": [{"id": q.question_id, "question": q.question, "options": [q.option_a, q.option_b, q.option_c, q.option_d]} for q in questions]}, meta={"total": len(questions)})


@student_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@student_required
def submit_quiz(quiz_id):
    student = current_student()
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return fail("Quiz not found", 404)
    if not StudentSubject.query.filter_by(student_id=student.student_id, subject_id=quiz.subject_id).first():
        return fail("You are not enrolled in this subject", 403)
    if QuizAttempt.query.filter_by(quiz_id=quiz_id, student_id=student.student_id).first():
        return fail("You have already attempted this quiz", 409)
    answers = (request.get_json(silent=True) or {}).get("answers") or {}
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return fail("This quiz has no questions yet", 400)
    correct = 0
    for q in questions:
        answer = answers.get(str(q.question_id), answers.get(q.question_id))
        if answer and str(answer).upper() == str(q.correct_option or "").upper():
            correct += 1
    score = round((correct / len(questions)) * 100, 2)
    attempt = QuizAttempt(quiz_id=quiz_id, student_id=student.student_id, score=score)
    db.session.add(attempt)
    db.session.commit()
    return ok({"score": score, "correctCount": correct, "totalQuestions": len(questions)}, message="Quiz submitted")


@student_bp.route('/booking-slots', methods=['GET'])
@student_required
def booking_slots():
    student = current_student()
    booked_ids = {b.session_id for b in SessionBooking.query.filter_by(student_id=student.student_id).all() if b.booking_status != "Cancelled"}
    sessions = Session.query.filter(Session.session_date >= date.today(), Session.status.in_(["Scheduled", "Rescheduled"])).order_by(Session.session_date, Session.start_time).all()
    regular, one = [], []
    for s in sessions:
        slot = session_json(s, "Confirmed" if s.session_id in booked_ids else None)
        slot.update({"id": s.session_id, "booked": s.session_id in booked_ids, "available": s.session_id not in booked_ids, "seats": 0 if s.session_id in booked_ids else 1})
        (one if s.session_type == "One-to-One" else regular).append(slot)
    return ok({"bookingSlots": {"regular": regular, "oneToOne": one}}, meta={"total": len(regular) + len(one)})


@student_bp.route('/book-session', methods=['POST'])
@student_required
def book_session():
    student = current_student()
    data = request.get_json(silent=True) or {}
    try:
        session_id = int(data.get("session_id"))
    except (TypeError, ValueError):
        return fail("session_id is required", 400)
    sess = db.session.get(Session, session_id)
    if not sess or sess.status not in ("Scheduled", "Rescheduled") or sess.session_date < date.today():
        return fail("Session is not available for booking", 400)
    existing = SessionBooking.query.filter_by(session_id=session_id, student_id=student.student_id).first()
    if existing and existing.booking_status != "Cancelled":
        return fail("You have already booked this session", 409)
    if existing:
        existing.booking_status = "Confirmed"
    else:
        existing = SessionBooking(session_id=session_id, student_id=student.student_id, booking_status="Confirmed")
        db.session.add(existing)
    db.session.commit()
    return ok({"booked_session_id": session_id, "booking_id": existing.booking_id, "status": existing.booking_status}, message="Session booked")


@student_bp.route('/reschedule-session', methods=['POST'])
@student_required
def reschedule_session():
    student = current_student()
    data = request.get_json(silent=True) or {}
    try:
        current_id = int(data.get("current_session_id")); target_id = int(data.get("target_session_id"))
    except (TypeError, ValueError):
        return fail("current_session_id and target_session_id are required")
    current = SessionBooking.query.filter_by(session_id=current_id, student_id=student.student_id).first()
    target = db.session.get(Session, target_id)
    if not current or current.booking_status == "Cancelled":
        return fail("Current booking not found", 404)
    if not target or target.status not in ("Scheduled", "Rescheduled") or target.session_date < date.today():
        return fail("Target session is not available", 400)
    if SessionBooking.query.filter_by(session_id=target_id, student_id=student.student_id).first():
        return fail("Target session is already booked", 409)
    current.booking_status = "Cancelled"
    db.session.add(SessionBooking(session_id=target_id, student_id=student.student_id, booking_status="Confirmed"))
    db.session.commit()
    return ok(message="Session rescheduled")


@student_bp.route('/sessions', methods=['GET'])
@student_required
def sessions():
    student = current_student()
    bookings = SessionBooking.query.filter_by(student_id=student.student_id).join(Session).order_by(Session.session_date, Session.start_time).all()
    upcoming, completed = [], []
    for b in bookings:
        sess = db.session.get(Session, b.session_id)
        if not sess:
            continue
        item = session_json(sess, b.booking_status)
        if sess.status == "Completed" or sess.session_date < date.today():
            completed.append(item)
        else:
            upcoming.append(item)
    return ok({"upcoming": upcoming, "completed": completed, "sessions": upcoming + completed}, meta={"total": len(upcoming) + len(completed)})


@student_bp.route('/upcoming-sessions', methods=['GET'])
@student_required
def upcoming_sessions():
    data, _, = _student_upcoming()
    return ok({"upcoming_sessions": data}, meta={"total": len(data)})


def _student_upcoming():
    student = current_student()
    bookings = SessionBooking.query.filter_by(student_id=student.student_id).join(Session).all()
    items = []
    for b in bookings:
        sess = db.session.get(Session, b.session_id)
        if sess and sess.status in ("Scheduled", "Rescheduled") and sess.session_date >= date.today():
            items.append(session_json(sess, b.booking_status))
    items.sort(key=lambda x: (x["date_iso"], x["start_time"]))
    return items, student, bookings


@student_bp.route('/next-session', methods=['GET'])
@student_required
def next_session():
    items, _, _ = _student_upcoming()
    return ok({"nextSession": items[0] if items else {}})


@student_bp.route('/study-tips', methods=['GET'])
@student_required
def study_tips():
    student = current_student()
    tips = StudyTip.query.filter_by(student_id=student.student_id).order_by(StudyTip.created_at.desc()).all()
    data = [{"id": t.tip_id, "subject": subject_name(db.session.get(Session, t.session_id).subject_id) if db.session.get(Session, t.session_id) else "General", "tip": t.tip_text, "createdAt": t.created_at.isoformat() if t.created_at else None} for t in tips]
    return ok({"studyTips": data}, meta={"total": len(data)})


@student_bp.route('/assignments', methods=['GET'])
@student_required
def assignments():
    student = current_student()
    rows = Assignment.query.join(Session).filter(Session.tutor_id.isnot(None)).order_by(Assignment.due_date).all()
    data = [assignment_json(a, student.student_id) for a in rows if SessionBooking.query.filter_by(session_id=a.session_id, student_id=student.student_id).first() or StudentSubject.query.filter_by(student_id=student.student_id, subject_id=db.session.get(Session, a.session_id).subject_id).first()]
    return ok({"assignments": data}, meta={"total": len(data)})


@student_bp.route('/assignments/<int:assignment_id>/update-progress', methods=['POST'])
@student_required
def update_assignment_progress(assignment_id):
    student = current_student(); assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return fail("Assignment not found", 404)
    sess = db.session.get(Session, assignment.session_id)
    if not sess or not StudentSubject.query.filter_by(student_id=student.student_id, subject_id=sess.subject_id).first():
        return fail("Assignment is not available to you", 403)
    data = request.get_json(silent=True) or {}
    try: progress = max(0, min(100, int(data.get("progress", 0))))
    except (TypeError, ValueError): return fail("progress must be a number")
    sub = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student.student_id).first()
    if not sub:
        sub = AssignmentSubmission(assignment_id=assignment_id, student_id=student.student_id)
        db.session.add(sub)
    sub.progress_percentage = progress
    sub.status = "Completed" if progress >= 100 else ("In Progress" if progress > 0 else "Pending")
    sub.submission_date = datetime.utcnow()
    db.session.commit()
    return ok({"assignment_id": assignment_id, "progress": progress, "status": sub.status})


@student_bp.route('/assignments/<int:assignment_id>/submit', methods=['POST'])
@student_required
def submit_assignment(assignment_id):
    student = current_student(); assignment = db.session.get(Assignment, assignment_id)
    if not assignment: return fail("Assignment not found", 404)
    sess = db.session.get(Session, assignment.session_id)
    if not sess or not StudentSubject.query.filter_by(student_id=student.student_id, subject_id=sess.subject_id).first(): return fail("Assignment is not available to you", 403)
    sub = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student.student_id).first()
    if not sub:
        sub = AssignmentSubmission(assignment_id=assignment_id, student_id=student.student_id)
        db.session.add(sub)
    sub.progress_percentage = 100
    sub.status = "Submitted"
    sub.submission_date = datetime.utcnow()
    db.session.commit()
    return ok({"assignment_id": assignment_id, "status": sub.status, "progress": 100}, message="Assignment submitted")


@student_bp.route('/timetable', methods=['GET'])
@student_required
def timetable():
    student = current_student(); days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    classes = {d: [] for d in days}
    bookings = SessionBooking.query.filter_by(student_id=student.student_id).join(Session).all()
    for b in bookings:
        s = db.session.get(Session, b.session_id)
        if not s:
            continue
        day = s.session_date.strftime("%A")
        if day in classes:
            classes[day].append({"subject": subject_name(s.subject_id), "time": f"{s.start_time.strftime('%I:%M %p')} – {s.end_time.strftime('%I:%M %p')}", "tutor": db.session.get(Tutor, s.tutor_id).tutor_name if db.session.get(Tutor, s.tutor_id) else "Tutor", "status": s.status, "session_id": s.session_id})
    return ok({"days": days, "classes": classes})


@student_bp.route('/resources', methods=['GET'])
@student_required
def resources():
    student = current_student(); rows = StudyResource.query.join(Session).order_by(StudyResource.resource_id.desc()).all()
    data = []
    for r in rows:
        sess = db.session.get(Session, r.session_id)
        if not sess: continue
        if not SessionBooking.query.filter_by(session_id=sess.session_id, student_id=student.student_id).first() and not StudentSubject.query.filter_by(student_id=student.student_id, subject_id=sess.subject_id).first(): continue
        data.append({"resource_id": r.resource_id, "session_id": r.session_id, "resource_title": r.resource_title, "resource_type": r.resource_type, "resource_link": r.resource_link, "subject": subject_name(sess.subject_id)})
    return ok({"resources": data}, meta={"total": len(data)})


@student_bp.route('/profile', methods=['GET', 'PUT'])
@student_required
def profile():
    student = current_student()
    if not student: return fail("Student profile not found", 404)
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        if "name" in data or "student_name" in data: student.student_name = (data.get("name") or data.get("student_name") or student.student_name).strip()
        if "phone" in data or "phone_no" in data: student.phone_no = data.get("phone") if "phone" in data else data.get("phone_no")
        if "school" in data: student.school = data.get("school")
        db.session.commit(); return ok(message="Profile updated successfully")
    subjects = [subject_name(x.subject_id) for x in StudentSubject.query.filter_by(student_id=student.student_id).all()]
    parent = db.session.get(Parent, student.parent_id) if student.parent_id else None
    return ok({"student": {"student_id": student.student_id, "name": student.student_name, "email": student.email, "phone": student.phone_no, "school": student.school, "subjects": subjects, "parentName": parent.parent_name if parent else None, "parentId": student.parent_id}})


@student_bp.route('/meetings', methods=['GET'])
@student_required
def meetings():
    student = current_student(); rows = MeetingRequest.query.filter_by(student_id=student.student_id).order_by(MeetingRequest.meeting_date.desc()).all()
    return ok({"meetings": [{"meeting_id": m.meeting_id, "date": m.meeting_date.isoformat(), "meeting_link": m.meeting_link, "reason": m.meeting_reason, "status": m.status, "tutor": db.session.get(Tutor, m.tutor_id).tutor_name if db.session.get(Tutor, m.tutor_id) else "Tutor"} for m in rows]})


@student_bp.route('/notifications', methods=['GET'])
@student_required
def notifications():
    student = current_student(); rows = Notification.query.filter_by(recipient_type="Student", recipient_id=student.student_id).order_by(Notification.created_at.desc()).all()
    return ok({"notifications": [{"id": n.notification_id, "title": n.title, "message": n.message, "type": n.notification_type, "isRead": n.is_read, "createdAt": n.created_at.isoformat()} for n in rows]})


@student_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@student_required
def mark_notification(notification_id):
    student = current_student(); n = Notification.query.filter_by(notification_id=notification_id, recipient_type="Student", recipient_id=student.student_id).first()
    if not n: return fail("Notification not found", 404)
    n.is_read = True; db.session.commit(); return ok(message="Notification marked as read")


@student_bp.route('/profile/password', methods=['PUT'])
@student_required
def change_password():
    student=current_student()
    data=request.get_json(silent=True) or {}
    current=data.get('currentPassword',''); new=data.get('newPassword',''); confirm=data.get('confirmPassword','')
    if not current or not new or not confirm: return fail('All password fields are required')
    if not check_password_hash(student.password_hash,current): return fail('Current password is incorrect',400)
    if len(new)<8: return fail('New password must contain at least 8 characters')
    if new!=confirm: return fail('New passwords do not match')
    student.password_hash=generate_password_hash(new);db.session.commit();return ok(message='Password changed successfully')
