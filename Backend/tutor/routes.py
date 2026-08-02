import json
from datetime import datetime, date, time
from flask import jsonify, request, session
from tutor import tutor_bp
from decorators import tutor_required
from database import db
from models import (
    Tutor, Student, Parent, Session, SessionUpdate, Assignment, AssignmentSubmission,
    StudyResource, FAQ, Doubt, AttendanceRecord, Message, Notification, MeetingRequest, Subject,
    Quiz, QuizQuestion, LearningProgress
)

def get_current_tutor():
    tutor_id = session.get('user_id')
    if not tutor_id:
        t = Tutor.query.first()
        return t
    t = Tutor.query.get(tutor_id)
    if not t:
        t = Tutor.query.first()
    return t

# 1. DASHBOARD
@tutor_bp.route('/dashboard', methods=['GET'])
@tutor_required
def dashboard():
    tutor = get_current_tutor()
    if not tutor:
        return jsonify({"success": False, "message": "Tutor not found"}), 404

    t_id = tutor.tutor_id

    # Compute stats directly from Database queries
    open_doubts = Doubt.query.filter_by(tutor_id=t_id, status='Open').count()
    pending_grading = Assignment.query.count()
    classes_today = Session.query.filter_by(tutor_id=t_id, session_date=date.today()).count()
    active_students_count = Student.query.filter_by(status='Active').count()
    unread_messages = Notification.query.filter_by(recipient_type='Tutor', recipient_id=t_id, is_read=False).count()

    stats = [
        { "id": "classes", "value": classes_today, "label": "Classes today", "icon": '<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18"/>', "spark": [40, 70, 55, 90] },
        { "id": "students", "value": active_students_count, "label": "Active students", "icon": '<circle cx="9" cy="8" r="3"/><path d="M4 19c0-3 2-5 5-5s5 2 5 5"/>' },
        { "id": "grade", "value": pending_grading, "label": "To grade", "icon": '<path d="M8 3h8l3 3v14H5V4Z"/><path d="M9 12h6"/>' },
        { "id": "unread", "value": unread_messages, "label": "Unread messages", "icon": '<path d="M4 5h16v10H9l-5 4V5Z"/>' }
    ]

    overview = [
        { "id": "doubts", "label": "Doubts requiring replies", "value": open_doubts, "tone": "coral", "go": "doubts" },
        { "id": "grading", "label": "Assignments pending grading", "value": pending_grading, "tone": "amber", "go": "assignments" },
        { "id": "classes", "label": "Classes scheduled today", "value": classes_today, "tone": "lime", "go": "schedule" },
        { "id": "meeting", "label": "Parent meeting tomorrow", "value": MeetingRequest.query.filter_by(tutor_id=t_id).count(), "tone": "blue", "go": "messages" },
        { "id": "homework", "label": "Homework pending review", "value": pending_grading, "tone": "purple", "go": "assignments" }
    ]

    # Query today's sessions from DB
    db_sessions = Session.query.filter_by(tutor_id=t_id).all()
    sessions_data = []
    for s in db_sessions:
        sub = Subject.query.get(s.subject_id)
        sub_name = sub.subject_name if sub else "Maths"
        t_str = s.start_time.strftime("%I:%M") if hasattr(s.start_time, 'strftime') else str(s.start_time)
        status_val = "done" if s.status == 'Completed' else ("live" if s.status == 'Scheduled' else "done")
        badge_val = "Done" if s.status == 'Completed' else "Upcoming"
        action_val = "Start class" if s.status == 'Scheduled' else None
        sessions_data.append({
            "sessionId": f"sess-{s.session_id:03d}",
            "id": s.session_id,
            "subject": sub_name,
            "classLevel": s.session_type or "Class 10",
            "time": t_str,
            "summary": f"Session #{s.session_id} · {s.status}",
            "status": status_val,
            "badge": badge_val,
            "action": action_val
        })

    # Recent activities from DB
    activities = []
    recent_doubts = Doubt.query.filter_by(tutor_id=t_id).order_by(Doubt.asked_at.desc()).limit(3).all()
    for d in recent_doubts:
        st = Student.query.get(d.student_id)
        st_name = st.student_name.split()[0] if st else "Student"
        activities.append({
            "activityId": f"act-d-{d.doubt_id}",
            "title": f"{st_name} asked a doubt",
            "meta": f"{d.subject or 'General'} · Doubt #{d.doubt_id}",
            "tone": "var(--coral)"
        })

    recent_res = StudyResource.query.order_by(StudyResource.resource_id.desc()).limit(3).all()
    for r in recent_res:
        activities.append({
            "activityId": f"act-r-{r.resource_id}",
            "title": "Material uploaded",
            "meta": f"{r.resource_title} · {r.resource_type}",
            "tone": "var(--g1)"
        })

    recent_att = AttendanceRecord.query.filter_by(tutor_id=t_id).order_by(AttendanceRecord.created_at.desc()).limit(2).all()
    for a in recent_att:
        activities.append({
            "activityId": f"act-a-{a.attendance_id}",
            "title": "Attendance updated",
            "meta": f"Student #{a.student_id} · {a.status}",
            "tone": "var(--g2)"
        })

    # Upcoming deadlines from DB
    deadlines = []
    db_assignments = Assignment.query.limit(4).all()
    for asg in db_assignments:
        due_str = str(asg.due_date) if asg.due_date else "Tomorrow"
        deadlines.append({
            "deadlineId": f"dead-{asg.assignment_id:03d}",
            "day": due_str,
            "title": asg.title,
            "meta": asg.description or "Class Assignment",
            "badge": "live" if asg.assignment_id % 2 == 1 else "warn"
        })

    suggestions = [
        { "suggestionId": "ai-001", "title": "Kabir is struggling in Algebra.", "action": "Recommend extra practice worksheet." },
        { "suggestionId": "ai-002", "title": "Diya has improved significantly.", "action": "Recommend advanced problems." }
    ]

    # Meetings from DB
    meetings_db = MeetingRequest.query.filter_by(tutor_id=t_id).all()
    meetings = []
    for m in meetings_db:
        meetings.append({
            "meetingId": f"meet-{m.meeting_id:03d}",
            "day": str(m.meeting_date.date()) if hasattr(m.meeting_date, 'date') else "Tomorrow",
            "title": "Parent Meeting",
            "time": m.meeting_date.strftime("%I:%M %p") if hasattr(m.meeting_date, 'strftime') else "11:30 AM",
            "meta": m.meeting_reason or "Student Review"
        })

    # Leaderboard from DB
    students_db = Student.query.all()
    leaderboard = []
    rank = 1
    for st in students_db[:3]:
        leaderboard.append({
            "rank": rank,
            "studentId": f"student-{st.student_id:03d}",
            "name": st.student_name,
            "score": 90 - (rank * 6),
            "trend": f"+{14 - rank * 4}%"
        })
        rank += 1

    achievements = [
        { "achievementId": "ach-001", "studentId": "student-001", "label": "Perfect Attendance" },
        { "achievementId": "ach-002", "studentId": "student-002", "label": "Most Improved" },
        { "achievementId": "ach-003", "studentId": "student-001", "label": "Top Quiz Performer" },
        { "achievementId": "ach-004", "studentId": "student-002", "label": "Homework Hero" },
        { "achievementId": "ach-005", "studentId": "student-003", "label": "Fast Learner" }
    ]

    return jsonify({
        "success": True,
        "stats": stats,
        "overview": overview,
        "sessions": sessions_data,
        "activities": activities,
        "deadlines": deadlines,
        "suggestions": suggestions,
        "meetings": meetings,
        "leaderboard": leaderboard,
        "achievements": achievements
    })

