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
  targets are the matching cells in column D (merged D:E). Divider label rows
  (14, 20, 28, 38, 44) are merged B:E and are part of the same contiguous B15:B48
  range — that whole range (B15:B48) is the intended Data Validation source for
  the Category dropdown on month tabs (flat list with divider rows, per the v2
  design brief's rejected-Apps-Script decision). Selecting a divider row is a
  known, accepted tradeoff.
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

## Decisions this session had to make (not specified by either brief)

- Editable-cell fill: Pale neutral (#F4F2EC) rather than v1's Pistachio, since v2's
  Section 2 palette table is a closed set that no longer includes Pistachio.
- Category divider row colours mapped from v2's palette-table wording: Income/Savings →
  Finance green, Bills → Dusty blue, Expenses → Muted tan, Debt payments → Deep rose.
- Year defaults to 2026 (current year at build time) rather than v1's stated 2025.
