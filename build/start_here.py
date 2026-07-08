"""Build the START HERE tab.

Per v1 Tab 1 + v2 Section 5 (Step 2's copy updated for month tabs; all
other content "carries over from v1 unchanged, styled per Section 2's
confirmed visual language"). v1's technical notes: "All merged cells, no
data columns... No formulas on this tab" -- honoured literally, so the
Category quick reference below is static text matching the SHIPPED
SETTINGS defaults, not a live formula reference (renaming a category in
SETTINGS won't update this page, which is an onboarding reference read
once before customisation, not a live tab).

Two-column layout (Minnie's feedback: the original single full-width
column read too wide). LEFT = steps + video block, RIGHT = support block +
category quick reference, with a blank gutter column between them -- this
also happens to restore v1's original "right column" framing for the
category reference, which an earlier single-column pass had simplified
away.

Category quick reference rows use a ~25%-opacity tint of each category's
colour (same `lighten()` technique as month tabs' Type badges) rather than
the original solid fills, with text switched to the full-strength colour
for contrast -- Minnie's feedback again, applied consistently.

Adds a TIPS section (Minnie's request, not in either brief): where data
entry happens, positive-amounts convention, Balance is calculated not
typed, and date entry. The date tip was reworded from what was asked for:
"enter DD/MM or MM/DD, then change display via Format Cells" isn't
accurate -- Sheets parses a typed date using the spreadsheet's *locale* at
entry time, not a per-cell choice, and Format Cells only changes how an
already-correct date *displays*. Telling a US-locale buyer to type DD/MM
could silently save the wrong date with no way to fix it after the fact
via formatting. Reworded to point buyers at checking their locale instead.
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
    lighten,
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


def row_height(sheets_requests, row_idx, height, end_idx=None):
    sheets_requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": SHEET_ID, "dimension": "ROWS", "startIndex": row_idx,
                      "endIndex": end_idx or row_idx + 1},
            "properties": {"pixelSize": height},
            "fields": "pixelSize",
        }
    })


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

# Two columns with a blank gutter between them.
LEFT_SPAN = (0, 5)     # B:F
RIGHT_SPAN = (7, 12)   # I:M
FULL_SPAN = (0, 12)    # B:M


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
    """Reset cell content/format AND unmerge the whole grid. updateCells
    only touches cell data -- merges are a separate sheet-level property it
    doesn't clear -- so a layout change (like this one, single column ->
    two columns) leaves old merges behind that collide with the new,
    differently-shaped ones ("You must select all cells in a merged range
    to merge or unmerge them")."""
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
        spreadsheetId=SPREADSHEET_ID, ranges=["START HERE"], fields="sheets(conditionalFormats)"
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
    for col, width in widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": SHEET_ID, "dimension": "COLUMNS", "startIndex": col, "endIndex": col + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    # Row 1: hero header (full width).
    hero_r = grid_range(0, 1, *FULL_SPAN)
    requests.append(merge(hero_r))
    requests.append(repeat_cell(hero_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=22,
                                                      bold=True, align="CENTER")))
    row_height(requests, 0, 56)

    # --- LEFT column: step 0, three steps, video block ---
    step0_r = grid_range(2, 3, *LEFT_SPAN)
    requests.append(merge(step0_r))
    requests.append(repeat_cell(step0_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=10,
                                                       italic=True, wrap=True, align="CENTER")))
    row_height(requests, 2, 44)

    for i in range(3):
        r = 4 + i
        step_r = grid_range(r, r + 1, *LEFT_SPAN)
        requests.append(merge(step_r))
        requests.append(repeat_cell(step_r, cell_format(bg=ROW_WHITE, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                          wrap=True)))
        row_height(requests, r, 54)
        requests.append(border_request(step_r, "left", FINANCE_GREEN, width=3))

    video_r = grid_range(8, 10, *LEFT_SPAN)
    requests.append(merge(video_r))
    requests.append(repeat_cell(video_r, cell_format(bg=NEAR_BLACK, fg=WHITE, font=CALIBRI, size=10, bold=True,
                                                       wrap=True, align="CENTER")))
    row_height(requests, 8, 30, end_idx=10)

    # --- RIGHT column: support block, category quick reference ---
    support_r = grid_range(2, 4, *RIGHT_SPAN)
    requests.append(merge(support_r))
    requests.append(repeat_cell(support_r, cell_format(bg=PALE_NEUTRAL, fg=NEAR_BLACK, font=CALIBRI, size=9,
                                                         wrap=True)))
    requests.append(border_request(support_r, "left", FINANCE_GREEN, width=4))
    row_height(requests, 2, 34, end_idx=4)

    band_r = grid_range(5, 6, *RIGHT_SPAN)
    requests.append(merge(band_r))
    requests.append(repeat_cell(band_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=11,
                                                      bold=True)))

    cat_note_r = grid_range(6, 7, *RIGHT_SPAN)
    requests.append(merge(cat_note_r))
    requests.append(repeat_cell(cat_note_r, cell_format(bg=CREAM, fg=NEAR_BLACK, font=CALIBRI, size=8, italic=True,
                                                          wrap=True)))
    row_height(requests, 6, 34)

    # Category rows: ~25%-opacity tint background, full-strength colour text
    # (same pattern as month tabs' Type badges -- solid fills read too
    # strong here too).
    for i, (group_name, color, categories) in enumerate(CATEGORY_GROUPS):
        r = 7 + i
        row_r = grid_range(r, r + 1, *RIGHT_SPAN)
        requests.append(merge(row_r))
        requests.append(repeat_cell(row_r, cell_format(bg=lighten(color, 0.25), fg=color, font=CALIBRI, size=8,
                                                         bold=True, wrap=True)))
        row_height(requests, r, 28)

    # --- Full width: TIPS section, below both columns ---
    tips_band_r = grid_range(12, 13, *FULL_SPAN)
    requests.append(merge(tips_band_r))
    requests.append(repeat_cell(tips_band_r, cell_format(bg=FINANCE_GREEN, fg=WHITE, font=ARIAL_BLACK, size=12,
                                                           bold=True)))

    for i in range(4):
        r = 13 + i
        tip_r = grid_range(r, r + 1, *FULL_SPAN)
        requests.append(merge(tip_r))
        band_bg = CREAM if i % 2 == 0 else PALE_NEUTRAL
        requests.append(repeat_cell(tip_r, cell_format(bg=band_bg, fg=NEAR_BLACK, font=CALIBRI, size=9, wrap=True)))
        row_height(requests, r, 32)

    layout = {}
    return requests, layout


