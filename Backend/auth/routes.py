from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from auth import auth_bp
from database import db
from models import Student, Parent, Tutor, Subject, StudentSubject
from utils import validate_registration, find_user_by_identifier, get_role_id, generate_jwt_token


@auth_bp.route('/subjects', methods=['GET'])
def list_subjects():
    subjects = Subject.query.order_by(Subject.subject_name).all()
    return jsonify({
        'success': True,
        'data': [{'subject_id': s.subject_id, 'subject_name': s.subject_name} for s in subjects]
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    session.clear()

    try:
        data = request.get_json(silent=True) or request.form or {}
        identifier = (data.get('identifier') or data.get('email') or '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)

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
            return jsonify({
                'success': True,
                'redirect_url': f'/{role.lower()}'
            }), 200

        data = request.get_json(silent=True) or request.form or {}
        name = (data.get('name') or data.get('fullName') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password') or data.get('confirmPassword') or ''
        role_name = (data.get('role') or 'Student').strip()
        subject_ids = data.get('subject_ids') or data.get('subjects') or []

        errors = validate_registration(name, email, password, confirm_password, role_name)

        if errors:
            return jsonify({
                'success': False,
                'message': errors[0],
                'errors': errors
            }), 400

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
        elif role_name == 'Tutor':
            new_user = Tutor(
                tutor_name=name,
                email=email,
                password_hash=hashed_pw,
                role_id=role_id,
                phone_no=data.get('phone_no') or data.get('phone'),
                experience_years=data.get('experience_years') or 0,
                bio=data.get('bio', ''),
                hourly_rate=data.get('hourly_rate', ''),
                status='Pending'
            )
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid role specified.'
            }), 400

        db.session.add(new_user)
        db.session.commit()

        if role_name == 'Student' and subject_ids:
            valid_ids = {
                sid for (sid,) in db.session.query(Subject.subject_id)
                .filter(Subject.subject_id.in_(subject_ids))
                .all()
            }
            for sid in valid_ids:
                db.session.add(StudentSubject(student_id=new_user.student_id, subject_id=sid))
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registration Successful! Please log in.'
        }), 201

    except Exception as e:
        db.session.rollback()
        print("REGISTER ERROR:", str(e))
        return jsonify({
            'success': False,
            'message': f'An error occurred during registration: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged Out Successfully.'
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    return jsonify({
        'success': True,
        'message': 'Password reset instructions have been logged if account exists.'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    return jsonify({
        'success': True,
        'message': 'Password reset processed.'
    }), 200