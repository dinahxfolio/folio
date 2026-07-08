"""Shared Google API auth helper for the Monthly Budget Tracker build.

Credentials come from an OAuth installed-app flow (see README.md in this
folder) whose token is cached outside the repo. Never commit the token file.
"""
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = os.environ.get(
    "FOLIO_SHEETS_TOKEN",
    "/tmp/claude-0/-home-user-folio/0d88e6b3-fd65-5a51-bbfb-6404b7ec97d1/scratchpad/token.json",
)


def get_credentials() -> Credentials:
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    return creds


def get_services():
    creds = get_credentials()
    sheets = build("sheets", "v4", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return sheets, drive
