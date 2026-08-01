"""
Test cases confirming every /admin/* Admin Dashboard route is actually
protected by @admin_required, now that real login/session auth exists.

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /admin/dashboard/stats | no session | 401 Unauthorized | 401 Unauthorized | Success |
| GET /admin/students | no session | 401 Unauthorized | 401 Unauthorized | Success |
| GET /admin/approvals | no session | 401 Unauthorized | 401 Unauthorized | Success |
| GET /admin/profile/me | no session | 401 Unauthorized | 401 Unauthorized | Success |
| GET /admin/dashboard/stats | logged in as Student | 403 Forbidden | 403 Forbidden | Success |
"""
from werkzeug.security import generate_password_hash

from database import db as _db
from models import Student


def test_unauthenticated_dashboard_stats(client):
    resp = client.get('/admin/dashboard/stats')
    assert resp.status_code == 401
    assert resp.get_json()['success'] is False


def test_unauthenticated_students_list(client):
    resp = client.get('/admin/students')
    assert resp.status_code == 401


def test_unauthenticated_approvals_list(client):
    resp = client.get('/admin/approvals')
    assert resp.status_code == 401


def test_unauthenticated_profile(client):
    resp = client.get('/admin/profile/me')
    assert resp.status_code == 401


def test_non_admin_role_forbidden(client, seed_roles):
    # A logged-in Student trying to hit an admin-only route should get a
    # 403, not a 401 (they ARE authenticated, just not authorized).
    student = Student(
        role_id=seed_roles['Student'].role_id,
        student_name='Regular Student',
        email='regular.student@learnmail.com',
        password_hash=generate_password_hash('Student@123'),
        status='Active',
    )
    _db.session.add(student)
    _db.session.commit()

    login_resp = client.post('/login', json={'identifier': student.email, 'password': 'Student@123'})
    assert login_resp.status_code == 200

    resp = client.get('/admin/dashboard/stats')
    assert resp.status_code == 403
