# Monthly Budget Tracker — build notes

Spreadsheet: https://docs.google.com/spreadsheets/d/1Xmhxkg3mvzMCbFF_cXHaoPgYB4iJi2A48UJPIvRNaKE/edit
Spreadsheet ID is also in `spreadsheet_id.txt` (gitignored is not needed, it's just an ID, not a secret).

Auth: OAuth installed-app flow (see `auth.py`). Token lives outside the repo at the path
in `FOLIO_SHEETS_TOKEN` (default: session scratchpad `token.json`). Never commit tokens
or client secrets.

## Sheet ID convention

| Tab | sheetId |
|-----|---------|
| SETTINGS | 100 |
| DASHBOARD | 200 |
| Jan..Dec | 300-311 |
| ANNUAL OVERVIEW | 400 |
| GOALS | 500 |

## Column convention (applies to every tab, not just SETTINGS)

Column A is a blank padding column on every tab — content never starts before
column B. This was added after the first SETTINGS review. When building
DASHBOARD, month tabs, ANNUAL OVERVIEW, and GOALS, reserve column A the same
way (narrow width, ~28px, base sheet-background fill, no content).

## SETTINGS cell map (for cross-tab formulas)

SETTINGS also merges 2-column label/value pairs so the General and Monthly
Budget Targets sections fill the same 4-column (B:E) width as the section
bands above them: label merged B:C, value merged D:E, so the value's address
is the top-left cell of that merge (column D), not column C.

- `B5` Your name label / `D5` value
- `B6` Year label / `D6` value
- `B7` Currency symbol label / `D7` value (reference `SETTINGS!D7` everywhere
  a header needs the symbol, e.g. `=CONCATENATE("Left to spend (",SETTINGS!D7,")")`)
- `B8` Starting balance label / `D8` value
- `B9` Savings rate threshold label / `D9` value (fraction, e.g. 0.10 = 10%)
- Category table: category names live in column B (merged B:C), rows 15-19 (Income),
  21-27 (Bills), 29-37 (Expenses), 39-43 (Savings), 45-48 (Debt payments). Budget
  targets are in column D (single cell, not merged). Column E holds "Due day"
  (day of month, 1-31) but only for the 7 Bills rows (21-27) -- feeds DASHBOARD's
  Upcoming Bills block. Divider label rows (14, 20, 28, 38, 44) are merged B:E
  and are part of the same contiguous **B14:B48** range (the divider row itself
  is row 14, so the range must start there, not at row 15) — that whole range
  is the Data Validation source used for the Category dropdown on month tabs
  (flat list with divider rows, per the v2 design brief's rejected-Apps-Script
  decision). Selecting a divider row is a known, accepted tradeoff.
- Savings goals table (genuine 4-column table, no merges): note row 51 (goal
  name must match a Category name, see below), header row 52 (B=#, C=Goal
  name, D=Target amount formula, E=Target date), data rows 53-60. Sample
  goals are the 5 real Savings category names (Emergency fund, Holiday,
  House deposit, Retirement, Other savings), not arbitrary names, since
  GOALS tracks progress via an exact Category-name match (see the "GOALS
  design gap" entry below).
- Debt tracker table (3-column table, no merges): header row 63 (B=#, C=Debt name,
  D=Starting balance formula), data rows 64-67. Column E is unused on this table.
- Transaction types helper list (for the Type dropdown on month tabs): `B72:B76`
  = Income, Bill, Expense, Saving, Debt (exact casing from the v1 brief, unchanged by v2).
  **These row numbers moved once already** (were B71:B75) when a note row was
  inserted above the Savings Goals table -- if SETTINGS' layout changes again,
  re-check every hardcoded SETTINGS row reference in month_tabs.py/dashboard.py/
  annual_overview.py, not just the ones that seem related.

## Palette source of truth

`palette.py` mirrors design-brief-monthly-budget-tracker-v2.md Section 2 exactly. Do not
add colours outside that set for spreadsheet elements.

## Decisions carried from v1 into SETTINGS (not overridden by v2)

- Category/goal/debt default names and counts (5/7/9/5/4 categories, 8 goal slots, 4 debt slots).
- SETTINGS tab colour: near black (1C1C1A) — v2 doesn't touch tab colours except month
  tabs (muted grey).
- Sample data: name "Sarah", starting balance 1,250, etc. Only one cell (`D5`, the
  sample name) carries an explanatory note, per Minnie's feedback that a note on
  every sample cell was noisy — the rest of the sample values are populated but
  unannotated.

## DASHBOARD dependencies and decisions

- DASHBOARD's month-lookup formulas (CHOOSE over Jan!..Dec!) need the month
  tabs to exist to be verifiable, so month tabs (Jan-Dec) are being built
  before DASHBOARD, not after.
- DASHBOARD's "Upcoming Bills" block (mentioned as confirmed-via-mockup in the
  v2 brief, Section 6) is not actually described in either brief's text --
  the mockup itself specified it and isn't available here. Minnie confirmed:
  show Bill-type categories with no matching transaction logged yet this
  month, sorted by soonest due day. This required adding the Due day field
  to SETTINGS above, since nothing in the original data model captured a due
  date.

## Month tabs (Jan-Dec, sheetIds 300-311)

Built per v2 Section 3/4/5: 12 visible tabs, muted grey tab colour, chronological
entry at the bottom (not the old newest-first/row-2-insertion model), no HYPERLINK
navigation, no INDIRECT.

Columns (padding convention applies, A blank): B Date | C Description | D Type |
E Category | F Amount ($) | G Balance ($) | H Notes. Row 1 = month title (B1:D1)
+ Opening balance pill (E1:H1). Row 2 = instruction note. Row 3 = column headers.
Rows 4-48 = 45 transaction rows. Column I holds a small "closing balance" helper
(I1) -- visible, not hidden, with an explanatory cell note.

Type dropdown source: `SETTINGS!$B$71:$B$75`. Category dropdown source:
`SETTINGS!$B$14:$B$48` (the whole flat range, dividers included). Both are strict
(reject values outside the list) since DASHBOARD/ANNUAL OVERVIEW's SUMIFS need
exact text matches. Amount has a NUMBER_GREATER 0 validation. Type cells get
conditional-formatting colour badges matching SETTINGS' divider colours
(Income/Saving = Finance green, Bill = Dusty blue, Expense = Muted tan,
Debt = Deep rose).

### Running balance across 12 separate tabs

Splitting one flat TRANSACTIONS tab into 12 month tabs means the running balance
has to hop from one tab's last row into the next tab's first row. Implementation:

- Each month has a small numeric helper cell **I1** ("closing balance"):
  `=IF(COUNTA($D$4:$D$48)=0, <this month's own opening value>, INDEX($G$4:$G$48, COUNTA($D$4:$D$48)))`
- Each month's **opening value** is a single hop: `SETTINGS!$D$8` for Jan, or
  `<PreviousMonth>!$I$1` for every other month.
- The visible "Opening: $X" pill and the first data row's Balance formula both
  reference this same opening value.

This two-part design (rather than one nested lookup) exists because of two bugs
caught only by reading calculated values back, not by the API accepting the
request:

1. **The classic "last value in a range" idiom fails silently here.**
   `=LOOKUP(2,1/(range<>""),range)` is a standard Excel/Sheets trick for finding
   the last non-blank cell in a range, but in Google Sheets it returned `#N/A`
   for this exact use (the `1/(range<>"")` division isn't auto-arrayed without
   an explicit `ARRAYFORMULA` wrapper). Replaced with `COUNTA` + `INDEX`, which
   needs no array wrapper.
2. **`INDEX(range, 0)` is not an error.** When a month has zero transactions,
   `COUNTA` is 0, and naively wrapping `INDEX(range, 0)` in `IFERROR` doesn't
   help -- `INDEX(range, 0)` returns the *entire range* as a reference rather
   than erroring, which breaks silently when coerced into text/arithmetic. A
   month with zero transactions must fall back to *its own opening value*
   (which may itself be inherited from further back), not to a hardcoded
   `IFERROR(...) -> SETTINGS starting balance`, or every empty month would
   incorrectly reset the running balance to the year's starting balance
   instead of carrying forward whatever it actually was. Verified by checking
   Mar (empty) and onward all the way to Dec: all correctly carry Feb's actual
   closing balance rather than resetting.
3. **Locale-ambiguous date strings get silently misparsed.** Sample dates
   written as `"02/01/2026"` (intended as 2 January, DD/MM) were read by
   Sheets' `USER_ENTERED` input as MM/DD (1 February) under the spreadsheet's
   default locale -- the cell's `dd/mm/yyyy` *display* format does nothing to
   protect the *input* parse. Fixed by writing sample dates in ISO format
   (`"2026-01-02"`), which parses unambiguously regardless of locale; the
   `dd/mm/yyyy` number format still controls how it displays.

All three were caught by reading FORMATTED_VALUE and UNFORMATTED_VALUE back
across the whole Jan-Dec chain, not by the batchUpdate/values.update calls
succeeding without error.

## DASHBOARD (sheetId 200)

Built per v1 Tab 2 + v2 Section 6. Content columns B-M (12, so the 3-card
headline row and 4-card breakdown row both divide evenly), helper cells in
P-T (MonthNumber, and a small ranking table for Upcoming Bills), with an
explanatory note on each helper, same pattern as month tabs' I1.

- Month selector (G1, dropdown Jan-Dec) drives `MonthNumber` (P1,
  `=MATCH(G1,{"Jan",...,"Dec"},0)`), which every CHOOSE() formula on the tab
  uses, e.g. `SUMIFS(CHOOSE(P$1,Jan!$F$4:$F$48,...),CHOOSE(P$1,Jan!$E$4:$E$48,...),category)`.
  Verified by switching the selector to Feb and confirming every headline/
  breakdown number changed to match Feb's actual sample transactions, not
  just that Jan's numbers happened to look right.
- Budget Target column is a **live reference to SETTINGS** (`=SETTINGS!$D$15`
  etc.), not an independently editable/carried-forward value the way v1's
  DASHBOARD section describes -- v1's own higher-priority rule ("SETTINGS is
  the source of truth... every other tab references SETTINGS, never its own
  hardcoded values") wins over that section's specific wording, and the
  per-month-editable-target design doesn't fit a single shared SETTINGS table
  anyway. v2 doesn't revisit this.
- Progress column uses `SPARKLINE(MIN(actual/target,1),{"charttype","bar";...})`
  per v2's explicit guidance for Sheets (Excel would use native Data Bars).
  **Caveat:** SPARKLINE cells return no readable value via the Sheets API
  (values.get returns nothing for them, formula-only) -- so unlike every
  other formula in this build, its output could not be verified by reading
  a calculated value back, only by confirming the underlying ratio inputs
  (Actual/Target columns) are individually correct, and that IFERROR
  suppresses the 0/0 case (Freelance, target=0) without an error string
  leaking into FORMATTED_VALUE. Worth a visual check in the Sheet itself.
- Progress colour coding (conditional formatting, not the sparkline colour):
  <80% = no rule (base Finance green sparkline), 80-99% = Rose pale tint
  fill, >=100% = Deep rose solid fill. Not v1's green/amber/red -- amber
  doesn't exist in v2's palette, and hot pink is confirmed border/line-only,
  so it cannot be the over-budget fill either.
- Hero card ("Left to spend") uses Deep rose solid fill -- v2's palette
  table explicitly names Deep rose for "hero card fill (rare, high-emphasis
  only)", replacing v1's amber. Hot pink appears only as a thin left-edge
  border accent on the hero card and the days-left pill, per v2's "border/
  line accents only" rule.