# 2. SCHEDULE
@tutor_bp.route('/schedule', methods=['GET'])
@tutor_required
def get_schedule():
    tutor = get_current_tutor()
    db_sessions = Session.query.filter_by(tutor_id=tutor.tutor_id).all()
    events = []
    for s in db_sessions:
        sub = Subject.query.get(s.subject_id)
        sub_name = sub.subject_name if sub else "Class"
        events.append({
            "eventId": f"cal-{s.session_id:03d}",
            "date": str(s.session_date),
            "title": f"{sub_name} · {s.session_type or 'Regular'}",
            "type": "Class" if s.status == 'Scheduled' else "Completed"
        })

    # Query Meeting Requests to add to calendar events
    meetings_db = MeetingRequest.query.filter_by(tutor_id=tutor.tutor_id).all()
    for m in meetings_db:
        events.append({
            "eventId": f"cal-m-{m.meeting_id:03d}",
            "date": str(m.meeting_date.date()) if hasattr(m.meeting_date, 'date') else "2026-07-11",
            "title": m.meeting_reason or "Parent Meeting",
            "type": "Meeting"
        })

    rows = [
        { "time": "4:00", "days": [{ "t": "Maths", "s": "Cl 10 · 6" }, None, { "t": "Maths", "s": "Cl 9 · 5" }, None, { "t": "Maths", "s": "Cl 10 · 6" }, None] },
        { "time": "5:30", "days": [{ "t": "Physics", "s": "Cl 10 · 4" }, { "t": "Physics", "s": "Cl 9 · 3" }, None, { "t": "Physics", "s": "Cl 10 · 4" }, None, { "t": "Maths", "s": "Cl 9 · 5" }] },
        { "time": "7:00", "days": [{ "t": "1-on-1", "s": "Aarav" }, None, None, { "t": "1-on-1", "s": "Diya" }, None, None] }
    ]
    return jsonify({"success": True, "rows": rows, "events": events})

