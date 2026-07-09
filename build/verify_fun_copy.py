from auth import get_services
with open("spreadsheet_id_fun.txt") as f:
    FUN_ID = f.read().strip()
sheets, _ = get_services()

meta = sheets.spreadsheets().get(spreadsheetId=FUN_ID, fields="sheets.properties").execute()
for s in meta["sheets"]:
    p = s["properties"]
    print(p["index"], p["title"], p["sheetId"])

r = sheets.spreadsheets().values().get(spreadsheetId=FUN_ID, range="DASHBOARD!B1", valueRenderOption="FORMULA").execute()
print("DASHBOARD B1 formula:", r.get("values"))
r2 = sheets.spreadsheets().values().get(spreadsheetId=FUN_ID, range="DASHBOARD!B1", valueRenderOption="FORMATTED_VALUE").execute()
print("DASHBOARD B1 value:", r2.get("values"))
