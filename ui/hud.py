import pygame
from engine.state import MatchState, PlayerStats, BowlerStats
from ui.match_table import abbreviate_teams
from engine.paths import get_resource_path

HUD_HEIGHT = 80

# Broadcast palette — kept inline for locality (only used here)
BLUE_DARK   = (10, 30, 80)
BLUE_MID    = (20, 60, 160)
BLUE_LIGHT  = (40, 90, 200)
GOLD        = (240, 200, 50)
WHITE       = (245, 245, 255)
SILVER      = (200, 200, 210)
RED         = (200, 40, 40)
ORANGE      = (200, 100, 50)
TEXT_DARK   = (20, 20, 25)
GREY_LIGHT  = (220, 220, 230)


class HUD:
    """
    Bottom-of-screen heads-up display: score card, batter/bowler info,
    ball-by-ball timeline for the current over, and playback controls.
    """

    def __init__(self, width, height, control_icons={}):
        self.width = width
        self.screen_height = height
        self.rect = pygame.Rect(0, height - HUD_HEIGHT, width, HUD_HEIGHT)
        if control_icons:
            self.icons = control_icons
        else:
            self._load_icons()

        self.font_score = pygame.font.SysFont("Impact", 32)
        self.font_bold  = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_norm  = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_sm    = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_stats = pygame.font.SysFont("Arial", 13, bold=True)

        self.ctrl_rects = {}

    def _load_icons(self):
        import os
        self.icons = {}
        for name in ("rewind", "arrow-left", "play", "pause", "arrow-right", "speed-", "speed+"):
            path = get_resource_path(os.path.join("images", "controls", f"{name}.png"))
            try:
                img = pygame.image.load(path).convert_alpha()
                self.icons[name] = pygame.transform.smoothscale(img, (32, 32))
            except pygame.error:
                import logging
                logging.warning("Missing icon: %s", path)
                self.icons[name] = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action, rect in self.ctrl_rects.items():
                if rect.collidepoint(event.pos):
                    return action
        return None

    def _rrect(self, surf, rect, color, radius=6, border=None):
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        if border:
            pygame.draw.rect(surf, border, rect, 2, border_radius=radius)

    # -- Main render ----------------------------------------------------------

    def render(self, screen, state: MatchState, recent_events: list, speed=1.0, playing=False):
        pygame.draw.rect(screen, BLUE_DARK, self.rect)
        pygame.draw.line(screen, WHITE, (0, self.rect.y), (self.width, self.rect.y), 2)

        self._match_info(screen, state)

        bat_w = self._batting_card(screen, state, x=300)
        bowl_w = self._bowling_card(screen, state, x=300 + bat_w + 20)
        self._over_timeline(screen, recent_events, state, x=300 + bat_w + 20 + bowl_w + 20)

        ctrl_w = 340
        self._controls(screen, self.width - ctrl_w - 20, self.rect.y + 12, speed, playing, ctrl_w)

    # -- Sub-sections ---------------------------------------------------------

    def _match_info(self, screen, state):
        x, y = 20, self.rect.y + 10

        raw = abbreviate_teams(f"{state.batting_team} vs {state.bowling_team}")
        parts = raw.split(" vs ")
        title = f"{parts[0]} v {parts[1]}" if len(parts) == 2 else raw

        tr = pygame.Rect(x, self.rect.y - 10, 150, 30)
        self._rrect(screen, tr, WHITE, 6, (150, 150, 150))
        ts = self.font_bold.render(title, True, TEXT_DARK)
        screen.blit(ts, ts.get_rect(center=tr.center))

        sr = pygame.Rect(x + 155, self.rect.y - 10, 120, 42)
        self._rrect(screen, sr, GOLD, 6, WHITE)
        ss = self.font_score.render(f"{state.score}-{state.wickets}", True, TEXT_DARK)
        screen.blit(ss, ss.get_rect(center=sr.center))

        ov = pygame.Rect(x, y + 24, 150, 24)
        self._rrect(screen, ov, BLUE_MID, 4, BLUE_LIGHT)
        screen.blit(self.font_norm.render(f"OVERS {state.overs_str}", True, WHITE), (ov.x + 10, ov.y + 4))

    def _batting_card(self, screen, state, x):
        y = self.rect.y + 12
        nw, rw, bw = 160, 45, 35
        total = nw + 2 + rw + 2 + bw

        def row(name, runs, balls, striker, dy):
            bg = WHITE if striker else SILVER
            fg = TEXT_DARK if striker else (60, 60, 60)
            nr = pygame.Rect(x, y + dy, nw, 26)
            self._rrect(screen, nr, bg, 4)
            screen.blit(self.font_bold.render(name[:15], True, fg), (x + 8, y + dy + 4))

            rr = pygame.Rect(x + nw + 2, y + dy, rw, 26)
            self._rrect(screen, rr, BLUE_MID, 4, BLUE_LIGHT)
            rt = self.font_bold.render(str(runs), True, WHITE)
            screen.blit(rt, rt.get_rect(center=rr.center))

            br = pygame.Rect(x + nw + rw + 4, y + dy, bw, 26)
            bt = self.font_sm.render(str(balls), True, SILVER)
            screen.blit(bt, bt.get_rect(center=br.center))

        p1 = state.batter_stats.get(state.current_batter, PlayerStats())
        p2 = state.batter_stats.get(state.current_non_striker, PlayerStats())
        row(state.current_batter + "*", p1.runs, p1.balls, True, 0)
        row(state.current_non_striker, p2.runs, p2.balls, False, 30)
        return total

    def _bowling_card(self, screen, state, x):
        y = self.rect.y + 12
        cw = 250
        bl = state.bowler_stats.get(state.current_bowler, BowlerStats())

        br = pygame.Rect(x, y, cw, 28)
        self._rrect(screen, br, WHITE, 6, SILVER)
        screen.blit(self.font_bold.render(state.current_bowler[:15], True, TEXT_DARK), (x + 10, y + 5))
        ft = self.font_bold.render(f"{bl.wickets}-{bl.runs_conceded}", True, BLUE_DARK)
        screen.blit(ft, ft.get_rect(midright=(br.right - 10, br.centery)))

        sr = pygame.Rect(x, y + 32, cw, 24)
        self._rrect(screen, sr, BLUE_MID, 4, BLUE_LIGHT)
        st = self.font_stats.render(
            f"RR: {state.run_rate} | 4s: {state.total_fours} | 6s: {state.total_sixes}",
            True, WHITE,
        )
        screen.blit(st, st.get_rect(center=sr.center))
        return cw

    def _over_timeline(self, screen, events, state, x):
        """Visual ball-by-ball strip for the current over."""
        y = self.rect.y + 12

        # Filter to just the balls from the current over
        cur_over = []
        if events:
            target = events[-1].over
            cur_over = [e for e in events if e.over == target]

        legal_so_far = sum(1 for e in cur_over if e.is_legal)
        remaining = max(0, 6 - legal_so_far)
        slots = max(8, len(cur_over) + remaining)

        ball_sz, gap, pad = 26, 6, 12
        w = slots * (ball_sz + gap) + pad * 2
        h = 56

        self._rrect(screen, pygame.Rect(x, y, w, h), WHITE, 6, SILVER)
        screen.blit(self.font_sm.render(f"OVER {state.legal_balls // 6 + 1}", True, (80, 80, 90)), (x + 8, y + 4))

        bx_start = x + pad
        by = y + 22

        # Delivered balls, color-coded
        for i, ev in enumerate(cur_over):
            bx = bx_start + i * (ball_sz + gap)
            rect = pygame.Rect(bx, by, ball_sz, ball_sz)

            bg, txt, fg = (60, 60, 70), str(ev.runs_batter), WHITE
            if ev.is_wicket:
                bg, txt = RED, "W"
            elif ev.runs_batter == 4:
                bg = BLUE_LIGHT
            elif ev.runs_batter == 6:
                bg, fg = GOLD, TEXT_DARK
            elif not ev.is_legal:
                bg, txt = ORANGE, ("wd" if ev.is_wide else "nb")

            self._rrect(screen, rect, bg, 4)
            screen.blit(self.font_sm.render(txt, True, fg), self.font_sm.render(txt, True, fg).get_rect(center=rect.center))

        # Placeholder dots for balls yet to come
        for i in range(remaining):
            bx = bx_start + (len(cur_over) + i) * (ball_sz + gap)
            rect = pygame.Rect(bx, by, ball_sz, ball_sz)
            pygame.draw.rect(screen, GREY_LIGHT, rect, border_radius=4)
            pygame.draw.circle(screen, (180, 180, 190), rect.center, 3)

        return w

    def _controls(self, screen, x, y, speed, playing, w):
        h = 56
        self._rrect(screen, pygame.Rect(x, y, w, h), WHITE, 6, SILVER)

        btns = [
            ("RESTART",    "rewind"),
            ("PREV",       "arrow-left"),
            ("PLAY_PAUSE", "pause" if playing else "play"),
            ("NEXT",       "arrow-right"),
            ("SPEED_DOWN", "speed-"),
            ("SPEED_UP",   "speed+"),
        ]

        cx = x + 16
        cy = y + h // 2
        btn_sz = 32
        mpos = pygame.mouse.get_pos()

        for action, icon_key in btns:
            rect = pygame.Rect(cx, cy - btn_sz // 2, btn_sz, btn_sz)
            self.ctrl_rects[action] = rect

            if rect.collidepoint(mpos):
                pygame.draw.circle(screen, (220, 220, 230), rect.center, btn_sz // 2 + 2)

            icon = self.icons.get(icon_key)
            if icon:
                screen.blit(icon, icon.get_rect(center=rect.center))
            else:
                t = self.font_sm.render(icon_key[:2], True, (60, 60, 60))
                screen.blit(t, t.get_rect(center=rect.center))

            cx += btn_sz + 10

        screen.blit(self.font_bold.render(f"{speed:.1f}x", True, TEXT_DARK), (cx + 8, cy - 8))