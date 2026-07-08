"""Build the 12 month transaction tabs (Jan-Dec), per design-brief-v2 Section 3/4/5:
visible tabs (not hidden), muted grey tab colour, chronological entry at the
bottom of the list (not newest-first), no HYPERLINK navigation, no INDIRECT.

Column scheme (padding convention applies): A = padding.
  B Date | C Description | D Type | E Category | F Amount | G Balance | H Notes

Running balance carries across tabs without INDIRECT: each tab's opening
balance is a static formula naming its specific predecessor tab directly.
Each month also carries a small numeric helper cell (I1, "closing balance")
so the carry-forward is a single hop rather than a growing nested formula:
  I1 = IF(no transactions this month, this month's own opening value,
          INDEX(Balance column, COUNTA(Type column)))
  next month's opening = this month's I1
A month with zero transactions still correctly passes its own (unchanged)
opening value through to the next month via this fallback, rather than
resetting to SETTINGS' starting balance.
"""
from auth import get_services
from palette import (
    ARIAL_BLACK,
    CALIBRI,
    CREAM,
    DEEP_ROSE,
    DUSTY_BLUE,
    FINANCE_GREEN,
    MUTED_GREY,
    MUTED_TAN,
    NEAR_BLACK,
    PALE_NEUTRAL,
    lighten,
    ROW_TINT,
    ROW_WHITE,
    WHITE,
)

PAD = 1
FIRST_DATA_ROW = 4  # 1-based
LAST_DATA_ROW = 48  # 1-based
N_DATA_ROWS = LAST_DATA_ROW - FIRST_DATA_ROW + 1

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_FULL = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
              "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
SHEET_IDS = {m: 300 + i for i, m in enumerate(MONTHS)}

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

TYPE_COLORS = {
    "Income": FINANCE_GREEN,
    "Bill": DUSTY_BLUE,
    "Expense": MUTED_TAN,
    "Saving": FINANCE_GREEN,
    "Debt": DEEP_ROSE,
}


def col_letter(logical_col):
    n = logical_col + PAD + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


COL_DATE = col_letter(0)         # B
COL_DESC = col_letter(1)         # C
COL_TYPE = col_letter(2)         # D
COL_CATEGORY = col_letter(3)     # E
COL_AMOUNT = col_letter(4)       # F
COL_BALANCE = col_letter(5)      # G
COL_NOTES = col_letter(6)        # H


