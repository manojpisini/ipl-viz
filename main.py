"""
ipl-viz — broadcast-style IPL match replay built on Pygame.

Entry point.  Boots the window, loads season data, and hands off to either
the match-selection screen or the live-replay view depending on state.
"""

import logging
import sys
from pathlib import Path

import pygame

log = logging.getLogger(__name__)

from data_io.season_index import list_seasons, list_matches_for_season
from data_io.match_context import load_match_and_stadium, extract_game_details
from data_io.cricsheet import extract_ball_events
from render.field import draw_field
from render.team_view import draw_team_view
from render.scorecard import ScorecardView
from render.points_table import PointsTableView
from render.tactical_overlay import draw_tactical_overlay

from engine.timeline import Timeline
from engine.parser import parse_match_events
from engine.reducer import apply_ball
from engine.state import MatchState

from ui.dropdown import Dropdown
from ui.panels import draw_panel, draw_weather_panel
from ui.title_bar import draw_title_bar
from ui.match_table import MatchTable, abbreviate_teams
from ui.hud import HUD
from ui.view_selector import ViewSelector


class Cfg:
    """Layout tokens and palette constants that don't belong to any widget."""
    FPS           = 60
    BG            = (18, 18, 18)
    HEADER_H      = 72
    HEADER_PAD    = 16
    CONTENT_TOP   = HEADER_H + 8
    GAP           = 6
    MARGIN        = 16

    # Panel heights
    P_MATCH   = 260
    P_GAME    = 240
    P_VENUE   = 190
    P_WEATHER = 240

    C_TITLE    = (245, 245, 245)
    C_SUBTITLE = (180, 180, 180)
    C_BTN      = (235, 240, 255)


class Phase:
    SELECT = "select"
    MATCH  = "match"


