import os
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from database import db
from models import Session, SessionBooking, MeetingRequest, Notification, SessionUpdate




APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Kolkata")

def _local_now():
    """Return the application-local wall clock used by DATE/TIME schedules."""
    try:
        return datetime.now(ZoneInfo(APP_TIMEZONE)).replace(tzinfo=None)
    except Exception:
        return datetime.now()

def session_window(s, now=None):
    """Return the authoritative local start/end datetimes for a Session."""
    if not s or not s.session_date or not s.start_time or not s.end_time:
        return None, None
    now = now or _local_now()
    start = datetime.combine(s.session_date, s.start_time)
    end = datetime.combine(s.session_date, s.end_time)
    return start, end

def meeting_lifecycle(s, now=None):
    """Return the single, time-aware meeting state used by every dashboard.

    Stored session dates/times are application-local wall-clock values in
    APP_TIMEZONE.  A meeting URL by itself never makes a future meeting
    joinable.  A tutor may explicitly start a meeting early; otherwise the
    scheduled start time activates it automatically.
    """
    now = now or _local_now()
    if not s:
        return {"status": "Meeting Not Started", "can_join": False, "can_start": False, "can_end": False}

    if s.status in ("Cancelled", "Completed") or s.meeting_ended_at:
        return {"status": "Meeting Ended", "can_join": False, "can_start": False, "can_end": False}

    start, end = session_window(s, now)
    if end and now >= end:
        return {"status": "Meeting Ended", "can_join": False, "can_start": False, "can_end": False}

    # An explicit tutor start activates the meeting immediately, even before
    # the scheduled start.  This is intentional for live parent/student flow.
    if s.meeting_started_at or s.status == "Live":
        return {
            "status": "Meeting Started",
            "can_join": bool(s.meeting_url),
            "can_start": False,
            "can_end": bool(s.meeting_url),
        }

    # A future session stays locked even if a Meet URL was generated when it
    # was scheduled.  At the scheduled start time the URL becomes joinable.
    if start and now >= start:
        return {
            "status": "Meeting Started",
            "can_join": bool(s.meeting_url),
            "can_start": True,
            "can_end": bool(s.meeting_url),
        }

    return {
        "status": "Meeting Not Started",
        "can_join": False,
        "can_start": True,
        "can_end": False,
    }

def _parse_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _parse_time(value):
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt).time()
        except ValueError:
            pass
    raise ValueError("Time must be in HH:MM or HH:MM:SS format.")