def grid_range(sheet_id, start_row, end_row, start_col, end_col):
    return {
        "sheetId": sheet_id,
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


def recreate_month_sheets(sheets):
    """Add any month sheets that don't exist yet. IMPORTANT: never delete and
    recreate a month sheet once DASHBOARD (or later, ANNUAL OVERVIEW/GOALS)
    references it via CHOOSE() -- Google Sheets binds cross-sheet formula
    references to an internal sheet identity, not just the visible
    sheetId/title, so a delete+recreate breaks every formula elsewhere that
    pointed at it (confirmed the hard way when this happened to SETTINGS;
    see build/NOTES.md). Once a month sheet exists, build_requests_for_month/
    build_values_for_month update it in place."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    existing_ids = {s["properties"]["sheetId"] for s in meta["sheets"]}

    requests = []
    for i, m in enumerate(MONTHS):
        sid = SHEET_IDS[m]
        if sid in existing_ids:
            continue
        requests.append({
            "addSheet": {
                "properties": {
                    "sheetId": sid,
                    "title": m,
                    "index": i + 1,  # after SETTINGS for now
                    "gridProperties": {"rowCount": 60, "columnCount": 9, "hideGridlines": True},
                    "tabColor": MUTED_GREY,
                }
            }
        })
    if not requests:
        return
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def opening_source(month_idx):
    """This month's opening-balance value: SETTINGS for Jan, or the previous
    month's own closing-balance helper cell (I1) for every other month. A
    single hop -- Feb points at Jan!$I$1, not at a re-derivation of Jan's
    whole history -- so formulas stay short and don't nest across 12 months."""
    if month_idx == 0:
        return "SETTINGS!$D$8"
    return f"{MONTHS[month_idx - 1]}!$I$1"


def closing_formula(month_idx):
    """This month's closing-balance helper (goes in I1). If no transactions
    were entered this month, the closing balance is just the opening value
    unchanged (not SETTINGS' starting balance -- that would reset every
    empty month back to year-start). Otherwise it's the last transaction's
    running balance, found via COUNTA/INDEX (transactions are entered
    contiguously from the top, so the count of filled Type cells is the row
    offset of the last one). Deliberately not the classic
    LOOKUP(2,1/(range<>""),range) "last value" idiom -- that returns #N/A in
    Google Sheets here since the division isn't auto-arrayed without an
    explicit ARRAYFORMULA wrapper; COUNTA/INDEX needs no such wrapper."""
    type_rng = f"$D${FIRST_DATA_ROW}:$D${LAST_DATA_ROW}"
    bal_rng = f"$G${FIRST_DATA_ROW}:$G${LAST_DATA_ROW}"
    return (f'=IF(COUNTA({type_rng})=0,{opening_source(month_idx)},'
            f'INDEX({bal_rng},COUNTA({type_rng})))')


def build_requests_for_month(month_idx):
    m = MONTHS[month_idx]
    sid = SHEET_IDS[m]
    requests = []

    # Base cream background across the used grid.
    requests.append(repeat_cell(
        {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 60, "startColumnIndex": 0, "endColumnIndex": 9},
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
    ))

    widths = {0: 28, 1: 90, 2: 190, 3: 110, 4: 170, 5: 110, 6: 110, 7: 160, 8: 70}
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: title (B1:E1) + opening balance pill (F1:H1).
    title_range = grid_range(sid, 0, 1, 0, 3)
    pill_range = grid_range(sid, 0, 1, 3, 7)
    requests.append(merge(title_range))
    requests.append(merge(pill_range))
    requests.append(repeat_cell(
        title_range, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=16, bold=True, align="LEFT"),
    ))
    requests.append(repeat_cell(
        pill_range, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=CALIBRI, size=10, bold=True, align="RIGHT"),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sid, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 40},
            "fields": "pixelSize",
        }
    })

    # I1: closing-balance helper cell -- visible but de-emphasised, with a
    # note explaining what it's for (see module docstring).
    closing_cell_range = grid_range(sid, 0, 1, 7, 8)
    requests.append(repeat_cell(
        closing_cell_range,
        cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=8, align="RIGHT",
                    number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
    ))
    requests.append({
        "updateCells": {
            "range": closing_cell_range,
            "rows": [{"values": [{"note": "Internal helper: this month's closing balance, "
                                           "used to carry the running total into next month. "
                                           "Please don't delete."}]}],
            "fields": "note",
        }
    })

    # Row 2: instruction note.
    note_range = grid_range(sid, 1, 2, 0, 7)
    requests.append(merge(note_range))
    requests.append(repeat_cell(
        note_range, cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True, wrap=True),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sid, "dimension": "ROWS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 30},
            "fields": "pixelSize",
        }
    })

    # Row 3: column headers.
    header_range = grid_range(sid, 2, 3, 0, 7)
    requests.append(repeat_cell(
        header_range, cell_format(bg=NEAR_BLACK, fg=WHITE, font=CALIBRI, size=10, bold=True),
    ))

    # Data rows 4-48 (0-indexed 3-47): row banding + number formats.
    for r in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
        idx = r - 1  # 0-indexed
        band_bg = ROW_WHITE if (r - FIRST_DATA_ROW) % 2 == 0 else ROW_TINT
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 0, 1),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="LEFT",
                        number_format={"type": "DATE", "pattern": "dd/mm/yyyy"}),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 1, 2),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 2, 3),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="CENTER"),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 3, 4),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 4, 5),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                        number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 5, 6),
            cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                        number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
        ))
        requests.append(repeat_cell(
            grid_range(sid, idx, idx + 1, 6, 7),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, italic=True),
        ))

    # Data validation: Type dropdown.
    requests.append({
        "setDataValidation": {
            "range": grid_range(sid, FIRST_DATA_ROW - 1, LAST_DATA_ROW, 2, 3),
            "rule": {
                "condition": {"type": "ONE_OF_RANGE",
                               "values": [{"userEnteredValue": "=SETTINGS!$B$71:$B$75"}]},
                "showCustomUi": True,
                "strict": True,
            },
        }
    })
    # Data validation: Category dropdown (flat list with divider rows, B14:B48).
    requests.append({
        "setDataValidation": {
            "range": grid_range(sid, FIRST_DATA_ROW - 1, LAST_DATA_ROW, 3, 4),
            "rule": {
                "condition": {"type": "ONE_OF_RANGE",
                               "values": [{"userEnteredValue": "=SETTINGS!$B$14:$B$48"}]},
                "showCustomUi": True,
                "strict": True,
            },
        }
    })
    # Data validation: Amount must be positive.
    requests.append({
        "setDataValidation": {
            "range": grid_range(sid, FIRST_DATA_ROW - 1, LAST_DATA_ROW, 4, 5),
            "rule": {
                "condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]},
                "inputMessage": "Enter a positive amount.",
                "strict": True,
            },
        }
    })

    # Conditional formatting: Type badge colours. Fill is a ~25%-opacity
    # tint of the type colour (Minnie's feedback: the original solid fills
    # read too strong for a per-transaction badge); text switches to the
    # full-strength colour instead of white, since white doesn't have
    # enough contrast against the lightened fill.
    type_range = grid_range(sid, FIRST_DATA_ROW - 1, LAST_DATA_ROW, 2, 3)
    for value, color in TYPE_COLORS.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [type_range],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": value}]},
                        "format": {"backgroundColor": lighten(color, 0.25),
                                   "textFormat": {"foregroundColor": color, "bold": True}},
                    },
                },
                "index": 0,
            }
        })

    return requests


