"""
One-time setup for LearnAtHome's dedicated Google Meet account.

1. In Google Cloud, enable the Google Meet REST API.
2. Create an OAuth 2.0 Desktop App client.
3. Download the client JSON and rename it:
       google_meet_credentials.json
   Put it beside this file (Backend/).
4. Run:
       python setup_google_meet.py
5. Sign in with the dedicated Google Workspace account.
6. Approve the Meet permission.
7. A google_meet_token.json file will be created.

Do NOT commit either JSON file.
"""

from __future__ import annotations

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/meetings.space.created"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_meet_credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "google_meet_token.json")


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print()
        print("Missing Backend/google_meet_credentials.json")
        print("Download the OAuth Desktop App credentials from Google Cloud")
        print("and place the file at that exact path.")
        print()
        raise SystemExit(1)

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if creds and creds.valid:
        print("Google Meet is already authorized.")
        print(f"Token: {TOKEN_FILE}")
        return

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES,
        )
        creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w", encoding="utf-8") as token:
        token.write(creds.to_json())

    print()
    print("Google Meet authorization completed.")
    print(f"Saved token to: {TOKEN_FILE}")
    print("You can now start the LearnAtHome backend.")
    print()


if __name__ == "__main__":
    main()
