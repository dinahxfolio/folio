"""Read back START HERE's live values to confirm content actually landed,
not just that the build script ran without error."""
from auth import get_services
with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()
sheets, _ = get_services()

r = sheets.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="'START HERE'!B1:B21", valueRenderOption="FORMATTED_VALUE").execute()
for i, row in enumerate(r.get("values", [])):
    print(1 + i, row)
