"""
Test cases for /admin/parents/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /parents | no params | 200, 1 parent, meta.total=1 | 200, 1 parent, meta.total=1 | Success |
| GET /parents | ?search=nonexistent | 200, 0 results | 200, 0 results | Success |
| GET /parents/<id> | valid id | 200, children list includes Aarav Mehta | 200, children list includes Aarav Mehta | Success |
| GET /parents/<id> | non-existent id | 404 Not Found | 404 Not Found | Success |
| PATCH /parents/<id>/status | {"status": "Blocked"} | 200, status now Blocked | 200, status now Blocked | Success |
| PATCH /parents/<id>/status | {"status": "Deleted"} (invalid value) | 400 Bad Request | 400 Bad Request | Success |
| DELETE /parents/<id> | valid id, has linked student | 200, parent removed, student's parent_id becomes null | 200, parent removed, student's parent_id becomes null | Success |
| DELETE /parents/<id> | non-existent id | 404 Not Found | 404 Not Found | Success |
"""


def test_list_parents(admin_client, seed_parent):
    resp = admin_client.get('/admin/parents')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["parent_name"] == "Rajesh Mehta"


def test_list_parents_search_no_match(admin_client, seed_parent):
    resp = admin_client.get('/admin/parents?search=nonexistent')
    assert resp.status_code == 200
    assert resp.get_json()["meta"]["total"] == 0


def test_get_parent_with_children(admin_client, seed_students):
    parent_id = seed_students[0].parent_id
    resp = admin_client.get(f'/admin/parents/{parent_id}')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    child_names = [c["student_name"] for c in data["children"]]
    assert "Aarav Mehta" in child_names


def test_get_parent_not_found(admin_client, seed_parent):
    resp = admin_client.get('/admin/parents/99999')
    assert resp.status_code == 404


def test_block_parent(admin_client, seed_parent):
    resp = admin_client.patch(f'/admin/parents/{seed_parent.parent_id}/status', json={"status": "Blocked"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["status"] == "Blocked"


def test_update_parent_status_invalid_value(admin_client, seed_parent):
    resp = admin_client.patch(f'/admin/parents/{seed_parent.parent_id}/status', json={"status": "Deleted"})
    assert resp.status_code == 400


def test_delete_parent_nulls_child_fk(admin_client, seed_students):
    parent_id = seed_students[0].parent_id
    student_id = seed_students[0].student_id

    resp = admin_client.delete(f'/admin/parents/{parent_id}')
    assert resp.status_code == 200

    student_resp = admin_client.get(f'/admin/students/{student_id}')
    assert student_resp.status_code == 200
    assert student_resp.get_json()["data"]["parent_id"] is None


def test_delete_parent_not_found(admin_client, seed_parent):
    resp = admin_client.delete('/admin/parents/99999')
    assert resp.status_code == 404


def test_block_pending_parent_is_rejected(admin_client, seed_roles):
    from models import Parent
    from database import db as _db
    from werkzeug.security import generate_password_hash

    pending_parent = Parent(
        role_id=seed_roles['Parent'].role_id,
        parent_name='Pending Parent',
        email='pending2.parent@parentmail.com',
        password_hash=generate_password_hash('Parent@123'),
        status='Pending',
    )
    _db.session.add(pending_parent)
    _db.session.commit()

    resp = admin_client.patch(f'/admin/parents/{pending_parent.parent_id}/status', json={"status": "Blocked"})
    assert resp.status_code == 409

    del_resp = admin_client.delete(f'/admin/parents/{pending_parent.parent_id}')
    assert del_resp.status_code == 409
