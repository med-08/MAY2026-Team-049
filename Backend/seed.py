import json
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash

from app import app
from database import db
from models import (
Role,
Subject,
FAQ,
Admin,
Tutor,
Parent,
Student,
StudentSubject,
Session,
SessionBooking,
SessionUpdate,
Assignment,
AssignmentSubmission,
StudyResource,
StudyTip,
Doubt,
AttendanceRecord,
Message,
Notification,
MeetingRequest,
LearningProgress,
TeachingPlan,
Quiz,
QuizAttempt,
WeeklySummary
)

with app.app_context():
\# IMPORTANT: create all missing tables first
db.create_all()

# 1. Roles
roles_list = ['Admin', 'Tutor', 'Parent', 'Student']
for r_name in roles_list:
    if not Role.query.filter_by(role_name=r_name).first():
        db.session.add(Role(role_name=r_name))
db.session.commit()

admin_role = Role.query.filter_by(role_name='Admin').first()
tutor_role = Role.query.filter_by(role_name='Tutor').first()
parent_role = Role.query.filter_by(role_name='Parent').first()
student_role = Role.query.filter_by(role_name='Student').first()

# 2. Default admin
# Repair the existing admin too, so an old/wrong password cannot survive.
admin_user = Admin.query.filter_by(username='admin').first()

if not admin_user:
    admin_user = Admin(
        role_id=admin_role.role_id,
        username='admin',
        password_hash=generate_password_hash('admin123'),
        admin_name='Admin User',
        email='admin@learnathome.com'
    )
    db.session.add(admin_user)
else:
    admin_user.role_id = admin_role.role_id
    admin_user.username = 'admin'
    admin_user.password_hash = generate_password_hash('admin123')
    admin_user.admin_name = 'Admin User'
    admin_user.email = 'admin@learnathome.com'

db.session.commit()

# 3. Default tutor
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

# Repair existing seeded tutor credentials/status too.
tutor_user.role_id = tutor_role.role_id
tutor_user.password_hash = generate_password_hash('tutor123')
tutor_user.status = 'Active'
db.session.commit()

# 5. Subjects
subject_names = ['Mathematics', 'Physics', 'Science']
subjects = {}
for name in subject_names:
    obj = Subject.query.filter_by(subject_name=name).first()
    if not obj:
        obj = Subject(subject_name=name)
        db.session.add(obj)
        db.session.commit()
    subjects[name] = obj

# 6. Parents
parents_data = [
    {'name': 'Mr. Sharma', 'email': 'sharma.parent@example.com', 'phone': '+91 98765 12001'},
    {'name': 'Mrs. Rao', 'email': 'rao.parent@example.com', 'phone': '+91 98765 12002'},
    {'name': 'Mrs. Joshi', 'email': 'joshi.parent@example.com', 'phone': '+91 98765 12003'},
    {'name': 'Demo Parent', 'email': 'parent@gmail.com', 'phone': '+91 90000 00001'}
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
            password_hash=generate_password_hash('123456'),
            status='Active'
        )
        db.session.add(p)
        db.session.commit()
    else:
        p.role_id = parent_role.role_id
        p.password_hash = generate_password_hash('123456')
        p.status = 'Active'
        p.parent_name = pdata['name']
        p.phone_no = pdata['phone']
        db.session.commit()

    parent_objs[pdata['email']] = p

# 7. Students
# Seeded students are always repaired to the intended parent account.
# This also fixes older databases where a student row existed but
# parent_id was left NULL.
students_data = [
    {
        'name': 'Aarav Sharma',
        'email': 'aarav@example.com',
        'school': 'Class 10',
        'parent_email': 'sharma.parent@example.com'
    },
    {
        'name': 'Diya Rao',
        'email': 'diya@example.com',
        'school': 'Class 9',
        'parent_email': 'rao.parent@example.com'
    },
    {
        'name': 'Kabir Joshi',
        'email': 'kabir@example.com',
        'school': 'Class 11',
        'parent_email': 'joshi.parent@example.com'
    },
    {
        'name': 'Demo Student',
        'email': 'student@gmail.com',
        'school': 'Class 10',
        'parent_email': 'parent@gmail.com'
    }
]

