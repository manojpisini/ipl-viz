import pygame

BG        = (10, 30, 80)
BTN_ON    = (240, 200, 50)
BTN_OFF   = (20, 60, 160)
TXT_ON    = (20, 20, 25)
TXT_OFF   = (245, 245, 255)
BORDER    = (200, 200, 210)


class ViewSelector:
    """Sidebar tab strip — lets the user swap between the five view modes."""

    TABS = [
        ("FIELD",      "view_field"),
        ("TEAMS",      "view_teams"),
        ("SCORECARD",  "view_batting"),
        ("SUMMARY",    "view_bowling"),
        ("STANDINGS",  "view_points"),
    ]

    def __init__(self, x, y, w, font):
        self.rect = pygame.Rect(x, y, w, 220)
        self.font = font
        self.btn_rects = {}
        self._layout()

    def _layout(self):
        btn_h, gap = 32, 8
        y = self.rect.y + 16
        for _, key in self.TABS:
            self.btn_rects[key] = pygame.Rect(self.rect.x + 12, y, self.rect.width - 24, btn_h)
            y += btn_h + gap

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.btn_rects.items():
                if rect.collidepoint(event.pos):
                    return key
        return None

    def draw(self, screen, current_view):
        pygame.draw.rect(screen, BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, self.rect, 1, border_radius=12)

        for label, key in self.TABS:
            rect = self.btn_rects[key]
            active = key == current_view
            bg = BTN_ON if active else BTN_OFF
            fg = TXT_ON if active else TXT_OFF

            pygame.draw.rect(screen, bg, rect, border_radius=6)
            if not active:
                pygame.draw.rect(screen, (100, 100, 120), rect, 1, border_radius=6)

            txt = self.font.render(label, True, fg)
            screen.blit(txt, txt.get_rect(center=rect.center))