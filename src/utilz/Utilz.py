import pygame
from src.utilz.Constants import *


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def lerp_dt(current: float, target: float, smoothing: float, dt: float) -> float:
    """Lerp estável em relação ao tempo (frame-rate independent)."""
    return lerp(current, target, 1 - pow(smoothing, dt))


def draw_gradient_rect(surf, rect, color_top, color_bot):
    for y in range(rect.height):
        t = y / max(rect.height - 1, 1)
        r = int(lerp(color_top[0], color_bot[0], t))
        g = int(lerp(color_top[1], color_bot[1], t))
        b = int(lerp(color_top[2], color_bot[2], t))
        pygame.draw.line(surf, (r, g, b),
                         (rect.left, rect.top + y),
                         (rect.right - 1, rect.top + y))
