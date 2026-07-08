"""Confirmed v2 spreadsheet palette (design-brief-monthly-budget-tracker-v2.md,
Section 2). Do not add colours outside this set for spreadsheet elements --
that table is the closed, confirmed palette for this build.
"""


def hex_to_rgb(hex_code: str) -> dict:
    hex_code = hex_code.lstrip("#")
    r = int(hex_code[0:2], 16) / 255
    g = int(hex_code[2:4], 16) / 255
    b = int(hex_code[4:6], 16) / 255
    return {"red": r, "green": g, "blue": b}


FINANCE_GREEN = hex_to_rgb("3D7A5A")
DEEP_ROSE = hex_to_rgb("A8495F")
ROSE_PALE_TINT = hex_to_rgb("F5E6EA")
DUSTY_BLUE = hex_to_rgb("6F93BE")
MUTED_TAN = hex_to_rgb("B89A68")
HOT_PINK = hex_to_rgb("FF3366")
NEAR_BLACK = hex_to_rgb("1C1C1A")
CREAM = hex_to_rgb("FBFAF6")
PALE_NEUTRAL = hex_to_rgb("F4F2EC")
ROW_WHITE = hex_to_rgb("FFFFFF")
ROW_TINT = hex_to_rgb("F7F5EF")
WHITE = hex_to_rgb("FFFFFF")

ARIAL_BLACK = "Arial Black"
CALIBRI = "Calibri"
