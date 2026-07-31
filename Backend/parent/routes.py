from flask import jsonify, session
from parent import parent_bp
from decorators import parent_required
from models import Student, Notification

@parent_bp.route('/dashboard')
@parent_required
def dashboard():
    parent_id = session.get('user_id')
    children = Student.query.filter_by(parent_id=parent_id).all() if parent_id else []
    notifications = Notification.query.filter_by(recipient_type='Parent', recipient_id=parent_id).all() if parent_id else []
    
    stats = {
        "children_count": len(children),
        "notifications_count": len(notifications)
    }
    return jsonify({"success": True, "stats": stats})
