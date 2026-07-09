"""Repaint the Fun colourway copy. Colour-only pass: every request here uses
a narrow field mask (userEnteredFormat.backgroundColor and/or
userEnteredFormat.textFormat.foregroundColor only), never touching values,
formulas, merges, data validation, or chart data/type/position. Every range
is built via each build module's own grid_range() (which already accounts
for the padding column), never hand-computed, to avoid off-by-one bugs from
mixing logical and physical column indices.

Role mapping (Neutral -> Fun), per Minnie's exact palette:
  Structural (bands/headers/tab colours), Savings category -> Lilac
  Income category, Bills category                          -> Blue
  Debt category, hero cards, over-budget/negative states    -> Pink
  Expenses category                                         -> Yellow (pale+text only, no solid -- see note)
  Upcoming/caution (old Rose pale tint role)                 -> Yellow (pale+text)
  Paid/fully-reached status (new -- no Neutral equivalent)   -> Green (pale+text), added fresh
  Pale neutral, Cream, row banding, near-black text, Hot pink, month-tab grey -> unchanged (not in the given palette)

Yellow and Green have no "full" solid hex in Minnie's spec (pale + text
only) -- so anywhere Neutral used a *solid* fill (category dividers, badges)
for what's now a Yellow-mapped role (Expenses), the Fun file uses pale
bg + dark text instead of solid bg + white text. This is a deliberate style
break for Expenses specifically, not an oversight.
"""
import goals
import month_tabs
import settings_tab
import start_here
import annual_overview
import dashboard
from fun_palette import (
    BLUE, BLUE_PALE, BLUE_TEXT,
    GREEN_PALE, GREEN_TEXT,
    LILAC, LILAC_PALE, LILAC_TEXT,
    PINK, PINK_PALE, PINK_TEXT,
    YELLOW_PALE, YELLOW_TEXT,
)
from auth import get_services

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()

WHITE = {"red": 1, "green": 1, "blue": 1}


def repaint(rng, bg=None, fg=None):
    """rng: a GridRange dict, e.g. from a module's own grid_range()."""
    fmt = {}
    fields = []
    if bg is not None:
        fmt["backgroundColor"] = bg
        fields.append("backgroundColor")
    if fg is not None:
        fmt.setdefault("textFormat", {})["foregroundColor"] = fg
        fields.append("textFormat.foregroundColor")
    return {
        "repeatCell": {
            "range": rng,
            "cell": {"userEnteredFormat": fmt},
            "fields": ",".join(f"userEnteredFormat.{f}" for f in fields),
        }
    }


