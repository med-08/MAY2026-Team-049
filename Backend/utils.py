import re
import jwt
from datetime import datetime, timedelta
from flask import current_app

from models import Admin, Tutor, Student, Parent, Role
from database import db

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validate_registration(name, email, password, confirm_password, role_name):
    """
    Validates the legacy flat single-role registration payload. This path
    now only serves Tutor sign-up: Student and Parent accounts are created
    together through the combined Student+Parent registration flow (see
    `validate_student_with_parent_registration` / `POST /auth/register`
    with a nested `student` object), which prevents duplicate Parent rows
    and always links a Student to its Parent.
    """
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Full Name must be at least 2 characters long.")

    if not email or not EMAIL_REGEX.match(email.strip()):
        errors.append("Please enter a valid email address.")

    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    if role_name not in ["Tutor"]:
        errors.append(
            "Direct registration is only available for Tutor accounts. "
            "Student accounts must be registered together with their "
            "Parent details."
        )

    if email and email_exists_across_roles(email):
        errors.append("Email Already Exists. Please use a different email or log in.")

    return errors


def email_exists_across_roles(email):
    """
    Case-insensitive check for whether an email is already registered
    against ANY role (Admin/Tutor/Student/Parent). Used to keep emails
    unique across the whole platform, e.g. when validating the Student
    email on the combined Student+Parent registration form.
    """
    if not email:
        return False

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

    return bool(tutor_exists or student_exists or parent_exists or admin_exists)


def find_parent_by_email(email):
    """Case-insensitive lookup of a Parent record by email."""
    if not email:
        return None
    clean_email = email.strip().lower()
    return Parent.query.filter(db.func.lower(Parent.email) == clean_email).first()


def validate_student_with_parent_registration(student_data, parent_data, existing_parent):
    """
    Validates the payload for the combined Student + Parent registration
    endpoint (POST /auth/register with a `student` object in the body).

    `existing_parent` should be the Parent row already looked up by email
    (or None). When it is None, the caller is expected to supply full
    Parent details (name/password/phone) which are validated here too.

    Returns a list of human-readable error strings (empty list == valid).
    """
    errors = []

    student_name = (student_data.get('name') or student_data.get('student_name') or '').strip()
    student_email = (student_data.get('email') or '').strip()
    student_password = student_data.get('password', '')
    student_confirm = (
        student_data.get('confirm_password')
        or student_data.get('confirmPassword')
        or student_password
    )
    student_school = (student_data.get('school') or '').strip()
    subject_ids = student_data.get('subject_ids') or student_data.get('subjects') or []

    if not student_name or len(student_name) < 2:
        errors.append("Student Name must be at least 2 characters long.")

    if not student_email or not EMAIL_REGEX.match(student_email):
        errors.append("Please enter a valid Student email address.")
    elif email_exists_across_roles(student_email):
        errors.append("Student Email Already Exists. Please use a different email or log in.")

    if not student_password or len(student_password) < 6:
        errors.append("Student Password must be at least 6 characters long.")

    if student_password != student_confirm:
        errors.append("Student passwords do not match.")

    # School is optional (the registration form labels it as such) - do not
    # block registration on it being blank. It's still stored on the
    # Student row if supplied.
    # Subjects are now mandatory: a student must pick at least one subject
    # at registration time rather than leaving it for later from the
    # profile page.
    if not subject_ids or not isinstance(subject_ids, list):
        errors.append("Please select at least one Subject.")

    parent_email = (parent_data.get('email') or '').strip()
    if not parent_email or not EMAIL_REGEX.match(parent_email):
        errors.append("Please enter a valid Parent email address.")

    if not existing_parent and parent_email and EMAIL_REGEX.match(parent_email):
        parent_name = (parent_data.get('name') or '').strip()
        parent_password = parent_data.get('password', '')
        parent_confirm = (
            parent_data.get('confirm_password')
            or parent_data.get('confirmPassword')
            or parent_password
        )

        if not parent_name or len(parent_name) < 2:
            errors.append("Parent Name must be at least 2 characters long.")

        if not parent_password or len(parent_password) < 6:
            errors.append("Parent Password must be at least 6 characters long.")

        if parent_password != parent_confirm:
            errors.append("Parent passwords do not match.")

        # The Parent email is new (no existing Parent row), so it must not
        # collide with an account of a *different* role either.
        if email_exists_across_roles(parent_email):
            errors.append(
                "Parent Email Already Exists as a different account type. "
                "Please use a different email or log in."
            )

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


