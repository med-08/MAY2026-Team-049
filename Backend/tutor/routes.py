import json
import os
from datetime import datetime, date, timedelta
from urllib.parse import urlparse

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
    FlashcardSet,
    Flashcard,
)
from utils import decode_jwt_token
from google_meet import create_meeting_space, GoogleMeetNotConfigured
from schedule import meeting_lifecycle, _local_now
from ai_service import AIConfigError, AIResponseError, AIServiceError, generate_text


# =========================================================
# CONSTANTS
# =========================================================

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

def normalize_subject_name(value):
    """Normalize tutor-entered subject names."""
    value = str(value or "").strip().lower()

    aliases = {
        "maths": "mathematics",
        "math": "mathematics",
    }

    return aliases.get(value, value)


def current_tutor():
    """Return the currently authenticated Tutor."""

    auth = request.headers.get("Authorization", "")

    if auth.startswith("Bearer "):
        payload = decode_jwt_token(
            auth.split(" ", 1)[1]
        )

        if payload and payload.get("role") == "Tutor":
            # The JWT stores the tutor's primary-key ID.  If the database was
            # recreated/reset after the token was issued, that ID may no longer
            # exist.  Try the username as a safe fallback before treating the
            # token as stale.
            tutor = db.session.get(
                Tutor,
                payload.get("user_id")
            )

            if not tutor and payload.get("username"):
                tutor = (
                    Tutor.query
                    .filter(db.func.lower(Tutor.tutor_name) ==
                            str(payload.get("username")).strip().lower())
                    .first()
                )

            if tutor:
                return tutor

    uid = session.get("user_id")

    if uid and session.get("role") == "Tutor":
        return db.session.get(
            Tutor,
            uid
        )

    return None


def ok(data=None, message=None, status=200):
    payload = {
        "success": True
    }

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


def clean_optional_url(value):
    url = str(value or "").strip()
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Meeting Link must be a valid URL")
    return url


def subject_name(subject_id):
    subject = db.session.get(
        Subject,
        subject_id
    )

    if subject:
        return subject.subject_name

    return "General"


def tutor_has_subject(tutor, subject_id):
    """
    Check whether the subject is assigned
    to the tutor profile.
    """

    subject = db.session.get(
        Subject,
        subject_id
    )

    if not subject:
        return False

    try:
        configured = json.loads(
            tutor.subjects_json or "[]"
        )
    except (TypeError, ValueError):
        configured = []

    allowed_names = {
        normalize_subject_name(x)
        for x in configured
        if str(x).strip()
    }

    return (
        normalize_subject_name(
            subject.subject_name
        )
        in allowed_names
    )


def get_tutor_subject_ids(tutor):
    """Return Subject IDs assigned to tutor."""

    try:
        configured = json.loads(
            tutor.subjects_json or "[]"
        )
    except (TypeError, ValueError):
        configured = []

    configured = {
        normalize_subject_name(x)
        for x in configured
        if str(x).strip()
    }

    if not configured:
        return set()

    return {
        subject.subject_id
        for subject in Subject.query.all()
        if normalize_subject_name(
            subject.subject_name
        ) in configured
    }


# =========================================================
# SESSION FORMATTER
# =========================================================

def session_item(s):
    subject = db.session.get(Subject, s.subject_id)
    bookings = SessionBooking.query.filter_by(session_id=s.session_id, booking_status="Confirmed").all()
    lifecycle = meeting_lifecycle(s)
    meeting_request = MeetingRequest.query.filter_by(session_id=s.session_id).first()

    # -----------------------------------------------------
    # WHO IS ACTUALLY IN THE ONE-TO-ONE MEETING?
    # -----------------------------------------------------
    # MeetingRequest.parent_id / MeetingRequest.student_id are the source of
    # truth for this: a parent-created request stores parent_id, and only
    # stores student_id too when the parent chose to include the child
    # (see Parent.request_meeting -> include_student). Without this, the
    # frontend had no real signal and had to guess, which is what produced
    # "With: Student" on requests where the parent had included the student.
    meeting_participant_type = None
    if meeting_request:
        has_parent = bool(meeting_request.parent_id)
        has_student = bool(meeting_request.student_id)
        if has_parent and has_student:
            meeting_participant_type = "PARENT_STUDENT"
        elif has_parent:
            meeting_participant_type = "PARENT"
        elif has_student:
            meeting_participant_type = "STUDENT"

    students = []
    for booking in bookings:
        student = db.session.get(Student, booking.student_id)
        if student:
            parent = db.session.get(Parent, student.parent_id) if student.parent_id else None
            students.append({
                "studentId": student.student_id,
                "name": student.student_name,
                "parentName": parent.parent_name if parent else None,
                "attendance": (AttendanceRecord.query.filter_by(session_id=s.session_id, student_id=student.student_id).first().status if AttendanceRecord.query.filter_by(session_id=s.session_id, student_id=student.student_id).first() else None),
            })
    return {
        "id": s.session_id,
        "sessionId": f"sess-{s.session_id:03d}",
        "subject": subject.subject_name if subject else "General",
        "subjectId": s.subject_id,
        "classLevel": s.session_type or "Regular",
        "date": s.session_date.isoformat() if s.session_date else None,
        "time": s.start_time.strftime("%I:%M %p") if s.start_time else None,
        "endTime": s.end_time.strftime("%I:%M %p") if s.end_time else None,
        "summary": f"{len(bookings)} booked · {s.status}",
        "status": s.status,
        "badge": lifecycle["status"],
        "meeting_lifecycle": lifecycle["status"],
        "can_join": lifecycle["can_join"],
        "can_start": lifecycle["can_start"],
        "can_end": lifecycle["can_end"],
        "action": "End class" if lifecycle["can_end"] else ("Start class" if lifecycle["can_start"] else None),
        "meeting_url": s.meeting_url,
        "meetingUrl": s.meeting_url,
        "meeting_started_at": s.meeting_started_at.isoformat() if s.meeting_started_at else None,
        "meeting_ended_at": s.meeting_ended_at.isoformat() if s.meeting_ended_at else None,
        "meeting_duration_seconds": s.meeting_duration_seconds or 0,
        "students": students,
        "meeting_request_status": meeting_request.status if meeting_request else None,
        "meeting_id": meeting_request.meeting_id if meeting_request else None,
        "meeting_reason": meeting_request.meeting_reason if meeting_request else None,
        "meeting_participant_type": meeting_participant_type,
        "meeting_requester_parent_id": meeting_request.parent_id if meeting_request else None,
        "meeting_requester_student_id": meeting_request.student_id if meeting_request else None,
    }


# =========================================================
# STUDENT FORMATTER
# =========================================================

