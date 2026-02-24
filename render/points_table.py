"""
Points table + playoff bracket view.

Uses matplotlib (Agg backend) to render the playoff tree into a PNG,
caches the result per-season so the heavy render only happens once.
"""

import io
import json
import logging
import os

import pandas as pd
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path as MplPath

from data.team_registry import(
    TEAM_COLORS as TEAM_COLORS_RGB,
    TEAM_COLORS_HEX,
    get_team_color,
)
from data.theme import (
    BG_COLOR, HEADER_BG as HEADER_BG_COLOR, TEXT_GOLD as TAB_ACTIVE,
    TEXT_WHITE, TEXT_GOLD, BORDER_COLOR,
)

TAB_INACTIVE = (60, 70, 90)
ROW_DEFAULT  = (30, 40, 60)

SEASON_WINNERS = {
    "2008": "Rajasthan Royals",   "2009": "Deccan Chargers",       "2010": "Chennai Super Kings",
    "2011": "Chennai Super Kings","2012": "Kolkata Knight Riders",  "2013": "Mumbai Indians",
    "2014": "Kolkata Knight Riders","2015": "Mumbai Indians",       "2016": "Sunrisers Hyderabad",
    "2017": "Mumbai Indians",     "2018": "Chennai Super Kings",    "2019": "Mumbai Indians",
    "2020": "Mumbai Indians",     "2021": "Chennai Super Kings",    "2022": "Gujarat Titans",
    "2023": "Chennai Super Kings","2024": "Kolkata Knight Riders",  "2025": "Royal Challengers Bengaluru",
}


