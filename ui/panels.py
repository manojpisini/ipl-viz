import pygame
from functools import lru_cache

_weather_lbl_font = None


def _lbl_font():
    """Lazy-init so we don't call SysFont before pygame.font.init()."""
    global _weather_lbl_font
    if _weather_lbl_font is None:
        _weather_lbl_font = pygame.font.SysFont("JetBrainsMono NF", 10)
    return _weather_lbl_font


class PanelTheme:
    BG_TOP  = (10, 30, 80)
    BG_BOT  = (5, 15, 40)
    BORDER  = (200, 200, 210)
    DIVIDER = (100, 100, 120)
    TITLE   = (240, 200, 50)
    SECTION = (200, 220, 255)
    LABEL   = (180, 180, 190)
    VALUE   = (245, 245, 255)
    RADIUS  = 12
    PAD_X   = 18
    PAD_Y   = 14
    COL_GAP = 20
    ROW_GAP = 8


@lru_cache(maxsize=32)
def _panel_bg(w, h):
    """Gradient background with rounded corners — cached by (width, height)."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        t = i / h
        c = [int(PanelTheme.BG_TOP[j] + t * (PanelTheme.BG_BOT[j] - PanelTheme.BG_TOP[j])) for j in range(3)]
        pygame.draw.line(surf, c + [255], (0, i), (w, i))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=PanelTheme.RADIUS)

    final = pygame.Surface((w, h), pygame.SRCALPHA)
    final.blit(surf, (0, 0))
    final.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(final, PanelTheme.BORDER, (0, 0, w, h), 1, border_radius=PanelTheme.RADIUS)
    return final


def _wrap(text, font, max_w):
    """Greedy word-wrap that avoids per-word Surface creation."""
    if not text:
        return []
    words = text.split(" ")
    lines, cur, cur_w = [], [], 0
    sp_w = font.size(" ")[0]
    for word in words:
        ww = font.size(word)[0]
        if cur_w + sp_w + ww <= max_w:
            cur.append(word)
            cur_w += sp_w + ww
        else:
            lines.append(" ".join(cur))
            cur, cur_w = [word], ww
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_panel(screen, x, y, w, h, title, lines, body_font, title_font):
    screen.blit(_panel_bg(w, h), (x, y))

    cx, cy = x + PanelTheme.PAD_X, y + PanelTheme.PAD_Y
    t_surf = title_font.render(title, True, PanelTheme.TITLE)
    screen.blit(t_surf, (cx, cy))

    cy += t_surf.get_height() + 10
    pygame.draw.line(screen, PanelTheme.DIVIDER, (cx, cy), (x + w - PanelTheme.PAD_X, cy), 1)
    cy += 12

    label_w = int(w * 0.40)
    val_x = cx + label_w + PanelTheme.COL_GAP
    max_val_w = w - (val_x - x) - PanelTheme.PAD_X
    max_y = y + h - 12

    for line in lines:
        if cy > max_y:
            break
        if not line.strip():
            cy += PanelTheme.ROW_GAP
            continue

        # Section header — ALL CAPS, no colon
        if line.isupper() and ":" not in line:
            h_surf = title_font.render(line, True, PanelTheme.SECTION)
            screen.blit(h_surf, (cx, cy))
            cy += h_surf.get_height() + 4
            pygame.draw.line(screen, PanelTheme.DIVIDER, (cx, cy), (x + w - PanelTheme.PAD_X, cy), 1)
            cy += 8
            continue

        # Key: Value pair — label on left, wrapped value on right
        if ":" in line:
            key, val = line.split(":", 1)
            k_surf = body_font.render(key.strip(), True, PanelTheme.LABEL)
            screen.blit(k_surf, (cx, cy))

            v_lines = _wrap(val.strip(), body_font, max_val_w)
            for i, v in enumerate(v_lines):
                v_surf = body_font.render(v, True, PanelTheme.VALUE)
                screen.blit(v_surf, (val_x, cy + i * body_font.get_height()))
            cy += max(k_surf.get_height(), len(v_lines) * body_font.get_height()) + PanelTheme.ROW_GAP
        else:
            # Free-form text
            for p in _wrap(line, body_font, w - 2 * PanelTheme.PAD_X):
                p_surf = body_font.render(p, True, PanelTheme.VALUE)
                screen.blit(p_surf, (cx, cy))
                cy += body_font.get_height()
            cy += PanelTheme.ROW_GAP


def draw_weather_panel(screen, x, y, w, h, weather_data, icons, font_body, font_title):
    draw_panel(screen, x, y, w, h, "Weather", [], font_body, font_title)

    ox, oy = x + 24, y + 50
    col_gap = 140

    if not weather_data or weather_data.get("air_temp") is None:
        screen.blit(font_body.render("Data Unavailable", True, (150, 150, 150)), (ox, oy))
        return

    items = [
        (f"Feels {weather_data.get('feels_like', '?')}", weather_data["air_temp"], "temp_hot"),
        ("Humidity", weather_data["humidity"], "humid"),
        ("Wind",     weather_data["wind"],     "wind"),
        ("Rain",     weather_data["rain"],     "rain_drop"),
    ]

    ICON_SZ, TXT_OFF = 36, 36

    for i, (label, val, icon_key) in enumerate(items):
        col, row = i % 2, i // 2
        px = ox + col * col_gap
        py = oy + row * 54          # 36 * 1.5

        icon = icons.get(icon_key)
        if icon:
            ix = px + (ICON_SZ - icon.get_width()) // 2
            iy = py + (ICON_SZ - icon.get_height()) // 2
            screen.blit(icon, (ix, iy))

        screen.blit(font_body.render(str(val), True, PanelTheme.VALUE), (px + TXT_OFF, py + 4))
        screen.blit(_lbl_font().render(label, True, PanelTheme.LABEL), (px + TXT_OFF, py + 22))

    # Summary row below the 2×2 grid
    sum_y = oy + 2 * 54 + 12
    pygame.draw.line(screen, PanelTheme.DIVIDER, (x + 20, sum_y - 8), (x + w - 20, sum_y - 8), 1)

    main_icon = icons.get(weather_data.get("icon", "cloudy"))
    txt_x = ox
    if main_icon:
        screen.blit(main_icon, (ox, sum_y))
        txt_x += main_icon.get_width() + 24

    summary = weather_data.get("summary", "Unknown")
    s_surf = font_title.render(summary, True, PanelTheme.TITLE)
    icon_h = main_icon.get_height() if main_icon else 32
    screen.blit(s_surf, (txt_x, sum_y + (icon_h - s_surf.get_height()) // 2))