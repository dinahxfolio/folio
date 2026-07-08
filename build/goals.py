"""Build the GOALS tab.

Per v1 Tab 5. v2 doesn't mock this up but flags it: "Savings goal and debt
payoff formulas need review for the same cross-tab-reference risks as
DASHBOARD" -- addressed here the same way as DASHBOARD/ANNUAL OVERVIEW:
direct SUMIFS per month tab, added together (no INDIRECT, no CHOOSE needed
since this is a whole-year cumulative view, not a single-month lookup).

Category-matching resolution (see build/NOTES.md "GOALS design gap"):
a savings goal only tracks automatically if its name in SETTINGS exactly
equals a Category value, since goal names and Category names are otherwise
unrelated lists. Debt names already align 1:1 with the 4 fixed Debt
payment categories, so no equivalent gap exists there.

Column scheme (padding convention, A blank): 12 content columns B-M, same
grid as DASHBOARD/ANNUAL OVERVIEW.

Row plan (1-based):
  1     Header band: "GOALS"
  2     Instruction note
  4-6   Summary cards: Total saved / Total debt remaining
  8     SAVINGS GOALS band
  9-12  Goal cards, row 1 (4 cards x 3 cols each)
  13-16 Goal cards, row 2
  18    DEBT PAYOFF band
  19    Debt table column headers
  20-23 4 debt rows

Simplifications from v1's colour scheme (documented, not silently dropped):
  - Progress bar colour: v1's 4-tier "light sage / amber / Finance green /
    Finance green+checkmark" collapses to a flat Finance green bar plus a
    checkmark + "Reached!" at 100%, since amber doesn't exist in v2's
    palette and a genuinely distinct "light sage" tone isn't in the
    confirmed set either.
  - Payoff-date colour: v1's "12-24 months / over 24 months" were both
    amber anyway (an apparent v1 inconsistency), so this collapses to two
    states: under 12 months (Finance green) and 12+ months (Rose pale
    tint/Deep rose, the same caution treatment used elsewhere).
  - "Reached [month year]" (the exact month a goal was completed) would
    need a running-cumulative-vs-date array formula to determine; shows a
    plain "Reached!" instead rather than attempting that.
"""
from auth import get_services
from month_tabs import COL_AMOUNT as MONTH_COL_AMOUNT, COL_CATEGORY as MONTH_COL_CATEGORY, \
    COL_TYPE as MONTH_COL_TYPE, FIRST_DATA_ROW, LAST_DATA_ROW, MONTHS
from palette import (
    ARIAL_BLACK,
    CALIBRI,
    CREAM,
    DEEP_ROSE,
    FINANCE_GREEN,
    NEAR_BLACK,
    PALE_NEUTRAL,
    ROSE_PALE_TINT,
    ROW_TINT,
    ROW_WHITE,
    WHITE,
)

SHEET_ID = 500
PAD = 1

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()


def col_letter(logical_col):
    n = logical_col + PAD + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def L(i):
    return col_letter(i)


def grid_range(start_row, end_row, start_col, end_col):
    return {
        "sheetId": SHEET_ID,
        "startRowIndex": start_row,
        "endRowIndex": end_row,
        "startColumnIndex": start_col + PAD,
        "endColumnIndex": end_col + PAD,
    }


def cell_format(bg=None, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=False,
                 italic=False, align="LEFT", valign="MIDDLE", wrap=False,
                 number_format=None):
    text_format = {"foregroundColor": fg, "fontFamily": font, "fontSize": size,
                    "bold": bold, "italic": italic}
    fmt = {
        "horizontalAlignment": align,
        "verticalAlignment": valign,
        "textFormat": text_format,
        "wrapStrategy": "WRAP" if wrap else "OVERFLOW_CELL",
    }
    if bg is not None:
        fmt["backgroundColor"] = bg
    if number_format is not None:
        fmt["numberFormat"] = number_format
    return fmt