def student_item(st):

    subject_ids = {
        x.subject_id
        for x in (
            StudentSubject.query
            .filter_by(
                student_id=st.student_id
            )
            .all()
        )
    }

    tutor = current_tutor()

    if not tutor:
        return None

    tutor_sessions = (
        Session.query
        .filter_by(
            tutor_id=tutor.tutor_id
        )
        .all()
    )

    relevant = [
        s
        for s in tutor_sessions
        if s.subject_id in subject_ids
    ]

    if not relevant:
        return None

    scores = []

    for s in relevant:

        progress_rows = (
            LearningProgress.query
            .filter_by(
                student_id=st.student_id,
                session_id=s.session_id
            )
            .all()
        )

        for p in progress_rows:

            if (
                p.session_completion_status
                == "Completed"
            ):
                scores.append(100)

            elif (
                p.session_completion_status
                == "Partially Completed"
            ):
                scores.append(50)

    attempts = (
        QuizAttempt.query
        .filter_by(
            student_id=st.student_id
        )
        .all()
    )

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
        round(
            sum(quiz_scores)
            / len(quiz_scores)
        )
        if quiz_scores
        else 0
    )

    parent = (
        db.session.get(
            Parent,
            st.parent_id
        )
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
                round(
                    sum(scores)
                    / len(scores)
                )
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

@tutor_bp.route(
    "/dashboard",
    methods=["GET"]
)
@tutor_required
def dashboard():

    tutor = current_tutor()

    if not tutor:
        return fail(
            "Tutor not found",
            404
        )

    tid = tutor.tutor_id

    sessions = (
        Session.query
        .filter_by(
            tutor_id=tid
        )
        .order_by(
            Session.session_date,
            Session.start_time
        )
        .all()
    )

    student_ids = {
        booking.student_id
        for s in sessions
        for booking in (
            SessionBooking.query
            .filter_by(
                session_id=s.session_id
            )
            .all()
        )
    }

    open_doubts = (
        Doubt.query
        .filter_by(
            tutor_id=tid,
            status="Open"
        )
        .count()
    )

    pending = (
        AssignmentSubmission.query
        .join(Assignment)
        .join(Session)
        .filter(
            Session.tutor_id == tid,
            AssignmentSubmission.status.in_(
                [
                    "Pending",
                    "In Progress",
                    "Late",
                ]
            )
        )
        .count()
    )

    classes_today = (
        Session.query
        .filter_by(
            tutor_id=tid,
            session_date=_local_now().date()
        )
        .count()
    )

    unread = (
        Notification.query
        .filter_by(
            recipient_type="Tutor",
            recipient_id=tid,
            is_read=False
        )
        .count()
    )

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
        .filter_by(
            tutor_id=tid
        )
        .order_by(
            Doubt.asked_at.desc()
        )
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
        .filter_by(
            tutor_id=tid
        )
        .order_by(
            MeetingRequest.meeting_date
        )
        .limit(5)
        .all()
    )

    for m in meeting_rows:

        meetings.append({
            "meetingId": f"meet-{m.meeting_id}",
            "day": (
                m.meeting_date.strftime(
                    "%d %b %Y"
                )
            ),
            "title": "Meeting",
            "time": (
                m.meeting_date.strftime(
                    "%I:%M %p"
                )
            ),
            "meta": (
                m.meeting_reason
                or "Student/Parent meeting"
            ),
        })

    deadlines = []

    assignment_rows = (
        Assignment.query
        .join(Session)
        .filter(
            Session.tutor_id == tid
        )
        .order_by(
            Assignment.due_date
        )
        .limit(5)
        .all()
    )

    for a in assignment_rows:

        deadlines.append({
            "deadlineId":
                f"a-{a.assignment_id}",

            "day": (
                a.due_date.strftime(
                    "%d %b %Y"
                )
                if a.due_date
                else "No due date"
            ),

            "title": a.title,
            "meta": (
                a.description
                or "Assignment"
            ),
            "badge": "warn",
        })

    leaderboard = []

    students = [
        student_item(s)
        for s in (
            Student.query
            .filter(
                Student.status == "Active"
            )
            .all()
        )
    ]

    students = [
        x
        for x in students
        if x
    ]

    students = sorted(
        students,
        key=lambda x:
            x["progress"]["weeklyScore"],
        reverse=True
    )[:5]

    for rank, student in enumerate(
        students,
        1
    ):
        leaderboard.append({
            "rank": rank,
            "studentId":
                student["studentId"],
            "name":
                student["name"],
            "score":
                student["progress"]["weeklyScore"],
            "trend": "",
        })

    return ok({

        "stats": stats,

        "overview": [
            {
                "id": "doubts",
                "label":
                    "Doubts requiring replies",
                "value": open_doubts,
                "tone": "coral",
                "go": "doubts",
            },
            {
                "id": "grading",
                "label":
                    "Assignments pending grading",
                "value": pending,
                "tone": "amber",
                "go": "assignments",
            },
            {
                "id": "classes",
                "label":
                    "Classes scheduled today",
                "value": classes_today,
                "tone": "lime",
                "go": "schedule",
            },
            {
                "id": "meeting",
                "label": "Meetings",
                "value": (
                    MeetingRequest.query
                    .filter_by(
                        tutor_id=tid
                    )
                    .count()
                ),
                "tone": "blue",
                "go": "messages",
            },
            {
                "id": "homework",
                "label":
                    "Homework pending review",
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
# SCHEDULE - GET
# =========================================================

@tutor_bp.route(
    "/schedule",
    methods=["GET"]
)
@tutor_required
def schedule():

    tutor = current_tutor()

    if not tutor:
        return fail(
            "Tutor not found",
            404
        )

    sessions = (
        Session.query
        .filter_by(
            tutor_id=tutor.tutor_id
        )
        .order_by(
            Session.session_date,
            Session.start_time
        )
        .all()
    )

    # A one-to-one request is not a scheduled tutor meeting until approved.
    # Keep pending/change-request records exclusively in Messages.
    pending_meeting_session_ids = {
        m.session_id
        for m in MeetingRequest.query.filter_by(tutor_id=tutor.tutor_id)
        .filter(MeetingRequest.status.in_(("Pending Approval", "Reschedule Requested")))
        .all()
        if m.session_id
    }
    sessions = [
        s for s in sessions
        if s.session_id not in pending_meeting_session_ids
    ]

    # -----------------------------------------------------
    # SUBJECTS AVAILABLE TO THIS TUTOR
    # -----------------------------------------------------

    subject_ids = get_tutor_subject_ids(
        tutor
    )

    # If tutor has no configured subjects,
    # return all subjects so the schedule page
    # can still display available subjects.
    if not subject_ids:

        subject_ids = {
            subject.subject_id
            for subject in (
                Subject.query
                .order_by(
                    Subject.subject_name
                )
                .all()
            )
        }

    subjects = [
        {
            "subjectId":
                subject.subject_id,
            "subject":
                subject.subject_name,
        }
        for subject in (
            Subject.query
            .filter(
                Subject.subject_id.in_(
                    subject_ids
                )
            )
            .order_by(
                Subject.subject_name
            )
            .all()
        )
    ]

    # -----------------------------------------------------
    # TIME SLOTS
    # -----------------------------------------------------

    times = sorted({
        s.start_time.strftime("%H:%M")
        for s in sessions
        if s.start_time
    })

    if not times:
        times = [
            "16:00",
            "17:30",
            "19:00",
        ]

    # -----------------------------------------------------
    # WEEKLY GRID
    # Monday -> Saturday
    # -----------------------------------------------------

    rows = []

    for tm in times:

        row = {
            "time": datetime.strptime(
                tm,
                "%H:%M"
            ).strftime("%I:%M %p"),

            "days": [],
        }

        for day_number in range(6):

            found = next(
                (
                    s
                    for s in sessions
                    if (
                        s.session_date
                        and
                        s.session_date.weekday()
                        == day_number
                        and
                        s.start_time
                        and
                        s.start_time.strftime(
                            "%H:%M"
                        ) == tm
                    )
                ),
                None,
            )

            if found:

                row["days"].append({
                    "t":
                        subject_name(
                            found.subject_id
                        ),
                    "s":
                        found.session_type,
                    "sessionId":
                        found.session_id,
                    "status":
                        found.status,
                })

            else:

                row["days"].append(None)

        rows.append(row)

    # -----------------------------------------------------
    # CALENDAR EVENTS
    # -----------------------------------------------------

    events = [
        {
            "eventId":
                s.session_id,

            "sessionId":
                s.session_id,

            "date":
                s.session_date.isoformat(),

            "title":
                subject_name(
                    s.subject_id
                ),

            "type":
                s.status,

            "startTime":
                s.start_time.strftime(
                    "%H:%M"
                ),

            "endTime":
                s.end_time.strftime(
                    "%H:%M"
                ),
        }
        for s in sessions
        if s.session_date
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
# SCHEDULE - CREATE CLASS
# =========================================================

@tutor_bp.route(
    "/schedule/class",
    methods=["POST"]
)
@tutor_required
def add_class():

    tutor = current_tutor()

    if not tutor:
        return fail(
            "Tutor not found",
            404
        )

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        subject_id = int(
            data.get("subject_id")
        )
        student_id = int(data.get("student_id")) if data.get("student_id") not in (None, "") else None

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

    except (
        TypeError,
        ValueError
    ):

        return fail(
            "subject_id, session_date, "
            "start_time and end_time are required"
        )

    try:
        meeting_link = clean_optional_url(data.get("meeting_link") or data.get("meeting_url"))
    except ValueError as exc:
        return fail(str(exc))

    # -----------------------------------------------------
    # SUBJECT VALIDATION
    # -----------------------------------------------------

    selected_subject = db.session.get(
        Subject,
        subject_id
    )

    if not selected_subject:
        return fail(
            "Subject not found",
            404
        )

    if not tutor_has_subject(
        tutor,
        subject_id
    ):
        return fail(
            "You can only schedule sessions "
            "for subjects assigned to your tutor profile.",
            403
        )

    selected_student = None
    if student_id is not None:
        selected_student = db.session.get(Student, student_id)
        if not selected_student:
            return fail("Student not found", 404)
        if not StudentSubject.query.filter_by(student_id=student_id, subject_id=subject_id).first():
            return fail("The selected student is not enrolled in this subject.", 403)

    # -----------------------------------------------------
    # TIME VALIDATION
    # -----------------------------------------------------

    if start_time >= end_time:

        return fail(
            "End time must be after start time"
        )

    # -----------------------------------------------------
    # OVERLAPPING SESSION CHECK
    # -----------------------------------------------------

    existing_sessions = (
        Session.query
        .filter_by(
            tutor_id=tutor.tutor_id,
            session_date=session_date
        )
        .all()
    )

    for existing in existing_sessions:

        if (
            start_time < existing.end_time
            and
            end_time > existing.start_time
        ):

            return fail(
                "The tutor already has another "
                "session scheduled during this time.",
                409
            )

    # -----------------------------------------------------
    # CREATE SESSION
    # -----------------------------------------------------

    s = Session(
        tutor_id=tutor.tutor_id,
        subject_id=subject_id,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time,
        session_type="One-to-One" if student_id is not None else data.get("session_type", "Regular"),
        status="Scheduled",
        meeting_url=meeting_link,
    )

    db.session.add(s)
    db.session.flush()

    if selected_student:
        db.session.add(SessionBooking(session_id=s.session_id, student_id=selected_student.student_id, booking_status="Confirmed"))
        if selected_student.parent_id:
            db.session.add(Notification(
                recipient_type="Parent", recipient_id=selected_student.parent_id,
                title=f"{subject_name(subject_id)} session scheduled",
                message=f"{tutor.tutor_name} scheduled a one-on-one {subject_name(subject_id)} session with {selected_student.student_name} for {session_date.strftime('%d %b %Y')}, {start_time.strftime('%I:%M %p')}–{end_time.strftime('%I:%M %p')}.",
                notification_type="Meeting Scheduled", action_url=f"/parent/schedule?session_id={s.session_id}"
            ))
        db.session.add(Notification(
            recipient_type="Student", recipient_id=selected_student.student_id,
            title=f"{subject_name(subject_id)} session scheduled",
            message=f"{tutor.tutor_name} scheduled your one-on-one {subject_name(subject_id)} session for {session_date.strftime('%d %b %Y')}, {start_time.strftime('%I:%M %p')}–{end_time.strftime('%I:%M %p')}.",
            notification_type="Meeting Scheduled", action_url=f"/student/sessions?session_id={s.session_id}"
        ))
    else:
        # Notify enrolled students only for genuinely bookable regular sessions.
        # The existing notification read state drives the Session Booking badge.
        enrolled_students = (
            Student.query
            .join(StudentSubject, StudentSubject.student_id == Student.student_id)
            .filter(StudentSubject.subject_id == subject_id)
            .all()
        )
        display_date = session_date.strftime('%d %b %Y')
        display_time = f"{start_time.strftime('%I:%M %p')}–{end_time.strftime('%I:%M %p')}"
        for student in enrolled_students:
            db.session.add(Notification(
                recipient_type="Student",
                recipient_id=student.student_id,
                title=f"New {subject_name(subject_id)} session available",
                message=f"A new {subject_name(subject_id)} session with {tutor.tutor_name} is available to book for {display_date}, {display_time}.",
                notification_type="Session Available",
                action_url=f"/student/booking?session_id={s.session_id}",
            ))
    db.session.commit()

    # -----------------------------------------------------
    # GOOGLE MEET
    # -----------------------------------------------------

    meet_message = "Session created"

    try:

        if not s.meeting_url:
            s.meeting_url = (
                create_meeting_space()
            )

            db.session.commit()

            meet_message = (
                "Session created with Google Meet"
            )
        else:
            meet_message = "Session created with meeting link"

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
            "session":
                session_item(s),

            "meeting_url":
                s.meeting_url,
        },
        meet_message,
        201,
    )


# =========================================================
# SCHEDULE - UPDATE CLASS
# =========================================================

@tutor_bp.route(
    "/schedule/class/<int:session_id>",
    methods=["PUT"]
)
@tutor_required
def update_class(session_id):

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

    if s.status == "Live":
        return fail(
            "A live class cannot be rescheduled.",
            400
        )

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        if data.get("student_id") is not None:
            new_student_id = int(data.get("student_id"))
            new_student = db.session.get(Student, new_student_id)
            if not new_student:
                return fail("Student not found", 404)
            if not StudentSubject.query.filter_by(student_id=new_student_id, subject_id=s.subject_id).first():
                return fail("The selected student is not enrolled in this subject.", 403)
            current_bookings = SessionBooking.query.filter_by(session_id=session_id).all()
            for booking in current_bookings:
                booking.booking_status = "Cancelled"
            existing_booking = SessionBooking.query.filter_by(session_id=session_id, student_id=new_student_id).first()
            if existing_booking:
                existing_booking.booking_status = "Confirmed"
            else:
                db.session.add(SessionBooking(session_id=session_id, student_id=new_student_id, booking_status="Confirmed"))

        if data.get("subject_id") is not None:

            subject_id = int(
                data.get("subject_id")
            )

            if not db.session.get(
                Subject,
                subject_id
            ):
                return fail(
                    "Subject not found",
                    404
                )

            if not tutor_has_subject(
                tutor,
                subject_id
            ):
                return fail(
                    "You can only schedule sessions "
                    "for subjects assigned to your tutor profile.",
                    403
                )

            s.subject_id = subject_id

        if data.get("session_date"):

            s.session_date = (
                datetime.strptime(
                    data["session_date"],
                    "%Y-%m-%d"
                ).date()
            )

        if data.get("start_time"):

            s.start_time = (
                datetime.strptime(
                    data["start_time"],
                    "%H:%M"
                ).time()
            )

        if data.get("end_time"):

            s.end_time = (
                datetime.strptime(
                    data["end_time"],
                    "%H:%M"
                ).time()
            )

        if "meeting_link" in data or "meeting_url" in data:
            s.meeting_url = clean_optional_url(
                data.get("meeting_link")
                if "meeting_link" in data
                else data.get("meeting_url")
            )

    except (
        TypeError,
        ValueError
    ) as exc:

        return fail(
            str(exc) if str(exc) == "Meeting Link must be a valid URL" else "Invalid schedule data"
        )

    if s.start_time >= s.end_time:

        return fail(
            "End time must be after start time"
        )

    # Check conflicts excluding this session.
    conflicts = (
        Session.query
        .filter(
            Session.tutor_id == tutor.tutor_id,
            Session.session_id != session_id,
            Session.session_date == s.session_date
        )
        .all()
    )

    for existing in conflicts:

        if (
            s.start_time < existing.end_time
            and
            s.end_time > existing.start_time
        ):
            return fail(
                "The tutor already has another "
                "session scheduled during this time.",
                409
            )

    if data.get("session_type") is not None:

        s.session_type = (
            data.get("session_type")
        )

    s.status = "Rescheduled"
    s.meeting_started_at = None
    s.meeting_ended_at = None
    s.meeting_duration_seconds = None
    # Keep the single Session record as the source of truth and update any
    # linked parent meeting request to the new schedule.
    linked_meeting = MeetingRequest.query.filter_by(session_id=s.session_id).first()
    if linked_meeting:
        linked_meeting.meeting_date = datetime.combine(s.session_date, s.start_time)
        linked_meeting.status = "Rescheduled"

    for booking in SessionBooking.query.filter_by(session_id=s.session_id, booking_status="Confirmed").all():
        student = db.session.get(Student, booking.student_id)
        if student:
            db.session.add(Notification(
                recipient_type="Student", recipient_id=student.student_id,
                title=f"{subject_name(s.subject_id)} schedule updated",
                message=f"Your {subject_name(s.subject_id)} session was rescheduled to {s.session_date.strftime('%d %b %Y')} from {s.start_time.strftime('%I:%M %p')} to {s.end_time.strftime('%I:%M %p')}.",
                notification_type="Session Updated", action_url=f"/student/sessions?session_id={s.session_id}"
            ))
            if student.parent_id:
                db.session.add(Notification(
                    recipient_type="Parent", recipient_id=student.parent_id,
                    title=f"{subject_name(s.subject_id)} schedule updated",
                    message=f"{student.student_name}'s session was rescheduled to {s.session_date.strftime('%d %b %Y')} from {s.start_time.strftime('%I:%M %p')} to {s.end_time.strftime('%I:%M %p')}.",
                    notification_type="Session Updated", action_url=f"/parent/schedule?session_id={s.session_id}"
                ))

    db.session.commit()

    return ok(
        {
            "session":
                session_item(s)
        },
        "Class rescheduled"
    )


# =========================================================
# SCHEDULE - DELETE/CANCEL CLASS
# =========================================================

@tutor_bp.route(
    "/schedule/class/<int:session_id>",
    methods=["DELETE"]
)
@tutor_required
def delete_class(session_id):

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

    if s.status == "Live":
        return fail(
            "A live class cannot be deleted.",
            400
        )

    # Notify booked students before deletion.
    bookings = (
        SessionBooking.query
        .filter_by(
            session_id=session_id
        )
        .all()
    )

    subject_label = subject_name(
        s.subject_id
    )

    # Parent-created meetings may not have a SessionBooking (for example,
    # a parent-only one-to-one request). Keep the linked request available
    # until recipients have been notified.
    linked_meeting = (
        MeetingRequest.query
        .filter_by(session_id=session_id)
        .first()
    )

    for booking in bookings:

        db.session.add(
            Notification(
                recipient_type="Student",
                recipient_id=booking.student_id,
                title="Class cancelled",
                message=(
                    f"Your {subject_label} class "
                    "has been cancelled."
                ),
                notification_type="Session Update",
            )
        )

        student = db.session.get(Student, booking.student_id)
        if student and student.parent_id:
            db.session.add(Notification(
                recipient_type="Parent", recipient_id=student.parent_id,
                title="Class cancelled",
                message=f"{student.student_name}'s {subject_label} class has been cancelled.",
                notification_type="Session Update",
                action_url="/parent/schedule",
            ))

    # Also notify the direct participants of a linked parent-created
    # meeting. Avoid duplicates when the student/parent was already notified
    # through a confirmed SessionBooking above.
    notified_student_ids = {booking.student_id for booking in bookings}
    notified_parent_ids = set()

    for booking in bookings:
        booked_student = db.session.get(Student, booking.student_id)
        if booked_student and booked_student.parent_id:
            notified_parent_ids.add(booked_student.parent_id)

    if linked_meeting:
        if (
            linked_meeting.student_id
            and linked_meeting.student_id not in notified_student_ids
        ):
            linked_student = db.session.get(
                Student,
                linked_meeting.student_id
            )
            db.session.add(Notification(
                recipient_type="Student",
                recipient_id=linked_meeting.student_id,
                title="Meeting cancelled",
                message=f"Your {subject_label} meeting has been cancelled by the tutor.",
                notification_type="Meeting Cancelled",
                action_url="/student/sessions",
            ))
            if (
                linked_student
                and linked_student.parent_id
                and linked_student.parent_id not in notified_parent_ids
                and linked_student.parent_id != linked_meeting.parent_id
            ):
                db.session.add(Notification(
                    recipient_type="Parent",
                    recipient_id=linked_student.parent_id,
                    title="Meeting cancelled",
                    message=f"{linked_student.student_name}'s {subject_label} meeting has been cancelled by the tutor.",
                    notification_type="Meeting Cancelled",
                    action_url="/parent/meetings",
                ))
                notified_parent_ids.add(linked_student.parent_id)

        if (
            linked_meeting.parent_id
            and linked_meeting.parent_id not in notified_parent_ids
        ):
            db.session.add(Notification(
                recipient_type="Parent",
                recipient_id=linked_meeting.parent_id,
                title="Meeting cancelled",
                message=f"The {subject_label} meeting has been cancelled by the tutor.",
                notification_type="Meeting Cancelled",
                action_url="/parent/meetings",
            ))

    # Remove dependent records.
    LearningProgress.query.filter_by(
        session_id=session_id
    ).delete()

    AttendanceRecord.query.filter_by(
        session_id=session_id
    ).delete()

    SessionBooking.query.filter_by(
        session_id=session_id
    ).delete()

    SessionUpdate.query.filter_by(
        session_id=session_id
    ).delete()

    # Assignments linked to the session.
    assignments = (
        Assignment.query
        .filter_by(
            session_id=session_id
        )
        .all()
    )

    for assignment in assignments:

        AssignmentSubmission.query.filter_by(
            assignment_id=assignment.assignment_id
        ).delete()

        db.session.delete(
            assignment
        )

    # Study resources linked to session.
    resources = (
        StudyResource.query
        .filter_by(
            session_id=session_id
        )
        .all()
    )

    for resource in resources:

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

    # Meeting requests linked to session.
    MeetingRequest.query.filter_by(
        session_id=session_id
    ).delete()

    db.session.delete(s)

    db.session.commit()

    return ok(
        message="Class cancelled and deleted"
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

    s = db.session.get(
        Session,
        session_id
    )

    if (
        not tutor
        or not s
        or s.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Session not found",
            404
        )

    linked_request = MeetingRequest.query.filter_by(session_id=s.session_id, tutor_id=tutor.tutor_id).first()
    if linked_request and linked_request.status in ("Pending Approval", "Reschedule Requested"):
        return fail("This one-to-one meeting is waiting for tutor approval.", 409)

    if s.status not in (
        "Scheduled",
        "Rescheduled",
        "Live",
    ):
        return fail(
            "This session is not available to start.",
            400
        )

    if meeting_lifecycle(s)["status"] == "Meeting Ended":
        return fail("This session has already ended and cannot be started.", 400)

    try:

        if not s.meeting_url:

            s.meeting_url = (
                create_meeting_space()
            )

        now = _local_now()

        if s.status != "Live":

            s.status = "Live"

            s.meeting_started_at = now
            s.meeting_ended_at = None
            s.meeting_duration_seconds = None

        subject = db.session.get(
            Subject,
            s.subject_id
        )

        subject_label = (
            subject.subject_name
            if subject
            else "class"
        )
        meeting_type = "One-to-One" if s.session_type == "One-to-One" else "Regular"
        display_date = s.session_date.strftime("%d %b %Y")
        display_time = f"{s.start_time.strftime('%I:%M %p')}–{s.end_time.strftime('%I:%M %p')}"

        bookings = (
            SessionBooking.query
            .filter_by(session_id=s.session_id, booking_status="Confirmed")
            .all()
        )

        for booking in bookings:
            existing = (
                Notification.query
                .filter_by(
                    recipient_type="Student",
                    recipient_id=booking.student_id,
                    notification_type="Class Started",
                    is_read=False,
                )
                .filter(Notification.action_url == f"/student/sessions?session_id={s.session_id}")
                .first()
            )
            if not existing:
                db.session.add(Notification(
                    recipient_type="Student",
                    recipient_id=booking.student_id,
                    title=f"{meeting_type} {subject_label} meeting started",
                    message=f"{tutor.tutor_name} started your {meeting_type} {subject_label} meeting on {display_date}, {display_time}. Join the meeting now: {s.meeting_url}",
                    notification_type="Class Started",
                    action_url=f"/student/sessions?session_id={s.session_id}",
                ))

            student = db.session.get(Student, booking.student_id)
            if student and student.parent_id:
                parent_existing = (
                    Notification.query
                    .filter_by(
                        recipient_type="Parent",
                        recipient_id=student.parent_id,
                        notification_type="Class Started",
                        is_read=False,
                    )
                    .filter(Notification.action_url == f"/parent/schedule?session_id={s.session_id}")
                    .first()
                )
                if not parent_existing:
                    db.session.add(Notification(
                        recipient_type="Parent",
                        recipient_id=student.parent_id,
                        title=f"{subject_label} class has started",
                        message=f"{tutor.tutor_name} has started {student.student_name}'s {subject_label} class. The meeting is now available.",
                        notification_type="Class Started",
                        action_url=f"/parent/schedule?session_id={s.session_id}",
                    ))

        parent_meeting = MeetingRequest.query.filter_by(session_id=s.session_id, tutor_id=tutor.tutor_id).first()
        if parent_meeting and parent_meeting.parent_id:
            parent_existing = Notification.query.filter_by(
                recipient_type="Parent", recipient_id=parent_meeting.parent_id,
                notification_type="Class Started", is_read=False
            ).filter(Notification.action_url == f"/parent/meetings").first()
            if not parent_existing:
                db.session.add(Notification(
                    recipient_type="Parent",
                    recipient_id=parent_meeting.parent_id,
                    title=f"{meeting_type} {subject_label} meeting started",
                    message=f"{tutor.tutor_name} started the {meeting_type} {subject_label} meeting on {display_date}, {display_time}. Join the meeting now: {s.meeting_url}",
                    notification_type="Class Started",
                    action_url="/parent/meetings"
                ))

        db.session.commit()

        return ok(
            {
                "session":
                    session_item(s),

                "meeting_url":
                    s.meeting_url,

                "started_at":
                    (
                        s.meeting_started_at.isoformat()
                        if s.meeting_started_at
                        else None
                    ),
            },
            "Class started. Students notified."
        )

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
            503
        )

    except Exception as exc:

        db.session.rollback()

        current_app.logger.exception(
            "Google Meet start failed: %s",
            exc
        )

        return fail(
            "Google Meet could not be started. "
            "Check the backend terminal for the "
            "Google API error.",
            502
        )


# =========================================================
# END CLASS
# =========================================================

@tutor_bp.route(
    "/schedule/class/<int:session_id>/end",
    methods=["POST"]
)
@tutor_required
def end_class(session_id):

    tutor = current_tutor()

    s = db.session.get(
        Session,
        session_id
    )

    if (
        not tutor
        or not s
        or s.tutor_id != tutor.tutor_id
    ):
        return fail(
            "Session not found",
            404
        )

    if s.status != "Live":

        return fail(
            "Only a live class can be ended.",
            400
        )

    now = _local_now()

    s.status = "Completed"

    s.meeting_ended_at = now

    if s.meeting_started_at:

        s.meeting_duration_seconds = max(
            0,
            int(
                (
                    now
                    - s.meeting_started_at
                ).total_seconds()
            )
        )

    subject_label = subject_name(
        s.subject_id
    )
    meeting_type = "One-to-One" if s.session_type == "One-to-One" else "Regular"
    display_date = s.session_date.strftime("%d %b %Y")
    display_time = f"{s.start_time.strftime('%I:%M %p')}–{s.end_time.strftime('%I:%M %p')}"

    bookings = (
        SessionBooking.query
        .filter_by(session_id=s.session_id, booking_status="Confirmed")
        .all()
    )

    for booking in bookings:
        db.session.add(Notification(
            recipient_type="Student",
            recipient_id=booking.student_id,
            title=f"{subject_label} class ended",
            message=f"Your {subject_label} class has ended. If you attended, you can mark the session as completed.",
            notification_type="Class Completed",
            action_url=f"/student/sessions?session_id={s.session_id}",
        ))
        student = db.session.get(Student, booking.student_id)
        if student and student.parent_id:
            db.session.add(Notification(
                recipient_type="Parent",
                recipient_id=student.parent_id,
                title=f"{subject_label} class ended",
                message=f"The {subject_label} session for {student.student_name} has ended. Attendance will reflect the student's completion or tutor confirmation.",
                notification_type="Class Completed",
                action_url=f"/parent/schedule?session_id={s.session_id}",
            ))

    parent_meeting = MeetingRequest.query.filter_by(session_id=s.session_id, tutor_id=tutor.tutor_id).first()
    if parent_meeting and parent_meeting.parent_id:
        db.session.add(Notification(
            recipient_type="Parent",
            recipient_id=parent_meeting.parent_id,
            title=f"{meeting_type} {subject_label} meeting completed",
            message=f"The {meeting_type} {subject_label} meeting on {display_date}, {display_time} has been completed.",
            notification_type="Class Completed",
            action_url="/parent/meetings"
        ))

    linked_meeting = MeetingRequest.query.filter_by(
        session_id=s.session_id,
        tutor_id=tutor.tutor_id,
    ).first()
    if linked_meeting:
        linked_meeting.status = "Completed"

    db.session.commit()

    return ok(
        {
            "session":
                session_item(s),

            "meeting_url":
                s.meeting_url,

            "ended_at":
                s.meeting_ended_at.isoformat(),

            "duration_seconds":
                s.meeting_duration_seconds or 0,
        },
        "Class ended. Attendance remains based on student completion or tutor confirmation."
    )


# =========================================================
# PARENT MEETING REQUESTS / SESSION DETAILS
# =========================================================

@tutor_bp.route('/meetings/requests', methods=['GET'])
@tutor_required
def meeting_requests():
    tutor = current_tutor()
    rows = MeetingRequest.query.filter_by(tutor_id=tutor.tutor_id).order_by(MeetingRequest.meeting_date.asc()).all()
    data = []
    for m in rows:
        if not m.session_id:
            continue
        sess = db.session.get(Session, m.session_id)
        student = db.session.get(Student, m.student_id) if m.student_id else None
        # A parent is only shown when the parent genuinely created/is part of
        # this meeting. A stray parent_id on a Student- or Tutor-created
        # meeting must never surface as "Parent: [Name]" on the tutor side.
        parent = db.session.get(Parent, m.parent_id) if (m.parent_id and m.creator_type == 'Parent') else None
        subject = db.session.get(Subject, sess.subject_id) if sess else None
        display_status = m.status
        if m.status == 'Pending Approval':
            display_status = 'Tutor Approval Pending'
        elif m.status == 'Scheduled':
            display_status = 'Approved'
        data.append({
            'meeting_id': m.meeting_id, 'session_id': m.session_id, 'status': m.status,
            'display_status': display_status,
            'date': sess.session_date.isoformat() if sess else m.meeting_date.date().isoformat(),
            'start_time': sess.start_time.strftime('%H:%M') if sess else m.meeting_date.strftime('%H:%M'),
            'end_time': sess.end_time.strftime('%H:%M') if sess else None,
            'student_id': student.student_id if student else None, 'student_name': student.student_name if student else None,
            'parent_id': parent.parent_id if parent else None, 'parent_name': parent.parent_name if parent else None,
            'creator_type': m.creator_type,
            'subject': subject.subject_name if subject else 'General', 'reason': m.meeting_reason or '',
            'denial_reason': m.denial_reason,
            'session_type': sess.session_type if sess else 'One-to-One', 'meeting_link': (sess.meeting_url if sess and sess.meeting_url else m.meeting_link),
            'meeting_started_at': sess.meeting_started_at.isoformat() if sess and sess.meeting_started_at else None, 'meeting_ended_at': sess.meeting_ended_at.isoformat() if sess and sess.meeting_ended_at else None,
        })
    return ok({'requests': data})


@tutor_bp.route('/meetings/<int:meeting_id>/decision', methods=['POST'])
@tutor_required
def decide_meeting(meeting_id):
    tutor = current_tutor()
    meeting = db.session.get(MeetingRequest, meeting_id)
    if not meeting or meeting.tutor_id != tutor.tutor_id:
        return fail('Meeting request not found', 404)
    # Approval is idempotent: a repeated click returns the already accepted
    # meeting instead of creating another Meet/session or returning an error.
    if meeting.status == 'Scheduled':
        sess = db.session.get(Session, meeting.session_id) if meeting.session_id else None
        if sess and sess.meeting_url:
            return ok({
                'meeting_id': meeting.meeting_id,
                'session_id': sess.session_id,
                'status': meeting.status,
                'meeting_url': sess.meeting_url,
            }, 'Meeting request already accepted')
    if meeting.status not in ('Pending Approval', 'Reschedule Requested'):
        return fail('This meeting request has already been decided', 409)
    data = request.get_json(silent=True) or {}
    decision = str(data.get('decision') or '').strip().lower()
    sess = db.session.get(Session, meeting.session_id) if meeting.session_id else None
    if not sess:
        return fail('Shared session not found', 404)
    student = db.session.get(Student, meeting.student_id) if meeting.student_id else None
    # Only notify/reference the parent when the parent actually created this
    # meeting. A Student+Tutor meeting must never treat the parent as a
    # participant, even if parent_id is present on the record.
    parent = db.session.get(Parent, meeting.parent_id) if (meeting.parent_id and meeting.creator_type == 'Parent') else None
    subject = db.session.get(Subject, sess.subject_id)
    label = subject.subject_name if subject else 'session'
    if decision == 'approve':
        # Approval only changes the request into an official scheduled
        # session. Google Meet creation belongs to Start Meeting, not approval.
        meeting.status = 'Scheduled'
        meeting.denial_reason = None
        meeting.meeting_link = sess.meeting_url or None
        if not meeting.meeting_type:
            meeting.meeting_type = 'STUDENT_TUTOR' if meeting.creator_type == 'Student' else ('PARENT_TUTOR' if meeting.parent_id else 'TUTOR_STUDENT')
        sess.status = 'Scheduled'
        sess.meeting_started_at = None
        sess.meeting_ended_at = None
        sess.meeting_duration_seconds = None
        meeting_type = 'One-to-One' if sess.session_type == 'One-to-One' else 'Regular'
        message = f'Tutor {tutor.tutor_name} approved your {meeting_type} {label} meeting for {sess.session_date.strftime("%d %b %Y")}, {sess.start_time.strftime("%I:%M %p")}–{sess.end_time.strftime("%I:%M %p")}. The meeting is scheduled and will become joinable when the tutor starts it.'
        if student:
            db.session.add(Notification(recipient_type='Student', recipient_id=student.student_id, title=f'{label} meeting approved', message=message, notification_type='Meeting Approved', action_url=f'/student/sessions?session_id={sess.session_id}'))
        if parent:
            db.session.add(Notification(recipient_type='Parent', recipient_id=parent.parent_id, title=f'{label} meeting approved', message=message, notification_type='Meeting Approved', action_url=f'/parent/schedule?session_id={sess.session_id}'))
        with_whom = parent.parent_name if parent else (student.student_name if student else 'the student')
        db.session.add(Notification(
            recipient_type='Tutor', recipient_id=tutor.tutor_id,
            title=f'{meeting_type} {label} meeting approved',
            message=f'Your {meeting_type} meeting with {with_whom} is scheduled for {sess.session_date.strftime("%d %b %Y")}, {sess.start_time.strftime("%I:%M %p")}–{sess.end_time.strftime("%I:%M %p")}. Meeting link is ready.',
            notification_type='Meeting Approved',
            action_url=f'/tutor/schedule?session_id={sess.session_id}'
        ))
    elif decision in ('deny', 'decline'):
        reason = str(data.get('reason') or '').strip()
        if not reason:
            return fail('A denial reason is required.', 400)
        meeting.denial_reason = reason
        meeting.status = 'Denied'
        sess.status = 'Cancelled'
        message = f'Tutor {tutor.tutor_name} denied the {label} meeting scheduled for {sess.session_date.strftime("%d %b %Y")}, {sess.start_time.strftime("%I:%M %p")}. Reason: {reason}'
        if parent:
            db.session.add(Message(sender_type='Tutor', sender_id=tutor.tutor_id, receiver_type='Parent', receiver_id=parent.parent_id, subject=f'{label} meeting denied', message=message))
            db.session.add(Notification(recipient_type='Parent', recipient_id=parent.parent_id, title=f'{label} meeting denied', message=message, notification_type='Meeting Denied', action_url=f'/parent/meetings'))
        if student:
            db.session.add(Notification(recipient_type='Student', recipient_id=student.student_id, title=f'{label} meeting cancelled', message=message, notification_type='Meeting Denied', action_url=f'/student/sessions'))
    elif decision in ('change', 'request_change', 'reschedule'):
        reason = str(data.get('reason') or '').strip() or 'Tutor requested a different time.'
        proposed_date = data.get('session_date')
        proposed_start = data.get('start_time')
        proposed_end = data.get('end_time')
        if proposed_date and proposed_start and proposed_end:
            try:
                sess.session_date = datetime.strptime(proposed_date, '%Y-%m-%d').date()
                sess.start_time = datetime.strptime(proposed_start, '%H:%M').time()
                sess.end_time = datetime.strptime(proposed_end, '%H:%M').time()
            except ValueError:
                return fail('Invalid proposed date/time')
        meeting.status = 'Reschedule Requested'
        sess.status = 'Rescheduled'
        proposed = f' Preferred timing: {sess.session_date.strftime("%d %b %Y")}, {sess.start_time.strftime("%I:%M %p")}–{sess.end_time.strftime("%I:%M %p")}. ' if proposed_date and proposed_start and proposed_end else ' '
        message = f'Tutor {tutor.tutor_name} requested a change to the {label} meeting. Reason: {reason}.{proposed}You can schedule the meeting again from Connect with Your Child.'
        if parent:
            db.session.add(Message(sender_type='Tutor', sender_id=tutor.tutor_id, receiver_type='Parent', receiver_id=parent.parent_id, subject=f'{label} meeting change requested', message=message))
            db.session.add(Notification(recipient_type='Parent', recipient_id=parent.parent_id, title=f'{label} meeting change requested', message=message, notification_type='Meeting Change Requested', action_url=f'/parent/schedule?session_id={sess.session_id}'))
        if student:
            db.session.add(Notification(recipient_type='Student', recipient_id=student.student_id, title=f'{label} meeting change requested', message=message, notification_type='Meeting Change Requested', action_url=f'/student/sessions?session_id={sess.session_id}'))
    else:
        return fail('Decision must be approve, deny, or change')
    db.session.commit()
    return ok({'meeting_id': meeting.meeting_id, 'session_id': sess.session_id, 'status': meeting.status}, 'Meeting request updated')


@tutor_bp.route('/session/<int:session_id>/details', methods=['GET', 'PUT'])
@tutor_required
def session_details(session_id):
    tutor = current_tutor()
    sess = db.session.get(Session, session_id)
    if not sess or sess.tutor_id != tutor.tutor_id:
        return fail('Session not found', 404)
    bookings = SessionBooking.query.filter_by(session_id=session_id, booking_status='Confirmed').all()
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        records = data.get('records', [])
        for item in records:
            try: student_id = int(item.get('student_id') or item.get('studentId'))
            except (TypeError, ValueError): return fail('Invalid student_id')
            if not SessionBooking.query.filter_by(session_id=session_id, student_id=student_id, booking_status='Confirmed').first():
                return fail('Student is not booked for this session', 403)
            attendance_status = item.get('attendance_status', item.get('attendanceStatus'))
            pace = item.get('learning_pace', item.get('learningPace'))
            observation = item.get('observation', item.get('remarks'))
            if attendance_status not in (None, '', 'Present', 'Absent', 'Late', 'Pending'):
                return fail('Invalid attendance status')
            if pace not in (None, '', 'Fast', 'Average', 'Needs Practice'):
                return fail('Invalid learning pace')
            progress = LearningProgress.query.filter_by(session_id=session_id, student_id=student_id).first()
            if not progress:
                progress = LearningProgress(session_id=session_id, student_id=student_id, learning_pace=None)
                db.session.add(progress)
            if pace: progress.learning_pace = pace
            if observation is not None: progress.tutor_remarks = observation.strip() or None
            if attendance_status:
                record = AttendanceRecord.query.filter_by(tutor_id=tutor.tutor_id, session_id=session_id, student_id=student_id).first()
                old_status = record.status if record else None
                if not record:
                    record = AttendanceRecord(tutor_id=tutor.tutor_id, session_id=session_id, student_id=student_id, status=attendance_status, date=sess.session_date)
                    db.session.add(record)
                else:
                    record.status = attendance_status; record.date = sess.session_date
                if attendance_status in ('Present', 'Absent', 'Late') and old_status != attendance_status:
                    student_obj = db.session.get(Student, student_id)
                    subject_label = subject_name(sess.subject_id)
                    result_label = 'attended' if attendance_status == 'Present' else ('was marked not attended' if attendance_status == 'Absent' else 'was marked late')
                    db.session.add(Notification(recipient_type='Student', recipient_id=student_id, title=f'Attendance updated · {subject_label}', message=f'Tutor {tutor.tutor_name} confirmed that you {result_label} for the {subject_label} session on {sess.session_date.strftime("%d %b %Y")}.', notification_type='Attendance Confirmation', action_url=f'/student/sessions?session_id={session_id}'))
                    if student_obj and student_obj.parent_id:
                        db.session.add(Notification(recipient_type='Parent', recipient_id=student_obj.parent_id, title=f'Attendance confirmed · {subject_label}', message=f'Tutor {tutor.tutor_name} confirmed that {student_obj.student_name} {result_label} for the {subject_label} session on {sess.session_date.strftime("%d %b %Y")}.', notification_type='Attendance Confirmation', action_url=f'/parent/progress?student_id={student_id}&session_id={session_id}'))
                if attendance_status in ('Present', 'Late'):
                    progress.session_completion_status = 'Completed'
                    progress.completion_source = 'Tutor'
                    if not progress.completed_at: progress.completed_at = _local_now()
                elif attendance_status == 'Absent':
                    progress.session_completion_status = 'Not Attended'
                    progress.completion_source = 'Tutor'
                    progress.completed_at = None
            if progress.joined_at and sess.meeting_ended_at and not progress.duration_seconds:
                progress.duration_seconds = max(0, int((sess.meeting_ended_at - progress.joined_at).total_seconds()))
        db.session.commit()
        return ok(message='Session details saved and parent/student records updated')
    data = []
    for booking in bookings:
        student = db.session.get(Student, booking.student_id)
        if not student: continue
        parent = db.session.get(Parent, student.parent_id) if student.parent_id else None
        attendance = AttendanceRecord.query.filter_by(tutor_id=tutor.tutor_id, session_id=session_id, student_id=student.student_id).first()
        progress = LearningProgress.query.filter_by(session_id=session_id, student_id=student.student_id).first()
        data.append({
            'student_id': student.student_id, 'student_name': student.student_name, 'parent_name': parent.parent_name if parent else None,
            'attendance_status': attendance.status if attendance else None,
            'learning_pace': progress.learning_pace if progress and progress.learning_pace else None,
            'observation': progress.tutor_remarks if progress else None,
            'completion_status': progress.session_completion_status if progress else None,
            'joined_at': progress.joined_at.isoformat() if progress and progress.joined_at else None,
            'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None,
        })
    return ok({'session': session_item(sess), 'records': data})


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
            for s in (
                Student.query
                .filter_by(
                    status="Active"
                )
                .all()
            )
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
            )
            or {}
        ).get(
            "records",
            []
        )

        for item in records:

            try:
                student_id = int(
                    item.get("studentId")
                )
            except (
                TypeError,
                ValueError
            ):
                return fail(
                    "Invalid studentId"
                )

            session_id = item.get(
                "sessionId"
            )

            status = item.get(
                "status",
                "Present"
            )
            if status not in {"Present", "Absent", "Late", "Pending"}:
                return fail("Invalid attendance status")

            existing = (
                AttendanceRecord.query
                .filter_by(
                    tutor_id=tutor.tutor_id,
                    student_id=student_id,
                    session_id=session_id,
                )
                .first()
            )

            old_status = existing.status if existing else None
            session_obj = db.session.get(Session, int(session_id)) if session_id else None
            record_date = session_obj.session_date if session_obj and session_obj.session_date else date.today()
            if existing:

                existing.status = status
                existing.date = record_date

            else:

                existing = AttendanceRecord(
                    tutor_id=tutor.tutor_id,
                    student_id=student_id,
                    session_id=session_id,
                    status=status,
                    date=record_date,
                )
                db.session.add(existing)

            if status in {"Present", "Absent", "Late"} and old_status != status:
                student = db.session.get(Student, student_id)
                sess = db.session.get(Session, int(session_id)) if session_id else None
                if student:
                    subject_label = subject_name(sess.subject_id) if sess else "session"
                    result_label = "attended" if status == "Present" else ("marked not attended" if status == "Absent" else "marked late")
                    db.session.add(Notification(
                        recipient_type="Student", recipient_id=student.student_id,
                        title=f"Attendance updated · {subject_label}",
                        message=f"The tutor confirmed that you were {result_label} for the {subject_label} session.",
                        notification_type="Attendance Confirmation",
                        action_url=f"/student/sessions?session_id={session_id}",
                    ))
                    if student.parent_id:
                        db.session.add(Notification(
                            recipient_type="Parent",
                            recipient_id=student.parent_id,
                            title=f"Attendance confirmed · {subject_label}",
                            message=f"The tutor confirmed that {student.student_name} was {result_label} for the {subject_label} session.",
                            notification_type="Attendance Confirmation",
                            action_url=f"/parent/progress?student_id={student.student_id}&session_id={session_id}",
                        ))

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
        "Pending": 0,
    }

    data = []

    for r in rows:

        counts[r.status] = (
            counts.get(
                r.status,
                0
            )
            + 1
        )

        student = db.session.get(Student, r.student_id)
        sess = db.session.get(Session, r.session_id) if r.session_id else None
        data.append({
            "attendanceId": r.attendance_id,
            "studentId": r.student_id,
            "studentName": student.student_name if student else f"Student #{r.student_id}",
            "sessionId": r.session_id,
            "subject": subject_name(sess.subject_id) if sess else "General",
            "sessionDate": sess.session_date.isoformat() if sess and sess.session_date else None,
            "status": r.status,
            "attendanceQuery": r.status == "Pending",
        })

    total = (
        sum(counts.values())
        or 1
    )

    analytics = [
        {
            "label": key,
            "value": round(
                value
                / total
                * 100
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

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        session_id = int(
            data.get("session_id")
        )

    except (
        TypeError,
        ValueError
    ):

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

            return fail(
                "Invalid next_session_date"
            )

    for booking in (
        SessionBooking.query
        .filter_by(
            session_id=session_id
        )
        .all()
    ):

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

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        try:

            session_id = int(
                data.get("session_id")
            )

        except (
            TypeError,
            ValueError
        ):

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

        db.session.add(
            assignment
        )

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
            else (
                "Submitted"
                if statuses
                else "Pending"
            )
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
                )
                if sess
                else "General",

            "submissions":
                f"{len(submissions)} submissions",

            "type":
                "assignment",

            "homeworkStatus":
                status,

            "sessionId":
                assignment.session_id,

            "dueDate":
                (
                    assignment.due_date.isoformat()
                    if assignment.due_date
                    else None
                ),
        })

    subject_ids = get_tutor_subject_ids(tutor)

    if not subject_ids:
        subject_ids = {
            subject.subject_id
            for subject in Subject.query.all()
        }

    linked_students = [
        {
            "studentId": student.student_id,
            "name": student.student_name,
        }
        for student in (
            Student.query
            .join(StudentSubject, StudentSubject.student_id == Student.student_id)
            .filter(
                StudentSubject.subject_id.in_(subject_ids),
                Student.status == "Active",
            )
            .order_by(Student.student_name)
            .distinct()
            .all()
        )
    ]

    return ok({
        "assignments": data,
        "students": linked_students,
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
    tutor = current_tutor()
    if not tutor:
        return fail("Tutor not found", 404)

    data = request.get_json(silent=True) or {}
    requested_subject = str(data.get("subject") or "").strip()
    topic = str(data.get("topic") or data.get("title") or "").strip()
    difficulty = str(data.get("difficulty") or "Medium").strip()
    try:
        question_count = int(data.get("question_count") or data.get("count") or 5)
    except (TypeError, ValueError):
        question_count = 5
    question_count = max(1, min(question_count, 10))

    subject_ids = get_tutor_subject_ids(tutor)
    if not subject_ids:
        subject_ids = {s.subject_id for s in Subject.query.all()}

    subjects = [
        subject_name(subject_id)
        for subject_id in sorted(subject_ids)
    ]
    subject = requested_subject or (subjects[0] if subjects else "General")

    sessions = (
        Session.query
        .filter(Session.tutor_id == tutor.tutor_id)
        .order_by(Session.session_date.desc(), Session.start_time.desc())
        .limit(12)
        .all()
    )
    session_data = [
        {
            "subject": subject_name(s.subject_id),
            "date": s.session_date.isoformat() if s.session_date else None,
            "status": s.status,
            "session_type": s.session_type,
        }
        for s in sessions
    ]

    student_ids = {
        booking.student_id
        for s in sessions
        for booking in SessionBooking.query.filter_by(session_id=s.session_id).all()
    }
    students = []
    for sid in sorted(student_ids):
        student = db.session.get(Student, sid)
        if not student:
            continue
        progress_rows = (
            LearningProgress.query
            .filter_by(student_id=sid)
            .order_by(LearningProgress.progress_id.desc())
            .limit(5)
            .all()
        )
        attempts = (
            QuizAttempt.query
            .filter_by(student_id=sid)
            .order_by(QuizAttempt.attempted_at.desc())
            .limit(5)
            .all()
        )
        attendance = (
            AttendanceRecord.query
            .filter_by(tutor_id=tutor.tutor_id, student_id=sid)
            .order_by(AttendanceRecord.date.desc())
            .limit(10)
            .all()
        )
        students.append({
            "learner": f"student_{len(students) + 1}",
            "progress": [
                {
                    "status": p.session_completion_status,
                    "learning_pace": p.learning_pace,
                    "remarks": p.tutor_remarks,
                }
                for p in progress_rows
            ],
            "quiz_attempts": [
                {
                    "score": a.score,
                    "attempted_at": a.attempted_at.isoformat() if a.attempted_at else None,
                }
                for a in attempts
            ],
            "attendance": [
                {
                    "status": a.status,
                    "date": a.date.isoformat() if a.date else None,
                }
                for a in attendance
            ],
        })

    payload = {
        "tutor": {
            "subjects": subjects,
        },
        "request": {
            "subject": subject,
            "topic": topic or "recent class topics",
            "difficulty": difficulty,
            "question_count": question_count,
        },
        "recent_sessions": session_data,
        "students": students,
    }

    prompt = (
        "You are Tutor AI for LearnAtHome. Generate quiz/practice questions "
        "for the tutor using only the exact requested subject, topic, "
        "difficulty, and question count below. Every question must directly "
        "test the requested topic; do not drift into adjacent topics. Do not "
        "invent student records. Return a JSON array of "
        "objects with question, option_a, option_b, option_c, option_d, "
        "correct_option, and explanation. correct_option must be exactly one "
        "of A, B, C, or D. Verify each answer against its explanation before "
        "returning it. Keep questions suitable for home "
        f"tuition. Return exactly {question_count} questions.\n\n"
        f"DATA:\n{json.dumps(payload, ensure_ascii=False, default=str)}"
    )

    try:
        raw_generated = generate_text(prompt, response_mime_type="application/json")
        json_text = raw_generated.strip()
        if json_text.startswith("```"):
            json_text = json_text.removeprefix("```json").removeprefix("```")
            json_text = json_text.removesuffix("```").strip()
        generated = json.loads(json_text)
        required_fields = {
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "explanation",
        }
        if not isinstance(generated, list) or not generated:
            raise AIResponseError("AI provider returned an invalid question set.")
        for item in generated:
            if not isinstance(item, dict) or not required_fields.issubset(item):
                raise AIResponseError("AI provider returned an invalid question set.")
            correct_option = str(item.get("correct_option", "")).strip().upper()
            if correct_option.startswith("OPTION_"):
                correct_option = correct_option[-1]
            if correct_option not in {"A", "B", "C", "D"}:
                raise AIResponseError("AI provider returned an invalid question set.")
            item["correct_option"] = correct_option
        generated = generated[:question_count]
    except AIConfigError as exc:
        return fail(str(exc), 503)
    except json.JSONDecodeError:
        return fail("AI question generation failed: AI provider returned invalid question JSON.", 502)
    except (AIServiceError, AIResponseError) as exc:
        return fail(f"AI question generation failed: {exc}", 502)

    return ok({
        "questions": generated,
        "sourceCounts": {
            "sessions": len(session_data),
            "students": len(students),
        },
    }, message="AI questions generated")


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

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        try:

            subject_id = int(
                data.get("subject_id")
            )

        except (
            TypeError,
            ValueError
        ):

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

        tutor_subject_ids = get_tutor_subject_ids(tutor)
        if tutor_subject_ids and subject_id not in tutor_subject_ids:
            return fail(
                "You can only create quizzes for subjects assigned to your tutor profile.",
                403
            )

        assigned_student_id = data.get("assigned_student_id")
        if assigned_student_id not in (None, ""):
            try:
                assigned_student_id = int(assigned_student_id)
            except (TypeError, ValueError):
                return fail("assigned_student_id must be a valid student id")

            student = db.session.get(Student, assigned_student_id)
            if not student:
                return fail("Assigned student not found", 404)

            linked = (
                Session.query
                .join(SessionBooking, SessionBooking.session_id == Session.session_id)
                .filter(
                    Session.tutor_id == tutor.tutor_id,
                    Session.subject_id == subject_id,
                    SessionBooking.student_id == assigned_student_id,
                    SessionBooking.booking_status == "Confirmed",
                )
                .first()
            )
            if not linked:
                return fail(
                    "The selected student is not assigned to your sessions for this subject.",
                    403
                )
        else:
            linked_student_ids = {
                booking.student_id
                for sess in Session.query.filter_by(
                    tutor_id=tutor.tutor_id,
                    subject_id=subject_id
                ).all()
                for booking in SessionBooking.query.filter_by(
                    session_id=sess.session_id,
                    booking_status="Confirmed"
                ).all()
            }
            assigned_student_id = (
                next(iter(linked_student_ids))
                if len(linked_student_ids) == 1
                else None
            )

        quiz = Quiz(
            tutor_id=tutor.tutor_id,
            subject_id=subject_id,
            assigned_student_id=assigned_student_id,
            title=(
                data.get("title")
                or ""
            ).strip(),
            topic=(data.get("topic") or "").strip() or None,
            difficulty=(data.get("difficulty") or "").strip() or None,
            week_number=data.get(
                "week_number"
            ),
        )

        if not quiz.title:

            return fail(
                "title is required"
            )

        db.session.add(
            quiz
        )

        db.session.commit()

        return ok(
            {
                "quiz": {
                    "quiz_id":
                        quiz.quiz_id,

                    "title":
                        quiz.title,

                    "assigned_student_id":
                        quiz.assigned_student_id,
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
                "quiz_id":
                    q.quiz_id,

                "subject_id":
                    q.subject_id,

                "title":
                    q.title,

                "subject":
                    subject_name(
                        q.subject_id
                    ),

                "topic":
                    q.topic,

                "difficulty":
                    q.difficulty,

                "assigned_student_id":
                    q.assigned_student_id,

                "assignedStudent":
                    (
                        db.session.get(Student, q.assigned_student_id).student_name
                        if q.assigned_student_id and db.session.get(Student, q.assigned_student_id)
                        else None
                    ),

                "questionCount":
                    QuizQuestion.query
                    .filter_by(
                        quiz_id=q.quiz_id
                    )
                    .count(),

                "questions": [
                    {
                        "id": question.question_id,
                        "question": question.question,
                        "option_a": question.option_a,
                        "option_b": question.option_b,
                        "option_c": question.option_c,
                        "option_d": question.option_d,
                        "correct_option": question.correct_option,
                        "explanation": question.explanation or "",
                    }
                    for question in QuizQuestion.query
                    .filter_by(quiz_id=q.quiz_id)
                    .order_by(QuizQuestion.question_id)
                    .all()
                ],
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

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

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

        explanation=(
            data.get("explanation")
            or ""
        ).strip(),
    )

    if (
        not question.question
        or not question.option_a
        or not question.option_b
        or not question.option_c
        or not question.option_d
        or question.correct_option
        not in {
            "A",
            "B",
            "C",
            "D"
        }
    ):

        return fail(
            "Question, options A-D, and correct_option A/B/C/D are required"
        )

    db.session.add(
        question
    )

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
# FLASHCARDS
# =========================================================

@tutor_bp.route(
    "/flashcards/ai-generate",
    methods=["POST"]
)
@tutor_required
def flashcards_ai_generate():
    tutor = current_tutor()
    if not tutor:
        return fail("Tutor not found", 404)

    data = request.get_json(silent=True) or {}
    subject = str(data.get("subject") or "").strip()
    topic = str(data.get("topic") or "").strip()
    class_level = str(data.get("class_level") or "").strip()
    context = str(data.get("context") or "").strip()
    try:
        count = int(data.get("count") or 10)
    except (TypeError, ValueError):
        count = 10
    count = max(1, min(count, 20))

    if not subject:
        return fail("subject is required")
    if not topic:
        return fail("topic is required")

    prompt = (
        "You are Tutor AI for LearnAtHome. Generate flashcards for the tutor "
        "using only the exact requested subject, topic, class level, and "
        "context below. Every flashcard must directly test or explain the "
        "requested topic; do not drift into adjacent topics. Do not invent "
        "content unrelated to what was provided. Return a JSON array of "
        "objects with exactly the keys front, back, and explanation. "
        "'front' is a short question or term for the student to recall, "
        "'back' is the concise answer or definition, 'explanation' is one "
        f"sentence giving context. Return exactly {count} flashcards.\n\n"
        f"Subject: {subject}\n"
        f"Topic: {topic}\n"
        f"Class level: {class_level or 'Not specified'}\n"
        f"Context: {context or 'None provided'}"
    )

    try:
        raw_generated = generate_text(prompt, response_mime_type="application/json")
        json_text = raw_generated.strip()
        if json_text.startswith("```"):
            json_text = json_text.removeprefix("```json").removeprefix("```")
            json_text = json_text.removesuffix("```").strip()
        generated = json.loads(json_text)
        if not isinstance(generated, list) or not generated:
            raise AIResponseError("AI provider returned an invalid flashcard set.")
        required_fields = {"front", "back"}
        for item in generated:
            if not isinstance(item, dict) or not required_fields.issubset(item):
                raise AIResponseError("AI provider returned an invalid flashcard set.")
            if not str(item.get("front") or "").strip() or not str(item.get("back") or "").strip():
                raise AIResponseError("AI provider returned an invalid flashcard set.")
        generated = generated[:count]
    except AIConfigError as exc:
        return fail(str(exc), 503)
    except json.JSONDecodeError:
        return fail("AI flashcard generation failed: AI provider returned invalid flashcard JSON.", 502)
    except (AIServiceError, AIResponseError) as exc:
        return fail(f"AI flashcard generation failed: {exc}", 502)

    return ok({"flashcards": generated}, message="AI flashcards generated")


@tutor_bp.route(
    "/flashcard-sets",
    methods=["GET", "POST"]
)
@tutor_required
def tutor_flashcard_sets():
    tutor = current_tutor()

    if request.method == "POST":
        data = request.get_json(silent=True) or {}

        try:
            subject_id = int(data.get("subject_id"))
        except (TypeError, ValueError):
            return fail("subject_id is required")

        if not db.session.get(Subject, subject_id):
            return fail("Subject not found", 404)

        tutor_subject_ids = get_tutor_subject_ids(tutor)
        if tutor_subject_ids and subject_id not in tutor_subject_ids:
            return fail(
                "You can only create flashcards for subjects assigned to your tutor profile.",
                403
            )

        assigned_student_id = data.get("assigned_student_id")
        if assigned_student_id not in (None, ""):
            try:
                assigned_student_id = int(assigned_student_id)
            except (TypeError, ValueError):
                return fail("assigned_student_id must be a valid student id")
            if not db.session.get(Student, assigned_student_id):
                return fail("Assigned student not found", 404)
        else:
            assigned_student_id = None

        title = (data.get("title") or "").strip()
        if not title:
            return fail("title is required")

        fset = FlashcardSet(
            tutor_id=tutor.tutor_id,
            subject_id=subject_id,
            assigned_student_id=assigned_student_id,
            title=title,
            topic=(data.get("topic") or "").strip() or None,
            class_level=(data.get("class_level") or "").strip() or None,
            context=(data.get("context") or "").strip() or None,
        )
        db.session.add(fset)
        db.session.commit()

        return ok(
            {"set": {"set_id": fset.set_id, "title": fset.title, "assigned_student_id": fset.assigned_student_id}},
            "Flashcard set created",
            201,
        )

    rows = (
        FlashcardSet.query
        .filter_by(tutor_id=tutor.tutor_id)
        .order_by(FlashcardSet.created_at.desc())
        .all()
    )

    return ok({
        "sets": [
            {
                "set_id": s.set_id,
                "subject_id": s.subject_id,
                "subject": subject_name(s.subject_id),
                "title": s.title,
                "topic": s.topic,
                "class_level": s.class_level,
                "context": s.context,
                "assigned_student_id": s.assigned_student_id,
                "assignedStudent": (
                    db.session.get(Student, s.assigned_student_id).student_name
                    if s.assigned_student_id and db.session.get(Student, s.assigned_student_id)
                    else None
                ),
                "cardCount": Flashcard.query.filter_by(set_id=s.set_id).count(),
                "cards": [
                    {"id": c.card_id, "front": c.front, "back": c.back, "explanation": c.explanation or ""}
                    for c in Flashcard.query.filter_by(set_id=s.set_id).order_by(Flashcard.card_id).all()
                ],
            }
            for s in rows
        ]
    })


@tutor_bp.route(
    "/flashcard-sets/<int:set_id>/cards",
    methods=["POST"]
)
@tutor_required
def create_flashcard(set_id):
    tutor = current_tutor()

    fset = db.session.get(FlashcardSet, set_id)
    if not fset or fset.tutor_id != tutor.tutor_id:
        return fail("Flashcard set not found", 404)

    data = request.get_json(silent=True) or {}
    front = (data.get("front") or "").strip()
    back = (data.get("back") or "").strip()
    explanation = (data.get("explanation") or "").strip()

    if not front or not back:
        return fail("front and back are required")

    card = Flashcard(set_id=set_id, front=front, back=back, explanation=explanation)
    db.session.add(card)
    db.session.commit()

    return ok({"card_id": card.card_id}, "Flashcard added", 201)


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

        except (
            TypeError,
            ValueError
        ):

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

        db.session.add(
            resource
        )

        db.session.commit()

        for booking in (
            SessionBooking.query
            .filter_by(
                session_id=session_id
            )
            .all()
        ):

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

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

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

        db.session.add(
            faq
        )

        db.session.commit()

        return ok(
            {
                "entry": {
                    "faqId":
                        faq.faq_id,

                    "question":
                        faq.question,

                    "answer":
                        faq.answer,

                    "meta":
                        "Published",
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
                "faqId":
                    faq.faq_id,

                "question":
                    faq.question,

                "answer":
                    faq.answer,

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
                "doubtId":
                    d.doubt_id,

                "studentId":
                    d.student_id,

                "subject":
                    d.subject,

                "question":
                    d.question,

                "askedAt":
                    (
                        d.asked_at.isoformat()
                        if d.asked_at
                        else None
                    ),

                "status":
                    d.status,
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
        (
            request.get_json(
                silent=True
            )
            or {}
        )
        .get(
            "reply",
            ""
        )
        .strip()
    )

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
                (
                    Message.sender_type
                    == "Tutor"
                )
                &
                (
                    Message.sender_id
                    == tutor.tutor_id
                )
            )
            |
            (
                (
                    Message.receiver_type
                    == "Tutor"
                )
                &
                (
                    Message.receiver_id
                    == tutor.tutor_id
                )
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

            other_type = (
                message.receiver_type
            )

            other_id = (
                message.receiver_id
            )

        else:

            other_type = (
                message.sender_type
            )

            other_id = (
                message.sender_id
            )

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

                name = (
                    person.student_name
                )

            else:

                name = (
                    person.parent_name
                    if person
                    else "User"
                )

            conversations_data[key] = {
                "id":
                    key,

                "participantName":
                    name,

                "subtitle":
                    other_type,

                "initials":
                    "".join(
                        x[0]
                        for x in name.split()[:2]
                    ).upper(),

                "gradient":
                    "linear-gradient(135deg,var(--g1),var(--g2))",

                "messages": [],

                "otherType":
                    other_type,

                "otherId":
                    other_id,
            }

        conversations_data[
            key
        ]["messages"].append({

            "messageId":
                message.message_id,

            "message":
                message.message,

            "timestamp":
                (
                    message.sent_at.isoformat()
                    if message.sent_at
                    else None
                ),

            "w":
                (
                    "me"
                    if message.sender_type
                    == "Tutor"
                    else "them"
                ),
        })

    # Make connected contacts discoverable even before the first message.
    linked_student_ids = [b.student_id for b in SessionBooking.query.join(Session, SessionBooking.session_id == Session.session_id).filter(
        Session.tutor_id == tutor.tutor_id, SessionBooking.booking_status == "Confirmed"
    ).all()]
    for sid in linked_student_ids:
        student = db.session.get(Student, sid)
        if not student:
            continue
        key = f"student-{sid}"
        conversations_data.setdefault(key, {
            "id": key, "participantName": student.student_name, "subtitle": "Student",
            "initials": "".join(x[0] for x in student.student_name.split()[:2]).upper(),
            "gradient": "linear-gradient(135deg,var(--g1),var(--g2))", "messages": [],
            "otherType": "Student", "otherId": sid,
        })
        if student.parent_id:
            parent = db.session.get(Parent, student.parent_id)
            if parent:
                pkey = f"parent-{parent.parent_id}"
                item = conversations_data.setdefault(pkey, {
                    "id": pkey, "participantName": parent.parent_name, "subtitle": "Parent",
                    "initials": "".join(x[0] for x in parent.parent_name.split()[:2]).upper(),
                    "gradient": "linear-gradient(135deg,var(--g1),var(--g2))", "messages": [],
                    "otherType": "Parent", "otherId": parent.parent_id,
                })
                item.setdefault("linkedStudents", []).append({"studentId": sid, "studentName": student.student_name})

    return ok({
        "conversations": conversations_data
    })


@tutor_bp.route(
    "/messages/send",
    methods=["POST"]
)
@tutor_required
def send_message():

    tutor = current_tutor()

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

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

    try:
        receiver_id = int(
            receiver_id
        )
    except (
        TypeError,
        ValueError
    ):
        return fail(
            "Invalid receiver_id"
        )

    if receiver_type == "Student":
        receiver = db.session.get(Student, receiver_id)
        if not receiver:
            return fail("Student not found", 404)
        related = Session.query.join(SessionBooking, SessionBooking.session_id == Session.session_id).filter(
            Session.tutor_id == tutor.tutor_id, SessionBooking.student_id == receiver_id,
            SessionBooking.booking_status == "Confirmed"
        ).first()
        if not related:
            return fail("You can only message students connected to you", 403)
    else:
        receiver = db.session.get(Parent, receiver_id)
        if not receiver:
            return fail("Parent not found", 404)
        child_ids = [x.student_id for x in Student.query.filter_by(parent_id=receiver_id).all()]
        related = Session.query.join(SessionBooking, SessionBooking.session_id == Session.session_id).filter(
            Session.tutor_id == tutor.tutor_id, SessionBooking.student_id.in_(child_ids or [-1]),
            SessionBooking.booking_status == "Confirmed"
        ).first()
        if not related:
            return fail("You can only message parents connected through your students", 403)

    message = Message(
        sender_type="Tutor",
        sender_id=tutor.tutor_id,
        receiver_type=receiver_type,
        receiver_id=receiver_id,
        message=text,
    )

    db.session.add(
        message
    )
    db.session.add(Notification(
        recipient_type=receiver_type, recipient_id=receiver_id,
        title="New message from tutor", message=f"{tutor.tutor_name} sent you a new message.",
        notification_type="New Message", action_url=f"/parent/messages" if receiver_type == "Parent" else "/student/messages"
    ))

    db.session.commit()

    return ok(
        {
            "messageId": message.message_id,
            "message_id": message.message_id,
            "message": message.message,
            "sender_type": message.sender_type,
            "sender_id": message.sender_id,
            "receiver_type": message.receiver_type,
            "receiver_id": message.receiver_id,
            "sent_at": message.sent_at.isoformat() if message.sent_at else None,
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

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        meeting_date = datetime.fromisoformat(
            data.get("meeting_date")
        )

    except (
        TypeError,
        ValueError
    ):

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

    try:
        meeting_link = clean_optional_url(data.get("meeting_link"))
    except ValueError as exc:
        return fail(str(exc))

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

    session_obj = None

    if student_id:

        student = db.session.get(
            Student,
            int(student_id)
        )

        enrolled = (
            StudentSubject.query
            .filter_by(
                student_id=student.student_id
            )
            .all()
        )

        if not enrolled:

            return fail(
                "The selected student has "
                "no registered subject",
                400
            )

        subject_id = (
            enrolled[0].subject_id
        )

        subject = db.session.get(
            Subject,
            subject_id
        )

        if not subject:

            return fail(
                "Student subject not found",
                404
            )

        if not tutor_has_subject(
            tutor,
            subject_id
        ):

            return fail(
                "The selected student's subject "
                "is not assigned to this tutor",
                403
            )

        session_obj = Session(
            tutor_id=tutor.tutor_id,
            subject_id=subject_id,
            session_date=meeting_date.date(),
            start_time=meeting_date.time(),
            end_time=(
                meeting_date
                + timedelta(hours=1)
            ).time(),
            session_type="One-to-One",
            status="Scheduled",
        )

        db.session.add(
            session_obj
        )

        db.session.flush()

        db.session.add(
            SessionBooking(
                session_id=session_obj.session_id,
                student_id=student.student_id,
                booking_status="Confirmed",
            )
        )
        try:
            session_obj.meeting_url = meeting_link or create_meeting_space()
        except GoogleMeetNotConfigured:
            session_obj.meeting_url = None

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
        ) if meeting_link else None,
        meeting_reason=data.get(
            "meeting_reason",
            ""
        ),
        session_id=(
            session_obj.session_id
            if session_obj
            else None
        ),
        status="Scheduled",
        creator_type="Tutor",
        meeting_type="TUTOR_STUDENT" if student_id else "TUTOR_PARENT",
    )

    db.session.add(
        meeting
    )

    db.session.flush()

    if student_id:

        db.session.add(
            Notification(
                recipient_type="Student",
                recipient_id=int(student_id),
                title="New meeting scheduled",
                message=data.get(
                    "meeting_reason",
                    "Meeting scheduled"
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
                message=data.get(
                    "meeting_reason",
                    "Meeting scheduled"
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

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        field_mapping = {
            "name":
                "tutor_name",

            "phone":
                "phone_no",

            "bio":
                "bio",

            "education":
                "education",

            "hourlyRate":
                "hourly_rate",

            "availability":
                "availability",

            "experience":
                "experience_years",
        }

        for field, attribute in (
            field_mapping.items()
        ):

            if field in data:

                setattr(
                    tutor,
                    attribute,
                    data[field]
                )

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
                if isinstance(
                    parsed,
                    list
                )
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
                tutor.phone_no
                or "",

            "experience":
                tutor.experience_years
                or 0,

            "bio":
                tutor.bio
                or "",

            "education":
                tutor.education
                or "",

            "hourlyRate":
                tutor.hourly_rate
                or "",

            "availability":
                tutor.availability
                or "",

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
                initials
                or "T",
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
    if not tutor:
        return fail(
            "Tutor account could not be found. Please log in again.",
            401
        )

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
                    (
                        n.action_url
                        or (
                            "/tutor/schedule"
                            if n.notification_type
                            == "One-to-One Meeting"
                            else
                            "dashboard"
                        )
                    ),

                "type":
                    n.notification_type,
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
    if not tutor:
        return fail(
            "Tutor account could not be found. Please log in again.",
            401
        )

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