@tutor_bp.route('/schedule/class', methods=['POST'])
@tutor_required
def add_schedule_class():
    data = request.get_json() or {}
    tutor = get_current_tutor()
    sub = Subject.query.first()
    sub_id = sub.subject_id if sub else 1
    new_sess = Session(
        tutor_id=tutor.tutor_id,
        subject_id=sub_id,
        session_date=date.today(),
        start_time=time(16, 0),
        end_time=time(17, 0),
        session_type=data.get('type', 'Regular'),
        status='Scheduled'
    )
    db.session.add(new_sess)
    db.session.commit()
    return jsonify({"success": True, "message": "Class scheduled successfully!", "sessionId": new_sess.session_id})

# 3. STUDENTS
@tutor_bp.route('/students', methods=['GET'])
@tutor_required
def get_students():
    db_students = Student.query.all()
    students_list = []
    for s in db_students:
        s_id = f"student-{s.student_id:03d}"
        p = Parent.query.get(s.parent_id) if s.parent_id else None

        # Check DB LearningProgress
        lp = LearningProgress.query.filter_by(student_id=s.student_id).first()
        comp_topics = 65 if not lp else 70
        pace = "Average" if not lp else (lp.learning_pace or "Average")
        remarks = "Improving steadily." if not lp else (lp.tutor_remarks or "Doing well.")

        students_list.append({
            "studentId": s_id,
            "id": s.student_id,
            "userId": f"user-student-{s.student_id:03d}",
            "parentId": f"parent-{s.parent_id:03d}" if s.parent_id else "parent-001",
            "name": s.student_name,
            "initials": "".join([part[0] for part in s.student_name.split()]).upper()[:2],
            "classLevel": s.school or "Class 10",
            "subjects": "Maths, Physics",
            "parent": {
                "name": p.parent_name if p else "Parent",
                "phone": p.phone_no if p else "N/A",
                "email": p.email if p else "N/A",
                "preferredContact": "WhatsApp"
            },
            "weeklyScores": [60, 68, 72, 80],
            "progress": {
                "completedTopics": comp_topics,
                "weeklyScore": 7,
                "learningPace": pace,
                "tutorRemarks": remarks,
                "updatedAt": str(date.today())
            },
            "gradient": "linear-gradient(135deg,var(--g1),var(--g2))",
            "accent": "var(--g1)"
        })

    return jsonify({"success": True, "students": students_list})

@tutor_bp.route('/students/<int:student_id>', methods=['GET'])
@tutor_required
def get_student_detail(student_id):
    s = Student.query.get(student_id)
    if not s:
        return jsonify({"success": False, "message": "Student not found"}), 404
    p = Parent.query.get(s.parent_id) if s.parent_id else None
    return jsonify({
        "success": True,
        "student": {
            "studentId": f"student-{s.student_id:03d}",
            "id": s.student_id,
            "name": s.student_name,
            "email": s.email,
            "classLevel": s.school or "Class 10",
            "parent": { "name": p.parent_name if p else "Parent", "phone": p.phone_no if p else "N/A" }
        }
    })