def build_values(layout):
    values = []

    def cell(a1, v):
        values.append({"range": f"'START HERE'!{a1}", "values": [[v]]})

    cell(f"{L(0)}1", "MONTHLY BUDGET TRACKER")

    # LEFT column.
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

    # RIGHT column.
    cell(f"{L(7)}3", "Message me on Etsy and I'll get back to you within 24 hours. No question "
                     "too small. If something isn't working, I want to know.\n-- Dinah")
    cell(f"{L(7)}6", "CATEGORY QUICK REFERENCE")
    cell(f"{L(7)}7", "These are your starting categories. Rename any of them in SETTINGS to "
                     "match how you actually spend. They'll update everywhere automatically.")
    for i, (group_name, _color, categories) in enumerate(CATEGORY_GROUPS):
        r = 8 + i
        cell(f"{L(7)}{r}", f"{group_name}: " + ", ".join(categories))

    # TIPS (full width).
    cell(f"{L(0)}13", "TIPS")
    cell(f"{L(0)}14", "Only SETTINGS and the month tabs (Jan-Dec) need your input. Everything "
                      "else is read only and updates automatically.")
    cell(f"{L(0)}15", "Amounts are always positive. Enter 45.00, always a positive number -- "
                      "the Type column tells the tracker whether it's income or an outgoing.")
    cell(f"{L(0)}16", "Balance fills automatically. Don't type into the Balance column -- it "
                      "calculates itself.")
    cell(f"{L(0)}17", "Dates: type them as DD/MM/YYYY (day first), matching how this sheet "
                      "displays them. If a date looks wrong right after you enter it, check "
                      "your Sheet's locale under File > Settings matches your country -- typing "
                      "a date the wrong way round for your locale can silently save the wrong "
                      "day, and Format Cells only changes how a date displays, not what got saved.")

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
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": values},
    ).execute()

    print("START HERE built.")


if __name__ == "__main__":
    main()
