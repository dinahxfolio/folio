from auth import get_services
with open("spreadsheet_id_fun.txt") as f:
    FUN_ID = f.read().strip()
sheets, _ = get_services()

for tab in ["DASHBOARD", "ANNUAL OVERVIEW", "GOALS", "Jan"]:
    meta = sheets.spreadsheets().get(spreadsheetId=FUN_ID, ranges=[tab], fields="sheets(conditionalFormats)").execute()
    cf = meta["sheets"][0].get("conditionalFormats", [])
    print(f"=== {tab}: {len(cf)} rules ===")
    for i, rule in enumerate(cf):
        cond = rule["booleanRule"]["condition"]
        print(i, cond.get("type"), cond.get("values", []), "->", rule["booleanRule"]["format"])
