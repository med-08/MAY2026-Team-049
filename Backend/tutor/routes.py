import json
import os
from datetime import datetime, date, time

from flask import jsonify, request, session, current_app, send_from_directory
from werkzeug.utils import secure_filename

from tutor import tutor_bp
from decorators import tutor_required
from database import db
from models import (
    Tutor,
    Student,
    Parent,
    Session,
    SessionUpdate,
    Assignment,
    AssignmentSubmission,
    StudyResource,
    FAQ,
    Doubt,
    AttendanceRecord,
    Message,
    Notification,
    MeetingRequest,
    Subject,
    Quiz,
    QuizQuestion,
    QuizAttempt,
    LearningProgress,
    StudentSubject,
    SessionBooking,
)
from utils import decode_jwt_token
from google_meet import create_meeting_space, GoogleMeetNotConfigured


ALLOWED_UPLOADS = {
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "txt",
    "png",
    "jpg",
    "jpeg",
    "mp4",
    "webm",
}


# =========================================================
# AUTH / HELPERS
# =========================================================

def current_tutor():
    auth = request.headers.get("Authorization", "")

    if auth.startswith("Bearer "):
        payload = decode_jwt_token(auth.split(" ", 1)[1])

        if payload and payload.get("role") == "Tutor":
            obj = db.session.get(Tutor, payload.get("user_id"))

            if obj:
                return obj

    uid = session.get("user_id")

    if uid and session.get("role") == "Tutor":
        return db.session.get(Tutor, uid)

    return None


def ok(data=None, message=None, status=200):
    payload = {"success": True}

    if message is not None:
        payload["message"] = message

    if data is not None:
        payload.update(data)

    return jsonify(payload), status


def fail(message, status=400):
    return jsonify({
        "success": False,
        "message": message
    }), status


def subject_name(subject_id):
    subject = db.session.get(Subject, subject_id)

    if subject:
        return subject.subject_name

    return "General"


# =========================================================
# SESSION FORMATTER
# =========================================================

def session_item(s):
    subject = db.session.get(Subject, s.subject_id)

    bookings = SessionBooking.query.filter_by(
        session_id=s.session_id
    ).all()

    return {
        "id": s.session_id,
        "sessionId": f"sess-{s.session_id:03d}",

        "subject": (
            subject.subject_name
            if subject
            else "General"
        ),

        "subjectId": s.subject_id,

        "classLevel": (
            s.session_type
            or "Regular"
        ),

        "date": s.session_date.isoformat(),

        "time": s.start_time.strftime("%I:%M %p"),

        "endTime": s.end_time.strftime("%I:%M %p"),

        "summary": (
            f"{len(bookings)} booked · {s.status}"
        ),

        "status": (
            "done"
            if s.status == "Completed"
            else "live"
            if s.status == "Scheduled"
            else "done"
        ),

        "badge": (
            "Done"
            if s.status == "Completed"
            else s.status
        ),

        "action": (
            "Start class"
            if s.status == "Scheduled"
            else None
        ),

        "meeting_url": s.meeting_url,
        "meetingUrl": s.meeting_url,
    }


# =========================================================
# STUDENT FORMATTER
# =========================================================

def student_item(st):
    subject_ids = {
        x.subject_id
        for x in StudentSubject.query.filter_by(
            student_id=st.student_id
        ).all()
    }

    tutor = current_tutor()

    if not tutor:
        return None

    tutor_sessions = Session.query.filter_by(
        tutor_id=tutor.tutor_id
    ).all()

    relevant = [
        s for s in tutor_sessions
        if s.subject_id in subject_ids
    ]

    if not relevant:
        return None

    scores = []

    for s in relevant:
        progress_rows = LearningProgress.query.filter_by(
            student_id=st.student_id,
            session_id=s.session_id
        ).all()

        for p in progress_rows:
            if p.session_completion_status == "Completed":
                scores.append(100)

            elif p.session_completion_status == "Partially Completed":
                scores.append(50)

    attempts = QuizAttempt.query.filter_by(
        student_id=st.student_id
    ).all()

    quiz_scores = []

    for attempt in attempts:
        quiz = db.session.get(
            Quiz,
            attempt.quiz_id
        )

        if (
            attempt.score is not None
            and quiz
            and quiz.tutor_id == tutor.tutor_id
        ):
            quiz_scores.append(
                float(attempt.score)
            )

    avg = (
        round(sum(quiz_scores) / len(quiz_scores))
        if quiz_scores
        else 0
    )

    parent = (
        db.session.get(Parent, st.parent_id)
        if st.parent_id
        else None
    )

    return {
        "studentId": st.student_id,
        "userId": st.student_id,
        "parentId": st.parent_id,

        "name": st.student_name,

        "initials": "".join(
            p[0]
            for p in st.student_name.split()[:2]
        ).upper(),

        "classLevel": st.school or "",

        "subjects": ", ".join(
            sorted(
                subject_name(x)
                for x in subject_ids
            )
        ) or "",

        "parent": (
            {
                "name": parent.parent_name,
                "phone": parent.phone_no,
                "email": parent.email,
            }
            if parent
            else None
        ),

        "progress": {
            "completedTopics": (
                round(sum(scores) / len(scores))
                if scores
                else 0
            ),

            "weeklyScore": avg,

            "learningPace": (
                "Not recorded"
                if not scores
                else "Average"
            ),
        },
    }


# =========================================================
# DASHBOARD
# =========================================================

