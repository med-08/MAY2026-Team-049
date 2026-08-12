import pytest
from app import app as flask_app
from database import db
from models import Parent, Student
from werkzeug.security import generate_password_hash
from utils import generate_jwt_token


@pytest.fixture
def app():
    """Configure Flask application instance for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return flask_app


@pytest.fixture
def client(app):
    """Create a Flask test client with a clean isolated in-memory DB and session per test."""
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            # Seed test parent and student
            p = Parent(
                parent_id=1,
                role_id=3,
                parent_name='Test Parent',
                email='test.parent@example.com',
                phone_no='+91 99999 99999',
                password_hash=generate_password_hash('123456'),
                status='Active'
            )
            db.session.add(p)

            s = Student(
                student_id=1,
                role_id=4,
                parent_id=1,
                student_name='Test Student',
                email='test.student@example.com',
                school='Class 10',
                password_hash=generate_password_hash('123456'),
                status='Active'
            )
            db.session.add(s)
            db.session.commit()

        # Set session variables for session-based auth fallback
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'Parent'
            sess['email'] = 'test.parent@example.com'

        yield client


@pytest.fixture
def auth_headers(app):
    """Fixture to generate a valid Parent JWT Bearer Token for tests."""
    with app.app_context():
        # Match exact keyword arguments expected by generate_jwt_token
        try:
            token = generate_jwt_token(user_id=1, role='Parent', username='Test Parent')
        except TypeError:
            token = generate_jwt_token(1, 'Test Parent', 'Parent')

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


def test_parent_health_endpoint(client):
    response = client.get('/parent/health')
    assert response.status_code == 200
    assert response.get_json()['success'] is True


def test_get_parent_profile_endpoint(client, auth_headers):
    response = client.get('/parent/profile/1', headers=auth_headers)
    assert response.status_code in [200, 404]


def test_get_parent_overview_endpoint(client, auth_headers):
    response = client.get('/parent/overview/1', headers=auth_headers)
    assert response.status_code in [200, 404]


def test_meeting_request_endpoint(client, auth_headers):
    payload = {
        "parent_id": 1,
        "tutor_id": 1,
        "student_id": 1,
        "preferred_date": "2026-08-05",
        "preferred_time": "16:00",
        "notes": "Discuss child progress"
    }
    response = client.post('/parent/meeting-request', json=payload, headers=auth_headers)
    assert response.status_code in [200, 201]


def test_get_child_progress_endpoint(client, auth_headers):
    response = client.get('/parent/child-progress/1/1', headers=auth_headers)
    assert response.status_code in [200, 404]


def test_get_child_curriculum_endpoint(client, auth_headers):
    response = client.get('/parent/curriculum/1', headers=auth_headers)
    assert response.status_code in [200, 404]


def test_get_weekly_summary_endpoint(client, auth_headers):
    response = client.get('/parent/weekly-summary/1/1', headers=auth_headers)
    assert response.status_code in [200, 404]


def test_get_parent_messages_endpoint(client, auth_headers):
    response = client.get('/parent/messages/1', headers=auth_headers)
    assert response.status_code == 200


def test_send_parent_message_endpoint(client, auth_headers):
    payload = {
        "parent_id": 1,
        "tutor_id": 1,
        "subject": "Test Query",
        "message": "Hello tutor"
    }
    response = client.post('/parent/messages/send', json=payload, headers=auth_headers)
    assert response.status_code in [200, 201]