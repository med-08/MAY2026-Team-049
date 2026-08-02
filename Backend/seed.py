import json
from datetime import datetime, date, time
from app import app
from database import db
from models import (
    Role, Subject, FAQ, Admin, Tutor, Parent, Student, Session,
    Assignment, AssignmentSubmission, StudyResource, Doubt, AttendanceRecord,
    Message, Notification, MeetingRequest, LearningProgress
)
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Insert Roles if not exist
    roles_list = ['Admin', 'Tutor', 'Parent', 'Student']
    for r_name in roles_list:
        if not Role.query.filter_by(role_name=r_name).first():
            db.session.add(Role(role_name=r_name))
    db.session.commit()

    admin_role = Role.query.filter_by(role_name='Admin').first()
    tutor_role = Role.query.filter_by(role_name='Tutor').first()
    parent_role = Role.query.filter_by(role_name='Parent').first()
    student_role = Role.query.filter_by(role_name='Student').first()

    # 2. Seed Default Admin if not exist
    if not Admin.query.filter_by(username='admin').first():
        admin_user = Admin(
            role_id=admin_role.role_id,
            username='admin',
            password_hash=generate_password_hash('admin123'),
            admin_name='Admin User',
            email='admin@learnathome.com'
        )
        db.session.add(admin_user)

    # 3. Seed Default Tutor (Anjali Mehta / Demo Tutor)
    tutor_user = Tutor.query.filter_by(email='tutor@example.com').first()
    if not tutor_user:
        tutor_user = Tutor(
            role_id=tutor_role.role_id,
            tutor_name='Anjali Mehta',
            email='tutor@example.com',
            phone_no='+91 98765 43210',
            experience_years=7,
            bio='Home tuition specialist focused on Maths and Physics foundations for Classes 9-11.',
            subjects_json=json.dumps(['Mathematics', 'Physics', 'Algebra', 'Trigonometry']),
            education='M.Sc. Mathematics, B.Ed.',
            hourly_rate='₹500/hr',
            availability='Mon-Sat · 4:00-8:00 PM',
            languages_json=json.dumps(['English', 'Hindi', 'Tamil']),
            certificates_json=json.dumps(['Advanced Pedagogy', 'Child Learning Psychology', 'STEM Mentor']),
            password_hash=generate_password_hash('tutor123'),
            status='Active'
        )
        db.session.add(tutor_user)
        db.session.commit()
    else:
        # Update profile attributes if empty
        if not tutor_user.bio:
            tutor_user.tutor_name = 'Anjali Mehta'
            tutor_user.bio = 'Home tuition specialist focused on Maths and Physics foundations for Classes 9-11.'
            tutor_user.subjects_json = json.dumps(['Mathematics', 'Physics', 'Algebra', 'Trigonometry'])
            tutor_user.education = 'M.Sc. Mathematics, B.Ed.'
            tutor_user.hourly_rate = '₹500/hr'
            tutor_user.availability = 'Mon-Sat · 4:00-8:00 PM'
            tutor_user.languages_json = json.dumps(['English', 'Hindi', 'Tamil'])
            tutor_user.certificates_json = json.dumps(['Advanced Pedagogy', 'Child Learning Psychology', 'STEM Mentor'])
            db.session.commit()

    # 4. Seed Sample Subjects
    sub_math = Subject.query.filter_by(subject_name='Mathematics').first()
    if not sub_math:
        sub_math = Subject(subject_name='Mathematics')
        db.session.add(sub_math)
    sub_phy = Subject.query.filter_by(subject_name='Physics').first()
    if not sub_phy:
        sub_phy = Subject(subject_name='Physics')
        db.session.add(sub_phy)
    sub_eng = Subject.query.filter_by(subject_name='English').first()
    if not sub_eng:
        sub_eng = Subject(subject_name='English')
        db.session.add(sub_eng)
    db.session.commit()

    # 5. Seed Demo Parents & Students
    parents_data = [
        {'name': 'Mr. Sharma', 'email': 'sharma.parent@example.com', 'phone': '+91 98765 12001'},
        {'name': 'Mrs. Rao', 'email': 'rao.parent@example.com', 'phone': '+91 98765 12002'},
        {'name': 'Mrs. Joshi', 'email': 'joshi.parent@example.com', 'phone': '+91 98765 12003'}
    ]
    parent_objs = {}
    for pdata in parents_data:
        p = Parent.query.filter_by(email=pdata['email']).first()
        if not p:
            p = Parent(
                role_id=parent_role.role_id,
                parent_name=pdata['name'],
                email=pdata['email'],
                phone_no=pdata['phone'],
                password_hash=generate_password_hash('parent123'),
                status='Active'
            )
            db.session.add(p)
            db.session.commit()
        parent_objs[pdata['email']] = p

    students_data = [
        {'name': 'Aarav Sharma', 'email': 'aarav@example.com', 'school': 'Class 10', 'parent': parent_objs['sharma.parent@example.com'].parent_id},
        {'name': 'Diya Rao', 'email': 'diya@example.com', 'school': 'Class 9', 'parent': parent_objs['rao.parent@example.com'].parent_id},
        {'name': 'Kabir Joshi', 'email': 'kabir@example.com', 'school': 'Class 11', 'parent': parent_objs['joshi.parent@example.com'].parent_id}
    ]
    student_objs = {}
    for sdata in students_data:
        s = Student.query.filter_by(email=sdata['email']).first()
        if not s:
            s = Student(
                role_id=student_role.role_id,
                parent_id=sdata['parent'],
                student_name=sdata['name'],
                email=sdata['email'],
                school=sdata['school'],
                password_hash=generate_password_hash('student123'),
                status='Active'
            )
            db.session.add(s)
            db.session.commit()
        student_objs[sdata['name']] = s

    # Ensure demo student@example.com exists
    if not Student.query.filter_by(email='student@example.com').first():
        db.session.add(Student(
            role_id=student_role.role_id,
            parent_id=parent_objs['sharma.parent@example.com'].parent_id,
            student_name='Demo Student',
            email='student@example.com',
            school='Class 10',
            password_hash=generate_password_hash('student123'),
            status='Active'
        ))
        db.session.commit()

    # 6. Seed Sessions
    if not Session.query.filter_by(tutor_id=tutor_user.tutor_id).first():
        s1 = Session(tutor_id=tutor_user.tutor_id, subject_id=sub_math.subject_id, session_date=date.today(), start_time=time(14, 30), end_time=time(15, 30), session_type='Regular', status='Completed')
        s2 = Session(tutor_id=tutor_user.tutor_id, subject_id=sub_math.subject_id, session_date=date.today(), start_time=time(16, 0), end_time=time(17, 0), session_type='Regular', status='Scheduled')
        s3 = Session(tutor_id=tutor_user.tutor_id, subject_id=sub_phy.subject_id, session_date=date.today(), start_time=time(17, 30), end_time=time(18, 30), session_type='Regular', status='Scheduled')
        s4 = Session(tutor_id=tutor_user.tutor_id, subject_id=sub_math.subject_id, session_date=date.today(), start_time=time(19, 0), end_time=time(20, 0), session_type='One-to-One', status='Scheduled')
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

    # 7. Seed Attendance
    if not AttendanceRecord.query.filter_by(tutor_id=tutor_user.tutor_id).first():
        aarav = student_objs.get('Aarav Sharma')
        diya = student_objs.get('Diya Rao')
        kabir = student_objs.get('Kabir Joshi')
        if aarav and diya and kabir:
            a1 = AttendanceRecord(tutor_id=tutor_user.tutor_id, student_id=aarav.student_id, status='Present', date=date.today())
            a2 = AttendanceRecord(tutor_id=tutor_user.tutor_id, student_id=diya.student_id, status='Present', date=date.today())
            a3 = AttendanceRecord(tutor_id=tutor_user.tutor_id, student_id=kabir.student_id, status='Absent', date=date.today())
            db.session.add_all([a1, a2, a3])
            db.session.commit()

    # 8. Seed Assignments
    if not Assignment.query.first():
        s_math = Session.query.filter_by(tutor_id=tutor_user.tutor_id).first()
        if s_math:
            asg1 = Assignment(session_id=s_math.session_id, title='Weekly quiz · Quadratics', description='Class 10 · 6 submissions', due_date=date.today())
            asg2 = Assignment(session_id=s_math.session_id, title='Assignment · Exercise 4.2', description='Class 10 · 5 submissions', due_date=date.today())
            asg3 = Assignment(session_id=s_math.session_id, title='Weekly quiz · Motion', description='Physics · 4 submissions', due_date=date.today())
            asg4 = Assignment(session_id=s_math.session_id, title='Worksheet · Algebra basics', description='Class 9 · 2 submissions', due_date=date.today())
            db.session.add_all([asg1, asg2, asg3, asg4])
            db.session.commit()

    # 9. Seed Doubts
    if not Doubt.query.filter_by(tutor_id=tutor_user.tutor_id).first():
        kabir = student_objs.get('Kabir Joshi')
        diya = student_objs.get('Diya Rao')
        if kabir:
            d1 = Doubt(tutor_id=tutor_user.tutor_id, student_id=kabir.student_id, subject='Physics', question="Sir, I didn't understand the discriminant part.", status='Open')
            db.session.add(d1)
        if diya:
            d2 = Doubt(tutor_id=tutor_user.tutor_id, student_id=diya.student_id, subject='Maths', question="Can I get more practice on trigonometry?", status='Open')
            db.session.add(d2)
        db.session.commit()

    # 10. Seed Q&A Board (FAQ)
    if not FAQ.query.first():
        f1 = FAQ(question='Why factor before using the formula?', answer='Factoring often gives a faster path when roots are simple.', category='Maths')
        f2 = FAQ(question='How to check number of roots?', answer='Use the discriminant to identify real, equal, or imaginary roots.', category='Maths')
        db.session.add_all([f1, f2])
        db.session.commit()

    # 11. Seed Study Resources
    if not StudyResource.query.first():
        s_math = Session.query.filter_by(tutor_id=tutor_user.tutor_id).first()
        if s_math:
            r1 = StudyResource(session_id=s_math.session_id, resource_title='Quadratics — Notes.pdf', resource_type='PDF', resource_link='#')
            r2 = StudyResource(session_id=s_math.session_id, resource_title='Motion — Walkthrough.mp4', resource_type='Video', resource_link='#')
            r3 = StudyResource(session_id=s_math.session_id, resource_title='Algebra — Puzzle set', resource_type='Notes', resource_link='#')
            db.session.add_all([r1, r2, r3])
            db.session.commit()

    # 12. Seed Messages
    if not Message.query.first():
        p_rao = parent_objs['rao.parent@example.com']
        m1 = Message(sender_type='Parent', sender_id=p_rao.parent_id, receiver_type='Tutor', receiver_id=tutor_user.tutor_id, subject='Extra classes', message='Will there be extra classes before the test?', reply_message='Yes — added a revision slot Saturday 5:30 PM.', sent_at=datetime.utcnow())
        db.session.add(m1)
        db.session.commit()

    # 13. Seed Notifications
    if not Notification.query.first():
        n1 = Notification(recipient_type='Tutor', recipient_id=tutor_user.tutor_id, title='New doubt from Kabir', message='Physics · 8m ago', notification_type='Doubt', is_read=False)
        n2 = Notification(recipient_type='Tutor', recipient_id=tutor_user.tutor_id, title='Diya submitted the weekly quiz', message='Maths · 1h ago', notification_type='Assignment', is_read=False)
        n3 = Notification(recipient_type='Tutor', recipient_id=tutor_user.tutor_id, title='Mrs. Rao replied to you', message='Message · 2h ago', notification_type='Message', is_read=False)
        db.session.add_all([n1, n2, n3])
        db.session.commit()

    db.session.commit()
    print("Database successfully seeded with Tutor Dashboard test data!")