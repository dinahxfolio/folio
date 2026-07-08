"""Build the ANNUAL OVERVIEW tab.

Per v1 Tab 4 + v2 Section 7 ("formula logic needs rewriting to sum SUMIFS
across each of the 12 month tabs directly -- additive, not INDIRECT-based").
Visual layout wasn't mocked up in either brief, so v1's layout carries over
with v2's palette substituted in (see NOTES.md for the amber/red remapping,
same pattern as DASHBOARD).

Column scheme (padding convention applies, A blank): B = row label,
C:N = Jan..Dec (12 columns, one each), O = Total. 14 content columns total.

Row plan (1-based):
  1     Header band: "ANNUAL OVERVIEW -- <year>"
  2     Instruction note
  4-6   Best month / Tightest month callout cards
  8     Grid header row (Jan..Dec, Total)
  9-13  Income / Bills / Expenses / Savings / Debt payments
  14    Spacer row (Finance tint background, per v1)
  15    Left over
  16    Savings rate %
  19    Bar chart (monthly left over)
"""
from auth import get_services
from month_tabs import COL_AMOUNT as MONTH_COL_AMOUNT, COL_TYPE as MONTH_COL_TYPE, \
    FIRST_DATA_ROW, LAST_DATA_ROW, MONTHS
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
    lighten,
)

SHEET_ID = 400
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


LABEL_COL = 0        # B
MONTH_COLS = list(range(1, 13))  # C..N (logical 1-12)
TOTAL_COL = 13        # O

GRID_ROWS = {
    "INCOME": 8, "BILLS": 9, "EXPENSES": 10, "SAVINGS": 11, "DEBT PAYMENTS": 12,
    # 13 = spacer
    "LEFT_OVER": 14, "SAVINGS_RATE": 15,
}  # 0-indexed

TYPE_MAP = {"INCOME": "Income", "BILLS": "Bill", "EXPENSES": "Expense",
            "SAVINGS": "Saving", "DEBT PAYMENTS": "Debt"}

# Positive/negative helper columns for the bar chart (per-series colouring
# workaround -- BasicChart series colour is per-series, not per-point, so a
# "green if positive / rose if negative" bar chart needs two series, each
# only populated where applicable).
POS_COL = 16   # Q
NEG_COL = 17   # R
THRESHOLD_COL = 18  # S -- local mirror of SETTINGS!D9; conditional format
                     # CUSTOM_FORMULA conditions cannot reference another
                     # sheet at all (confirmed empirically -- the API
                     # rejects it outright), so the threshold has to be
                     # copied onto this sheet first.
CHART_MONTH_COL = 19  # T -- vertical (12-row) copy of the month names, since
                       # a chart's domain and series must share the same
                       # row/column orientation, and the grid header (row 8)
                       # is horizontal while POS_COL/NEG_COL are vertical.


def has_data_expr(month):
    return f'COUNTA({month}!${MONTH_COL_TYPE}${FIRST_DATA_ROW}:${MONTH_COL_TYPE}${LAST_DATA_ROW})>0'


def month_type_sum(month, type_value):
    return (f'SUMIFS({month}!${MONTH_COL_AMOUNT}${FIRST_DATA_ROW}:${MONTH_COL_AMOUNT}${LAST_DATA_ROW},'
            f'{month}!${MONTH_COL_TYPE}${FIRST_DATA_ROW}:${MONTH_COL_TYPE}${LAST_DATA_ROW},"{type_value}")')


