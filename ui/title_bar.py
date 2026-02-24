import pygame
from functools import lru_cache


class TitleTheme:
    BG_TOP    = (10, 30, 80)
    BG_BOT    = (20, 60, 160)
    BORDER    = (200, 200, 210)
    TEXT_MAIN = (245, 245, 255)
    TEXT_SUB  = (240, 200, 50)


@lru_cache(maxsize=16)
def _make_bar(width, height, title, subtitle, font_main, font_sub):
    """Pre-render the title bar gradient + text so we only do it once per size/content combo."""
    surf = pygame.Surface((width, height))

    for y in range(height):
        t = y / height
        c = [int(TitleTheme.BG_TOP[i] + t * (TitleTheme.BG_BOT[i] - TitleTheme.BG_TOP[i])) for i in range(3)]
        pygame.draw.line(surf, c, (0, y), (width, y))

    pygame.draw.line(surf, TitleTheme.BORDER, (0, height - 1), (width, height - 1), 2)

    t_surf = font_main.render(title, True, TitleTheme.TEXT_MAIN)
    s_surf = font_sub.render(subtitle, True, TitleTheme.TEXT_SUB)
    surf.blit(t_surf, ((width - t_surf.get_width()) // 2, 6))
    surf.blit(s_surf, ((width - s_surf.get_width()) // 2, 32))

    return surf


def draw_title_bar(screen, rect, title, subtitle, font_main, font_sub):
    screen.blit(_make_bar(rect.width, rect.height, title, subtitle, font_main, font_sub), rect.topleft)