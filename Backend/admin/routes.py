from flask import jsonify
from admin import admin_bp
from decorators import admin_required
from models import Student, Tutor, Parent, Admin

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        "students_count": Student.query.count(),
        "tutors_count": Tutor.query.count(),
        "parents_count": Parent.query.count(),
        "admins_count": Admin.query.count()
    }
    return jsonify({"success": True, "stats": stats})