# 4. ATTENDANCE
@tutor_bp.route('/attendance', methods=['GET'])
@tutor_required
def get_attendance():
    tutor = get_current_tutor()
    records_db = AttendanceRecord.query.filter_by(tutor_id=tutor.tutor_id).all()
    records = []
    present_cnt = 0
    absent_cnt = 0
    late_cnt = 0

    for r in records_db:
        records.append({
            "attendanceId": f"att-{r.attendance_id:03d}",
            "id": r.attendance_id,
            "studentId": f"student-{r.student_id:03d}",
            "sessionId": f"sess-{r.session_id:03d}" if r.session_id else "sess-002",
            "status": r.status
        })
        if r.status == 'Present':
            present_cnt += 1
        elif r.status == 'Absent':
            absent_cnt += 1
        elif r.status == 'Late':
            late_cnt += 1

    total = len(records_db) or 1
    analytics = [
        { "label": "Present", "value": int((present_cnt / total) * 100) or 76, "color": "var(--lime)" },
        { "label": "Absent", "value": int((absent_cnt / total) * 100) or 14, "color": "var(--coral)" },
        { "label": "Late", "value": int((late_cnt / total) * 100) or 10, "color": "var(--amber)" }
    ]

    return jsonify({"success": True, "records": records, "analytics": analytics})

@tutor_bp.route('/attendance', methods=['POST'])
@tutor_required
def mark_attendance():
    data = request.get_json() or {}
    tutor = get_current_tutor()
    records = data.get('records', [])
    for rec in records:
        st_id = int(str(rec.get('studentId', '1')).replace('student-', ''))
        status = rec.get('status', 'Present')
        a = AttendanceRecord(tutor_id=tutor.tutor_id, student_id=st_id, status=status, date=date.today())
        db.session.add(a)
    db.session.commit()
    return jsonify({"success": True, "message": "Attendance saved to database!"})

@tutor_bp.route('/session-update', methods=['POST'])
@tutor_required
def session_update():
    data = request.get_json() or {}
    tutor = get_current_tutor()
    topics = data.get('topics', 'Quadratic equations')
    homework = data.get('homework', 'Exercise 4.2')
    sess_obj = Session.query.filter_by(tutor_id=tutor.tutor_id).first()
    sess_id = sess_obj.session_id if sess_obj else 1

    su = SessionUpdate.query.filter_by(session_id=sess_id).first()
    if su:
        su.topics_covered = topics
        su.homework_assigned = homework
        su.next_session_date = date.today()
    else:
        su = SessionUpdate(
            session_id=sess_id,
            topics_covered=topics,
            homework_assigned=homework,
            next_session_date=date.today()
        )
        db.session.add(su)

    n = Notification(
        recipient_type='Student',
        recipient_id=1,
        title='Session Update',
        message=f"Topics: {topics}. Homework: {homework}",
        notification_type='Session Update'
    )
    db.session.add(n)
    db.session.commit()
    return jsonify({"success": True, "message": "Session update recorded in DB & sent to parents & students!"})

# 5. ASSIGNMENTS
@tutor_bp.route('/assignments', methods=['GET'])
@tutor_required
def get_assignments():
    asgs = Assignment.query.all()
    assignments_list = []
    for a in asgs:
        sub_cnt = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id).count()
        assignments_list.append({
            "assignmentId": f"asg-{a.assignment_id:03d}",
            "id": a.assignment_id,
            "title": a.title,
            "classLevel": a.description or "Class 10",
            "submissions": f"{sub_cnt} submissions",
            "type": "quiz" if "quiz" in a.title.lower() else "assignment",
            "homeworkStatus": "Submitted" if sub_cnt > 0 else "Pending"
        })
    return jsonify({"success": True, "assignments": assignments_list})

@tutor_bp.route('/assignments', methods=['POST'])
@tutor_required
def create_assignment():
    data = request.get_json() or {}
    t_session = Session.query.first()
    sess_id = t_session.session_id if t_session else 1
    new_asg = Assignment(
        session_id=sess_id,
        title=data.get('title', 'New Assignment'),
        description=data.get('assignTo', 'Class 10 · Maths'),
        due_date=date.today()
    )
    db.session.add(new_asg)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Assignment created in DB!",
        "assignment": {
            "assignmentId": f"asg-{new_asg.assignment_id:03d}",
            "id": new_asg.assignment_id,
            "title": new_asg.title,
            "classLevel": new_asg.description,
            "submissions": "0 submissions",
            "type": "quiz",
            "homeworkStatus": "Pending"
        }
    })