@tutor_bp.route("/dashboard", methods=["GET"])
@tutor_required
def dashboard():

    tutor = current_tutor()

    if not tutor:
        return fail("Tutor not found", 404)

    tid = tutor.tutor_id

    sessions = (
        Session.query
        .filter_by(tutor_id=tid)
        .order_by(
            Session.session_date,
            Session.start_time
        )
        .all()
    )

    student_ids = {
        booking.student_id
        for s in sessions
        for booking in SessionBooking.query.filter_by(
            session_id=s.session_id
        ).all()
    }

    open_doubts = Doubt.query.filter_by(
        tutor_id=tid,
        status="Open"
    ).count()

    pending = (
        AssignmentSubmission.query
        .join(Assignment)
        .join(Session)
        .filter(
            Session.tutor_id == tid,
            AssignmentSubmission.status.in_(
                ["Pending", "In Progress", "Late"]
            )
        )
        .count()
    )

    classes_today = Session.query.filter_by(
        tutor_id=tid,
        session_date=date.today()
    ).count()

    unread = Notification.query.filter_by(
        recipient_type="Tutor",
        recipient_id=tid,
        is_read=False
    ).count()

    stats = [
        {
            "id": "classes",
            "value": classes_today,
            "label": "Classes today",
            "icon": "<rect x='3' y='4.5' width='18' height='16' rx='2'/><path d='M3 9h18'/>",
            "spark": [],
        },
        {
            "id": "students",
            "value": len(student_ids),
            "label": "Active students",
            "icon": "<circle cx='9' cy='8' r='3'/><path d='M4 19c0-3 2-5 5-5s5 2 5 5'/>",
            "spark": [],
        },
        {
            "id": "grade",
            "value": pending,
            "label": "To grade",
            "icon": "<path d='M8 3h8l3 3v14H5V4Z'/><path d='M9 12h6'/>",
            "spark": [],
        },
        {
            "id": "unread",
            "value": unread,
            "label": "Unread messages",
            "icon": "<path d='M4 5h16v10H9l-5 4V5Z'/>",
            "spark": [],
        },
    ]

    activities = []

    doubts_rows = (
        Doubt.query
        .filter_by(tutor_id=tid)
        .order_by(Doubt.asked_at.desc())
        .limit(5)
        .all()
    )

    for d in doubts_rows:

        student = db.session.get(
            Student,
            d.student_id
        )

        activities.append({
            "activityId": f"d-{d.doubt_id}",
            "title": (
                f"{student.student_name if student else 'Student'} "
                "asked a doubt"
            ),
            "meta": (
                f"{d.subject or 'General'} · {d.status}"
            ),
            "tone": "var(--coral)",
        })

    meetings = []

    meeting_rows = (
        MeetingRequest.query
        .filter_by(tutor_id=tid)
        .order_by(MeetingRequest.meeting_date)
        .limit(5)
        .all()
    )

    for m in meeting_rows:

        meetings.append({
            "meetingId": f"meet-{m.meeting_id}",
            "day": m.meeting_date.strftime("%d %b %Y"),
            "title": "Meeting",
            "time": m.meeting_date.strftime("%I:%M %p"),
            "meta": (
                m.meeting_reason
                or "Student/Parent meeting"
            ),
        })

    deadlines = []

    assignment_rows = (
        Assignment.query
        .join(Session)
        .filter(Session.tutor_id == tid)
        .order_by(Assignment.due_date)
        .limit(5)
        .all()
    )

    for a in assignment_rows:

        deadlines.append({
            "deadlineId": f"a-{a.assignment_id}",
            "day": (
                a.due_date.strftime("%d %b %Y")
                if a.due_date
                else "No due date"
            ),
            "title": a.title,
            "meta": a.description or "Assignment",
            "badge": "warn",
        })

    leaderboard = []

    students = [
        student_item(s)
        for s in Student.query.filter(
            Student.status == "Active"
        ).all()
    ]

    students = [
        x for x in students
        if x
    ]

    students = sorted(
        students,
        key=lambda x: x["progress"]["weeklyScore"],
        reverse=True
    )[:5]

    for rank, student in enumerate(
        students,
        1
    ):
        leaderboard.append({
            "rank": rank,
            "studentId": student["studentId"],
            "name": student["name"],
            "score": student["progress"]["weeklyScore"],
            "trend": "",
        })

    return ok({
        "stats": stats,

        "overview": [
            {
                "id": "doubts",
                "label": "Doubts requiring replies",
                "value": open_doubts,
                "tone": "coral",
                "go": "doubts",
            },
            {
                "id": "grading",
                "label": "Assignments pending grading",
                "value": pending,
                "tone": "amber",
                "go": "assignments",
            },
            {
                "id": "classes",
                "label": "Classes scheduled today",
                "value": classes_today,
                "tone": "lime",
                "go": "schedule",
            },
            {
                "id": "meeting",
                "label": "Meetings",
                "value": MeetingRequest.query.filter_by(
                    tutor_id=tid
                ).count(),
                "tone": "blue",
                "go": "messages",
            },
            {
                "id": "homework",
                "label": "Homework pending review",
                "value": pending,
                "tone": "purple",
                "go": "assignments",
            },
        ],

        "sessions": [
            session_item(s)
            for s in sessions
        ],

        "activities": activities,
        "deadlines": deadlines,
        "suggestions": [],
        "meetings": meetings,
        "leaderboard": leaderboard,
        "achievements": [],
    })


# =========================================================
# SCHEDULE
# =========================================================

