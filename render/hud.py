import pygame
from engine.state import MatchState
from engine.events import BallEvent

# -------------------------------------------------
# HUD Styling (IPL Broadcast Style)
# -------------------------------------------------
HUD_HEIGHT = 72
BG_COLOR = (20, 24, 35)      # Dark Navy
ACCENT_COLOR = (28, 32, 44)  # Lighter Navy strip
BORDER_COLOR = (50, 60, 80)
TEXT_WHITE = (245, 245, 245)
TEXT_GOLD = (255, 204, 0)
TEXT_GRAY = (160, 160, 160)
TIMELINE_BG = (35, 40, 50)

class HUD:
    def __init__(self, width, height):
        self.width = width
        self.screen_height = height
        self.rect = pygame.Rect(0, height - HUD_HEIGHT, width, HUD_HEIGHT)
        
        # Caching
        self._cache_surface = pygame.Surface((width, HUD_HEIGHT))
        self._last_state_hash = None
        
        # Fonts (Lazy load in render if None, or init here)
        self.font_lg = pygame.font.SysFont("JetBrainsMono NF", 28, bold=True)
        self.font_md = pygame.font.SysFont("JetBrainsMono NF", 16, bold=True)
        self.font_sm = pygame.font.SysFont("JetBrainsMono NF", 12)

    def _render_to_cache(self, state: MatchState, recent_events: list[BallEvent]):
        """
        Renders the entire HUD to self._cache_surface.
        This is expensive, so we only do it when state changes.
        """
        s = self._cache_surface
        s.fill(BG_COLOR)
        
        # Top Border
        pygame.draw.line(s, TEXT_GOLD, (0, 0), (self.width, 0), 2)

        # Padding
        px = 24
        py = 12

        # -------------------------------------------------
        # 1. Main Score (Left)
        # -------------------------------------------------
        # Score: "145 / 3"
        score_str = f"{state.score}/{state.wickets}"
        score_surf = self.font_lg.render(score_str, True, TEXT_WHITE)
        s.blit(score_surf, (px, py))
        
        # Overs: "14.2 Overs" (Small, below score)
        over_str = f"{state.overs_str} Overs"
        over_surf = self.font_sm.render(over_str, True, TEXT_GRAY)
        s.blit(over_surf, (px, py + 34))

        # Vertical Divider
        div_x = px + 140
        pygame.draw.line(s, BORDER_COLOR, (div_x, 10), (div_x, HUD_HEIGHT - 10), 1)

        # -------------------------------------------------
        # 2. Match Situation (Middle)
        # -------------------------------------------------
        mid_x = div_x + 20
        
        # Current Batter / Bowler
        batter_txt = f"Batting: {state.current_batter or 'Unknown'}"
        bowler_txt = f"Bowling: {state.current_bowler or 'Unknown'}"
        
        s.blit(self.font_md.render(batter_txt, True, TEXT_WHITE), (mid_x, py + 2))
        s.blit(self.font_sm.render(bowler_txt, True, TEXT_GRAY), (mid_x, py + 24))

        # Target / Run Rate
        rr_txt = f"CRR: {state.run_rate}"
        if state.req_run_rate:
            rr_txt += f"  |  RRR: {state.req_run_rate}"
        
        s.blit(self.font_sm.render(rr_txt, True, TEXT_GOLD), (mid_x, py + 40))

        # -------------------------------------------------
        # 3. Recent Balls Timeline (Right)
        # -------------------------------------------------
        self._draw_timeline(s, recent_events)

    def _draw_timeline(self, surface, events):
        """Draws circles for the last 6-8 balls on the right side."""
        # Config
        circle_radius = 14
        gap = 8
        
        # Start from right edge
        start_x = self.width - 40
        center_y = HUD_HEIGHT // 2
        
        # Background container for timeline
        bg_w = (len(events) * (circle_radius * 2 + gap)) + 20
        bg_rect = pygame.Rect(start_x - bg_w + 20, 10, bg_w, HUD_HEIGHT - 20)
        pygame.draw.rect(surface, TIMELINE_BG, bg_rect, border_radius=16)

        # Iterate backwards (most recent on right)
        for i, ev in enumerate(reversed(events)):
            if i >= 8: break # Max 8 balls shown
            
            cx = start_x - (i * (circle_radius * 2 + gap))
            
            # Color Coding
            bg_col = (50, 50, 50) # Default Dot
            txt_col = TEXT_WHITE
            label = str(ev.runs_batter)

            if ev.is_wicket:
                bg_col = (200, 50, 50) # Red
                label = "W"
            elif ev.runs_batter == 4:
                bg_col = (50, 100, 200) # Blue
            elif ev.runs_batter == 6:
                bg_col = (50, 160, 50)  # Green
            elif not ev.is_legal:
                bg_col = (160, 100, 50) # Orange (Wide/NB)
                label = "wd" if ev.is_wide else "nb"

            # Draw
            pygame.draw.circle(surface, bg_col, (cx, center_y), circle_radius)
            
            # Text centering
            txt = self.font_sm.render(label, True, txt_col)
            txt_rect = txt.get_rect(center=(cx, center_y))
            surface.blit(txt, txt_rect)

    def render(self, screen, state: MatchState, recent_events: list):
        """
        Main render call. Checks hash to see if redraw is needed.
        """
        # Create a simple hash of the display state to avoid redundant rendering
        current_hash = hash((
            state.score, state.wickets, state.legal_balls, 
            state.current_batter, state.current_bowler, 
            len(recent_events)
        ))

        if current_hash != self._last_state_hash:
            self._render_to_cache(state, recent_events)
            self._last_state_hash = current_hash

        # Blit the cached surface
        screen.blit(self._cache_surface, self.rect.topleft)