student_objs = {}

for sdata in students_data:
    parent_obj = parent_objs[sdata['parent_email']]

    s = Student.query.filter_by(email=sdata['email']).first()

    if not s:
        s = Student(
            role_id=student_role.role_id,
            parent_id=parent_obj.parent_id,
            student_name=sdata['name'],
            email=sdata['email'],
            school=sdata['school'],
            password_hash=generate_password_hash('123456'),
            status='Active'
        )
        db.session.add(s)
        db.session.commit()
    else:
        # IMPORTANT: repair the parent relationship on existing seeded
        # students instead of only setting it during INSERT.
        changed = False

        if s.parent_id != parent_obj.parent_id:
            s.parent_id = parent_obj.parent_id
            changed = True

        if s.role_id != student_role.role_id:
            s.role_id = student_role.role_id
            changed = True

        # Keep seeded login credentials deterministic.
        s.password_hash = generate_password_hash('123456')

        if not s.school:
            s.school = sdata['school']
            changed = True

        if s.status in (None, '', 'Pending'):
            s.status = 'Active'
            changed = True

        if changed:
            db.session.commit()

    student_objs[sdata['name']] = s

# 8. Student subjects
# Each student is enrolled in the subject(s) relevant to their profile,
# so the admin dashboard shows a real, non-empty subject list per student
# instead of only the demo account having one.
student_subject_map = {
    'Aarav Sharma': ['Mathematics'],
    'Diya Rao': ['Physics'],
    'Kabir Joshi': ['Science'],
    'Demo Student': ['Mathematics', 'Science'],
}
for student_name, subject_list in student_subject_map.items():
    student_obj = student_objs.get(student_name)
    if not student_obj:
        continue
    for subject_name in subject_list:
        subject_obj = subjects.get(subject_name)
        if not subject_obj:
            continue
        exists = StudentSubject.query.filter_by(
            student_id=student_obj.student_id,
            subject_id=subject_obj.subject_id
        ).first()
        if not exists:
            db.session.add(StudentSubject(
                student_id=student_obj.student_id,
                subject_id=subject_obj.subject_id
            ))
db.session.commit()

demo_student = Student.query.filter_by(email='student@gmail.com').first()

# 9. Sessions
if not Session.query.filter_by(tutor_id=tutor_user.tutor_id).first():
    s1 = Session(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Mathematics'].subject_id,
        session_date=date.today(),
        start_time=time(14, 30),
        end_time=time(15, 30),
        session_type='Regular',
        status='Completed'
    )
    s2 = Session(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Mathematics'].subject_id,
        session_date=date.today(),
        start_time=time(16, 0),
        end_time=time(17, 0),
        session_type='Regular',
        status='Scheduled'
    )
    s3 = Session(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Physics'].subject_id,
        session_date=date.today(),
        start_time=time(17, 30),
        end_time=time(18, 30),
        session_type='Regular',
        status='Scheduled'
    )
    s4 = Session(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Mathematics'].subject_id,
        session_date=date.today(),
        start_time=time(19, 0),
        end_time=time(20, 0),
        session_type='One-to-One',
        status='Scheduled'
    )
    db.session.add_all([s1, s2, s3, s4])
    db.session.commit()

all_sessions = Session.query.filter_by(tutor_id=tutor_user.tutor_id).all()

# 10. Session bookings
# There is no direct Tutor <-> Parent foreign key in the current schema.
# The real relationship is Tutor -> Session -> SessionBooking -> Student
# -> Parent. These bookings make the Tutor/Student/Parent chain visible
# throughout the dashboards and communication APIs.
#
# Book each seeded student into a suitable tutor session. Existing
# bookings are preserved; missing links are added.
if all_sessions:
    student_subject_preferences = {
        'Aarav Sharma': ['Mathematics'],
        'Diya Rao': ['Physics'],
        'Kabir Joshi': ['Science'],
        'Demo Student': ['Mathematics', 'Science'],
    }

    for student_name, preferred_subjects in student_subject_preferences.items():
        student_obj = student_objs.get(student_name)

        if not student_obj:
            continue

        student_subject_ids = {
            subjects[name].subject_id
            for name in preferred_subjects
            if name in subjects
        }

        matching_sessions = [
            sess for sess in all_sessions
            if sess.subject_id in student_subject_ids
        ]

        # Always give the student at least one tutor relationship.
        if not matching_sessions:
            matching_sessions = all_sessions[:1]

        for sess in matching_sessions[:2]:
            exists = SessionBooking.query.filter_by(
                session_id=sess.session_id,
                student_id=student_obj.student_id
            ).first()

            if not exists:
                db.session.add(SessionBooking(
                    session_id=sess.session_id,
                    student_id=student_obj.student_id,
                    booking_status='Confirmed'
                ))

    db.session.commit()

