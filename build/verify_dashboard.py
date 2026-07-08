"""Read back DASHBOARD's live calculated values to confirm formulas actually
computed, not just that the build scripts ran without error."""
from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()

ranges = ["DASHBOARD!B1:M10", "DASHBOARD!B11:M20", "DASHBOARD!B22:M30", "DASHBOARD!B59:M61"]
resp = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption="FORMATTED_VALUE"
).execute()
for vr in resp["valueRanges"]:
    print("---", vr["range"], "---")
    for row in vr.get("values", []):
        print(row)
