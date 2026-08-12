"""
Test cases for the new Admin Dashboard improvements:
  - GET /admin/dashboard/analytics/tutors-per-subject
  - GET /admin/dashboard/analytics/status-breakdown
  - GET /admin/search

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /dashboard/analytics/tutors-per-subject | seeded tutors+session on Mathematics | Mathematics=1, Science=0, English=0 | Mathematics=1, Science=0, English=0 | Success |
| GET /dashboard/analytics/status-breakdown | seeded 3 students, 2 tutors, 1 parent | Students active=1/blocked=1/pending=1, Tutors active=1/pending=1, Parents active=1 | matched | Success |
| GET /search | q='mehta' | 1 student + 1 parent match ("Mehta") | matched | Success |
| GET /search | q='a' (too short) | empty results, no DB error | empty results | Success |
| GET /search | q='zzz-no-match' | empty results, 200 OK | empty results | Success |
| GET /search | unauthenticated | 401 | 401 | Success |
"""


def test_tutors_per_subject(admin_client, seed_tutors):
    resp = admin_client.get('/admin/dashboard/analytics/tutors-per-subject')
    assert resp.status_code == 200
    data = {row["subject"]: row["count"] for row in resp.get_json()["data"]}
    assert data["Mathematics"] == 1
    assert data["Science"] == 0
    assert data["English"] == 0


def test_status_breakdown(admin_client, seed_students, seed_tutors):
    resp = admin_client.get('/admin/dashboard/analytics/status-breakdown')
    assert resp.status_code == 200
    data = {row["type"]: row for row in resp.get_json()["data"]}

    assert data["Students"]["active"] == 1
    assert data["Students"]["blocked"] == 1
    assert data["Students"]["pending"] == 1

    assert data["Tutors"]["active"] == 1
    assert data["Tutors"]["pending"] == 1
    assert data["Tutors"]["blocked"] == 0

    assert data["Parents"]["active"] == 1
    assert data["Parents"]["blocked"] == 0
    assert data["Parents"]["pending"] == 0


def test_status_breakdown_empty_database(admin_client):
    resp = admin_client.get('/admin/dashboard/analytics/status-breakdown')
    assert resp.status_code == 200
    for row in resp.get_json()["data"]:
        assert row["active"] == 0
        assert row["blocked"] == 0
        assert row["pending"] == 0


def test_global_search_matches_across_entity_types(admin_client, seed_students, seed_tutors):
    # "Mehta" matches student Aarav Mehta (by name) and parent Rajesh Mehta
    # (by name) -- exercising the cross-entity fan-out in one query.
    resp = admin_client.get('/admin/search?q=Mehta')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True

    student_names = [s["name"] for s in body["data"]["students"]]
    parent_names = [p["name"] for p in body["data"]["parents"]]
    assert "Aarav Mehta" in student_names
    assert "Rajesh Mehta" in parent_names
    assert body["meta"]["total"] >= 2


def test_global_search_matches_by_email(admin_client, seed_tutors):
    resp = admin_client.get('/admin/search?q=sarah.bennett')
    assert resp.status_code == 200
    tutor_names = [t["name"] for t in resp.get_json()["data"]["tutors"]]
    assert "Dr. Sarah Bennett" in tutor_names


def test_global_search_short_query_returns_empty_without_error(admin_client, seed_students):
    resp = admin_client.get('/admin/search?q=a')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data == {"students": [], "tutors": [], "parents": []}


def test_global_search_no_matches(admin_client, seed_students):
    resp = admin_client.get('/admin/search?q=zzz-no-match')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data == {"students": [], "tutors": [], "parents": []}
    assert resp.get_json()["meta"]["total"] == 0


def test_global_search_requires_admin_session(client):
    resp = client.get('/admin/search?q=mehta')
    assert resp.status_code == 401
