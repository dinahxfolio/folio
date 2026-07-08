"""Build the DASHBOARD tab.

Column scheme (padding convention applies, A blank): 12 content columns B-M,
a 12-wide grid so both the 3-card headline row (4 cols/card) and the 4-card
breakdown row (3 cols/card) divide evenly. N/O are a buffer gap; P-T hold
small visible (not hidden) helper cells/columns -- MonthNumber and the
Upcoming Bills ranking table -- each with an explanatory note, same pattern
as month tabs' I1 closing-balance helper.

Row plan (1-based; MONTHLY BUDGET onward shifts with N_HELPER_BILLS, since
the Upcoming Bills block's height depends on how many Bills categories
SETTINGS has -- currently 12, so the numbers below reflect that):
  1     Header bar: title (B:F) + month selector (G1) + days-left pill (I:L)
  2     Instruction note
  4-6   Headline cards (Left to spend / Total income / Total spent): label / value / subtitle
  8-10  Breakdown cards (Bills / Expenses / Savings / Debt): label / value / subtitle
  12    UPCOMING BILLS band
  13    Upcoming Bills column headers
  14-25 up to 12 unpaid-bill rows, ranked by soonest due day
  27    MONTHLY BUDGET band
  28    Budget table column headers (Category / Budget target / Actual / Difference / Progress)
  29-63 category rows mirroring SETTINGS' 5-group structure (35 rows incl. 5 dividers)
  65    Total row

Formula-level decisions per design-brief-v2 Section 6:
  - Month-tab totals via CHOOSE(), not INDIRECT().
  - Currency symbol in header/card labels only, never baked into a numeric cell.

Budget Target column is a live reference to SETTINGS (=SETTINGS!D<row>), not an
independently editable/carried-forward value -- v1's own stated rule ("SETTINGS
is the source of truth for all category names and budget targets... every
other tab references SETTINGS, never its own hardcoded values") takes
precedence over v1's DASHBOARD-specific wording about an editable, carried-
forward target, since v2 didn't re-open that rule and the per-month-editable
design doesn't fit a single shared SETTINGS table. See build/NOTES.md.
"""
from auth import get_services
from month_tabs import COL_AMOUNT as MONTH_COL_AMOUNT, COL_CATEGORY as MONTH_COL_CATEGORY, \
    COL_TYPE as MONTH_COL_TYPE, FIRST_DATA_ROW, LAST_DATA_ROW, MONTHS
from palette import (
    ARIAL_BLACK,
    CALIBRI,
    CREAM,
    DEEP_ROSE,
    DUSTY_BLUE,
    FINANCE_GREEN,
    HOT_PINK,
    MUTED_TAN,
    NEAR_BLACK,
    PALE_NEUTRAL,
    ROSE_PALE_TINT,
    ROW_TINT,
    ROW_WHITE,
    WHITE,
)

SHEET_ID = 200
PAD = 1
N_HELPER_BILLS = 12  # matches SETTINGS' 12 Bills categories (was 7)

# MONTHLY BUDGET band's row position, computed rather than hardcoded: it
# must sit right after the Upcoming Bills block (band + header + N data
# rows + 1 spacer), whose height depends on N_HELPER_BILLS.
BUDGET_BAND_IDX = 14 + N_HELPER_BILLS
BUDGET_HEADER_IDX = BUDGET_BAND_IDX + 1
FIRST_DIVIDER_IDX = BUDGET_HEADER_IDX + 1  # 0-indexed row of the first category-group divider

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()


def col_letter(logical_col):
    n = logical_col + PAD + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


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


def border_request(rng, side, color, width=2, style="SOLID"):
    return {"updateBorders": {"range": rng, side: {"style": style, "width": width, "color": color}}}


# Logical column letters, content is B..M (indices 0-11).
def L(i):
    return col_letter(i)


# Budget table column spans (logical, end-exclusive).
CAT_SPAN = (0, 3)     # B:D -- narrowed (was B:E) to leave I:M free for charts
TARGET_SPAN = (3, 4)  # E
ACTUAL_SPAN = (4, 5)  # F
DIFF_SPAN = (5, 6)    # G
PROG_SPAN = (6, 7)    # H

# Helper columns beyond the buffer (logical indices 14-18 -> P,Q,R,S,T).
MONTH_NUMBER_COL = L(14)     # P
BILLS_CAT_COL = L(15)        # Q
BILLS_DUE_COL = L(16)        # R
BILLS_PAID_COL = L(17)       # S
BILLS_RANK_COL = L(18)       # T
CHART_DATA_COL = L(19)       # U (group label, for the donut chart)
CHART_DATA_VALUE_COL = L(20)  # V (group actual total)
CHART_DATA_COL_IDX = 19 + PAD  # physical column index of U, for chart GridRange sources

