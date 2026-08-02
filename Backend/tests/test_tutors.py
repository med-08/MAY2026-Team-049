"""
Test cases for /admin/tutors/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /tutors | no params | 200, 2 tutors | 200, 2 tutors | Success |
| GET /tutors | ?status=Pending | 200, 1 tutor (Nathan Cole) | 200, 1 tutor (Nathan Cole) | Success |
| GET /tutors/<id> | valid id with a scheduled session | 200, subjects includes 'Mathematics' | 200, subjects includes 'Mathematics' | Success |
| GET /tutors/<id> | non-existent id | 404 Not Found | 404 Not Found | Success |
| PATCH /tutors/<id>/status | {"status": "Blocked"} | 200, status now Blocked | 200, status now Blocked | Success |
| PATCH /tutors/<id>/status | {"status": "Approved"} invalid value | 400 Bad Request | 400 Bad Request | Success |
| DELETE /tutors/<id> | valid id | 200, tutor removed | 200, tutor removed | Success |
| DELETE /tutors/<id> | non-existent id | 404 Not Found | 404 Not Found | Success |
"""


def test_list_tutors(admin_client, seed_tutors):
    resp = admin_client.get('/admin/tutors')
    assert resp.status_code == 200
    assert resp.get_json()["meta"]["total"] == 2


def test_list_tutors_status_filter(admin_client, seed_tutors):
    resp = admin_client.get('/admin/tutors?status=Pending')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["tutor_name"] == "Nathan Cole"


def test_get_tutor_with_subjects(admin_client, seed_tutors):
    tutor = seed_tutors[0]
    resp = admin_client.get(f'/admin/tutors/{tutor.tutor_id}')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "Mathematics" in data["subjects"]


def test_get_tutor_not_found(admin_client, seed_tutors):
    resp = admin_client.get('/admin/tutors/99999')
    assert resp.status_code == 404


def test_block_tutor(admin_client, seed_tutors):
    tutor = seed_tutors[0]
    resp = admin_client.patch(f'/admin/tutors/{tutor.tutor_id}/status', json={"status": "Blocked"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["status"] == "Blocked"


def test_update_tutor_status_invalid_value(admin_client, seed_tutors):
    tutor = seed_tutors[0]
    resp = admin_client.patch(f'/admin/tutors/{tutor.tutor_id}/status', json={"status": "Approved"})
    assert resp.status_code == 400


def test_delete_tutor(admin_client, seed_tutors):
    tutor = seed_tutors[1]
    resp = admin_client.delete(f'/admin/tutors/{tutor.tutor_id}')
    assert resp.status_code == 200

    list_resp = admin_client.get('/admin/tutors')
    assert list_resp.get_json()["meta"]["total"] == 1


def test_delete_tutor_not_found(admin_client, seed_tutors):
    resp = admin_client.delete('/admin/tutors/99999')
    assert resp.status_code == 404
