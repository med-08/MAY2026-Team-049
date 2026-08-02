"""
Test cases for /admin/students/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /students | no params | 200, 3 students, meta.total=3 | 200, 3 students, meta.total=3 | Success |
| GET /students | ?status=Blocked | 200, 1 student (Isha Kapoor) | 200, 1 student (Isha Kapoor) | Success |
| GET /students | ?search=liam | 200, 1 student (Liam Johnson) | 200, 1 student (Liam Johnson) | Success |
| GET /students | ?status=Invalid | 400 Bad Request | 400 Bad Request | Success |
| GET /students | ?sort_by=not_a_field | 400 Bad Request | 400 Bad Request | Success |
| GET /students | ?page=0 | 400 Bad Request | 400 Bad Request | Success |
| GET /students | ?per_page=500 | 400 Bad Request | 400 Bad Request | Success |
| GET /students/<id> | valid id | 200, correct student payload | 200, correct student payload | Success |
| GET /students/<id> | non-existent id (99999) | 404 Not Found | 404 Not Found | Success |
| PATCH /students/<id>/status | {"status": "Blocked"} on Active student | 200, status now Blocked | 200, status now Blocked | Success |
| PATCH /students/<id>/status | {"status": "Pending"} (not allowed value) | 400 Bad Request | 400 Bad Request | Success |
| PATCH /students/<id>/status | missing body | 400 Bad Request | 400 Bad Request | Success |
| PATCH /students/<id>/status | non-existent id | 404 Not Found | 404 Not Found | Success |
| DELETE /students/<id> | valid id | 200, student removed, count drops by 1 | 200, student removed, count drops by 1 | Success |
| DELETE /students/<id> | non-existent id | 404 Not Found | 404 Not Found | Success |
| GET /students | ?search=_ (literal underscore) | 0 matches (no name/email contains "_") | **3 matches before fix** (LIKE wildcard bug) -> 0 matches after fix | Fail -> Success (fixed) |
| GET /students | ?search=%25 (literal percent) | 0 matches | 0 matches (after fix) | Success |
"""


def test_list_students_no_filters(admin_client, seed_students):
    resp = admin_client.get('/admin/students')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["meta"]["total"] == 3
    assert len(body["data"]) == 3


def test_list_students_status_filter(admin_client, seed_students):
    resp = admin_client.get('/admin/students?status=Blocked')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["student_name"] == "Isha Kapoor"


def test_list_students_search(admin_client, seed_students):
    resp = admin_client.get('/admin/students?search=liam')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["student_name"] == "Liam Johnson"


def test_list_students_invalid_status(admin_client, seed_students):
    resp = admin_client.get('/admin/students?status=NotAStatus')
    assert resp.status_code == 400


def test_list_students_invalid_sort_field(admin_client, seed_students):
    resp = admin_client.get('/admin/students?sort_by=not_a_field')
    assert resp.status_code == 400


def test_list_students_invalid_page(admin_client, seed_students):
    resp = admin_client.get('/admin/students?page=0')
    assert resp.status_code == 400


def test_list_students_per_page_too_large(admin_client, seed_students):
    resp = admin_client.get('/admin/students?per_page=500')
    assert resp.status_code == 400


def test_get_student_by_id(admin_client, seed_students):
    student = seed_students[0]
    resp = admin_client.get(f'/admin/students/{student.student_id}')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["student_name"] == "Aarav Mehta"
    assert data["parent_name"] == "Rajesh Mehta"
    assert "Mathematics" in data["subjects"]


def test_get_student_not_found(admin_client, seed_students):
    resp = admin_client.get('/admin/students/99999')
    assert resp.status_code == 404


def test_block_active_student(admin_client, seed_students):
    student = seed_students[0]
    assert student.status == 'Active'
    resp = admin_client.patch(f'/admin/students/{student.student_id}/status', json={"status": "Blocked"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["status"] == "Blocked"


def test_update_student_status_invalid_value(admin_client, seed_students):
    student = seed_students[0]
    resp = admin_client.patch(f'/admin/students/{student.student_id}/status', json={"status": "Pending"})
    assert resp.status_code == 400


def test_update_student_status_missing_body(admin_client, seed_students):
    student = seed_students[0]
    resp = admin_client.patch(f'/admin/students/{student.student_id}/status')
    assert resp.status_code == 400


def test_update_student_status_not_found(admin_client, seed_students):
    resp = admin_client.patch('/admin/students/99999/status', json={"status": "Blocked"})
    assert resp.status_code == 404


def test_delete_student(admin_client, seed_students):
    student = seed_students[1]
    resp = admin_client.delete(f'/admin/students/{student.student_id}')
    assert resp.status_code == 200

    list_resp = admin_client.get('/admin/students')
    assert list_resp.get_json()["meta"]["total"] == 2


def test_delete_student_not_found(admin_client, seed_students):
    resp = admin_client.delete('/admin/students/99999')
    assert resp.status_code == 404


def test_search_with_sql_wildcard_characters_is_treated_literally(admin_client, seed_students):
    """Regression test for a real bug found during iterative testing of an
    earlier version of this admin blueprint (same bug class applies here
    since apply_search() is shared logic).

    BUG: searching for a literal underscore ("_") originally returned all
    3 seeded students (actual output), instead of the expected 0 matches,
    because none of the seeded names/emails contain a literal underscore.
    Root cause: SQL LIKE treats "_" as a single-character wildcard and "%"
    as a multi-character wildcard; the raw search term was interpolated
    into the LIKE pattern without escaping those characters.

    FIX: `apply_search()` in admin/helpers.py escapes '\\', '%' and '_' in
    the user-supplied search term and passes escape='\\' to SQLAlchemy's
    ilike(), so these characters are matched literally.

    | Inputs   | Expected Output | Actual Output (before fix) | Actual Output (after fix) | Result |
    |-----------|-------------------|--------------------------------|-------------------------------|--------|
    | ?search=_ | 0 matches         | 3 matches (bug)                | 0 matches                     | Success (after fix) |
    """
    resp = admin_client.get('/admin/students?search=_')
    assert resp.status_code == 200
    assert resp.get_json()["meta"]["total"] == 0


def test_search_with_percent_wildcard_is_treated_literally(admin_client, seed_students):
    resp = admin_client.get('/admin/students?search=%25')  # URL-encoded '%'
    assert resp.status_code == 200
    assert resp.get_json()["meta"]["total"] == 0
