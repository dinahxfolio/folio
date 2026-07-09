"""Fun colourway palette -- exact hexes as specified by Minnie. Role-for-role
replacement of the Neutral palette (see palette.py). Unlike Neutral, Green and
Yellow have no "full" solid variant -- they're deliberately scoped to narrow
status uses only ("nowhere else"), so anywhere a full/solid fill would be
needed for an Expenses or Paid-status element, the pale tint + dark text
combo is used instead (this changes those specific elements from
solid-fill-white-text to pale-fill-dark-text, a deliberate style break from
the other four category groups, which keep solid fills).
"""
from palette import hex_to_rgb

LILAC = hex_to_rgb("B39DDB")
LILAC_PALE = hex_to_rgb("EAE2F7")
LILAC_TEXT = hex_to_rgb("5A4A7A")

PINK = hex_to_rgb("E8829E")
PINK_PALE = hex_to_rgb("FBE0EC")
PINK_TEXT = hex_to_rgb("7A3555")

BLUE = hex_to_rgb("7FA8D9")
BLUE_PALE = hex_to_rgb("E1EBFA")
BLUE_TEXT = hex_to_rgb("2C4A70")

GREEN_PALE = hex_to_rgb("E4F0E6")
GREEN_TEXT = hex_to_rgb("3D6B45")

YELLOW_PALE = hex_to_rgb("FBF0D0")
YELLOW_TEXT = hex_to_rgb("8A7020")

HOT_PINK = hex_to_rgb("FF3366")  # unchanged, thin accent-line only
