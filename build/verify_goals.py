"""Read back GOALS' live calculated values to confirm formulas actually
computed, not just that the build script ran without error."""
from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()

ranges = ["GOALS!B1:M16", "GOALS!B18:N23"]
resp = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption="FORMATTED_VALUE"
).execute()
for vr in resp["valueRanges"]:
    print("---", vr["range"], "---")
    for row in vr.get("values", []):
        print(row)
