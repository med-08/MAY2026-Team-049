from functools import wraps
from flask import session, request, jsonify
from utils import decode_jwt_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_jwt_token(token)
            if payload:
                request.jwt_user = payload
                return f(*args, **kwargs)

        return jsonify({"success": False, "message": "Please log in to access this resource."}), 401
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("user_id"):
                user_role = session.get("role")
                if user_role in allowed_roles:
                    return f(*args, **kwargs)
                return jsonify({
                    "success": False,
                    "message": "Unauthorized Access: You do not have permission to view this resource."
                }), 403

            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_jwt_token(token)
                if payload:
                    request.jwt_user = payload
                    user_role = payload.get("role")
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
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_jwt_token(token)
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