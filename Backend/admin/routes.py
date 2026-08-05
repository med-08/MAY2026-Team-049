"""
Admin Dashboard API
=====================
All routes below are mounted under the blueprint's url_prefix='/admin'
(see admin/__init__.py) and require an authenticated Admin session via the
existing @admin_required decorator (decorators.py) -- i.e. the caller must
have already POSTed to /login with an Admin account.

Sections:
  - Dashboard stats & analytics
  - Student management
  - Parent management
  - Tutor management
  - Pending approvals (Student/Tutor/Parent sign-ups)
  - Admin profile (view/edit own profile, change own password)

User stories covered (Sprint 1 - Admin Dashboard):
  - Overview stats snapshot (students/tutors/parents/blocked/pending/subjects)
  - Students-per-subject and monthly-registration analytics
  - View/search/sort/filter/block/unblock/delete students
  - View/search/sort/filter/block/unblock/delete parents
  - View/search/sort/filter tutors (+ bonus block/delete, schema parity)
  - Review, approve, reject pending Student/Tutor/Parent registrations
  - View/edit own admin profile, change own password
"""
import calendar
from datetime import date

from flask import jsonify, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from admin import admin_bp
from decorators import admin_required
from database import db
from models import Student, Tutor, Parent, Admin, Role, Subject, StudentSubject, Session
from admin.helpers import (
    error_response, success_response, parse_pagination_args,
    apply_search, apply_sort, paginate, pagination_meta,
)


# ==================== DASHBOARD: STATS & ANALYTICS ====================

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_stats():
    """GET /admin/dashboard/stats -> top-level KPI cards for the Overview page."""
    try:
        total_students = Student.query.count()
        total_tutors = Tutor.query.count()
        total_parents = Parent.query.count()
        blocked_students = Student.query.filter_by(status='Blocked').count()
        pending_approvals = (
            Student.query.filter_by(status='Pending').count()
            + Tutor.query.filter_by(status='Pending').count()
            + Parent.query.filter_by(status='Pending').count()
        )
        total_subjects = Subject.query.count()
    except Exception as e:
        return error_response("Failed to compute dashboard statistics.", 500, errors=str(e))

    return success_response(data={
        "total_students": total_students,
        "total_tutors": total_tutors,
        "total_parents": total_parents,
        "blocked_students": blocked_students,
        "pending_approvals": pending_approvals,
        "total_subjects": total_subjects,
    })


# Kept for backward compatibility with the original teammate stub
# (`GET /admin/dashboard`), which returned a differently-shaped payload.
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard_legacy():
    """Legacy dashboard summary endpoint. Prefer /admin/dashboard/stats."""
    stats = {
        "students_count": Student.query.count(),
        "tutors_count": Tutor.query.count(),
        "parents_count": Parent.query.count(),
        "admins_count": Admin.query.count(),
    }
    return jsonify({"success": True, "stats": stats})


@admin_bp.route('/dashboard/analytics/students-per-subject', methods=['GET'])
@admin_required
def students_per_subject():
    """GET /admin/dashboard/analytics/students-per-subject -> doughnut chart data.

    NOTE (assumption): the schema models a many-to-many Student<->Subject
    relationship via StudentSubject; a student enrolled in 2 subjects is
    counted once per subject.
    """
    try:
        rows = (
            db.session.query(Subject.subject_name, func.count(StudentSubject.student_id))
            .outerjoin(StudentSubject, StudentSubject.subject_id == Subject.subject_id)
            .group_by(Subject.subject_id)
            .all()
        )
    except Exception as e:
        return error_response("Failed to compute students-per-subject analytics.", 500, errors=str(e))

    return success_response(data=[{"subject": name, "count": count} for name, count in rows])


def _month_buckets(n):
    """Return a list of (year, month) tuples for the last n months, oldest first."""
    today = date.today()
    year, month = today.year, today.month
    buckets = []
    for _ in range(n):
        buckets.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    buckets.reverse()
    return buckets


