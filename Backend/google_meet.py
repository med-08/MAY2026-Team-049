"""
Optional Google Meet integration for LearnAtHome.

This module uses one dedicated Google account that is authorized once
through setup_google_meet.py. The resulting refresh token is reused by
the Flask backend when a tutor creates a session.

Files expected in Backend/:
  google_meet_credentials.json  <- downloaded OAuth client JSON
  google_meet_token.json        <- created by setup script

The token/credentials files are intentionally not committed.
"""

from __future__ import annotations

import os

SCOPES = ["https://www.googleapis.com/auth/meetings.space.created"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_meet_credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "google_meet_token.json")


class GoogleMeetNotConfigured(RuntimeError):
    """Raised when the one-time Google Meet account setup is missing."""


def _load_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not os.path.exists(CREDENTIALS_FILE):
            raise GoogleMeetNotConfigured(
                "Google Meet is not connected. Run setup_google_meet.py "
                "once with your dedicated Google Workspace account."
            )

        # The web application itself never launches the OAuth browser.
        # The one-time setup is deliberately performed by the setup script.
        raise GoogleMeetNotConfigured(
            "Google Meet authorization is required. Run setup_google_meet.py "
            "once with your dedicated Google Workspace account."
        )

    with open(TOKEN_FILE, "w", encoding="utf-8") as token:
        token.write(creds.to_json())

    return creds


def create_meeting_space() -> str:
    """Create a real Google Meet space and return its meeting URL."""
    credentials = _load_credentials()

    from google.apps import meet_v2

    client = meet_v2.SpacesServiceClient(credentials=credentials)

    # Google Meet creates the space ID/meeting code server-side.
    # The request body is intentionally empty, matching Google's current
    # Python quickstart for the Meet REST API.
    response = client.create_space(
        request=meet_v2.CreateSpaceRequest()
    )

    meeting_uri = getattr(response, "meeting_uri", None)

    if not meeting_uri:
        raise RuntimeError(
            "Google Meet created a space but did not return a meeting URL."
        )

    return meeting_uri
