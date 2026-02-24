"""
Canonical team data — the one true source for colors, abbreviations, and hex values.

If you need to add a franchise (hello, new expansion team), do it here and
everything downstream picks it up automatically.
"""

from __future__ import annotations

# RGB tuples for Pygame surfaces
TEAM_COLORS: dict[str, tuple[int, int, int]] = {
    "Chennai Super Kings":         (249, 205,   5),
    "Mumbai Indians":              (  0,  75, 160),
    "Royal Challengers Bangalore": (215,  25,  32),
    "Royal Challengers Bengaluru": (215,  25,  32),
    "Kolkata Knight Riders":       ( 58,  34,  93),
    "Rajasthan Royals":            (233,  30,  99),
    "Delhi Capitals":              ( 23,  71, 158),
    "Delhi Daredevils":            ( 23,  71, 158),
    "Sunrisers Hyderabad":         (242, 101,  34),
    "Punjab Kings":                (215,  25,  32),
    "Kings XI Punjab":             (215,  25,  32),
    "Gujarat Titans":              ( 28,  28,  58),
    "Lucknow Super Giants":       (  0,  87, 163),
    "Deccan Chargers":             (  0,  82, 155),
    "Pune Warriors":               (  0,  58, 143),
    "Pune Warriors India":         (  0,  58, 143),
    "Rising Pune Supergiant":      (108,  29,  69),
    "Rising Pune Supergiants":     (108,  29,  69),
    "Gujarat Lions":               (230,  74,  25),
    "Kochi Tuskers Kerala":        (123,  31, 162),
}

# Auto-generated hex versions for matplotlib — no manual sync needed
TEAM_COLORS_HEX: dict[str, str] = {
    name: "#{:02X}{:02X}{:02X}".format(*rgb)
    for name, rgb in TEAM_COLORS.items()
}

# Short codes for tight UI spaces (scoreboards, tables)
TEAM_ABBR: dict[str, str] = {
    "Royal Challengers Bangalore": "RCB",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders":       "KKR",
    "Chennai Super Kings":         "CSK",
    "Mumbai Indians":              "MI",
    "Rajasthan Royals":            "RR",
    "Kings XI Punjab":             "KXIP",
    "Punjab Kings":                "PBKS",
    "Delhi Daredevils":            "DD",
    "Delhi Capitals":              "DC",
    "Sunrisers Hyderabad":         "SRH",
    "Deccan Chargers":             "DCG",
    "Gujarat Titans":              "GT",
    "Lucknow Super Giants":        "LSG",
    "Gujarat Lions":               "GL",
    "Kochi Tuskers Kerala":        "KTK",
    "Rising Pune Supergiants":     "RPS",
    "Rising Pune Supergiant":      "RPS",
    "Pune Warriors India":         "PWI",
    "Pune Warriors":               "PWI",
}

_FALLBACK_RGB = (30, 40, 60)
_FALLBACK_HEX = "#333333"


def get_team_color(name: str) -> tuple[int, int, int]:
    return TEAM_COLORS.get(name, _FALLBACK_RGB)


def get_team_hex(name: str) -> str:
    return TEAM_COLORS_HEX.get(name, _FALLBACK_HEX)


def abbreviate_team(name: str) -> str:
    return TEAM_ABBR.get(name, name)