- Upcoming Bills block (spec not in either brief -- see the DASHBOARD
  dependencies section above) ranks the 7 Bills categories by due day using
  COUNTIFS (paid-this-month check) + SMALL/INDEX/MATCH with a tiny
  position-based tie-breaker (`due_day + i*0.0001`), not SORT()/FILTER().
  The brief's SORT() rejection was specifically about Excel-version
  compatibility for a different, now-obsolete feature (the flat newest-first
  TRANSACTIONS view); it doesn't transfer to this Sheets-only block, but
  SMALL/INDEX/MATCH was used anyway to stay consistent with the brief's
  general preference for classic, non-dynamic-array functions. Verified
  against Jan's sample data: Rent and Electricity (paid in Jan's sample
  transactions) correctly excluded; the remaining 5 unpaid bills appear
  sorted 1, 1, 5, 10, 18 by due day.
- "Days left" pill always reflects days left in the *actual* current month
  (`EOMONTH(TODAY(),0)-TODAY()`), not the month selected for review -- v1's
  literal formula only makes sense when the selected month is the current
  one; showing e.g. "-40 days left" while reviewing a past month would be
  confusing and wasn't the evident intent.

### Charts

Donut (spending breakdown, U:V helper table) and horizontal bar (budget vs
actual, W:Y helper table) charts sit below the total row. Both charts read
from small gap-free helper blocks rather than the visible budget table
directly, because the Sheets API rejects multi-range chart sources unless
each range is contiguous ("each sourceRange across the domain & series must
be in order and contiguous") -- the real budget table has divider rows
breaking every group's rows apart, which fails that check. W:X:Y is a
25-row mirror (7 Bills + 9 Expenses + 5 Savings + 4 Debt) that just
references the already-computed budget-table cells, so there's no new
calculation, only a chart-friendly reshaping of it. Verified the donut/bar
data ranges resolve to the correct Jan totals and that both `addChart`
requests came back with the expected `chartId`s.

### Post-review fixes (round 2)

Minnie's review of DASHBOARD surfaced several real issues:

1. **Month tabs were broken** ("no longer work"). Root cause: the same
   delete+recreate-breaks-cross-sheet-references bug described below also
   hit the month tabs' data validation (Type/Category dropdowns reference
   `SETTINGS!...`) and Balance-chain formulas (`SETTINGS!$D$8` for Jan's
   seed), since settings_tab.py's old delete+recreate ran *after* month_tabs.py
   had already built those references. Fixed by re-running month_tabs.py
   (now safe, since it no longer deletes existing sheets) to re-write the
   formula/validation text with fresh bindings. Confirmed repaired by reading
   Jan!E1/I1/G4 back (previously `#REF!`, now calculating correctly again).