@admin_bp.route('/dashboard/analytics/monthly-registrations', methods=['GET'])
@admin_required
def monthly_registrations():
    """GET /admin/dashboard/analytics/monthly-registrations?months=7 -> line chart data.

    NOTE (assumption): "New Registrations" counts all new platform users
    combined (students + tutors + parents), grouped by registration month.
    """
    raw_months = request.args.get('months', '7')
    try:
        months = int(raw_months)
    except (TypeError, ValueError):
        return error_response("Query param 'months' must be an integer.", 400)

    if months < 1 or months > 24:
        return error_response("Query param 'months' must be between 1 and 24.", 400)

    buckets = _month_buckets(months)
    counts = {b: 0 for b in buckets}

    try:
        all_dates = []
        for Model in (Student, Tutor, Parent):
            rows = db.session.query(Model.registered_at).all()
            all_dates.extend([r[0] for r in rows if r[0] is not None])
    except Exception as e:
        return error_response("Failed to compute monthly registration analytics.", 500, errors=str(e))

    for dt in all_dates:
        key = (dt.year, dt.month)
        if key in counts:
            counts[key] += 1

    data = [
        {"month": calendar.month_abbr[m], "year": y, "count": counts[(y, m)]}
        for (y, m) in buckets
    ]
    return success_response(data=data)


@admin_bp.route('/dashboard/analytics/tutors-per-subject', methods=['GET'])
@admin_required
def tutors_per_subject():
    """GET /admin/dashboard/analytics/tutors-per-subject -> bar chart data
    showing tutor *supply* per subject, meant to be read alongside
    students-per-subject (demand) so admins can spot subjects that are
    short on tutors.

    NOTE (assumption): mirrors _tutor_subjects()'s existing assumption --
    there is no direct Tutor<->Subject table, so "teaches this subject" is
    derived from distinct subjects across a tutor's scheduled Sessions.
    """
    try:
        rows = (
            db.session.query(Subject.subject_name, func.count(func.distinct(Session.tutor_id)))
            .outerjoin(Session, Session.subject_id == Subject.subject_id)
            .group_by(Subject.subject_id)
            .all()
        )
    except Exception as e:
        return error_response("Failed to compute tutors-per-subject analytics.", 500, errors=str(e))

    return success_response(data=[{"subject": name, "count": count} for name, count in rows])


@admin_bp.route('/dashboard/analytics/status-breakdown', methods=['GET'])
@admin_required
def status_breakdown():
    """GET /admin/dashboard/analytics/status-breakdown -> stacked bar chart
    data: Active/Blocked/Pending counts for each of Students/Tutors/Parents.
    Gives a fuller picture than the single "blocked_students" KPI card on
    the Overview page.
    """
    try:
        data = []
        for label, Model in (('Students', Student), ('Tutors', Tutor), ('Parents', Parent)):
            data.append({
                "type": label,
                "active": Model.query.filter_by(status='Active').count(),
                "blocked": Model.query.filter_by(status='Blocked').count(),
                "pending": Model.query.filter_by(status='Pending').count(),
            })
    except Exception as e:
        return error_response("Failed to compute status breakdown analytics.", 500, errors=str(e))

    return success_response(data=data)


# ==================== STUDENTS ====================

STUDENT_SORT_FIELDS = {'student_id', 'student_name', 'email', 'school', 'status', 'registered_at'}
STATUS_FILTERS = {'All', 'Active', 'Blocked', 'Pending'}
STATUS_UPDATES = {'Active', 'Blocked'}


def _student_subjects(student_id):
    rows = (
        db.session.query(Subject.subject_name)
        .join(StudentSubject, StudentSubject.subject_id == Subject.subject_id)
        .filter(StudentSubject.student_id == student_id)
        .all()
    )
    return [r[0] for r in rows]


def _serialize_student(s):
    parent = Parent.query.get(s.parent_id) if s.parent_id else None
    return {
        "student_id": s.student_id,
        "student_name": s.student_name,
        "email": s.email,
        "phone_no": s.phone_no,
        "school": s.school,
        "status": s.status,
        "parent_id": s.parent_id,
        "parent_name": parent.parent_name if parent else None,
        "subjects": _student_subjects(s.student_id),
        "registered_at": s.registered_at.isoformat() if s.registered_at else None,
        "last_login_at": s.last_login_at.isoformat() if s.last_login_at else None,
    }


