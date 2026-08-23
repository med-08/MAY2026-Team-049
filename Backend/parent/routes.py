import json
from datetime import datetime, date, timezone
from flask import jsonify, request, session, current_app
from parent import parent_bp
from database import db
from models import (
    Parent, Student, WeeklySummary, Quiz, QuizAttempt, AttendanceRecord, 
    TeachingPlan, MeetingRequest, Tutor, Session, SessionBooking, 
    Subject, StudentSubject, Message, Notification, LearningProgress
)
from decorators import parent_required
from utils import decode_jwt_token
from google_meet import create_meeting_space, GoogleMeetNotConfigured
from schedule import meeting_lifecycle, _local_now
from ai_service import AIConfigError, AIResponseError, AIServiceError, generate_text


def current_parent():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        payload = decode_jwt_token(auth.split(' ', 1)[1])
        if payload and payload.get('role') == 'Parent':
            p = db.session.get(Parent, payload.get('user_id'))
            if p:
                return p
    uid = session.get('user_id')
    if uid and session.get('role') == 'Parent':
        return db.session.get(Parent, uid)
    return None


def ok(data=None, message=None, status=200):
    p = {'success': True, 'status': 'success'}
    if message:
        p['message'] = message
    if data is not None:
        p['data'] = data
    return jsonify(p), status


def fail(message, status=400):
    return jsonify({'success': False, 'status': 'error', 'message': message}), status


@parent_bp.route('/health', methods=['GET'])
def health_check():
    return ok(message='Parent API blueprint working!')


