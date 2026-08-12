# LearnAtHome – Google Meet setup

This integration uses one dedicated Google Workspace account. Tutor/student/parent app logins do not need to be Google accounts.

## 1. Google Cloud

1. Create/select a Google Cloud project.
2. Enable **Google Meet API**.
3. Configure Google Auth Platform/OAuth.
4. Create an OAuth 2.0 **Desktop app** client.
5. Download the JSON and place it at:

   `Backend/google_meet_credentials.json`

Google's current Python quickstart uses the `meetings.space.created` scope and a Desktop OAuth client.

## 2. Authorize the dedicated account

From the `Backend` folder:

```bash
python setup_google_meet.py
```

Sign in with the dedicated Google Workspace account and approve the Meet permission.

The token is saved as:

`Backend/google_meet_token.json`

Do not commit either JSON file.

## 3. Verify the API actually works

Authorization alone is not enough. Before testing the app, run:

```bash
python test_google_meet.py
```

A successful test prints a real URL like:

`https://meet.google.com/abc-defg-hij`

If this test fails, copy the complete terminal error. The most common account-side requirement is that the account is a Google Workspace account with Google Meet enabled.

## 4. App behavior

- Creating a tutor session attempts to create one real Meet and stores its URL in `session.meeting_url`.
- If Meet creation is temporarily unavailable, the normal session is still saved.
- Clicking **Start Session** on a scheduled/rescheduled tutor session will create the Meet on demand if the session does not already have a URL. This also repairs older sessions created before Meet authorization.
- Student and Parent pages use the same stored session URL and therefore join the same meeting.

## 5. Existing database

The integration does not recreate the database. On startup the app adds `meeting_url` to the existing `session` table only when that column is missing.
