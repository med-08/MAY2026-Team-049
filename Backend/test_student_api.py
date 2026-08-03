"""
Test cases for /student/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /student/dashboard | logged-in student | 200, dashboard payload with summaryStats | 200, dashboard payload with summaryStats | Success |
| GET /student/progress | logged-in student | 200, growthMetrics and completedTopics | 200, growthMetrics and completedTopics | Success |
| GET /student/faqs | no params | 200, faq list | 200, faq list | Success |
| GET /student/quizzes | logged-in student | 200, quiz list | 200, quiz list | Success |
| GET /student/quizzes/<id> | valid quiz id | 200, 5 question payload | 200, 5 question payload | Success |
| POST /student/quizzes/<id>/submit | valid answers | 200, scoring data | 200, scoring data | Success |
| GET /student/booking-slots | logged-in student | 200, regular and one-to-one slots | 200, regular and one-to-one slots | Success |
| POST /student/book-session | valid session_id | 200, booking success | 200, booking success | Success |
| POST /student/book-session | invalid/missing session_id | 400 Bad Request | 400 Bad Request | Success |
| GET /student/upcoming-sessions | logged-in student | 200, upcoming sessions list | 200, upcoming sessions list | Success |
| GET /student/study-tips | logged-in student | 200, study tips list | 200, study tips list | Success |
| GET /student/assignments | logged-in student | 200, assignments list | 200, assignments list | Success |
| POST /student/assignments/<id>/update-progress | valid progress payload | 200, progress updated | 200, progress updated | Success |
"""

from datetime import date, datetime, time, timedelta

import pytest
from app import app
from database import db
from models import (
    Assignment,
    AssignmentSubmission,
    FAQ,
    Parent,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    Role,
    Session,
    SessionBooking,
    SessionUpdate,
    StudyResource,
    StudyTip,
    Student,
    StudentSubject,
    Subject,
    Tutor,
)

