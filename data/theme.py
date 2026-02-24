"""
TV-broadcast color palette.

Every module that draws UI chrome imports from here.  If you change a color
here it propagates everywhere — that's the whole point.
"""

from __future__ import annotations

# The deep navy → electric blue spectrum that gives the app its broadcast feel
TV_BLUE_DARK  = ( 10,  30,  80)
TV_BLUE_MID   = ( 20,  60, 160)
TV_BLUE_LIGHT = ( 40,  90, 200)
TV_BLUE_ALT   = ( 15,  40,  95)

TV_GOLD       = (240, 200,  50)
TV_WHITE      = (245, 245, 255)
TV_SILVER     = (200, 200, 210)
TV_TEXT_DARK   = ( 20,  20,  25)

TV_RED        = (200,  40,  40)
TV_ORANGE     = (200, 100,  50)
TV_GREY_LIGHT = (220, 220, 230)

# Convenience aliases — these read better at call sites
BG_COLOR      = TV_BLUE_DARK
HEADER_BG     = TV_BLUE_MID
BORDER_COLOR  = TV_SILVER
DIVIDER_COLOR = (100, 100, 120)
TEXT_WHITE     = TV_WHITE
TEXT_GOLD      = TV_GOLD
TEXT_BLACK     = TV_TEXT_DARK
ROW_A         = ( 15,  35,  70)
ROW_B         = ( 20,  45,  90)

# Panel chrome
SECTION_COLOR = (200, 220, 255)
LABEL_COLOR   = (180, 180, 190)

PANEL_RADIUS  = 12
PANEL_PAD_X   = 18
PANEL_PAD_Y   = 14
COL_GAP       = 20
ROW_GAP       = 8