def main():
    sheets, _drive = get_services()
    requests = []

    # ================= SETTINGS (sheetId 100) =================
    S = settings_tab
    gr = S.grid_range  # (start_row, end_row, start_col, end_col) -> GridRange, PAD-aware
    _struct_requests, layout = S.build_requests()  # local call only, no API -- just need `layout`

    requests.append(repaint(gr(3, 4, 0, 7), bg=LILAC, fg=WHITE))       # GENERAL band
    requests.append(repaint(gr(10, 11, 0, 7), bg=LILAC, fg=WHITE))     # MONTHLY BUDGET TARGETS band
    goals_band_idx = layout["goals_start_idx"] - 3
    requests.append(repaint(gr(goals_band_idx, goals_band_idx + 1, 0, 7), bg=LILAC, fg=WHITE))  # SAVINGS GOALS band
    debt_band_idx = layout["debt_start_idx"] - 2
    requests.append(repaint(gr(debt_band_idx, debt_band_idx + 1, 0, 7), bg=PINK, fg=WHITE))      # DEBT TRACKER band

    # Editable general-setting values (Year/Currency/Starting balance/Savings rate threshold): text colour only.
    requests.append(repaint(gr(5, 9, 1, 2), fg=LILAC_TEXT))

    # Category dividers, by group (divider row sits one row above each group's first category row).
    cat_map = layout["category_row_map"]
    divider_fmt = {"INCOME": (BLUE, WHITE), "BILLS": (BLUE, WHITE), "EXPENSES": (YELLOW_PALE, YELLOW_TEXT),
                   "SAVINGS": (LILAC, WHITE), "DEBT PAYMENTS": (PINK, WHITE)}
    for group_name, (bg, fg) in divider_fmt.items():
        start_idx, _end_idx = cat_map[group_name]
        divider_idx = start_idx - 1
        requests.append(repaint(gr(divider_idx, divider_idx + 1, 0, 2), bg=bg, fg=fg))

    # Closing note (savings rate threshold) -- was Rose pale tint/Deep rose.
    note_idx = layout["note_idx"]
    requests.append(repaint(gr(note_idx, note_idx + 1, 0, 4), bg=YELLOW_PALE, fg=YELLOW_TEXT))

    # ================= Month tabs (sheetIds 300-311) =================
    M = month_tabs
    for m in M.MONTHS:
        sid = M.SHEET_IDS[m]
        requests.append(repaint(M.grid_range(sid, 0, 1, 0, 3), bg=LILAC, fg=WHITE))   # title
        requests.append(repaint(M.grid_range(sid, 0, 1, 3, 7), bg=LILAC, fg=WHITE))   # opening-balance pill

    # ================= DASHBOARD (sheetId 200) =================
    D = dashboard
    gr = D.grid_range
    requests.append(repaint(gr(0, 1, 0, 5), bg=LILAC, fg=WHITE))          # title band
    requests.append(repaint(gr(0, 1, 5, 6), fg=LILAC_TEXT))               # month selector text
    requests.append(repaint(gr(3, 6, 0, 4), bg=PINK, fg=WHITE))           # hero card (Left to spend)
    requests.append(repaint(gr(11, 12, 0, 12), bg=BLUE, fg=WHITE))        # UPCOMING BILLS band
    requests.append(repaint(gr(D.BUDGET_BAND_IDX, D.BUDGET_BAND_IDX + 1, 0, 7), bg=LILAC, fg=WHITE))  # MONTHLY BUDGET band

    row_cursor = D.FIRST_DIVIDER_IDX
    dash_divider_fmt = {"INCOME": (BLUE, WHITE), "BILLS": (BLUE, WHITE), "EXPENSES": (YELLOW_PALE, YELLOW_TEXT),
                         "SAVINGS": (LILAC, WHITE), "DEBT PAYMENTS": (PINK, WHITE)}
    for group_name, _color, categories in D.TYPE_GROUPS:
        bg, fg = dash_divider_fmt[group_name]
        requests.append(repaint(gr(row_cursor, row_cursor + 1, 0, 7), bg=bg, fg=fg))
        row_cursor += 1 + len(categories)

    # ================= ANNUAL OVERVIEW (sheetId 400) =================
    A = annual_overview
    gr = A.grid_range
    requests.append(repaint(gr(0, 1, A.LABEL_COL, A.TOTAL_COL + 1), bg=LILAC, fg=WHITE))          # header band
    requests.append(repaint(gr(4, 5, A.LABEL_COL, A.LABEL_COL + 7), fg=LILAC_TEXT))                # Best month value
    requests.append(repaint(gr(4, 5, 7, 14), fg=LILAC_TEXT))                                       # Tightest month value
    requests.append(repaint(gr(7, 8, A.LABEL_COL, A.TOTAL_COL + 1), bg=LILAC, fg=WHITE))            # grid header row
    requests.append(repaint(gr(13, 14, A.LABEL_COL, A.TOTAL_COL + 1), bg=LILAC_PALE))               # spacer row tint
    requests.append(repaint(gr(14, 15, A.LABEL_COL, A.TOTAL_COL + 1), bg=LILAC_PALE, fg=LILAC_TEXT))  # Left over row
    requests.append(repaint(gr(8, 16, A.TOTAL_COL, A.TOTAL_COL + 1), bg=LILAC_PALE, fg=LILAC_TEXT))  # Total column

    # ================= GOALS (sheetId 500) =================
    G = goals
    gr = G.grid_range
    requests.append(repaint(gr(0, 1, 0, 12), bg=LILAC, fg=WHITE))          # title
    requests.append(repaint(gr(3, 6, 6, 12), bg=PINK, fg=WHITE))           # Total debt remaining (hero)
    requests.append(repaint(gr(3, 6, 0, 6), fg=LILAC_TEXT))                # Total saved text
    requests.append(repaint(gr(7, 8, 0, 12), bg=LILAC, fg=WHITE))          # SAVINGS GOALS band
    requests.append(repaint(gr(17, 18, 0, 12), bg=PINK, fg=WHITE))         # DEBT PAYOFF band
    for goal_i in range(G.N_GOALS):
        card_row_group = goal_i // 4
        card_col_i = goal_i % 4
        start, end = G.GOAL_CARD_SPANS[card_col_i]
        base_row = 8 + card_row_group * 4
        requests.append(repaint(gr(base_row + 3, base_row + 4, start, end), fg=LILAC_TEXT))
    requests.append(repaint(gr(19, 19 + G.N_DEBTS, *G.DEBT_PAYMENT_SPAN), fg=LILAC_TEXT))

    # ================= START HERE (sheetId 600) =================
    H = start_here
    gr = H.grid_range
    requests.append(repaint(gr(0, 1, *H.FULL_SPAN), bg=LILAC, fg=WHITE))    # hero
    requests.append(repaint(gr(5, 6, *H.RIGHT_SPAN), bg=LILAC, fg=WHITE))   # CATEGORY QUICK REFERENCE band
    requests.append(repaint(gr(12, 13, *H.FULL_SPAN), bg=LILAC, fg=WHITE))  # TIPS band
    h_fmt = {"INCOME": (BLUE_PALE, BLUE_TEXT), "BILLS": (BLUE_PALE, BLUE_TEXT),
             "EXPENSES": (YELLOW_PALE, YELLOW_TEXT), "SAVINGS": (LILAC_PALE, LILAC_TEXT),
             "DEBT PAYMENTS": (PINK_PALE, PINK_TEXT)}
    for i, (group_name, _color, _categories) in enumerate(H.CATEGORY_GROUPS):
        r = 7 + i
        bg, fg = h_fmt[group_name]
        requests.append(repaint(gr(r, r + 1, *H.RIGHT_SPAN), bg=bg, fg=fg))

    print(f"{len(requests)} colour-only repaint requests queued.")

    CHUNK = 300
    for i in range(0, len(requests), CHUNK):
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=FUN_SPREADSHEET_ID, body={"requests": requests[i:i + CHUNK]}
        ).execute()

    print("Base repaint pass complete.")


if __name__ == "__main__":
    main()