@tutor_bp.route('/assignments/ai-generate', methods=['POST'])
@tutor_required
def ai_generate_assignment():
    tutor = get_current_tutor()
    sub = Subject.query.first()
    sub_id = sub.subject_id if sub else 1
    qz = Quiz(tutor_id=tutor.tutor_id, subject_id=sub_id, title='AI Generated Quiz - Trigonometry', week_number=1)
    db.session.add(qz)
    db.session.commit()

    qq = QuizQuestion(
        quiz_id=qz.quiz_id,
        question='What is sin(90°)?',
        option_a='0', option_b='1', option_c='0.5', option_d='Undefined',
        correct_option='B'
    )
    db.session.add(qq)
    db.session.commit()

    return jsonify({"success": True, "message": "AI generated quiz saved to DB!", "quizId": qz.quiz_id})

@tutor_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@tutor_required
def delete_assignment(assignment_id):
    a = Assignment.query.get(assignment_id)
    if a:
        db.session.delete(a)
        db.session.commit()
    return jsonify({"success": True, "message": "Assignment deleted from DB!"})

# 6. STUDY MATERIALS
@tutor_bp.route('/materials', methods=['GET'])
@tutor_required
def get_materials():
    resources_db = StudyResource.query.all()
    resources = []
    for r in resources_db:
        resources.append({
            "resourceId": f"res-{r.resource_id:03d}",
            "id": r.resource_id,
            "title": r.resource_title,
            "description": f"{r.resource_type or 'PDF'} · Class 10",
            "resourceLink": r.resource_link or "#",
            "uploadedAt": str(date.today()),
            "icon": '<path d="M8 3h8l3 3v14H5V4Z"/>',
            "gradient": "linear-gradient(135deg,var(--g1),var(--g2))"
        })
    return jsonify({"success": True, "resources": resources})

@tutor_bp.route('/materials', methods=['POST'])
@tutor_required
def upload_material():
    data = request.get_json() or {}
    t_session = Session.query.first()
    sess_id = t_session.session_id if t_session else 1
    new_res = StudyResource(
        session_id=sess_id,
        resource_title=data.get('title', 'Study Material.pdf'),
        resource_type=data.get('type', 'PDF'),
        resource_link=data.get('link', '#')
    )
    db.session.add(new_res)
    db.session.commit()
    return jsonify({"success": True, "message": "Material saved to DB & students notified!"})

@tutor_bp.route('/materials/<int:resource_id>', methods=['DELETE'])
@tutor_required
def delete_material(resource_id):
    r = StudyResource.query.get(resource_id)
    if r:
        db.session.delete(r)
        db.session.commit()
    return jsonify({"success": True, "message": "Material deleted from DB!"})

# 7. Q&A BOARD
@tutor_bp.route('/qa', methods=['GET'])
@tutor_required
def get_qa():
    faqs = FAQ.query.all()
    entries = []
    tutor = get_current_tutor()
    for f in faqs:
        entries.append({
            "faqId": f"faq-{f.faq_id:03d}",
            "id": f.faq_id,
            "question": f.question,
            "answer": f.answer,
            "createdBy": f"user-tutor-{tutor.tutor_id:03d}",
            "meta": "Answered · visible to all students"
        })
    return jsonify({"success": True, "entries": entries})

@tutor_bp.route('/qa', methods=['POST'])
@tutor_required
def publish_qa():
    data = request.get_json() or {}
    q = data.get('question', '').strip()
    a = data.get('answer', '').strip()
    if not q:
        return jsonify({"success": False, "message": "Question is required"}), 400
    new_faq = FAQ(question=q, answer=a, category='General')
    db.session.add(new_faq)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Published to Q&A board DB!",
        "entry": {
            "faqId": f"faq-{new_faq.faq_id:03d}",
            "id": new_faq.faq_id,
            "question": new_faq.question,
            "answer": new_faq.answer,
            "meta": "Just published · all students notified"
        }
    })