2. **Two section bands had no text.** `section_band()` only applied merge +
   fill colour + font; nothing ever wrote "UPCOMING BILLS" (row 12) or
   "MONTHLY BUDGET" (row 22) into the merged cell, so the bands rendered as
   empty coloured strips. Same gap existed for the Upcoming Bills column
   headers (row 13: Category/Amount/Due day) and the budget table's column
   headers (row 23: Category/Budget/Actual/Diff./Progress) -- formatting was
   built for all of these, the label text was not. All four now populated.
3. **Layout**: the Monthly Budget table (rows 22 down) narrowed from B:M
   (12 cols) to B:H (7 cols) -- Category (B:D, 3 cols) / Budget (E) /
   Actual (F) / Diff. (G) / Progress (H) -- freeing I:M for the charts,
   which now sit beside the table (stacked vertically: donut at row 22,
   bar chart ~row 37) instead of anchored below everything. Rows 1-20
   (header, headline cards, breakdown cards, Upcoming Bills) stay full
   12-column width -- only the budget table section narrowed, per the
   specific ask.
4. **Chart colours.** The bar chart's two series now use explicit brand
   colours (Budget = Pale neutral, Actual = Finance green) via
   `colorStyle`. The donut chart's slice colours could **not** be changed
   the same way: `PieChartSpec` in the Sheets API has no field for
   per-slice colour (only `legendPosition`/`domain`/`series`/
   `threeDimensional`/`pieHole` exist) -- this is a hard platform
   limitation, not something left undone. If matching brand colours on the
   donut matters enough, the alternative is swapping it for a 100%-stacked
   bar (which does support per-series colour) at the cost of no longer
   being donut-shaped; flagged to Minnie rather than silently choosing
   either option.
