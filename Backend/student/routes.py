from flask import jsonify, session
from student import student_bp
from decorators import student_required
from models import StudentSubject, AssignmentSubmission, QuizAttempt

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session.get('user_id')
    stats = {
        "enrolled_subjects": StudentSubject.query.filter_by(student_id=student_id).count() if student_id else 0,
        "submissions_count": AssignmentSubmission.query.filter_by(student_id=student_id).count() if student_id else 0,
        "quiz_attempts": QuizAttempt.query.filter_by(student_id=student_id).count() if student_id else 0
    }
    return jsonify({"success": True, "stats": stats})