@pytest.fixture
def client():
    """Create a Flask test client for API testing with an active Student session."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            parent_role = Role(role_name='Parent')
            student_role = Role(role_name='Student')
            tutor_role = Role(role_name='Tutor')
            db.session.add_all([parent_role, student_role, tutor_role])
            db.session.commit()

            parent = Parent(
                role_id=parent_role.role_id,
                parent_name='Test Parent',
                email='parent@example.com',
                phone_no='1234567890',
                password_hash='hashed-parent',
                status='Active',
                registered_at=datetime.utcnow(),
            )

            tutor = Tutor(
                role_id=tutor_role.role_id,
                tutor_name='Test Tutor',
                email='tutor@example.com',
                experience_years=5,
                password_hash='hashed-password',
                status='Active'
            )
            subject = Subject(subject_name='Mathematics')
            science = Subject(subject_name='Science')
            english = Subject(subject_name='English')
            db.session.add_all([parent, tutor, subject, science, english])
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
                parent_id=parent.parent_id,
                student_name='Test Student',
                email='student@example.com',
                school='Class 10',
                password_hash='hashed-password',
                status='Active'
            )
            db.session.add(student)
            db.session.commit()
            student_id = student.student_id

            db.session.add_all([
                StudentSubject(student_id=student_id, subject_id=subject.subject_id),
                StudentSubject(student_id=student_id, subject_id=science.subject_id),
                StudentSubject(student_id=student_id, subject_id=english.subject_id),
                SessionUpdate(
                    session_id=session.session_id,
                    topics_covered='Algebra, Geometry, Fractions',
                    homework_assigned='Complete worksheet',
                    next_session_date=date.today() + timedelta(days=7),
                ),
                SessionBooking(
                    session_id=session.session_id,
                    student_id=student_id,
                    booking_status='Confirmed',
                ),
                FAQ(
                    question='How do I book a tuition session?',
                    answer='Choose a slot and tap Book Slot',
                    category='Booking',
                ),
                FAQ(
                    question='How do I reschedule a booked session?',
                    answer='Open your booked slot and tap Reschedule',
                    category='Booking',
                ),
                Quiz(
                    tutor_id=tutor.tutor_id,
                    subject_id=subject.subject_id,
                    title='Algebra Review',
                    week_number=1,
                ),
                Quiz(
                    tutor_id=tutor.tutor_id,
                    subject_id=science.subject_id,
                    title='Science Review',
                    week_number=2,
                ),
                Quiz(
                    tutor_id=tutor.tutor_id,
                    subject_id=english.subject_id,
                    title='English Review',
                    week_number=3,
                ),
                StudyTip(
                    session_id=session.session_id,
                    student_id=student_id,
                    tip_text='Use a revision checklist before the next session.',
                    created_at=datetime.utcnow(),
                ),
                StudyTip(
                    session_id=session.session_id,
                    student_id=student_id,
                    tip_text='Summarize each topic in one line after class.',
                    created_at=datetime.utcnow(),
                ),
                StudyTip(
                    session_id=session.session_id,
                    student_id=student_id,
                    tip_text='Solve 5 extra practice questions every evening.',
                    created_at=datetime.utcnow(),
                ),
                StudyResource(
                    session_id=session.session_id,
                    resource_title='Algebra Basics Notes',
                    resource_type='PDF',
                    resource_link='#',
                ),
                StudyResource(
                    session_id=session.session_id,
                    resource_title='Geometry Practice Sheet',
                    resource_type='Practice Sheet',
                    resource_link='#',
                ),
            ])
            db.session.commit()

            quizzes = Quiz.query.order_by(Quiz.quiz_id).all()
            for quiz in quizzes:
                db.session.add_all([
                    QuizQuestion(quiz_id=quiz.quiz_id, question='Solve 2x + 3 = 9', option_a='x=2', option_b='x=3', option_c='x=4', option_d='x=5', correct_option='B'),
                    QuizQuestion(quiz_id=quiz.quiz_id, question='Which is a prime number?', option_a='8', option_b='9', option_c='11', option_d='15', correct_option='C'),
                    QuizQuestion(quiz_id=quiz.quiz_id, question='Which sentence is correct?', option_a='He go to school.', option_b='He goes to school.', option_c='He going to school.', option_d='He gone to school.', correct_option='B'),
                    QuizQuestion(quiz_id=quiz.quiz_id, question='What is 3 + 4?', option_a='5', option_b='6', option_c='7', option_d='8', correct_option='C'),
                    QuizQuestion(quiz_id=quiz.quiz_id, question='Choose the correct option.', option_a='A', option_b='B', option_c='C', option_d='D', correct_option='A'),
                ])
            db.session.commit()

            assignments = []
            for i in range(4):
                assignment = Assignment(
                    session_id=session.session_id,
                    title=f'Assignment {i + 1}',
                    description='Practice task from class',
                    due_date=date.today() + timedelta(days=i + 1),
                )
                assignments.append(assignment)
            db.session.add_all(assignments)
            db.session.commit()

            for idx, assignment in enumerate(assignments, start=1):
                db.session.add(AssignmentSubmission(
                    assignment_id=assignment.assignment_id,
                    student_id=student_id,
                    status='In Progress' if idx % 2 else 'Completed',
                    progress_percentage=25 * idx,
                ))
            db.session.commit()

        with client.session_transaction() as sess:
            sess['user_id'] = student_id
            sess['role'] = 'Student'
            sess['username'] = 'Test Student'

        yield client


def test_get_student_dashboard(client):
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["summaryStats"]
    assert data["weeklyQuizProgress"]
    assert data["subjectQuizScores"]
    assert data["nextSession"]
    assert data["todaysTasks"]
    assert body["meta"]["total"] == len(data["todaysTasks"])


def test_get_student_progress(client):
    response = client.get('/student/progress')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["growthMetrics"]
    assert data["completedTopics"]
    assert body["meta"]["total"] == len(data["completedTopics"])


def test_get_student_faqs(client):
    response = client.get('/student/faqs')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert len(data.get("faqs", [])) >= 2
    assert body["meta"]["total"] == len(data.get("faqs", []))

    search_res = client.get('/student/faqs?q=quiz')
    assert search_res.status_code == 200
    search_body = search_res.get_json()
    assert search_body["success"] is True


def test_get_student_quizzes(client):
    response = client.get('/student/quizzes')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert len(data.get("quizzes", [])) >= 3
    assert body["meta"]["total"] == len(data.get("quizzes", []))


def test_get_student_quiz_details(client):
    response = client.get('/student/quizzes/1')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert len(data.get("questions", [])) >= 5
    assert body["meta"]["total"] == len(data.get("questions", []))


def test_submit_student_quiz(client):
    payload = {"answers": {"1": "B", "2": "B", "3": "B", "4": "C", "5": "A"}}
    response = client.post('/student/quizzes/1/submit', json=payload)
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert "score" in data
    assert "correctCount" in data
    assert body["meta"]["total"] == data["totalQuestions"]


def test_get_student_booking_slots(client):
    response = client.get('/student/booking-slots')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    slots = data.get("bookingSlots", {})
    assert "regular" in slots
    assert "oneToOne" in slots
    assert body["meta"]["total"] == len(slots.get("regular", [])) + len(slots.get("oneToOne", []))


def test_book_student_session(client):
    payload = {"session_id": 1}
    response = client.post('/student/book-session', json=payload)
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["booked_session_id"] == 1


def test_book_student_session_requires_valid_session_id(client):
    response = client.post('/student/book-session', json={})
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "session_id" in body["message"]


def test_get_student_upcoming_sessions(client):
    response = client.get('/student/upcoming-sessions')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["upcoming_sessions"]
    assert body["meta"]["total"] == len(data.get("upcoming_sessions", []))


def test_get_student_study_tips(client):
    response = client.get('/student/study-tips')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["studyTips"]
    assert len(data.get("studyTips", [])) >= 3
    assert body["meta"]["total"] == len(data.get("studyTips", []))


def test_get_student_assignments(client):
    response = client.get('/student/assignments')
    assert response.status_code == 200
    body = response.get_json()
    data = body["data"]
    assert body["success"] is True
    assert data["assignments"]
    assert len(data.get("assignments", [])) >= 4
    assert body["meta"]["total"] == len(data.get("assignments", []))

    update_res = client.post('/student/assignments/1/update-progress', json={"progress": 75})
    assert update_res.status_code == 200
    update_body = update_res.get_json()
    update_data = update_body["data"]
    assert update_body["success"] is True
    assert update_data["progress"] == 75
    assert update_body["meta"]["total"] == 1