5. **"Thicker lines" on the bar chart.** The Charts API has no bar-
   thickness/gap-width field to set directly. Increased the chart's pixel
   height substantially (320px -> 700px for 25 categories) instead, which
   is the only available lever -- more vertical room per category makes
   Sheets render each bar thicker.

### Post-review fixes (round 3)

Minnie asked for the month tabs' Type badge colours to be lighter (~20-30%
opacity of the originals). Sheets fills have no real alpha channel, so
`palette.lighten(color, alpha)` simulates it by blending toward white
(`color*alpha + white*(1-alpha)`, alpha=0.25). Badge text switched from
white to the full-strength type colour, since white loses contrast against
the now much lighter fill.

This also surfaced a duplicate-rule bug: re-running month_tabs.py on
already-existing sheets (the normal, safe path now) calls
`addConditionalFormatRule` again without removing the old rules first, so
a previous repair run had silently left 10 rules per month tab (5 old +
5 new) instead of 5. Added `clear_conditional_formats()` to delete all
existing rules on each month sheet before adding fresh ones. Confirmed via
`conditionalFormats` count (10 -> 5 per tab) and reading back the actual
rule colours (background = 25%-blend, text = full-strength, matching the
`lighten()` math).

## ANNUAL OVERVIEW (sheetId 400)