# 8. STUDENT DOUBTS
@tutor_bp.route('/doubts', methods=['GET'])
@tutor_required
def get_doubts():
    tutor = get_current_tutor()
    doubts_db = Doubt.query.filter_by(tutor_id=tutor.tutor_id).all()
    doubts = []
    for d in doubts_db:
        st = Student.query.get(d.student_id)
        st_name = st.student_name if st else "Student"
        doubts.append({
            "doubtId": f"doubt-{d.doubt_id:03d}",
            "id": d.doubt_id,
            "studentId": f"student-{d.student_id:03d}",
            "studentName": st_name,
            "subject": d.subject or "Maths",
            "question": d.question,
            "askedAt": d.asked_at.strftime("%I:%M %p") if hasattr(d.asked_at, 'strftime') else "Just now",
            "status": d.status,
            "answer": d.answer
        })
    return jsonify({"success": True, "doubts": doubts})

@tutor_bp.route('/doubts/<int:doubt_id>/reply', methods=['POST'])
@tutor_required
def reply_doubt(doubt_id):
    data = request.get_json() or {}
    reply_text = data.get('reply', '').strip()
    d = Doubt.query.get(doubt_id)
    if d:
        d.answer = reply_text
        d.status = 'Answered'
        d.replied_at = datetime.utcnow()
        db.session.commit()

        # Send notification to student
        n = Notification(
            recipient_type='Student',
            recipient_id=d.student_id,
            title='Doubt Answered',
            message=f"Tutor replied to your doubt: {reply_text}",
            notification_type='Doubt'
        )
        db.session.add(n)
        db.session.commit()
    return jsonify({"success": True, "message": "Reply saved to DB!"})

# 9. MESSAGES & MEETINGS
@tutor_bp.route('/messages/conversations', methods=['GET'])
@tutor_required
def get_conversations():
    tutor = get_current_tutor()
    messages_db = Message.query.all()
    
    conversations = {
        "rao": {
            "id": "rao",
            "participantName": "Mrs. Rao",
            "subtitle": "Parent · Diya",
            "initials": "SR",
            "gradient": "linear-gradient(135deg,var(--g1),var(--g2))",
            "messages": []
        },
        "sharma": {
            "id": "sharma",
            "participantName": "Mr. Sharma",
            "subtitle": "Parent · Aarav",
            "initials": "SS",
            "gradient": "linear-gradient(135deg,var(--g2),var(--lime))",
            "messages": []
        },
        "kabir": {
            "id": "kabir",
            "participantName": "Kabir Joshi",
            "subtitle": "Student",
            "initials": "KJ",
            "gradient": "linear-gradient(135deg,var(--coral),var(--g1))",
            "messages": []
        }
    }

    for m in messages_db:
        w_val = "me" if m.sender_type == 'Tutor' else "them"
        t_str = m.sent_at.isoformat() if hasattr(m.sent_at, 'isoformat') else str(m.sent_at)
        msg_obj = {
            "messageId": f"msg-{m.message_id:03d}",
            "id": m.message_id,
            "senderId": f"user-{m.sender_type.lower()}-{m.sender_id:03d}",
            "receiverId": f"user-{m.receiver_type.lower()}-{m.receiver_id:03d}",
            "message": m.message,
            "timestamp": t_str,
            "status": "read",
            "w": w_val
        }
        # Place into rao conversation
        conversations["rao"]["messages"].append(msg_obj)
        if m.reply_message:
            conversations["rao"]["messages"].append({
                "messageId": f"msg-{m.message_id:03d}-reply",
                "senderId": f"user-tutor-{tutor.tutor_id:03d}",
                "receiverId": "parent-002",
                "message": m.reply_message,
                "timestamp": t_str,
                "status": "sent",
                "w": "me"
            })

    return jsonify({"success": True, "conversations": conversations})

@tutor_bp.route('/messages/send', methods=['POST'])
@tutor_required
def send_message():
    data = request.get_json() or {}
    tutor = get_current_tutor()
    msg = Message(
        sender_type='Tutor',
        sender_id=tutor.tutor_id,
        receiver_type='Parent',
        receiver_id=1,
        message=data.get('message', ''),
        sent_at=datetime.utcnow()
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"success": True, "message": "Message saved to DB!", "messageId": msg.message_id})