def repeat_cell(rng, fmt, fields="userEnteredFormat"):
    return {"repeatCell": {"range": rng, "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def merge(rng, merge_type="MERGE_ALL"):
    return {"mergeCells": {"range": rng, "mergeType": merge_type}}


def border_request(rng, side, color, width, style="DASHED"):
    return {"updateBorders": {"range": rng, side: {"style": style, "width": width, "color": color}}}


N_GOALS = 8
GOAL_CARD_SPANS = [(0, 3), (3, 6), (6, 9), (9, 12)]  # 4 cards per row of cards
GOALS_SETTINGS_ROWS = list(range(53, 61))  # SETTINGS Savings Goals data rows (see NOTES.md)

N_DEBTS = 4
DEBT_SETTINGS_ROWS = list(range(64, 68))  # SETTINGS Debt Tracker data rows
DEBT_NAME_SPAN = (0, 2)
DEBT_START_SPAN = (2, 3)
DEBT_PAID_SPAN = (3, 4)
DEBT_REMAIN_SPAN = (4, 5)
DEBT_PAYMENT_SPAN = (5, 6)
DEBT_PROGRESS_SPAN = (6, 7)
DEBT_PAYOFF_SPAN = (7, 8)


def month_category_sum_all_months(category_cell):
    """Sum a category's Amount across all 12 month tabs directly (additive,
    not INDIRECT/CHOOSE -- this is a whole-year total, not a single-month
    lookup)."""
    parts = []
    for m in MONTHS:
        amt = f"{m}!${MONTH_COL_AMOUNT}${FIRST_DATA_ROW}:${MONTH_COL_AMOUNT}${LAST_DATA_ROW}"
        cat = f"{m}!${MONTH_COL_CATEGORY}${FIRST_DATA_ROW}:${MONTH_COL_CATEGORY}${LAST_DATA_ROW}"
        parts.append(f'SUMIFS({amt},{cat},{category_cell})')
    return "+".join(parts)


def recreate_sheet(sheets):
    """Create-only-if-missing -- see build/NOTES.md on delete+recreate
    breaking cross-sheet formula references. Nothing references GOALS yet,
    but staying consistent with the safe pattern."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    exists = any(s["properties"]["sheetId"] == SHEET_ID for s in meta["sheets"])
    if exists:
        return

    requests = [{"addSheet": {"properties": {"sheetId": 999996, "title": "__temp4__"}}}]
    requests.append({
        "addSheet": {
            "properties": {
                "sheetId": SHEET_ID,
                "title": "GOALS",
                "index": 15,  # after ANNUAL OVERVIEW
                "gridProperties": {"rowCount": 30, "columnCount": 15, "hideGridlines": True,
                                    "frozenRowCount": 1},
                "tabColor": FINANCE_GREEN,
            }
        }
    })
    requests.append({"deleteSheet": {"sheetId": 999996}})
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def clear_sheet_content(sheets):
    """See settings_tab.py's clear_sheet_content() -- resets cell content
    without deleting the sheet, so re-runs don't leave stale content behind
    if the layout ever changes. Also unmerges first (merges are a separate
    sheet-level property updateCells doesn't touch), or a layout change
    that alters merge shapes would collide with the old ones -- confirmed
    on START HERE's single-column -> two-column change."""
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [
            {
                "unmergeCells": {
                    "range": {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 30,
                              "startColumnIndex": 0, "endColumnIndex": 15},
                }
            },
            {
                "updateCells": {
                    "range": {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 30,
                              "startColumnIndex": 0, "endColumnIndex": 15},
                    "fields": "*",
                }
            },
        ]},
    ).execute()


def clear_conditional_formats(sheets):
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, ranges=["GOALS"], fields="sheets(conditionalFormats)"
    ).execute()
    count = len(meta["sheets"][0].get("conditionalFormats", []))
    if not count:
        return
    requests = [{"deleteConditionalFormatRule": {"sheetId": SHEET_ID, "index": 0}} for _ in range(count)]
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def build_requests():
    requests = []

    requests.append(repeat_cell(
        {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 30, "startColumnIndex": 0, "endColumnIndex": 15},
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
    ))

    widths = {0: 28}
    for i in range(1, 13):
        widths[i] = 95
    widths[13] = 40
    widths[14] = 40
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: title.
    title_r = grid_range(0, 1, 0, 12)
    requests.append(merge(title_r))
    requests.append(repeat_cell(title_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=18,
                                                       bold=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 44},
            "fields": "pixelSize",
        }
    })

    # Row 2: instruction note.
    note_r = grid_range(1, 2, 0, 12)
    requests.append(merge(note_r))
    requests.append(repeat_cell(note_r, cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True,
                                                      wrap=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 28},
            "fields": "pixelSize",
        }
    })

    # Rows 4-6: summary cards (Total saved / Total debt remaining, hero).
    for idx, (start, end) in enumerate([(0, 6), (6, 12)]):
        is_hero = idx == 1  # Total debt remaining is the one hero card
        label_r = grid_range(3, 4, start, end)
        value_r = grid_range(4, 5, start, end)
        sub_r = grid_range(5, 6, start, end)
        for r in (label_r, value_r, sub_r):
            requests.append(merge(r))
        bg = DEEP_ROSE if is_hero else PALE_NEUTRAL
        fg = WHITE if is_hero else FINANCE_GREEN
        requests.append(repeat_cell(label_r, cell_format(bg=bg, fg=fg, font=CALIBRI, size=10, bold=True)))
        requests.append(repeat_cell(value_r, cell_format(bg=bg, fg=fg, font=ARIAL_BLACK, size=20, bold=True)))
        requests.append(repeat_cell(sub_r, cell_format(bg=bg, fg=fg, font=CALIBRI, size=9, italic=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 4, "endIndex": 5},
            "properties": {"pixelSize": 32},
            "fields": "pixelSize",
        }
    })

    def section_band(row_idx, bg=FINANCE_GREEN):
        r = grid_range(row_idx, row_idx + 1, 0, 12)
        requests.append(merge(r))
        requests.append(repeat_cell(r, cell_format(bg=bg, fg=WHITE, font=ARIAL_BLACK, size=12, bold=True)))

    # Row 8 (idx 7): SAVINGS GOALS band.
    section_band(7)

    # Goal cards: rows 9-12 (idx 8-11) and 13-16 (idx 12-15).
    for goal_i in range(N_GOALS):
        card_row_group = goal_i // 4
        card_col_i = goal_i % 4
        start, end = GOAL_CARD_SPANS[card_col_i]
        base_row = 8 + card_row_group * 4  # idx
        name_r = grid_range(base_row, base_row + 1, start, end)
        amounts_r = grid_range(base_row + 1, base_row + 2, start, end)
        bar_r = grid_range(base_row + 2, base_row + 3, start, end)
        remaining_r = grid_range(base_row + 3, base_row + 4, start, end)
        for r in (name_r, amounts_r, bar_r, remaining_r):
            requests.append(merge(r))
        requests.append(repeat_cell(name_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                          bold=True)))
        requests.append(repeat_cell(amounts_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9)))
        requests.append(repeat_cell(bar_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9)))
        requests.append(repeat_cell(remaining_r, cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI,
                                                               size=9, italic=True)))
        card_full_r = grid_range(base_row, base_row + 4, start, end)
        requests.append(border_request(card_full_r, "top", PALE_NEUTRAL, 1, style="SOLID"))

    # Row 18 (idx 17): DEBT PAYOFF band.
    section_band(17, bg=DEEP_ROSE)

    # Row 19 (idx 18): debt table column headers.
    debt_header_spans = [DEBT_NAME_SPAN, DEBT_START_SPAN, DEBT_PAID_SPAN, DEBT_REMAIN_SPAN,
                          DEBT_PAYMENT_SPAN, DEBT_PROGRESS_SPAN, DEBT_PAYOFF_SPAN]
    for span in debt_header_spans:
        r = grid_range(18, 19, *span)
        if span[1] - span[0] > 1:
            requests.append(merge(r))
        requests.append(repeat_cell(r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9, bold=True,
                                                     wrap=True)))

    # Rows 20-23 (idx 19-22): 4 debt rows.
    for i in range(N_DEBTS):
        r = 19 + i
        band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
        name_r = grid_range(r, r + 1, *DEBT_NAME_SPAN)
        requests.append(merge(name_r))
        requests.append(repeat_cell(name_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10)))
        for span in (DEBT_START_SPAN, DEBT_PAID_SPAN, DEBT_REMAIN_SPAN, DEBT_PAYMENT_SPAN):
            requests.append(repeat_cell(
                grid_range(r, r + 1, *span),
                cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=9, align="RIGHT",
                            number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
            ))
        requests.append(repeat_cell(grid_range(r, r + 1, *DEBT_PROGRESS_SPAN),
                                     cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=9, align="CENTER")))
        payoff_r = grid_range(r, r + 1, *DEBT_PAYOFF_SPAN)
        requests.append(repeat_cell(payoff_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                            align="CENTER")))

    # Monthly payment column is the one editable input on this tab.
    payment_col_r = grid_range(19, 19 + N_DEBTS, *DEBT_PAYMENT_SPAN)
    requests.append(repeat_cell(payment_col_r, cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI,
                                                             size=9, bold=True, align="RIGHT",
                                                             number_format={"type": "NUMBER",
                                                                            "pattern": "#,##0.00"})))

    # Payoff-date colour: under 12 months = Finance green text; 12+ months
    # = Rose pale tint / Deep rose (v1's 12-24 and 24+ tiers were both amber
    # anyway, so this collapses to one caution state -- see module docstring).
    months_helper_col = 8  # logical col used below for a months-to-payoff helper
    payoff_range = grid_range(19, 19 + N_DEBTS, *DEBT_PAYOFF_SPAN)
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [payoff_range],
                "booleanRule": {
                    "condition": {"type": "CUSTOM_FORMULA",
                                   "values": [{"userEnteredValue":
                                               f'=AND(ISNUMBER({L(months_helper_col)}20),{L(months_helper_col)}20>=12)'}]},
                    "format": {"backgroundColor": ROSE_PALE_TINT,
                               "textFormat": {"foregroundColor": DEEP_ROSE, "bold": True}},
                },
            },
            "index": 0,
        }
    })
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [payoff_range],
                "booleanRule": {
                    "condition": {"type": "CUSTOM_FORMULA",
                                   "values": [{"userEnteredValue":
                                               f'=AND(ISNUMBER({L(months_helper_col)}20),{L(months_helper_col)}20<12)'}]},
                    "format": {"textFormat": {"foregroundColor": FINANCE_GREEN, "bold": True}},
                },
            },
            "index": 0,
        }
    })

    # Helper column (N, logical 12) for months-to-payoff, used only by the
    # conditional formatting above -- kept off to the side, visible, with a note.
    helper_range = grid_range(19, 19 + N_DEBTS, 12, 13)
    requests.append(repeat_cell(helper_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8)))
    requests.append({
        "updateCells": {
            "range": grid_range(19, 20, 12, 13),
            "rows": [{"values": [{"note": "Internal helper: months remaining until payoff, used "
                                           "only for the payoff-date colour coding above (conditional "
                                           "formatting can't derive this inline as cleanly as a plain "
                                           "cell can). Please don't delete."}]}],
            "fields": "note",
        }
    })

    layout = {}
    return requests, layout


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"GOALS!{a1}", "values": [[v]]})

    cell(f"{L(0)}1", "GOALS")
    cell(f"{L(0)}2", "Progress updates automatically from your transactions.")

    # Savings goals (rows 9-16).
    goal_saved_cells = []
    for goal_i in range(N_GOALS):
        card_row_group = goal_i // 4
        card_col_i = goal_i % 4
        start, _end = GOAL_CARD_SPANS[card_col_i]
        base_row = 9 + card_row_group * 4  # 1-based
        col = L(start)
        settings_row = GOALS_SETTINGS_ROWS[goal_i]
        name_cell = f"SETTINGS!$C${settings_row}"
        target_cell = f"SETTINGS!$D${settings_row}"
        date_cell = f"SETTINGS!$E${settings_row}"

        saved_expr = f'IF({name_cell}="","",{month_category_sum_all_months(name_cell)})'
        cell(f"{col}{base_row}", f'=IF({name_cell}="","Add a goal in Settings",{name_cell})')
        cell(f"{col}{base_row + 1}",
             f'=IF({name_cell}="","",CONCATENATE(SETTINGS!$D$7,TEXT({saved_expr},"#,##0.00")'
             f'," of ",SETTINGS!$D$7,TEXT({target_cell},"#,##0.00")))')
        ratio_expr = f'IFERROR(MIN({saved_expr}/{target_cell},1),0)'
        cell(f"{col}{base_row + 2}",
             f'=IF({name_cell}="","",'
             f'IF({ratio_expr}>=1,"✅ Goal reached!",'
             f'IFERROR(SPARKLINE({ratio_expr},{{"charttype","bar";"max",1;"color1","#3D7A5A"}}),"")))')
        cell(f"{col}{base_row + 3}",
             f'=IF({name_cell}="","",IF({ratio_expr}>=1,"",'
             f'CONCATENATE("Remaining: ",SETTINGS!$D$7,TEXT(MAX({target_cell}-{saved_expr},0),"#,##0.00"),'
             f'" · by ",TEXT({date_cell},"mmm yyyy"))))')
        goal_saved_cells.append((name_cell, saved_expr))

    # Total saved across all goals: sum only the populated goal slots.
    total_saved_terms = [f'IF({name_cell}<>"",{saved_expr},0)' for name_cell, saved_expr in goal_saved_cells]
    total_saved_formula = "=" + "+".join(total_saved_terms)
    cell(f"{L(0)}4", "TOTAL SAVED")
    cell(f"{L(0)}5", f'=CONCATENATE(SETTINGS!$D$7,TEXT({total_saved_formula[1:]},"#,##0.00"))')
    cell(f"{L(0)}6", "across all goals")

    # Debt payoff (rows 20-23).
    name_col = L(DEBT_NAME_SPAN[0])
    start_col = L(DEBT_START_SPAN[0])
    paid_col = L(DEBT_PAID_SPAN[0])
    remain_col = L(DEBT_REMAIN_SPAN[0])
    payment_col = L(DEBT_PAYMENT_SPAN[0])
    progress_col = L(DEBT_PROGRESS_SPAN[0])
    payoff_col = L(DEBT_PAYOFF_SPAN[0])
    months_col = L(12)  # N

    cell(f"{name_col}19", "Debt name")
    cell(f"{start_col}19", '=CONCATENATE("Starting (",SETTINGS!$D$7,")")')
    cell(f"{paid_col}19", "Paid off")
    cell(f"{remain_col}19", "Remaining")
    cell(f"{payment_col}19", '=CONCATENATE("Monthly (",SETTINGS!$D$7,")")')
    cell(f"{progress_col}19", "Progress")
    cell(f"{payoff_col}19", "Est. payoff")

    debt_starts = []
    debt_paids = []
    for i in range(N_DEBTS):
        r = 20 + i
        settings_row = DEBT_SETTINGS_ROWS[i]
        name_cell = f"SETTINGS!$C${settings_row}"
        start_cell = f"SETTINGS!$D${settings_row}"
        cell(f"{name_col}{r}", f'=IF({name_cell}="","Add a debt in Settings",{name_cell})')
        cell(f"{start_col}{r}", f'=IF({name_cell}="","",{start_cell})')
        paid_expr = month_category_sum_all_months(name_cell)
        cell(f"{paid_col}{r}", f'=IF({name_cell}="","",{paid_expr})')
        cell(f"{remain_col}{r}", f'=IF({name_cell}="","",MAX({start_cell}-({paid_expr}),0))')
        # Monthly payment: editable input, left blank for the user to fill in.
        cell(f"{progress_col}{r}",
             f'=IF({name_cell}="","",IFERROR(SPARKLINE(MIN(({paid_expr})/{start_cell},1),'
             f'{{"charttype","bar";"max",1;"color1","#A8495F"}}),""))')
        months_expr = f'CEILING({remain_col}{r}/{payment_col}{r},1)'
        cell(f"{payoff_col}{r}",
             f'=IF(OR({name_cell}="",{payment_col}{r}="",{payment_col}{r}=0),"",'
             f'IFERROR(TEXT(EDATE(TODAY(),{months_expr}),"mmm yyyy"),""))')
        cell(f"{months_col}{r}",
             f'=IF(OR({name_cell}="",{payment_col}{r}="",{payment_col}{r}=0),"",IFERROR({months_expr},""))')
        debt_starts.append(f'IF({name_cell}<>"",{start_cell},0)')
        debt_paids.append(f'IF({name_cell}<>"",{paid_expr},0)')

    # Total debt remaining: sum of starting balances minus all debt payments.
    total_start = "+".join(debt_starts)
    total_paid = "+".join(debt_paids)
    cell(f"{L(6)}4", "TOTAL DEBT REMAINING")
    cell(f"{L(6)}5", f'=CONCATENATE(SETTINGS!$D$7,TEXT(MAX(({total_start})-({total_paid}),0),"#,##0.00"))')
    cell(f"{L(6)}6", "starting balance minus payments made")

    return values


def main():
    sheets, _drive = get_services()

    recreate_sheet(sheets)
    clear_sheet_content(sheets)
    clear_conditional_formats(sheets)

    requests, layout = build_requests()
    CHUNK = 400
    for i in range(0, len(requests), CHUNK):
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": requests[i:i + CHUNK]}
        ).execute()

    values = build_values(layout)
    VCHUNK = 300
    for i in range(0, len(values), VCHUNK):
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": values[i:i + VCHUNK]},
        ).execute()

    print("GOALS built.")


if __name__ == "__main__":
    main()
