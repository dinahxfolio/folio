"""Build the SETTINGS tab: structure, formatting, and values.

Layout reference (1-based row numbers as designed and approved):
  1     Title band
  2     Instruction note
  4     GENERAL band
  5-9   General settings (name, year, currency, starting balance, threshold)
  11    MONTHLY BUDGET TARGETS band
  12    Note
  13    Column headers (Category / Monthly budget target ($))
  14    INCOME divider          15-19  income categories
  20    BILLS divider           21-27  bills categories
  28    EXPENSES divider        29-37  expenses categories
  38    SAVINGS divider         39-43  savings categories
  44    DEBT PAYMENTS divider   45-48  debt categories
  50    SAVINGS GOALS band
  51    Column headers
  52-59 8 goal rows (4 sample, 4 empty)
  61    DEBT TRACKER band
  62    Column headers
  63-66 4 debt rows (2 sample, 2 empty)
  68    Closing note (savings rate threshold)
  70    TRANSACTION TYPES helper label
  71-75 5 type values (Income/Bill/Expense/Saving/Debt)
"""
from auth import get_services
from palette import (
    ARIAL_BLACK,
    CALIBRI,
    CREAM,
    DEEP_ROSE,
    DUSTY_BLUE,
    FINANCE_GREEN,
    MUTED_TAN,
    NEAR_BLACK,
    PALE_NEUTRAL,
    ROSE_PALE_TINT,
    ROW_TINT,
    ROW_WHITE,
    WHITE,
)

SHEET_ID = 100

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()


