import pygame
import math

from data.field_tactics import FIELD_TACTICS
from data.team_colors import TEAM_COLORS

YARD_M = 0.9144   # yards → metres conversion factor

# Lazy-init — pygame must be ready before we create Font objects
_fonts: dict[str, pygame.font.Font] = {}


def _font(key: str) -> pygame.font.Font:
    if key not in _fonts:
        _fonts.update({
            "label": pygame.font.SysFont("JetBrainsMono NF", 11),
            "arc":   pygame.font.SysFont("JetBrainsMono NF", 16, bold=True),
        })
    return _fonts[key]


def _attr(obj, name):
    """Uniform accessor — works on both dicts and dataclass-style objects."""
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


def _striker(event):
    return _attr(event, "striker") or _attr(event, "batter")


def _pick_tactic(over, powerplay):
    if powerplay and over <= int(powerplay.get("to", 6)):
        return "powerplay_1"
    return "death_overs" if over >= 16 else "ring_defense"


def _fielding_xi(match, team, bowler):
    """Return (wicket-keeper, outfielders) minus the bowler."""
    squad = match["info"]["players"].get(team, []).copy()
    if bowler in squad:
        squad.remove(bowler)

    # Crude WK detection by name convention — good enough for visualisation
    wk = next((p for p in squad if "wk" in p.lower() or "keeper" in p.lower()), None)
    if not wk and squad:
        wk = squad[-1]
    if wk in squad:
        squad.remove(wk)

    return wk, squad


def draw_tactical_overlay(screen, event, stadium, match, game):
    """
    Place fielder + batter dots on the pitch using the tactic templates
    from `field_tactics.py`, assigning real player names from the squad.
    """
    if not event or not stadium or not match:
        return

    striker      = _striker(event)
    non_striker  = _attr(event, "non_striker")
    bowler       = _attr(event, "bowler")
    field_team   = _attr(event, "fielding_team")
    bat_team     = _attr(event, "batting_team")
    over         = int(_attr(event, "over") or 0)

    pp      = game.get("powerplay") if game else None
    tactic  = FIELD_TACTICS.get(_pick_tactic(over, pp), [])

    w, h = screen.get_size()
    cx, cy = w // 2, h // 2
    max_r  = min(w, h) // 2 - 180
    scale  = max_r / (min(stadium.width_m, stadium.length_m) / 2)

    fc = TEAM_COLORS.get(field_team, (220, 220, 220))
    bc = TEAM_COLORS.get(bat_team, (240, 240, 240))
    fn = _font("label")

    def label_at(pos, name, prefix=""):
        """Small translucent name tag next to a dot."""
        txt = fn.render(f"{prefix}{name.split()[-1]}", True, bc)
        pad = 4
        bg_r = txt.get_rect(topleft=(pos[0] + 12, pos[1] - 8)).inflate(pad * 2, pad * 2)
        overlay = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, bg_r.topleft)
        screen.blit(txt, (bg_r.x + pad, bg_r.y + pad))

    # Assign real names to tactical positions
    wk, outfield = _fielding_xi(match, field_team, bowler)
    role_map = {"Bowler": bowler, "WK": wk}
    pool = iter(outfield)

    for role, r_yards, theta_deg in tactic:
        if role not in role_map:
            try:
                role_map[role] = next(pool)
            except StopIteration:
                continue

        player = role_map[role]
        if not player:
            continue

        r_px = r_yards * YARD_M * scale
        theta = math.radians(theta_deg - 90)
        x = cx + r_px * math.cos(theta)
        y = cy + r_px * math.sin(theta)

        pygame.draw.circle(screen, fc, (int(x), int(y)), 6)
        pygame.draw.circle(screen, (15, 15, 15), (int(x), int(y)), 1)

        surname = player.split()[-1]
        if role.lower() == "bowler":
            surname = f"B: {surname}"
        elif role.lower() == "wk":
            surname = f"WK: {surname}"
        screen.blit(fn.render(surname, True, fc), (x + 8, y - 8))

    # Batsmen at the crease
    ns_pos = (cx + 60, cy - 28)
    st_pos = (cx + 60, cy + 28)

    if striker:
        pygame.draw.circle(screen, bc, st_pos, 8)
        label_at(st_pos, striker)

    if non_striker:
        pygame.draw.circle(screen, bc, ns_pos, 8)
        label_at(ns_pos, non_striker, prefix="NS: ")

    # Arc text showing the fielding team name around the boundary
    if field_team:
        af = _font("arc")
        radius = max_r + 42
        text = field_team.upper()
        span = math.pi * 0.85
        step = span / max(len(text), 1)
        start = math.pi * 0.075

        for i, ch in enumerate(text):
            a = start + i * step
            tx = cx - radius * math.cos(a)
            ty = cy + radius * math.sin(a)
            surf = af.render(ch, True, fc)
            rot = pygame.transform.rotate(surf, math.degrees(a) - 90)
            screen.blit(rot, rot.get_rect(center=(tx, ty)))
