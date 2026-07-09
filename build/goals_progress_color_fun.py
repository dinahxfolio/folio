"""Swap GOALS' progress-bar SPARKLINE colours on the Fun copy, per Minnie's
request: savings-goal progress bars (Finance green) -> Blue, debt-payoff
progress bars (Deep rose) -> Hot pink. Same technique as
progress_bar_color_fun.py -- the colour is a literal hex baked into the
SPARKLINE formula string, so this reads each cell's live formula and does
an exact substring swap, touching nothing else on the tab (not even the
"Goal reached!" text branch of the same formula, which has no colour to
swap). Scoped to GOALS only.
"""
from auth import get_services

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()

SWAPS = [
    ("#3D7A5A", "#7FA8D9"),  # savings-goal progress: Finance green -> Blue
    ("#A8495F", "#FF3366"),  # debt-payoff progress: Deep rose -> Hot pink
]

RANGE = "GOALS!B1:M25"


def main():
    sheets, _drive = get_services()

    resp = sheets.spreadsheets().values().get(
        spreadsheetId=FUN_SPREADSHEET_ID, range=RANGE, valueRenderOption="FORMULA"
    ).execute()
    rows = resp.get("values", [])

    data = []
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            if not isinstance(val, str):
                continue
            new_val = val
            for old_hex, new_hex in SWAPS:
                if old_hex in new_val:
                    new_val = new_val.replace(old_hex, new_hex)
            if new_val != val:
                col_letter = chr(ord("B") + c_i)
                data.append({"range": f"GOALS!{col_letter}{r_i + 1}", "values": [[new_val]]})

    print(f"{len(data)} progress-bar formulas to update.")
    if data:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=FUN_SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": data},
        ).execute()
    print("Done.")


if __name__ == "__main__":
    main()