def grid_range(start_row, end_row, start_col, end_col):
    return {
        "sheetId": SHEET_ID,
        "startRowIndex": start_row,
        "endRowIndex": end_row,
        "startColumnIndex": start_col,
        "endColumnIndex": end_col,
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


def build_requests():
    requests = []

    # Base cream background + default text style across the whole used grid.
    requests.append(repeat_cell(
        grid_range(0, 80, 0, 6),
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
    ))

    # Column widths.
    widths = {0: 210, 1: 170, 2: 150, 3: 150, 4: 40, 5: 40}
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS",
                          "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: title band.
    requests.append(merge(grid_range(0, 1, 0, 4)))
    requests.append(repeat_cell(
        grid_range(0, 1, 0, 4),
        cell_format(bg=NEAR_BLACK, fg=WHITE, font=ARIAL_BLACK, size=18, bold=True, align="LEFT"),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 44},
            "fields": "pixelSize",
        }
    })

    # Row 2: instruction note.
    requests.append(merge(grid_range(1, 2, 0, 4)))
    requests.append(repeat_cell(
        grid_range(1, 2, 0, 4),
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10, italic=True, wrap=True),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 50},
            "fields": "pixelSize",
        }
    })

    def section_band(row_idx, span_cols=4, bg=FINANCE_GREEN):
        r = grid_range(row_idx, row_idx + 1, 0, span_cols)
        requests.append(merge(r))
        requests.append(repeat_cell(
            r, cell_format(bg=bg, fg=WHITE, font=ARIAL_BLACK, size=12, bold=True, align="LEFT"),
        ))

    # Row 4 (idx 3): GENERAL band.
    section_band(3)

    # Rows 5-9 (idx 4-8): general settings label/value pairs.
    general_rows = [4, 5, 6, 7, 8]
    for r in general_rows:
        requests.append(repeat_cell(
            grid_range(r, r + 1, 0, 1),
            cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10, align="LEFT"),
        ))
        requests.append(repeat_cell(
            grid_range(r, r + 1, 1, 2),
            cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=10,
                        bold=True, align="LEFT"),
        ))

    # Number formats for specific general cells.
    requests.append(repeat_cell(
        grid_range(5, 6, 1, 2),
        cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=10, bold=True,
                    number_format={"type": "NUMBER", "pattern": "0"}),
        fields="userEnteredFormat.numberFormat",
    ))
    requests.append(repeat_cell(
        grid_range(7, 8, 1, 2),
        cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=10, bold=True,
                    number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
        fields="userEnteredFormat.numberFormat",
    ))
    requests.append(repeat_cell(
        grid_range(8, 9, 1, 2),
        cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=10, bold=True,
                    number_format={"type": "PERCENT", "pattern": "0.00%"}),
        fields="userEnteredFormat.numberFormat",
    ))

    # Row 11 (idx 10): MONTHLY BUDGET TARGETS band.
    section_band(10)

    # Row 12 (idx 11): note.
    requests.append(merge(grid_range(11, 12, 0, 4)))
    requests.append(repeat_cell(
        grid_range(11, 12, 0, 4),
        cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True, wrap=True),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 11, "endIndex": 12},
            "properties": {"pixelSize": 34},
            "fields": "pixelSize",
        }
    })

    # Row 13 (idx 12): column headers for the budget table.
    requests.append(repeat_cell(
        grid_range(12, 13, 0, 2),
        cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True),
    ))

    type_groups = [
        ("INCOME", FINANCE_GREEN, ["Salary / Wages", "Freelance", "Side hustle", "Bonus", "Other income"]),
        ("BILLS", DUSTY_BLUE, ["Rent / Mortgage", "Electricity", "Gas / Water", "Internet", "Phone",
                                "Insurance", "Subscriptions"]),
        ("EXPENSES", MUTED_TAN, ["Groceries", "Dining out", "Transport", "Health", "Clothing",
                                  "Entertainment", "Personal care", "Gifts", "Miscellaneous"]),
        ("SAVINGS", FINANCE_GREEN, ["Emergency fund", "Holiday", "House deposit", "Retirement",
                                     "Other savings"]),
        ("DEBT PAYMENTS", DEEP_ROSE, ["Credit card", "Student loan", "Personal loan", "Car finance"]),
    ]

    row_cursor = 13  # 0-indexed row for the first divider (row 14, 1-based)
    category_row_map = {}  # group name -> (start_idx, end_idx) for later reference
    for group_name, color, categories in type_groups:
        divider_range = grid_range(row_cursor, row_cursor + 1, 0, 2)
        requests.append(merge(divider_range))
        requests.append(repeat_cell(
            divider_range,
            cell_format(bg=color, fg=WHITE, font=CALIBRI, size=10, bold=True, align="LEFT"),
        ))
        row_cursor += 1
        start_idx = row_cursor
        for i, _cat in enumerate(categories):
            row_idx = row_cursor + i
            band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
            requests.append(repeat_cell(
                grid_range(row_idx, row_idx + 1, 0, 1),
                cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
            ))
            requests.append(repeat_cell(
                grid_range(row_idx, row_idx + 1, 1, 2),
                cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                            number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
            ))
        category_row_map[group_name] = (start_idx, start_idx + len(categories))
        row_cursor += len(categories)

    # row_cursor is now idx 48 (row 49), the spacer before SAVINGS GOALS.
    goals_band_idx = row_cursor + 1  # idx 49 -> row 50
    section_band(goals_band_idx)

    goals_header_idx = goals_band_idx + 1  # idx 50 -> row 51
    requests.append(repeat_cell(
        grid_range(goals_header_idx, goals_header_idx + 1, 0, 4),
        cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True),
    ))

    goals_start_idx = goals_header_idx + 1  # idx 51 -> row 52
    for i in range(8):
        row_idx = goals_start_idx + i
        band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 0, 1),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="CENTER"),
        ))
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 1, 2),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
        ))
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 2, 3),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                        number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
        ))
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 3, 4),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                        number_format={"type": "DATE", "pattern": "dd/mm/yyyy"}),
        ))

    goals_end_idx = goals_start_idx + 8  # idx 59 -> row 60 (spacer)

    debt_band_idx = goals_end_idx + 1  # idx 60 -> row 61
    section_band(debt_band_idx, bg=DEEP_ROSE)

    debt_header_idx = debt_band_idx + 1  # idx 61 -> row 62
    requests.append(repeat_cell(
        grid_range(debt_header_idx, debt_header_idx + 1, 0, 3),
        cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True),
    ))

    debt_start_idx = debt_header_idx + 1  # idx 62 -> row 63
    for i in range(4):
        row_idx = debt_start_idx + i
        band_bg = ROW_WHITE if i % 2 == 0 else ROW_TINT
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 0, 1),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="CENTER"),
        ))
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 1, 2),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
        ))
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 2, 3),
            cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                        number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
        ))

    debt_end_idx = debt_start_idx + 4  # idx 66 -> row 67 (spacer)

    # Closing note (row 68 -> idx 67), rose pale tint.
    note_idx = debt_end_idx + 1
    requests.append(merge(grid_range(note_idx, note_idx + 1, 0, 4)))
    requests.append(repeat_cell(
        grid_range(note_idx, note_idx + 1, 0, 4),
        cell_format(bg=ROSE_PALE_TINT, fg=DEEP_ROSE, font=CALIBRI, size=10, wrap=True),
    ))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": note_idx, "endIndex": note_idx + 1},
            "properties": {"pixelSize": 44},
            "fields": "pixelSize",
        }
    })

    # Transaction types helper block.
    types_label_idx = note_idx + 2  # one spacer row then label
    requests.append(merge(grid_range(types_label_idx, types_label_idx + 1, 0, 2)))
    requests.append(repeat_cell(
        grid_range(types_label_idx, types_label_idx + 1, 0, 2),
        cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True, wrap=True),
    ))
    types_start_idx = types_label_idx + 1
    for i in range(5):
        row_idx = types_start_idx + i
        requests.append(repeat_cell(
            grid_range(row_idx, row_idx + 1, 0, 1),
            cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10),
        ))

    layout = {
        "category_row_map": category_row_map,
        "goals_start_idx": goals_start_idx,
        "debt_start_idx": debt_start_idx,
        "types_start_idx": types_start_idx,
        "note_idx": note_idx,
        "types_label_idx": types_label_idx,
    }
    return requests, layout


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"SETTINGS!{a1}", "values": [[v]]})

    cell("A1", "SETTINGS")
    cell("A2", "Start here before using any other tab. Fill in your name, year, currency, and "
               "starting balance first, then set your monthly budget targets by category. "
               "You only need to do this once.")

    cell("A4", "GENERAL")
    cell("A5", "Your name")
    cell("B5", "Sarah")
    cell("A6", "Year")
    cell("B6", 2026)
    cell("A7", "Currency symbol")
    cell("B7", "$")
    cell("A8", "Starting balance")
    cell("B8", 1250)
    cell("A9", "Savings rate threshold")
    cell("B9", 0.10)

    cell("A11", "MONTHLY BUDGET TARGETS")
    cell("A12", "Category names are fully editable. Change any name here and it updates across "
                "the whole spreadsheet, including the transaction dropdowns, the dashboard, and "
                "the annual overview.")
    cell("A13", "Category")
    cell("B13", '=CONCATENATE("Monthly budget target (",B7,")")')

    type_groups = [
        ("INCOME", ["Salary / Wages", "Freelance", "Side hustle", "Bonus", "Other income"]),
        ("BILLS", ["Rent / Mortgage", "Electricity", "Gas / Water", "Internet", "Phone",
                    "Insurance", "Subscriptions"]),
        ("EXPENSES", ["Groceries", "Dining out", "Transport", "Health", "Clothing",
                       "Entertainment", "Personal care", "Gifts", "Miscellaneous"]),
        ("SAVINGS", ["Emergency fund", "Holiday", "House deposit", "Retirement", "Other savings"]),
        ("DEBT PAYMENTS", ["Credit card", "Student loan", "Personal loan", "Car finance"]),
    ]
    row_cursor = 13  # 0-indexed row for first divider (row 14)
    for group_name, categories in type_groups:
        cell(f"A{row_cursor + 1}", group_name)
        row_cursor += 1
        for i, catname in enumerate(categories):
            cell(f"A{row_cursor + i + 1}", catname)
        row_cursor += len(categories)

    # Savings goals.
    gs = layout["goals_start_idx"] + 1  # 1-based first goal row
    cell(f"A{gs - 2}", "SAVINGS GOALS")
    cell(f"A{gs - 1}", "#")
    cell(f"B{gs - 1}", "Goal name")
    cell(f"C{gs - 1}", '=CONCATENATE("Target amount (",B7,")")')
    cell(f"D{gs - 1}", "Target date")

    goal_rows = [
        (1, "Emergency fund (3 months)", 5000, "31/12/2026"),
        (2, "Dream holiday", 2000, "30/06/2026"),
        (3, "New laptop", 1200, "30/09/2026"),
        (4, "Wedding fund", 8000, "31/12/2027"),
        (5, "", "", ""),
        (6, "", "", ""),
        (7, "", "", ""),
        (8, "", "", ""),
    ]
    for i, (num, name, amt, date) in enumerate(goal_rows):
        r = gs + i
        cell(f"A{r}", num)
        if name:
            cell(f"B{r}", name)
            cell(f"C{r}", amt)
            cell(f"D{r}", date)

    # Debt tracker.
    ds = layout["debt_start_idx"] + 1
    cell(f"A{ds - 2}", "DEBT TRACKER")
    cell(f"A{ds - 1}", "#")
    cell(f"B{ds - 1}", "Debt name")
    cell(f"C{ds - 1}", '=CONCATENATE("Starting balance (",B7,")")')

    debt_rows = [
        (1, "Credit card", 3500),
        (2, "Student loan", 12000),
        (3, "", ""),
        (4, "", ""),
    ]
    for i, (num, name, bal) in enumerate(debt_rows):
        r = ds + i
        cell(f"A{r}", num)
        if name:
            cell(f"B{r}", name)
            cell(f"C{r}", bal)

    note_row = layout["note_idx"] + 1
    cell(f"A{note_row}",
         "Savings rate threshold: set this to the minimum savings rate you want to hit each "
         "month. The Annual Overview will flag any month that falls below it.")

    types_label_row = layout["types_label_idx"] + 1
    cell(f"A{types_label_row}",
         "Transaction types (used for the Type dropdown on month tabs -- please don't delete)")
    ts = layout["types_start_idx"] + 1
    for i, t in enumerate(["Income", "Bill", "Expense", "Saving", "Debt"]):
        cell(f"A{ts + i}", t)

    return values


