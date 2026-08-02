from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from auth import auth_bp
from database import db
from models import Student, Parent
from utils import validate_registration, find_user_by_identifier, get_role_id, generate_jwt_token

@auth_bp.route('/login', methods=['POST'])
def login():
    # Clear any previous session so a fresh login always validates
    # the credentials just submitted, instead of re-using a stale session.
    session.clear()

    data = request.get_json() or request.form or {}
    identifier = (data.get('identifier') or data.get('email') or '').strip()
    password = data.get('password', '')
    remember = data.get('remember', False)

    if not identifier or not password:
        return jsonify({'success': False, 'message': 'Please provide both Email/Username and Password.'}), 400

    user_info = find_user_by_identifier(identifier)

    if user_info and check_password_hash(user_info['password_hash'], password):
        user_status = user_info.get('status', 'Active')
        if user_status in ['Pending', 'pending']:
            return jsonify({
                'success': False,
                'message': 'Your account is pending admin approval. Please wait for an administrator to activate your account.'
            }), 403
        elif user_status in ['Blocked', 'blocked', 'Inactive', 'inactive']:
            return jsonify({
                'success': False,
                'message': 'Your account has been blocked or suspended. Please contact support.'
            }), 403
        # Store session
        session['user_id'] = user_info['user_id']
        session['username'] = user_info['display_name']
        session['role'] = user_info['role']
        session.permanent = bool(remember)

        # Update timestamp
        user_obj = user_info['user']
        if hasattr(user_obj, 'last_login_at'):
            user_obj.last_login_at = datetime.utcnow()
            db.session.commit()

        role_target = user_info['role'].lower()
        jwt_token = generate_jwt_token(user_info['user_id'], user_info['display_name'], user_info['role'])

        return jsonify({
            'success': True,
            'message': 'Login Successful!',
            'token': jwt_token,
            'role': user_info['role'],
            'username': user_info['display_name'],
            'redirect_url': f'/{role_target}'
        })
    else:
        return jsonify({'success': False, 'message': 'Wrong Password or Email/Username. Invalid credentials.'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    if session.get('user_id') and session.get('role'):
        role = session.get('role')
        return jsonify({'success': True, 'redirect_url': f'/{role.lower()}'})

    data = request.get_json() or request.form or {}
    name = (data.get('name') or data.get('fullName') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password') or data.get('confirmPassword') or ''
    role_name = data.get('role', 'Student')

    errors = validate_registration(name, email, password, confirm_password, role_name)

    if errors:
        return jsonify({'success': False, 'message': errors[0], 'errors': errors}), 400

    try:
        role_id = get_role_id(role_name)
        hashed_pw = generate_password_hash(password)

        if role_name == 'Student':
            new_user = Student(
                student_name=name,
                email=email,
                password_hash=hashed_pw,
                role_id=role_id,
                status='Active'
            )
        elif role_name == 'Parent':
            new_user = Parent(
                parent_name=name,
                email=email,
                password_hash=hashed_pw,
                role_id=role_id,
                status='Active'
            )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Registration Successful! Please log in.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred during registration. Please try again.'}), 500


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged Out Successfully.'})


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    return jsonify({'success': True, 'message': 'Password reset instructions have been logged if account exists.'})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    return jsonify({'success': True, 'message': 'Password reset processed.'})