@admin_bp.route('/students', methods=['GET'])
@admin_required
def list_students():
    """GET /admin/students?search=&status=&sort_by=&order=&page=&per_page="""
    try:
        page, per_page = parse_pagination_args(request)
    except ValueError as e:
        return error_response(str(e), 400)

    status = request.args.get('status', 'All')
    if status not in STATUS_FILTERS:
        return error_response(f"Invalid 'status' filter '{status}'. Must be one of {sorted(STATUS_FILTERS)}.", 400)

    sort_by = request.args.get('sort_by', 'student_id')
    if sort_by not in STUDENT_SORT_FIELDS:
        return error_response(f"Cannot sort by '{sort_by}'. Allowed: {sorted(STUDENT_SORT_FIELDS)}.", 400)

    order = request.args.get('order', 'asc')
    if order not in {'asc', 'desc'}:
        return error_response("Query param 'order' must be 'asc' or 'desc'.", 400)

    search = request.args.get('search', '').strip()

    query = Student.query
    if status != 'All':
        query = query.filter(Student.status == status)
    query = apply_search(query, Student, ['student_name', 'email'], search)
    query = apply_sort(query, Student, sort_by, order)

    try:
        items, total = paginate(query, page, per_page)
    except Exception as e:
        return error_response("Failed to retrieve students.", 500, errors=str(e))

    return success_response(
        data=[_serialize_student(s) for s in items],
        meta=pagination_meta(page, per_page, total),
    )


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return error_response(f"Student with id {student_id} not found.", 404)
    return success_response(data=_serialize_student(student))


@admin_bp.route('/students/<int:student_id>/status', methods=['PATCH'])
@admin_required
def update_student_status(student_id):
    """PATCH /admin/students/<id>/status  body: {"status": "Active"|"Blocked"}"""
    student = Student.query.get(student_id)
    if not student:
        return error_response(f"Student with id {student_id} not found.", 404)

    body = request.get_json(silent=True)
    if not body or 'status' not in body:
        return error_response("Request body must be JSON and include a 'status' field.", 400)

    new_status = body['status']
    if new_status not in STATUS_UPDATES:
        return error_response(f"'status' must be one of {sorted(STATUS_UPDATES)}.", 400)

    try:
        student.status = new_status
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update student status.", 500, errors=str(e))

    return success_response(
        data=_serialize_student(student),
        message=f"Student '{student.student_name}' status updated to {new_status}.",
    )