def build_values_for_month(month_idx):
    m = MONTHS[month_idx]
    opening = opening_source(month_idx)
    values = []

    def cell(a1, v):
        values.append({"range": f"{m}!{a1}", "values": [[v]]})

    cell(f"{COL_DATE}1", f'=CONCATENATE("{MONTH_FULL[month_idx]} ",SETTINGS!$D$6)')
    cell(f"{COL_CATEGORY}1", f'=CONCATENATE("Opening: ",SETTINGS!$D$7,TEXT({opening},"#,##0.00"))')
    cell(f"{COL_DATE}2", "Enter each transaction in the next empty row below. "
                          "Your Dashboard updates automatically.")
    # Closing-balance helper (see module docstring). Visible, not hidden, but
    # off to the side in the unused buffer column, with a note explaining it.
    cell("I1", closing_formula(month_idx))

    cell(f"{COL_DATE}3", "Date")
    cell(f"{COL_DESC}3", "Description")
    cell(f"{COL_TYPE}3", "Type")
    cell(f"{COL_CATEGORY}3", "Category")
    cell(f"{COL_AMOUNT}3", '=CONCATENATE("Amount (",SETTINGS!$D$7,")")')
    cell(f"{COL_BALANCE}3", '=CONCATENATE("Balance (",SETTINGS!$D$7,")")')
    cell(f"{COL_NOTES}3", "Notes")

    # Balance formulas for every data row (blank rows stay blank).
    for r in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
        prev_balance = opening if r == FIRST_DATA_ROW else f"{COL_BALANCE}{r - 1}"
        formula = (f'=IF({COL_TYPE}{r}="","",'
                   f'IF({COL_TYPE}{r}="Income",{prev_balance}+{COL_AMOUNT}{r},'
                   f'{prev_balance}-{COL_AMOUNT}{r}))')
        cell(f"{COL_BALANCE}{r}", formula)

    return values


