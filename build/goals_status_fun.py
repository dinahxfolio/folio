"""Add NEW Green 'Paid/reached' conditional-format rules to GOALS on the Fun
copy -- there's no Neutral equivalent to recolour (v1/v2 never called out a
distinct 'reached' colour, per goals.py's docstring), so this is a fresh
addition rather than a recolour, scoped exactly to Minnie's confirmed
mapping: "GOALS' fully-reached/paid-off state (Goal reached! / debt fully
paid)" and nowhere else.

Savings goal reached: the card's progress cell shows the literal text
"Goal reached!" once a goal's ratio hits 100% (see goals.py build_values()) --
matched by TEXT_CONTAINS rather than TEXT_EQ since the cell also contains a
leading checkmark emoji.

Debt fully paid: the Remaining column reaching exactly 0 is the existing,
already-computed signal for "paid off" (no formula change needed) --
matched by NUMBER_EQ 0.

Colour-only, additive: no existing rule/range/formula is touched.
"""
import goals as G
from auth import get_services
from fun_palette import GREEN_PALE, GREEN_TEXT

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()


def main():
    sheets, _drive = get_services()

    meta = sheets.spreadsheets().get(
        spreadsheetId=FUN_SPREADSHEET_ID, ranges=["GOALS"], fields="sheets(conditionalFormats)"
    ).execute()
    existing_count = len(meta["sheets"][0].get("conditionalFormats", []))

    requests = []

    # Savings goal "Goal reached!" cells (8 goal cards, each card's 3rd data row).
    goal_ranges = []
    for goal_i in range(G.N_GOALS):
        card_row_group = goal_i // 4
        card_col_i = goal_i % 4
        start, end = G.GOAL_CARD_SPANS[card_col_i]
        base_row = 8 + card_row_group * 4  # 0-indexed
        goal_ranges.append(G.grid_range(base_row + 2, base_row + 3, start, end))

    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": goal_ranges,
                "booleanRule": {
                    "condition": {"type": "TEXT_CONTAINS",
                                   "values": [{"userEnteredValue": "Goal reached!"}]},
                    "format": {"backgroundColor": GREEN_PALE,
                               "textFormat": {"foregroundColor": GREEN_TEXT, "bold": True}},
                },
            },
            "index": existing_count,
        }
    })

    # Debt fully paid: Remaining column reaches exactly 0.
    remain_range = G.grid_range(19, 19 + G.N_DEBTS, *G.DEBT_REMAIN_SPAN)
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [remain_range],
                "booleanRule": {
                    "condition": {"type": "NUMBER_EQ", "values": [{"userEnteredValue": "0"}]},
                    "format": {"backgroundColor": GREEN_PALE,
                               "textFormat": {"foregroundColor": GREEN_TEXT, "bold": True}},
                },
            },
            "index": existing_count + 1,
        }
    })

    print(f"{len(requests)} new GOALS status rule(s) queued.")
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=FUN_SPREADSHEET_ID, body={"requests": requests}
    ).execute()
    print("GOALS Green status rules added.")


if __name__ == "__main__":
    main()
