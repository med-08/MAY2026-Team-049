from flask import Blueprint, jsonify, request
from database import db
from models import Parent, Student, WeeklySummary, QuizAttempt, AttendanceRecord, TeachingPlan, MeetingRequest, Tutor
from decorators import parent_required
from datetime import datetime, date

# Define Blueprint
from parent import parent_bp


@parent_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Parent API blueprint working!"}), 200


# -------------------------------------------------------------------
# 1. GET PARENT PROFILE
# -------------------------------------------------------------------
@parent_bp.route('/profile/<int:parent_id>', methods=['GET'])
@parent_required
def get_parent_profile(parent_id):
    parent = db.session.get(Parent, parent_id)
    if not parent:
        return jsonify({"status": "error", "message": "Parent not found"}), 404

    children = Student.query.filter_by(parent_id=parent_id).all()
    children_list = [{
        "student_id": child.student_id,
        "student_name": getattr(child, 'student_name', 'N/A'),
        "email": getattr(child, 'email', 'N/A'),
        "status": getattr(child, 'status', 'Pending')
    } for child in children]

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
# 3. GET PARENT DASHBOARD OVERVIEW  ← REAL DB VERSION
# -------------------------------------------------------------------
@parent_bp.route('/overview/<int:parent_id>', methods=['GET'])
@parent_required
def get_parent_overview(parent_id):
    parent = db.session.get(Parent, parent_id)
    if not parent:
        return jsonify({"status": "error", "message": "Parent not found"}), 404

    children = Student.query.filter_by(parent_id=parent_id).all()
    children_summary = [{
        "student_id": child.student_id,
        "student_name": getattr(child, 'student_name', 'N/A'),
        "status": getattr(child, 'status', 'Active')
    } for child in children]

    # Get latest weekly summary for any child (most recent)
    latest_summary = WeeklySummary.query.filter(
        WeeklySummary.student_id.in_([c.student_id for c in children])
    ).order_by(WeeklySummary.created_at.desc()).first()

    latest = {
        "topics_taught": latest_summary.topics_taught if latest_summary else "No summary yet",
        "homework": latest_summary.homework_summary if latest_summary else "No homework recorded",
        "areas_for_improvement": latest_summary.areas_for_improvement if latest_summary else "No remarks yet"
    }

    return jsonify({
        "status": "success",
        "data": {
            "parent_id": parent.parent_id,
            "parent_name": getattr(parent, 'parent_name', 'N/A'),
            "total_children": len(children_summary),
            "children": children_summary,
            "latest_summary": latest
        }
    }), 200


# -------------------------------------------------------------------
# 4. REQUEST MEETING WITH TUTOR  ← NOW SAVES TO DB
# -------------------------------------------------------------------
@parent_bp.route('/meeting-request', methods=['POST'])
@parent_required
def request_meeting():
    data = request.get_json() or {}

    required = ['parent_id', 'tutor_id', 'student_id', 'preferred_date', 'preferred_time']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    try:
        meeting_date = datetime.strptime(f"{data['preferred_date']} {data['preferred_time']}", "%Y-%m-%d %H:%M")

        new_request = MeetingRequest(
            tutor_id=data['tutor_id'],
            student_id=data['student_id'],
            parent_id=data['parent_id'],
            meeting_date=meeting_date,
            meeting_reason=data.get('notes', ''),
            status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Meeting request submitted successfully!",
            "data": {
                "meeting_id": new_request.meeting_id,
                "parent_id": new_request.parent_id,
                "tutor_id": new_request.tutor_id,
                "student_id": new_request.student_id,
                "meeting_date": new_request.meeting_date.isoformat(),
                "status": new_request.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------------------------------------------
# 5. GET CHILD PROGRESS & PERFORMANCE  ← REAL DB VERSION
# -------------------------------------------------------------------
@parent_bp.route('/child-progress/<int:parent_id>/<int:student_id>', methods=['GET'])
@parent_required
def get_child_progress(parent_id, student_id):
    child = db.session.get(Student, student_id)
    if not child or child.parent_id != parent_id:
        return jsonify({"status": "error", "message": "Child not found for this parent"}), 404

    # Attendance
    attendance_records = AttendanceRecord.query.filter_by(student_id=student_id).all()
    present = sum(1 for a in attendance_records if a.status == 'Present')
    total = len(attendance_records)
    attendance_rate = f"{round((present / total) * 100)}%" if total > 0 else "N/A"

    # Recent quiz scores
    recent_quizzes = QuizAttempt.query.filter(
        QuizAttempt.student_id == student_id
    ).order_by(QuizAttempt.attempted_at.desc()).limit(5).all()

    quiz_scores = []
    for attempt in recent_quizzes:
        quiz_scores.append({
            "subject": "Mathematics",  # You can enhance with subject join later
            "topic": "Quiz",
            "score": f"{attempt.score}/100" if attempt.score else "N/A",
            "date": attempt.attempted_at.strftime("%Y-%m-%d")
        })

    # Tutor remarks from WeeklySummary
    remarks = WeeklySummary.query.filter_by(student_id=student_id).order_by(WeeklySummary.created_at.desc()).limit(3).all()
    tutor_remarks = [{
        "tutor_name": "Tutor",
        "subject": "General",
        "remark": r.areas_for_improvement or r.topics_taught,
        "date": r.created_at.strftime("%Y-%m-%d")
    } for r in remarks]

    return jsonify({
        "status": "success",
        "data": {
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "attendance_rate": attendance_rate,
            "recent_quiz_scores": quiz_scores,
            "tutor_remarks": tutor_remarks
        }
    }), 200


# -------------------------------------------------------------------
# 6. GET CURRICULUM PLAN FOR CHILD  ← REAL DB VERSION
# -------------------------------------------------------------------
@parent_bp.route('/curriculum/<int:student_id>', methods=['GET'])
@parent_required
def get_child_curriculum(student_id):
    child = db.session.get(Student, student_id)
    if not child:
        return jsonify({"status": "error", "message": "Child not found"}), 404

    plans = TeachingPlan.query.filter_by(student_id=student_id).order_by(TeachingPlan.planned_date).all() if hasattr(TeachingPlan, 'student_id') else []

    curriculum = []
    for plan in plans:
        curriculum.append({
            "month": plan.month,
            "subject": "Subject",   # Enhance with subject join if needed
            "topics": [plan.topic_name],
            "status": "In Progress"
        })

    if not curriculum:
        curriculum = [{"month": "August 2026", "subject": "Mathematics", "topics": ["No curriculum data yet"], "status": "Planned"}]

    return jsonify({
        "status": "success",
        "data": {
            "student_id": child.student_id,
            "student_name": getattr(child, 'student_name', 'N/A'),
            "curriculum_plan": curriculum
        }
    }), 200