# Sample data: a handful of illustrative transactions in Jan and Feb only.
# Dates are entered in ISO format (YYYY-MM-DD) so Sheets parses them
# unambiguously regardless of spreadsheet locale -- a DD/MM-style string like
# "02/01/2026" gets silently misread as MM/DD (1 Feb) under the default en_US
# locale, which the dd/mm/yyyy *display* format does not protect against.
SAMPLE_DATA = {
    0: [  # Jan
        ("2026-01-01", "Salary", "Income", "Salary / Wages", 3200, ""),
        ("2026-01-02", "Rent", "Bill", "Rent / Mortgage", 950, "SAMPLE -- delete this row"),
        ("2026-01-03", "Weekly shop", "Expense", "Groceries", 62.50, "SAMPLE -- delete this row"),
        ("2026-01-05", "Electricity bill", "Bill", "Electricity", 48, "SAMPLE -- delete this row"),
        ("2026-01-10", "Emergency fund transfer", "Saving", "Emergency fund", 200, "SAMPLE -- delete this row"),
        ("2026-01-15", "Credit card payment", "Debt", "Credit card", 150, "SAMPLE -- delete this row"),
    ],
    1: [  # Feb
        ("2026-02-01", "Salary", "Income", "Salary / Wages", 3200, "SAMPLE -- delete this row"),
        ("2026-02-02", "Rent", "Bill", "Rent / Mortgage", 950, "SAMPLE -- delete this row"),
        ("2026-02-04", "Dinner out", "Expense", "Dining out", 38, "SAMPLE -- delete this row"),
    ],
}


def build_sample_values(month_idx):
    m = MONTHS[month_idx]
    values = []
    rows = SAMPLE_DATA.get(month_idx, [])
    for i, (date, desc, ttype, cat, amount, note) in enumerate(rows):
        r = FIRST_DATA_ROW + i
        values.append({"range": f"{m}!{COL_DATE}{r}", "values": [[date]]})
        values.append({"range": f"{m}!{COL_DESC}{r}", "values": [[desc]]})
        values.append({"range": f"{m}!{COL_TYPE}{r}", "values": [[ttype]]})
        values.append({"range": f"{m}!{COL_CATEGORY}{r}", "values": [[cat]]})
        values.append({"range": f"{m}!{COL_AMOUNT}{r}", "values": [[amount]]})
        if note:
            values.append({"range": f"{m}!{COL_NOTES}{r}", "values": [[note]]})
    return values


def clear_conditional_formats(sheets):
    """Delete every existing conditional format rule on each month sheet
    before build_requests_for_month() adds fresh ones. Necessary because
    re-running this script on sheets that already exist (the normal,
    now-safe path) would otherwise stack duplicate rules on top of the old
    ones via addConditionalFormatRule, rather than replacing them -- this
    happened for real: a previous repair run left 10 rules per month tab
    (5 old strong-colour + 5 new) instead of 5."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets(properties(sheetId,title),conditionalFormats)"
    ).execute()
    requests = []
    for s in meta["sheets"]:
        if s["properties"]["title"] not in MONTHS:
            continue
        sid = s["properties"]["sheetId"]
        count = len(s.get("conditionalFormats", []))
        for _ in range(count):
            requests.append({"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}})
    if requests:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
        ).execute()


def main():
    sheets, _drive = get_services()

    recreate_month_sheets(sheets)
    clear_conditional_formats(sheets)

    all_requests = []
    for i in range(12):
        all_requests.extend(build_requests_for_month(i))
    # batchUpdate has a practical size limit; chunk it.
    CHUNK = 400
    for i in range(0, len(all_requests), CHUNK):
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": all_requests[i:i + CHUNK]}
        ).execute()

    all_values = []
    for i in range(12):
        all_values.extend(build_values_for_month(i))
    for i in range(12):
        all_values.extend(build_sample_values(i))

    VCHUNK = 300
    for i in range(0, len(all_values), VCHUNK):
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": all_values[i:i + VCHUNK]},
        ).execute()

    print("Month tabs built:", MONTHS)


if __name__ == "__main__":
    main()
