import re
from werkzeug.security import generate_password_hash, check_password_hash
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
        
    if role_name not in ["Student", "Parent"]:
        errors.append("Registration is currently only allowed for Students and Parents.")

    # Check email uniqueness across models that have email
    if email:
        clean_email = email.strip().lower()
        if Tutor.query.filter(db.func.lower(Tutor.email) == clean_email).first() or \
           Student.query.filter(db.func.lower(Student.email) == clean_email).first() or \
           Parent.query.filter(db.func.lower(Parent.email) == clean_email).first():
            errors.append("Email Already Exists. Please use a different email or log in.")

    return errors

def find_user_by_identifier(identifier):
    """
    Search across Admin, Tutor, Student, Parent models for an email or username match.
    Returns dict with keys: 'user', 'user_id', 'display_name', 'email', 'role', 'password_hash' or None.
    """
    if not identifier:
        return None
    
    clean_id = identifier.strip().lower()

    # 1. Check Admin (by username or email aliases)
    admin = Admin.query.filter((db.func.lower(Admin.username) == clean_id)).first()
    if not admin and (clean_id in ['admin', 'admin@gmail.com', 'admin@example.com'] or clean_id.startswith('admin@')):
        admin = Admin.query.filter_by(username='admin').first()
        
    if admin:
        return {
            "user": admin,
            "user_id": admin.admin_id,
            "display_name": admin.username,
            "email": getattr(admin, "email", "admin@gmail.com"),
            "role": "Admin",
            "status": "Active",
            "password_hash": admin.password_hash
        }

    # 2. Check Tutor (by email or tutor_name)
    tutor = Tutor.query.filter((db.func.lower(Tutor.email) == clean_id) | (db.func.lower(Tutor.tutor_name) == clean_id)).first()
    if not tutor and clean_id in ['tutor@gmail.com', 'tutor@example.com']:
        tutor = Tutor.query.filter_by(email='tutor@example.com').first()
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

    # 3. Check Student (by email or student_name)
    student = Student.query.filter((db.func.lower(Student.email) == clean_id) | (db.func.lower(Student.student_name) == clean_id)).first()
    if not student and clean_id in ['student@gmail.com', 'student@example.com']:
        student = Student.query.filter_by(email='student@example.com').first()
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

    # 4. Check Parent (by email or parent_name)
    parent = Parent.query.filter((db.func.lower(Parent.email) == clean_id) | (db.func.lower(Parent.parent_name) == clean_id)).first()
    if not parent and clean_id in ['parent@gmail.com', 'parents@gmail.com', 'parent@example.com']:
        parent = Parent.query.filter_by(email='parent@example.com').first()
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

import jwt
from datetime import datetime, timedelta
from flask import current_app

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
