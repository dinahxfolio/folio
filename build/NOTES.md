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
- Savings goals table (genuine 4-column table, no merges): header row 51 (B=#,
  C=Goal name, D=Target amount formula, E=Target date), data rows 52-59.
- Debt tracker table (3-column table, no merges): header row 62 (B=#, C=Debt name,
  D=Starting balance formula), data rows 63-66. Column E is unused on this table.
- Transaction types helper list (for the Type dropdown on month tabs): `B71:B75`
  = Income, Bill, Expense, Saving, Debt (exact casing from the v1 brief, unchanged by v2).

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

## Decisions this session had to make (not specified by either brief)

- Editable-cell fill: Pale neutral (#F4F2EC) rather than v1's Pistachio, since v2's
  Section 2 palette table is a closed set that no longer includes Pistachio.
- Category divider row colours mapped from v2's palette-table wording: Income/Savings →
  Finance green, Bills → Dusty blue, Expenses → Muted tan, Debt payments → Deep rose.
- Year defaults to 2026 (current year at build time) rather than v1's stated 2025.