@tutor_bp.route("/schedule", methods=["GET"])
@tutor_required
def schedule():

    tutor = current_tutor()

    if not tutor:
        return fail("Tutor not found", 404)

    sessions = (
        Session.query
        .filter_by(tutor_id=tutor.tutor_id)
        .order_by(
            Session.session_date,
            Session.start_time
        )
        .all()
    )

    subject_ids = set()

    # Tutor profile subjects
    try:
        configured_subjects = json.loads(
            tutor.subjects_json or "[]"
        )
    except (TypeError, ValueError):
        configured_subjects = []

    configured_subjects = {
        str(x).strip().lower()
        for x in configured_subjects
        if str(x).strip()
    }

    if configured_subjects:

        for subject in Subject.query.all():

            if (
                subject.subject_name.strip().lower()
                in configured_subjects
            ):
                subject_ids.add(
                    subject.subject_id
                )

    # Existing session subjects
    if configured_subjects:

        for s in sessions:

            if s.subject_id:
                subject_ids.add(
                    s.subject_id
                )

    # If tutor has no configured subjects,
    # show ALL real subjects.
    else:

        subject_ids = {
            subject.subject_id
            for subject in Subject.query.order_by(
                Subject.subject_name
            ).all()
        }

    subjects = [
        {
            "subjectId": subject.subject_id,
            "subject": subject.subject_name,
        }
        for subject in (
            Subject.query
            .filter(
                Subject.subject_id.in_(subject_ids)
            )
            .order_by(Subject.subject_name)
            .all()
        )
    ]

    times = sorted({
        s.start_time.strftime("%H:%M")
        for s in sessions
    })

    if not times:
        times = [
            "16:00",
            "17:30",
            "19:00",
        ]

    rows = []

    for tm in times:

        row = {
            "time": datetime.strptime(
                tm,
                "%H:%M"
            ).strftime("%I:%M %p"),

            "days": [],
        }

        for day_number in range(0, 6):

            found = next(
                (
                    s
                    for s in sessions
                    if (
                        s.session_date.weekday()
                        == day_number
                        and
                        s.start_time.strftime("%H:%M")
                        == tm
                    )
                ),
                None,
            )

            row["days"].append(
                {
                    "t": subject_name(
                        found.subject_id
                    ),
                    "s": found.session_type,
                }
                if found
                else None
            )

        rows.append(row)

    events = [
        {
            "eventId": s.session_id,
            "date": s.session_date.isoformat(),
            "title": subject_name(
                s.subject_id
            ),
            "type": s.status,
        }
        for s in sessions
    ]

    return ok({
        "rows": rows,
        "events": events,
        "sessions": [
            session_item(s)
            for s in sessions
        ],
        "subjects": subjects,
    })


# =========================================================
# ADD CLASS
# =========================================================

@tutor_bp.route(
    "/schedule/class",
    methods=["POST"]
)
@tutor_required
def add_class():

    tutor = current_tutor()

    data = request.get_json(
        silent=True
    ) or {}

    try:

        subject_id = int(
            data.get("subject_id")
        )

        session_date = datetime.strptime(
            data.get("session_date"),
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            data.get("start_time"),
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            data.get("end_time"),
            "%H:%M"
        ).time()

    except (TypeError, ValueError):

        return fail(
            "subject_id, session_date, "
            "start_time and end_time are required"
        )

    if not db.session.get(
        Subject,
        subject_id
    ):
        return fail(
            "Subject not found",
            404
        )

    if start_time >= end_time:
        return fail(
            "End time must be after start time"
        )

    s = Session(
        tutor_id=tutor.tutor_id,
        subject_id=subject_id,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time,
        session_type=data.get(
            "session_type",
            "Regular"
        ),
        status="Scheduled",
    )

    db.session.add(s)
    db.session.commit()

    # Try to create Meet, but never break
    # scheduling if Google Meet is unavailable.
    meet_message = "Session created"

    try:

        s.meeting_url = create_meeting_space()

        db.session.commit()

        meet_message = (
            "Session created with Google Meet"
        )

    except GoogleMeetNotConfigured as exc:

        db.session.rollback()

        meet_message = (
            "Session created. "
            "Google Meet is not connected yet."
        )

        current_app.logger.warning(
            "Google Meet setup required: %s",
            exc
        )

    except Exception as exc:

        db.session.rollback()

        meet_message = (
            "Session created. "
            "Google Meet could not be created."
        )

        current_app.logger.exception(
            "Google Meet creation failed: %s",
            exc
        )

    return ok(
        {
            "session": session_item(s),
            "meeting_url": s.meeting_url,
        },
        meet_message,
        201,
    )


# =========================================================
# START CLASS / GOOGLE MEET
# =========================================================

@tutor_bp.route(
    "/schedule/class/<int:session_id>/start",
    methods=["POST"]
)
@tutor_required
def start_class(session_id):

    tutor = current_tutor()

    if not tutor:
        return fail(
            "Tutor not found",
            404
        )

    s = db.session.get(
        Session,
        session_id
    )

    if (
        not s
        or s.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Session not found",
            404
        )

    if s.status not in (
        "Scheduled",
        "Rescheduled",
    ):
        return fail(
            "This session is not available to start.",
            400
        )

    if s.meeting_url:

        return ok(
            {
                "session": session_item(s),
                "meeting_url": s.meeting_url,
            },
            "Meeting ready"
        )

    try:

        s.meeting_url = create_meeting_space()

        db.session.commit()

    except GoogleMeetNotConfigured as exc:

        db.session.rollback()

        current_app.logger.warning(
            "Google Meet setup required: %s",
            exc
        )

        return fail(
            "Google Meet is not connected. "
            "Run setup_google_meet.py and authorize "
            "the dedicated Google account.",
            503,
        )

    except Exception as exc:

        db.session.rollback()

        current_app.logger.exception(
            "Google Meet start failed: %s",
            exc
        )

        return fail(
            "Google Meet could not be created. "
            "Check the backend terminal for "
            "the Google API error.",
            502,
        )

    return ok(
        {
            "session": session_item(s),
            "meeting_url": s.meeting_url,
        },
        "Meeting ready"
    )


# =========================================================
# STUDENTS
# =========================================================

