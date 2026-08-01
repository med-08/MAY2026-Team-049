"""
Shared pytest fixtures for the Admin Dashboard test suite.

Follows the same in-memory-database pattern already used by the project's
existing Backend/test_db.py (swap SQLALCHEMY_DATABASE_URI to sqlite memory,
then drop_all/create_all) so these tests never touch the real
learnathome.db file, and require no changes to app.py.

Because the Admin Dashboard routes are now protected by @admin_required
(session-based), most tests log in as the seeded admin first via the real
POST /login endpoint -- exercising the actual auth flow rather than
bypassing it.
"""
import os
import sys
from datetime import datetime, date, time, timedelta

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database import db as _db
from models import Role, Admin, Student, Tutor, Parent, Subject, StudentSubject, Session


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            _db.drop_all()  # clear any tables from a previous test/import
            _db.create_all()
            yield test_client


@pytest.fixture
def seed_roles(client):
    roles = {}
    for name in ['Admin', 'Tutor', 'Parent', 'Student']:
        r = Role(role_name=name)
        _db.session.add(r)
        roles[name] = r
    _db.session.commit()
    return roles


@pytest.fixture
def seed_admin(client, seed_roles):
    admin = Admin(
        role_id=seed_roles['Admin'].role_id,
        username='admin',
        password_hash=generate_password_hash('admin123'),
        admin_name='Admin User',
        email='admin@learnathome.com',
    )
    _db.session.add(admin)
    _db.session.commit()
    return admin


@pytest.fixture
def admin_client(client, seed_admin):
    """A test client already logged in as the seeded Admin (real session,
    via the actual POST /login endpoint -- not a bypass)."""
    resp = client.post('/login', json={'identifier': 'admin', 'password': 'admin123'})
    assert resp.status_code == 200, resp.get_json()
    assert resp.get_json()['success'] is True
    return client


@pytest.fixture
def seed_subjects(client):
    subjects = {}
    for name in ['Mathematics', 'Science', 'English']:
        s = Subject(subject_name=name)
        _db.session.add(s)
        subjects[name] = s
    _db.session.commit()
    return subjects


@pytest.fixture
def seed_parent(client, seed_roles):
    parent = Parent(
        role_id=seed_roles['Parent'].role_id,
        parent_name='Rajesh Mehta',
        email='rajesh.mehta@parentmail.com',
        phone_no='+1 200 555 1000',
        password_hash=generate_password_hash('Parent@123'),
        status='Active',
        registered_at=datetime.utcnow(),
    )
    _db.session.add(parent)
    _db.session.commit()
    return parent


@pytest.fixture
def seed_students(client, seed_roles, seed_subjects, seed_parent):
    s1 = Student(
        role_id=seed_roles['Student'].role_id,
        parent_id=seed_parent.parent_id,
        student_name='Aarav Mehta',
        email='aarav.mehta@learnmail.com',
        school='Greenfield High School',
        password_hash=generate_password_hash('Student@123'),
        status='Active',
        registered_at=datetime.utcnow() - timedelta(days=40),
    )
    s2 = Student(
        role_id=seed_roles['Student'].role_id,
        student_name='Isha Kapoor',
        email='isha.kapoor@learnmail.com',
        school='Riverside International School',
        password_hash=generate_password_hash('Student@123'),
        status='Blocked',
        registered_at=datetime.utcnow() - timedelta(days=10),
    )
    s3 = Student(
        role_id=seed_roles['Student'].role_id,
        student_name='Liam Johnson',
        email='liam.johnson@learnmail.com',
        school='Maple Grove Academy',
        password_hash=generate_password_hash('Student@123'),
        status='Pending',
        registered_at=datetime.utcnow(),
    )
    _db.session.add_all([s1, s2, s3])
    _db.session.commit()

    _db.session.add_all([
        StudentSubject(student_id=s1.student_id, subject_id=seed_subjects['Mathematics'].subject_id),
        StudentSubject(student_id=s2.student_id, subject_id=seed_subjects['Science'].subject_id),
    ])
    _db.session.commit()
    return [s1, s2, s3]


@pytest.fixture
def seed_tutors(client, seed_roles, seed_subjects):
    t1 = Tutor(
        role_id=seed_roles['Tutor'].role_id,
        tutor_name='Dr. Sarah Bennett',
        email='sarah.bennett@tutormail.com',
        experience_years=8,
        password_hash=generate_password_hash('Tutor@123'),
        status='Active',
        registered_at=datetime.utcnow() - timedelta(days=100),
    )
    t2 = Tutor(
        role_id=seed_roles['Tutor'].role_id,
        tutor_name='Nathan Cole',
        email='nathan.cole@tutormail.com',
        experience_years=2,
        password_hash=generate_password_hash('Tutor@123'),
        status='Pending',
        registered_at=datetime.utcnow(),
    )
    _db.session.add_all([t1, t2])
    _db.session.commit()

    session1 = Session(
        tutor_id=t1.tutor_id,
        subject_id=seed_subjects['Mathematics'].subject_id,
        session_date=date.today(),
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    _db.session.add(session1)
    _db.session.commit()
    return [t1, t2]
