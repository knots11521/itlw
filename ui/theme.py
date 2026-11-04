"""Theme definitions and drawing helpers."""
import pygame
import config as cfg


class Theme:
    def __init__(self):
        self.colors = {
            'bg': cfg.COLOR_BACKGROUND,
            'card': cfg.COLOR_CARD,
            'surface': cfg.COLOR_CARD,
            'accent_primary': cfg.COLOR_ACCENT_PRIMARY,
            'accent_secondary': cfg.COLOR_ACCENT_SECONDARY,
            'core': cfg.COLOR_CORE,
            'flux': cfg.COLOR_FLUX,
            'text': cfg.COLOR_TEXT,
            'text_subtle': cfg.COLOR_TEXT_SUBTLE,
            'border': cfg.COLOR_BORDER,
            'button': cfg.COLOR_CARD,
            'button_hover': cfg.COLOR_BUTTON_HOVER,
            'button_pressed': cfg.COLOR_BUTTON_PRESSED,
            'input': (255, 255, 255),
            'result': (250, 250, 250),
            'simulation': (18, 18, 18),
            'focus': (18, 18, 18),
            'success': (18, 18, 18),
            'warning': (18, 18, 18),
            'danger': (18, 18, 18),
        }
        self.font_cache = {}

    def get_font(self, size, bold=False, italic=False):
        key = (size, bold, italic)
        if key not in self.font_cache:
            try:
                self.font_cache[key] = pygame.font.SysFont(
                    cfg.FONT_FAMILY, size, bold=bold, italic=italic
                )
            except Exception:
                try:
                    self.font_cache[key] = pygame.font.SysFont(
                        "Arial", size, bold=bold, italic=italic
                    )
                except Exception:
                    self.font_cache[key] = pygame.font.Font(None, size)
        return self.font_cache[key]

    def render_text(self, text, size, color=None, bold=False, italic=False, antialias=True):
        font = self.get_font(size, bold, italic)
        color = color if color is not None else self.colors['text']
        return font.render(text, antialias, color)


def init_fonts():
    try:
        pygame.font.init()
    except Exception:
        pass


def draw_rounded_rect(surface, color, rect, radius=None, border_width=0, border_color=None):
    radius = cfg.CORNER_RADIUS if radius is None else radius
    rect = pygame.Rect(rect)
    if border_width == 0:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        return
    if border_color is None:
        border_color = (100, 100, 100)
    pygame.draw.rect(surface, border_color, rect, border_radius=radius)
    inner_rect = rect.inflate(-border_width * 2, -border_width * 2)
    pygame.draw.rect(surface, color, inner_rect, border_radius=radius)


def draw_aa_line(surface, color, start_pos, end_pos, width=1):
    try:
        pygame.draw.aaline(surface, color, start_pos, end_pos)
    except Exception:
        pygame.draw.line(surface, color, start_pos, end_pos, width)