# Explicit relationship verification for the seeded accounts.
# This does not create a new schema/table: it confirms that every
# seeded student has both a parent and a tutor session connection.
for student_name, student_obj in student_objs.items():
    if not student_obj.parent_id:
        raise RuntimeError(
            f"Seed relationship error: {student_name} has no parent_id"
        )

    has_tutor_link = (
        db.session.query(SessionBooking)
        .join(Session, Session.session_id == SessionBooking.session_id)
        .filter(
            SessionBooking.student_id == student_obj.student_id,
            Session.tutor_id == tutor_user.tutor_id
        )
        .first()
    )

    if not has_tutor_link:
        raise RuntimeError(
            f"Seed relationship error: {student_name} has no tutor session link"
        )

# 11. Session updates
completed_session = Session.query.filter_by(status='Completed').first()
if completed_session and not SessionUpdate.query.filter_by(session_id=completed_session.session_id).first():
    db.session.add(SessionUpdate(
        session_id=completed_session.session_id,
        topics_covered='Quadratic equations and basic factorization',
        homework_assigned='Worksheet 4A',
        next_session_date=date.today(),
        notification_time=datetime.utcnow()
    ))
    db.session.commit()

# 12. Attendance
if not AttendanceRecord.query.filter_by(tutor_id=tutor_user.tutor_id).first():
    aarav = student_objs.get('Aarav Sharma')
    diya = student_objs.get('Diya Rao')
    kabir = student_objs.get('Kabir Joshi')
    if aarav:
        db.session.add(AttendanceRecord(
            tutor_id=tutor_user.tutor_id,
            student_id=aarav.student_id,
            session_id=completed_session.session_id if completed_session else None,
            status='Present',
            date=date.today()
        ))
    if diya:
        db.session.add(AttendanceRecord(
            tutor_id=tutor_user.tutor_id,
            student_id=diya.student_id,
            session_id=completed_session.session_id if completed_session else None,
            status='Present',
            date=date.today()
        ))
    if kabir:
        db.session.add(AttendanceRecord(
            tutor_id=tutor_user.tutor_id,
            student_id=kabir.student_id,
            session_id=completed_session.session_id if completed_session else None,
            status='Absent',
            date=date.today()
        ))
    if demo_student:
        db.session.add(AttendanceRecord(
            tutor_id=tutor_user.tutor_id,
            student_id=demo_student.student_id,
            session_id=completed_session.session_id if completed_session else None,
            status='Present',
            date=date.today()
        ))
    db.session.commit()

# 13. Assignments
if not Assignment.query.first() and completed_session:
    asg1 = Assignment(
        session_id=completed_session.session_id,
        title='Weekly quiz · Quadratics',
        description='Class 10 · 6 submissions',
        due_date=date.today()
    )
    asg2 = Assignment(
        session_id=completed_session.session_id,
        title='Assignment · Exercise 4.2',
        description='Class 10 · 5 submissions',
        due_date=date.today()
    )
    db.session.add_all([asg1, asg2])
    db.session.commit()

# 14. Assignment submissions
first_assignment = Assignment.query.first()
if first_assignment and demo_student:
    sub = AssignmentSubmission.query.filter_by(
        assignment_id=first_assignment.assignment_id,
        student_id=demo_student.student_id
    ).first()
    if not sub:
        db.session.add(AssignmentSubmission(
            assignment_id=first_assignment.assignment_id,
            student_id=demo_student.student_id,
            status='Submitted',
            progress_percentage=100,
            tutor_feedback='Good work.'
        ))
        db.session.commit()