@parent_bp.route('/profile/<int:parent_id>', methods=['GET', 'PUT'])
@parent_required
def profile(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    if request.method == 'PUT':
        d = request.get_json(silent=True) or {}
        if 'parent_name' in d:
            parent.parent_name = d['parent_name']
        if 'phone_no' in d:
            parent.phone_no = d['phone_no']
        db.session.commit()
        return ok({'parent_id': parent.parent_id, 'parent_name': parent.parent_name, 'email': parent.email, 'phone_no': parent.phone_no}, 'Parent profile updated')
    children = Student.query.filter_by(parent_id=parent_id).all()
    linked_children = []
    for c in children:
        bookings = SessionBooking.query.filter_by(student_id=c.student_id, booking_status='Confirmed').all()
        tutor_ids = set()
        for b in bookings:
            sess = db.session.get(Session, b.session_id)
            if sess and sess.tutor_id:
                tutor_ids.add(sess.tutor_id)
        tutors = []
        for tid in sorted(tutor_ids):
            tutor = db.session.get(Tutor, tid)
            if tutor:
                tutors.append({'tutor_id': tutor.tutor_id, 'tutor_name': tutor.tutor_name, 'email': tutor.email})
        linked_children.append({
            'student_id': c.student_id, 'student_name': c.student_name, 'email': c.email, 'status': c.status,
            'tutor_id': tutors[0]['tutor_id'] if len(tutors) == 1 else None,
            'tutors': tutors,
        })
    return ok({'parent_id': parent.parent_id, 'parent_name': parent.parent_name, 'email': parent.email, 'phone_no': parent.phone_no, 'status': parent.status, 'linked_children': linked_children})


@parent_bp.route('/overview/<int:parent_id>', methods=['GET'])
@parent_required
def overview(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    children = Student.query.filter_by(parent_id=parent_id).all()
    ids = [c.student_id for c in children]
    latest = WeeklySummary.query.filter(WeeklySummary.student_id.in_(ids)).order_by(WeeklySummary.created_at.desc()).first() if ids else None
    return ok({'parent_id': parent.parent_id, 'parent_name': parent.parent_name, 'total_children': len(children), 'children': [{'student_id': c.student_id, 'student_name': c.student_name, 'status': c.status} for c in children], 'latest_summary': {'topics_taught': latest.topics_taught if latest else 'No summary yet', 'homework': latest.homework_summary if latest else 'No homework recorded', 'areas_for_improvement': latest.areas_for_improvement if latest else 'No remarks yet'}})


@parent_bp.route('/meeting-request', methods=['POST'])
@parent_required
def request_meeting():
    parent = current_parent()
    d = request.get_json(silent=True) or {}
    if not parent:
        return fail('Parent not logged in', 401)
    try:
        parent_id = int(d.get('parent_id'))
        tutor_id = int(d.get('tutor_id'))
        student_id = int(d.get('student_id'))
    except (TypeError, ValueError):
        return fail('parent_id, tutor_id and student_id are required')
    include_student = bool(d.get('include_student', True))
    if parent_id != parent.parent_id:
        return fail('Unauthorized parent access', 403)
    child = db.session.get(Student, student_id)
    tutor = db.session.get(Tutor, tutor_id)
    if not child or child.parent_id != parent.parent_id:
        return fail('Child is not linked to this parent', 403)
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

    # Prevent duplicate requests for the same parent/tutor/child/time.
    # A request already waiting for approval or already accepted should not
    # create another Session/MeetingRequest record.
    duplicate_query = MeetingRequest.query.filter(
        MeetingRequest.parent_id == parent.parent_id,
        MeetingRequest.tutor_id == tutor.tutor_id,
        MeetingRequest.meeting_date == start_dt,
        MeetingRequest.status.in_(['Pending Approval', 'Scheduled', 'Reschedule Requested'])
    )
    if duplicate_query.first():
        return fail('A meeting request for this tutor and time already exists.', 409)

    subject_row = StudentSubject.query.filter_by(student_id=child.student_id).first()
    if not subject_row:
        return fail('Child has no registered subject')
    subject = db.session.get(Subject, subject_row.subject_id)
    # Parent scheduling must use an existing tutor/student relationship or a
    # tutor who is configured for the child's enrolled subject.
    related = Session.query.join(SessionBooking, SessionBooking.session_id == Session.session_id).filter(
        Session.tutor_id == tutor.tutor_id, SessionBooking.student_id == child.student_id
    ).first()
    if not related:
        try:
            configured = {str(x).strip().lower() for x in __import__('json').loads(tutor.subjects_json or '[]')}
        except Exception:
            configured = set()
        if not subject or subject.subject_name.strip().lower() not in configured:
            return fail('This tutor is not associated with the selected child/subject', 403)

    conflicts = Session.query.filter(Session.tutor_id == tutor.tutor_id, Session.session_date == start_dt.date()).all()
    for existing in conflicts:
        if existing.status != 'Cancelled' and start_dt.time() < existing.end_time and end_dt.time() > existing.start_time:
            return fail('The tutor already has another session scheduled during this time.', 409)

    # Reuse the existing Session + SessionBooking system. Parent-created
    # meetings are not stored in a separate parent-only schedule.
    session_obj = Session(
        tutor_id=tutor.tutor_id, subject_id=subject_row.subject_id,
        session_date=start_dt.date(), start_time=start_dt.time(), end_time=end_dt.time(),
        session_type='One-to-One', status='Scheduled'
    )
    db.session.add(session_obj)
    db.session.flush()
    if include_student:
        db.session.add(SessionBooking(session_id=session_obj.session_id, student_id=child.student_id, booking_status='Confirmed'))

    # A pending request does not need a Meet resource yet. The single
    # persisted meeting link is created/confirmed atomically during approval.
    meeting_link = None
    session_obj.meeting_url = None
    m = MeetingRequest(
        tutor_id=tutor.tutor_id, student_id=(child.student_id if include_student else None), parent_id=parent.parent_id,
        meeting_date=start_dt, meeting_link=meeting_link, meeting_reason=d.get('notes', ''),
        session_id=session_obj.session_id, status='Pending Approval'
    )
    db.session.add(m)

    display_date = start_dt.strftime('%d %b %Y')
    display_start = start_dt.strftime('%I:%M %p')
    display_end = end_dt.strftime('%I:%M %p')
    db.session.add(Notification(
        recipient_type='Tutor', recipient_id=tutor.tutor_id,
        title=f'{subject.subject_name} meeting request',
        message=f'{parent.parent_name} requested a one-on-one {subject.subject_name} meeting with {child.student_name} for {display_date}, {display_start}–{display_end}.',
        notification_type='Meeting Request', action_url=f'/tutor/schedule?session_id={session_obj.session_id}'
    ))
    db.session.commit()
    return ok({
        'meeting_id': m.meeting_id, 'session_id': session_obj.session_id,
        'meeting_date': m.meeting_date.isoformat(), 'meeting_link': meeting_link, 'status': m.status
    }, 'Meeting scheduled', 201)


@parent_bp.route('/meetings/<int:parent_id>', methods=['GET'])
@parent_required
def meetings(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    rows = MeetingRequest.query.filter_by(parent_id=parent_id).order_by(MeetingRequest.meeting_date.desc()).all()
    data = []
    for m in rows:
        st = db.session.get(Student, m.student_id)
        t = db.session.get(Tutor, m.tutor_id)
        sess = db.session.get(Session, m.session_id) if m.session_id else None
        lifecycle = meeting_lifecycle(sess) if sess else {'status': m.status, 'can_join': bool(m.meeting_link), 'can_start': False, 'can_end': False}
        if m.status == 'Pending Approval':
            lifecycle = {**lifecycle, 'status': 'Awaiting Tutor Approval', 'can_join': False}
        elif m.status == 'Scheduled' and lifecycle.get('status') == 'Meeting Not Started':
            link = sess.meeting_url if sess and sess.meeting_url else m.meeting_link
            # Parent-created ONE-TO-ONE meetings expose the persisted meeting
            # immediately after approval; regular sessions still require the
            # tutor to start them first.
            can_join = bool(link) and sess and sess.session_type == 'One-to-One'
            lifecycle = {**lifecycle, 'status': 'Request Accepted', 'can_join': can_join}
        elif m.status in ('Denied', 'Reschedule Requested'):
            lifecycle = {**lifecycle, 'status': m.status, 'can_join': False}
        feedback = Message.query.filter(
            Message.sender_type == 'Tutor',
            Message.sender_id == m.tutor_id,
            Message.receiver_type == 'Parent',
            Message.receiver_id == parent_id,
            Message.subject.in_([f'{db.session.get(Subject, sess.subject_id).subject_name if sess else "General"} meeting denied',
                                f'{db.session.get(Subject, sess.subject_id).subject_name if sess else "General"} meeting change requested'])
        ).order_by(Message.sent_at.desc()).first()
        data.append({
            'meeting_id': m.meeting_id, 'student_id': m.student_id, 'student_name': st.student_name if st else None,
            'tutor_id': m.tutor_id, 'tutor_name': t.tutor_name if t else None,
            'meeting_date': m.meeting_date.isoformat(), 'meeting_link': (sess.meeting_url if sess and sess.meeting_url else m.meeting_link),
            'meeting_reason': m.meeting_reason, 'status': m.status, 'session_id': m.session_id,
            'tutor_message': feedback.message if feedback else None,
            'meeting_lifecycle': lifecycle['status'], 'can_join': lifecycle['can_join'], 'can_start': lifecycle.get('can_start', False), 'can_end': bool(sess and sess.session_type == 'One-to-One' and sess.status == 'Live'), 'meeting_started_at': sess.meeting_started_at.isoformat() if sess and sess.meeting_started_at else None,
            'meeting_ended_at': sess.meeting_ended_at.isoformat() if sess and sess.meeting_ended_at else None,
            'meeting_duration_seconds': sess.meeting_duration_seconds if sess else None,
            'subject': db.session.get(Subject, sess.subject_id).subject_name if sess and db.session.get(Subject, sess.subject_id) else 'General',
            'session_type': sess.session_type if sess else 'One-to-One',
            'start_time': sess.start_time.strftime('%H:%M') if sess else m.meeting_date.strftime('%H:%M'),
            'end_time': sess.end_time.strftime('%H:%M') if sess else None,
        })
    return ok(data)


@parent_bp.route('/attendance-query', methods=['POST'])
@parent_required
def attendance_query():
    parent = current_parent()
    d = request.get_json(silent=True) or {}
    try:
        student_id = int(d.get('student_id'))
        session_id = int(d.get('session_id'))
    except (TypeError, ValueError):
        return fail('student_id and session_id are required')
    child = db.session.get(Student, student_id)
    sess = db.session.get(Session, session_id)
    if not child or child.parent_id != parent.parent_id:
        return fail('Child not found for this parent', 403)
    if not sess:
        return fail('Session not found', 404)
    booking = SessionBooking.query.filter_by(session_id=session_id, student_id=student_id, booking_status='Confirmed').first()
    if not booking:
        return fail('Child is not booked for this session', 403)
    record = AttendanceRecord.query.filter_by(tutor_id=sess.tutor_id, student_id=student_id, session_id=session_id).first()
    if not record:
        record = AttendanceRecord(tutor_id=sess.tutor_id, student_id=student_id, session_id=session_id, status='Pending', date=sess.session_date)
        db.session.add(record)
    if record.status == 'Pending':
        existing = Notification.query.filter_by(recipient_type='Tutor', recipient_id=sess.tutor_id, notification_type='Attendance Query', is_read=False).filter(Notification.action_url == f'/tutor/attendance?session_id={session_id}&student_id={student_id}').first()
        if not existing:
            tutor = db.session.get(Tutor, sess.tutor_id)
            subject = db.session.get(Subject, sess.subject_id)
            db.session.add(Notification(
                recipient_type='Tutor', recipient_id=sess.tutor_id,
                title='Attendance confirmation requested',
                message=f"{parent.parent_name} requested confirmation of {child.student_name}'s attendance for {subject.subject_name if subject else 'the session'} on {sess.session_date.strftime('%d %b %Y')}.",
                notification_type='Attendance Query',
                action_url=f'/tutor/attendance?session_id={session_id}&student_id={student_id}'
            ))
    db.session.commit()
    return ok({'attendance': {'session_id': session_id, 'student_id': student_id, 'status': record.status}}, 'Attendance confirmation request sent')


@parent_bp.route('/child-progress/<int:parent_id>/<int:student_id>', methods=['GET'])
@parent_required
def child_progress(parent_id, student_id):
    parent = current_parent()
    child = db.session.get(Student, student_id)
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    if not child or child.parent_id != parent_id:
        return fail('Child not found for this parent', 404)
    
    attendance = AttendanceRecord.query.filter_by(student_id=student_id).all()
    final_attendance = [a for a in attendance if a.status in {'Present', 'Absent', 'Late'}]
    present = sum(a.status == 'Present' for a in final_attendance)
    rate = round(present / len(final_attendance) * 100) if final_attendance else 0
    
    attempts = QuizAttempt.query.filter_by(student_id=student_id).order_by(QuizAttempt.attempted_at.desc()).limit(5).all()
    quiz_scores = []
    for a in attempts:
        q = __import__('models').Quiz.query.get(a.quiz_id)
        sub = db.session.get(Subject, q.subject_id).subject_name if q and db.session.get(Subject, q.subject_id) else 'General'
        quiz_scores.append({'subject': sub, 'topic': q.title if q else 'Quiz', 'score': f'{a.score}/100' if a.score is not None else 'N/A', 'date': a.attempted_at.strftime('%Y-%m-%d') if a.attempted_at else ''})
    
    progress_records = LearningProgress.query.filter_by(student_id=student_id).all()
    session_logs = []
    for p in progress_records:
        session_obj = db.session.get(Session, p.session_id) if p.session_id else None
        attendance_row = AttendanceRecord.query.filter_by(session_id=p.session_id, student_id=student_id).first() if session_obj else None
        subject = db.session.get(Subject, session_obj.subject_id) if session_obj else None
        tutor = db.session.get(Tutor, session_obj.tutor_id) if session_obj else None
        session_logs.append({
            "session_id": p.session_id,
            "date": session_obj.session_date.strftime("%Y-%m-%d") if session_obj and session_obj.session_date else "Recent",
            "status": p.session_completion_status or "Not recorded",
            "attendance_status": attendance_row.status if attendance_row else None,
            "learning_pace": p.learning_pace or "Not set by tutor",
            "remarks": p.tutor_remarks or "No tutor observation recorded.",
            "subject": subject.subject_name if subject else "General",
            "tutor_name": tutor.tutor_name if tutor else "Tutor",
            "joined_at": p.joined_at.isoformat() if p.joined_at else None,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        })

    remarks = WeeklySummary.query.filter_by(student_id=student_id).order_by(WeeklySummary.created_at.desc()).limit(3).all()
    return ok({
        'student_id': child.student_id,
        'student_name': child.student_name,
        'attendance_rate': f'{rate}%',
        'session_logs': session_logs,
        'recent_quiz_scores': quiz_scores,
        'tutor_remarks': [{'tutor_name': (db.session.get(Tutor, r.tutor_id).tutor_name if db.session.get(Tutor, r.tutor_id) else 'Tutor'), 'subject': 'General', 'remark': r.areas_for_improvement or r.topics_taught, 'date': r.created_at.strftime('%Y-%m-%d')} for r in remarks]
    })


@parent_bp.route('/weekly-summary/<int:parent_id>/<int:student_id>', methods=['GET'])
@parent_required
def get_weekly_summary(parent_id, student_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    child = db.session.get(Student, student_id)
    if not child or child.parent_id != parent_id:
        return fail('Child not found for this parent', 404)
    
    summary = WeeklySummary.query.filter_by(student_id=student_id).order_by(WeeklySummary.created_at.desc()).first()
    if not summary:
        return ok({
            'summary_id': None,
            'topics_taught': 'No summary report available for this week yet.',
            'homework_summary': 'N/A',
            'areas_for_improvement': 'N/A'
        })

    return ok({
        'summary_id': summary.summary_id,
        'week_start': summary.week_start.strftime('%Y-%m-%d') if summary.week_start else 'N/A',
        'week_end': summary.week_end.strftime('%Y-%m-%d') if summary.week_end else 'N/A',
        'topics_taught': summary.topics_taught,
        'homework_summary': summary.homework_summary,
        'areas_for_improvement': summary.areas_for_improvement
    })


@parent_bp.route('/ai-weekly-report/<int:parent_id>/<int:student_id>', methods=['POST'])
@parent_required
def ai_weekly_report(parent_id, student_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    child = db.session.get(Student, student_id)
    if not child or child.parent_id != parent_id:
        return fail('Child not found for this parent', 404)

    attendance = AttendanceRecord.query.filter_by(student_id=student_id).all()
    final_attendance = [a for a in attendance if a.status in {'Present', 'Absent', 'Late'}]
    present = sum(a.status == 'Present' for a in final_attendance)
    attendance_rate = round(present / len(final_attendance) * 100) if final_attendance else 0

    attempts = (
        QuizAttempt.query
        .filter_by(student_id=student_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .limit(5)
        .all()
    )
    quiz_scores = []
    for attempt in attempts:
        quiz = db.session.get(Quiz, attempt.quiz_id)
        subject = db.session.get(Subject, quiz.subject_id) if quiz else None
        quiz_scores.append({
            'subject': subject.subject_name if subject else 'General',
            'topic': quiz.title if quiz else 'Quiz',
            'score': attempt.score,
            'date': attempt.attempted_at.strftime('%Y-%m-%d') if attempt.attempted_at else None,
        })

    progress_records = (
        LearningProgress.query
        .filter_by(student_id=student_id)
        .order_by(LearningProgress.progress_id.desc())
        .limit(10)
        .all()
    )
    session_logs = []
    for progress in progress_records:
        sess = db.session.get(Session, progress.session_id) if progress.session_id else None
        subject = db.session.get(Subject, sess.subject_id) if sess else None
        attendance_row = AttendanceRecord.query.filter_by(session_id=progress.session_id, student_id=student_id).first() if sess else None
        session_logs.append({
            'date': sess.session_date.strftime('%Y-%m-%d') if sess and sess.session_date else None,
            'subject': subject.subject_name if subject else 'General',
            'status': progress.session_completion_status,
            'attendance_status': attendance_row.status if attendance_row else None,
            'learning_pace': progress.learning_pace,
            'remarks': progress.tutor_remarks,
        })

    summaries = (
        WeeklySummary.query
        .filter_by(student_id=student_id)
        .order_by(WeeklySummary.created_at.desc())
        .limit(3)
        .all()
    )
    summary_data = [
        {
            'week_start': s.week_start.isoformat() if s.week_start else None,
            'week_end': s.week_end.isoformat() if s.week_end else None,
            'topics_taught': s.topics_taught,
            'homework_summary': s.homework_summary,
            'areas_for_improvement': s.areas_for_improvement,
        }
        for s in summaries
    ]

    payload = {
        'student': {
            'subjects': [
                subject.subject_name
                for row in StudentSubject.query.filter_by(student_id=student_id).all()
                if (subject := db.session.get(Subject, row.subject_id))
            ],
        },
        'attendance_rate': f'{attendance_rate}%',
        'quiz_scores': quiz_scores,
        'session_logs': session_logs,
        'weekly_summaries': summary_data,
    }

    prompt = (
        "You are LearnAtHome Parent AI. Write a clear weekly progress report "
        "for a parent using only the real child data below. Do not invent "
        "quiz records, attendance, tutor remarks, or homework. If data is "
        "limited, explicitly mention that and provide practical next steps.\n\n"
        f"DATA:\n{json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
        "Return a short parent-friendly report with attendance, learning "
        "progress, assessment performance, concerns, and recommended next step."
    )

    try:
        report = generate_text(prompt)
    except AIConfigError as exc:
        return fail(str(exc), 503)
    except (AIServiceError, AIResponseError) as exc:
        return fail(f"AI weekly report generation failed: {exc}", 502)

    return ok({
        'report': report,
        'sourceCounts': {
            'attendanceRecords': len(attendance),
            'quizAttempts': len(quiz_scores),
            'sessionLogs': len(session_logs),
            'weeklySummaries': len(summary_data),
        }
    })


@parent_bp.route('/curriculum/<int:student_id>', methods=['GET'])
@parent_required
def curriculum(student_id):
    parent = current_parent()
    child = db.session.get(Student, student_id)
    if not parent or not child or child.parent_id != parent.parent_id:
        return fail('Child not found for this parent', 404)
    subject_ids = {x.subject_id for x in StudentSubject.query.filter_by(student_id=student_id).all()}
    plans = TeachingPlan.query.filter(TeachingPlan.subject_id.in_(subject_ids)).order_by(TeachingPlan.planned_date).all() if subject_ids else []
    data = [{'month': p.month, 'subject': db.session.get(Subject, p.subject_id).subject_name if db.session.get(Subject, p.subject_id) else 'General', 'topics': [p.topic_name], 'status': 'Planned'} for p in plans]
    return ok({'student_id': student_id, 'student_name': child.student_name, 'curriculum_plan': data})


@parent_bp.route('/schedule/<int:parent_id>', methods=['GET'])
@parent_required
def schedule(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)

    # This page is ONLY for parent-created one-to-one meetings that include
    # the child. Regular booked classes stay out of the parent meeting area.
    meetings = (
        MeetingRequest.query
        .filter(
            MeetingRequest.parent_id == parent_id,
            MeetingRequest.student_id.isnot(None),
        )
        .order_by(MeetingRequest.meeting_date, MeetingRequest.meeting_id)
        .all()
    )

    data = []
    for meeting in meetings:
        s = db.session.get(Session, meeting.session_id) if meeting.session_id else None
        if not s or s.session_type != 'One-to-One':
            continue

        st = db.session.get(Student, meeting.student_id)
        if not st or st.parent_id != parent_id:
            continue

        t = db.session.get(Tutor, s.tutor_id)
        sub = db.session.get(Subject, s.subject_id)
        lifecycle = meeting_lifecycle(s)

        if meeting.status == 'Pending Approval':
            lifecycle = {**lifecycle, 'status': 'Awaiting Tutor Approval', 'can_join': False}
        elif meeting.status in ('Denied', 'Reschedule Requested', 'Cancelled'):
            lifecycle = {**lifecycle, 'status': meeting.status, 'can_join': False}

        attendance = AttendanceRecord.query.filter_by(
            session_id=s.session_id,
            student_id=st.student_id,
        ).first()

        data.append({
            'session_id': s.session_id,
            'student_id': st.student_id,
            'student_name': st.student_name,
            'subject': sub.subject_name if sub else 'General',
            'tutor': t.tutor_name if t else 'Tutor',
            'tutor_id': s.tutor_id,
            'date': s.session_date.isoformat(),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'status': s.status,
            'session_type': s.session_type,
            'meeting_url': s.meeting_url,
            'meetingUrl': s.meeting_url,
            'meeting_lifecycle': lifecycle['status'],
            'can_join': lifecycle.get('can_join', False),
            'can_start': lifecycle.get('can_start', False),
            'meeting_started_at': s.meeting_started_at.isoformat() if s.meeting_started_at else None,
            'meeting_ended_at': s.meeting_ended_at.isoformat() if s.meeting_ended_at else None,
            'meeting_duration_seconds': s.meeting_duration_seconds,
            'attendance_status': attendance.status if attendance else None,
            'attendance_query': attendance.status == 'Pending' if attendance else False,
            'meeting_id': meeting.meeting_id,
            'meeting_request_status': meeting.status,
            'meeting_reason': meeting.meeting_reason,
        })

    return ok(data)


@parent_bp.route('/schedule/session/<int:session_id>/start', methods=['POST'])
@parent_required
def start_parent_session(session_id):
    parent = current_parent()
    sess = db.session.get(Session, session_id)
    meeting = MeetingRequest.query.filter_by(session_id=session_id, parent_id=parent.parent_id).first() if parent else None
    if not sess or not meeting:
        return fail('Parent-created session not found', 404)
    if meeting.status != 'Scheduled':
        return fail('The meeting must be approved by the tutor before it can be started.', 409)
    lifecycle = meeting_lifecycle(sess)
    if lifecycle['status'] == 'Meeting Ended':
        return fail('This meeting has already ended.', 409)
    if not sess.meeting_url:
        try:
            sess.meeting_url = create_meeting_space()
        except GoogleMeetNotConfigured as exc:
            current_app.logger.warning('Google Meet setup required: %s', exc)
            return fail('Google Meet is not connected.', 503)
    if not sess.meeting_started_at:
        sess.status = 'Live'
        sess.meeting_started_at = _local_now()
        sess.meeting_ended_at = None
        sess.meeting_duration_seconds = None
    student = db.session.get(Student, meeting.student_id)
    tutor = db.session.get(Tutor, meeting.tutor_id)
    subject = db.session.get(Subject, sess.subject_id)
    label = subject.subject_name if subject else 'session'
    if student:
        db.session.add(Notification(recipient_type='Student', recipient_id=student.student_id, title=f'{label} meeting started', message=f'{parent.parent_name} started the {label} meeting. Join the meeting now.', notification_type='Class Started', action_url=f'/student/sessions?session_id={session_id}'))
    if tutor:
        db.session.add(Notification(recipient_type='Tutor', recipient_id=tutor.tutor_id, title=f'{label} meeting started', message=f'{parent.parent_name} started {student.student_name if student else "the student"}’s {label} meeting.', notification_type='Class Started', action_url=f'/tutor/schedule?session_id={session_id}'))
    db.session.commit()
    return ok({'session_id': session_id, 'meeting_url': sess.meeting_url, 'meeting_started_at': sess.meeting_started_at.isoformat()}, 'Meeting started')


# =========================================================
# END PARENT ONE-TO-ONE MEETING
# =========================================================

@parent_bp.route('/schedule/session/<int:session_id>/end', methods=['POST'])
@parent_required
def end_parent_session(session_id):
    parent = current_parent()
    if not parent:
        return fail('Parent not logged in', 401)

    sess = db.session.get(Session, session_id)
    meeting = MeetingRequest.query.filter_by(
        session_id=session_id,
        parent_id=parent.parent_id
    ).first()

    if not sess or not meeting:
        return fail('Parent-created meeting not found', 404)

    if sess.session_type != 'One-to-One':
        return fail('Only one-to-one meetings can be ended here.', 400)

    if sess.status != 'Live':
        return fail('Only a live meeting can be ended.', 400)

    now = _local_now()
    sess.status = 'Completed'
    meeting.status = 'Completed'
    sess.meeting_ended_at = now

    if sess.meeting_started_at:
        sess.meeting_duration_seconds = max(
            0,
            int((now - sess.meeting_started_at).total_seconds())
        )

    student = db.session.get(Student, meeting.student_id) if meeting.student_id else None
    tutor = db.session.get(Tutor, meeting.tutor_id)
    subject = db.session.get(Subject, sess.subject_id)
    label = subject.subject_name if subject else 'session'

    if student:
        db.session.add(Notification(
            recipient_type='Student',
            recipient_id=student.student_id,
            title=f'{label} meeting ended',
            message=f'Your {label} meeting has ended. Attendance confirmation can now continue.',
            notification_type='Class Completed',
            action_url=f'/student/sessions?session_id={session_id}'
        ))

    if tutor:
        db.session.add(Notification(
            recipient_type='Tutor',
            recipient_id=tutor.tutor_id,
            title=f'{label} meeting ended',
            message=f'{parent.parent_name} ended the {label} one-to-one meeting.',
            notification_type='Class Completed',
            action_url=f'/tutor/schedule?session_id={session_id}'
        ))

    db.session.commit()

    return ok({
        'session_id': session_id,
        'status': 'Completed',
        'meeting_ended_at': sess.meeting_ended_at.isoformat(),
        'duration_seconds': sess.meeting_duration_seconds or 0
    }, 'Meeting ended successfully.')


@parent_bp.route('/schedule/session/<int:session_id>', methods=['PUT', 'DELETE'])
@parent_required
def manage_parent_session(session_id):
    parent = current_parent()
    sess = db.session.get(Session, session_id)
    meeting = MeetingRequest.query.filter_by(session_id=session_id, parent_id=parent.parent_id).first() if parent else None
    if not sess or not meeting:
        return fail('Parent-created session not found', 404)
    if sess.status in ('Live', 'Completed', 'Cancelled'):
        return fail('This session can no longer be changed', 400)
    student = db.session.get(Student, meeting.student_id)
    subject = db.session.get(Subject, sess.subject_id)
    tutor = db.session.get(Tutor, sess.tutor_id)
    if request.method == 'DELETE':
        sess.status = 'Cancelled'
        meeting.status = 'Cancelled'
        db.session.add(Notification(
            recipient_type='Student', recipient_id=student.student_id,
            title=f'{subject.subject_name if subject else "Session"} cancelled',
            message=f'{parent.parent_name} cancelled the {subject.subject_name if subject else "session"} scheduled for {sess.session_date.strftime("%d %b %Y")} at {sess.start_time.strftime("%I:%M %p")}.',
            notification_type='Meeting Cancelled', action_url='/student/sessions'
        ))
        db.session.add(Notification(
            recipient_type='Tutor', recipient_id=tutor.tutor_id,
            title=f'{subject.subject_name if subject else "Session"} cancelled',
            message=f'{parent.parent_name} cancelled {student.student_name}\'s session scheduled for {sess.session_date.strftime("%d %b %Y")} at {sess.start_time.strftime("%I:%M %p")}.',
            notification_type='Meeting Cancelled', action_url='/tutor/schedule'
        ))
        db.session.commit()
        return ok({'session_id': session_id, 'status': 'Cancelled'}, 'Session cancelled')

    d = request.get_json(silent=True) or {}
    try:
        new_date = datetime.strptime(d.get('session_date'), '%Y-%m-%d').date() if d.get('session_date') else sess.session_date
        new_start = datetime.strptime(d.get('start_time'), '%H:%M').time() if d.get('start_time') else sess.start_time
        new_end = datetime.strptime(d.get('end_time'), '%H:%M').time() if d.get('end_time') else sess.end_time
    except (TypeError, ValueError):
        return fail('Invalid schedule data')
    if new_end <= new_start:
        return fail('End time must be later than start time')
    conflicts = Session.query.filter(Session.tutor_id == sess.tutor_id, Session.session_id != session_id, Session.session_date == new_date).all()
    for other in conflicts:
        if other.status != 'Cancelled' and new_start < other.end_time and new_end > other.start_time:
            return fail('The tutor already has another session scheduled during this time.', 409)
    sess.session_date, sess.start_time, sess.end_time = new_date, new_start, new_end
    sess.status = 'Scheduled' if meeting.status in ('Pending Approval', 'Reschedule Requested') else 'Rescheduled'
    sess.meeting_started_at = None
    sess.meeting_ended_at = None
    sess.meeting_duration_seconds = None
    meeting.meeting_date = datetime.combine(new_date, new_start)
    meeting.status = 'Pending Approval' if meeting.status in ('Pending Approval', 'Reschedule Requested') else 'Rescheduled'
    display = f'{new_date.strftime("%d %b %Y")}, {new_start.strftime("%I:%M %p")}–{new_end.strftime("%I:%M %p")}'
    db.session.add(Notification(
        recipient_type='Student', recipient_id=student.student_id,
        title=f'{subject.subject_name if subject else "Session"} rescheduled',
        message=f'Your parent updated the session schedule to {display}.',
        notification_type='Meeting Updated', action_url=f'/student/sessions?session_id={session_id}'
    ))
    db.session.add(Notification(
        recipient_type='Tutor', recipient_id=tutor.tutor_id,
        title=f'{subject.subject_name if subject else "Session"} rescheduled',
        message=f'{parent.parent_name} updated {student.student_name}\'s session to {display}.',
        notification_type='Meeting Updated', action_url=f'/tutor/schedule?session_id={session_id}'
    ))
    db.session.commit()
    return ok({'session_id': session_id, 'date': new_date.isoformat(), 'start_time': new_start.strftime('%H:%M'), 'end_time': new_end.strftime('%H:%M'), 'status': sess.status}, 'Session rescheduled')


@parent_bp.route('/messages/<int:parent_id>', methods=['GET'])
@parent_required
def messages(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    rows = Message.query.filter(((Message.sender_type == 'Parent') & (Message.sender_id == parent_id)) | ((Message.receiver_type == 'Parent') & (Message.receiver_id == parent_id))).order_by(Message.sent_at).all()
    return ok([{'message_id': m.message_id, 'sender_type': m.sender_type, 'sender_id': m.sender_id, 'receiver_type': m.receiver_type, 'receiver_id': m.receiver_id, 'subject': m.subject, 'message': m.message, 'sent_at': m.sent_at.isoformat() if m.sent_at else None, 'reply_message': m.reply_message} for m in rows])


@parent_bp.route('/messages/send', methods=['POST'])
@parent_required
def send_message():
    parent = current_parent()
    if not parent:
        return fail('Parent not logged in', 401)
    
    d = request.get_json(silent=True) or {}
    p_id = int(d.get('parent_id', -1))
    if p_id != parent.parent_id:
        return fail('Unauthorized parent access', 403)
        
    tutor_id = int(d.get('tutor_id', 1))
    subject = d.get('subject', 'Parent Query')
    message_text = d.get('message')

    if not message_text:
        return fail('Message text is required')

    new_msg = Message(
        sender_type='Parent',
        sender_id=parent.parent_id,
        receiver_type='Tutor',
        receiver_id=tutor_id,
        subject=subject,
        message=message_text,
        sent_at=datetime.now(timezone.utc)
    )
    db.session.add(new_msg)

    notif = Notification(
        recipient_type='Tutor',
        recipient_id=tutor_id,
        title='New Message from Parent',
        message=f"New query regarding: '{subject}'",
        notification_type='New Message',
        action_url='/tutor/messages',
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(notif)
    db.session.commit()

    return ok({'message_id': new_msg.message_id}, 'Message sent successfully', 201)


@parent_bp.route('/notifications/<int:parent_id>', methods=['GET'])
@parent_required
def notifications(parent_id):
    parent = current_parent()
    if not parent or parent.parent_id != parent_id:
        return fail('Unauthorized parent access', 403)
    rows = Notification.query.filter_by(recipient_type='Parent', recipient_id=parent_id).order_by(Notification.created_at.desc()).all()
    return ok([{'id': n.notification_id, 'title': n.title, 'message': n.message, 'is_read': n.is_read, 'created_at': n.created_at.isoformat(), 'action_url': n.action_url} for n in rows])

@parent_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@parent_required
def mark_notification_read(notification_id):
    parent = current_parent()
    n = Notification.query.filter_by(notification_id=notification_id, recipient_type='Parent', recipient_id=parent.parent_id).first()
    if not n:
        return fail('Notification not found', 404)
    n.is_read = True
    db.session.commit()
    return ok(message='Notification marked as read')