@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    """DELETE /admin/students/<id>

    NOTE (assumption): the schema has no ON DELETE CASCADE for tables
    referencing student_id (StudentSubject, AssignmentSubmission,
    LearningProgress, SessionBooking, etc). SQLite does not enforce FK
    constraints here by default, so the row deletes cleanly but dependent
    rows become orphaned. Flagged as a schema follow-up.
    """
    student = Student.query.get(student_id)
    if not student:
        return error_response(f"Student with id {student_id} not found.", 404)

    try:
        name = student.student_name
        db.session.delete(student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete student.", 500, errors=str(e))

    return success_response(message=f"Student '{name}' (id {student_id}) deleted successfully.")


# ==================== PARENTS ====================

PARENT_SORT_FIELDS = {'parent_id', 'parent_name', 'email', 'status', 'registered_at'}


def _parent_children(parent_id):
    rows = Student.query.filter(Student.parent_id == parent_id).all()
    return [{"student_id": s.student_id, "student_name": s.student_name} for s in rows]


def _serialize_parent(p):
    return {
        "parent_id": p.parent_id,
        "parent_name": p.parent_name,
        "email": p.email,
        "phone_no": p.phone_no,
        "status": p.status,
        "children": _parent_children(p.parent_id),
        "registered_at": p.registered_at.isoformat() if p.registered_at else None,
        "last_login_at": p.last_login_at.isoformat() if p.last_login_at else None,
    }


@admin_bp.route('/parents', methods=['GET'])
@admin_required
def list_parents():
    """GET /admin/parents?search=&status=&sort_by=&order=&page=&per_page="""
    try:
        page, per_page = parse_pagination_args(request)
    except ValueError as e:
        return error_response(str(e), 400)

    status = request.args.get('status', 'All')
    if status not in STATUS_FILTERS:
        return error_response(f"Invalid 'status' filter '{status}'. Must be one of {sorted(STATUS_FILTERS)}.", 400)

    sort_by = request.args.get('sort_by', 'parent_id')
    if sort_by not in PARENT_SORT_FIELDS:
        return error_response(f"Cannot sort by '{sort_by}'. Allowed: {sorted(PARENT_SORT_FIELDS)}.", 400)

    order = request.args.get('order', 'asc')
    if order not in {'asc', 'desc'}:
        return error_response("Query param 'order' must be 'asc' or 'desc'.", 400)

    search = request.args.get('search', '').strip()

    query = Parent.query
    if status != 'All':
        query = query.filter(Parent.status == status)
    query = apply_search(query, Parent, ['parent_name', 'email'], search)
    query = apply_sort(query, Parent, sort_by, order)

    try:
        items, total = paginate(query, page, per_page)
    except Exception as e:
        return error_response("Failed to retrieve parents.", 500, errors=str(e))

    return success_response(
        data=[_serialize_parent(p) for p in items],
        meta=pagination_meta(page, per_page, total),
    )


@admin_bp.route('/parents/<int:parent_id>', methods=['GET'])
@admin_required
def get_parent(parent_id):
    parent = Parent.query.get(parent_id)
    if not parent:
        return error_response(f"Parent with id {parent_id} not found.", 404)
    return success_response(data=_serialize_parent(parent))


@admin_bp.route('/parents/<int:parent_id>/status', methods=['PATCH'])
@admin_required
def update_parent_status(parent_id):
    parent = Parent.query.get(parent_id)
    if not parent:
        return error_response(f"Parent with id {parent_id} not found.", 404)

    body = request.get_json(silent=True)
    if not body or 'status' not in body:
        return error_response("Request body must be JSON and include a 'status' field.", 400)

    new_status = body['status']
    if new_status not in STATUS_UPDATES:
        return error_response(f"'status' must be one of {sorted(STATUS_UPDATES)}.", 400)

    try:
        parent.status = new_status
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update parent status.", 500, errors=str(e))

    return success_response(
        data=_serialize_parent(parent),
        message=f"Parent '{parent.parent_name}' status updated to {new_status}.",
    )


@admin_bp.route('/parents/<int:parent_id>', methods=['DELETE'])
@admin_required
def delete_parent(parent_id):
    """DELETE /admin/parents/<id>

    Defensively nulls out parent_id on any linked students first, so we
    don't leave a dangling FK reference behind (the schema allows
    Student.parent_id to be nullable).
    """
    parent = Parent.query.get(parent_id)
    if not parent:
        return error_response(f"Parent with id {parent_id} not found.", 404)

    try:
        name = parent.parent_name
        Student.query.filter(Student.parent_id == parent_id).update({"parent_id": None})
        db.session.delete(parent)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete parent.", 500, errors=str(e))

    return success_response(message=f"Parent '{name}' (id {parent_id}) deleted successfully.")


# ==================== TUTORS ====================

TUTOR_SORT_FIELDS = {'tutor_id', 'tutor_name', 'email', 'experience_years', 'status', 'registered_at'}


def _tutor_subjects(tutor_id):
    """NOTE (assumption): there's no direct Tutor<->Subject table; we derive
    "subjects taught" from distinct subjects across the tutor's scheduled
    Sessions, which is the closest real signal available.
    """
    rows = (
        db.session.query(Subject.subject_name)
        .join(Session, Session.subject_id == Subject.subject_id)
        .filter(Session.tutor_id == tutor_id)
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def _serialize_tutor(t):
    return {
        "tutor_id": t.tutor_id,
        "tutor_name": t.tutor_name,
        "email": t.email,
        "phone_no": t.phone_no,
        "experience_years": t.experience_years,
        "status": t.status,
        "subjects": _tutor_subjects(t.tutor_id),
        "registered_at": t.registered_at.isoformat() if t.registered_at else None,
        "last_login_at": t.last_login_at.isoformat() if t.last_login_at else None,
    }


@admin_bp.route('/tutors', methods=['GET'])
@admin_required
def list_tutors():
    """GET /admin/tutors?search=&status=&sort_by=&order=&page=&per_page="""
    try:
        page, per_page = parse_pagination_args(request)
    except ValueError as e:
        return error_response(str(e), 400)

    status = request.args.get('status', 'All')
    if status not in STATUS_FILTERS:
        return error_response(f"Invalid 'status' filter '{status}'. Must be one of {sorted(STATUS_FILTERS)}.", 400)

    sort_by = request.args.get('sort_by', 'tutor_id')
    if sort_by not in TUTOR_SORT_FIELDS:
        return error_response(f"Cannot sort by '{sort_by}'. Allowed: {sorted(TUTOR_SORT_FIELDS)}.", 400)

    order = request.args.get('order', 'asc')
    if order not in {'asc', 'desc'}:
        return error_response("Query param 'order' must be 'asc' or 'desc'.", 400)

    search = request.args.get('search', '').strip()

    query = Tutor.query
    if status != 'All':
        query = query.filter(Tutor.status == status)
    query = apply_search(query, Tutor, ['tutor_name', 'email'], search)
    query = apply_sort(query, Tutor, sort_by, order)

    try:
        items, total = paginate(query, page, per_page)
    except Exception as e:
        return error_response("Failed to retrieve tutors.", 500, errors=str(e))

    return success_response(
        data=[_serialize_tutor(t) for t in items],
        meta=pagination_meta(page, per_page, total),
    )


@admin_bp.route('/tutors/<int:tutor_id>', methods=['GET'])
@admin_required
def get_tutor(tutor_id):
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return error_response(f"Tutor with id {tutor_id} not found.", 404)
    return success_response(data=_serialize_tutor(tutor))


@admin_bp.route('/tutors/<int:tutor_id>/status', methods=['PATCH'])
@admin_required
def update_tutor_status(tutor_id):
    """Bonus endpoint (schema parity) - not yet wired into Tutors.vue's
    read-only UI."""
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return error_response(f"Tutor with id {tutor_id} not found.", 404)

    body = request.get_json(silent=True)
    if not body or 'status' not in body:
        return error_response("Request body must be JSON and include a 'status' field.", 400)

    new_status = body['status']
    if new_status not in STATUS_UPDATES:
        return error_response(f"'status' must be one of {sorted(STATUS_UPDATES)}.", 400)

    try:
        tutor.status = new_status
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update tutor status.", 500, errors=str(e))

    return success_response(
        data=_serialize_tutor(tutor),
        message=f"Tutor '{tutor.tutor_name}' status updated to {new_status}.",
    )


@admin_bp.route('/tutors/<int:tutor_id>', methods=['DELETE'])
@admin_required
def delete_tutor(tutor_id):
    """Bonus endpoint (schema parity) - not yet wired into Tutors.vue's
    read-only UI."""
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return error_response(f"Tutor with id {tutor_id} not found.", 404)

    try:
        name = tutor.tutor_name
        db.session.delete(tutor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete tutor.", 500, errors=str(e))

    return success_response(message=f"Tutor '{name}' (id {tutor_id}) deleted successfully.")


# ==================== GLOBAL SEARCH ====================

SEARCH_RESULT_LIMIT = 6


@admin_bp.route('/search', methods=['GET'])
@admin_required
def global_search():
    """GET /admin/search?q=<term> -> dashboard-wide quick search.

    Powers the command-palette style search in the navbar so an admin can
    jump straight to a student/tutor/parent from *any* page, not just from
    within that entity's own list view. Searches name + email across all
    three entity types (any status, since Pending/Blocked records are
    often exactly what an admin is hunting for) and returns a handful of
    the closest matches per type.
    """
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return success_response(
            data={"students": [], "tutors": [], "parents": []},
            meta={"query": q, "total": 0},
        )

    try:
        student_rows = (
            apply_search(Student.query, Student, ['student_name', 'email'], q)
            .limit(SEARCH_RESULT_LIMIT).all()
        )
        tutor_rows = (
            apply_search(Tutor.query, Tutor, ['tutor_name', 'email'], q)
            .limit(SEARCH_RESULT_LIMIT).all()
        )
        parent_rows = (
            apply_search(Parent.query, Parent, ['parent_name', 'email'], q)
            .limit(SEARCH_RESULT_LIMIT).all()
        )
    except Exception as e:
        return error_response("Search failed.", 500, errors=str(e))

    data = {
        "students": [
            {"id": s.student_id, "name": s.student_name, "email": s.email, "status": s.status}
            for s in student_rows
        ],
        "tutors": [
            {"id": t.tutor_id, "name": t.tutor_name, "email": t.email, "status": t.status}
            for t in tutor_rows
        ],
        "parents": [
            {"id": p.parent_id, "name": p.parent_name, "email": p.email, "status": p.status}
            for p in parent_rows
        ],
    }
    total = len(data["students"]) + len(data["tutors"]) + len(data["parents"])
    return success_response(data=data, meta={"query": q, "total": total})


# ==================== PENDING APPROVALS ====================

ENTITY_MAP = {
    'student': (Student, 'student_id', 'student_name'),
    'tutor': (Tutor, 'tutor_id', 'tutor_name'),
    'parent': (Parent, 'parent_id', 'parent_name'),
}
APPROVAL_STATUS_FILTERS = {'All', 'Pending', 'Active', 'Blocked', 'Rejected'}


def _serialize_entity(entity_type, entity, id_attr, name_attr):
    return {
        "id": getattr(entity, id_attr),
        "type": entity_type.capitalize(),
        "name": getattr(entity, name_attr),
        "email": entity.email,
        "status": entity.status,
        "registration_date": entity.registered_at.isoformat() if entity.registered_at else None,
    }


@admin_bp.route('/approvals', methods=['GET'])
@admin_required
def list_approvals():
    """GET /admin/approvals?status=Pending -> combined Student+Tutor+Parent list."""
    status = request.args.get('status', 'Pending')
    if status not in APPROVAL_STATUS_FILTERS:
        return error_response(
            f"Invalid 'status' filter '{status}'. Must be one of {sorted(APPROVAL_STATUS_FILTERS)}.", 400
        )

    try:
        result = []
        for entity_type, (Model, id_attr, name_attr) in ENTITY_MAP.items():
            query = Model.query
            if status != 'All':
                query = query.filter(Model.status == status)
            for entity in query.all():
                result.append(_serialize_entity(entity_type, entity, id_attr, name_attr))
    except Exception as e:
        return error_response("Failed to retrieve pending approvals.", 500, errors=str(e))

    result.sort(key=lambda x: x["registration_date"] or "")
    return success_response(data=result, meta={"total": len(result)})


@admin_bp.route('/approvals/<string:entity_type>/<int:entity_id>/approve', methods=['PATCH'])
@admin_required
def approve_entity(entity_type, entity_id):
    entity_type = entity_type.lower()
    if entity_type not in ENTITY_MAP:
        return error_response(f"Invalid entity type '{entity_type}'. Must be one of {sorted(ENTITY_MAP)}.", 400)

    Model, id_attr, name_attr = ENTITY_MAP[entity_type]
    entity = Model.query.get(entity_id)
    if not entity:
        return error_response(f"{entity_type.capitalize()} with id {entity_id} not found.", 404)

    if entity.status != 'Pending':
        return error_response(f"Only pending registrations can be approved. Current status: '{entity.status}'.", 409)

    try:
        entity.status = 'Active'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to approve registration.", 500, errors=str(e))

    return success_response(
        data=_serialize_entity(entity_type, entity, id_attr, name_attr),
        message=f"{getattr(entity, name_attr)}'s registration was approved.",
    )


@admin_bp.route('/approvals/<string:entity_type>/<int:entity_id>/reject', methods=['PATCH'])
@admin_required
def reject_entity(entity_type, entity_id):
    entity_type = entity_type.lower()
    if entity_type not in ENTITY_MAP:
        return error_response(f"Invalid entity type '{entity_type}'. Must be one of {sorted(ENTITY_MAP)}.", 400)

    Model, id_attr, name_attr = ENTITY_MAP[entity_type]
    entity = Model.query.get(entity_id)
    if not entity:
        return error_response(f"{entity_type.capitalize()} with id {entity_id} not found.", 404)

    if entity.status != 'Pending':
        return error_response(f"Only pending registrations can be rejected. Current status: '{entity.status}'.", 409)

    try:
        entity.status = 'Rejected'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to reject registration.", 500, errors=str(e))

    return success_response(
        data=_serialize_entity(entity_type, entity, id_attr, name_attr),
        message=f"{getattr(entity, name_attr)}'s registration was rejected.",
    )


# ==================== ADMIN PROFILE (self-service) ====================

def _current_admin_or_none():
    admin_id = session.get('user_id')
    if not admin_id or session.get('role') != 'Admin':
        return None
    return Admin.query.get(admin_id)


def _serialize_admin(admin):
    role = Role.query.get(admin.role_id)
    return {
        "admin_id": admin.admin_id,
        "username": admin.username,
        "admin_name": admin.admin_name,
        "email": admin.email,
        "role": role.role_name if role else None,
        "registered_at": admin.registered_at.isoformat() if admin.registered_at else None,
        "last_login_at": admin.last_login_at.isoformat() if admin.last_login_at else None,
    }


@admin_bp.route('/profile/me', methods=['GET'])
@admin_required
def get_my_profile():
    """GET /admin/profile/me -> the logged-in admin's own profile.

    NOTE: uses the session's admin id rather than trusting an id in the
    URL, now that real login/session auth exists (see decorators.py).
    """
    admin = _current_admin_or_none()
    if not admin:
        return error_response("Admin session not found.", 401)
    return success_response(data=_serialize_admin(admin))


@admin_bp.route('/profile/me', methods=['PUT'])
@admin_required
def update_my_profile():
    """PUT /admin/profile/me  body: {"admin_name"?: str, "email"?: str}"""
    admin = _current_admin_or_none()
    if not admin:
        return error_response("Admin session not found.", 401)

    body = request.get_json(silent=True)
    if not body:
        return error_response("Request body must be valid JSON.", 400)

    admin_name = body.get('admin_name')
    email = body.get('email')

    if admin_name is None and email is None:
        return error_response("Provide at least one of 'admin_name' or 'email' to update.", 400)

    if admin_name is not None:
        if not isinstance(admin_name, str) or not admin_name.strip():
            return error_response("'admin_name' must be a non-empty string.", 400)
        admin.admin_name = admin_name.strip()

    if email is not None:
        if not isinstance(email, str) or '@' not in email or '.' not in email.split('@')[-1]:
            return error_response("'email' must be a valid email address.", 400)
        existing = Admin.query.filter(Admin.email == email, Admin.admin_id != admin.admin_id).first()
        if existing:
            return error_response(f"Email '{email}' is already in use by another admin.", 409)
        admin.email = email

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update profile.", 500, errors=str(e))

    return success_response(data=_serialize_admin(admin), message="Profile updated successfully.")


@admin_bp.route('/profile/me/password', methods=['PUT'])
@admin_required
def change_my_password():
    """PUT /admin/profile/me/password
    body: {"current_password": str, "new_password": str, "confirm_password": str}
    """
    admin = _current_admin_or_none()
    if not admin:
        return error_response("Admin session not found.", 401)

    body = request.get_json(silent=True)
    if not body:
        return error_response("Request body must be valid JSON.", 400)

    current_password = body.get('current_password')
    new_password = body.get('new_password')
    confirm_password = body.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        return error_response(
            "'current_password', 'new_password' and 'confirm_password' are all required.", 400
        )

    if not check_password_hash(admin.password_hash, current_password):
        return error_response("Current password is incorrect.", 401)

    if len(new_password) < 6:
        return error_response("New password must be at least 6 characters long.", 400)

    if new_password != confirm_password:
        return error_response("New password and confirmation do not match.", 400)

    try:
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update password.", 500, errors=str(e))

    return success_response(message="Password changed successfully.")
