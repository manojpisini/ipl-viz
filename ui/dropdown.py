import pygame

THEME_BG     = (20, 60, 160)
THEME_HOVER  = (40, 90, 200)
THEME_BORDER = (200, 200, 210)
THEME_TEXT   = (245, 245, 255)
THEME_MUTED  = (180, 180, 190)
THEME_GOLD   = (240, 200, 50)
RADIUS       = 6
PAD_X        = 10


class Dropdown:
    """Season picker that expands into a scrollable list on click."""

    def __init__(self, x, y, w, h, options, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.font = font
        self.selected = 0
        self.open = False
        self.item_height = h

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False

        if self.rect.collidepoint(event.pos):
            self.open = not self.open
            return True

        if self.open:
            for i in range(len(self.options)):
                iy = self.rect.bottom + i * self.item_height
                ir = pygame.Rect(self.rect.x, iy, self.rect.width, self.item_height)
                if ir.collidepoint(event.pos):
                    self.selected = i
                    self.open = False
                    return True
            self.open = False

        return False

    def draw(self, screen):
        if self.selected >= len(self.options):
            self.selected = 0
        label = self.options[self.selected] if self.options else ""
        self._box(screen, self.rect, label, THEME_BG)

        # Gold dropdown arrow
        ax = self.rect.right - 18
        ay = self.rect.centery
        pygame.draw.polygon(screen, THEME_GOLD, [(ax - 4, ay - 2), (ax + 4, ay - 2), (ax, ay + 4)])

        if self.open:
            mpos = pygame.mouse.get_pos()
            for i, opt in enumerate(self.options):
                iy = self.rect.bottom + i * self.item_height
                ir = pygame.Rect(self.rect.x, iy, self.rect.width, self.item_height)
                bg = THEME_HOVER if ir.collidepoint(mpos) else THEME_BG
                fg = THEME_TEXT if i == self.selected else THEME_MUTED
                self._box(screen, ir, opt, bg, fg)

    def _box(self, screen, rect, text, bg, fg=THEME_TEXT):
        pygame.draw.rect(screen, bg, rect, border_radius=RADIUS)
        pygame.draw.rect(screen, THEME_BORDER, rect, 1, border_radius=RADIUS)
        surf = self.font.render(str(text), True, fg)
        screen.blit(surf, (rect.x + PAD_X, rect.y + (rect.height - surf.get_height()) // 2))