Built per v1 Tab 4 + v2 Section 7 ("SUMIFS across each of the 12 month tabs
directly -- additive, not INDIRECT-based"; visual layout wasn't mocked up,
so v1's layout carries over with v2's palette substituted, same remapping
pattern as DASHBOARD). Columns: B = row label, C:N = Jan..Dec, O = Total.
Each month's cell is its own direct `SUMIFS(<month>!Amount, <month>!Type,
"<type>")` -- no CHOOSE needed here since all 12 months display
simultaneously (CHOOSE was for DASHBOARD's single-selected-month lookup).

- Best/Tightest month cards use `INDEX(month_names, MATCH(MAX/MIN(leftover_row),...))`.
  `MAX`/`MIN` automatically skip the `"--"` text placeholders for months
  with no transactions yet, so no data yet is naturally excluded from
  contention without extra logic. Verified against Jan/Feb's sample data:
  Feb ($2,212 left over) correctly wins Best, Jan ($1,789.50) Tightest.
- Palette remapping (same pattern as DASHBOARD): v1's amber current-month
  highlight -> Pale neutral background (closest confirmed "light emphasis"
  colour; hot pink can't be a fill). v1's "red" for negative left-over /
  below-threshold savings rate -> Deep rose (v2's designated negative/
  caution colour throughout). v1's "light green" Total column ->
  `lighten(FINANCE_GREEN, 0.15)` (v2's palette has no explicit Finance-green
  pale tint, so this reuses the same `lighten()` helper added for the
  month-tab Type badges).
- Bar chart colours bars by sign via two series (Positive/Negative helper
  columns, Q/R) rather than per-point styling, same technique as
  DASHBOARD's bar chart needing a workaround for a per-point limitation --
  charts colour by series, not by individual bar/slice. No distinct
  "current month" bar colour or "future month" grey placeholder bar was
  implemented (no per-point styling available, and a third series felt
  like too much complexity for a cosmetic detail) -- flagging this
  simplification rather than silently dropping it.

### Two more Sheets API limitations discovered here

1. **Conditional format `CUSTOM_FORMULA` conditions cannot reference another
   sheet at all** -- confirmed empirically: `=C16<SETTINGS!$D$9` is rejected
   outright by the API (not just unsupported in some edge case). The
   Savings rate row's below-threshold conditional formatting needs to
   compare against `SETTINGS!$D$9`, so a same-sheet mirror cell (`T1`,
   `=SETTINGS!$D$9`) exists purely so the conditional format has a
   same-sheet cell to reference.
2. **A chart's domain and series must share the same row/column
   orientation.** The grid header (row 8, Jan..Dec horizontally) couldn't
   be used as the bar chart's domain because the Positive/Negative helper
   columns are vertical (12 rows) -- the API rejects mixing a 1-row domain
   with 12-row series ("ChartSourceRange ranges require all rows or all
   columns to have length of 1" was the error, which undersells the actual
   constraint). Added a vertical month-name helper column (`U1:U12`) to
   match the series' orientation instead.

### Duplicate-rule bug recurs here too -- and gets its general fix

The same "re-running a build script on an already-existing sheet stacks
duplicate rules/charts instead of replacing them" bug (first found with
month tabs' Type badges) hit both the conditional format rules (42 stacked
up in one debugging session, should have been 14) and the embedded chart
(2 identical "Monthly left over" charts) here too. Fixed with
`clear_conditional_formats()` and `clear_charts()`, called at the top of
`main()` before their respective `build_requests()`/`build_charts()` calls
-- same pattern as month_tabs.py's fix, now applied consistently. **Any
future tab script (GOALS) that adds conditional formats or charts needs
this same clear-before-add pattern from the start**, not bolted on after
a duplicate is discovered.

### Critical lesson: never delete+recreate a sheet other tabs already reference

Building DASHBOARD (which formula-references SETTINGS and the month tabs)
after re-running settings_tab.py exposed a serious bug: settings_tab.py and
month_tabs.py both used a delete-then-recreate pattern (needed early on to
avoid stale merges/formatting from earlier layout iterations). Once DASHBOARD
existed with formulas like `=SETTINGS!$D$15`, re-running settings_tab.py
(which deletes sheetId 100 and adds a new sheet back with the *identical*
sheetId and title "SETTINGS") broke every one of those formulas with
`#REF! (Unresolved sheet name 'SETTINGS')` -- even though a sheet named
SETTINGS still existed immediately afterwards with the same ID. Google
Sheets evidently binds cross-sheet formula references to an internal sheet
identity that a delete+recreate invalidates regardless of matching
sheetId/title. Re-running dashboard.py's values.batchUpdate (re-writing the
same formula text) repaired it, since that creates fresh bindings against
the sheet that currently exists.

