from flask import jsonify, session
from tutor import tutor_bp
from decorators import tutor_required
from models import Session, Assignment, Quiz

@tutor_bp.route('/dashboard')
@tutor_required
def dashboard():
    tutor_id = session.get('user_id')
    stats = {
        "sessions_count": Session.query.filter_by(tutor_id=tutor_id).count() if tutor_id else 0,
        "assignments_count": Assignment.query.count(),
        "quizzes_count": Quiz.query.filter_by(tutor_id=tutor_id).count() if tutor_id else 0
    }
    return jsonify({"success": True, "stats": stats})
