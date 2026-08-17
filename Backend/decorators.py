from functools import wraps
from flask import session, request, jsonify
from utils import decode_jwt_token

# NOTE on ordering: the Authorization/JWT check MUST run before the Flask
# session-cookie check in every decorator below.
#
# The session cookie Flask sets on /login is scoped to the domain
# (e.g. "localhost"), not to the origin/port. Browsers do not separate
# cookies by port, so when two different frontend apps (e.g. a Student app
# on one port and a Tutor/Admin app on another) run in the same browser,
# they all share that ONE session cookie. Logging in on one app overwrites
# the shared cookie for every other app.
#
# Each app's JWT, by contrast, lives in that app's own localStorage
# (scoped per-origin) and is sent explicitly via the Authorization header,
# so it correctly identifies "this app's logged-in user" even when the
# shared session cookie belongs to someone else. Checking the JWT first
# (falling back to the session cookie only when no Authorization header is
# present) is what lets multiple users stay logged in across different
# apps/tabs at once. This matches current_student()/current_tutor()/
# current_parent(), which already check JWT before session.

def _resolve_jwt():
    """Return the decoded JWT payload from the Authorization header, or None."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        return decode_jwt_token(token)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = _resolve_jwt()
        if payload:
            request.jwt_user = payload
            return f(*args, **kwargs)

        if session.get("user_id"):
            return f(*args, **kwargs)

        return jsonify({"success": False, "message": "Please log in to access this resource."}), 401
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = _resolve_jwt()
            if payload:
                request.jwt_user = payload
                user_role = payload.get("role")
                if user_role in allowed_roles:
                    return f(*args, **kwargs)
                return jsonify({
                    "success": False,
                    "message": "Unauthorized Access: You do not have permission to view this resource."
                }), 403

            if session.get("user_id"):
                user_role = session.get("role")
                if user_role in allowed_roles:
                    return f(*args, **kwargs)
                return jsonify({
                    "success": False,
                    "message": "Unauthorized Access: You do not have permission to view this resource."
                }), 403

            return jsonify({"success": False, "message": "Please log in to access this resource."}), 401
        return decorated_function
    return decorator

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = _resolve_jwt()
        if payload:
            request.jwt_user = payload
            return f(*args, **kwargs)

        if session.get("user_id"):
            return f(*args, **kwargs)

        return jsonify({"success": False, "message": "Valid JWT token or active session required."}), 401
    return decorated

def admin_required(f):
    return role_required("Admin")(f)

def tutor_required(f):
    return role_required("Tutor")(f)

def student_required(f):
    return role_required("Student")(f)

def parent_required(f):
    return role_required("Parent")(f)