@tutor_bp.route(
    "/students",
    methods=["GET"]
)
@tutor_required
def students():

    items = [
        x
        for x in (
            student_item(s)
            for s in Student.query.filter_by(
                status="Active"
            ).all()
        )
        if x
    ]

    return ok({
        "students": items
    })


# =========================================================
# ATTENDANCE
# =========================================================

@tutor_bp.route(
    "/attendance",
    methods=["GET", "POST"]
)
@tutor_required
def attendance():

    tutor = current_tutor()

    if request.method == "POST":

        records = (
            request.get_json(
                silent=True
            ) or {}
        ).get("records", [])

        for item in records:

            student_id = int(
                item.get("studentId")
            )

            session_id = item.get(
                "sessionId"
            )

            status = item.get(
                "status",
                "Present"
            )

            existing = (
                AttendanceRecord.query
                .filter_by(
                    tutor_id=tutor.tutor_id,
                    student_id=student_id,
                    session_id=session_id,
                )
                .first()
            )

            if existing:

                existing.status = status
                existing.date = date.today()

            else:

                db.session.add(
                    AttendanceRecord(
                        tutor_id=tutor.tutor_id,
                        student_id=student_id,
                        session_id=session_id,
                        status=status,
                        date=date.today(),
                    )
                )

        db.session.commit()

        return ok(
            message="Attendance saved"
        )

    rows = (
        AttendanceRecord.query
        .filter_by(
            tutor_id=tutor.tutor_id
        )
        .order_by(
            AttendanceRecord.date.desc()
        )
        .all()
    )

    counts = {
        "Present": 0,
        "Absent": 0,
        "Late": 0,
    }

    data = []

    for r in rows:

        counts[r.status] = (
            counts.get(r.status, 0) + 1
        )

        data.append({
            "attendanceId": r.attendance_id,
            "studentId": r.student_id,
            "sessionId": r.session_id,
            "status": r.status,
        })

    total = sum(
        counts.values()
    ) or 1

    analytics = [
        {
            "label": key,
            "value": round(
                value / total * 100
            ),
        }
        for key, value
        in counts.items()
    ]

    return ok({
        "records": data,
        "analytics": analytics,
    })


# =========================================================
# SESSION UPDATE
# =========================================================

@tutor_bp.route(
    "/session-update",
    methods=["POST"]
)
@tutor_required
def session_update():

    tutor = current_tutor()

    data = request.get_json(
        silent=True
    ) or {}

    try:

        session_id = int(
            data.get("session_id")
        )

    except:

        return fail(
            "session_id is required"
        )

    sess = db.session.get(
        Session,
        session_id
    )

    if (
        not sess
        or sess.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Session not found",
            404
        )

    update = (
        SessionUpdate.query
        .filter_by(
            session_id=session_id
        )
        .first()
    )

    if not update:

        update = SessionUpdate(
            session_id=session_id
        )

        db.session.add(update)

    update.topics_covered = data.get(
        "topics_covered",
        ""
    )

    update.homework_assigned = data.get(
        "homework_assigned",
        ""
    )

    if data.get("next_session_date"):

        try:

            update.next_session_date = (
                datetime.strptime(
                    data["next_session_date"],
                    "%Y-%m-%d"
                ).date()
            )

        except ValueError:
            pass

    for booking in SessionBooking.query.filter_by(
        session_id=session_id
    ).all():

        db.session.add(
            Notification(
                recipient_type="Student",
                recipient_id=booking.student_id,
                title="Session update",
                message=(
                    update.topics_covered
                    or "Session update available"
                ),
                notification_type="Session Update",
            )
        )

        student = db.session.get(
            Student,
            booking.student_id
        )

        if student and student.parent_id:

            db.session.add(
                Notification(
                    recipient_type="Parent",
                    recipient_id=student.parent_id,
                    title="Session update",
                    message=(
                        f"{student.student_name}: "
                        f"{update.topics_covered or 'Session update available'}"
                    ),
                    notification_type="Session Update",
                )
            )

    db.session.commit()

    return ok(
        message=(
            "Session update saved and "
            "notifications created"
        )
    )


# =========================================================
# ASSIGNMENTS
# =========================================================

@tutor_bp.route(
    "/assignments",
    methods=["GET", "POST"]
)
@tutor_required
def assignments():

    tutor = current_tutor()

    if request.method == "POST":

        data = request.get_json(
            silent=True
        ) or {}

        try:

            session_id = int(
                data.get("session_id")
            )

        except:

            return fail(
                "session_id is required"
            )

        sess = db.session.get(
            Session,
            session_id
        )

        if (
            not sess
            or sess.tutor_id != tutor.tutor_id
        ):
            return fail(
                "Session not found",
                404
            )

        due = None

        if data.get("due_date"):

            try:

                due = datetime.strptime(
                    data["due_date"],
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return fail(
                    "Invalid due_date"
                )

        assignment = Assignment(
            session_id=session_id,
            title=(
                data.get("title")
                or ""
            ).strip(),
            description=data.get(
                "description",
                ""
            ),
            due_date=due,
        )

        if not assignment.title:

            return fail(
                "title is required"
            )

        db.session.add(assignment)
        db.session.commit()

        return ok(
            {
                "assignment": {
                    "assignmentId":
                        assignment.assignment_id,
                    "title":
                        assignment.title,
                }
            },
            "Assignment created",
            201,
        )

    rows = (
        Assignment.query
        .join(Session)
        .filter(
            Session.tutor_id == tutor.tutor_id
        )
        .order_by(
            Assignment.due_date
        )
        .all()
    )

    data = []

    for assignment in rows:

        submissions = (
            AssignmentSubmission.query
            .filter_by(
                assignment_id=
                    assignment.assignment_id
            )
            .all()
        )

        statuses = [
            x.status
            for x in submissions
        ]

        status = (
            "Pending"
            if any(
                x in statuses
                for x in (
                    "Pending",
                    "In Progress",
                )
            )
            else
            "Submitted"
            if statuses
            else
            "Pending"
        )

        sess = db.session.get(
            Session,
            assignment.session_id
        )

        data.append({
            "assignmentId":
                assignment.assignment_id,
            "title":
                assignment.title,
            "classLevel":
                subject_name(
                    sess.subject_id
                ) if sess else "General",
            "submissions":
                f"{len(submissions)} submissions",
            "type":
                "assignment",
            "homeworkStatus":
                status,
            "sessionId":
                assignment.session_id,
            "dueDate":
                assignment.due_date.isoformat()
                if assignment.due_date
                else None,
        })

    return ok({
        "assignments": data
    })


@tutor_bp.route(
    "/assignments/<int:assignment_id>",
    methods=["DELETE"]
)
@tutor_required
def delete_assignment(
    assignment_id
):

    tutor = current_tutor()

    assignment = db.session.get(
        Assignment,
        assignment_id
    )

    sess = (
        db.session.get(
            Session,
            assignment.session_id
        )
        if assignment
        else None
    )

    if (
        not assignment
        or not sess
        or sess.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Assignment not found",
            404
        )

    AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id
    ).delete()

    db.session.delete(
        assignment
    )

    db.session.commit()

    return ok(
        message="Assignment deleted"
    )


