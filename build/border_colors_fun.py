"""Recolour the Fun copy's accent borders in place -- colour-only, same
ranges/widths/styles as the Neutral build, just a different border colour.
Hot pink borders (DASHBOARD's days-left pill, headline hero card) are left
untouched: per Minnie's spec, hot pink "stays exactly as-is, still the thin
accent-line only."

DASHBOARD breakdown-card top borders: Bills/Expenses/Savings/Debt
  Neutral: [Dusty blue, Muted tan, Finance green, Deep rose]
  Fun:     [Blue,       Yellow text, Lilac,        Pink]
  (Yellow has no "full" solid in Minnie's spec -- Yellow text is the only
  Yellow value with enough contrast to read as a border line.)

START HERE: step left-borders and support-block left-border, both Finance
green -> Lilac (Finance green's structural role).
"""
import dashboard as D
import start_here as H
from auth import get_services
from fun_palette import BLUE, LILAC, PINK, YELLOW_TEXT

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()


def border(rng, side, color, width, style="SOLID"):
    return {"updateBorders": {"range": rng, side: {"style": style, "width": width, "color": color}}}


def main():
    requests = []

    # DASHBOARD breakdown-card top borders.
    breakdown_spans = [(0, 3), (3, 6), (6, 9), (9, 12)]
    breakdown_colors = [BLUE, YELLOW_TEXT, LILAC, PINK]
    for (start, end), color in zip(breakdown_spans, breakdown_colors):
        requests.append(border(D.grid_range(7, 10, start, end), "top", color, width=4))

    # START HERE step left-borders (rows 4-6, idx) and support-block
    # left-border (rows 2-4, idx).
    for i in range(3):
        r = 4 + i
        requests.append(border(H.grid_range(r, r + 1, *H.LEFT_SPAN), "left", LILAC, width=3))
    requests.append(border(H.grid_range(2, 4, *H.RIGHT_SPAN), "left", LILAC, width=4))

    print(f"{len(requests)} border recolour requests queued.")
    sheets, _drive = get_services()
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=FUN_SPREADSHEET_ID, body={"requests": requests}
    ).execute()
    print("Border recolour pass complete.")


if __name__ == "__main__":
    main()
