from datetime import date, time

import pytest
from app import app
from database import db
from models import Role, Student, Tutor, Subject, Session

@pytest.fixture
def client():
    """Create a Flask test client for API testing with an active Student session."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            student_role = Role(role_name='Student')
            tutor_role = Role(role_name='Tutor')
            db.session.add_all([student_role, tutor_role])
            db.session.commit()

            tutor = Tutor(
                role_id=tutor_role.role_id,
                tutor_name='Test Tutor',
                email='tutor@example.com',
                experience_years=5,
                password_hash='hashed-password',
                status='Active'
            )
            subject = Subject(subject_name='Mathematics')
            db.session.add_all([tutor, subject])
            db.session.commit()

            session = Session(
                tutor_id=tutor.tutor_id,
                subject_id=subject.subject_id,
                session_date=date.today(),
                start_time=time(16, 0),
                end_time=time(17, 0),
                session_type='Regular',
                status='Scheduled'
            )
            db.session.add(session)
            db.session.commit()

            student = Student(
                role_id=student_role.role_id,
                student_name='Test Student',
                email='student@example.com',
                school='Class 10',
                password_hash='hashed-password',
                status='Active'
            )
            db.session.add(student)
            db.session.commit()
            student_id = student.student_id

        with client.session_transaction() as sess:
            sess['user_id'] = student_id
            sess['role'] = 'Student'
            sess['username'] = 'Test Student'

        yield client


def test_student_dashboard_endpoint(client):
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'summaryStats' in data
    assert 'weeklyQuizProgress' in data
    assert 'subjectQuizScores' in data
    assert 'nextSession' in data
    assert 'todaysTasks' in data


def test_student_progress_endpoint(client):
    response = client.get('/student/progress')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'completedTopics' in data
    assert 'growthMetrics' in data


def test_student_faqs_endpoint(client):
    response = client.get('/student/faqs')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data.get('faqs', [])) >= 2

    search_res = client.get('/student/faqs?q=quiz')
    assert search_res.status_code == 200
    search_data = search_res.get_json()
    assert search_data['success'] is True


def test_student_weekly_quizzes_endpoint(client):
    response = client.get('/student/quizzes')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data.get('quizzes', [])) >= 3


def test_student_quiz_details_endpoint(client):
    response = client.get('/student/quizzes/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data.get('questions', [])) >= 5


def test_student_quiz_submission_endpoint(client):
    payload = {"answers": {"1": "B", "2": "B", "3": "B", "4": "C", "5": "A"}}
    response = client.post('/student/quizzes/1/submit', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'score' in data
    assert 'correctCount' in data


def test_student_booking_slots_endpoint(client):
    response = client.get('/student/booking-slots')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    slots = data.get('bookingSlots', {})
    assert 'regular' in slots
    assert 'oneToOne' in slots


def test_student_book_session_endpoint(client):
    payload = {"session_id": 1}
    response = client.post('/student/book-session', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_student_book_session_requires_valid_session_id(client):
    response = client.post('/student/book-session', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is False
    assert 'session_id' in data['message']


def test_student_upcoming_sessions_endpoint(client):
    response = client.get('/student/upcoming-sessions')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'upcoming_sessions' in data


def test_student_study_tips_endpoint(client):
    response = client.get('/student/study-tips')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'studyTips' in data
    assert len(data.get('studyTips', [])) >= 3


def test_student_assignments_endpoint(client):
    response = client.get('/student/assignments')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'assignments' in data
    assert len(data.get('assignments', [])) >= 4

    update_res = client.post('/student/assignments/1/update-progress', json={"progress": 75})
    assert update_res.status_code == 200
    update_data = update_res.get_json()
    assert update_data['success'] is True
    assert update_data['progress'] == 75


def test_student_book_session_should_succeed_with_missing_session(client):
    response = client.post('/student/book-session', json={"session_id": 999})
    assert response.status_code == 200  
