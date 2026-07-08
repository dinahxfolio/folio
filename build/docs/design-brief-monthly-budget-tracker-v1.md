# The Folio Studio — Spreadsheet Design Brief
## Monthly Budget Tracker (Core)

*Completed: July 2026*
*Status: Approved. Ready to build.*
*Refer to this document throughout the build. Do not write any code until this brief is complete.*

---

## Product overview

**Product name:** Monthly Budget Tracker (Core)
**Cluster:** Finance
**Formats this file serves:** Google Sheets (delivered via PDF link) + Excel (delivered as .xlsx directly)
**Colourways:** Neutral (this build) + Fun (second colourway, switchable via SETTINGS dropdown)
**Differentiator:** Properly tested formulas, mobile-conscious layout, genuinely linked tabs, frictionless delivery, warm seller support. Design being beautiful is why they click. Product working correctly is why they leave five stars.

---

## Brand standards

### Fonts
| Role | Font | Usage |
|------|------|-------|
| Display / headers | Arial Black | Tab title bars, section headers, hero text |
| Body / functional | Calibri | Column headers, data cells, labels, notes, instructions |

### Colours
| Name | Hex | Usage |
|------|-----|-------|
| Finance green | 3D7A5A | Header bars, section headers, progress fills, tab colours |
| Finance tint | C8E8D8 | Alternating rows, month dividers, tints, background fills |
| Near black | 1C1C1A | Body text, column headers, SETTINGS tab header |
| Pistachio | EEF3E8 | Sheet background, editable cell fills |
| Hot pink | FF3366 | Debt progress, over-budget indicators, accent |
| Amber | D4A028 | Left to spend headline card, near-budget warnings, current month |
| White | FFFFFF | Card backgrounds, alternating rows |

### Tab colours
All tabs: Finance green (3D7A5A)
SETTINGS tab only: Near black (1C1C1A)

---

## Tab structure

| # | Tab name | Purpose | Opens by default |
|---|----------|---------|-----------------|
| 1 | START HERE | Welcome, setup instructions, tutorial link, category reference | Excel version only |
| 2 | DASHBOARD | Monthly overview — month selector, headline numbers, budget vs actual, charts | Google Sheets version |
| 3 | TRANSACTIONS | Full year transaction log, newest first, feeds all other tabs | Never |
| 4 | ANNUAL OVERVIEW | 12-month summary, best/worst month callouts, annual bar chart | Never |
| 5 | GOALS | Savings goals (8 cards) + debt payoff tracker, linked to transactions | Never |
| 6 | SETTINGS | All configuration — name, year, currency, categories, goals, debts, theme | Never |

**Critical behaviour:** SETTINGS is the source of truth for all category names and budget targets. Every other tab references SETTINGS, never its own hardcoded values.

---

## Tab 1 — START HERE

### Purpose
Onboarding tab. Replaces the need for a separate instruction document in the Excel version. Google Sheets version opens on DASHBOARD instead, but START HERE is still included for buyers who navigate to it.

### Layout

**Row 1 — Hero header**
- Background: Finance green (3D7A5A)
- Title: "Monthly Budget Tracker" in Arial Black, white, uppercase, large
- No eyebrow / branding line — this is the buyer's tracker, not a product page
- No tagline

**Row 2 — Step 0 (copy before step)**
Before you begin, make a copy of this file and keep it somewhere safe. That's your blank template for next year.

**Rows 3–5 — Three numbered steps**
1. Go to SETTINGS — Set your currency symbol, your name, and customise your budget categories to match how you actually spend. Takes about two minutes.
2. Go to TRANSACTIONS — Log each transaction in row 2. Newest entry always goes at the top, so there's no scrolling. Your Dashboard updates automatically as you go.
3. Go to DASHBOARD — Select your month from the dropdown. See your full picture — what's in, what's out, what's left, all in one place.

**Video tutorial block**
- Dark background card
- YouTube icon
- "Full walkthrough — 6 minutes"
- "Watch on YouTube →" (link added once video is made)

**Support block**
- Pistachio background, Finance green left border
- "Message me on Etsy and I'll get back to you within 24 hours. No question too small. If something isn't working, I want to know."
- First person throughout — Dinah, not a team

**Category quick reference (right column)**
- Note: "These are your starting categories. Rename any of them in SETTINGS to match how you actually spend. They'll update everywhere automatically."
- Four groups: Income / Bills / Expenses / Savings / Debt
- Default names listed (see SETTINGS section below for full list)

### Technical notes
- All merged cells, no data columns
- Tab colour: Finance green
- No formulas on this tab
---

## Tab 2 — DASHBOARD