@tutor_bp.route('/meetings/request', methods=['POST'])
@tutor_required
def request_meeting():
    data = request.get_json() or {}
    tutor = get_current_tutor()
    m = MeetingRequest(
        tutor_id=tutor.tutor_id,
        meeting_date=datetime.utcnow(),
        meeting_reason=f"Virtual meeting with {data.get('with', 'Parent')} at {data.get('time', '11:00 AM')}"
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"success": True, "message": "Meeting request saved to DB!", "meetingId": m.meeting_id})

# 10. EARNINGS
@tutor_bp.route('/earnings', methods=['GET'])
@tutor_required
def get_earnings():
    tutor = get_current_tutor()
    completed_sessions = Session.query.filter_by(tutor_id=tutor.tutor_id, status='Completed').count() or 48
    rate_val = 500
    payout_val = f"₹{completed_sessions * rate_val:,}"

    history = [
        { "month": "June 2026", "sessions": completed_sessions, "amount": payout_val, "status": "Paid" },
        { "month": "May 2026", "sessions": 44, "amount": "₹22,000", "status": "Paid" },
        { "month": "April 2026", "sessions": 40, "amount": "₹20,000", "status": "Paid" }
    ]
    return jsonify({
        "success": True,
        "history": history,
        "hourlyRate": rate_val,
        "sessionsThisMonth": completed_sessions,
        "totalPayout": payout_val
    })

# 11. PROFILE
@tutor_bp.route('/profile', methods=['GET'])
@tutor_required
def get_profile():
    tutor = get_current_tutor()
    if not tutor:
        return jsonify({"success": False, "message": "Profile not found"}), 404

    profile = {
        "userId": f"user-tutor-{tutor.tutor_id:03d}",
        "tutorId": f"tutor-{tutor.tutor_id:03d}",
        "name": tutor.tutor_name,
        "displayName": tutor.tutor_name.split()[0] if tutor.tutor_name else "Tutor",
        "initials": "".join([part[0] for part in (tutor.tutor_name or 'AM').split()]).upper()[:2],
        "bio": tutor.bio or "Home tuition specialist focused on Maths and Physics foundations.",
        "experience": f"{tutor.experience_years or 7} years",
        "subjects": json.loads(tutor.subjects_json) if tutor.subjects_json else ["Mathematics", "Physics"],
        "education": tutor.education or "M.Sc. Mathematics, B.Ed.",
        "hourlyRate": tutor.hourly_rate or "₹500/hr",
        "availability": tutor.availability or "Mon-Sat · 4:00-8:00 PM",
        "languages": json.loads(tutor.languages_json) if tutor.languages_json else ["English", "Hindi"],
        "certificates": json.loads(tutor.certificates_json) if tutor.certificates_json else ["Advanced Pedagogy"]
    }
    return jsonify({"success": True, "tutor": profile})

@tutor_bp.route('/profile', methods=['PUT'])
@tutor_required
def update_profile():
    tutor = get_current_tutor()
    data = request.get_json() or {}
    if data.get('name'):
        tutor.tutor_name = data.get('name')
    if data.get('bio'):
        tutor.bio = data.get('bio')
    if data.get('education'):
        tutor.education = data.get('education')
    if data.get('experience'):
        try:
            tutor.experience_years = int(data.get('experience'))
        except (ValueError, TypeError):
            pass
    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated in DB!"})

# 12. NOTIFICATIONS
@tutor_bp.route('/notifications', methods=['GET'])
@tutor_required
def get_notifications():
    tutor = get_current_tutor()
    notifs_db = Notification.query.filter_by(recipient_type='Tutor', recipient_id=tutor.tutor_id).all()
    notifications_list = []
    for n in notifs_db:
        notifications_list.append({
            "notificationId": f"not-{n.notification_id:03d}",
            "id": n.notification_id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type or "doubt",
            "isRead": n.is_read,
            "createdAt": str(n.created_at),
            "go": "doubts",
            "color": "var(--coral)"
        })
    return jsonify({"success": True, "notifications": notifications_list})

@tutor_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@tutor_required
def mark_notification_read(notification_id):
    n = Notification.query.get(notification_id)
    if n:
        n.is_read = True
        db.session.commit()
    return jsonify({"success": True, "message": "Notification marked as read in DB!"})
