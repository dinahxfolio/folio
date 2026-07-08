"""Build the START HERE tab.

Per v1 Tab 1 + v2 Section 5 (Step 2's copy updated for month tabs; all
other content "carries over from v1 unchanged, styled per Section 2's
confirmed visual language"). v1's technical notes: "All merged cells, no
data columns... No formulas on this tab" -- honoured literally, so the
Category quick reference below is static text matching the SHIPPED
SETTINGS defaults, not a live formula reference (renaming a category in
SETTINGS won't update this page, which is an onboarding reference read
once before customisation, not a live tab).

Simplification from v1: the brief describes the Category quick reference
as sitting in a "right column" alongside the steps/video/support blocks
(implying a two-column layout with mismatched row-heights per column).
Stacked as a single full-width flow instead (steps -> video -> support ->
category reference, top to bottom) -- much simpler merge geometry, reads
fine as a single-column onboarding page, and avoids inventing arbitrary
row-height math to make two independent-height columns align.
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
    ROW_WHITE,
    WHITE,
)

SHEET_ID = 600
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
                 italic=False, align="LEFT", valign="MIDDLE", wrap=False):
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
    return fmt


def repeat_cell(rng, fmt, fields="userEnteredFormat"):
    return {"repeatCell": {"range": rng, "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def merge(rng, merge_type="MERGE_ALL"):
    return {"mergeCells": {"range": rng, "mergeType": merge_type}}


def border_request(rng, side, color, width=3, style="SOLID"):
    return {"updateBorders": {"range": rng, side: {"style": style, "width": width, "color": color}}}


CATEGORY_GROUPS = [
    ("INCOME", FINANCE_GREEN, ["Salary / Wages", "Freelance", "Side hustle", "Bonus", "Other income"]),
    ("BILLS", DUSTY_BLUE, ["Rent / Mortgage", "Electricity", "Gas / Water", "Internet", "Phone",
                            "Insurance", "Subscriptions"]),
    ("EXPENSES", MUTED_TAN, ["Groceries", "Dining out", "Transport", "Health", "Clothing",
                              "Entertainment", "Personal care", "Gifts", "Miscellaneous"]),
    ("SAVINGS", FINANCE_GREEN, ["Emergency fund", "Holiday", "House deposit", "Retirement",
                                 "Other savings"]),
    ("DEBT PAYMENTS", DEEP_ROSE, ["Credit card", "Student loan", "Personal loan", "Car finance"]),
]


def recreate_sheet(sheets):
    """Create-only-if-missing -- see build/NOTES.md on delete+recreate
    breaking cross-sheet formula references."""
    meta = sheets.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    exists = any(s["properties"]["sheetId"] == SHEET_ID for s in meta["sheets"])
    if exists:
        return

    requests = [{"addSheet": {"properties": {"sheetId": 999995, "title": "__temp5__"}}}]
    requests.append({
        "addSheet": {
            "properties": {
                "sheetId": SHEET_ID,
                "title": "START HERE",
                "index": 0,  # v2 Section 3's confirmed tab order puts this first
                "gridProperties": {"rowCount": 30, "columnCount": 15, "hideGridlines": True},
                "tabColor": FINANCE_GREEN,
            }
        }
    })
    requests.append({"deleteSheet": {"sheetId": 999995}})
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
    ).execute()


def clear_sheet_content(sheets):
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "updateCells": {
                "range": {"sheetId": SHEET_ID, "startRowIndex": 0, "endRowIndex": 30,
                          "startColumnIndex": 0, "endColumnIndex": 15},
                "fields": "*",
            }
        }]},
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
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: hero header.
    hero_r = grid_range(0, 1, 0, 12)
    requests.append(merge(hero_r))
    requests.append(repeat_cell(hero_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=22,
                                                      bold=True, align="CENTER")))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 56},
            "fields": "pixelSize",
        }
    })

    # Row 3 (idx 2): Step 0 note.
    step0_r = grid_range(2, 3, 0, 12)
    requests.append(merge(step0_r))
    requests.append(repeat_cell(step0_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                       italic=True, wrap=True, align="CENTER")))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 2, "endIndex": 3},
            "properties": {"pixelSize": 34},
            "fields": "pixelSize",
        }
    })

    # Rows 5-7 (idx 4-6): three numbered steps.
    for i in range(3):
        r = 4 + i
        step_r = grid_range(r, r + 1, 0, 12)
        requests.append(merge(step_r))
        requests.append(repeat_cell(step_r, cell_format(bg=ROW_WHITE, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                          wrap=True)))
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": r, "endIndex": r + 1},
                "properties": {"pixelSize": 34},
                "fields": "pixelSize",
            }
        })
        requests.append(border_request(step_r, "left", FINANCE_GREEN, width=3))

    # Rows 9-10 (idx 8-9): video tutorial block, dark background.
    video_r = grid_range(8, 10, 0, 12)
    requests.append(merge(video_r))
    requests.append(repeat_cell(video_r, cell_format(bg=NEAR_BLACK, fg=WHITE, font=CALIBRI, size=11, bold=True,
                                                       wrap=True, align="CENTER")))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 8, "endIndex": 10},
            "properties": {"pixelSize": 30},
            "fields": "pixelSize",
        }
    })

    # Rows 12-13 (idx 11-12): support block.
    support_r = grid_range(11, 13, 0, 12)
    requests.append(merge(support_r))
    requests.append(repeat_cell(support_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                         wrap=True)))
    requests.append(border_request(support_r, "left", FINANCE_GREEN, width=4))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 11, "endIndex": 13},
            "properties": {"pixelSize": 30},
            "fields": "pixelSize",
        }
    })

    # Row 15 (idx 14): CATEGORY QUICK REFERENCE band.
    band_r = grid_range(14, 15, 0, 12)
    requests.append(merge(band_r))
    requests.append(repeat_cell(band_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=12,
                                                      bold=True)))

    # Row 16 (idx 15): note.
    cat_note_r = grid_range(15, 16, 0, 12)
    requests.append(merge(cat_note_r))
    requests.append(repeat_cell(cat_note_r, cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=9, italic=True,
                                                          wrap=True)))
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": 15, "endIndex": 16},
            "properties": {"pixelSize": 28},
            "fields": "pixelSize",
        }
    })

    # Rows 17-21 (idx 16-20): one row per category group.
    for i, (group_name, color, categories) in enumerate(CATEGORY_GROUPS):
        r = 16 + i
        row_r = grid_range(r, r + 1, 0, 12)
        requests.append(merge(row_r))
        requests.append(repeat_cell(row_r, cell_format(bg=color, fg=WHITE, font=CALIBRI, size=9, wrap=True)))
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": r, "endIndex": r + 1},
                "properties": {"pixelSize": 26},
                "fields": "pixelSize",
            }
        })

    layout = {}
    return requests, layout


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"'START HERE'!{a1}", "values": [[v]]})

    cell(f"{L(0)}1", "MONTHLY BUDGET TRACKER")
    cell(f"{L(0)}3", "Before you begin, make a copy of this file and keep it somewhere safe. "
                     "That's your blank template for next year.")

    cell(f"{L(0)}5", "1. Go to SETTINGS -- Set your currency symbol, your name, and customise "
                     "your budget categories to match how you actually spend. Takes about two "
                     "minutes.")
    cell(f"{L(0)}6", "2. Go to your current month's tab -- Find the tab for this month along "
                     "the bottom (they're labelled Jan through Dec). Log each transaction in "
                     "the next empty row. Your Dashboard updates automatically as you go.")
    cell(f"{L(0)}7", "3. Go to DASHBOARD -- Select your month from the dropdown. See your full "
                     "picture: what's in, what's out, what's left, all in one place.")

    cell(f"{L(0)}9", "▶ Full walkthrough -- 6 minutes\nWatch on YouTube →")

    cell(f"{L(0)}12", "Message me on Etsy and I'll get back to you within 24 hours. No question "
                      "too small. If something isn't working, I want to know.\n-- Dinah")

    cell(f"{L(0)}15", "CATEGORY QUICK REFERENCE")
    cell(f"{L(0)}16", "These are your starting categories. Rename any of them in SETTINGS to "
                      "match how you actually spend. They'll update everywhere automatically.")

    for i, (group_name, _color, categories) in enumerate(CATEGORY_GROUPS):
        r = 17 + i
        cell(f"{L(0)}{r}", f"{group_name}: " + ", ".join(categories))

    return values


def main():
    sheets, _drive = get_services()

    recreate_sheet(sheets)
    clear_sheet_content(sheets)

    requests, layout = build_requests()
    CHUNK = 400
    for i in range(0, len(requests), CHUNK):
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": requests[i:i + CHUNK]}
        ).execute()

    values = build_values(layout)
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": values},
    ).execute()

    print("START HERE built.")


if __name__ == "__main__":
    main()
