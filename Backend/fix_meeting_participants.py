"""
One-time data cleanup for the Student/Parent/Tutor meeting-participant bug.

Background
----------
Student-created Student+Tutor meetings used to be saved with
MeetingRequest.parent_id = student.parent_id, which silently made the
parent a "participant" on every query that filters by parent_id, even
though the parent never created or was selected for that meeting.

The application code has been fixed so this can no longer happen going
forward (see Backend/student/routes.py). This script is a one-time,
idempotent repair for rows that were already written to the database
before that fix, so the bad data itself is corrected rather than just
hidden by the read-path guards.

Rule applied
------------
A MeetingRequest's parent_id should only ever be set when the parent
genuinely created (or was explicitly part of) the meeting, i.e.
creator_type == 'Parent'. Any row where parent_id is set but
creator_type is something else (Student, Tutor, or missing/legacy
data) has its parent_id cleared.

This script is:
  - Read-only by default (use --apply to actually write changes).
  - Idempotent (running it again after --apply finds nothing left to fix).
  - Non-destructive to anything except the incorrect parent_id column
    on affected MeetingRequest rows.

Usage
-----
    # Show what would change, without touching the database
    python3 fix_meeting_participants.py

    # Apply the fix
    python3 fix_meeting_participants.py --apply
"""

import argparse

from app import create_app
from database import db
from models import MeetingRequest


def find_affected_rows():
    """Return MeetingRequest rows whose parent_id should be cleared."""
    return (
        MeetingRequest.query
        .filter(
            MeetingRequest.parent_id.isnot(None),
            MeetingRequest.creator_type != 'Parent',
        )
        .order_by(MeetingRequest.meeting_id)
        .all()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--apply', action='store_true',
        help='Actually write the fix. Without this flag, only a dry-run report is printed.'
    )
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        rows = find_affected_rows()

        if not rows:
            print("No affected rows found. Nothing to fix.")
            return

        print(f"Found {len(rows)} MeetingRequest row(s) with an incorrect parent_id:\n")
        for m in rows:
            print(
                f"  meeting_id={m.meeting_id:<6} creator_type={m.creator_type!r:<10} "
                f"meeting_type={m.meeting_type!r:<16} student_id={m.student_id} "
                f"tutor_id={m.tutor_id} parent_id(will clear)={m.parent_id} status={m.status!r}"
            )

        if not args.apply:
            print("\nDry run only — no changes written. Re-run with --apply to fix these rows.")
            return

        for m in rows:
            m.parent_id = None
        db.session.commit()
        print(f"\nCleared parent_id on {len(rows)} row(s). Done.")


if __name__ == '__main__':
    main()
