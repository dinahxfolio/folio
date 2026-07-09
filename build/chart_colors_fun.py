"""Recolour chart series on the Fun copy in place -- fetches each chart's
current spec, swaps only colorStyle.rgbColor on matching series (tolerance-
matched, same reasoning as recolor_cf_fun.py: Sheets quantizes stored RGB to
8-bit), and pushes back the full spec unchanged otherwise via
updateChartSpec. Chart type/domains/series ranges/position/title are never
touched -- colour-only pass.

DASHBOARD's bar chart: Actual series (Finance green) -> Lilac. Budget series
(Pale neutral) is unchanged -- not in Minnie's given palette.
ANNUAL OVERVIEW's column chart: positive series (Finance green) -> Lilac,
negative series (Deep rose) -> Pink.
"""
from auth import get_services
from palette import DEEP_ROSE, DUSTY_BLUE, FINANCE_GREEN
from fun_palette import LILAC, PINK

with open("spreadsheet_id_fun.txt") as f:
    FUN_SPREADSHEET_ID = f.read().strip()

TOLERANCE = 0.02

# DASHBOARD's live "Budget vs Actual" bar chart uses Dusty blue/Hot pink, not
# the Pale-neutral/Finance-green pairing the build script's comments
# describe (a manual tweak made after the script was last run). Per
# Minnie's clarification: Dusty blue -> Lilac here (still follows Finance
# green's structural role-for-role swap), Hot pink is left untouched
# (matches nothing below, since it's not in COLOR_SWAPS -- stays exactly as
# it is, per her "accent-line only" instruction).
COLOR_SWAPS = [
    (FINANCE_GREEN, LILAC),
    (DEEP_ROSE, PINK),
    (DUSTY_BLUE, LILAC),
]


def close(a, b, tol=TOLERANCE):
    return all(abs(a.get(k, 0) - b.get(k, 0)) <= tol for k in ("red", "green", "blue"))


def swap_color(rgb):
    for old, new in COLOR_SWAPS:
        if close(rgb, old):
            return new
    return None


def recolor_charts(sheets, sheet_id, tab_label):
    meta = sheets.spreadsheets().get(
        spreadsheetId=FUN_SPREADSHEET_ID, ranges=[tab_label], fields="sheets(charts(chartId,spec))"
    ).execute()
    charts = meta["sheets"][0].get("charts", [])
    requests = []
    for chart in charts:
        spec = chart["spec"]
        basic = spec.get("basicChart")
        if not basic:
            continue
        changed = False
        for series in basic.get("series", []):
            color_style = series.get("colorStyle", {})
            rgb = color_style.get("rgbColor")
            if rgb is None:
                continue
            new_rgb = swap_color(rgb)
            if new_rgb is not None:
                series["colorStyle"] = {"rgbColor": new_rgb}
                changed = True
        if changed:
            requests.append({
                "updateChartSpec": {
                    "chartId": chart["chartId"],
                    "spec": spec,
                }
            })
    return requests


def main():
    sheets, _drive = get_services()
    requests = []
    requests += recolor_charts(sheets, 200, "DASHBOARD")
    requests += recolor_charts(sheets, 400, "ANNUAL OVERVIEW")

    print(f"{len(requests)} chart recolour requests queued.")
    if requests:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=FUN_SPREADSHEET_ID, body={"requests": requests}
        ).execute()
    print("Chart recolour pass complete.")


if __name__ == "__main__":
    main()
