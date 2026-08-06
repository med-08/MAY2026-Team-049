import re
import jwt
from datetime import datetime, timedelta
from flask import current_app

from models import Admin, Tutor, Student, Parent, Role
from database import db

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validate_registration(name, email, password, confirm_password, role_name):
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Full Name must be at least 2 characters long.")

    if not email or not EMAIL_REGEX.match(email.strip()):
        errors.append("Please enter a valid email address.")

    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    if role_name not in ["Student", "Parent", "Tutor"]:
        errors.append("Registration is only allowed for Students, Parents, and Tutors.")

    if email:
        clean_email = email.strip().lower()

        tutor_exists = Tutor.query.filter(db.func.lower(Tutor.email) == clean_email).first()
        student_exists = Student.query.filter(db.func.lower(Student.email) == clean_email).first()
        parent_exists = Parent.query.filter(db.func.lower(Parent.email) == clean_email).first()

        admin_exists = None
        try:
            if hasattr(Admin, 'email'):
                admin_exists = Admin.query.filter(db.func.lower(Admin.email) == clean_email).first()
            elif hasattr(Admin, 'username'):
                admin_exists = Admin.query.filter(db.func.lower(Admin.username) == clean_email).first()
        except Exception:
            admin_exists = None

        if tutor_exists or student_exists or parent_exists or admin_exists:
            errors.append("Email Already Exists. Please use a different email or log in.")

    return errors


def find_user_by_identifier(identifier):
    if not identifier:
        return None

    clean_id = identifier.strip().lower()

    # 1. Admin lookup, but safely skip if admin table doesn't exist
    admin = None
    try:
        if hasattr(Admin, 'username'):
            admin = Admin.query.filter(db.func.lower(Admin.username) == clean_id).first()

        if not admin and hasattr(Admin, 'email'):
            admin = Admin.query.filter(db.func.lower(Admin.email) == clean_id).first()
    except Exception:
        admin = None

    if admin:
        return {
            "user": admin,
            "user_id": admin.admin_id,
            "display_name": getattr(admin, "admin_name", getattr(admin, "username", "Admin")),
            "email": getattr(admin, "email", ""),
            "role": "Admin",
            "status": getattr(admin, "status", "Active"),
            "password_hash": admin.password_hash
        }

    # 2. Tutor
    tutor = Tutor.query.filter(
        (db.func.lower(Tutor.email) == clean_id) |
        (db.func.lower(Tutor.tutor_name) == clean_id)
    ).first()

    if tutor:
        return {
            "user": tutor,
            "user_id": tutor.tutor_id,
            "display_name": tutor.tutor_name,
            "email": tutor.email,
            "role": "Tutor",
            "status": getattr(tutor, "status", "Active"),
            "password_hash": tutor.password_hash
        }

    # 3. Student
    student = Student.query.filter(
        (db.func.lower(Student.email) == clean_id) |
        (db.func.lower(Student.student_name) == clean_id)
    ).first()

    if student:
        return {
            "user": student,
            "user_id": student.student_id,
            "display_name": student.student_name,
            "email": student.email,
            "role": "Student",
            "status": getattr(student, "status", "Active"),
            "password_hash": student.password_hash
        }

    # 4. Parent
    parent = Parent.query.filter(
        (db.func.lower(Parent.email) == clean_id) |
        (db.func.lower(Parent.parent_name) == clean_id)
    ).first()

    if parent:
        return {
            "user": parent,
            "user_id": parent.parent_id,
            "display_name": parent.parent_name,
            "email": parent.email,
            "role": "Parent",
            "status": getattr(parent, "status", "Active"),
            "password_hash": parent.password_hash
        }

    return None


def get_role_id(role_name):
    role = Role.query.filter_by(role_name=role_name).first()
    if not role:
        role = Role(role_name=role_name)
        db.session.add(role)
        db.session.commit()
    return role.role_id


def generate_jwt_token(user_id, username, role, expires_in_hours=24):
    secret_key = current_app.config.get('SECRET_KEY', 'learnathome-secret-key-2026')
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def decode_jwt_token(token):
    secret_key = current_app.config.get('SECRET_KEY', 'learnathome-secret-key-2026')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None