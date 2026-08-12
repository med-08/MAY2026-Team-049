"""
Test cases for the Tutor QA add/delete and Ask Doubt notification flow.

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| POST /tutor/qa | valid question/answer | 201, entry published | 201, entry published | Success |
| DELETE /tutor/qa/<id> | existing faq id | 200, deleted | 200, deleted | Success |
| DELETE /tutor/qa/<id> | missing faq id | 404 Not Found | 404 Not Found | Success |
| POST /student/doubts -> GET /tutor/doubts | doubt asked by student | tutor sees the doubt | tutor sees the doubt | Success |
| POST /tutor/doubts/<id>/reply | valid reply | 200, student notified | 200, student notified | Success |
"""

from datetime import datetime

import pytest
from app import app
from database import db
from models import Parent, Role, Student, Tutor, Subject


@pytest.fixture
def ctx():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            tutor_role = Role(role_name='Tutor')
            student_role = Role(role_name='Student')
            parent_role = Role(role_name='Parent')
            db.session.add_all([tutor_role, student_role, parent_role])
            db.session.commit()

            tutor = Tutor(
                role_id=tutor_role.role_id,
                tutor_name='Test Tutor',
                email='tutor2@example.com',
                password_hash='hashed',
                status='Active',
            )
            parent = Parent(
                role_id=parent_role.role_id,
                parent_name='Test Parent',
                email='parent2@example.com',
                password_hash='hashed',
                status='Active',
            )
            subject = Subject(subject_name='Physics')
            db.session.add_all([tutor, parent, subject])
            db.session.commit()

            student = Student(
                role_id=student_role.role_id,
                parent_id=parent.parent_id,
                student_name='Test Student',
                email='student2@example.com',
                password_hash='hashed',
                status='Active',
            )
            db.session.add(student)
            db.session.commit()

            ids = {'tutor_id': tutor.tutor_id, 'student_id': student.student_id}

        yield client, ids


def as_tutor(client, tutor_id):
    with client.session_transaction() as sess:
        sess['user_id'] = tutor_id
        sess['role'] = 'Tutor'
        sess['username'] = 'Test Tutor'


def as_student(client, student_id):
    with client.session_transaction() as sess:
        sess['user_id'] = student_id
        sess['role'] = 'Student'
        sess['username'] = 'Test Student'


def test_publish_and_delete_qa_entry(ctx):
    client, ids = ctx
    as_tutor(client, ids['tutor_id'])

    create_res = client.post('/tutor/qa', json={
        "question": "How do I join the session?",
        "answer": "Use the Join Meeting button on My Sessions.",
    })
    assert create_res.status_code == 201
    # Tutor blueprint's ok() merges data at the top level (not nested under
    # "data" like the student blueprint) - this is an intentional, consistent
    # convention across all /tutor/* routes, so we assert against that shape.
    faq_id = create_res.get_json()["entry"]["faqId"]

    delete_res = client.delete(f'/tutor/qa/{faq_id}')
    assert delete_res.status_code == 200
    assert delete_res.get_json()["success"] is True

    listing = client.get('/tutor/qa').get_json()["entries"]
    assert all(entry["faqId"] != faq_id for entry in listing)


def test_delete_qa_entry_not_found(ctx):
    client, ids = ctx
    as_tutor(client, ids['tutor_id'])
    response = client.delete('/tutor/qa/999999')
    assert response.status_code == 404


def test_student_doubt_visible_to_tutor_and_reply_notifies_student(ctx):
    client, ids = ctx

    as_student(client, ids['student_id'])
    ask_res = client.post('/student/doubts', json={
        "question": "What is Newton's second law?",
        "subject": "Physics",
        "tutor_id": ids['tutor_id'],
    })
    assert ask_res.status_code == 201
    doubt_id = ask_res.get_json()["data"]["doubt"]["doubtId"]

    as_tutor(client, ids['tutor_id'])
    tutor_doubts = client.get('/tutor/doubts').get_json()["doubts"]
    assert any(d["doubtId"] == doubt_id for d in tutor_doubts)

    reply_res = client.post(f'/tutor/doubts/{doubt_id}/reply', json={"reply": "F = ma"})
    assert reply_res.status_code == 200

    as_student(client, ids['student_id'])
    doubts_after = client.get('/student/doubts').get_json()["data"]["doubts"]
    answered = next(d for d in doubts_after if d["doubtId"] == doubt_id)
    assert answered["status"] == "Answered"
    assert answered["answer"] == "F = ma"

    notifications = client.get('/student/notifications').get_json()["data"]["notifications"]
    assert any(n["type"] == "Doubt" for n in notifications)
