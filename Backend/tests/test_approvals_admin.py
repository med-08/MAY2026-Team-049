"""
Test cases for /admin/approvals/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /approvals | default (status=Pending) | 200, 2 entries (Liam Johnson, Nathan Cole) | 200, 2 entries (Liam Johnson, Nathan Cole) | Success |
| GET /approvals | ?status=All | 200, 6 entries (3 students + 2 tutors + 1 parent) | 200, 6 entries (3 students + 2 tutors + 1 parent) | Success |
| GET /approvals | ?status=Invalid | 400 Bad Request | 400 Bad Request | Success |
| PATCH /approvals/student/<id>/approve | valid pending student id | 200, status becomes Active | 200, status becomes Active | Success |
| PATCH /approvals/student/<id>/approve | already-Active student | 409 Conflict | 409 Conflict | Success |
| PATCH /approvals/tutor/<id>/reject | valid pending tutor id | 200, tutor deleted from DB (no longer in /tutors) | 200, tutor deleted from DB | Success |
| PATCH /approvals/bogus/<id>/approve | invalid entity_type | 400 Bad Request | 400 Bad Request | Success |
| PATCH /approvals/student/<id>/approve | non-existent id | 404 Not Found | 404 Not Found | Success |
"""


def test_list_pending_approvals_default(admin_client, seed_students, seed_tutors):
    resp = admin_client.get('/admin/approvals')
    assert resp.status_code == 200
    body = resp.get_json()
    names = {row["name"] for row in body["data"]}
    assert names == {"Liam Johnson", "Nathan Cole"}
    assert body["meta"]["total"] == 2


def test_list_all_approvals(admin_client, seed_students, seed_tutors):
    resp = admin_client.get('/admin/approvals?status=All')
    assert resp.status_code == 200
    assert resp.get_json()["meta"]["total"] == 6


def test_list_approvals_invalid_status(admin_client, seed_students):
    resp = admin_client.get('/admin/approvals?status=Invalid')
    assert resp.status_code == 400


def test_approve_pending_student(admin_client, seed_students):
    pending_student = next(s for s in seed_students if s.status == 'Pending')
    resp = admin_client.patch(f'/admin/approvals/student/{pending_student.student_id}/approve')
    assert resp.status_code == 200
    assert resp.get_json()["data"]["status"] == "Active"


def test_approve_already_active_student_conflict(admin_client, seed_students):
    active_student = next(s for s in seed_students if s.status == 'Active')
    resp = admin_client.patch(f'/admin/approvals/student/{active_student.student_id}/approve')
    assert resp.status_code == 409


def test_reject_pending_tutor(admin_client, seed_tutors):
    pending_tutor = next(t for t in seed_tutors if t.status == 'Pending')
    resp = admin_client.patch(f'/admin/approvals/tutor/{pending_tutor.tutor_id}/reject')
    assert resp.status_code == 200
    assert resp.get_json()["data"]["status"] == "Rejected"

    # The record itself must be gone from the database -- not just
    # relabeled -- so it never resurfaces in User Manager or Pending
    # Approvals, even after a "refresh" (re-querying the list endpoints).
    get_resp = admin_client.get(f'/admin/tutors/{pending_tutor.tutor_id}')
    assert get_resp.status_code == 404

    list_resp = admin_client.get('/admin/tutors')
    names = {row["tutor_name"] for row in list_resp.get_json()["data"]}
    assert "Nathan Cole" not in names

    approvals_resp = admin_client.get('/admin/approvals?status=All')
    approval_names = {row["name"] for row in approvals_resp.get_json()["data"]}
    assert "Nathan Cole" not in approval_names


def test_reject_pending_parent_nulls_child_fk(admin_client, seed_students):
    """Rejecting a pending parent should delete the parent row and null
    out parent_id on any linked students, mirroring delete_parent()."""
    from models import Parent, Student
    from database import db as _db
    from werkzeug.security import generate_password_hash

    pending_parent = Parent(
        role_id=seed_students[0].role_id,
        parent_name='Pending Parent',
        email='pending.parent@parentmail.com',
        password_hash=generate_password_hash('Parent@123'),
        status='Pending',
    )
    _db.session.add(pending_parent)
    _db.session.commit()

    child = seed_students[0]
    child.parent_id = pending_parent.parent_id
    _db.session.commit()

    resp = admin_client.patch(f'/admin/approvals/parent/{pending_parent.parent_id}/reject')
    assert resp.status_code == 200

    assert Parent.query.get(pending_parent.parent_id) is None
    refreshed_child = Student.query.get(child.student_id)
    assert refreshed_child.parent_id is None


def test_approve_then_block_and_delete_become_available(admin_client, seed_students):
    """After approval, normal User Manager actions (block/delete) should
    work again on the (now-Active) account."""
    pending_student = next(s for s in seed_students if s.status == 'Pending')

    approve_resp = admin_client.patch(f'/admin/approvals/student/{pending_student.student_id}/approve')
    assert approve_resp.status_code == 200
    assert approve_resp.get_json()["data"]["status"] == "Active"

    block_resp = admin_client.patch(
        f'/admin/students/{pending_student.student_id}/status', json={"status": "Blocked"}
    )
    assert block_resp.status_code == 200
    assert block_resp.get_json()["data"]["status"] == "Blocked"

    delete_resp = admin_client.delete(f'/admin/students/{pending_student.student_id}')
    assert delete_resp.status_code == 200


def test_block_pending_student_is_rejected(admin_client, seed_students):
    """A still-pending student cannot be blocked/unblocked from User
    Manager -- they must go through Approve/Reject first."""
    pending_student = next(s for s in seed_students if s.status == 'Pending')
    resp = admin_client.patch(
        f'/admin/students/{pending_student.student_id}/status', json={"status": "Blocked"}
    )
    assert resp.status_code == 409


def test_delete_pending_student_is_rejected(admin_client, seed_students):
    """A still-pending student cannot be deleted from User Manager --
    that must go through the Reject action instead."""
    pending_student = next(s for s in seed_students if s.status == 'Pending')
    resp = admin_client.delete(f'/admin/students/{pending_student.student_id}')
    assert resp.status_code == 409


def test_approve_invalid_entity_type(admin_client, seed_students):
    pending_student = next(s for s in seed_students if s.status == 'Pending')
    resp = admin_client.patch(f'/admin/approvals/bogus/{pending_student.student_id}/approve')
    assert resp.status_code == 400


def test_approve_not_found(admin_client, seed_students):
    resp = admin_client.patch('/admin/approvals/student/99999/approve')
    assert resp.status_code == 404
