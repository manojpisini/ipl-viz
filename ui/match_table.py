import pygame
from pygame import Rect
import math

from data.team_registry import TEAM_ABBR
from data.theme import (
    BG_COLOR, TV_BLUE_ALT as BG_ALT, TV_BLUE_LIGHT as BG_HOVER,
    HEADER_BG, BORDER_COLOR, TV_WHITE as TEXT, TV_SILVER as TEXT_MUTED,
)

# Table inherits most colors from the theme — only need the inactive tab shade here
TAB_INACTIVE = (60, 70, 90)


def abbreviate_teams(teams: str) -> str:
    parts = teams.split(" vs ")
    if len(parts) == 2:
        return f"{TEAM_ABBR.get(parts[0], parts[0])} vs {TEAM_ABBR.get(parts[1], parts[1])}"
    return teams


def truncate_text(font, text, max_width):
    if font.size(text)[0] <= max_width:
        return text
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if font.size(text[:mid] + "...")[0] <= max_width:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + "..." if lo > 0 else "..."


class MatchTable:
    """
    Paginated table listing matches for a season.

    Pre-renders the text layer once per page change so the per-frame draw
    is just a pair of blits (row backgrounds + cached text surface).
    """

    COLUMNS = [
        ("#",     50,  "center"),
        ("Stage", 180, "center"),
        ("Teams", 240, "center"),
        ("Date",  110, "center"),
        ("Venue", None, "left"),
    ]

    def __init__(self, x, y, w, h, font):
        self.rect = Rect(x, y, w, h)
        self.font = font
        self.header_h = font.get_height() + 14
        self.row_h    = font.get_height() + 12
        self.footer_h = 44
        self.matches  = []
        self.page     = 0
        self.hover_index = None
        self._text_layer = None

    def set_matches(self, matches):
        self.matches = matches
        self.page = 0
        self._prerender()

    @property
    def rows_per_page(self):
        usable = self.rect.height - self.header_h - self.footer_h
        return max(1, usable // self.row_h)

    @property
    def total_pages(self):
        if not self.matches:
            return 1
        return math.ceil(len(self.matches) / self.rows_per_page)

    # -- Events ---------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if event.y < 0 and self.page < self.total_pages - 1:
                    self.page += 1
                    self._prerender()
                elif event.y > 0 and self.page > 0:
                    self.page -= 1
                    self._prerender()
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            prev_btn, next_btn = self._pager_rects()

            if prev_btn.collidepoint(mx, my) and self.page > 0:
                self.page -= 1
                self._prerender()
                return None

            if next_btn.collidepoint(mx, my) and self.page < self.total_pages - 1:
                self.page += 1
                self._prerender()
                return None

            if self.hover_index is not None:
                return self.hover_index
        return None

    # -- Drawing --------------------------------------------------------------

    def draw(self, screen):
        pygame.draw.rect(screen, BG_COLOR, self.rect)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 1)

        # Column headers
        hr = Rect(self.rect.x, self.rect.y, self.rect.width, self.header_h)
        pygame.draw.rect(screen, HEADER_BG, hr)
        cx = self.rect.x
        for title, w, _ in self.COLUMNS:
            col_w = w if w else self.rect.width - (cx - self.rect.x)
            txt = self.font.render(title, True, (240, 200, 50))
            screen.blit(txt, (cx + (col_w - txt.get_width()) // 2, self.rect.y + 14))
            cx += col_w

        # Row backgrounds + hover highlight
        start_y = self.rect.y + self.header_h
        mpos = pygame.mouse.get_pos()
        self.hover_index = None
        count = min(self.rows_per_page, len(self.matches) - self.page * self.rows_per_page)

        for i in range(count):
            gi = self.page * self.rows_per_page + i
            rr = Rect(self.rect.x, start_y + i * self.row_h, self.rect.width, self.row_h)
            if rr.collidepoint(mpos) and self.rect.collidepoint(mpos):
                pygame.draw.rect(screen, BG_HOVER, rr)
                self.hover_index = gi
            elif gi % 2 == 0:
                pygame.draw.rect(screen, BG_ALT, rr)

        if self._text_layer:
            screen.blit(self._text_layer, self.rect.topleft)
        self._draw_footer(screen)

    # -- Internals ------------------------------------------------------------

    def _pager_rects(self):
        y = self.rect.bottom - self.footer_h + 8
        return Rect(self.rect.x + 16, y, 80, 28), Rect(self.rect.right - 96, y, 80, 28)

    def _prerender(self):
        self._text_layer = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        start = self.page * self.rows_per_page
        visible = self.matches[start : start + self.rows_per_page]
        y = self.header_h

        for i, m in enumerate(visible):
            ry = y + i * self.row_h
            rcy = ry + self.row_h // 2
            data = [str(start + i + 1), m["stage"], abbreviate_teams(m["teams"]), m["date"], m["venue"]]
            xc = 0

            for (_, col_w, align), cell in zip(self.COLUMNS, data):
                w = col_w if col_w else self.rect.width - xc
                disp = truncate_text(self.font, cell, w - 16)
                surf = self.font.render(disp, True, TEXT_MUTED)
                tr = surf.get_rect()
                if align == "center":
                    tr.center = (xc + w // 2, rcy)
                else:
                    tr.midleft = (xc + 8, rcy)

                clip = Rect(xc, ry, w, self.row_h)
                self._text_layer.set_clip(clip)
                self._text_layer.blit(surf, tr)
                self._text_layer.set_clip(None)
                xc += w

    def _draw_footer(self, screen):
        fy = self.rect.bottom - self.footer_h
        pygame.draw.line(screen, BORDER_COLOR, (self.rect.x, fy), (self.rect.right, fy), 1)
        prev, nxt = self._pager_rects()

        def btn(rect, label, enabled):
            col = HEADER_BG if enabled else BG_ALT
            tc  = TEXT if enabled else TEXT_MUTED
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1, border_radius=6)
            t = self.font.render(label, True, tc)
            screen.blit(t, t.get_rect(center=rect.center))

        btn(prev, "Prev", self.page > 0)
        btn(nxt,  "Next", self.page < self.total_pages - 1)

        info = self.font.render(f"Page {self.page + 1} / {self.total_pages}", True, TEXT_MUTED)
        screen.blit(info, info.get_rect(center=(self.rect.centerx, fy + 22)))