class PointsTableView:
    def __init__(self):
        self.font_lg    = pygame.font.SysFont("Impact", 36)
        self.font_row   = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_win   = pygame.font.SysFont("Impact", 32)
        self.font_tab   = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_match = pygame.font.SysFont("Arial", 14, bold=True)

        self.current_tab = "standings"
        self.tab_rects   = {}

        self.points_data   = self._load("data/points_table.json")
        self.playoffs_data = self._load("data/playoffs.json")
        self.tree_cache    = {}

    @staticmethod
    def _load(path):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.tab_rects.items():
                if rect.collidepoint(event.pos):
                    if self.current_tab != key:
                        self.current_tab = key
                    return True
        return False

    def draw(self, screen, rect, year, font_title, font_body):
        pygame.draw.rect(screen, BG_COLOR, rect, border_radius=12)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1, border_radius=12)

        self._tabs(screen, rect, year)
        content = pygame.Rect(rect.x + 20, rect.y + 60, rect.width - 40, rect.height - 160)
        yr = str(year)

        if self.current_tab == "standings":
            self._standings(screen, content, yr)
        else:
            self._playoffs(screen, content, yr)

        self._winner_block(screen, rect, yr)

    # -- Tabs -----------------------------------------------------------------

    def _tabs(self, screen, rect, year):
        try:
            label_p = "SEMIFINALS" if int(year) < 2011 else "PLAYOFFS"
        except ValueError:
            label_p = "PLAYOFFS"

        tabs = [("POINTS TABLE", "standings"), (label_p, "playoffs")]
        tw, th = 180, 36
        sx = rect.centerx - (tw * 2 + 10) // 2
        y = rect.y + 15

        for label, key in tabs:
            r = pygame.Rect(sx, y, tw, th)
            self.tab_rects[key] = r
            active = key == self.current_tab
            bg = TAB_ACTIVE if active else TAB_INACTIVE
            fg = (0, 0, 0) if active else TEXT_WHITE
            pygame.draw.rect(screen, bg, r, border_radius=18)
            t = self.font_tab.render(label, True, fg)
            screen.blit(t, t.get_rect(center=r.center))
            sx += tw + 10

    # -- Standings table ------------------------------------------------------

    def _standings(self, screen, rect, year):
        cols = [("TEAM", 250), ("M", 60), ("W", 60), ("L", 60), ("N/R", 60), ("NRR", 90), ("PTS", 70)]
        tw = sum(c[1] for c in cols)
        sx = rect.centerx - tw // 2
        y = rect.y

        pygame.draw.rect(screen, (0, 0, 0), (sx, y, tw, 40))
        cx = sx
        for name, w in cols:
            screen.blit(self.font_row.render(name, True, TEXT_WHITE), (cx + 10, y + 10))
            cx += w

        data = self.points_data.get(year, [])
        if not data:
            self._no_data(screen, rect, f"No Standings for {year}")
            return

        y += 42
        for i, ts in enumerate(data):
            if y + 48 > rect.bottom:
                break
            name = ts.get("team", "Unknown")
            bg = get_team_color(name)
            pygame.draw.rect(screen, bg, (sx, y, tw, 48))

            vals = [
                name, ts.get("matches", 0), ts.get("wins", 0), ts.get("losses", 0),
                ts.get("nr", 0), f"{ts.get('nrr', 0.0):.3f}", ts.get("points", 0),
            ]
            cx = sx
            for j, v in enumerate(vals):
                fc = (0, 0, 0) if name == "Chennai Super Kings" else TEXT_WHITE
                t = self.font_row.render(str(v), True, fc)
                if j == 0:
                    screen.blit(t, (cx + 15, y + 14))
                else:
                    screen.blit(t, (cx + (cols[j][1] - t.get_width()) // 2, y + 14))
                cx += cols[j][1]
            y += 50

    # -- Playoffs bracket (matplotlib) ----------------------------------------

    def _playoffs(self, screen, rect, year):
        data = self.playoffs_data.get(year, {})
        if not data:
            self._no_data(screen, rect, f"No Playoff Data for {year}")
            return

        if year not in self.tree_cache:
            try:
                self.tree_cache[year] = self._mpl_tree(data, year, rect.size)
            except Exception as exc:
                logging.warning("Matplotlib bracket failed: %s — using fallback", exc)
                self.tree_cache[year] = None

        surf = self.tree_cache[year]
        if surf:
            ox = rect.x + (rect.width - surf.get_width()) // 2
            oy = rect.y + (rect.height - surf.get_height()) // 2
            screen.blit(surf, (ox, oy))
        else:
            self._manual_playoffs(screen, rect, data, year)

    def _mpl_tree(self, data, year, size):
        dpi = 100
        fig, ax = plt.subplots(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax.axis("off")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        def path(pts, color="gold", style="-"):
            codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1)
            ax.add_patch(patches.PathPatch(MplPath(pts, codes), facecolor="none", edgecolor=color, lw=2, linestyle=style))

        def card(x, y, title, md, final=False):
            if not md:
                return
            w, h = 22, 12
            ax.add_patch(patches.FancyBboxPatch(
                (x, y - h / 2), w, h,
                boxstyle="round,pad=0.2,rounding_size=1",
                ec="gold" if final else "white", fc="#101525", lw=2,
            ))
            hh = 3.5
            ax.add_patch(patches.Rectangle((x, y + h / 2 - hh), w, hh, color="white"))
            ax.text(x + w / 2, y + h / 2 - hh / 2, title.upper(),
                    ha="center", va="center", fontsize=9, fontweight="bold", color="black")

            teams  = md.get("teams", ["?", "?"])
            winner = md.get("winner")
            ry = y + h / 2 - hh - 2.5

            for tm in teams:
                c_hex = TEAM_COLORS_HEX.get(tm, "#333333")
                ax.add_patch(patches.Rectangle((x, ry - 1.5), w, 3, color=c_hex, alpha=0.9))
                fc = "black" if tm == "Chennai Super Kings" else "white"
                dn = tm if len(tm) <= 15 else tm[:13] + ".."
                pre = "✔ " if tm == winner else ""
                wt  = "bold" if tm == winner else "normal"
                ax.text(x + 1, ry, pre + dn, ha="left", va="center", fontsize=8, fontweight=wt, color=fc)
                ry -= 3.5

        cw = 22
        if "qualifier_1" in data:
            q1, el, q2, fn = (5, 75), (5, 25), (38, 50), (72, 50)
            path([(q1[0]+cw, q1[1]+3), (70, q1[1]+3), (70, fn[1]+3), (fn[0], fn[1]+3)], "#F7C843")
            path([(q1[0]+cw, q1[1]-3), (34, q1[1]-3), (34, q2[1]+3), (q2[0], q2[1]+3)], "#FF4444", "--")
            path([(el[0]+cw, el[1]),    (34, el[1]),    (34, q2[1]-3), (q2[0], q2[1]-3)], "#F7C843")
            path([(q2[0]+cw, q2[1]),    (fn[0], fn[1])], "#F7C843")
            card(*q1, "QUALIFIER 1", data.get("qualifier_1"))
            card(*el, "ELIMINATOR",  data.get("eliminator"))
            card(*q2, "QUALIFIER 2", data.get("qualifier_2"))
            card(*fn, "FINAL",       data.get("final"), True)
        else:
            s1, s2, fn = (10, 70), (10, 30), (60, 50)
            path([(s1[0]+cw, s1[1]), (50, s1[1]), (50, fn[1]+2), (fn[0], fn[1]+2)], "#F7C843")
            path([(s2[0]+cw, s2[1]), (50, s2[1]), (50, fn[1]-2), (fn[0], fn[1]-2)], "#F7C843")
            card(*s1, "SEMIFINAL 1", data.get("semifinal_1"))
            card(*s2, "SEMIFINAL 2", data.get("semifinal_2"))
            card(*fn, "FINAL",       data.get("final"), True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", transparent=True, bbox_inches="tight", pad_inches=0.1)
        buf.seek(0)
        plt.close(fig)

        img = pygame.image.load(buf)
        ir = img.get_rect()
        s  = min(size[0] / ir.width, size[1] / ir.height) * 0.95
        return pygame.transform.smoothscale(img, (int(ir.width * s), int(ir.height * s)))

    # -- Pygame-only fallback bracket -----------------------------------------

    def _manual_playoffs(self, screen, rect, data, year):
        cx, cy = rect.centerx, rect.centery
        top_y, bot_y = rect.y + 30, rect.bottom - 100
        lx, rx = cx - 300, cx + 80

        if "qualifier_1" in data:
            self._manual_card(screen, lx, top_y,   "QUALIFIER 1", data.get("qualifier_1"))
            self._manual_card(screen, lx, cy + 20, "ELIMINATOR",  data.get("eliminator"))
            self._manual_card(screen, cx - 110, cy - 60, "QUALIFIER 2", data.get("qualifier_2"))
            self._manual_card(screen, rx, cy - 20, "FINAL",       data.get("final"), True)
            pygame.draw.line(screen, TEXT_GOLD, (lx + 220, top_y + 40), (rx, cy + 20), 2)
        else:
            self._manual_card(screen, lx, top_y,       "SEMIFINAL 1", data.get("semifinal_1"))
            self._manual_card(screen, lx, bot_y - 50, "SEMIFINAL 2", data.get("semifinal_2"))
            self._manual_card(screen, rx, cy - 20,     "FINAL",       data.get("final"), True)

    def _manual_card(self, screen, x, y, title, match, final=False):
        if not match:
            return
        r = pygame.Rect(x, y, 220, 80)
        bc = TEXT_GOLD if final else (100, 100, 120)
        pygame.draw.rect(screen, (20, 25, 40), r, border_radius=8)
        pygame.draw.rect(screen, bc, r, 2, border_radius=8)
        screen.blit(self.font_match.render(title, True, bc), (x + 10, y + 5))

        winner = match.get("winner")
        ty = y + 25
        for t in match.get("teams", []):
            col = TEXT_GOLD if t == winner else TEXT_WHITE
            screen.blit(self.font_match.render(t[:18], True, col), (x + 10, ty))
            ty += 20

    # -- Winner banner --------------------------------------------------------

    def _winner_block(self, screen, rect, year):
        winner = "TBD"
        pd = self.playoffs_data.get(year, {})
        if "final" in pd:
            winner = pd["final"].get("winner", "TBD")

        wc = get_team_color(winner)
        h, w = 90, rect.width - 60
        x, y = rect.x + 30, rect.bottom - h - 20
        pygame.draw.rect(screen, TEXT_GOLD, (x - 4, y - 4, w + 8, h + 8), border_radius=16)
        pygame.draw.rect(screen, wc, (x, y, w, h), border_radius=12)
        ly = self.font_row.render(f"IPL {year} CHAMPIONS", True, TEXT_WHITE)
        lw = self.font_win.render(winner.upper(), True, TEXT_GOLD)
        screen.blit(ly, (rect.centerx - ly.get_width() // 2, y + 15))
        screen.blit(lw, (rect.centerx - lw.get_width() // 2, y + 45))

    def _no_data(self, screen, rect, msg):
        t = self.font_lg.render(msg, True, (100, 100, 100))
        screen.blit(t, t.get_rect(center=rect.center))