def recreate_sheet(sheets):
    """Create-only-if-missing -- see build/NOTES.md on why delete+recreate
    breaks cross-sheet formula references once other tabs exist. Nothing
    references ANNUAL OVERVIEW yet, but staying consistent with the safe
    pattern now that it's the default going forward."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    exists = any(s["properties"]["sheetId"] == SHEET_ID for s in meta["sheets"])
    if exists:
        return

    requests = [{"addSheet": {"properties": {"sheetId": 999997, "title": "__temp3__"}}}]
    requests.append({
        "addSheet": {
            "properties": {
                "sheetId": SHEET_ID,
                "title": "ANNUAL OVERVIEW",
                "index": 14,  # after Dec
                "gridProperties": {"rowCount": 40, "columnCount": 23, "hideGridlines": True,
                                    "frozenRowCount": 1},
                "tabColor": FINANCE_GREEN,
            }
        }
    })
    requests.append({"deleteSheet": {"sheetId": 999997}})
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def build_requests():
    requests = []

    requests.append(repeat_cell(
        {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 40, "startColumnIndex": 0, "endColumnIndex": 20},
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
    ))

    widths = {0: 28, 1: 130}
    for i in range(2, 15):
        widths[i] = 78
    for i in range(15, 20):
        widths[i] = 70
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: header band.
    header_r = grid_range(0, 1, LABEL_COL, TOTAL_COL + 1)
    requests.append(merge(header_r))
    requests.append(repeat_cell(header_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=18,
                                                        bold=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 44},
            "fields": "pixelSize",
        }
    })

    # Row 2: instruction note.
    note_r = grid_range(1, 2, LABEL_COL, TOTAL_COL + 1)
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

    # Rows 4-6: Best / Tightest month cards.
    for start, end in [(0, 7), (7, 14)]:
        label_r = grid_range(3, 4, start, end)
        value_r = grid_range(4, 5, start, end)
        sub_r = grid_range(5, 6, start, end)
        for r in (label_r, value_r, sub_r):
            requests.append(merge(r))
        requests.append(repeat_cell(label_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                           bold=True)))
        requests.append(repeat_cell(value_r, cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=ARIAL_BLACK,
                                                           size=16, bold=True)))
        requests.append(repeat_cell(sub_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                         italic=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 4, "endIndex": 5},
            "properties": {"pixelSize": 30},
            "fields": "pixelSize",
        }
    })

    # Row 8: grid header (Jan..Dec, Total), each its own cell.
    header_row_r = grid_range(7, 8, LABEL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(header_row_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=CALIBRI, size=10,
                                                            bold=True, align="CENTER")))
    # Current-month column gets a highlight across the whole grid (rows
    # 8-15) -- v1 used amber, which no longer exists in v2's palette.
    # First attempt was Pale neutral, which read as too washed-out/hard to
    # tell apart from the row banding (Minnie's feedback). Switched to the
    # same light Finance-green tint used for the Left over row/Total column
    # (lighten(FINANCE_GREEN, 0.15)) for stronger, more legible contrast.
    # A hot-pink border was considered instead, but conditional formatting
    # can't set borders at all (only fill/text) -- a border tied to
    # TODAY()'s month would need to be static and manually moved every
    # month, defeating the point of an automatic highlight.
    # Split into a header-row rule and a data-rows rule: the header row's
    # static text is white (for contrast against the green header band),
    # which goes unreadable once the same light-green tint lands under it,
    # so that one cell also needs its text switched to Finance green.
    # The data rows (9-16) stay background-only -- adding a text-colour
    # override there too would compete with the negative-value rule (Deep
    # rose text), and Sheets only applies the first matching rule per cell.
    current_month_bg = lighten(FINANCE_GREEN, 0.15)
    for i, m in enumerate(MONTHS):
        col = 1 + i
        header_cond_range = grid_range(7, 8, col, col + 1)
        data_cond_range = grid_range(8, 16, col, col + 1)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [header_cond_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA",
                                       "values": [{"userEnteredValue": f'=MONTH(TODAY())={i + 1}'}]},
                        "format": {"backgroundColor": current_month_bg,
                                   "textFormat": {"foregroundColor": FINANCE_GREEN, "bold": True}},
                    },
                },
                "index": 0,
            }
        })
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [data_cond_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA",
                                       "values": [{"userEnteredValue": f'=MONTH(TODAY())={i + 1}'}]},
                        "format": {"backgroundColor": current_month_bg},
                    },
                },
                "index": 0,
            }
        })

    # Rows 9-13: type rows. Row 14: spacer. Rows 15-16: Left over / Savings rate.
    row_labels = [("INCOME", "Income"), ("BILLS", "Bills"), ("EXPENSES", "Expenses"),
                  ("SAVINGS", "Savings"), ("DEBT PAYMENTS", "Debt payments")]
    for i, (_key, _label) in enumerate(row_labels):
        r = 8 + i
        band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
        row_r = grid_range(r, r + 1, LABEL_COL, TOTAL_COL + 1)
        requests.append(repeat_cell(row_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                         align="RIGHT",
                                                         number_format={"type": "NUMBER", "pattern": "#,##0.00"})))
        requests.append(repeat_cell(grid_range(r, r + 1, LABEL_COL, LABEL_COL + 1),
                                     cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="LEFT")))

    spacer_r = grid_range(13, 14, LABEL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(spacer_r, cell_format(bg=lighten(FINANCE_GREEN, 0.15), fg=NEAR_BLACK,
                                                        font=CALIBRI, size=4)))

    left_over_r = grid_range(14, 15, LABEL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(left_over_r, cell_format(bg=lighten(FINANCE_GREEN, 0.15), fg=FINANCE_GREEN,
                                                           font=CALIBRI, size=10, bold=True, align="RIGHT",
                                                           number_format={"type": "NUMBER", "pattern": "#,##0.00"})))
    requests.append(repeat_cell(grid_range(14, 15, LABEL_COL, LABEL_COL + 1),
                                 cell_format(bg=lighten(FINANCE_GREEN, 0.15), fg=NEAR_BLACK, font=CALIBRI, size=10,
                                             bold=True, align="LEFT")))

    savings_rate_r = grid_range(15, 16, LABEL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(savings_rate_r, cell_format(bg=ROW_WHITE, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                              align="RIGHT",
                                                              number_format={"type": "PERCENT", "pattern": "0.0%"})))
    requests.append(repeat_cell(grid_range(15, 16, LABEL_COL, LABEL_COL + 1),
                                 cell_format(bg=ROW_WHITE, fg=NEAR_BLACK, font=CALIBRI, size=10, align="LEFT")))

    # Negative left-over / below-threshold savings rate -> Deep rose text
    # (v1 used "red"; v2's palette designates Deep rose for negative/caution
    # states throughout, e.g. Debt type, Overdue status, over-budget).
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range(14, 15, LABEL_COL + 1, TOTAL_COL + 1)],
                "booleanRule": {
                    "condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]},
                    "format": {"textFormat": {"foregroundColor": DEEP_ROSE, "bold": True}},
                },
            },
            "index": 0,
        }
    })
    threshold_cell = f"${L(THRESHOLD_COL)}$1"
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range(15, 16, LABEL_COL + 1, TOTAL_COL + 1)],
                "booleanRule": {
                    "condition": {"type": "CUSTOM_FORMULA",
                                   "values": [{"userEnteredValue":
                                               f'=AND(ISNUMBER({L(1)}16),{L(1)}16<{threshold_cell})'}]},
                    "format": {"backgroundColor": ROSE_PALE_TINT,
                               "textFormat": {"foregroundColor": DEEP_ROSE, "bold": True}},
                },
            },
            "index": 0,
        }
    })

    # Total column: light Finance-green tint background, Finance green text.
    # Split at the Savings rate row so its percent format isn't clobbered
    # by the currency format used for every other row in this column.
    total_col_amounts_r = grid_range(8, 15, TOTAL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(total_col_amounts_r, cell_format(bg=lighten(FINANCE_GREEN, 0.15), fg=FINANCE_GREEN,
                                                                   font=CALIBRI, size=10, bold=True, align="RIGHT",
                                                                   number_format={"type": "NUMBER",
                                                                                  "pattern": "#,##0.00"})))
    total_col_rate_r = grid_range(15, 16, TOTAL_COL, TOTAL_COL + 1)
    requests.append(repeat_cell(total_col_rate_r, cell_format(bg=lighten(FINANCE_GREEN, 0.15), fg=FINANCE_GREEN,
                                                                font=CALIBRI, size=10, bold=True, align="RIGHT",
                                                                number_format={"type": "PERCENT",
                                                                               "pattern": "0.0%"})))

    # Helper columns Q/R (positive/negative left-over, for the bar chart)
    # and S (local mirror of SETTINGS!D9, for the conditional format rule
    # above -- conditional format CUSTOM_FORMULA conditions cannot
    # reference another sheet at all).
    helper_range = grid_range(0, 12, POS_COL, CHART_MONTH_COL + 1)
    requests.append(repeat_cell(helper_range, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8)))
    requests.append({
        "updateCells": {
            "range": grid_range(0, 1, POS_COL, POS_COL + 1),
            "rows": [{"values": [{"note": "Internal helper table (rows 1-12): splits the Left "
                                           "over row into positive/negative columns so the bar "
                                           "chart can colour bars by sign (Sheets charts colour "
                                           "per series, not per bar). Please don't delete."}]}],
            "fields": "note",
        }
    })
    requests.append({
        "updateCells": {
            "range": grid_range(0, 1, THRESHOLD_COL, THRESHOLD_COL + 1),
            "rows": [{"values": [{"note": "Internal helper: mirrors SETTINGS!D9 (savings rate "
                                           "threshold) so the Savings rate row's conditional "
                                           "formatting can compare against it -- conditional "
                                           "format formulas can't reference another sheet at all. "
                                           "Please don't delete."}]}],
            "fields": "note",
        }
    })

    layout = {}
    return requests, layout


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"'ANNUAL OVERVIEW'!{a1}", "values": [[v]]})

    year_col = L(LABEL_COL)
    cell(f"{year_col}1", '=CONCATENATE("ANNUAL OVERVIEW -- ",SETTINGS!$D$6)')
    cell(f"{year_col}2", "Read only. Updates automatically from your transactions.")

    # Grid header row.
    cell(f"{year_col}8", "")
    for i, m in enumerate(MONTHS):
        cell(f"{L(1 + i)}8", m)
    cell(f"{L(TOTAL_COL)}8", "Total")

    row_labels = [("INCOME", "Income"), ("BILLS", "Bills"), ("EXPENSES", "Expenses"),
                  ("SAVINGS", "Savings"), ("DEBT PAYMENTS", "Debt payments")]
    for i, (key, label) in enumerate(row_labels):
        r = 9 + i  # 1-based
        cell(f"{year_col}{r}", label)
        type_value = TYPE_MAP[key]
        for j, m in enumerate(MONTHS):
            col = L(1 + j)
            formula = f'=IF({has_data_expr(m)},{month_type_sum(m, type_value)},"--")'
            cell(f"{col}{r}", formula)
        total_col = L(TOTAL_COL)
        cell(f"{total_col}{r}", f"=SUM({L(1)}{r}:{L(12)}{r})")

    # Left over (row 15) and Savings rate (row 16).
    income_row = 9
    bills_row, expenses_row, savings_row, debt_row = 10, 11, 12, 13
    left_over_row = 15
    savings_rate_row = 16
    cell(f"{year_col}{left_over_row}", "Left over")
    cell(f"{year_col}{savings_rate_row}", "Savings rate %")
    for j, m in enumerate(MONTHS):
        col = L(1 + j)
        lo_formula = (f'=IF({has_data_expr(m)},{col}{income_row}-{col}{bills_row}-{col}{expenses_row}'
                      f'-{col}{savings_row}-{col}{debt_row},"--")')
        cell(f"{col}{left_over_row}", lo_formula)
        sr_formula = f'=IF({has_data_expr(m)},IFERROR({col}{savings_row}/{col}{income_row},0),"--")'
        cell(f"{col}{savings_rate_row}", sr_formula)
    cell(f"{L(TOTAL_COL)}{left_over_row}", f"=SUM({L(1)}{left_over_row}:{L(12)}{left_over_row})")
    cell(f"{L(TOTAL_COL)}{savings_rate_row}",
         f"=IFERROR({L(TOTAL_COL)}{savings_row}/{L(TOTAL_COL)}{income_row},0)")

    # Best / Tightest month callouts.
    lo_range = f"{L(1)}{left_over_row}:{L(12)}{left_over_row}"
    month_names_range = f"{L(1)}8:{L(12)}8"
    cell(f"{year_col}4", "\U0001F3C6 BEST MONTH")
    cell(f"{year_col}5", f'=IFERROR(INDEX({month_names_range},MATCH(MAX({lo_range}),{lo_range},0)),"--")')
    cell(f"{year_col}6",
         f'=IFERROR(CONCATENATE(SETTINGS!$D$7,TEXT(MAX({lo_range}),"#,##0.00"))," No data yet")')

    tight_col = L(7)
    cell(f"{tight_col}4", "\U0001F4CA TIGHTEST MONTH")
    cell(f"{tight_col}5", f'=IFERROR(INDEX({month_names_range},MATCH(MIN({lo_range}),{lo_range},0)),"--")')
    cell(f"{tight_col}6",
         f'=IFERROR(CONCATENATE(SETTINGS!$D$7,TEXT(MIN({lo_range}),"#,##0.00"))," No data yet")')

    # Positive/negative helper columns for the bar chart.
    pos_col = L(POS_COL)
    neg_col = L(NEG_COL)
    for j, m in enumerate(MONTHS):
        r = j + 1
        lo_cell = f"{L(1 + j)}{left_over_row}"
        cell(f"{pos_col}{r}", f'=IF(ISNUMBER({lo_cell}),IF({lo_cell}>=0,{lo_cell},0),"")')
        cell(f"{neg_col}{r}", f'=IF(ISNUMBER({lo_cell}),IF({lo_cell}<0,{lo_cell},0),"")')

    # Local mirror of SETTINGS!D9 for the Savings rate conditional format rule.
    cell(f"{L(THRESHOLD_COL)}1", "=SETTINGS!$D$9")

    # Vertical month-name column for the chart domain (see CHART_MONTH_COL note).
    for j, m in enumerate(MONTHS):
        cell(f"{L(CHART_MONTH_COL)}{j + 1}", m)

    return values


def _gr(start_row, end_row, start_col, end_col):
    return {"sheetId": SHEET_ID, "startRowIndex": start_row, "endRowIndex": end_row,
            "startColumnIndex": start_col, "endColumnIndex": end_col}


def build_charts():
    """Monthly left-over column chart, positive/negative bars coloured via
    two series (see POS_COL/NEG_COL note) since Sheets charts colour by
    series, not by individual bar. No distinct "current month" bar colour
    or "future month" grey placeholder -- the Charts API has no per-point
    styling, and adding a third series for a placeholder didn't seem worth
    the complexity for a cosmetic detail; flagged in NOTES.md."""
    month_col_phys = CHART_MONTH_COL + PAD
    pos_phys = POS_COL + PAD
    neg_phys = NEG_COL + PAD

    chart = {
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Monthly left over",
                    "basicChart": {
                        "chartType": "COLUMN",
                        "axis": [{"position": "BOTTOM_AXIS"}, {"position": "LEFT_AXIS"}],
                        "domains": [{"domain": {"sourceRange": {"sources": [
                            _gr(0, 12, month_col_phys, month_col_phys + 1)
                        ]}}}],
                        "series": [
                            {"series": {"sourceRange": {"sources": [_gr(0, 12, pos_phys, pos_phys + 1)]}},
                             "targetAxis": "LEFT_AXIS", "colorStyle": {"rgbColor": FINANCE_GREEN}},
                            {"series": {"sourceRange": {"sources": [_gr(0, 12, neg_phys, neg_phys + 1)]}},
                             "targetAxis": "LEFT_AXIS", "colorStyle": {"rgbColor": DEEP_ROSE}},
                        ],
                        "stackedType": "STACKED",
                    },
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": SHEET_ID, "rowIndex": 18, "columnIndex": PAD},
                        "widthPixels": 760,
                        "heightPixels": 340,
                    }
                },
            }
        }
    }
    return [chart]


def clear_conditional_formats(sheets):
    """Delete all existing conditional format rules on this sheet before
    build_requests() adds fresh ones -- same duplicate-rule bug as
    month_tabs.py's clear_conditional_formats(), confirmed here too (a
    second run left 42 rules instead of 14)."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, ranges=["ANNUAL OVERVIEW"], fields="sheets(conditionalFormats)"
    ).execute()
    count = len(meta["sheets"][0].get("conditionalFormats", []))
    if not count:
        return
    requests = [{"deleteConditionalFormatRule": {"sheetId": SHEET_ID, "index": 0}} for _ in range(count)]
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def clear_charts(sheets):
    """Delete any existing charts on this sheet before adding fresh ones.
    Necessary for the same reason clear_conditional_formats() is in
    month_tabs.py: re-running this script on an already-existing sheet
    calls addChart again without removing the old one, so charts stack up
    (confirmed: a first debugging run followed by a fix-and-rerun left two
    identical "Monthly left over" charts instead of one)."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, ranges=["ANNUAL OVERVIEW"], fields="sheets(charts(chartId))"
    ).execute()
    charts = meta["sheets"][0].get("charts", [])
    if not charts:
        return
    requests = [{"deleteEmbeddedObject": {"objectId": c["chartId"]}} for c in charts]
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def main():
    sheets, _drive = get_services()

    recreate_sheet(sheets)
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

    clear_charts(sheets)
    chart_requests = build_charts()
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": chart_requests}
    ).execute()

    print("ANNUAL OVERVIEW built.")


if __name__ == "__main__":
    main()
