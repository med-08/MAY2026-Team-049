import json

from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from auth import auth_bp
from database import db
from models import Student, Parent, Tutor, Subject, StudentSubject
from utils import (
    validate_registration,
    validate_student_with_parent_registration,
    find_parent_by_email,
    find_user_by_identifier,
    get_role_id,
    generate_jwt_token,
    EMAIL_REGEX,
)


@auth_bp.route('/subjects', methods=['GET'])
def list_subjects():
    subjects = Subject.query.order_by(Subject.subject_name).all()
    return jsonify({
        'success': True,
        'data': [{'subject_id': s.subject_id, 'subject_name': s.subject_name} for s in subjects]
    }), 200


@auth_bp.route('/check-parent-email', methods=['GET'])
def check_parent_email():
    """
    Used by the combined Student + Parent registration form to look up a
    Parent by email as the user types it, so the UI can either confirm the
    existing parent account or reveal the "new parent" fields.
    """
    email = (request.args.get('email') or '').strip()

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email address.'
        }), 400

    parent = find_parent_by_email(email)

    if parent:
        return jsonify({
            'success': True,
            'exists': True,
            'parent': {
                'parent_id': parent.parent_id,
                'parent_name': parent.parent_name,
                'email': parent.email
            }
        }), 200

    return jsonify({
        'success': True,
        'exists': False
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    session.clear()

    try:
        data = request.get_json(silent=True) or request.form or {}
        identifier = (data.get('identifier') or data.get('email') or '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        requested_role = (data.get('role') or '').strip()

        if not identifier or not password:
            return jsonify({
                'success': False,
                'message': 'Please provide both Email/Username and Password.'
            }), 400

        user_info = find_user_by_identifier(identifier)

        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Wrong Password or Email/Username. Invalid credentials.'
            }), 401

        stored_hash = user_info.get('password_hash')
        if not stored_hash or not check_password_hash(stored_hash, password):
            return jsonify({
                'success': False,
                'message': 'Wrong Password or Email/Username. Invalid credentials.'
            }), 401

        # The role selected on the login screen is a safety check. The
        # database remains authoritative, so selecting Tutor cannot turn a
        # Student account into a Tutor account (or vice versa).
        if requested_role and requested_role.lower() != user_info['role'].lower():
            return jsonify({
                'success': False,
                'message': (
                    f"This account is registered as {user_info['role']}. "
                    f"Please select {user_info['role']} on the login screen."
                ),
                'actual_role': user_info['role']
            }), 403

        user_status = user_info.get('status', 'Active')
        if user_status in ['Pending', 'pending']:
            return jsonify({
                'success': False,
                'message': 'Your account is pending admin approval. Please wait for an administrator to activate your account.'
            }), 403

        if user_status in ['Blocked', 'blocked', 'Inactive', 'inactive']:
            return jsonify({
                'success': False,
                'message': 'Your account has been blocked or suspended. Please contact support.'
            }), 403

        session['user_id'] = user_info['user_id']
        session['username'] = user_info['display_name']
        session['role'] = user_info['role']
        session.permanent = bool(remember)

        user_obj = user_info['user']
        if hasattr(user_obj, 'last_login_at'):
            user_obj.last_login_at = datetime.utcnow()
            db.session.commit()

        role_target = user_info['role'].lower()
        jwt_token = generate_jwt_token(
            user_info['user_id'],
            user_info['display_name'],
            user_info['role']
        )

        response_data = {
            'success': True,
            'message': 'Login Successful!',
            'token': jwt_token,
            'role': user_info['role'],
            'username': user_info['display_name'],
            'user_id': user_info['user_id'],
            'redirect_url': f'/{role_target}'
        }

        if user_info['role'] == 'Parent' and hasattr(user_obj, 'parent_id'):
            response_data['parent_id'] = user_obj.parent_id

        if user_info['role'] == 'Student' and hasattr(user_obj, 'student_id'):
            response_data['student_id'] = user_obj.student_id

        if user_info['role'] == 'Tutor' and hasattr(user_obj, 'tutor_id'):
            response_data['tutor_id'] = user_obj.tutor_id

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print("LOGIN ERROR:", str(e))
        return jsonify({
            'success': False,
            'message': f'Login failed due to server error: {str(e)}'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        if session.get('user_id') and session.get('role'):
            role = session.get('role')
            username = session.get('username', 'a user')
            # Previously this silently returned success:true with no
            # account created, which the frontend displayed as "Registration
            # Successful!" even though nothing was actually registered.
            # Return an explicit, honest error instead so the user knows
            # they need to log out before creating a different account.
            return jsonify({
                'success': False,
                'already_logged_in': True,
                'message': (
                    f"You're already logged in as {username} ({role}). "
                    "Please log out before creating a new account."
                ),
                'role': role,
                'redirect_url': f'/{role.lower()}'
            }), 409

        data = request.get_json(silent=True) or request.form or {}

        # Combined Student + Parent registration: the request body carries a
        # nested `student` object (and, optionally, a `parent` object). This
        # is the path used by the current registration form for the Student
        # role, which replaces the old separate Parent Registration form.
        if isinstance(data.get('student'), dict):
            return _register_student_with_parent(data)

        # Legacy flat single-role registration. Student and Parent accounts
        # can no longer be created through this path (see
        # validate_registration) - it now only serves Tutor sign-up, which
        # this change did not touch.
        name = (data.get('name') or data.get('fullName') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password') or data.get('confirmPassword') or ''
        role_name = (data.get('role') or 'Tutor').strip()

        errors = validate_registration(name, email, password, confirm_password, role_name)

        if errors:
            return jsonify({
                'success': False,
                'message': errors[0],
                'errors': errors
            }), 400

        role_id = get_role_id(role_name)
        hashed_pw = generate_password_hash(password)

        # Subjects: the registration form sends subject_ids (from the same
        # subject picker used by Student sign-up). Tutors are matched against
        # subjects_json by subject NAME elsewhere (see parent/routes.py and
        # tutor/routes.py profile), so resolve ids -> names here.
        subject_ids = data.get('subject_ids') or []
        subject_names = []
        if isinstance(subject_ids, list) and subject_ids:
            rows = Subject.query.filter(Subject.subject_id.in_(subject_ids)).all()
            subject_names = [s.subject_name for s in rows]

        # Teaching languages: accept either a list (["English", "Hindi"]) or
        # a comma-separated string ("English, Hindi").
        languages = data.get('languages') or data.get('teaching_languages') or []
        if isinstance(languages, str):
            languages = [lang.strip() for lang in languages.split(',') if lang.strip()]
        elif not isinstance(languages, list):
            languages = []

        try:
            experience_years = int(data.get('experience_years') or 0)
        except (TypeError, ValueError):
            experience_years = 0

        new_user = Tutor(
            tutor_name=name,
            email=email,
            password_hash=hashed_pw,
            role_id=role_id,
            phone_no=data.get('phone_no') or data.get('phone'),
            experience_years=experience_years,
            bio=data.get('bio', ''),
            education=data.get('education', ''),
            hourly_rate=data.get('hourly_rate', ''),
            availability=data.get('availability', ''),
            subjects_json=json.dumps(subject_names),
            languages_json=json.dumps(languages),
            status='Pending'
        )

        db.session.add(new_user)
        db.session.commit()

        pending_message = (
            'Registration Successful! Your account is pending admin approval. '
            'You will be able to log in once an administrator approves it.'
        )
        return jsonify({
            'success': True,
            'message': pending_message
        }), 201

    except Exception as e:
        db.session.rollback()
        print("REGISTER ERROR:", str(e))
        return jsonify({
            'success': False,
            'message': f'An error occurred during registration: {str(e)}'
        }), 500


def _register_student_with_parent(data):
    """
    Combined Student + Parent registration.

    Expected body:
    {
      "student": {"name", "email", "password", "confirm_password", "phone_no"?, "school", "subject_ids"},
      "parent":  {"email", "name"?, "password"?, "confirm_password"?, "phone_no"?}
    }

    "school" and "subject_ids" are required (subject_ids must contain at
    least one subject id) - see validate_student_with_parent_registration.

    - Looks up the Parent by email.
    - If found: reuses that parent_id, never creates a second Parent row.
    - If not found: creates a new Parent using the supplied details.
    - Both the (possible) Parent creation and the Student creation happen
      in a single DB transaction, so a Student is never left pointing at
      an invalid parent_id if something goes wrong partway through.
    """
    student_data = data.get('student') or {}
    parent_data = data.get('parent') or {}

    parent_email = (parent_data.get('email') or '').strip()
    existing_parent = find_parent_by_email(parent_email) if parent_email else None

    errors = validate_student_with_parent_registration(student_data, parent_data, existing_parent)

    if errors:
        return jsonify({
            'success': False,
            'message': errors[0],
            'errors': errors
        }), 400

    student_name = (student_data.get('name') or student_data.get('student_name') or '').strip()
    student_email = (student_data.get('email') or '').strip()
    student_password = student_data.get('password', '')
    student_phone = student_data.get('phone_no') or student_data.get('phone')
    student_school = (student_data.get('school') or '').strip()
    subject_ids = student_data.get('subject_ids') or student_data.get('subjects') or []

    try:
        creating_new_parent = existing_parent is None

        if creating_new_parent:
            parent_role_id = get_role_id('Parent')
            parent_obj = Parent(
                parent_name=(parent_data.get('name') or '').strip(),
                email=parent_email,
                phone_no=parent_data.get('phone_no') or parent_data.get('phone'),
                password_hash=generate_password_hash(parent_data.get('password', '')),
                role_id=parent_role_id,
                status='Pending'
            )
            # flush (not commit) so parent_obj.parent_id is generated but the
            # row is only made durable together with the Student below.
            db.session.add(parent_obj)
            db.session.flush()
            resolved_parent = parent_obj
        else:
            resolved_parent = existing_parent

        student_role_id = get_role_id('Student')
        new_student = Student(
            student_name=student_name,
            email=student_email,
            password_hash=generate_password_hash(student_password),
            role_id=student_role_id,
            phone_no=student_phone,
            school=student_school,
            parent_id=resolved_parent.parent_id,
            status='Pending'
        )
        db.session.add(new_student)
        db.session.flush()

        if subject_ids:
            valid_ids = {
                sid for (sid,) in db.session.query(Subject.subject_id)
                .filter(Subject.subject_id.in_(subject_ids))
                .all()
            }
            for sid in valid_ids:
                db.session.add(StudentSubject(student_id=new_student.student_id, subject_id=sid))

        # Single commit: Parent (if new) + Student + subject links all
        # succeed or all roll back together.
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("REGISTER ERROR:", str(e))
        return jsonify({
            'success': False,
            'message': f'An error occurred during registration: {str(e)}'
        }), 500

    pending_message = (
        'Registration Successful! Your account is pending admin approval. '
        'You will be able to log in once an administrator approves it.'
    )
    return jsonify({
        'success': True,
        'message': pending_message,
        'parent': {
            'parent_id': resolved_parent.parent_id,
            'parent_name': resolved_parent.parent_name,
            'email': resolved_parent.email,
            'newly_created': creating_new_parent
        }
    }), 201


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged Out Successfully.'
    }), 200


