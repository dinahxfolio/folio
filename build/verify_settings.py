from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()

ranges = ["SETTINGS!A1:E13", "SETTINGS!A50:E66", "SETTINGS!A67:E75"]
resp = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=ranges, valueRenderOption="FORMATTED_VALUE"
).execute()
for vr in resp["valueRanges"]:
    print("---", vr["range"], "---")
    for row in vr.get("values", []):
        print(row)

print()
resp2 = sheets.spreadsheets().values().batchGet(
    spreadsheetId=SPREADSHEET_ID, ranges=["SETTINGS!D13", "SETTINGS!D51", "SETTINGS!D62"],
    valueRenderOption="FORMULA"
).execute()
for vr in resp2["valueRanges"]:
    print(vr["range"], vr.get("values"))

# notes check
resp3 = sheets.spreadsheets().get(
    spreadsheetId=SPREADSHEET_ID, ranges=["SETTINGS!D5", "SETTINGS!D8", "SETTINGS!C52", "SETTINGS!C63"],
    fields="sheets(data(rowData(values(note))))"
).execute()
print(resp3)

# merges + column count
meta = sheets.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, fields="sheets(properties,merges)").execute()
props = meta["sheets"][0]["properties"]
print("columnCount:", props["gridProperties"]["columnCount"], "hideGridlines:", props["gridProperties"].get("hideGridlines"))
print("merges:", len(meta["sheets"][0].get("merges", [])))
