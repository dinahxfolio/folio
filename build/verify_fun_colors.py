from auth import get_services
with open("spreadsheet_id_fun.txt") as f:
    FUN_ID = f.read().strip()
with open("spreadsheet_id.txt") as f:
    ORIG_ID = f.read().strip()
sheets, _ = get_services()

def check(sid_label, spreadsheet_id, ranges):
    meta = sheets.spreadsheets().get(
        spreadsheetId=spreadsheet_id, ranges=ranges,
        fields="sheets(data(rowData(values(userEnteredFormat(backgroundColor,textFormat(foregroundColor))))))"
    ).execute()
    print(f"--- {sid_label} ---")
    for s in meta["sheets"]:
        for rd in s.get("data", []):
            for row in rd.get("rowData", []):
                for v in row.get("values", []):
                    print(v.get("userEnteredFormat", {}))

check("FUN SETTINGS!B4 (GENERAL band)", FUN_ID, ["SETTINGS!B4"])
check("FUN DASHBOARD!B4 (hero card label)", FUN_ID, ["DASHBOARD!B4"])
check("FUN Jan!B1 (title)", FUN_ID, ["Jan!B1"])
check("ORIGINAL SETTINGS!B4 (should be unchanged Finance green)", ORIG_ID, ["SETTINGS!B4"])
