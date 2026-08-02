import pytest
from app import app
from database import db

@pytest.fixture
def client():
    """Create a Flask test client for API testing with active Parent session."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'Parent'
            sess['username'] = 'Test Parent'

        yield client

def test_parent_health_endpoint(client):
    response = client.get('/parent/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'

def test_get_parent_profile_endpoint(client):
    response = client.get('/parent/profile/1')
    assert response.status_code in [200, 404]

def test_get_parent_overview_endpoint(client):
    response = client.get('/parent/overview/1')
    assert response.status_code in [200, 404]

def test_meeting_request_endpoint(client):
    payload = {
        "parent_id": 1,
        "tutor_id": 1,
        "student_id": 1,
        "preferred_date": "2026-08-05",
        "preferred_time": "16:00"
    }
    response = client.post('/parent/meeting-request', json=payload)
    assert response.status_code == 201
    assert response.get_json()['status'] == 'success'

def test_get_child_progress_endpoint(client):
    response = client.get('/parent/child-progress/1/1')
    assert response.status_code in [200, 404]

def test_get_child_curriculum_endpoint(client):
    response = client.get('/parent/curriculum/1')
    assert response.status_code in [200, 404]