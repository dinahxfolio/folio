"""Build the SETTINGS tab: structure, formatting, and values.

Column scheme (applies as the standing convention for every tab in this build):
  Column A = blank padding column, never contains content.
  Columns B-E = the 4-column content width. Two-column sections (General,
  Monthly Budget Targets) merge B:C for the label and D:E for the value, so
  they visually fill the same width as the full-width section bands above them.

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
PAD = 1  # column A is padding; content starts at column B (index 1)

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()


def grid_range(start_row, end_row, start_col, end_col):
    """start_col/end_col are logical content-column indices (0 = column B)."""
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


def recreate_sheet(sheets):
    """Create the SETTINGS sheet if it doesn't exist yet. IMPORTANT: never
    delete+recreate an existing sheet that other tabs already reference --
    Google Sheets binds cross-sheet formula references (e.g. DASHBOARD's
    "=SETTINGS!$D$15") to an internal sheet identity, not just the visible
    sheetId/title. Deleting and recreating SETTINGS (even with the identical
    sheetId and name) previously broke every DASHBOARD formula that
    referenced it with "#REF! (Unresolved sheet name 'SETTINGS')", even
    though a sheet named SETTINGS still existed afterwards. Once downstream
    tabs exist, updates must happen in place: build_requests()/build_values()
    already overwrite the full grid's formatting and content, which is
    sufficient since SETTINGS' shape only ever grows additively."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    exists = any(s["properties"]["sheetId"] == SHEET_ID for s in meta["sheets"])
    if exists:
        return

    requests = [{"addSheet": {"properties": {"sheetId": 999999, "title": "__temp__"}}}]
    requests.append({
        "addSheet": {
            "properties": {
                "sheetId": SHEET_ID,
                "title": "SETTINGS",
                "gridProperties": {"rowCount": 80, "columnCount": 7, "hideGridlines": True},
                "tabColor": NEAR_BLACK,
            }
        }
    })
    requests.append({"deleteSheet": {"sheetId": 999999}})
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def build_requests():
    requests = []

    # Base cream background + default text style across the whole used grid
    # (including the padding column, so it reads as blank margin, not white).
    requests.append({
        "repeatCell": {
            "range": {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 80,
                      "startColumnIndex": 0, "endColumnIndex": 7},
            "cell": {"userEnteredFormat": cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10)},
            "fields": "userEnteredFormat",
        }
    })

    # Column widths: A = padding, B-E = content, F/G = right buffer.
    widths = {0: 28, 1: 150, 2: 150, 3: 150, 4: 150, 5: 40, 6: 40}
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS",
                          "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: title band (full 4-column content width).
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

    def section_band(row_idx, bg=FINANCE_GREEN):
        r = grid_range(row_idx, row_idx + 1, 0, 4)
        requests.append(merge(r))
        requests.append(repeat_cell(
            r, cell_format(bg=bg, fg=WHITE, font=ARIAL_BLACK, size=12, bold=True, align="LEFT"),
        ))

    def label_value_row(row_idx, number_format=None):
        """Label merged over logical cols 0-1 (B:C), value merged over 2-3 (D:E)."""
        label_range = grid_range(row_idx, row_idx + 1, 0, 2)
        value_range = grid_range(row_idx, row_idx + 1, 2, 4)
        requests.append(merge(label_range))
        requests.append(merge(value_range))
        requests.append(repeat_cell(
            label_range,
            cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=10, align="LEFT"),
        ))
        value_fmt = cell_format(bg=PALE_NEUTRAL, fg=FINANCE_GREEN, font=CALIBRI, size=10,
                                 bold=True, align="LEFT", number_format=number_format)
        requests.append(repeat_cell(value_range, value_fmt))

    # Row 4 (idx 3): GENERAL band.
    section_band(3)

    # Rows 5-9 (idx 4-8): general settings label/value pairs.
    label_value_row(4)  # Your name
    label_value_row(5, {"type": "NUMBER", "pattern": "0"})  # Year
    label_value_row(6)  # Currency symbol
    label_value_row(7, {"type": "NUMBER", "pattern": "#,##0.00"})  # Starting balance
    label_value_row(8, {"type": "PERCENT", "pattern": "0.00%"})  # Savings rate threshold

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
    # Category (merged B:C) | Monthly budget target (D) | Due day (E, Bills only).
    header_label = grid_range(12, 13, 0, 2)
    header_target = grid_range(12, 13, 2, 3)
    header_due = grid_range(12, 13, 3, 4)
    requests.append(merge(header_label))
    requests.append(repeat_cell(
        header_label, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True),
    ))
    requests.append(repeat_cell(
        header_target, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True),
    ))
    requests.append(repeat_cell(
        header_due, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10, bold=True,
                                 align="RIGHT"),
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
        divider_range = grid_range(row_cursor, row_cursor + 1, 0, 4)
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
            name_range = grid_range(row_idx, row_idx + 1, 0, 2)
            target_range = grid_range(row_idx, row_idx + 1, 2, 3)
            due_range = grid_range(row_idx, row_idx + 1, 3, 4)
            requests.append(merge(name_range))
            requests.append(repeat_cell(
                name_range, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10),
            ))
            requests.append(repeat_cell(
                target_range,
                cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                            number_format={"type": "NUMBER", "pattern": "#,##0.00"}),
            ))
            requests.append(repeat_cell(
                due_range,
                cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=10, align="RIGHT",
                            number_format={"type": "NUMBER", "pattern": "0"}),
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


def col_letter(logical_col):
    """logical_col 0 -> 'B', 1 -> 'C', etc. (accounts for the padding column)."""
    n = logical_col + PAD + 1  # 1-based sheet column number
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


LABEL_COL = col_letter(0)   # B
VALUE_COL = col_letter(2)   # D  (top-left of the merged D:E value cell)
COL_C = col_letter(1)       # C
COL_E = col_letter(3)       # E


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"SETTINGS!{a1}", "values": [[v]]})

    cell(f"{LABEL_COL}1", "SETTINGS")
    cell(f"{LABEL_COL}2", "Start here before using any other tab. Fill in your name, year, currency, and "
                          "starting balance first, then set your monthly budget targets by category. "
                          "You only need to do this once.")

    cell(f"{LABEL_COL}4", "GENERAL")
    cell(f"{LABEL_COL}5", "Your name")
    cell(f"{VALUE_COL}5", "Sarah")
    cell(f"{LABEL_COL}6", "Year")
    cell(f"{VALUE_COL}6", 2026)
    cell(f"{LABEL_COL}7", "Currency symbol")
    cell(f"{VALUE_COL}7", "$")
    cell(f"{LABEL_COL}8", "Starting balance")
    cell(f"{VALUE_COL}8", 1250)
    cell(f"{LABEL_COL}9", "Savings rate threshold")
    cell(f"{VALUE_COL}9", 0.10)

    currency_cell = f"{VALUE_COL}7"  # SETTINGS!D7

    cell(f"{LABEL_COL}11", "MONTHLY BUDGET TARGETS")
    cell(f"{LABEL_COL}12", "Category names are fully editable. Change any name here and it updates across "
                           "the whole spreadsheet, including the transaction dropdowns, the dashboard, and "
                           "the annual overview.")
    cell(f"{LABEL_COL}13", "Category")
    cell(f"{VALUE_COL}13", f'=CONCATENATE("Monthly budget target (",{currency_cell},")")')
    cell(f"{COL_E}13", "Due day")

    # Sample monthly budget targets, plausible representative amounts (Sarah's
    # sample data set, same spirit as the general-settings sample values).
    # Due day (day of month, 1-31) only applies to Bills -- it feeds the
    # DASHBOARD Upcoming Bills block. Other groups leave due day blank.
    type_groups = [
        ("INCOME", [("Salary / Wages", 3200, None), ("Freelance", 0, None),
                     ("Side hustle", 0, None), ("Bonus", 0, None), ("Other income", 0, None)]),
        ("BILLS", [("Rent / Mortgage", 950, 1), ("Electricity", 60, 15), ("Gas / Water", 45, 18),
                    ("Internet", 35, 5), ("Phone", 30, 10), ("Insurance", 40, 1),
                    ("Subscriptions", 25, 1)]),
        ("EXPENSES", [("Groceries", 400, None), ("Dining out", 120, None), ("Transport", 100, None),
                       ("Health", 50, None), ("Clothing", 60, None), ("Entertainment", 80, None),
                       ("Personal care", 40, None), ("Gifts", 30, None), ("Miscellaneous", 50, None)]),
        ("SAVINGS", [("Emergency fund", 200, None), ("Holiday", 100, None), ("House deposit", 150, None),
                      ("Retirement", 100, None), ("Other savings", 50, None)]),
        ("DEBT PAYMENTS", [("Credit card", 150, None), ("Student loan", 200, None),
                            ("Personal loan", 100, None), ("Car finance", 180, None)]),
    ]
    row_cursor = 13  # 0-indexed row for first divider (row 14)
    for group_name, categories in type_groups:
        cell(f"{LABEL_COL}{row_cursor + 1}", group_name)
        row_cursor += 1
        for i, (catname, target, due_day) in enumerate(categories):
            cell(f"{LABEL_COL}{row_cursor + i + 1}", catname)
            cell(f"{VALUE_COL}{row_cursor + i + 1}", target)
            if due_day is not None:
                cell(f"{COL_E}{row_cursor + i + 1}", due_day)
        row_cursor += len(categories)

    # Savings goals (genuine 4-column table: B=#, C=Goal name, D=Target amount, E=Target date).
    gs = layout["goals_start_idx"] + 1  # 1-based first goal row
    cell(f"{LABEL_COL}{gs - 2}", "SAVINGS GOALS")
    cell(f"{LABEL_COL}{gs - 1}", "#")
    cell(f"{COL_C}{gs - 1}", "Goal name")
    cell(f"{COL_E}{gs - 1}", "Target date")
    values.append({"range": f"SETTINGS!{VALUE_COL}{gs - 1}",
                    "values": [[f'=CONCATENATE("Target amount (",{currency_cell},")")']]})

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
        cell(f"{LABEL_COL}{r}", num)
        if name:
            cell(f"{COL_C}{r}", name)
            cell(f"{VALUE_COL}{r}", amt)
            cell(f"{COL_E}{r}", date)

    # Debt tracker (3-column table: B=#, C=Debt name, D=Starting balance).
    ds = layout["debt_start_idx"] + 1
    cell(f"{LABEL_COL}{ds - 2}", "DEBT TRACKER")
    cell(f"{LABEL_COL}{ds - 1}", "#")
    cell(f"{COL_C}{ds - 1}", "Debt name")
    values.append({"range": f"SETTINGS!{VALUE_COL}{ds - 1}",
                    "values": [[f'=CONCATENATE("Starting balance (",{currency_cell},")")']]})

    debt_rows = [
        (1, "Credit card", 3500),
        (2, "Student loan", 12000),
        (3, "", ""),
        (4, "", ""),
    ]
    for i, (num, name, bal) in enumerate(debt_rows):
        r = ds + i
        cell(f"{LABEL_COL}{r}", num)
        if name:
            cell(f"{COL_C}{r}", name)
            cell(f"{VALUE_COL}{r}", bal)

    note_row = layout["note_idx"] + 1
    cell(f"{LABEL_COL}{note_row}",
         "Savings rate threshold: set this to the minimum savings rate you want to hit each "
         "month. The Annual Overview will flag any month that falls below it.")

    types_label_row = layout["types_label_idx"] + 1
    cell(f"{LABEL_COL}{types_label_row}",
         "Transaction types (used for the Type dropdown on month tabs -- please don't delete)")
    ts = layout["types_start_idx"] + 1
    for i, t in enumerate(["Income", "Bill", "Expense", "Saving", "Debt"]):
        cell(f"{LABEL_COL}{ts + i}", t)

    return values


def build_notes():
    """Cell notes marking sample data. Only one example note is kept (per
    Minnie's feedback -- a note on every sample cell was noisy); the rest of
    the sample values are still populated, just without individual notes."""
    return {
        f"{VALUE_COL}5": "Sample value -- replace with your own.",
    }


def main():
    sheets, _drive = get_services()

    recreate_sheet(sheets)

    requests, layout = build_requests()
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()

    values = build_values(layout)
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": values},
    ).execute()

    # Cell note for the one sample-data example.
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
    print("LABEL_COL:", LABEL_COL, "VALUE_COL:", VALUE_COL)


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
