# The Folio Studio — Spreadsheet Design Brief v2
## Monthly Budget Tracker (Core)

*Revised: July 2026*
*Status: In progress. Supersedes design-brief-monthly-budget-tracker.md (v1) for all sections below.*
*DASHBOARD and TRANSACTIONS architecture confirmed via mockup review. ANNUAL OVERVIEW, GOALS, and SETTINGS still pending review.*

---

## Change log — what changed from v1, and why

| Change | Reason |
|--------|--------|
| Visual language overhauled — see Section 2 | Original amber/hot-pink-heavy treatment tested as "loud" and "corporate" against a competitor audit. Rebuilt around evidence: muted palette, restrained saturated fills, gridlines hidden, hot pink reduced to thin accent lines only. |
| Colour palette expanded with four distinct category hues plus a deep/urgent rose | Amber replaced entirely. See Section 2 for full palette. |
| Sheet background shifted from Pistachio (#EEF3E8) to a warm cream (#FBFAF6) | Matches the muted "editorial planner" tone identified in competitor audit. This is a spreadsheet-specific change — Pistachio remains correct for other brand assets (logo, web, Canva). Flagging since it diverges from v1's stated sheet background colour. |
| Single flat TRANSACTIONS tab replaced with 12 visible month tabs (Jan–Dec) | A full year of transactions in one flat list makes entry cumbersome — this was flagged directly as a functionality requirement, not a preference. Each month tab stays small (roughly 20–60 rows), so scrolling is never a problem. |
| Dropped: hidden tabs, HYPERLINK-based navigation, row-2 insertion, QUERY(), SORT() | Each was tested against actual platform behaviour and found unreliable — see Section 4 for the specific reason each was rejected. |
| SETTINGS theme switcher (Neutral/Fun dropdown) removed | Tab colours cannot be changed by formula or conditional formatting on either platform. Rather than build a partial/misleading switcher, Neutral and Fun ship as two separate files, consistent with how they were always going to become separate Etsy listings anyway. |
| Currency symbol moved from per-cell number formatting to column/card header labels only | Google Sheets' conditional formatting cannot alter number format (Excel's can, asymmetrically) — building dynamic per-cell currency symbols would work in Excel and silently fail in Sheets. Putting the symbol once in each header/label sidesteps the platform gap entirely. |
| Month-tab lookups on DASHBOARD use CHOOSE() instead of INDIRECT() | INDIRECT() resolves by text-matching a tab name — fragile if a tab is ever renamed, and volatile (recalculates on every edit) across 12 tabs feeding a live dashboard, which risks reproducing the "too many tabs, runs slowly" complaint flagged in competitor reviews. CHOOSE() references ranges directly; a broken reference throws a visible #REF! error instead of silently returning zero. |
| No em dashes anywhere in spreadsheet copy | Existing brand voice rule, previously missed in mockup copy. Applies retroactively to all tabs. |

---

## Product overview

**Product name:** Monthly Budget Tracker (Core)
**Cluster:** Finance
**Formats this file serves:** Google Sheets (delivered via PDF link) + Excel (delivered as .xlsx directly)
**Colourways:** Neutral and Fun now ship as **two separate complete files** (not one switchable file — see change log)
**Differentiator:** Properly tested formulas, mobile-conscious layout (bounded per-tab row counts, no INDIRECT-heavy live calculations), genuinely linked tabs, frictionless delivery, warm seller support, polish without being overbuilt.

---

## Section 2 — Visual language (confirmed)

### Palette

| Role | Hex | Usage |
|------|-----|-------|
| Finance green | #3D7A5A | Structural — header bars, section bands, Savings/Income type colour, "good" status |
| Deep rose | #A8495F | Debt type colour, Overdue status, hero card fill (rare, high-emphasis only) |
| Rose pale tint | #F5E6EA (fill) / #A8495F (text) | Upcoming status, caution states |
| Dusty blue | #6F93BE | Bills type/category colour |
| Muted tan | #B89A68 | Expenses type/category colour |
| Hot pink | #FF3366 | Thin border/line accents only — never a fill. Days-left indicator border, headline card left-edge accent line. |
| Near black | #1C1C1A | All text |
| Cream (sheet background) | #FBFAF6 | Page/sheet background — see change log |
| Pale neutral | #F4F2EC | Secondary card fills, non-hero cards |
| Row banding | #FFFFFF / #F7F5EF | Alternating row colours |

### Core rules

