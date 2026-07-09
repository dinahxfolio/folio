"""Swap the DASHBOARD budget-table Progress column's SPARKLINE bar colour
from Finance green to Lilac on the Fun copy. The colour is a literal hex
baked into the SPARKLINE formula string (Sheets SPARKLINE has no separate
format/colorStyle field for this), so this reads each cell's live formula
and does an exact substring swap ("#3D7A5A" -> "#B39DDB"), leaving every
other part of the formula (and every other cell/tab) untouched. Scoped to
DASHBOARD only per Minnie's request -- GOALS' savings-goal progress bar
uses the same green and is deliberately left alone.
"""
from auth import get_services

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()

OLD_HEX = "#3D7A5A"
NEW_HEX = "#B39DDB"
COLUMN = "H"
RANGE = f"DASHBOARD!{COLUMN}1:{COLUMN}70"


def main():
    sheets, _drive = get_services()

    resp = sheets.spreadsheets().values().get(
        spreadsheetId=FUN_SPREADSHEET_ID, range=RANGE, valueRenderOption="FORMULA"
    ).execute()
    rows = resp.get("values", [])

    data = []
    for i, row in enumerate(rows):
        if row and OLD_HEX in row[0]:
            new_formula = row[0].replace(OLD_HEX, NEW_HEX)
            data.append({"range": f"DASHBOARD!{COLUMN}{i + 1}", "values": [[new_formula]]})

    print(f"{len(data)} Progress-bar formulas to update.")
    if data:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=FUN_SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": data},
        ).execute()
    print("Done.")


if __name__ == "__main__":
    main()