# Bar-chart data (W,X,Y): a clean, gap-free 25-row mirror of the 4 spending
# groups' Category/Target/Actual cells. The Sheets API rejects multi-range
# chart sources unless the ranges are contiguous, and the real budget table
# has divider rows breaking each group up -- so the chart reads from this
# single unbroken block instead, which just references the already-computed
# budget-table cells (no new calculation, same source of truth).
BAR_CAT_COL = L(21)   # W
BAR_TGT_COL = L(22)   # X
BAR_ACT_COL = L(23)   # Y
BAR_CHART_ROWS = 25   # 7 Bills + 9 Expenses + 5 Savings + 4 Debt

MONTH_NUMBER_CELL = f"{MONTH_NUMBER_COL}$1"   # for use inside formulas (absolute)
MONTH_NUMBER_ADDR = f"{MONTH_NUMBER_COL}1"    # for direct cell writes
MONTH_ARRAY = '{"' + '","'.join(MONTHS) + '"}'

TYPE_GROUPS = [
    ("INCOME", FINANCE_GREEN, ["Salary / Wages", "Freelance", "Side hustle", "Bonus", "Other income"]),
    ("BILLS", DUSTY_BLUE, ["Rent / Mortgage", "Electricity", "Gas / Water", "Internet", "Phone",
                            "Insurance", "Subscriptions", "Council Tax / Property Tax", "Childcare",
                            "Streaming Services", "Home Maintenance", "Membership Fees"]),
    ("EXPENSES", MUTED_TAN, ["Groceries", "Dining out", "Transport", "Health", "Clothing",
                              "Entertainment", "Personal care", "Gifts", "Miscellaneous"]),
    ("SAVINGS", FINANCE_GREEN, ["Emergency fund", "Holiday", "House deposit", "Retirement",
                                 "Other savings"]),
    ("DEBT PAYMENTS", DEEP_ROSE, ["Credit card", "Student loan", "Personal loan", "Car finance"]),
]

# SETTINGS row numbers for each group's categories (see build/NOTES.md cell map).
SETTINGS_ROWS = {
    "INCOME": list(range(15, 20)),
    "BILLS": list(range(21, 33)),
    "EXPENSES": list(range(34, 43)),
    "SAVINGS": list(range(44, 49)),
    "DEBT PAYMENTS": list(range(50, 54)),
}


def choose_range(month_tab_col):
    parts = [f"{m}!${month_tab_col}${FIRST_DATA_ROW}:${month_tab_col}${LAST_DATA_ROW}" for m in MONTHS]
    return f"CHOOSE({MONTH_NUMBER_CELL}," + ",".join(parts) + ")"


