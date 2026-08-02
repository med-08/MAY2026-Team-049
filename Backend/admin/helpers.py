"""
Shared helpers for the Admin Dashboard blueprint.

Response shape matches the convention already used elsewhere in this app
(auth/routes.py, app.py error handlers): {"success": bool, "message": ...}
rather than reinventing a different envelope just for /admin/*.
"""
from flask import jsonify
from sqlalchemy import or_

MAX_PER_PAGE = 100
DEFAULT_PER_PAGE = 8


def error_response(message, status_code=400, errors=None):
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code


def success_response(data=None, message=None, status_code=200, meta=None):
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def parse_pagination_args(request):
    """Parse & validate `page`/`per_page` query params.

    Raises ValueError with a human readable message on bad input.
    """
    raw_page = request.args.get('page', '1')
    raw_per_page = request.args.get('per_page', str(DEFAULT_PER_PAGE))

    try:
        page = int(raw_page)
        per_page = int(raw_per_page)
    except (TypeError, ValueError):
        raise ValueError("Query params 'page' and 'per_page' must be integers.")

    if page < 1:
        raise ValueError("Query param 'page' must be >= 1.")
    if per_page < 1 or per_page > MAX_PER_PAGE:
        raise ValueError(f"Query param 'per_page' must be between 1 and {MAX_PER_PAGE}.")

    return page, per_page


def apply_search(query, model, search_fields, search_term):
    """Apply a case-insensitive OR search across the given model fields.

    Escapes SQL LIKE wildcard characters ('%', '_', '\\') so a literal
    search for one of them is matched literally rather than being
    interpreted as a wildcard by the database.
    """
    if not search_term:
        return query

    escaped = (
        search_term.replace('\\', '\\\\')
        .replace('%', '\\%')
        .replace('_', '\\_')
    )
    like = f"%{escaped}%"
    conditions = [
        getattr(model, f).ilike(like, escape='\\')
        for f in search_fields if hasattr(model, f)
    ]
    if conditions:
        query = query.filter(or_(*conditions))
    return query


def apply_sort(query, model, sort_by, order):
    """Apply ORDER BY sort_by (asc/desc) if sort_by is a valid column."""
    if sort_by and hasattr(model, sort_by):
        column = getattr(model, sort_by)
        query = query.order_by(column.desc() if order == 'desc' else column.asc())
    return query


def paginate(query, page, per_page):
    """Return (items, total) for the given page/per_page."""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def pagination_meta(page, per_page, total):
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