Fix applied: `recreate_sheet()`/`recreate_month_sheets()` in settings_tab.py
and month_tabs.py now only **add** a sheet if it doesn't exist yet, and
never delete+recreate one that already exists -- build_requests()/
build_values() already overwrite the full grid's formatting and content on
every run, which is sufficient since each tab's shape only ever grows
additively. dashboard.py still uses delete+recreate for now since nothing
references DASHBOARD yet (ANNUAL OVERVIEW/GOALS will reference SETTINGS and
the month tabs directly, not DASHBOARD) -- flagged in its own docstring to
switch to the same safe pattern if that ever changes.

A side effect of the temp-sheet dance across separate script runs also
scrambled the tab bar order (Jan ended up before DASHBOARD, SETTINGS at the
very end) -- fixed with an explicit batch of `updateSheetProperties`
(`index`) requests in the desired left-to-right order. Confirmed final order:
SETTINGS, DASHBOARD, Jan..Dec.

## GOALS design gap resolved before building

v1's GOALS tab pulls "amount saved so far" from transactions "category
matched" against each Savings Goal's name. But SETTINGS' sample Goals
("Emergency fund (3 months)", "Dream holiday", "New laptop", "Wedding
fund") didn't actually match any value in the Category dropdown (which
only has the 5 fixed Savings categories: Emergency fund, Holiday, House
deposit, Retirement, Other savings) -- "New laptop" and "Wedding fund"
aren't selectable categories at all, so there was nothing for a SUMIFS to
match against.

Resolved (Minnie confirmed): **goal name must exactly match a Category
name.** A goal tracks automatically only if its name equals one of the 5
Savings categories (the user can rename a category to match a custom goal,
e.g. rename "Other savings" to "Wedding fund"). SETTINGS' sample goals
now use the 5 real category names directly (rows 53-57), and a note was
added above the Goals table explaining the linkage requirement. This
inserted one new row into SETTINGS (a note row, matching the pattern
already used for Monthly Budget Targets), which shifted every row after it
down by one -- see the "SETTINGS row-shift" entry below for what that broke
and how it was caught.

### SETTINGS row-shift fallout (and the general fix)

Inserting that note row shifted SETTINGS' Savings Goals (52-59 -> 53-60),
Debt Tracker (62-66 -> 63-67), and Transaction Types helper list (71-75 ->
72-76) down by one row each. This broke month_tabs.py's hardcoded Type
dropdown source (`SETTINGS!$B$71:$B$75`, now wrong by one row) -- fixed to
`$B$72:$B$76`. DASHBOARD and ANNUAL OVERVIEW were unaffected since their
SETTINGS references (category rows 15-48, general settings rows 5-9) all
sit *before* the insertion point.

This also surfaced a **new class of bug, distinct from the delete+recreate
one**: build_values() only ever writes to a layout's *current* row
positions, so when a row insertion shifts the layout, whatever used to
occupy the old positions is never explicitly overwritten and is left
behind as a stale duplicate (confirmed: the old "Transaction types..."
label stayed at row 70 after the new layout moved it to row 71, so both
70 and 71 showed the label text). Fixed generally with
`clear_sheet_content()` in settings_tab.py -- resets every cell's value/
format/note/validation across the whole grid (via `updateCells` with
`fields: "*"` and no `rows`, which clears rather than writes) before
rebuilding. This is safe to run even with other tabs holding live formula
references to SETTINGS, since it clears cell *content*, not the sheet
itself -- unlike the delete+recreate pattern, which breaks those
references (see below). **Any tab script that can have its row layout
change between runs should clear its own sheet's content first**, the
same way month_tabs.py/annual_overview.py now clear conditional formats/
charts first for the equivalent reason.

## Decisions this session had to make (not specified by either brief)

- Editable-cell fill: Pale neutral (#F4F2EC) rather than v1's Pistachio, since v2's
  Section 2 palette table is a closed set that no longer includes Pistachio.
- Category divider row colours mapped from v2's palette-table wording: Income/Savings →
  Finance green, Bills → Dusty blue, Expenses → Muted tan, Debt payments → Deep rose.
- Year defaults to 2026 (current year at build time) rather than v1's stated 2025.
