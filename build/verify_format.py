from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, _ = get_services()
resp = sheets.spreadsheets().get(
    spreadsheetId=SPREADSHEET_ID,
    fields="sheets(properties,merges)"
).execute()
props = resp["sheets"][0]["properties"]
print("gridProperties.hideGridlines:", props["gridProperties"].get("hideGridlines"))
print("tabColor:", props.get("tabColor"))
print("merge count:", len(resp["sheets"][0].get("merges", [])))
print("first 5 merges:", resp["sheets"][0].get("merges", [])[:5])

resp2 = sheets.spreadsheets().get(
    spreadsheetId=SPREADSHEET_ID,
    ranges=["SETTINGS!B5", "SETTINGS!B52"],
    fields="sheets(data(rowData(values(note))))"
).execute()
print(resp2)
