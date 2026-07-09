"""Recolour existing conditional-format rules on the Fun copy in place --
condition and range untouched, only the rule's format colours change.

Two matching strategies:
  1. Month-tab Type badges (Income/Bill/Expense/Saving/Debt): matched by the
     rule's condition text, not colour -- Income and Saving currently share
     the *identical* Neutral colour (both derived from Finance green), but
     diverge in Fun (Income -> Blue, Saving -> Lilac), so colour alone can't
     disambiguate them.
  2. Everything else (DASHBOARD/ANNUAL OVERVIEW/GOALS): matched by current
     colour, since there's no such collision there -- every Neutral colour
     pattern maps to exactly one Fun outcome across those three tabs.
"""
from auth import get_services
from palette import DEEP_ROSE, DUSTY_BLUE, FINANCE_GREEN, MUTED_TAN, ROSE_PALE_TINT, WHITE, lighten
from fun_palette import (
    BLUE_PALE, BLUE_TEXT,
    GREEN_PALE, GREEN_TEXT,
    LILAC_PALE, LILAC_TEXT,
    PINK, PINK_PALE, PINK_TEXT,
    YELLOW_PALE, YELLOW_TEXT,
)

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()


TOLERANCE = 0.02  # Sheets quantizes stored colour components; exact-match
                   # after rounding was too strict (saw ~0.004 drift on a
                   # freshly-recomputed lighten() vs what was actually stored).


def close(a, b, tol=TOLERANCE):
    if a is None or b is None:
        return a is b
    return all(abs(a.get(k, 0) - b.get(k, 0)) <= tol for k in ("red", "green", "blue"))


def color_key(fmt):
    bg = fmt.get("backgroundColor")
    fg = fmt.get("textFormat", {}).get("foregroundColor")
    return (bg, fg)


# (bg, fg) pairs (raw color dicts, matched with tolerance) -> (new_bg, new_fg)
# for DASHBOARD/ANNUAL OVERVIEW/GOALS.
COLOR_MAP = [
    (DEEP_ROSE, WHITE, PINK, WHITE),
    (ROSE_PALE_TINT, DEEP_ROSE, YELLOW_PALE, YELLOW_TEXT),
    (None, DEEP_ROSE, None, PINK_TEXT),
    (lighten(FINANCE_GREEN, 0.15), None, LILAC_PALE, None),
    (lighten(FINANCE_GREEN, 0.15), FINANCE_GREEN, LILAC_PALE, LILAC_TEXT),
    (None, FINANCE_GREEN, None, LILAC_TEXT),
]


def find_color_map(bg, fg):
    for old_bg, old_fg, new_bg, new_fg in COLOR_MAP:
        if close(bg, old_bg) and close(fg, old_fg):
            return new_bg, new_fg
    return None

# TEXT_EQ condition value -> (new_bg, new_fg) for month-tab Type badges.
# Income and Bill both mapped to Blue at first, but Minnie asked for them
# to be visually distinct in the dropdown -- Income moved to Green (a
# one-off exception to Green's otherwise "paid status only" scope, per her
# direct request).
TYPE_BADGE_MAP = {
    "Income": (GREEN_PALE, GREEN_TEXT),
    "Bill": (BLUE_PALE, BLUE_TEXT),
    "Expense": (YELLOW_PALE, YELLOW_TEXT),
    "Saving": (LILAC_PALE, LILAC_TEXT),
    "Debt": (PINK_PALE, PINK_TEXT),
}


def build_new_format(old_format, new_bg, new_fg):
    fmt = {}
    if "backgroundColor" in old_format or new_bg is not None:
        fmt["backgroundColor"] = new_bg if new_bg is not None else old_format.get("backgroundColor")
    if "textFormat" in old_format:
        tf = dict(old_format["textFormat"])
        tf.pop("foregroundColorStyle", None)
        if new_fg is not None:
            tf["foregroundColor"] = new_fg
        fmt["textFormat"] = tf
    return fmt


def recolor_sheet_rules(sheets, sheet_id, tab_label, by_condition=False):
    meta = sheets.spreadsheets().get(
        spreadsheetId=FUN_SPREADSHEET_ID, ranges=[tab_label], fields="sheets(conditionalFormats)"
    ).execute()
    rules = meta["sheets"][0].get("conditionalFormats", [])
    requests = []
    unmatched = 0
    for i, rule in enumerate(rules):
        old_format = rule["booleanRule"]["format"]
        new_bg = new_fg = None
        matched = False
        if by_condition:
            cond = rule["booleanRule"]["condition"]
            if cond.get("type") == "TEXT_EQ":
                value = cond["values"][0]["userEnteredValue"]
                if value in TYPE_BADGE_MAP:
                    new_bg, new_fg = TYPE_BADGE_MAP[value]
                    matched = True
        else:
            bg = old_format.get("backgroundColor")
            fg = old_format.get("textFormat", {}).get("foregroundColor")
            result = find_color_map(bg, fg)
            if result is not None:
                new_bg, new_fg = result
                matched = True
        if not matched:
            unmatched += 1
            continue
        new_format = build_new_format(old_format, new_bg, new_fg)
        new_rule = {
            "ranges": rule["ranges"],
            "booleanRule": {"condition": rule["booleanRule"]["condition"], "format": new_format},
        }
        requests.append({
            "updateConditionalFormatRule": {
                "index": i,
                "rule": new_rule,
                "sheetId": sheet_id,
            }
        })
    if unmatched:
        print(f"  WARNING: {unmatched} unmatched rule(s) on {tab_label} -- left unchanged.")
    return requests


def main():
    sheets, _drive = get_services()
    all_requests = []

    all_requests += recolor_sheet_rules(sheets, 200, "DASHBOARD")
    all_requests += recolor_sheet_rules(sheets, 400, "ANNUAL OVERVIEW")
    all_requests += recolor_sheet_rules(sheets, 500, "GOALS")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, m in enumerate(months):
        all_requests += recolor_sheet_rules(sheets, 300 + i, m, by_condition=True)

    print(f"{len(all_requests)} conditional-format recolour requests queued.")
    CHUNK = 150
    for i in range(0, len(all_requests), CHUNK):
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=FUN_SPREADSHEET_ID, body={"requests": all_requests[i:i + CHUNK]}
        ).execute()
    print("Conditional-format recolour pass complete.")


if __name__ == "__main__":
    main()