### Purpose
The hero tab. Read-only except for the Budget Target column. All data pulls from TRANSACTIONS. Month selector controls which month is displayed.

### Layout — above the fold

**Header bar (Finance green background)**
- Left: "Dashboard" in Arial Black, white, uppercase
- Right: Month selector dropdown (e.g. "November 2025") + Days left pill in hot pink

**Headline numbers — three cards**
- Card 1 (amber background, larger): Left to Spend — total remaining across all categories this month
- Card 2 (white): Total Income — actual vs budgeted subtitle
- Card 3 (white): Total Spent — actual vs budgeted subtitle

**Left to spend breakdown — four cards**
One card per category group: Bills / Expenses / Savings / Debt
Each shows: amount left, of X budgeted
Top border colour matches category type:
- Bills: Travel blue (5888C8)
- Expenses: Amber (D4A028)
- Savings: Finance green (3D7A5A)
- Debt: Hot pink (FF3366)

**Transactions note (Finance tint background)**
"Actuals update automatically. To log a transaction, go to the TRANSACTIONS tab and enter in row 2. Newest entries always go at the top."

### Layout — budget vs actual table

**Column headers (Finance green background):**
Category / Budget Target / Actual / Difference / Progress

**Rows:**
- Category group sub-headers (light green background, uppercase, small)
- One row per category
- Budget Target column: editable (pistachio fill, Finance green border, Finance green text) — this is the only column the user types into on this tab
- Budget targets carry forward from previous month automatically
- Actual column: pulls from TRANSACTIONS via SUMIFS
- Difference column: Budget minus Actual (positive = under budget, negative = over)
- Progress bar: colour coded
  - Under 80% of budget used: Finance green
  - 80–99% of budget used: Amber
  - Over 100%: Hot pink/red
- Total row (Finance tint background) at bottom

### Layout — charts (inline, below table)

**Chart 1: Spending breakdown donut**
- Shows actual spend split by category group (Bills / Expenses / Savings / Debt)
- Colours: Bills = Travel blue, Expenses = Amber, Savings = Finance green, Debt = Hot pink
- Total spent in centre of donut

**Chart 2: Budget vs actual bar chart**
- Horizontal bars, one per category
- Light tint bar = budget, coloured fill = actual
- Same colour coding as progress bars (green/amber/red)
- Legend below

### Frozen rows
- Row 1 (header bar): frozen
- Columns A–B: frozen

### Tab colour: Finance green

---

## Tab 3 — TRANSACTIONS

### Purpose
The data entry engine. Every transaction for the full year goes here. All other tabs pull from this tab via SUMIFS formulas. User never needs to go anywhere else to enter data.

### Column structure

| Col | Header | Input type | Notes |
|-----|--------|------------|-------|
| A | Date | Manual, date format DD/MM/YYYY | |
| B | Description | Manual, free text | |
| C | Type | Dropdown | Income / Bill / Expense / Saving / Debt |
| D | Category | Dropdown | Filtered by Type selection, options from SETTINGS |
| E | Amount | Manual, currency format | Always entered as positive number |
| F | Balance | Formula, locked | Running balance, cumulative from starting balance in SETTINGS |
| G | Notes | Manual, free text | Optional |

### Key behaviours
- **Newest first:** Row 2 is always the input row. New entries go in row 2, previous entries push down. Header row frozen.
- **Linked dropdowns:** Category dropdown in column D filters based on Type selected in column C. If Type = Expense, only expense categories appear.
- **Running balance:** Column F = previous balance ± current transaction amount. Income adds, all other types subtract.
- **Income vs expense logic:** Amount is always entered as a positive number. The formula in Balance determines whether to add or subtract based on Type.

### Visual structure
- Header bar: Finance green, "Transactions" in Arial Black, white. Instruction note: "Enter each transaction in row 2. Newest first. Dashboard updates automatically."
- Column headers: Near black background, white text
- Input row (row 2): Amber dashed bottom border, pistachio background, placeholder text in muted colour
- Balance column: Locked appearance — light grey background, auto label in input row
- Type badges: Colour coded pills per type
  - Income: Finance green
  - Bill: Travel blue (5888C8)
  - Expense: Amber
  - Saving: Home purple (9080C0)
  - Debt: Hot pink
- Month divider rows: Finance tint background, Finance green border top and bottom, month name in Arial Black uppercase
- Alternating row colours: White / #FAFAF8

### Tab colour: Finance green

---

## Tab 4 — ANNUAL OVERVIEW

### Purpose
Read-only year-at-a-glance view. January to December fixed structure regardless of when the user starts. All data pulls from TRANSACTIONS via SUMIFS by month.