@tutor_bp.route(
    "/assignments/ai-generate",
    methods=["POST"]
)
@tutor_required
def ai_generate():

    return fail(
        "AI generation is not configured; "
        "create real quiz questions in the database instead.",
        501,
    )


# =========================================================
# QUIZZES
# =========================================================

@tutor_bp.route(
    "/quizzes",
    methods=["GET", "POST"]
)
@tutor_required
def tutor_quizzes():

    tutor = current_tutor()

    if request.method == "POST":

        data = request.get_json(
            silent=True
        ) or {}

        try:

            subject_id = int(
                data.get("subject_id")
            )

        except:

            return fail(
                "subject_id is required"
            )

        if not db.session.get(
            Subject,
            subject_id
        ):
            return fail(
                "Subject not found",
                404
            )

        quiz = Quiz(
            tutor_id=tutor.tutor_id,
            subject_id=subject_id,
            title=(
                data.get("title")
                or ""
            ).strip(),
            week_number=data.get(
                "week_number"
            ),
        )

        if not quiz.title:

            return fail(
                "title is required"
            )

        db.session.add(quiz)
        db.session.commit()

        return ok(
            {
                "quiz": {
                    "quiz_id":
                        quiz.quiz_id,
                    "title":
                        quiz.title,
                }
            },
            "Quiz created",
            201,
        )

    rows = (
        Quiz.query
        .filter_by(
            tutor_id=tutor.tutor_id
        )
        .order_by(
            Quiz.created_at.desc()
        )
        .all()
    )

    return ok({
        "quizzes": [
            {
                "quiz_id": q.quiz_id,
                "title": q.title,
                "subject":
                    subject_name(
                        q.subject_id
                    ),
                "questionCount":
                    QuizQuestion.query
                    .filter_by(
                        quiz_id=q.quiz_id
                    )
                    .count(),
            }
            for q in rows
        ]
    })


