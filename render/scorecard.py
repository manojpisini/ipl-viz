import pygame

from data.team_registry import TEAM_COLORS
from data.theme import (
    BG_COLOR, HEADER_BG as HEADER_BAR, TEXT_GOLD as TAB_ACTIVE,
    BORDER_COLOR, TEXT_WHITE, TEXT_GOLD, TEXT_BLACK, ROW_A, ROW_B,
)

TAB_INACTIVE = (60, 70, 90)


class ScorecardView:
    """
    Batting / bowling scorecard — tabbed by innings.

    Stats are computed live from the raw delivery data so we don't
    need a separate aggregation step.
    """

    def __init__(self):
        self.selected_inning = 0
        self.tab_rects = {}
        self.font_lg  = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_res = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_pom = pygame.font.SysFont("Arial", 22, bold=True)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.tab_rects.items():
                if rect.collidepoint(event.pos):
                    if key == "inn0":
                        self.selected_inning = 0
                    elif key == "inn1":
                        self.selected_inning = 1
                    return True
        return False

    def draw(self, screen, rect, match_data, mode, font_title, font_body):
        pygame.draw.rect(screen, BG_COLOR, rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1, border_radius=12)

        if not match_data or "innings" not in match_data:
            return

        innings = match_data["innings"]
        squad   = match_data.get("info", {}).get("players", {})

        if mode == "batting":
            cols = [("BATTER", 260), ("DISMISSAL", 300), ("R", 60), ("B", 60), ("4s", 60), ("6s", 60), ("SR", 80)]
        else:
            cols = [("BOWLER", 300), ("O", 80), ("M", 80), ("R", 80), ("W", 80), ("ECON", 100)]

        tw = sum(c[1] for c in cols)
        sx = rect.centerx - tw // 2
        sy = rect.y + 70
        footer_room = 160

        # Innings tabs
        tab_h = 40
        tabs = []
        total_tw = 0
        for i in range(len(innings)):
            name = innings[i].get("team", f"Inn {i+1}")
            w = max(180, self.font_med.size(name)[0] + 50)
            tabs.append((name, w))
            total_tw += w + 10

        tx = rect.centerx - total_tw // 2
        ty = rect.y + 20

        for i, (name, w) in enumerate(tabs):
            tr = pygame.Rect(tx, ty, w, tab_h)
            self.tab_rects[f"inn{i}"] = tr
            active = i == self.selected_inning
            bg = TEAM_COLORS.get(name, TAB_ACTIVE) if active else TAB_INACTIVE
            fg = (0, 0, 0) if active and name == "Chennai Super Kings" else TEXT_WHITE
            pygame.draw.rect(screen, bg, tr, border_top_left_radius=8, border_top_right_radius=8)
            lbl = self.font_med.render(name, True, fg)
            screen.blit(lbl, lbl.get_rect(center=tr.center))
            tx += w + 10

        # Column header bar
        pygame.draw.rect(screen, HEADER_BAR, (sx, sy, tw, 40))
        cx = sx
        for name, w in cols:
            screen.blit(self.font_med.render(name, True, TEXT_GOLD), (cx + 10, sy + 10))
            cx += w

        # Data rows
        if self.selected_inning < len(innings):
            inn = innings[self.selected_inning]
            team_squad = squad.get(inn.get("team"), [])
            ry = sy + 40
            limit = rect.bottom - footer_room
            if mode == "batting":
                self._bat_rows(screen, inn, team_squad, sx, ry, cols, tw, limit)
            else:
                self._bowl_rows(screen, inn, sx, ry, cols, tw, limit)

        self._footer(screen, rect, match_data)

    # -- Batting card ---------------------------------------------------------

    def _bat_rows(self, screen, inn, squad, sx, y, cols, tw, limit):
        stats = {}
        for ov in inn.get("overs", []):
            for ball in ov.get("deliveries", []):
                bat = ball["batter"]
                r = ball["runs"]["batter"]
                if bat not in stats:
                    stats[bat] = {"r": 0, "b": 0, "4": 0, "6": 0, "out": "not out"}
                s = stats[bat]
                s["r"] += r
                if "wides" not in ball.get("extras", {}):
                    s["b"] += 1
                if r == 4: s["4"] += 1
                if r == 6: s["6"] += 1
                if "wickets" in ball:
                    for w in ball["wickets"]:
                        if w["player_out"] == bat:
                            s["out"] = w["kind"]

        display = squad if squad else list(stats.keys())

        for i, name in enumerate(display):
            if y + 42 > limit:
                break
            bg = ROW_A if i % 2 == 0 else ROW_B
            pygame.draw.rect(screen, bg, (sx, y, tw, 42))

            if name in stats:
                s = stats[name]
                sr = round(s["r"] / s["b"] * 100, 1) if s["b"] > 0 else 0.0
                vals = [name, s["out"], s["r"], s["b"], s["4"], s["6"], sr]
            else:
                vals = [name, "Did not bat", "-", "-", "-", "-", "-"]

            cx = sx
            for j, v in enumerate(vals):
                col = (255, 255, 255) if j in (0, 2) else TEXT_WHITE
                screen.blit(self.font_lg.render(str(v), True, col), (cx + 10, y + 10))
                cx += cols[j][1]
            y += 44

    # -- Bowling card ---------------------------------------------------------

    def _bowl_rows(self, screen, inn, sx, y, cols, tw, limit):
        stats = {}
        for ov in inn.get("overs", []):
            for ball in ov.get("deliveries", []):
                bwl = ball["bowler"]
                if bwl not in stats:
                    stats[bwl] = {"b": 0, "r": 0, "w": 0}
                s = stats[bwl]
                ex = ball.get("extras", {})
                if "wides" not in ex and "noballs" not in ex:
                    s["b"] += 1
                if "legbyes" not in ex and "byes" not in ex:
                    s["r"] += ball["runs"]["total"]
                if "wickets" in ball:
                    for w in ball["wickets"]:
                        if w["kind"] not in ["run out"]:
                            s["w"] += 1

        for i, (name, s) in enumerate(stats.items()):
            if y + 42 > limit:
                break
            overs = f"{s['b'] // 6}.{s['b'] % 6}"
            econ = round(s["r"] / (s["b"] / 6), 2) if s["b"] > 0 else 0.0
            bg = ROW_A if i % 2 == 0 else ROW_B
            pygame.draw.rect(screen, bg, (sx, y, tw, 42))

            vals = [name, overs, "0", s["r"], s["w"], econ]
            cx = sx
            for j, v in enumerate(vals):
                screen.blit(self.font_lg.render(str(v), True, TEXT_WHITE), (cx + 10, y + 10))
                cx += cols[j][1]
            y += 44

    # -- Footer (POM + result pill) -------------------------------------------

    def _footer(self, screen, rect, match_data):
        info = match_data.get("info", {})

        pom = info.get("player_of_match", [])
        if pom:
            txt = f"PLAYER OF THE MATCH: {', '.join(pom).upper()}"
            bw = rect.width - 60
            br = pygame.Rect(rect.x + 30, rect.bottom - 130, bw, 45)
            pygame.draw.rect(screen, (5, 10, 25), br, border_radius=6)
            pygame.draw.rect(screen, TEXT_GOLD, br, 1, border_radius=6)
            screen.blit(self.font_pom.render(txt, True, TEXT_GOLD), self.font_pom.render(txt, True, TEXT_GOLD).get_rect(center=br.center))

        outcome = info.get("outcome", {})
        winner = outcome.get("winner")
        if not winner:
            return

        by = outcome.get("by", {})
        if "runs" in by:
            text = f"{winner.upper()} WON BY {by['runs']} RUNS"
        elif "wickets" in by:
            text = f"{winner.upper()} WON BY {by['wickets']} WICKETS"
        else:
            text = "MATCH TIED"

        pw, ph = rect.width - 60, 50
        pr = pygame.Rect(rect.x + 30, rect.bottom - 70, pw, ph)
        pygame.draw.rect(screen, (245, 245, 255), pr, border_radius=25)

        wc = TEAM_COLORS.get(winner, BG_COLOR)
        if winner == "Chennai Super Kings":
            wc = (0, 0, 0)
        screen.blit(self.font_res.render(text, True, wc), self.font_res.render(text, True, wc).get_rect(center=pr.center))