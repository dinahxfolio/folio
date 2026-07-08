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

## SETTINGS cell map (for cross-tab formulas)

- `B5` Your name
- `B6` Year
- `B7` Currency symbol (reference this everywhere a header needs the symbol,
  e.g. `=CONCATENATE("Left to spend (",SETTINGS!B7,")")`)
- `B8` Starting balance
- `B9` Savings rate threshold (fraction, e.g. 0.10 = 10%)
- Category table: category names live in column A, rows 15-19 (Income), 21-27 (Bills),
  29-37 (Expenses), 39-43 (Savings), 45-48 (Debt payments). Budget targets are the
  matching cells in column B. Divider label rows (14, 20, 28, 38, 44) are merged
  A:B and are part of the same contiguous A15:A48 range — that whole range
  (A15:A48) is the intended Data Validation source for the Category dropdown on
  month tabs (flat list with divider rows, per the v2 design brief's rejected-Apps-Script
  decision). Selecting a divider row is a known, accepted tradeoff.
- Savings goals table: header row 51, data rows 52-59 (# / Goal name / Target amount / Target date).
- Debt tracker table: header row 62, data rows 63-66 (# / Debt name / Starting balance).
- Transaction types helper list (for the Type dropdown on month tabs): `A71:A75`
  = Income, Bill, Expense, Saving, Debt (exact casing from the v1 brief, unchanged by v2).

## Palette source of truth

`palette.py` mirrors design-brief-monthly-budget-tracker-v2.md Section 2 exactly. Do not
add colours outside that set for spreadsheet elements.

## Decisions carried from v1 into SETTINGS (not overridden by v2)

- Category/goal/debt default names and counts (5/7/9/5/4 categories, 8 goal slots, 4 debt slots).
- SETTINGS tab colour: near black (1C1C1A) — v2 doesn't touch tab colours except month
  tabs (muted grey).
- Sample data: name "Sarah", starting balance 1,250, marked via cell notes rather than
  a dedicated "SAMPLE" column (SETTINGS' 2-4 column tables have no spare column for a
  literal marker row the way TRANSACTIONS/month tabs will).

## Decisions this session had to make (not specified by either brief)

- Editable-cell fill: Pale neutral (#F4F2EC) rather than v1's Pistachio, since v2's
  Section 2 palette table is a closed set that no longer includes Pistachio.
- Category divider row colours mapped from v2's palette-table wording: Income/Savings →
  Finance green, Bills → Dusty blue, Expenses → Muted tan, Debt payments → Deep rose.
- Year defaults to 2026 (current year at build time) rather than v1's stated 2025.