def build_notes():
    """Cell notes marking sample data, keyed by A1 address."""
    return {
        "B5": "Sample value -- replace with your own name.",
        "B8": "Sample value -- replace with your own starting balance.",
        "B52": "Sample goal -- delete or replace.",
        "C52": "Sample goal -- delete or replace.",
        "D52": "Sample goal -- delete or replace.",
        "B53": "Sample goal -- delete or replace.",
        "C53": "Sample goal -- delete or replace.",
        "D53": "Sample goal -- delete or replace.",
        "B54": "Sample goal -- delete or replace.",
        "C54": "Sample goal -- delete or replace.",
        "D54": "Sample goal -- delete or replace.",
        "B55": "Sample goal -- delete or replace.",
        "C55": "Sample goal -- delete or replace.",
        "D55": "Sample goal -- delete or replace.",
        "B63": "Sample debt -- delete or replace.",
        "C63": "Sample debt -- delete or replace.",
        "B64": "Sample debt -- delete or replace.",
        "C64": "Sample debt -- delete or replace.",
    }


def main():
    sheets, _drive = get_services()

    requests, layout = build_requests()
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()

    values = build_values(layout)
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": values},
    ).execute()

    # Cell notes for sample-data markers.
    note_requests = []
    for a1, text in build_notes().items():
        note_requests.append({
            "updateCells": {
                "range": a1_to_grid_range(a1),
                "rows": [{"values": [{"note": text}]}],
                "fields": "note",
            }
        })
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": note_requests}
    ).execute()

    print("SETTINGS tab built. Layout:", layout)


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


if __name__ == "__main__":
    main()
