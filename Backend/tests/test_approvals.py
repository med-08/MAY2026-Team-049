"""
Test cases for /admin/approvals/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /approvals | default (status=Pending) | 200, 2 entries (Liam Johnson, Nathan Cole) | 200, 2 entries (Liam Johnson, Nathan Cole) | Success |
| GET /approvals | ?status=All | 200, 6 entries (3 students + 2 tutors + 1 parent) | 200, 6 entries (3 students + 2 tutors + 1 parent) | Success |
| GET /approvals | ?status=Invalid | 400 Bad Request | 400 Bad Request | Success |
| PATCH /approvals/student/<id>/approve | valid pending student id | 200, status becomes Active | 200, status becomes Active | Success |
| PATCH /approvals/student/<id>/approve | already-Active student | 409 Conflict | 409 Conflict | Success |
| PATCH /approvals/tutor/<id>/reject | valid pending tutor id | 200, status becomes Rejected | 200, status becomes Rejected | Success |
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


def test_approve_invalid_entity_type(admin_client, seed_students):
    pending_student = next(s for s in seed_students if s.status == 'Pending')
    resp = admin_client.patch(f'/admin/approvals/bogus/{pending_student.student_id}/approve')
    assert resp.status_code == 400


def test_approve_not_found(admin_client, seed_students):
    resp = admin_client.patch('/admin/approvals/student/99999/approve')
    assert resp.status_code == 404