# 15. Learning progress
if completed_session and demo_student:
    lp = LearningProgress.query.filter_by(
        session_id=completed_session.session_id,
        student_id=demo_student.student_id
    ).first()
    if not lp:
        db.session.add(LearningProgress(
            session_id=completed_session.session_id,
            student_id=demo_student.student_id,
            session_completion_status='Completed',
            learning_pace='Average',
            tutor_remarks='Doing well, needs a bit more practice in word problems.'
        ))
        db.session.commit()

# 16. Study resources
if not StudyResource.query.first() and completed_session:
    r1 = StudyResource(
        session_id=completed_session.session_id,
        resource_title='Quadratics — Notes.pdf',
        resource_type='PDF',
        resource_link='#'
    )
    r2 = StudyResource(
        session_id=completed_session.session_id,
        resource_title='Factorization Walkthrough',
        resource_type='Video',
        resource_link='#'
    )
    db.session.add_all([r1, r2])
    db.session.commit()

# 17. Study tips
if completed_session and demo_student and not StudyTip.query.filter_by(
    session_id=completed_session.session_id,
    student_id=demo_student.student_id
).first():
    db.session.add(StudyTip(
        session_id=completed_session.session_id,
        student_id=demo_student.student_id,
        tip_text='Practice 5 algebra problems daily for faster improvement.'
    ))
    db.session.commit()

# 18. Teaching plan
if not TeachingPlan.query.first():
    db.session.add(TeachingPlan(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Mathematics'].subject_id,
        month='August 2026',
        topic_name='Algebra Basics',
        planned_date=date.today()
    ))
    db.session.add(TeachingPlan(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Science'].subject_id,
        month='August 2026',
        topic_name='Force and Motion',
        planned_date=date.today()
    ))
    db.session.commit()

# 19. Quiz + attempt
quiz = Quiz.query.filter_by(title='Math Weekly Quiz 1').first()
if not quiz:
    quiz = Quiz(
        tutor_id=tutor_user.tutor_id,
        subject_id=subjects['Mathematics'].subject_id,
        title='Math Weekly Quiz 1',
        week_number=1
    )
    db.session.add(quiz)
    db.session.commit()

if demo_student:
    qa = QuizAttempt.query.filter_by(
        quiz_id=quiz.quiz_id,
        student_id=demo_student.student_id
    ).first()
    if not qa:
        db.session.add(QuizAttempt(
            quiz_id=quiz.quiz_id,
            student_id=demo_student.student_id,
            score=82
        ))
        db.session.commit()

# 20. Weekly summary
if demo_student and not WeeklySummary.query.filter_by(student_id=demo_student.student_id).first():
    db.session.add(WeeklySummary(
        tutor_id=tutor_user.tutor_id,
        student_id=demo_student.student_id,
        week_start=date.today(),
        week_end=date.today(),
        topics_taught='Algebra basics and factorization',
        homework_summary='Worksheet 4A and revision practice',
        areas_for_improvement='Needs more confidence in solving multi-step problems'
    ))
    db.session.commit()

# 21. Doubts
if not Doubt.query.filter_by(tutor_id=tutor_user.tutor_id).first():
    if demo_student:
        db.session.add(Doubt(
            tutor_id=tutor_user.tutor_id,
            student_id=demo_student.student_id,
            subject='Maths',
            question="Can I get more practice on algebra?",
            status='Open'
        ))
    db.session.commit()

# 22. FAQ
if not FAQ.query.first():
    db.session.add(FAQ(
        question='Why factor before using the formula?',
        answer='Factoring can be faster when the roots are simple.',
        category='Maths'
    ))
    db.session.add(FAQ(
        question='How to check number of roots?',
        answer='Use the discriminant to identify real, equal, or imaginary roots.',
        category='Maths'
    ))
    db.session.commit()