- **Gridlines hidden** throughout (View → Show gridlines, off) — a real, one-time toggle in both apps
- **Maximum restraint on solid fills.** Solid colour is reserved for: header/section bands, the one hero metric card, the Overdue status, and category legend swatches. Everything else is pale tint, plain white, or a thin border.
- **Colour bands replace gridlines structurally** — header rows use solid fill with white bold text and no border, doing the visual separation job a gridline would otherwise do.
- **No rounded corners anywhere.** Neither Sheets nor Excel support border-radius on cells. All "cards" are square-cornered merged-cell blocks.
- **Status badges are flat cell fills**, not pills — matches actual conditional-formatting capability on both platforms.
- **Progress indicators:** Excel can use native Data Bar conditional formatting. Google Sheets cannot — use `SPARKLINE(value, {"charttype","bar"})` or a manually built row of coloured segment cells instead. The two files will look slightly different here by necessity.
- **Charts** (donut, clustered bar) are native chart objects on both platforms and accept custom segment colours directly — this is one area with no cross-platform gap.
---

## Section 3 — Tab structure (revised)

| # | Tab name | Visible? | Purpose |
|---|----------|----------|---------|
| 1 | START HERE | Yes | Onboarding — copy updated, see Section 5 |
| 2 | DASHBOARD | Yes | Monthly overview — confirmed, see Section 6 |
| 3–14 | Jan – Dec | Yes, muted grey tab colour | One month's transactions each. Entry at the bottom of the list, plain chronological order. |
| 15 | ANNUAL OVERVIEW | Yes | Year-at-a-glance — formulas updated to sum across all 12 month tabs directly (pending mockup review) |
| 16 | GOALS | Yes | Savings + debt tracker — pending mockup review |
| 17 | SETTINGS | Yes | Configuration — theme switcher removed, currency handling updated, pending mockup review |

Month tabs sit after DASHBOARD in the tab bar, positioned before ANNUAL OVERVIEW/GOALS/SETTINGS, coloured a muted grey to visually deprioritise them relative to the four "hero" tabs.

---

## Section 4 — Rejected approaches (kept for reference, do not revisit)

| Approach | Why it was rejected |
|----------|---------------------|
| Row-2 insertion with everything shifting down | Not achievable via formulas on either platform. Requires a script (Apps Script/VBA) or manual row insertion by the user every time — both fragile, both contradict the "just type, no extra steps" onboarding promise. |
| Hidden month tabs + HYPERLINK() navigation | Google Sheets: hyperlinks to a tab's gid break the moment the file is duplicated, since duplication assigns new gids to every sheet — and duplicating the file for next year is the exact behaviour instructed on START HERE. Excel: hyperlinks generally cannot navigate to a hidden sheet at all. |
| QUERY() for a consolidated transactions view | Google Sheets-only function. Does not exist in Excel. |
| SORT() as a live newest-first formula | Dynamic-array function, requires Excel 365/2021+. Fails silently on older Excel versions, which competitor research already flagged as a real compatibility line buyers hit. |
| INDIRECT() for DASHBOARD's month-tab lookup | Volatile (recalculates on every edit across 12 tabs), and breaks silently (returns zero, not an error) if a tab is ever renamed. |
| SETTINGS theme dropdown switching tab colours | Tab colour is not a formula-addressable property on either platform. |
| Dynamic per-cell currency symbol via conditional formatting | Achievable in Excel, not achievable in Google Sheets (conditional formatting there cannot alter number format) — would ship asymmetric behaviour between the two files. |

---

## Section 5 — START HERE (copy updated)

Step 2 changes from:

> ~~Go to TRANSACTIONS — Log each transaction in row 2. Newest entry always goes at the top, so there's no scrolling.~~

To:

> Go to your current month's tab — Find the tab for this month along the bottom (they're labelled Jan through Dec). Log each transaction in the next empty row. Your Dashboard updates automatically as you go.

All other START HERE content (Step 0 copy-the-file note, Steps 1 and 3, video tutorial block, support block, category quick reference) carries over from v1 unchanged, styled per Section 2's confirmed visual language.

---

## Section 6 — DASHBOARD (confirmed)

Layout, headline cards, breakdown cards, budget table, donut chart, clustered bar chart, and Upcoming Bills block are confirmed as mocked up and reviewed. Two formula-level updates from v1:

- **Month-tab totals use CHOOSE(), not INDIRECT()** — e.g. `SUMIFS(CHOOSE(MonthNumber, Jan!E:E, Feb!E:E, ..., Dec!E:E), ...)`
- **Currency symbol appears in card/column labels only** (e.g. "Left to spend (£)"), never baked into individual numeric cells
---

## Section 7 — Pending

- **ANNUAL OVERVIEW:** formula logic needs rewriting to sum SUMIFS across each of the 12 month tabs directly (additive, not INDIRECT-based), consistent with Section 4's rejection of INDIRECT for this purpose. Visual layout not yet mocked up against Section 2's confirmed palette.
- **GOALS:** not yet mocked up. Savings goal and debt payoff formulas need review for the same cross-tab-reference risks as DASHBOARD.
- **SETTINGS:** theme switcher section to be removed. Currency section to be rewritten around the header-label approach. Category/budget target table layout not yet mocked up against confirmed visual language.
---

*This document is the active source of truth for the Monthly Budget Tracker build, superseding v1 for all sections above. Continue formalising remaining tabs here as each is confirmed.*
