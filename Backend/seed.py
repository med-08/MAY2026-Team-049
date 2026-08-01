from app import app
from database import db
from models import Role, Subject, FAQ, Admin, Tutor, Parent, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    # Insert Roles if not exist
    roles_list = ['Admin', 'Tutor', 'Parent', 'Student']
    for r_name in roles_list:
        if not Role.query.filter_by(role_name=r_name).first():
            db.session.add(Role(role_name=r_name))
    db.session.commit()

    admin_role = Role.query.filter_by(role_name='Admin').first()
    tutor_role = Role.query.filter_by(role_name='Tutor').first()
    parent_role = Role.query.filter_by(role_name='Parent').first()
    student_role = Role.query.filter_by(role_name='Student').first()

    # Seed Default Admin if not exist
    if not Admin.query.filter_by(username='admin').first():
        admin_user = Admin(
            role_id=admin_role.role_id,
            username='admin',
            password_hash=generate_password_hash('admin123'),
            admin_name='Admin User',
            email='admin@learnathome.com'
        )
        db.session.add(admin_user)

    # Seed Default Tutor if not exist
    if not Tutor.query.filter_by(email='tutor@example.com').first():
        tutor_user = Tutor(
            role_id=tutor_role.role_id,
            tutor_name='Demo Tutor',
            email='tutor@example.com',
            phone_no='1234567890',
            password_hash=generate_password_hash('tutor123'),
            status='Active'
        )
        db.session.add(tutor_user)

    # Seed Default Parent if not exist
    if not Parent.query.filter_by(email='parent@example.com').first():
        parent_user = Parent(
            role_id=parent_role.role_id,
            parent_name='Demo Parent',
            email='parent@example.com',
            phone_no='0987654321',
            password_hash=generate_password_hash('parent123'),
            status='Active'
        )
        db.session.add(parent_user)

    # Seed Default Student if not exist
    if not Student.query.filter_by(email='student@example.com').first():
        student_user = Student(
            role_id=student_role.role_id,
            student_name='Demo Student',
            email='student@example.com',
            phone_no='5555555555',
            password_hash=generate_password_hash('student123'),
            status='Active'
        )
        db.session.add(student_user)
    
    # Insert Sample Subjects
    if not Subject.query.first():
        subjects = [Subject(subject_name='Mathematics'), Subject(subject_name='Science'), Subject(subject_name='English')]
        db.session.add_all(subjects)
        
    # Insert Sample FAQ
    if not FAQ.query.first():
        faqs = [
            FAQ(question="How to book a session?", answer="Select a slot from tutor schedule.", category="General"),
            FAQ(question="Where to see assignments?", answer="Check student dashboard under assignments tab.", category="Academic")
        ]
        db.session.add_all(faqs)

    db.session.commit()
    print("Database successfully seeded with initial test data and default users!")