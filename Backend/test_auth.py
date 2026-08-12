"""
Test cases for /login and /register (Backend/auth/routes.py)

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| POST /auth/login | missing identifier & password | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/login | unknown identifier | 401 Unauthorized | 401 Unauthorized | Success |
| POST /auth/login | correct identifier, wrong password | 401 Unauthorized | 401 Unauthorized | Success |
| POST /auth/login | correct email + password (Student) | 200, token/role/redirect_url returned | 200, token/role/redirect_url returned | Success |
| POST /auth/login | correct username + password (Admin) | 200, role == "Admin" | 200, role == "Admin" | Success |
| POST /auth/login | credentials for a Pending account | 403 Forbidden | 403 Forbidden | Success |
| POST /auth/login | credentials for a Blocked account | 403 Forbidden | 403 Forbidden | Success |
| POST /auth/login | valid login updates last_login_at | last_login_at is set | last_login_at is set | Success |
| POST /auth/register | empty body | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student password < 6 chars | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student password != confirm_password | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student missing school | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student missing subject_ids | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | invalid student email format | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | invalid parent email format | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student email already exists | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | new parent email but missing parent name/password | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | new parent passwords do not match | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | legacy flat body with role outside [Tutor] | 400 Bad Request | 400 Bad Request | Success |
| POST /auth/register | student + existing parent email | 201, Student linked to existing parent_id, no duplicate Parent row | 201, Student linked to existing parent_id, no duplicate Parent row | Success |
| POST /auth/register | student + new parent email | 201, new Parent row created, Student.parent_id == new parent's id | 201, new Parent row created, Student.parent_id == new parent's id | Success |
| POST /auth/register | legacy flat valid Tutor payload | 201, Tutor row created (status Pending) | 201, Tutor row created (status Pending) | Success |
| POST /auth/register | already logged in (existing session) | 200, redirect_url for current role, no new row | 200, redirect_url for current role, no new row | Success |
| GET /auth/check-parent-email | existing parent email | 200, exists=true, parent info returned | 200, exists=true, parent info returned | Success |
| GET /auth/check-parent-email | unknown parent email | 200, exists=false | 200, exists=false | Success |
| GET /auth/check-parent-email | invalid/missing email | 400 Bad Request | 400 Bad Request | Success |
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
    resp = client.post('/auth/login', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_login_unknown_identifier(client, seed_roles):
    resp = client.post('/auth/login', json={'identifier': 'nobody@nowhere.com', 'password': 'whatever'})
    assert resp.status_code == 401
    assert resp.get_json()['success'] is False


def test_login_wrong_password(client, seed_students):
    resp = client.post('/auth/login', json={'identifier': 'aarav.mehta@learnmail.com', 'password': 'WrongPass'})
    assert resp.status_code == 401
    assert resp.get_json()['success'] is False


def test_login_success_student(client, seed_students):
    resp = client.post('/auth/login', json={'identifier': 'aarav.mehta@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['role'] == 'Student'
    assert data['username'] == 'Aarav Mehta'
    assert data['redirect_url'] == '/student'
    assert 'token' in data and data['token']


def test_login_success_admin_by_username(client, seed_admin):
    resp = client.post('/auth/login', json={'identifier': 'admin', 'password': 'admin123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['role'] == 'Admin'
    assert data['redirect_url'] == '/admin'


def test_login_pending_account_forbidden(client, seed_students):
    # s3 "Liam Johnson" is seeded with status='Pending'
    resp = client.post('/auth/login', json={'identifier': 'liam.johnson@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 403
    assert 'pending' in resp.get_json()['message'].lower()


def test_login_blocked_account_forbidden(client, seed_students):
    # s2 "Isha Kapoor" is seeded with status='Blocked'
    resp = client.post('/auth/login', json={'identifier': 'isha.kapoor@learnmail.com', 'password': 'Student@123'})
    assert resp.status_code == 403
    assert 'blocked' in resp.get_json()['message'].lower()


def test_login_updates_last_login_at(client, seed_students):
    student = seed_students[0]
    assert student.last_login_at is None

    resp = client.post('/auth/login', json={'identifier': student.email, 'password': 'Student@123'})
    assert resp.status_code == 200

    refreshed = _db.session.get(Student, student.student_id)
    assert refreshed.last_login_at is not None


# ----------------------------- /register (combined Student+Parent) -------

def _student_parent_payload(student_overrides=None, parent_overrides=None, subject_ids=None):
    student = {
        'name': 'New Student',
        'email': 'new.student@learnmail.com',
        'password': 'Passw0rd!',
        'confirm_password': 'Passw0rd!',
        'school': 'Greenfield High School',
        'subject_ids': subject_ids or [],
    }
    student.update(student_overrides or {})

    parent = {
        'email': 'new.parent@parentmail.com',
        'name': 'New Parent',
        'password': 'ParentPass1!',
        'confirm_password': 'ParentPass1!',
        'phone_no': '+1 200 555 2000',
    }
    parent.update(parent_overrides or {})

    return {'student': student, 'parent': parent}


def _tutor_payload(**overrides):
    payload = {
        'name': 'New Tutor',
        'email': 'new.tutor@learnmail.com',
        'password': 'Passw0rd!',
        'confirm_password': 'Passw0rd!',
        'role': 'Tutor',
    }
    payload.update(overrides)
    return payload


def test_register_empty_body(client, seed_roles):
    resp = client.post('/auth/register', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_register_student_password_too_short(client, seed_roles):
    payload = _student_parent_payload(student_overrides={'password': 'abc', 'confirm_password': 'abc'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_student_password_mismatch(client, seed_roles):
    payload = _student_parent_payload(student_overrides={'confirm_password': 'Different1!'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_student_missing_school(client, seed_roles, seed_subjects):
    payload = _student_parent_payload(
        student_overrides={'school': ''},
        subject_ids=[seed_subjects['Mathematics'].subject_id],
    )
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400
    assert 'school' in resp.get_json()['message'].lower()


def test_register_student_missing_subjects(client, seed_roles):
    # subject_ids defaults to [] in _student_parent_payload when not given.
    payload = _student_parent_payload()
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400
    assert 'subject' in resp.get_json()['message'].lower()


def test_register_invalid_student_email(client, seed_roles):
    payload = _student_parent_payload(student_overrides={'email': 'not-an-email'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_invalid_parent_email(client, seed_roles):
    payload = _student_parent_payload(parent_overrides={'email': 'not-an-email'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_student_duplicate_email(client, seed_roles, seed_students):
    payload = _student_parent_payload(student_overrides={'email': 'aarav.mehta@learnmail.com'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400
    assert 'already exists' in resp.get_json()['message'].lower()


def test_register_new_parent_missing_details(client, seed_roles):
    # Parent email is new, but no name/password supplied for it.
    payload = _student_parent_payload(parent_overrides={
        'email': 'brand.new.parent@parentmail.com',
        'name': '',
        'password': '',
        'confirm_password': '',
    })
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_new_parent_password_mismatch(client, seed_roles):
    payload = _student_parent_payload(parent_overrides={
        'email': 'brand.new.parent2@parentmail.com',
        'confirm_password': 'SomethingElse1!',
    })
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 400


def test_register_legacy_flat_role_not_tutor_rejected(client, seed_roles):
    # The old flat Student/Parent registration path has been removed;
    # only Tutor sign-up may use the flat shape.
    resp = client.post('/auth/register', json=_tutor_payload(role='Student'))
    assert resp.status_code == 400


def test_register_student_with_existing_parent(client, seed_roles, seed_parent, seed_subjects):
    before_parent_count = Parent.query.count()

    payload = _student_parent_payload(
        student_overrides={'email': 'linked.student@learnmail.com'},
        parent_overrides={'email': seed_parent.email},  # only email needed - parent already exists
        subject_ids=[seed_subjects['Mathematics'].subject_id],
    )
    # Strip the "new parent" fields to mimic what the frontend sends once
    # the email lookup confirms the parent already exists.
    payload['parent'] = {'email': seed_parent.email}

    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    assert data['parent']['parent_id'] == seed_parent.parent_id
    assert data['parent']['newly_created'] is False

    created_student = Student.query.filter_by(email='linked.student@learnmail.com').first()
    assert created_student is not None
    assert created_student.parent_id == seed_parent.parent_id
    assert created_student.password_hash != 'Passw0rd!'  # must be hashed

    # No duplicate Parent row should have been created.
    assert Parent.query.count() == before_parent_count


def test_register_student_with_new_parent(client, seed_roles, seed_subjects):
    before_parent_count = Parent.query.count()

    payload = _student_parent_payload(
        student_overrides={'email': 'newparent.student@learnmail.com'},
        parent_overrides={'email': 'freshly.created.parent@parentmail.com'},
        subject_ids=[seed_subjects['Science'].subject_id],
    )

    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    assert data['parent']['newly_created'] is True

    created_parent = Parent.query.filter_by(email='freshly.created.parent@parentmail.com').first()
    assert created_parent is not None
    assert created_parent.parent_name == 'New Parent'
    assert created_parent.password_hash != 'ParentPass1!'  # must be hashed
    assert Parent.query.count() == before_parent_count + 1

    created_student = Student.query.filter_by(email='newparent.student@learnmail.com').first()
    assert created_student is not None
    assert created_student.parent_id == created_parent.parent_id


def test_register_tutor_legacy_flat_success(client, seed_roles):
    resp = client.post('/auth/register', json=_tutor_payload())
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True

    created = Tutor.query.filter_by(email='new.tutor@learnmail.com').first()
    assert created is not None
    assert created.tutor_name == 'New Tutor'
    assert created.status == 'Pending'
    assert created.password_hash != 'Passw0rd!'  # must be hashed


def test_register_already_logged_in_short_circuits(client, seed_students):
    student = seed_students[0]
    login_resp = client.post('/auth/login', json={'identifier': student.email, 'password': 'Student@123'})
    assert login_resp.status_code == 200

    before_count = Student.query.count()
    payload = _student_parent_payload(student_overrides={'email': 'should.not.be.created@learnmail.com'})
    resp = client.post('/auth/register', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['redirect_url'] == '/student'

    # no new row should have been created since registration short-circuited
    assert Student.query.count() == before_count


# ----------------------------- /check-parent-email -------------------------

def test_check_parent_email_found(client, seed_roles, seed_parent):
    resp = client.get('/auth/check-parent-email', query_string={'email': seed_parent.email})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['exists'] is True
    assert data['parent']['parent_id'] == seed_parent.parent_id
    assert data['parent']['parent_name'] == seed_parent.parent_name


def test_check_parent_email_not_found(client, seed_roles):
    resp = client.get('/auth/check-parent-email', query_string={'email': 'nobody.here@parentmail.com'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['exists'] is False


def test_check_parent_email_invalid(client, seed_roles):
    resp = client.get('/auth/check-parent-email', query_string={'email': 'not-an-email'})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_check_parent_email_missing(client, seed_roles):
    resp = client.get('/auth/check-parent-email')
    assert resp.status_code == 400