def _parse_datetime(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def session_to_dict(s):
    return {
        "session_id": s.session_id, "tutor_id": s.tutor_id,
        "subject_id": s.subject_id,
        "session_date": s.session_date.isoformat() if s.session_date else None,
        "start_time": s.start_time.strftime("%H:%M:%S") if s.start_time else None,
        "end_time": s.end_time.strftime("%H:%M:%S") if s.end_time else None,
        "session_type": s.session_type, "status": s.status,
        "meeting_url": s.meeting_url,
        "meeting_started_at": s.meeting_started_at.isoformat() if s.meeting_started_at else None,
        "meeting_ended_at": s.meeting_ended_at.isoformat() if s.meeting_ended_at else None,
        "meeting_duration_seconds": s.meeting_duration_seconds,
        "meeting_lifecycle": meeting_lifecycle(s)["status"],
        "can_join": meeting_lifecycle(s)["can_join"],
        "can_start": meeting_lifecycle(s)["can_start"],
        "can_end": meeting_lifecycle(s)["can_end"],
    }


def booking_to_dict(b):
    return {"booking_id": b.booking_id, "session_id": b.session_id,
            "student_id": b.student_id,
            "booking_date": b.booking_date.isoformat() if b.booking_date else None,
            "booking_status": b.booking_status}


def meeting_to_dict(m):
    return {"meeting_id": m.meeting_id, "tutor_id": m.tutor_id,
            "student_id": m.student_id, "parent_id": m.parent_id,
            "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
            "meeting_link": m.meeting_link, "meeting_reason": m.meeting_reason,
            "session_id": m.session_id, "status": m.status}


def session_update_to_dict(u):
    return {"update_id": u.update_id, "session_id": u.session_id,
            "topics_covered": u.topics_covered, "homework_assigned": u.homework_assigned,
            "next_session_date": u.next_session_date.isoformat() if u.next_session_date else None,
            "notification_time": u.notification_time.isoformat() if u.notification_time else None}


def create_session(tutor_id, subject_id, session_date, start_time, end_time,
                   session_type="Regular", status="Scheduled", meeting_url=None):
    if not tutor_id or not subject_id:
        raise ValueError("tutor_id and subject_id are required.")
    d, st, et = _parse_date(session_date), _parse_time(start_time), _parse_time(end_time)
    if d is None or st is None or et is None:
        raise ValueError("session_date, start_time and end_time are required.")
    if et <= st:
        raise ValueError("end_time must be later than start_time.")
    if status not in {"Scheduled", "Completed", "Cancelled", "Rescheduled"}:
        raise ValueError("Invalid session status.")
    s = Session(tutor_id=int(tutor_id), subject_id=int(subject_id), session_date=d,
                start_time=st, end_time=et, session_type=session_type or "Regular",
                status=status, meeting_url=meeting_url)
    db.session.add(s); db.session.commit()
    return s


def get_session(session_id):
    return db.session.get(Session, int(session_id))


def list_sessions(tutor_id=None, subject_id=None, student_id=None,
                  session_date=None, status=None):
    q = Session.query
    if tutor_id is not None: q = q.filter(Session.tutor_id == int(tutor_id))
    if subject_id is not None: q = q.filter(Session.subject_id == int(subject_id))
    if session_date: q = q.filter(Session.session_date == _parse_date(session_date))
    if status: q = q.filter(Session.status == status)
    if student_id is not None:
        ids = db.session.query(SessionBooking.session_id).filter(
            SessionBooking.student_id == int(student_id)).subquery()
        q = q.filter(Session.session_id.in_(ids))
    return q.order_by(Session.session_date.asc(), Session.start_time.asc()).all()


def update_session(s, data):
    if "tutor_id" in data and data["tutor_id"] is not None: s.tutor_id = int(data["tutor_id"])
    if "subject_id" in data and data["subject_id"] is not None: s.subject_id = int(data["subject_id"])
    if "session_date" in data: s.session_date = _parse_date(data["session_date"])
    if "start_time" in data: s.start_time = _parse_time(data["start_time"])
    if "end_time" in data: s.end_time = _parse_time(data["end_time"])
    if s.start_time and s.end_time and s.end_time <= s.start_time:
        raise ValueError("end_time must be later than start_time.")
    if "session_type" in data and data["session_type"] is not None: s.session_type = data["session_type"]
    if "status" in data and data["status"] is not None:
        if data["status"] not in {"Scheduled", "Completed", "Cancelled", "Rescheduled"}: raise ValueError("Invalid session status.")
        s.status = data["status"]
    if "meeting_url" in data: s.meeting_url = data["meeting_url"]
    db.session.commit(); return s


def delete_session(s):
    if (SessionBooking.query.filter_by(session_id=s.session_id).first() or
        SessionUpdate.query.filter_by(session_id=s.session_id).first() or
        MeetingRequest.query.filter_by(session_id=s.session_id).first()):
        raise ValueError("Session cannot be deleted because related records exist. Cancel or reschedule it instead.")
    db.session.delete(s); db.session.commit()


def create_booking(session_id, student_id):
    s = get_session(session_id)
    if s is None: raise LookupError("Session not found.")
    if s.status != "Scheduled": raise ValueError("Only Scheduled sessions can be booked.")
    b = SessionBooking.query.filter_by(session_id=int(session_id), student_id=int(student_id)).first()
    if b:
        if b.booking_status != "Cancelled": raise ValueError("Student is already booked for this session.")
        b.booking_status, b.booking_date = "Confirmed", datetime.utcnow()
    else:
        b = SessionBooking(session_id=int(session_id), student_id=int(student_id), booking_date=datetime.utcnow(), booking_status="Confirmed")
        db.session.add(b)
        db.session.add(Notification(recipient_type="Student", recipient_id=int(student_id),
            title="Session Booking Confirmed", message=f"Your booking for session {s.session_id} has been confirmed.",
            notification_type="Reminder"))
    db.session.commit(); return b


def get_booking(booking_id): return db.session.get(SessionBooking, int(booking_id))


def list_bookings(student_id=None, session_id=None, booking_status=None):
    q = SessionBooking.query
    if student_id is not None: q = q.filter(SessionBooking.student_id == int(student_id))
    if session_id is not None: q = q.filter(SessionBooking.session_id == int(session_id))
    if booking_status: q = q.filter(SessionBooking.booking_status == booking_status)
    return q.order_by(SessionBooking.booking_date.desc()).all()


def cancel_booking(b):
    b.booking_status = "Cancelled"; db.session.commit(); return b


def create_meeting_request(tutor_id, meeting_date, student_id=None, parent_id=None,
                           meeting_link=None, meeting_reason=None, session_id=None, status="Scheduled"):
    if not tutor_id: raise ValueError("tutor_id is required.")
    if student_id is None and parent_id is None: raise ValueError("Either student_id or parent_id is required.")
    d = _parse_datetime(meeting_date)
    if d is None: raise ValueError("meeting_date is required.")
    m = MeetingRequest(tutor_id=int(tutor_id), student_id=int(student_id) if student_id is not None else None,
        parent_id=int(parent_id) if parent_id is not None else None, meeting_date=d,
        meeting_link=meeting_link, meeting_reason=meeting_reason,
        session_id=int(session_id) if session_id is not None else None, status=status or "Scheduled")
    db.session.add(m)
    rtype, rid = ("Student", int(student_id)) if student_id is not None else ("Parent", int(parent_id))
    db.session.add(Notification(recipient_type=rtype, recipient_id=rid, title="Meeting Scheduled",
        message=f"A meeting has been scheduled for {d.isoformat()}.", notification_type="Reminder", action_url=meeting_link))
    db.session.commit(); return m


def get_meeting(meeting_id): return db.session.get(MeetingRequest, int(meeting_id))


def list_meetings(tutor_id=None, student_id=None, parent_id=None, status=None):
    q = MeetingRequest.query
    if tutor_id is not None: q = q.filter(MeetingRequest.tutor_id == int(tutor_id))
    if student_id is not None: q = q.filter(MeetingRequest.student_id == int(student_id))
    if parent_id is not None: q = q.filter(MeetingRequest.parent_id == int(parent_id))
    if status: q = q.filter(MeetingRequest.status == status)
    return q.order_by(MeetingRequest.meeting_date.asc()).all()


def update_meeting_status(m, status):
    if status not in {"Scheduled", "Completed", "Cancelled", "Rescheduled"}: raise ValueError("Invalid meeting status.")
    m.status = status; db.session.commit(); return m


def create_session_update(session_id, topics_covered=None, homework_assigned=None, next_session_date=None):
    if get_session(session_id) is None: raise LookupError("Session not found.")
    u = SessionUpdate.query.filter_by(session_id=int(session_id)).first()
    if u is None:
        u = SessionUpdate(session_id=int(session_id), topics_covered=topics_covered,
            homework_assigned=homework_assigned, next_session_date=_parse_date(next_session_date),
            notification_time=datetime.utcnow())
        db.session.add(u)
    else:
        if topics_covered is not None: u.topics_covered = topics_covered
        if homework_assigned is not None: u.homework_assigned = homework_assigned
        if next_session_date is not None: u.next_session_date = _parse_date(next_session_date)
        u.notification_time = datetime.utcnow()
    db.session.commit(); return u