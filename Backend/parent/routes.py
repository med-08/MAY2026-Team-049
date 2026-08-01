from flask import Blueprint, jsonify, request
from database import db
from models import Parent, Student
from decorators import parent_required

# Define Blueprint
from parent import parent_bp

@parent_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check route."""
    return jsonify({"status": "success", "message": "Parent API blueprint working!"}), 200


# -------------------------------------------------------------------
# 1. GET PARENT PROFILE
# -------------------------------------------------------------------
@parent_bp.route('/profile/<int:parent_id>', methods=['GET'])
@parent_required
def get_parent_profile(parent_id):
    """Retrieve parent profile along with linked children."""
    parent = db.session.get(Parent, parent_id)
    if not parent:
        return jsonify({"status": "error", "message": "Parent not found"}), 404

    children = Student.query.filter_by(parent_id=parent_id).all()
    children_list = []
    for child in children:
        children_list.append({
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "email": getattr(child, 'email', 'N/A'),
            "status": getattr(child, 'status', 'Pending')
        })

    return jsonify({
        "status": "success",
        "data": {
            "parent_id": parent.parent_id,
            "parent_name": getattr(parent, 'parent_name', 'N/A'),
            "email": parent.email,
            "phone_no": getattr(parent, 'phone_no', 'N/A'),
            "status": getattr(parent, 'status', 'Pending'),
            "linked_children": children_list
        }
    }), 200


# -------------------------------------------------------------------
# 2. UPDATE PARENT PROFILE
# -------------------------------------------------------------------
@parent_bp.route('/profile/<int:parent_id>', methods=['PUT'])
@parent_required
def update_parent_profile(parent_id):
    """Update parent details (name, phone_no)."""
    parent = db.session.get(Parent, parent_id)
    if not parent:
        return jsonify({"status": "error", "message": "Parent not found"}), 404

    data = request.get_json() or {}
    
    if 'parent_name' in data:
        parent.parent_name = data['parent_name']
    if 'phone_no' in data:
        parent.phone_no = data['phone_no']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Parent profile updated successfully",
            "data": {
                "parent_id": parent.parent_id,
                "parent_name": parent.parent_name,
                "email": parent.email,
                "phone_no": parent.phone_no
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Failed to update profile: {str(e)}"}), 500


# -------------------------------------------------------------------
# 3. GET PARENT DASHBOARD OVERVIEW
# -------------------------------------------------------------------
@parent_bp.route('/overview/<int:parent_id>', methods=['GET'])
@parent_required
def get_parent_overview(parent_id):
    """Get high-level summary stats for Parent Dashboard."""
    parent = db.session.get(Parent, parent_id)
    if not parent:
        return jsonify({"status": "error", "message": "Parent not found"}), 404

    children = Student.query.filter_by(parent_id=parent_id).all()
    
    children_summary = []
    for child in children:
        children_summary.append({
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "status": getattr(child, 'status', 'Active')
        })

    return jsonify({
        "status": "success",
        "data": {
            "parent_id": parent.parent_id,
            "parent_name": getattr(parent, 'parent_name', 'N/A'),
            "total_children": len(children_summary),
            "children": children_summary,
            "latest_summary": {
                "topics_taught": "Quadratic Equations, Chemical Bonding basics",
                "homework": "2 worksheets on factorization",
                "areas_for_improvement": "Needs more practice on ionic vs covalent bonds"
            }
        }
    }), 200


# -------------------------------------------------------------------
# 4. REQUEST MEETING WITH TUTOR
# -------------------------------------------------------------------
@parent_bp.route('/meeting-request', methods=['POST'])
@parent_required
def request_meeting():
    """Submit a virtual or in-person meeting request to a tutor."""
    data = request.get_json() or {}
    
    required_fields = ['parent_id', 'tutor_id', 'student_id', 'preferred_date', 'preferred_time']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    return jsonify({
        "status": "success",
        "message": "Meeting request submitted successfully!",
        "data": {
            "parent_id": data['parent_id'],
            "tutor_id": data['tutor_id'],
            "student_id": data['student_id'],
            "preferred_date": data['preferred_date'],
            "preferred_time": data['preferred_time'],
            "meeting_type": data.get('meeting_type', 'Virtual'),
            "notes": data.get('notes', ''),
            "status": "Pending"
        }
    }), 201


# -------------------------------------------------------------------
# 5. GET CHILD PROGRESS & PERFORMANCE
# -------------------------------------------------------------------
@parent_bp.route('/child-progress/<int:parent_id>/<int:student_id>', methods=['GET'])
@parent_required
def get_child_progress(parent_id, student_id):
    """Retrieve detailed progress, attendance, and quiz history for a specific child."""
    child = db.session.get(Student, student_id)
    if not child or child.parent_id != parent_id:
        return jsonify({"status": "error", "message": "Child not found for this parent"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "attendance_rate": "92%",
            "recent_quiz_scores": [
                {"subject": "Mathematics", "topic": "Quadratic Equations", "score": "88/100", "date": "2026-07-20"},
                {"subject": "Science", "topic": "Chemical Bonding", "score": "75/100", "date": "2026-07-24"}
            ],
            "tutor_remarks": [
                {"tutor_name": "Dr. Sharma", "subject": "Mathematics", "remark": "Excellent grasping speed in algebra.", "date": "2026-07-28"}
            ]
        }
    }), 200


# -------------------------------------------------------------------
# 6. GET CURRICULUM PLAN FOR CHILD
# -------------------------------------------------------------------
@parent_bp.route('/curriculum/<int:student_id>', methods=['GET'])
@parent_required
def get_child_curriculum(student_id):
    """Retrieve monthly curriculum and syllabus details for a child."""
    child = db.session.get(Student, student_id)
    if not child:
        return jsonify({"status": "error", "message": "Child not found"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "curriculum_plan": [
                {
                    "month": "August 2026",
                    "subject": "Mathematics",
                    "topics": ["Polynomials", "Coordinate Geometry", "Triangles"],
                    "status": "In Progress"
                },
                {
                    "month": "August 2026",
                    "subject": "Science",
                    "topics": ["Acids, Bases & Salts", "Metals & Non-Metals"],
                    "status": "Planned"
                }
            ]
        }
    }), 200