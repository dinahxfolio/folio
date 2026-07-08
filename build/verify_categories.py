from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()
resp = sheets.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range="SETTINGS!A14:E22", valueRenderOption="FORMATTED_VALUE"
).execute()
for i, row in enumerate(resp.get("values", [])):
    print(14 + i, row)
