from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()

# Jan: title, opening pill, headers, sample rows with balance calc
resp = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID,
    ranges=["Jan!B1:H10", "Feb!B1:H6"],
    valueRenderOption="FORMATTED_VALUE"
).execute()
for vr in resp["valueRanges"]:
    print("---", vr["range"], "---")
    for row in vr.get("values", []):
        print(row)