class IPLVizApp:

    def __init__(self):
        pygame.init()
        pygame.font.init()

        disp = pygame.display.Info()
        self.w = int(disp.current_w * 0.92)
        self.h = int(disp.current_h * 0.92)

        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE, vsync=1)
        pygame.display.set_caption("ipl-viz")
        self.clock = pygame.time.Clock()

        self.ft  = pygame.font.SysFont("JetBrainsMono NF", 14, bold=True)
        self.fb  = pygame.font.SysFont("JetBrainsMono NF", 12)
        self.fst = pygame.font.SysFont("JetBrainsMono NF", 12, bold=True)
        self.fsb = pygame.font.SysFont("JetBrainsMono NF", 10)

        self.phase    = Phase.SELECT
        self.running  = True
        self.sel_idx  = None
        self.view     = "view_field"

        self.seasons = list_seasons()
        self.matches = list_matches_for_season(self.seasons[0]) if self.seasons else []

        self.match_data   = None
        self.stadium      = None
        self.game_info    = None
        self.timeline     = None
        self.state        = MatchState()
        self.cur_event    = None

        self.scorecard = ScorecardView()
        self.pts_view  = PointsTableView()
        self.hud       = HUD(self.w, self.h, {})

        self._load_assets()
        self._init_ui()
        self._layout()

    # -- Asset loading --------------------------------------------------------

    def _load_assets(self):
        self.wx_icons = {}
        names = {
            "temp_hot": "hotthermometer.png", "humid": "drop.png",
            "wind": "wind.png",               "rain_drop": "waterdrops.png",
            "clear": "sun.png",               "cloudy_sun": "cloudysun.png",
            "cloudy": "clouds.png",           "cloudy_wind": "cloudywind.png",
            "drizzle": "drizzle.png",         "rain": "rain.png",
            "thunder": "thunder.png",
        }
        summary_keys = {"clear", "cloudy", "rain", "thunder", "cloudy_sun", "cloudy_wind", "drizzle"}
        base = Path("images") / "weather"

        for key, fname in names.items():
            try:
                img = pygame.image.load(base / fname).convert_alpha()
                sz = (42, 42) if key in summary_keys else (24, 24)
                self.wx_icons[key] = pygame.transform.smoothscale(img, sz)
            except Exception as exc:
                log.warning("Missing weather icon %s: %s", fname, exc)

    # -- UI bootstrap ---------------------------------------------------------

    def _init_ui(self):
        self.dd = Dropdown(
            x=self.w - 180 - Cfg.HEADER_PAD, y=Cfg.HEADER_PAD,
            w=180, h=32,
            options=self.seasons or ["<no seasons>"],
            font=self.fb,
        )
        self.table = MatchTable(0, Cfg.CONTENT_TOP, self.w, self.h, self.fb)
        self.table.set_matches(self.matches)
        self._layout()

    def _layout(self):
        ratio = 0.72
        self.table.rect.width  = int(self.w * ratio)
        self.table.rect.x      = (self.w - self.table.rect.width) // 2
        self.table.rect.height = self.h - Cfg.CONTENT_TOP - 16

        self.dd.rect.x = self.w - self.dd.rect.width - Cfg.HEADER_PAD

        pw = 320
        px_l = Cfg.MARGIN
        px_r = self.w - pw - Cfg.MARGIN
        py   = Cfg.HEADER_H + Cfg.MARGIN

        cx = px_l + pw + Cfg.MARGIN
        cw = px_r - cx - Cfg.MARGIN
        ch = self.h - py - 100
        self.center = pygame.Rect(cx, py, cw, ch)
        self.pw, self.px_l, self.px_r, self.py = pw, px_l, px_r, py

        self.vs = ViewSelector(px_l, py + Cfg.P_VENUE + Cfg.P_WEATHER + 12, pw, self.fst)

        hud_h = 80
        self.hud.rect  = pygame.Rect(0, self.h - hud_h, self.w, hud_h)
        self.hud.width = self.w
        self.btn_back  = pygame.Rect(20, 16, 90, 32)

    # -- Main loop ------------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(Cfg.FPS) / 1000.0
            self._events()
            self._tick(dt)
            self._draw()
        pygame.quit()
        sys.exit()

    # -- Events ---------------------------------------------------------------

    def _events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.VIDEORESIZE:
                self.w, self.h = ev.w, ev.h
                self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE, vsync=1)
                self._layout()

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if self.phase == Phase.MATCH:
                        self.phase = Phase.SELECT
                    else:
                        self.running = False

                if self.phase == Phase.MATCH and self.timeline:
                    if ev.key == pygame.K_SPACE:
                        self.timeline.toggle_play()
                    elif ev.key == pygame.K_RIGHT:
                        self.timeline.seek(self.timeline.index + 1)
                    elif ev.key == pygame.K_LEFT:
                        self.timeline.seek(self.timeline.index - 1)

            if self.phase == Phase.SELECT:
                self._ev_select(ev)
            elif self.phase == Phase.MATCH:
                self._ev_match(ev)

    def _ev_select(self, ev):
        if self.dd.handle_event(ev):
            self.matches = list_matches_for_season(self.seasons[self.dd.selected])
            self.table.set_matches(self.matches)
            return

        row = self.table.handle_event(ev)
        if row is not None:
            self.sel_idx = row
            self._load_match()
            self.phase = Phase.MATCH

    def _ev_match(self, ev):
        if self.view in ("view_batting", "view_bowling"):
            if self.scorecard.handle_event(ev):
                return
        elif self.view == "view_points":
            if self.pts_view.handle_event(ev):
                return

        action = self.hud.handle_event(ev)
        if action:
            if action == "PLAY_PAUSE":
                self.timeline.toggle_play()
            elif action == "SPEED_UP":
                self.timeline.set_speed(min(self.timeline.speed + 0.5, 4.0))
            elif action == "SPEED_DOWN":
                self.timeline.set_speed(max(self.timeline.speed - 0.5, 0.5))
            elif action == "RESTART":
                self.timeline.seek(0)
            return

        nv = self.vs.handle_event(ev)
        if nv:
            self.view = nv
            return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_back.collidepoint(ev.pos):
                self.phase = Phase.SELECT

    # -- Match loading --------------------------------------------------------

    def _load_match(self):
        m = self.matches[self.sel_idx]
        raw, self.stadium, self.game_info = load_match_and_stadium(m["file"])
        self.match_data = raw

        self.timeline = Timeline(parse_match_events(raw))
        self.timeline.playing = True
        self.timeline.set_speed(1.0)
        self.state     = MatchState()
        self.cur_event = None

    # -- Update ---------------------------------------------------------------

    def _tick(self, dt):
        if self.phase != Phase.MATCH or not self.timeline:
            return
        ev = self.timeline.update(dt)
        if ev:
            self.cur_event = ev
            self.state = apply_ball(self.state, ev)

    # -- Render ---------------------------------------------------------------

    def _draw(self):
        self.screen.fill(Cfg.BG)
        if self.phase == Phase.SELECT:
            self._draw_select()
        else:
            self._draw_match()
        pygame.display.flip()

    def _draw_select(self):
        self.screen.blit(self.ft.render("IPL Match Replay", True, Cfg.C_TITLE), (Cfg.HEADER_PAD, Cfg.HEADER_PAD))
        self.table.draw(self.screen)
        self.dd.draw(self.screen)

    def _draw_match(self):
        m = self.matches[self.sel_idx]
        draw_title_bar(self.screen, pygame.Rect(0, 0, self.w, Cfg.HEADER_H),
                        m["teams"], f"{m['date']} | {m['stage']}", self.ft, self.fb)
        self._btn(self.btn_back, "← Back")

        if self.view == "view_field":
            if self.stadium:
                draw_field(self.screen, self.stadium)
            if self.cur_event:
                draw_tactical_overlay(self.screen, self.cur_event, self.stadium,
                                      self.match_data, self.game_info)
        elif self.view == "view_teams":
            draw_team_view(self.screen, self.center, self.match_data, self.ft, self.fb)
        elif self.view == "view_batting":
            self.scorecard.draw(self.screen, self.center, self.match_data, "batting", self.ft, self.fb)
        elif self.view == "view_bowling":
            self.scorecard.draw(self.screen, self.center, self.match_data, "bowling", self.ft, self.fb)
        elif self.view == "view_points":
            year = m["date"].split("-")[0]
            self.pts_view.draw(self.screen, self.center, year, self.ft, self.fb)

        self._panels()
        self.vs.draw(self.screen, self.view)

        recent = []
        if self.timeline:
            start = max(0, self.timeline.index - 8)
            recent = self.timeline.events[start : self.timeline.index]

        self.hud.render(
            self.screen, self.state, recent,
            self.timeline.speed if self.timeline else 1.0,
            self.timeline.playing if self.timeline else False,
        )

    # -- Side panels ----------------------------------------------------------

    def _panels(self):
        info = self.match_data.get("info", {})
        det  = self.game_info
        stad = self.stadium
        offs = info.get("officials", {})

        venue_lines = [
            f"Stadium: {stad.name}",
            f"City: {info.get('city')}",
            f"Boundaries: {stad.straight_boundary_m}m(S) | {stad.square_boundary_m}m(Q)",
            "",
        ]

        match_lines = [
            f"Season: {info.get('season')}",
            f"Match: #{info.get('event', {}).get('match_number', 'N/A')}",
            f"Teams: {info['teams'][0]} v {info['teams'][1]}",
            f"Date: {det['date']}",
            f"Umpires: {', '.join(offs.get('umpires', []))}",
            f"Referee: {offs.get('match_referees', ['N/A'])[0]}",
        ]

        cur_inn = self.cur_event.innings if self.cur_event else 1
        pp = det.get("powerplay", {})
        pp_txt = "Standard" if pp else "None"
        if self.state.legal_balls <= 36:
            pp_txt = f"ACTIVE ({pp.get('type', 'Mandatory')})"

        game_lines = [
            f"Toss: {det['toss_winner']} ({det['toss_decision']})",
            f"Innings: {cur_inn}",
        ]
        if cur_inn == 2:
            tgt = det.get("target", {})
            if tgt:
                game_lines.append(f"Target: {tgt.get('runs')} ({tgt.get('overs')} ov)")
        game_lines += [f"Powerplay: {pp_txt}", f"Run Rate: {self.state.run_rate}"]

        draw_panel(self.screen, self.px_l, self.py, self.pw, Cfg.P_VENUE, "Venue", venue_lines, self.fb, self.ft)
        draw_weather_panel(self.screen, self.px_l, self.py + Cfg.P_VENUE + Cfg.GAP, self.pw, Cfg.P_WEATHER,
                           self.game_info.get("weather", {}), self.wx_icons, self.fb, self.ft)
        draw_panel(self.screen, self.px_r, self.py, self.pw, Cfg.P_MATCH, "Match", match_lines, self.fb, self.ft)
        draw_panel(self.screen, self.px_r, self.py + Cfg.P_MATCH + Cfg.GAP, self.pw, Cfg.P_GAME, "Game", game_lines, self.fb, self.ft)

    def _btn(self, rect, text):
        pygame.draw.rect(self.screen, (40, 40, 40), rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 120), rect, 1, border_radius=8)
        t = self.fb.render(text, True, Cfg.C_BTN)
        self.screen.blit(t, t.get_rect(center=rect.center))


if __name__ == "__main__":
    IPLVizApp().run()