def recreate_sheet(sheets):
    """Safe to delete+recreate DASHBOARD for now since nothing else
    references it (ANNUAL OVERVIEW/GOALS reference SETTINGS and the month
    tabs directly, not DASHBOARD). If that ever changes, switch to the
    create-only-if-missing pattern used in settings_tab.py/month_tabs.py --
    a delete+recreate breaks cross-sheet formula references elsewhere even
    when the sheetId/title are reused identically. See build/NOTES.md."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    exists = any(s["properties"]["sheetId"] == SHEET_ID for s in meta["sheets"])

    requests = [{"addSheet": {"properties": {"sheetId": 999998, "title": "__temp2__"}}}]
    if exists:
        requests.append({"deleteSheet": {"sheetId": SHEET_ID}})
    requests.append({
        "addSheet": {
            "properties": {
                "sheetId": SHEET_ID,
                "title": "DASHBOARD",
                "index": 1,  # right after SETTINGS, before the month tabs
                "gridProperties": {"rowCount": 85, "columnCount": 26, "hideGridlines": True,
                                    "frozenRowCount": 1},
                "tabColor": FINANCE_GREEN,
            }
        }
    })
    requests.append({"deleteSheet": {"sheetId": 999998}})
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def build_requests():
    requests = []

    requests.append(repeat_cell(
        {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 65, "startColumnIndex": 0, "endColumnIndex": 20},
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
    ))

    widths = {0: 28}
    for i in range(1, 13):
        widths[i] = 95
    widths[13] = 30
    widths[14] = 30
    for i in range(15, 20):
        widths[i] = 90
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: title + month selector + days-left pill.
    title_range = grid_range(0, 1, 0, 5)
    selector_range = grid_range(0, 1, 5, 6)   # single cell G1, not merged
    pill_range = grid_range(0, 1, 8, 12)
    requests.append(merge(title_range))
    requests.append(merge(pill_range))
    requests.append(repeat_cell(
        title_range, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=18, bold=True, align="LEFT"),
    ))
    requests.append(repeat_cell(
        selector_range, cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=11, bold=True,
                                     align="CENTER"),
    ))
    requests.append(repeat_cell(
        pill_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=11, bold=True, align="CENTER"),
    ))
    requests.append(border_request(pill_range, "left", HOT_PINK, width=3))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 44},
            "fields": "pixelSize",
        }
    })

    # Row 2: instruction note.
    note_range = grid_range(1, 2, 0, 12)
    requests.append(merge(note_range))
    requests.append(repeat_cell(
        note_range, cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True, wrap=True),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 28},
            "fields": "pixelSize",
        }
    })

    # Headline cards (rows 4-6): Left to spend (hero, deep rose) / Total income / Total spent.
    headline_spans = [(0, 4), (4, 8), (8, 12)]
    for idx, (start, end) in enumerate(headline_spans):
        is_hero = idx == 0
        label_r = grid_range(3, 4, start, end)
        value_r = grid_range(4, 5, start, end)
        sub_r = grid_range(5, 6, start, end)
        requests.append(merge(label_r))
        requests.append(merge(value_r))
        requests.append(merge(sub_r))
        bg = DEEP_ROSE if is_hero else PALE_NEUTRAL
        fg = WHITE if is_hero else NEAR_BLACK
        requests.append(repeat_cell(label_r, cell_format(bg=bg, fg=fg, font=CALIBRI, size=10, bold=True)))
        requests.append(repeat_cell(value_r, cell_format(bg=bg, fg=fg, font=ARIAL_BLACK, size=22, bold=True)))
        requests.append(repeat_cell(sub_r, cell_format(bg=bg, fg=fg, font=CALIBRI, size=9, italic=True)))
        if is_hero:
            requests.append(border_request(grid_range(3, 6, start, end), "left", HOT_PINK, width=4))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 4, "endIndex": 5},
            "properties": {"pixelSize": 34},
            "fields": "pixelSize",
        }
    })

    # Breakdown cards (rows 8-10): Bills / Expenses / Savings / Debt.
    breakdown_spans = [(0, 3), (3, 6), (6, 9), (9, 12)]
    breakdown_colors = [DUSTY_BLUE, MUTED_TAN, FINANCE_GREEN, DEEP_ROSE]
    for (start, end), color in zip(breakdown_spans, breakdown_colors):
        label_r = grid_range(7, 8, start, end)
        value_r = grid_range(8, 9, start, end)
        sub_r = grid_range(9, 10, start, end)
        requests.append(merge(label_r))
        requests.append(merge(value_r))
        requests.append(merge(sub_r))
        requests.append(repeat_cell(label_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                           bold=True)))
        requests.append(repeat_cell(value_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=ARIAL_BLACK, size=15,
                                                           bold=True)))
        requests.append(repeat_cell(sub_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8,
                                                         italic=True)))
        requests.append(border_request(grid_range(7, 10, start, end), "top", color, width=4))

    def section_band(row_idx, bg=FINANCE_GREEN, span_cols=12):
        r = grid_range(row_idx, row_idx + 1, 0, span_cols)
        requests.append(merge(r))
        requests.append(repeat_cell(r, cell_format(bg=bg, fg=WHITE, font=ARIAL_BLACK, size=12, bold=True)))

    def maybe_merge(rng):
        if rng["endColumnIndex"] - rng["startColumnIndex"] > 1:
            requests.append(merge(rng))

    # Row 12 (idx 11): UPCOMING BILLS band.
    section_band(11, bg=DUSTY_BLUE)
    ub_cat = grid_range(12, 13, 0, 4)
    ub_amt = grid_range(12, 13, 4, 8)
    ub_due = grid_range(12, 13, 8, 12)
    for r in (ub_cat, ub_amt, ub_due):
        requests.append(merge(r))
        requests.append(repeat_cell(r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True)))
    for i in range(N_HELPER_BILLS):
        row_idx = 13 + i
        band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
        r_cat = grid_range(row_idx, row_idx + 1, 0, 4)
        r_amt = grid_range(row_idx, row_idx + 1, 4, 8)
        r_due = grid_range(row_idx, row_idx + 1, 8, 12)
        requests.append(merge(r_cat))
        requests.append(merge(r_amt))
        requests.append(merge(r_due))
        requests.append(repeat_cell(r_cat, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10)))
        requests.append(repeat_cell(r_amt, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                                                         number_format={"type": "NUMBER", "pattern": "#,##0.00"})))
        requests.append(repeat_cell(r_due, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT")))

    # MONTHLY BUDGET band -- narrowed to B:H (7 cols) so I:M is free for the
    # charts, which sit alongside the table rather than below everything.
    # Row position is computed, not hardcoded: it must sit right after the
    # Upcoming Bills block, whose height depends on N_HELPER_BILLS (grew
    # from 7 to 12 when Bills categories did -- a hardcoded "21" here would
    # have silently overlapped the expanded Upcoming Bills rows).
    BUDGET_TABLE_WIDTH = 7
    section_band(BUDGET_BAND_IDX, span_cols=BUDGET_TABLE_WIDTH)
    for span in (CAT_SPAN, TARGET_SPAN, ACTUAL_SPAN, DIFF_SPAN, PROG_SPAN):
        r = grid_range(BUDGET_HEADER_IDX, BUDGET_HEADER_IDX + 1, *span)
        maybe_merge(r)
        requests.append(repeat_cell(r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True)))

    row_cursor = FIRST_DIVIDER_IDX
    for group_name, color, categories in TYPE_GROUPS:
        divider_r = grid_range(row_cursor, row_cursor + 1, 0, BUDGET_TABLE_WIDTH)
        requests.append(merge(divider_r))
        requests.append(repeat_cell(divider_r, cell_format(bg=color, fg=WHITE, font=CALIBRI, size=10, bold=True)))
        row_cursor += 1
        for i, _cat in enumerate(categories):
            r = row_cursor + i
            band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
            cat_r = grid_range(r, r + 1, *CAT_SPAN)
            tgt_r = grid_range(r, r + 1, *TARGET_SPAN)
            act_r = grid_range(r, r + 1, *ACTUAL_SPAN)
            dif_r = grid_range(r, r + 1, *DIFF_SPAN)
            pro_r = grid_range(r, r + 1, *PROG_SPAN)
            for rr in (cat_r, tgt_r, act_r, dif_r, pro_r):
                maybe_merge(rr)
            requests.append(repeat_cell(cat_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10)))
            for rr in (tgt_r, act_r, dif_r):
                requests.append(repeat_cell(rr, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                              align="RIGHT",
                                                              number_format={"type": "NUMBER", "pattern": "#,##0.00"})))
            requests.append(repeat_cell(pro_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                             align="CENTER")))
        row_cursor += len(categories)

    total_row_idx = row_cursor + 1  # idx 59 -> row 60, after a spacer at idx 58 -> row 59
    for span in (CAT_SPAN, TARGET_SPAN, ACTUAL_SPAN, DIFF_SPAN, PROG_SPAN):
        r = grid_range(total_row_idx, total_row_idx + 1, *span)
        maybe_merge(r)
        requests.append(repeat_cell(r, cell_format(bg=ROSE_PALE_TINT, fg=DEEP_ROSE, font=CALIBRI, size=10, bold=True,
                                                     align="RIGHT" if span != CAT_SPAN else "LEFT")))

    # Helper cells (P, Q:T) -- visible but de-emphasised, with explanatory notes.
    helper_note_targets = {
        f"{MONTH_NUMBER_COL}1": "Internal helper: numeric index (1-12) of the selected month, "
                                  "used by CHOOSE() formulas across this tab. Please don't delete.",
        f"{BILLS_CAT_COL}1": "Internal helper table (rows 1-7): Bills categories, due days, "
                              "whether paid this month, and a sort key -- feeds the Upcoming "
                              "Bills block above. Please don't delete.",
        f"{CHART_DATA_COL}1": "Internal helper table (rows 1-4): spending-by-group totals for "
                               "the selected month, feeding the donut chart below. Please don't delete.",
    }
    for a1, note in helper_note_targets.items():
        requests.append({
            "updateCells": {
                "range": a1_to_grid_range(a1),
                "rows": [{"values": [{"note": note}]}],
                "fields": "note",
            }
        })
    helper_range = grid_range(0, N_HELPER_BILLS, 14, 19)
    requests.append(repeat_cell(
        helper_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8),
    ))
    chart_data_range = grid_range(0, 4, 19, 21)
    requests.append(repeat_cell(
        chart_data_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8),
    ))
    requests.append({
        "updateCells": {
            "range": a1_to_grid_range(f"{BAR_CAT_COL}1"),
            "rows": [{"values": [{"note": "Internal helper table (rows 1-25): a gap-free mirror "
                                           "of the 4 spending groups' Category/Target/Actual cells "
                                           "in the budget table above, used as the bar chart's data "
                                           "source (the Sheets API requires chart source ranges to "
                                           "be contiguous, and the real table has divider rows "
                                           "breaking each group up). Please don't delete."}]}],
            "fields": "note",
        }
    })
    bar_data_range = grid_range(0, BAR_CHART_ROWS, 21, 24)
    requests.append(repeat_cell(
        bar_data_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8),
    ))

    layout = {"total_row_idx": total_row_idx, "budget_band_idx": BUDGET_BAND_IDX}
    return requests, layout


def conditional_formats():
    """Progress-column colour coding, per category row. <80% used: Finance
    green (no explicit rule needed, that's the base state). 80-99%: Rose
    pale tint. >=100%: Deep rose solid (hot pink is border/line-accent only
    in v2's confirmed palette, so it cannot be used as the over-budget fill)."""
    requests = []
    row_cursor = FIRST_DIVIDER_IDX
    for group_name, _color, categories in TYPE_GROUPS:
        row_cursor += 1
        for i in range(len(categories)):
            r = row_cursor + i
            pro_range = grid_range(r, r + 1, *PROG_SPAN)
            act_col = L(ACTUAL_SPAN[0])
            tgt_col = L(TARGET_SPAN[0])
            ratio = f'IFERROR({act_col}{r + 1}/{tgt_col}{r + 1},0)'
            requests.append({
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [pro_range],
                        "booleanRule": {
                            "condition": {"type": "CUSTOM_FORMULA",
                                           "values": [{"userEnteredValue": f'={ratio}>=1'}]},
                            "format": {"backgroundColor": DEEP_ROSE,
                                       "textFormat": {"foregroundColor": WHITE, "bold": True}},
                        },
                    },
                    "index": 0,
                }
            })
            requests.append({
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [pro_range],
                        "booleanRule": {
                            "condition": {"type": "CUSTOM_FORMULA",
                                           "values": [{"userEnteredValue": f'=AND({ratio}>=0.8,{ratio}<1)'}]},
                            "format": {"backgroundColor": ROSE_PALE_TINT,
                                       "textFormat": {"foregroundColor": DEEP_ROSE, "bold": True}},
                        },
                    },
                    "index": 1,
                }
            })
        row_cursor += len(categories)
    return requests


