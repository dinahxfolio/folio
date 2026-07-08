# The Folio Studio — Spreadsheet Build Process

*For use at the start of every new spreadsheet product build*
*Claude should follow this process before writing any code*

---

## Purpose

This document ensures every spreadsheet is designed before it is built. Claude must complete the Design Brief with the user before generating any Python or openpyxl code. No exceptions.

---

## Brand Standards for Spreadsheets

### Fonts
Brand fonts (Syne, DM Sans) are NOT used in spreadsheets. Customers will not have these installed. Use system-safe substitutes only.

| Brand font | Spreadsheet substitute | Usage |
|------------|----------------------|-------|
| Syne ExtraBold | Arial Black | Tab titles, section headers, hero text |
| DM Sans | Calibri | All body copy, column headers, data, labels |

**Rule:** Arial Black for display moments — tab titles, section headers, any text that needs weight and presence. Calibri for everything functional — column headers, data, labels, notes.

**Why these fonts:** Arial Black is the closest system font to Syne's geometric weight and character. Calibri is universally installed across Windows and Mac and renders cleanly at small sizes. Georgia and Aptos were considered — Georgia was retired because it's a serif with no visual relationship to the brand; Aptos is cleaner but not yet reliably installed on all customer machines.

### Colour Palette (hex codes)
Use brand colours for fills, headers and accents. All are safe as hex fills in Excel/Sheets.

**Main palette**

| Name | Hex | Spreadsheet usage |
|------|-----|-------------------|
| Pistachio | EEF3E8 | Primary background, alternating rows (light) |
| Lilac | EDE0F5 | Home cluster background, secondary fills |
| Hot pink | FF3366 | Accent highlights, status indicators, key values |
| Teal | 3A9090 | Sensitive product accents (fertility, sobriety, wellness) |
| Near black | 1C1C1A | All body text, headers |
| White | FFFFFF | Alternating rows, clean fills |

**Cluster colours**

| Cluster | Full colour hex | Pale tint hex | Usage |
|---------|----------------|---------------|-------|
| Finance | 3D7A5A | C8E8D8 | Header rows, tab colour, alternating tint |
| Home | 9080C0 | E0DCF5 | Header rows, tab colour, alternating tint |
| Wellness | E07858 | FAE0D8 | Header rows, tab colour, alternating tint |
| Food | D4A028 | F5EAC0 | Header rows, tab colour, alternating tint |
| Travel | 5888C8 | C8DCF5 | Header rows, tab colour, alternating tint |
| Personal Dev | D4608C | F5D4E4 | Header rows, tab colour, alternating tint |

### Tab colour coding
Assign tab colours consistently using the full cluster colour (not the pale tint):
- Finance tabs → Dark green (3D7A5A)
- Home tabs → Purple (9080C0)
- Wellness tabs → Terracotta (E07858)
- Food tabs → Amber (D4A028)
- Travel tabs → Blue (5888C8)
- Personal Development tabs → Bubblegum pink (D4608C)
- Summary/Dashboard tabs → Near black (1C1C1A)
---

## Pre-Build Design Brief

Claude must ask and confirm answers to ALL of the following before writing any code.

### Step 1 — Tab structure
- What tabs does this spreadsheet need?
- What is the primary purpose of each tab?
- Are any tabs optional or phase 2?

### Step 2 — Per-tab layout (repeat for each tab)
Ask these questions for every tab:

**Above the fold**
- What is the single most important thing the user needs to see first on this tab?
- Should there be a summary/totals block? If yes, where does it sit — top right beside the title, below the title, or at the bottom?
- Should any rows or columns be frozen?

**Data structure**
- What are the columns and in what order?
- Which columns have dropdown validation? What are the options?
- Which columns have formulas? What should they calculate?
- Are there any columns that reference data from other tabs?

**Visual hierarchy**
- Which rows are headers? What background colour?
- Should rows alternate in colour? Which two colours?
- Are there any columns that should be colour-coded by value (e.g. status columns)?

**Size and space**
- Approximate column widths for key columns?
- Any merged cells needed?
- Any rows that need extra height (e.g. title rows)?

### Step 3 — Charts
- Does this spreadsheet need any charts?
- If yes: what data should each chart show?
- Where should each chart live — inline on the relevant tab, or on a dedicated Charts tab?
- What chart type — pie, bar, line?

### Step 4 — Sample data
- Should sample data be included to show how the sheet works?
- If yes: how many sample rows?
- Should sample data be clearly marked so the user knows to delete it?

### Step 5 — Confirm with a wireframe
Before writing any code, Claude produces a simple text wireframe for each tab showing the layout. The user approves or adjusts before building begins.

**Wireframe format:**

```
TAB NAME
─────────────────────────────────────────────────
[ TITLE                    ] [ SUMMARY BLOCK     ]
[ subtitle / instructions                        ]
─────────────────────────────────────────────────
[ Col A header ] [ Col B ] [ Col C ] [ Col D    ]
[ data row     ] [ ...   ] [ ...   ] [ ...      ]
[ data row     ] [ ...   ] [ ...   ] [ ...      ]
─────────────────────────────────────────────────
[ CHART (if any)                                 ]
─────────────────────────────────────────────────
```

---

## Build Standards

### Formulas
- Always use Excel formulas, never Python calculations hardcoded as values
- Test all cross-tab references carefully — use exact sheet names in quotes
- Protect against divide-by-zero with IFERROR wrappers
- Summary totals use SUMIF/COUNTIF, not SUM of a smaller hardcoded range

### Validation
- All status columns get dropdown validation
- All date columns get DD/MM/YYYY number format
- All currency columns get £#,##0.00 number format
- All percentage columns get 0.00% format

### After building
- Always run scripts/recalc.py to validate
- Fix all errors before presenting the file
- Status must be "success" with zero errors before delivery
---

## Chart Standards

### When to use each chart type
- **Pie chart** — share of a total (income by category, sales by cluster, expenses breakdown)
- **Bar chart** — comparison across categories or time (monthly revenue, products by status)
- **Line chart** — trends over time (monthly revenue trend, Pinterest growth)

### Chart colours
Use brand palette colours in this order for chart segments/bars:
1. Deep sage — 3A5C3E
2. Mustard — D4A830
3. Dusty coral — C97B6E
4. Sage — 7A9E7E
5. Powder pink — ECC8C0
6. Deep warm brown — 2C1810

### Chart placement
- Charts on their own Charts tab unless the user specifies inline
- Charts tab gets deep warm brown tab colour (2C1810)
- Each chart has a clear title in Georgia Bold
- Legend always included
---

## Delivery Checklist

Before presenting the file to the user:

- [ ] All tabs built as per approved wireframe
- [ ] Correct fonts used throughout (Georgia / Calibri only)
- [ ] Brand colour palette applied correctly
- [ ] All dropdowns validated
- [ ] All formulas correct — no hardcoded Python calculations
- [ ] recalc.py run and returns status: success, zero errors
- [ ] Sample data present and clearly marked if requested
- [ ] File saved to /mnt/user-data/outputs/
---

*This document is the single source of truth for spreadsheet build process at The Folio Studio.*
*Update it whenever new standards or decisions are made.*
