# LearnAtHome Meeting & Messaging Workflow Update

Implemented the requested meeting and messaging workflow improvements.

## Parent
- `Connect with Your Child` now creates a direct Parent -> Child one-on-one meeting.
- Parent -> Child meetings do not create tutor approval requests or tutor messages.
- Reason is required and persisted.
- Child sees the scheduled meeting immediately as `Meeting Not Started`.
- Parent can start the meeting; the child becomes able to join after start.
- `Meeting Requests` is presented as `Connect with Tutor`.
- Added `All Meetings` route with creator, type, reason, participants, time, approval and lifecycle state.

## Student
- Meeting serialization now exposes meeting type, creator and reason when a meeting request exists.
- Student session UI shows `One-on-One Session`, `Created by ...`, and reason where available.
- Student -> Tutor requests remain tutor-approval based.

## Tutor
- Tutor schedule/request workflow keeps approval for student-created and parent-tutor requests.
- Tutor messaging now persists through the backend and returns the created message data.
- Connected students and their parents are discoverable even before a first message.
- Parent/student messaging authorization is relationship-aware.

## Data compatibility
- Added additive `MeetingRequest.creator_type` and `MeetingRequest.meeting_type` fields.
- Existing SQLite databases are upgraded automatically by the compatibility layer without dropping tables.

## Validation
- Python backend files were syntax-checked with `py_compile` successfully.
- Full pytest could not run in the build environment because Python dependencies were not installed and external package download is unavailable.
- Frontend build could not complete because the supplied `node_modules` is missing Rollup's platform optional dependency; no source-code build error was established from that failure.