def data_validations():
    return [{
        "setDataValidation": {
            "range": grid_range(0, 1, 5, 6),
            "rule": {
                "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": m} for m in MONTHS]},
                "showCustomUi": True,
                "strict": True,
            },
        }
    }]


def compute_group_row_ranges():
    """1-based (first, last) category-data-row range per group in the budget
    table, e.g. INCOME -> (30, 34). Deterministic from TYPE_GROUPS' fixed
    category counts, so both build_values() and build_charts() can share it
    without build_values() needing to run first."""
    row_cursor = FIRST_DIVIDER_IDX
    ranges = {}
    for group_name, _color, categories in TYPE_GROUPS:
        row_cursor += 1  # divider row
        first = row_cursor + 1
        last = row_cursor + len(categories)
        ranges[group_name] = (first, last)
        row_cursor += len(categories)
    return ranges


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"DASHBOARD!{a1}", "values": [[v]]})

    month_selector_cell = f"{L(5)}1"  # G1

    # Personalised title (the whole point of SETTINGS' "Your name" field):
    # falls back to a generic title if the name hasn't been filled in yet.
    cell(f"{L(0)}1", '=IF(SETTINGS!$D$5="","MONTHLY BUDGET TRACKER",'
                     'CONCATENATE(SETTINGS!$D$5,"\'s Budget"))')
    cell(month_selector_cell, "Jan")
    cell(MONTH_NUMBER_ADDR, f'=MATCH({month_selector_cell},{MONTH_ARRAY},0)')
    cell(f"{L(8)}1", '=CONCATENATE(TEXT(EOMONTH(TODAY(),0)-TODAY(),"0")," days left in ",TEXT(TODAY(),"mmmm"))')

    cell(f"{L(0)}2",
         "Actuals update automatically. To log a transaction, go to the tab for the selected "
         "month and enter it in the next empty row.")

    cell(f"{L(0)}12", "UPCOMING BILLS")
    cell(f"{L(0)}13", "Category")
    cell(f"{L(4)}13", '=CONCATENATE("Amount (",SETTINGS!$D$7,")")')
    cell(f"{L(8)}13", "Due day")

    cell(f"{L(0)}{BUDGET_BAND_IDX + 1}", "MONTHLY BUDGET")

    # Budget table: category rows first (headline/breakdown cards reference the group ranges below).
    row_cursor = FIRST_DIVIDER_IDX
    amount_choose = choose_range(MONTH_COL_AMOUNT)
    category_choose = choose_range(MONTH_COL_CATEGORY)
    cat_col = L(CAT_SPAN[0])
    tgt_col = L(TARGET_SPAN[0])
    act_col = L(ACTUAL_SPAN[0])
    dif_col = L(DIFF_SPAN[0])
    pro_col = L(PROG_SPAN[0])

    cell(f"{cat_col}23", "Category")
    cell(f"{tgt_col}23", '=CONCATENATE("Budget (",SETTINGS!$D$7,")")')
    cell(f"{act_col}23", "Actual")
    cell(f"{dif_col}23", "Diff.")
    cell(f"{pro_col}23", "Progress")

    for group_name, _color, categories in TYPE_GROUPS:
        cell(f"{cat_col}{row_cursor + 1}", group_name)
        row_cursor += 1
        settings_rows = SETTINGS_ROWS[group_name]
        for i, _catname in enumerate(categories):
            r1 = row_cursor + i + 1  # 1-based
            settings_row = settings_rows[i]
            cell(f"{cat_col}{r1}", f"=SETTINGS!$B${settings_row}")
            cell(f"{tgt_col}{r1}", f"=SETTINGS!$D${settings_row}")
            cell(f"{act_col}{r1}", f'=SUMIFS({amount_choose},{category_choose},{cat_col}{r1})')
            cell(f"{dif_col}{r1}", f"={tgt_col}{r1}-{act_col}{r1}")
            cell(f"{pro_col}{r1}",
                 f'=IFERROR(SPARKLINE(MIN({act_col}{r1}/{tgt_col}{r1},1),'
                 f'{{"charttype","bar";"max",1;"color1","#3D7A5A"}}),"")')
        row_cursor += len(categories)
    group_row_ranges = compute_group_row_ranges()

    def group_sum(col, group_name):
        first, last = group_row_ranges[group_name]
        return f"SUM({col}{first}:{col}{last})"

    income_target = group_sum(tgt_col, "INCOME")
    income_actual = group_sum(act_col, "INCOME")
    spend_groups = ["BILLS", "EXPENSES", "SAVINGS", "DEBT PAYMENTS"]
    spend_target = "+".join(group_sum(tgt_col, g) for g in spend_groups)
    spend_actual = "+".join(group_sum(act_col, g) for g in spend_groups)

    # Headline cards.
    cell(f"{L(0)}4", "LEFT TO SPEND")
    cell(f"{L(0)}5", f'=CONCATENATE(SETTINGS!$D$7,TEXT(({spend_target})-({spend_actual}),"#,##0.00"))')
    cell(f"{L(0)}6", f'=CONCATENATE("of ",SETTINGS!$D$7,TEXT({spend_target},"#,##0.00")," budgeted")')

    cell(f"{L(4)}4", "TOTAL INCOME")
    cell(f"{L(4)}5", f'=CONCATENATE(SETTINGS!$D$7,TEXT({income_actual},"#,##0.00"))')
    cell(f"{L(4)}6", f'=CONCATENATE("of ",SETTINGS!$D$7,TEXT({income_target},"#,##0.00")," budgeted")')

    cell(f"{L(8)}4", "TOTAL SPENT")
    cell(f"{L(8)}5", f'=CONCATENATE(SETTINGS!$D$7,TEXT({spend_actual},"#,##0.00"))')
    cell(f"{L(8)}6", f'=CONCATENATE("of ",SETTINGS!$D$7,TEXT({spend_target},"#,##0.00")," budgeted")')

    # Breakdown cards.
    breakdown_specs = [(0, "BILLS", "Bills"), (3, "EXPENSES", "Expenses"),
                        (6, "SAVINGS", "Savings"), (9, "DEBT PAYMENTS", "Debt")]
    for start, group_name, label in breakdown_specs:
        tgt = group_sum(tgt_col, group_name)
        act = group_sum(act_col, group_name)
        cell(f"{L(start)}8", label.upper())
        cell(f"{L(start)}9", f'=CONCATENATE(SETTINGS!$D$7,TEXT(({tgt})-({act}),"#,##0.00"))')
        cell(f"{L(start)}10", f'=CONCATENATE("of ",SETTINGS!$D$7,TEXT({tgt},"#,##0.00")," budgeted")')

    # Donut-chart data table (U:V, rows 1-4): spending-by-group actual totals.
    for i, (_start, group_name, label) in enumerate(breakdown_specs):
        r = i + 1
        cell(f"{CHART_DATA_COL}{r}", label)
        cell(f"{CHART_DATA_VALUE_COL}{r}", f"={group_sum(act_col, group_name)}")

    # Bar-chart data table (W:Y, rows 1-25): gap-free mirror of the 4 spending
    # groups' Category/Target/Actual cells (see note on W1 for why).
    bar_row = 1
    for group_name in ["BILLS", "EXPENSES", "SAVINGS", "DEBT PAYMENTS"]:
        first, last = group_row_ranges[group_name]
        for src_row in range(first, last + 1):
            cell(f"{BAR_CAT_COL}{bar_row}", f"={cat_col}{src_row}")
            cell(f"{BAR_TGT_COL}{bar_row}", f"={tgt_col}{src_row}")
            cell(f"{BAR_ACT_COL}{bar_row}", f"={act_col}{src_row}")
            bar_row += 1

    # Upcoming Bills helper table (Q:T, rows 1-7) and display rows (14-20).
    bills_settings_rows = SETTINGS_ROWS["BILLS"]
    type_choose = choose_range(MONTH_COL_TYPE)
    for i, settings_row in enumerate(bills_settings_rows):
        r = i + 1
        cell(f"{BILLS_CAT_COL}{r}", f"=SETTINGS!$B${settings_row}")
        cell(f"{BILLS_DUE_COL}{r}", f"=SETTINGS!$E${settings_row}")
        paid_formula = (f'=COUNTIFS({type_choose},"Bill",{category_choose},{BILLS_CAT_COL}{r})>0')
        cell(f"{BILLS_PAID_COL}{r}", paid_formula)
        cell(f"{BILLS_RANK_COL}{r}",
             f'=IF({BILLS_PAID_COL}{r},9999+{i}*0.0001,{BILLS_DUE_COL}{r}+{i}*0.0001)')

    rank_range = f"${BILLS_RANK_COL}$1:${BILLS_RANK_COL}${N_HELPER_BILLS}"
    cat_range = f"${BILLS_CAT_COL}$1:${BILLS_CAT_COL}${N_HELPER_BILLS}"
    due_range = f"${BILLS_DUE_COL}$1:${BILLS_DUE_COL}${N_HELPER_BILLS}"
    settings_target_range = "SETTINGS!$D$21:$D$32"

    for n in range(1, N_HELPER_BILLS + 1):
        r = 13 + n  # display row (14-20)
        small_expr = f"SMALL({rank_range},{n})"
        pos_expr = f"MATCH({small_expr},{rank_range},0)"
        no_more = f"{small_expr}>=9999"
        cell(f"{cat_col}{r}", f'=IF({no_more},"",INDEX({cat_range},{pos_expr}))')
        cell(f"{L(4)}{r}", f'=IF({no_more},"",INDEX({settings_target_range},{pos_expr}))')
        cell(f"{L(8)}{r}", f'=IF({no_more},"",INDEX({due_range},{pos_expr}))')

    # Total row.
    total_row = layout["total_row_idx"] + 1
    all_groups = ["INCOME", "BILLS", "EXPENSES", "SAVINGS", "DEBT PAYMENTS"]
    cell(f"{cat_col}{total_row}", "TOTAL")
    cell(f"{tgt_col}{total_row}", "=" + "+".join(group_sum(tgt_col, g) for g in all_groups))
    cell(f"{act_col}{total_row}", "=" + "+".join(group_sum(act_col, g) for g in all_groups))
    cell(f"{dif_col}{total_row}", f"={tgt_col}{total_row}-{act_col}{total_row}")

    return values