### Layout

**Header bar:** Finance green, "Annual Overview — [YEAR]" in Arial Black. Note: "Read only. Updates automatically from your transactions."

**Best / Worst callouts — two cards**
- Best month: auto-identifies the month with the highest left-over amount. Trophy emoji, month name in Arial Black, value.
- Tightest month: auto-identifies the month with the lowest (or most negative) left-over amount. Chart emoji, month name, value.
- Both pull automatically from the grid below.

**Annual grid**
Columns: Row label / Jan / Feb / Mar / Apr / May / Jun / Jul / Aug / Sep / Oct / Nov / Dec / Total

Rows:
1. Income — sum of all income transactions that month
2. Bills — sum of all bill transactions that month
3. Expenses — sum of all expense transactions that month
4. Savings — sum of all saving transactions that month
5. Debt payments — sum of all debt transactions that month
6. [Spacer row — Finance tint background]
7. Left over — Income minus all outgoings
8. Savings rate % — Savings divided by Income

**Visual behaviour:**
- Current month column: Amber highlight across header and cells
- Future months with no data: Show dash (—) not zero
- Left over row: Finance tint background
- Left over positive values: Finance green text
- Left over negative values: Red text
- Savings rate below threshold (set in SETTINGS): Amber text
- Total column: Light green background, Finance green text

**Bar chart — monthly left over**
- 12 bars, one per month
- Positive months: Finance green bars
- Negative months: Red bars
- Current month: Amber bar
- Future months: Light grey placeholder bars
- Legend below

### Tab colour: Finance green

---

## Tab 5 — GOALS

### Purpose
Savings progress and debt payoff tracker. All progress data pulls automatically from TRANSACTIONS — user sets up goal names and targets in SETTINGS, then this tab does the rest.

### Layout

**Header bar:** Finance green, "Goals" in Arial Black. Note: "Progress updates automatically from your transactions."

**Summary headlines — two cards**
- Total saved across all goals: Finance green accent, sum of all savings transactions mapped to goals
- Total debt remaining: Hot pink accent, sum of starting balances minus all debt payments

**Section 1 — Savings goals**
8 cards in a 4×2 grid. Each card shows:
- Goal name (from SETTINGS)
- Amount saved so far (pulls from TRANSACTIONS, category matched)
- Target amount (from SETTINGS)
- Progress bar (Finance green fill)
- Target date (entered in SETTINGS)
- Amount remaining

Progress bar colour:
- Under 50%: Light sage green
- 50–89%: Amber
- 90–99%: Finance green
- 100%: Finance green, checkmark badge, "Reached [month year]" instead of remaining amount

Empty goal slots: Dashed border, "Add a goal in Settings" placeholder text

**Section 2 — Debt payoff**
Table layout. Columns:
- Debt name (from SETTINGS)
- Starting balance (from SETTINGS, editable)
- Paid off (auto, pulls from TRANSACTIONS)
- Remaining (auto, starting balance minus paid off)
- Monthly payment (editable — user enters expected monthly payment)
- Progress bar (hot pink fill)
- Est. payoff date (auto-calculated from remaining balance and monthly payment)

Payoff date colour coding:
- Under 12 months: Finance green
- 12–24 months: Amber
- Over 24 months: Amber

Empty debt rows: Faded/muted appearance with placeholder text

### Tab colour: Finance green

---

## Tab 6 — SETTINGS

### Purpose
Single configuration tab. User sets everything here once. All other tabs reference SETTINGS. Nothing is hardcoded elsewhere.

### Layout

**Header bar:** Near black background (unique to this tab), "Settings" in Arial Black, white. Note: "Set up once. Everything updates automatically."

**Instruction note**
"Start here before using any other tab. Fill in your name, year, currency, and starting balance first, then set your monthly budget targets by category. Your goals and debt names go at the bottom. You only need to do this once. targets carry forward each month automatically."

**Section 1 — General (left column)**
| Setting | Default |
|---------|---------|
| Your name | [blank] |
| Year | 2025 |
| Currency symbol | $ |
| Starting balance | [blank] |
| Savings rate threshold | 10% |

**Section 2 — Colour theme (right column)**
Dropdown with two options: Neutral / Fun
- Neutral: Pistachio background, Finance green accents, near black text
- Fun: Finance tint background, hot pink accents, Finance green headers
Switching theme updates colours across all tabs automatically via conditional formatting rules.
Small colour swatch preview beside each option.

**Section 3 — Monthly budget targets**
Two-column table spanning full width. Grouped by type: Income / Bills / Expenses / Savings / Debt payments.
Columns: Category name / Monthly budget target

