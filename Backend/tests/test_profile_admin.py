"""
Test cases for /admin/profile/me*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /profile/me | logged in as seeded admin | 200, correct name/email/role | 200, correct name/email/role | Success |
| PUT /profile/me | {"admin_name": "New Name"} | 200, admin_name updated | 200, admin_name updated | Success |
| PUT /profile/me | {"email": "not-an-email"} | 400 Bad Request | 400 Bad Request | Success |
| PUT /profile/me | {} (empty body) | 400 Bad Request | 400 Bad Request | Success |
| PUT /profile/me | {"email": <email of another existing admin>} | 409 Conflict | 409 Conflict | Success |
| PUT /profile/me/password | correct current_password, valid new password, matching confirm | 200, password changed | 200, password changed | Success |
| PUT /profile/me/password | wrong current_password | 401 Unauthorized | 401 Unauthorized | Success |
| PUT /profile/me/password | new_password/confirm_password mismatch | 400 Bad Request | 400 Bad Request | Success |
| PUT /profile/me/password | new_password too short (<6 chars) | 400 Bad Request | 400 Bad Request | Success |
"""
from werkzeug.security import check_password_hash

from database import db as _db
from models import Admin


def test_get_profile(admin_client, seed_admin):
    resp = admin_client.get('/admin/profile/me')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["admin_name"] == "Admin User"
    assert data["email"] == "admin@learnathome.com"
    assert data["role"] == "Admin"


def test_update_profile_name(admin_client, seed_admin):
    resp = admin_client.put('/admin/profile/me', json={"admin_name": "New Admin Name"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["admin_name"] == "New Admin Name"


def test_update_profile_invalid_email(admin_client, seed_admin):
    resp = admin_client.put('/admin/profile/me', json={"email": "not-an-email"})
    assert resp.status_code == 400


def test_update_profile_empty_body(admin_client, seed_admin):
    resp = admin_client.put('/admin/profile/me', json={})
    assert resp.status_code == 400


def test_update_profile_duplicate_email(admin_client, seed_admin, seed_roles):
    other_admin = Admin(
        role_id=seed_roles['Admin'].role_id,
        username='admin2',
        password_hash='x',
        admin_name='Other Admin',
        email='other@learnathome.com',
    )
    _db.session.add(other_admin)
    _db.session.commit()

    resp = admin_client.put('/admin/profile/me', json={"email": "other@learnathome.com"})
    assert resp.status_code == 409


def test_change_password_success(admin_client, seed_admin):
    resp = admin_client.put(
        '/admin/profile/me/password',
        json={
            "current_password": "admin123",
            "new_password": "NewPass@456",
            "confirm_password": "NewPass@456",
        },
    )
    assert resp.status_code == 200
    assert check_password_hash(seed_admin.password_hash, "NewPass@456")


def test_change_password_wrong_current(admin_client, seed_admin):
    resp = admin_client.put(
        '/admin/profile/me/password',
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPass@456",
            "confirm_password": "NewPass@456",
        },
    )
    assert resp.status_code == 401


def test_change_password_mismatch(admin_client, seed_admin):
    resp = admin_client.put(
        '/admin/profile/me/password',
        json={
            "current_password": "admin123",
            "new_password": "NewPass@456",
            "confirm_password": "Different@789",
        },
    )
    assert resp.status_code == 400


def test_change_password_too_short(admin_client, seed_admin):
    resp = admin_client.put(
        '/admin/profile/me/password',
        json={
            "current_password": "admin123",
            "new_password": "abc",
            "confirm_password": "abc",
        },
    )
    assert resp.status_code == 400
