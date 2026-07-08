"""Create the Monthly Budget Tracker spreadsheet with the SETTINGS tab shell.

Sheet ID convention for this build (documented here since later tabs will
reference these ids when adding sheets of their own):
  100 = SETTINGS
  200 = DASHBOARD
  300-311 = Jan..Dec
  400 = ANNUAL OVERVIEW
  500 = GOALS
"""
import json
import os

from auth import get_services
from palette import NEAR_BLACK

SPREADSHEET_ID_PATH = os.path.join(os.path.dirname(__file__), "spreadsheet_id.txt")


def create():
    sheets, _drive = get_services()

    body = {
        "properties": {
            "title": "Monthly Budget Tracker",
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 100,
                    "title": "SETTINGS",
                    "gridProperties": {
                        "rowCount": 80,
                        "columnCount": 6,
                        "hideGridlines": True,
                    },
                    "tabColor": NEAR_BLACK,
                }
            }
        ],
    }

    result = sheets.spreadsheets().create(body=body, fields="spreadsheetId,spreadsheetUrl").execute()
    with open(SPREADSHEET_ID_PATH, "w") as f:
        f.write(result["spreadsheetId"])

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    create()