**Note above the table:** "Category names are fully editable. Change any name here and it updates across the whole spreadsheet — the transaction dropdowns, the dashboard, and the annual overview all update automatically."

Default categories:

Income: Salary / Wages, Freelance, Side hustle, Bonus, Other income
Bills: Rent / Mortgage, Electricity, Gas / Water, Internet, Phone, Insurance, Subscriptions
Expenses: Groceries, Dining out, Transport, Health, Clothing, Entertainment, Personal care, Gifts, Miscellaneous
Savings: Emergency fund, Holiday, House deposit, Retirement, Other savings
Debt payments: Credit card, Student loan, Personal loan, Car finance

**Section 4 — Savings goal names**
8 rows. Columns: Number / Goal name / Target amount / Target date
All user-editable. Feed the Goals tab cards.

**Section 5 — Debt names**
4 rows. Columns: Number / Debt name / Starting balance
All user-editable. Feed the Goals tab debt table.

**Amber note below debt section:**
"Savings rate threshold: Set this to the minimum savings rate you want to hit each month. The Annual Overview will highlight any month that falls below it in amber."

### Tab colour: Near black (1C1C1A)

---

## Formula logic summary

### TRANSACTIONS tab
- Column F (Balance): `=IF(C2="Income", F3+E2, F3-E2)` — adds income, subtracts everything else
- Starting balance seed: pulls from SETTINGS!B4

### DASHBOARD tab
- Actual values: `=SUMIFS(TRANSACTIONS!E:E, TRANSACTIONS!D:D, [category], TRANSACTIONS!month_col, [selected month])`
- Left to spend per group: Budget target minus actual
- Progress %: Actual divided by budget target (IFERROR wrapper for divide by zero)
- Days left: `=EOMONTH([selected month],0) - TODAY()`

### ANNUAL OVERVIEW tab
- Each cell: `=SUMIFS(TRANSACTIONS!E:E, TRANSACTIONS!type_col, [type], TRANSACTIONS!month_col, [month number])`
- Left over: Income minus Bills minus Expenses minus Savings minus Debt
- Savings rate: Savings divided by Income
- Best month: `=INDEX(month_names, MATCH(MAX(leftover_row), leftover_row, 0))`
- Worst month: `=INDEX(month_names, MATCH(MIN(leftover_row), leftover_row, 0))`

### GOALS tab
- Saved so far: `=SUMIFS(TRANSACTIONS!E:E, TRANSACTIONS!D:D, [goal category name])`
- Debt paid off: `=SUMIFS(TRANSACTIONS!E:E, TRANSACTIONS!D:D, [debt category name])`
- Est. payoff date: `=EDATE(TODAY(), CEILING(remaining/monthly_payment, 1))`
---

## Sample data

Include sample data clearly marked for deletion.
- TRANSACTIONS: 12 rows across 2 months (Nov and Oct), covering all 5 transaction types
- SETTINGS: Pre-filled with example values (Sarah, $, 2025, $1,250 starting balance)
- GOALS: 4 goals filled, 4 empty; 2 debts filled, 2 empty
- All sample data rows highlighted in a distinct tint with a note in column A: "SAMPLE — delete this row"
---

## Delivery checklist

Before presenting the file:

- [ ] All 6 tabs built as per approved wireframes above
- [ ] Arial Black used for all display moments, Calibri for all functional copy
- [ ] Finance green (3D7A5A) applied to all tab colours except SETTINGS
- [ ] SETTINGS tab colour: Near black (1C1C1A)
- [ ] All dropdowns validated — Type and Category linked dropdowns working
- [ ] All formulas correct — no hardcoded Python calculations
- [ ] IFERROR wrappers on all divide-by-zero risk formulas
- [ ] Running balance formula working correctly (income adds, all else subtracts)
- [ ] Month divider rows appearing correctly in TRANSACTIONS
- [ ] Best/worst month callouts pulling correctly in ANNUAL OVERVIEW
- [ ] Goals progress pulling from TRANSACTIONS correctly
- [ ] Debt payoff estimator calculating correctly
- [ ] Theme switcher in SETTINGS changes colours across all tabs
- [ ] Sample data present and clearly marked
- [ ] Duplicate file instruction on START HERE tab
- [ ] recalc.py run — status: success, zero errors
- [ ] File saved to /mnt/user-data/outputs/
---

*This brief is the single source of truth for the Monthly Budget Tracker build.*
*Do not begin coding until all sections above are confirmed.*
*Refer back when writing Etsy listing copy — the feature list here is the basis for the listing description.*