@tutor_bp.route(
    "/quizzes/<int:quiz_id>/questions",
    methods=["POST"]
)
@tutor_required
def create_question(
    quiz_id
):

    tutor = current_tutor()

    quiz = db.session.get(
        Quiz,
        quiz_id
    )

    if (
        not quiz
        or quiz.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Quiz not found",
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    question = QuizQuestion(
        quiz_id=quiz_id,
        question=data.get(
            "question",
            ""
        ),
        option_a=data.get(
            "option_a",
            ""
        ),
        option_b=data.get(
            "option_b",
            ""
        ),
        option_c=data.get(
            "option_c",
            ""
        ),
        option_d=data.get(
            "option_d",
            ""
        ),
        correct_option=str(
            data.get(
                "correct_option",
                ""
            )
        ).upper(),
    )

    if (
        not question.question
        or question.correct_option
        not in {"A", "B", "C", "D"}
    ):
        return fail(
            "Question and correct_option A/B/C/D are required"
        )

    db.session.add(question)
    db.session.commit()

    return ok(
        {
            "question_id":
                question.question_id
        },
        "Question added",
        201,
    )


# =========================================================
# MATERIALS
# =========================================================

@tutor_bp.route(
    "/materials",
    methods=["GET", "POST"]
)
@tutor_required
def materials():

    tutor = current_tutor()

    if request.method == "POST":

        form = request.form

        try:

            session_id = int(
                form.get("session_id")
            )

        except:

            return fail(
                "session_id is required"
            )

        sess = db.session.get(
            Session,
            session_id
        )

        if (
            not sess
            or sess.tutor_id != tutor.tutor_id
        ):
            return fail(
                "Session not found",
                404
            )

        title = (
            form.get("title")
            or ""
        ).strip()

        if not title:

            return fail(
                "title is required"
            )

        link = (
            form.get("resource_link")
            or ""
        ).strip()

        file = request.files.get(
            "file"
        )

        resource_type = (
            form.get("resource_type")
            or "Notes"
        )

        if file and file.filename:

            ext = (
                os.path.splitext(
                    file.filename
                )[1]
                .lower()
                .lstrip(".")
            )

            if ext not in ALLOWED_UPLOADS:

                return fail(
                    "File type is not supported"
                )

            folder = os.path.join(
                current_app.root_path,
                "uploads"
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            safe_name = (
                f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_"
                f"{secure_filename(file.filename)}"
            )

            file.save(
                os.path.join(
                    folder,
                    safe_name
                )
            )

            link = (
                f"/tutor/uploads/{safe_name}"
            )

            if ext == "pdf":
                resource_type = "PDF"

        if not link:

            return fail(
                "Provide a file or resource link"
            )

        resource = StudyResource(
            session_id=session_id,
            resource_title=title,
            resource_type=resource_type,
            resource_link=link,
        )

        db.session.add(resource)
        db.session.commit()

        for booking in SessionBooking.query.filter_by(
            session_id=session_id
        ).all():

            db.session.add(
                Notification(
                    recipient_type="Student",
                    recipient_id=booking.student_id,
                    title="New study resource",
                    message=title,
                    notification_type="Reminder",
                )
            )

        db.session.commit()

        return ok(
            {
                "resource": {
                    "resourceId":
                        resource.resource_id,
                    "title":
                        resource.resource_title,
                    "resourceLink":
                        resource.resource_link,
                }
            },
            "Material uploaded",
            201,
        )

    rows = (
        StudyResource.query
        .join(Session)
        .filter(
            Session.tutor_id == tutor.tutor_id
        )
        .order_by(
            StudyResource.resource_id.desc()
        )
        .all()
    )

    data = []

    for resource in rows:

        sess = db.session.get(
            Session,
            resource.session_id
        )

        data.append({
            "resourceId":
                resource.resource_id,
            "sessionId":
                resource.session_id,
            "title":
                resource.resource_title,
            "description":
                (
                    f"{subject_name(sess.subject_id)} "
                    f"· {resource.resource_type}"
                ),
            "resourceLink":
                resource.resource_link,
            "resourceType":
                resource.resource_type,
            "gradient":
                "linear-gradient(135deg,var(--g1),var(--g2))",
            "icon":
                "<path d='M8 3h8l3 3v14H5V4Z'/>",
        })

    return ok({
        "resources": data
    })


@tutor_bp.route(
    "/materials/<int:resource_id>",
    methods=["DELETE"]
)
@tutor_required
def delete_material(
    resource_id
):

    tutor = current_tutor()

    resource = db.session.get(
        StudyResource,
        resource_id
    )

    sess = (
        db.session.get(
            Session,
            resource.session_id
        )
        if resource
        else None
    )

    if (
        not resource
        or not sess
        or sess.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Material not found",
            404
        )

    if (
        resource.resource_link
        and resource.resource_link.startswith(
            "/tutor/uploads/"
        )
    ):

        path = os.path.join(
            current_app.root_path,
            "uploads",
            os.path.basename(
                resource.resource_link
            )
        )

        if os.path.exists(path):
            os.remove(path)

    db.session.delete(
        resource
    )

    db.session.commit()

    return ok(
        message="Material deleted"
    )


@tutor_bp.route(
    "/uploads/<path:filename>",
    methods=["GET"]
)
def uploaded_file(filename):

    return send_from_directory(
        os.path.join(
            current_app.root_path,
            "uploads"
        ),
        filename
    )


# =========================================================
# Q&A
# =========================================================

@tutor_bp.route(
    "/qa",
    methods=["GET", "POST"]
)
@tutor_required
def qa():

    if request.method == "POST":

        data = request.get_json(
            silent=True
        ) or {}

        question = (
            data.get("question")
            or ""
        ).strip()

        answer = (
            data.get("answer")
            or ""
        ).strip()

        if not question or not answer:

            return fail(
                "question and answer are required"
            )

        faq = FAQ(
            question=question,
            answer=answer,
            category=data.get(
                "category",
                "General"
            ),
        )

        db.session.add(faq)
        db.session.commit()

        return ok(
            {
                "entry": {
                    "faqId": faq.faq_id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "meta": "Published",
                }
            },
            "FAQ published",
            201,
        )

    rows = (
        FAQ.query
        .order_by(
            FAQ.faq_id.desc()
        )
        .all()
    )

    return ok({
        "entries": [
            {
                "faqId": faq.faq_id,
                "question": faq.question,
                "answer": faq.answer,
                "meta":
                    faq.category
                    or "General",
            }
            for faq in rows
        ]
    })


@tutor_bp.route(
    "/qa/<int:faq_id>",
    methods=["DELETE"]
)
@tutor_required
def delete_qa(
    faq_id
):
    """Delete a Q&A board entry. Tutor/admin-only action, exposed here
    because the tutor role already owns Q&A publishing."""

    faq = db.session.get(
        FAQ,
        faq_id
    )

    if not faq:

        return fail(
            "Q&A entry not found",
            404
        )

    db.session.delete(
        faq
    )
    db.session.commit()

    return ok(
        message="Q&A entry deleted"
    )


# =========================================================
# DOUBTS
# =========================================================

@tutor_bp.route(
    "/doubts",
    methods=["GET"]
)
@tutor_required
def doubts():

    tutor = current_tutor()

    rows = (
        Doubt.query
        .filter_by(
            tutor_id=tutor.tutor_id
        )
        .order_by(
            Doubt.asked_at.desc()
        )
        .all()
    )

    return ok({
        "doubts": [
            {
                "doubtId": d.doubt_id,
                "studentId": d.student_id,
                "subject": d.subject,
                "question": d.question,
                "askedAt":
                    d.asked_at.isoformat()
                    if d.asked_at
                    else None,
                "status": d.status,
            }
            for d in rows
        ]
    })


@tutor_bp.route(
    "/doubts/<int:doubt_id>/reply",
    methods=["POST"]
)
@tutor_required
def reply_doubt(
    doubt_id
):

    tutor = current_tutor()

    doubt = (
        Doubt.query
        .filter_by(
            doubt_id=doubt_id,
            tutor_id=tutor.tutor_id
        )
        .first()
    )

    if not doubt:

        return fail(
            "Doubt not found",
            404
        )

    text = (
        request.get_json(
            silent=True
        ) or {}
    ).get(
        "reply",
        ""
    ).strip()

    if not text:

        return fail(
            "Reply is required"
        )

    doubt.answer = text
    doubt.status = "Answered"
    doubt.replied_at = datetime.utcnow()

    db.session.add(
        Notification(
            recipient_type="Student",
            recipient_id=doubt.student_id,
            title="Doubt answered",
            message=text,
            notification_type="Doubt",
        )
    )

    db.session.commit()

    return ok(
        message="Reply sent"
    )


# =========================================================
# MESSAGES
# =========================================================

@tutor_bp.route(
    "/messages/conversations",
    methods=["GET"]
)
@tutor_required
def conversations():

    tutor = current_tutor()

    rows = (
        Message.query
        .filter(
            (
                (Message.sender_type == "Tutor")
                &
                (Message.sender_id == tutor.tutor_id)
            )
            |
            (
                (Message.receiver_type == "Tutor")
                &
                (Message.receiver_id == tutor.tutor_id)
            )
        )
        .order_by(
            Message.sent_at
        )
        .all()
    )

    conversations_data = {}

    for message in rows:

        if message.sender_type == "Tutor":

            other_type = message.receiver_type
            other_id = message.receiver_id

        else:

            other_type = message.sender_type
            other_id = message.sender_id

        key = (
            f"{other_type.lower()}-{other_id}"
        )

        if key not in conversations_data:

            person = (
                db.session.get(
                    Student,
                    other_id
                )
                if other_type == "Student"
                else db.session.get(
                    Parent,
                    other_id
                )
            )

            if isinstance(
                person,
                Student
            ):

                name = person.student_name

            else:

                name = (
                    person.parent_name
                    if person
                    else "User"
                )

            conversations_data[key] = {
                "id": key,
                "participantName": name,
                "subtitle": other_type,
                "initials": "".join(
                    x[0]
                    for x in name.split()[:2]
                ).upper(),
                "gradient":
                    "linear-gradient(135deg,var(--g1),var(--g2))",
                "messages": [],
                "otherType": other_type,
                "otherId": other_id,
            }

        conversations_data[key]["messages"].append({
            "messageId": message.message_id,
            "message": message.message,
            "timestamp":
                message.sent_at.isoformat()
                if message.sent_at
                else None,
            "w":
                "me"
                if message.sender_type == "Tutor"
                else "them",
        })

    return ok({
        "conversations":
            conversations_data
    })


@tutor_bp.route(
    "/messages/send",
    methods=["POST"]
)
@tutor_required
def send_message():

    tutor = current_tutor()

    data = request.get_json(
        silent=True
    ) or {}

    receiver_type = data.get(
        "receiver_type"
    )

    receiver_id = data.get(
        "receiver_id"
    )

    text = (
        data.get("message")
        or ""
    ).strip()

    if (
        not receiver_type
        or not receiver_id
        or not text
    ):
        return fail(
            "receiver_type, receiver_id "
            "and message are required"
        )

    if receiver_type not in {
        "Student",
        "Parent",
    }:

        return fail(
            "Invalid receiver type"
        )

    if (
        receiver_type == "Student"
        and not db.session.get(
            Student,
            int(receiver_id)
        )
    ):

        return fail(
            "Student not found",
            404
        )

    if (
        receiver_type == "Parent"
        and not db.session.get(
            Parent,
            int(receiver_id)
        )
    ):

        return fail(
            "Parent not found",
            404
        )

    message = Message(
        sender_type="Tutor",
        sender_id=tutor.tutor_id,
        receiver_type=receiver_type,
        receiver_id=int(receiver_id),
        message=text,
    )

    db.session.add(message)
    db.session.commit()

    return ok(
        {
            "messageId":
                message.message_id
        },
        "Message sent",
        201,
    )


# =========================================================
# MEETING REQUEST
# =========================================================

@tutor_bp.route(
    "/meetings/request",
    methods=["POST"]
)
@tutor_required
def request_meeting():

    tutor = current_tutor()

    data = request.get_json(
        silent=True
    ) or {}

    try:

        meeting_date = datetime.fromisoformat(
            data.get("meeting_date")
        )

    except (TypeError, ValueError):

        return fail(
            "meeting_date must be ISO datetime"
        )

    student_id = data.get(
        "student_id"
    )

    parent_id = data.get(
        "parent_id"
    )

    if not student_id and not parent_id:

        return fail(
            "student_id or parent_id is required"
        )

    if (
        student_id
        and not db.session.get(
            Student,
            int(student_id)
        )
    ):

        return fail(
            "Student not found",
            404
        )

    if (
        parent_id
        and not db.session.get(
            Parent,
            int(parent_id)
        )
    ):

        return fail(
            "Parent not found",
            404
        )

    meeting = MeetingRequest(
        tutor_id=tutor.tutor_id,
        student_id=(
            int(student_id)
            if student_id
            else None
        ),
        parent_id=(
            int(parent_id)
            if parent_id
            else None
        ),
        meeting_date=meeting_date,
        meeting_link=data.get(
            "meeting_link"
        ),
        meeting_reason=data.get(
            "meeting_reason",
            ""
        ),
        status="Scheduled",
    )

    db.session.add(meeting)
    db.session.commit()

    if student_id:

        db.session.add(
            Notification(
                recipient_type="Student",
                recipient_id=int(student_id),
                title="New meeting scheduled",
                message=(
                    data.get(
                        "meeting_reason",
                        "Meeting scheduled"
                    )
                ),
                notification_type="Reminder",
            )
        )

    if parent_id:

        db.session.add(
            Notification(
                recipient_type="Parent",
                recipient_id=int(parent_id),
                title="New meeting scheduled",
                message=(
                    data.get(
                        "meeting_reason",
                        "Meeting scheduled"
                    )
                ),
                notification_type="Reminder",
            )
        )

    db.session.commit()

    return ok(
        {
            "meeting_id":
                meeting.meeting_id
        },
        "Meeting scheduled",
        201,
    )


# =========================================================
# EARNINGS
# =========================================================

@tutor_bp.route(
    "/earnings",
    methods=["GET"]
)
@tutor_required
def earnings():

    tutor = current_tutor()

    completed = (
        Session.query
        .filter_by(
            tutor_id=tutor.tutor_id,
            status="Completed"
        )
        .all()
    )

    try:

        rate = float(
            str(
                tutor.hourly_rate or ""
            )
            .replace("₹", "")
            .replace("/hr", "")
            .replace(",", "")
            .strip()
        )

    except:

        rate = 0

    total_hours = sum(
        max(
            0,
            (
                datetime.combine(
                    date.today(),
                    s.end_time
                )
                -
                datetime.combine(
                    date.today(),
                    s.start_time
                )
            ).seconds
        ) / 3600
        for s in completed
    )

    history = []

    for s in completed:

        minutes = (
            s.end_time.hour * 60
            + s.end_time.minute
        ) - (
            s.start_time.hour * 60
            + s.start_time.minute
        )

        history.append({
            "month":
                s.session_date.strftime(
                    "%b %Y"
                ),
            "sessions": 1,
            "amount":
                round(
                    rate * minutes / 60,
                    2
                ),
            "status":
                "Completed",
        })

    return ok({
        "history": history,
        "total":
            round(
                rate * total_hours,
                2
            ),
    })


# =========================================================
# PROFILE
# =========================================================

@tutor_bp.route(
    "/profile",
    methods=["GET", "PUT"]
)
@tutor_required
def profile():

    tutor = current_tutor()

    if not tutor:
        return fail(
            "Tutor not found",
            404
        )

    # -----------------------------------------------------
    # UPDATE PROFILE
    # -----------------------------------------------------

    if request.method == "PUT":

        data = request.get_json(
            silent=True
        ) or {}

        # Basic profile fields
        field_mapping = {
            "name": "tutor_name",
            "phone": "phone_no",
            "bio": "bio",
            "education": "education",
            "hourlyRate": "hourly_rate",
            "availability": "availability",
            "experience": "experience_years",
        }

        for field, attribute in field_mapping.items():

            if field in data:

                setattr(
                    tutor,
                    attribute,
                    data[field]
                )

        # Subjects
        if "subjects" in data:

            subjects = data.get(
                "subjects"
            )

            if not isinstance(
                subjects,
                list
            ):
                subjects = []

            tutor.subjects_json = json.dumps(
                subjects
            )

        # Languages
        if "languages" in data:

            languages = data.get(
                "languages"
            )

            if not isinstance(
                languages,
                list
            ):
                languages = []

            tutor.languages_json = json.dumps(
                languages
            )

        # Certificates
        if "certificates" in data:

            certificates = data.get(
                "certificates"
            )

            if not isinstance(
                certificates,
                list
            ):
                certificates = []

            tutor.certificates_json = json.dumps(
                certificates
            )

        db.session.commit()

        return ok(
            message="Profile updated"
        )

    # -----------------------------------------------------
    # GET PROFILE
    # -----------------------------------------------------

    def load_json(value):

        try:

            parsed = json.loads(
                value or "[]"
            )

            return (
                parsed
                if isinstance(parsed, list)
                else []
            )

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):

            return []

    name = (
        tutor.tutor_name
        or "Tutor"
    )

    initials = "".join(
        part[0]
        for part in name.split()[:2]
        if part
    ).upper()

    return ok({
        "tutor": {

            "userId":
                tutor.tutor_id,

            "name":
                name,

            "email":
                tutor.email,

            "phone":
                tutor.phone_no or "",

            "experience":
                tutor.experience_years or 0,

            "bio":
                tutor.bio or "",

            "education":
                tutor.education or "",

            "hourlyRate":
                tutor.hourly_rate or "",

            "availability":
                tutor.availability or "",

            "subjects":
                load_json(
                    tutor.subjects_json
                ),

            "languages":
                load_json(
                    tutor.languages_json
                ),

            "certificates":
                load_json(
                    tutor.certificates_json
                ),

            "initials":
                initials or "T",
        }
    })


# =========================================================
# NOTIFICATIONS
# =========================================================

@tutor_bp.route(
    "/notifications",
    methods=["GET"]
)
@tutor_required
def notifications():

    tutor = current_tutor()

    rows = (
        Notification.query
        .filter_by(
            recipient_type="Tutor",
            recipient_id=tutor.tutor_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return ok({
        "notifications": [
            {
                "id":
                    n.notification_id,

                "title":
                    n.title,

                "message":
                    n.message,

                "isRead":
                    n.is_read,

                "go":
                    "dashboard",
            }
            for n in rows
        ]
    })


@tutor_bp.route(
    "/notifications/<int:notification_id>/read",
    methods=["PATCH"]
)
@tutor_required
def mark_notification(
    notification_id
):

    tutor = current_tutor()

    notification = (
        Notification.query
        .filter_by(
            notification_id=notification_id,
            recipient_type="Tutor",
            recipient_id=tutor.tutor_id,
        )
        .first()
    )

    if not notification:

        return fail(
            "Notification not found",
            404
        )

    notification.is_read = True

    db.session.commit()

    return ok(
        message="Notification marked as read"
    )