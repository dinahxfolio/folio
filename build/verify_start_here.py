"""Read back START HERE's live values to confirm content actually landed,
not just that the build script ran without error."""
from auth import get_services
with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()
sheets, _ = get_services()

r = sheets.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="'START HERE'!B1:M17", valueRenderOption="FORMATTED_VALUE").execute()
for i, row in enumerate(r.get("values", [])):
    print(1 + i, row)

# lighter category colours check
meta = sheets.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, ranges=["'START HERE'!I8"], fields="sheets(data(rowData(values(userEnteredFormat(backgroundColor,textFormat)))))").execute()
import json
print(json.dumps(meta, indent=2))