def _gr(start_row, end_row, start_col, end_col):
    """Raw (non-padding-adjusted) GridRange, for chart sources that need to
    reference already-known absolute column indices directly."""
    return {"sheetId": SHEET_ID, "startRowIndex": start_row, "endRowIndex": end_row,
            "startColumnIndex": start_col, "endColumnIndex": end_col}


def build_charts(layout):
    """Donut (spending breakdown by group) + horizontal bar (budget vs actual
    per category) charts, per v1 Tab 2 / v2 Section 6. Both sit in columns
    I:M, stacked vertically, alongside the narrowed (B:H) budget table rather
    than below everything. The bar chart reads from the gap-free W:Y helper
    block (see build/NOTES.md) since the Sheets API rejects multi-range
    chart sources unless each range is contiguous, and the real budget table
    has divider rows breaking every group up.

    Colour caveat: PieChartSpec has no field for custom per-slice colours in
    the Sheets API (confirmed -- legendPosition/domain/series/
    threeDimensional/pieHole are the only fields; there's no colours array),
    so the donut's slice colours are Sheets' own default palette, not the
    confirmed brand palette. The bar chart's two series *do* support custom
    colours and are set to Pale neutral (budget) / Finance green (actual).
    """
    bar_cat_col_idx = 21 + PAD
    bar_tgt_col_idx = 22 + PAD
    bar_act_col_idx = 23 + PAD
    cat_sources = [_gr(0, BAR_CHART_ROWS, bar_cat_col_idx, bar_cat_col_idx + 1)]
    tgt_sources = [_gr(0, BAR_CHART_ROWS, bar_tgt_col_idx, bar_tgt_col_idx + 1)]
    act_sources = [_gr(0, BAR_CHART_ROWS, bar_act_col_idx, bar_act_col_idx + 1)]

    chart_col_idx = PROG_SPAN[1] + PAD  # column I, right after the narrowed budget table (B:H)
    donut_row = layout["budget_band_idx"]       # same row as the MONTHLY BUDGET band
    bar_row = layout["budget_band_idx"] + 15    # ~15 rows below the donut

    donut_chart = {
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Spending breakdown",
                    "pieChart": {
                        "legendPosition": "RIGHT_LEGEND",
                        "domain": {"sourceRange": {"sources": [
                            _gr(0, 4, CHART_DATA_COL_IDX, CHART_DATA_COL_IDX + 1)
                        ]}},
                        "series": {"sourceRange": {"sources": [
                            _gr(0, 4, CHART_DATA_COL_IDX + 1, CHART_DATA_COL_IDX + 2)
                        ]}},
                        "pieHole": 0.5,
                    },
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": SHEET_ID, "rowIndex": donut_row, "columnIndex": chart_col_idx},
                        "widthPixels": 470,
                        "heightPixels": 320,
                    }
                },
            }
        }
    }

    bar_chart = {
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Budget vs actual",
                    "basicChart": {
                        "chartType": "BAR",
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [{"position": "LEFT_AXIS"}, {"position": "BOTTOM_AXIS"}],
                        "domains": [{"domain": {"sourceRange": {"sources": cat_sources}}}],
                        "series": [
                            {"series": {"sourceRange": {"sources": tgt_sources}},
                             "targetAxis": "BOTTOM_AXIS", "colorStyle": {"rgbColor": PALE_NEUTRAL}},
                            {"series": {"sourceRange": {"sources": act_sources}},
                             "targetAxis": "BOTTOM_AXIS", "colorStyle": {"rgbColor": FINANCE_GREEN}},
                        ],
                    },
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": SHEET_ID, "rowIndex": bar_row, "columnIndex": chart_col_idx},
                        "widthPixels": 470,
                        # Tall relative to 25 categories so each bar reads as
                        # thick and legible -- the Charts API has no direct
                        # bar-thickness/gap-width field, so more vertical
                        # room per category is the only lever available.
                        "heightPixels": 700,
                    }
                },
            }
        }
    }

    return [donut_chart, bar_chart]


def a1_to_grid_range(a1):
    import re
    m = re.match(r"([A-Z]+)(\d+)", a1)
    col_letters, row_num = m.group(1), int(m.group(2))
    col = 0
    for ch in col_letters:
        col = col * 26 + (ord(ch) - ord("A") + 1)
    col -= 1
    row = row_num - 1
    return {"sheetId": SHEET_ID, "startRowIndex": row, "endRowIndex": row + 1,
            "startColumnIndex": col, "endColumnIndex": col + 1}


def main():
    sheets, _drive = get_services()

    recreate_sheet(sheets)

    requests, layout = build_requests()
    requests.extend(conditional_formats())
    requests.extend(data_validations())

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

    chart_requests = build_charts(layout)
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": chart_requests}
    ).execute()

    print("DASHBOARD built. Layout:", layout)


if __name__ == "__main__":
    main()
