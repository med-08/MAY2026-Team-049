"""
Test cases for GET /admin/dashboard/*

| API | Inputs | Expected Output | Actual Output | Result |
|---|---|---|---|---|
| GET /dashboard/stats | seeded 3 students, 2 tutors, 1 parent, 3 subjects | counts match seeded data, blocked=1, pending=2 | counts matched seeded data, blocked=1, pending=2 | Success |
| GET /dashboard/stats | empty DB | all counts = 0 | all counts = 0 | Success |
| GET /dashboard/analytics/students-per-subject | seeded subjects+enrollments | Mathematics=1, Science=1, English=0 | Mathematics=1, Science=1, English=0 | Success |
| GET /dashboard/analytics/monthly-registrations | default (months=7) | 7 buckets returned, ordered oldest->newest | 7 buckets returned, ordered oldest->newest | Success |
| GET /dashboard/analytics/monthly-registrations | months=abc (invalid) | 400 Bad Request | 400 Bad Request | Success |
| GET /dashboard/analytics/monthly-registrations | months=30 (out of range) | 400 Bad Request | 400 Bad Request | Success |
| GET /dashboard | seeded 3 students, 2 tutors | legacy {success, stats} shape, students_count=3 | legacy {success, stats} shape, students_count=3 | Success |
"""
import calendar
from datetime import date


def test_stats_with_seeded_data(admin_client, seed_students, seed_tutors):
    resp = admin_client.get('/admin/dashboard/stats')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["total_students"] == 3
    assert data["total_tutors"] == 2
    assert data["total_parents"] == 1
    assert data["blocked_students"] == 1
    assert data["pending_approvals"] == 2  # 1 pending student + 1 pending tutor
    assert data["total_subjects"] == 3


def test_stats_empty_database(admin_client):
    resp = admin_client.get('/admin/dashboard/stats')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data == {
        "total_students": 0,
        "total_tutors": 0,
        "total_parents": 0,
        "blocked_students": 0,
        "pending_approvals": 0,
        "total_subjects": 0,
    }


def test_students_per_subject(admin_client, seed_students):
    resp = admin_client.get('/admin/dashboard/analytics/students-per-subject')
    assert resp.status_code == 200
    data = {row["subject"]: row["count"] for row in resp.get_json()["data"]}
    assert data["Mathematics"] == 1
    assert data["Science"] == 1
    assert data["English"] == 0


def test_monthly_registrations_default(admin_client, seed_students):
    resp = admin_client.get('/admin/dashboard/analytics/monthly-registrations')
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 7
    current_month_label = calendar.month_abbr[date.today().month]
    assert data[-1]["month"] == current_month_label
    assert data[-1]["count"] >= 1


def test_monthly_registrations_invalid_months_param(admin_client):
    resp = admin_client.get('/admin/dashboard/analytics/monthly-registrations?months=abc')
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_monthly_registrations_out_of_range(admin_client):
    resp = admin_client.get('/admin/dashboard/analytics/monthly-registrations?months=30')
    assert resp.status_code == 400


def test_legacy_dashboard_alias_still_works(admin_client, seed_students, seed_tutors):
    """The original teammate stub (/admin/dashboard) is preserved for
    backward compatibility, with its original response shape."""
    resp = admin_client.get('/admin/dashboard')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['success'] is True
    assert body['stats']['students_count'] == 3
