import pygame

from data.team_registry import TEAM_COLORS
from data.theme import BG_COLOR, HEADER_BG as HEADER_COLOR, TEXT_WHITE, TEXT_GOLD, BORDER_COLOR

ROW_ALT = (15, 40, 95)

# Lazy-init — pygame.font must be ready before we create these
_fonts: dict[str, pygame.font.Font] = {}


def _font(key: str) -> pygame.font.Font:
    if key not in _fonts:
        _fonts.update({
            "lg": pygame.font.SysFont("Arial", 22, bold=True),
            "pl": pygame.font.SysFont("Arial", 20),
            "sm": pygame.font.SysFont("Arial", 14),
        })
    return _fonts[key]


def draw_team_view(screen, rect, match_data, font_title, font_body):
    """Side-by-side squad lists plus officials block at the bottom."""
    lg, pl, sm = _font("lg"), _font("pl"), _font("sm")

    pygame.draw.rect(screen, BG_COLOR, rect, border_radius=12)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 1, border_radius=12)

    if not match_data:
        return

    info    = match_data.get("info", {})
    teams   = info.get("teams", ["Team A", "Team B"])
    players = info.get("players", {})

    col_w = 400
    gap   = 40
    sx = rect.centerx - (col_w * 2 + gap) // 2
    sy = rect.y + 30

    officials_h = 130
    playable_h  = rect.height - 60 - officials_h

    x1, x2 = sx, sx + col_w + gap

    # Team header bars — colored by franchise
    def header(x, name):
        r = pygame.Rect(x, sy, col_w, 50)
        bg = TEAM_COLORS.get(name, (20, 60, 160))
        fg = (0, 0, 0) if name == "Chennai Super Kings" else TEXT_WHITE
        pygame.draw.rect(screen, bg, r, border_top_left_radius=8, border_top_right_radius=8)
        t = lg.render(name.upper(), True, fg)
        screen.blit(t, t.get_rect(center=r.center))

    header(x1, teams[0])
    header(x2, teams[1])

    # Player rows
    y = sy + 50
    row_h = 42
    l1, l2 = players.get(teams[0], []), players.get(teams[1], [])

    for i in range(max(len(l1), len(l2))):
        if y + row_h > sy + playable_h:
            break
        bg = ROW_ALT if i % 2 else BG_COLOR

        pygame.draw.rect(screen, bg, (x1, y, col_w, row_h))
        if i < len(l1):
            screen.blit(pl.render(l1[i], True, TEXT_WHITE), (x1 + 20, y + 10))

        pygame.draw.rect(screen, bg, (x2, y, col_w, row_h))
        if i < len(l2):
            screen.blit(pl.render(l2[i], True, TEXT_WHITE), (x2 + 20, y + 10))
        y += row_h

    # Officials block at the bottom
    off_r = pygame.Rect(rect.x + 20, rect.bottom - officials_h - 20, rect.width - 40, officials_h)
    pygame.draw.rect(screen, (5, 10, 20), off_r, border_radius=8)
    pygame.draw.rect(screen, (40, 50, 70), off_r, 1, border_radius=8)

    lbl = font_title.render("MATCH OFFICIALS", True, TEXT_GOLD)
    screen.blit(lbl, (off_r.centerx - lbl.get_width() // 2, off_r.y + 15))

    officials = info.get("officials", {})
    join = lambda k: ", ".join(officials.get(k, ["-"]))

    oy = off_r.y + 60
    cw = off_r.width // 3
    cx = off_r.x

    for title, names in [("UMPIRES", join("umpires")), ("TV UMPIRE", join("tv_umpires")), ("MATCH REFEREE", join("match_referees"))]:
        ts = sm.render(title, True, (120, 130, 150))
        screen.blit(ts, (cx + (cw - ts.get_width()) // 2, oy - 10))
        ns = pl.render(names, True, TEXT_WHITE)
        screen.blit(ns, (cx + (cw - ns.get_width()) // 2, oy + 15))
        cx += cw