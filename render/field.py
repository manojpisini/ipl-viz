import pygame
import math

# Ground palette
GRASS_DARK  = (18, 42, 22)
GRASS_LIGHT = (34, 68, 40)
WHITE       = (240, 240, 240)
GRAY        = (170, 170, 170)
PITCH_LIGHT = (170, 145, 110)
PITCH_DARK  = (150, 125, 95)
LINE_W      = 1

# Real-world pitch / crease dimensions in metres
PITCH_LEN  = 20.12
PITCH_WID  = 3.05
BOWL_CREASE_HALF = 2.64
POP_CREASE_HALF  = 3.20
CREASE_EXT       = 1.50
THIRTY_YARD_R    = 27.432
OUTER_GAP        = 6.0
OUTER_RING_W     = 4


class FieldRenderer:
    """
    Renders the cricket ground once into an off-screen surface, then blits
    that cached texture every frame.  Only regenerates when the window is
    resized or a different stadium is loaded.
    """

    def __init__(self):
        self._surface = None
        self._dims = (0, 0)
        self._stadium_name = None

    def _m2px(self, metres, scale):
        return int(round(metres * scale))

    def _dotted_circle(self, surf, center, radius, dots=60):
        """30-yard circle markers — small dots equally spaced around the arc."""
        cx, cy = center
        step = 2 * math.pi / dots
        for i in range(dots):
            a = i * step
            x = int(cx + radius * math.cos(a))
            y = int(cy + radius * math.sin(a))
            pygame.draw.circle(surf, (190, 190, 190), (x, y), 2)

    def _grass_gradient(self, surf, center, max_r):
        """
        Radial gradient from dark outfield to lighter centre.  Expensive
        loop, but it only runs on cache refresh (~once or twice per session).
        """
        steps = 160
        for i in range(steps):
            t = i / steps
            r = int(max_r * (1 - t))
            if r <= 0:
                continue
            c = tuple(int(GRASS_DARK[j] + t * (GRASS_LIGHT[j] - GRASS_DARK[j])) for j in range(3))
            pygame.draw.circle(surf, c, center, r)

        # Mowing rings — barely visible stripes that sell the broadcast look
        ring_col = (26, 54, 32)
        for r in range(0, max_r, 22):
            pygame.draw.circle(surf, ring_col, center, r, 1)

    def render(self, screen, stadium):
        w, h = screen.get_size()

        if (w, h) != self._dims or stadium.name != self._stadium_name:
            self._rebuild(w, h, stadium)
            self._dims = (w, h)
            self._stadium_name = stadium.name

        screen.blit(self._surface, (0, 0))

    def _rebuild(self, w, h, stadium):
        self._surface = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        center = (cx, cy)

        max_r = min(w, h) // 2 - 180
        scale = max_r / (min(stadium.width_m, stadium.length_m) / 2)

        self._grass_gradient(self._surface, center, max_r + 80)

        # Boundary ellipse — shaped to match real ground dimensions
        bw = self._m2px(stadium.width_m / 2, scale)
        bh = self._m2px(stadium.length_m / 2, scale)
        boundary = pygame.Rect(cx - bw, cy - bh, bw * 2, bh * 2)
        pygame.draw.ellipse(self._surface, WHITE, boundary, LINE_W)

        # Outer spectator ring
        gap = self._m2px(OUTER_GAP, scale)
        outer = boundary.inflate(gap * 2, gap * 2)
        pygame.draw.ellipse(self._surface, (200, 200, 200), outer, OUTER_RING_W)

        self._dotted_circle(self._surface, center, self._m2px(THIRTY_YARD_R, scale))

        # Pitch rectangle with alternating soil-tone stripes
        pw = self._m2px(PITCH_WID, scale)
        pl = self._m2px(PITCH_LEN, scale)
        pitch = pygame.Rect(0, 0, pw, pl)
        pitch.center = center

        pygame.draw.rect(self._surface, PITCH_LIGHT, pitch)
        stripe = 6
        for y in range(pitch.top, pitch.bottom, stripe * 2):
            pygame.draw.rect(self._surface, PITCH_DARK, (pitch.left, y, pw, stripe))
        pygame.draw.rect(self._surface, WHITE, pitch, LINE_W)

        # Bowling + popping creases at both ends
        bc = self._m2px(BOWL_CREASE_HALF + 2 * CREASE_EXT, scale)
        pc = self._m2px(POP_CREASE_HALF + 12 * CREASE_EXT, scale)
        pop_off = self._m2px(1.22, scale)

        for sign in (-1, 1):
            by = pitch.bottom if sign == 1 else pitch.top
            pygame.draw.line(self._surface, WHITE, (cx - bc // 2, by), (cx + bc // 2, by), LINE_W)
            py = by - sign * pop_off
            pygame.draw.line(self._surface, WHITE, (cx - pc // 2, py), (cx + pc // 2, py), LINE_W)


# Module-level singleton — avoids re-instantiating per frame
_renderer = FieldRenderer()


def draw_field(screen, stadium):
    _renderer.render(screen, stadium)