# 23. Messages
if not Message.query.first():
    demo_parent = parent_objs.get('parent@gmail.com')
    if demo_parent:
        db.session.add(Message(
            sender_type='Parent',
            sender_id=demo_parent.parent_id,
            receiver_type='Tutor',
            receiver_id=tutor_user.tutor_id,
            subject='Extra classes',
            message='Will there be extra classes before the test?',
            reply_message='Yes — a revision slot has been added.',
            sent_at=datetime.utcnow()
        ))
        db.session.commit()

# 24. Notifications
if not Notification.query.first():
    db.session.add(Notification(
        recipient_type='Tutor',
        recipient_id=tutor_user.tutor_id,
        title='New doubt from student',
        message='Maths doubt posted recently.',
        notification_type='Doubt',
        is_read=False
    ))
    db.session.add(Notification(
        recipient_type='Parent',
        recipient_id=parent_objs['parent@gmail.com'].parent_id,
        title='Weekly summary available',
        message='Your child weekly summary has been posted.',
        notification_type='Weekly Summary',
        is_read=False
    ))
    db.session.commit()

# 25. Meeting requests / Tutor <-> Parent communication
# There is intentionally no direct tutor_id/parent_id relationship
# table in the current model. A MeetingRequest links the tutor, student
# and that student's parent, which is the application's real
# Tutor -> Student -> Parent relationship.
for student_name, student_obj in student_objs.items():
    if not student_obj.parent_id:
        continue

    existing_meeting = MeetingRequest.query.filter_by(
        tutor_id=tutor_user.tutor_id,
        student_id=student_obj.student_id,
        parent_id=student_obj.parent_id
    ).first()

    if not existing_meeting:
        db.session.add(MeetingRequest(
            tutor_id=tutor_user.tutor_id,
            student_id=student_obj.student_id,
            parent_id=student_obj.parent_id,
            meeting_date=datetime.utcnow(),
            meeting_link=None,
            meeting_reason='Discuss progress and next steps',
            status='Scheduled'
        ))

db.session.commit()

# Seed a parent <-> tutor message for the demo parent. This is useful
# for verifying the tutor Messages screen against real DB data.
demo_parent = parent_objs.get('parent@gmail.com')

if demo_parent:
    existing_message = Message.query.filter_by(
        sender_type='Parent',
        sender_id=demo_parent.parent_id,
        receiver_type='Tutor',
        receiver_id=tutor_user.tutor_id
    ).first()

    if not existing_message:
        db.session.add(Message(
            sender_type='Parent',
            sender_id=demo_parent.parent_id,
            receiver_type='Tutor',
            receiver_id=tutor_user.tutor_id,
            subject='Student progress',
            message='Can we discuss the student progress and next steps?',
            reply_message='Yes — a progress discussion meeting has been scheduled.',
            sent_at=datetime.utcnow(),
            replied_at=datetime.utcnow()
        ))
        db.session.commit()

# Tutor-specific notification for the demo parent/student relationship.
# Do not duplicate it if the seed is run again.
demo_student = student_objs.get('Demo Student')

if demo_student and demo_parent:
    notification_exists = Notification.query.filter_by(
        recipient_type='Tutor',
        recipient_id=tutor_user.tutor_id,
        notification_type='Meeting'
    ).first()

    if not notification_exists:
        db.session.add(Notification(
            recipient_type='Tutor',
            recipient_id=tutor_user.tutor_id,
            title='One-on-one meeting scheduled',
            message=(
                f'One-on-one meeting scheduled for '
                f'{demo_student.student_name} with their parent.'
            ),
            notification_type='Meeting',
            is_read=False
        ))
        db.session.commit()


print("Database successfully created and seeded!")

# ---------------------------------------------------------------------------
# DEMO LOGIN CREDENTIALS
# Admin:   admin@learnathome.com  / admin123
#          username "admin"       / admin123
# Tutor:   tutor@example.com      / tutor123
# Parent:  parent@gmail.com       / 123456
# Student: student@gmail.com      / 123456
#
# DEMO RELATIONSHIP
# student@gmail.com -> parent@gmail.com
# Tutor relationship is through:
# tutor@example.com -> Session -> SessionBooking -> student@gmail.com
# ---------------------------------------------------------------------------