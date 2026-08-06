"""
Test cases for /login and /register (Backend/auth/routes.py)

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| POST /login | missing identifier & password | 400 Bad Request | 400 Bad Request | Success |
| POST /login | unknown identifier | 401 Unauthorized | 401 Unauthorized | Success |
| POST /login | correct identifier, wrong password | 401 Unauthorized | 401 Unauthorized | Success |
| POST /login | correct email + password (Student) | 200, token/role/redirect_url returned | 200, token/role/redirect_url returned | Success |
| POST /login | correct username + password (Admin) | 200, role == "Admin" | 200, role == "Admin" | Success |
| POST /login | credentials for a Pending account | 403 Forbidden | 403 Forbidden | Success |
| POST /login | credentials for a Blocked account | 403 Forbidden | 403 Forbidden | Success |
| POST /login | valid login updates last_login_at | last_login_at is set | last_login_at is set | Success |
| POST /register | empty body | 400 Bad Request | 400 Bad Request | Success |
| POST /register | password < 6 chars | 400 Bad Request | 400 Bad Request | Success |
| POST /register | password != confirm_password | 400 Bad Request | 400 Bad Request | Success |
| POST /register | invalid email format | 400 Bad Request | 400 Bad Request | Success |
| POST /register | role not in [Student, Parent] | 400 Bad Request | 400 Bad Request | Success |
| POST /register | email already exists | 400 Bad Request | 400 Bad Request | Success |
| POST /register | valid Student payload | 200, Student row created (status Active) | 200, Student row created (status Active) | Success |
| POST /register | valid Parent payload | 200, Parent row created (status Active) | 200, Parent row created (status Active) | Success |
| POST /register | already logged in (existing session) | 200, redirect_url for current role, no new row | 200, redirect_url for current role, no new row | Success |
"""
from datetime import datetime, timedelta

import pytest
from werkzeug.security import generate_password_hash

from app import app as flask_app
from database import db as _db
from models import Admin, Parent, Role, Student, Subject, StudentSubject, Tutor


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            _db.drop_all()
            _db.create_all()
            yield test_client


@pytest.fixture
def seed_roles(client):
    roles = {}
    for name in ['Admin', 'Tutor', 'Parent', 'Student']:
        role = Role(role_name=name)
        _db.session.add(role)
        roles[name] = role
    _db.session.commit()
    return roles


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
def seed_subjects(client):
    subjects = {}
    for name in ['Mathematics', 'Science', 'English']:
        subject = Subject(subject_name=name)
        _db.session.add(subject)
        subjects[name] = subject
    _db.session.commit()
    return subjects


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


# ----------------------------- /login ------------------------------------

def test_login_missing_fields(client):
    resp = client.post('/login', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_login_unknown_identifier(client, seed_roles):
    resp = client.post('/login', json={'identifier': 'nobody@nowhere.com', 'password': 'whatever'})
    assert resp.status_code == 401
    assert resp.get_json()['success'] is False


def test_login_wrong_password(client, seed_students):
    resp = client.post('/login', json={'identifier': 'aarav.mehta@learnmail.com', 'password': 'WrongPass'})
    assert resp.status_code == 401
    assert resp.get_json()['success'] is False


def test_login_success_student(client, seed_students):
    resp = client.post('/login', json={'identifier': 'aarav.mehta@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['role'] == 'Student'
    assert data['username'] == 'Aarav Mehta'
    assert data['redirect_url'] == '/student'
    assert 'token' in data and data['token']


def test_login_success_admin_by_username(client, seed_admin):
    resp = client.post('/login', json={'identifier': 'admin', 'password': 'admin123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['role'] == 'Admin'
    assert data['redirect_url'] == '/admin'


def test_login_pending_account_forbidden(client, seed_students):
    # s3 "Liam Johnson" is seeded with status='Pending'
    resp = client.post('/login', json={'identifier': 'liam.johnson@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 403
    assert 'pending' in resp.get_json()['message'].lower()


def test_login_blocked_account_forbidden(client, seed_students):
    # s2 "Isha Kapoor" is seeded with status='Blocked'
    resp = client.post('/login', json={'identifier': 'isha.kapoor@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 403
    assert 'blocked' in resp.get_json()['message'].lower()


def test_login_updates_last_login_at(client, seed_students):
    student = seed_students[0]
    assert student.last_login_at is None

    resp = client.post('/login', json={'identifier': student.email, 'password': 'Student@123'})
    assert resp.status_code == 200

    refreshed = _db.session.get(Student, student.student_id)
    assert refreshed.last_login_at is not None


# ----------------------------- /register ----------------------------------

def _valid_student_payload(**overrides):
    payload = {
        'name': 'New Student',
        'email': 'new.student@learnmail.com',
        'password': 'Passw0rd!',
        'confirm_password': 'Passw0rd!',
        'role': 'Student',
    }
    payload.update(overrides)
    return payload


def test_register_empty_body(client, seed_roles):
    resp = client.post('/register', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_register_password_too_short(client, seed_roles):
    resp = client.post('/register', json=_valid_student_payload(password='abc', confirm_password='abc'))
    assert resp.status_code == 400


def test_register_password_mismatch(client, seed_roles):
    resp = client.post('/register', json=_valid_student_payload(confirm_password='Different1!'))
    assert resp.status_code == 400


def test_register_invalid_email(client, seed_roles):
    resp = client.post('/register', json=_valid_student_payload(email='not-an-email'))
    assert resp.status_code == 400


def test_register_invalid_role(client, seed_roles):
    resp = client.post('/register', json=_valid_student_payload(role='Tutor'))
    assert resp.status_code == 400


def test_register_duplicate_email(client, seed_roles, seed_students):
    resp = client.post('/register', json=_valid_student_payload(email='aarav.mehta@learnmail.com'))
    assert resp.status_code == 400 
    assert 'already exists' in resp.get_json()['message'].lower()


def test_register_student_success(client, seed_roles):
    resp = client.post('/register', json=_valid_student_payload())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    created = Student.query.filter_by(email='new.student@learnmail.com').first()
    assert created is not None
    assert created.student_name == 'New Student'
    assert created.status == 'Active'
    assert created.password_hash != 'Passw0rd!'  # must be hashed


def test_register_parent_success(client, seed_roles):
    payload = _valid_student_payload(
        name='New Parent',
        email='new.parent@parentmail.com',
        role='Parent',
    )
    resp = client.post('/register', json=payload)
    assert resp.status_code == 200

    created = Parent.query.filter_by(email='new.parent@parentmail.com').first()
    assert created is not None
    assert created.parent_name == 'New Parent'
    assert created.status == 'Active'


def test_register_already_logged_in_short_circuits(client, seed_students):
    student = seed_students[0]
    login_resp = client.post('/login', json={'identifier': student.email, 'password': 'Student@123'})
    assert login_resp.status_code == 200

    before_count = Student.query.count()
    resp = client.post('/register', json=_valid_student_payload(email='should.not.be.created@learnmail.com'))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['redirect_url'] == '/student'

    # no new row should have been created since registration short-circuited
    assert Student.query.count() == before_count



