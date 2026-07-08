from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()

ranges = ["SETTINGS!A1:D13", "SETTINGS!A50:D66", "SETTINGS!A67:D75"]

resp = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption="FORMATTED_VALUE"
).execute()
for vr in resp["valueRanges"]:
    print("---", vr["range"], "---")
    for row in vr.get("values", []):
        print(row)

print()
print("=== Formulas (UNFORMATTED / FORMULA render) ===")
resp2 = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=["SETTINGS!B13", "SETTINGS!C51", "SETTINGS!C62"],
    valueRenderOption="FORMULA"
).execute()
for vr in resp2["valueRanges"]:
    print(vr["range"], vr.get("values"))
