import math
import random

import pygame

from src.utilz.Constants import *
from src.utilz.Utilz import draw_gradient_rect


class Platform:
    def __init__(self, x, y, w, h, kind="normal"):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind
        self.move_range = 0
        self.move_speed = 0
        self.origin_x = x
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, tick):
        if self.kind == "moving":
            self.rect.x = int(
                self.origin_x +
                math.sin(tick * self.move_speed + self.phase) * self.move_range
            )

    def draw(self, surf, cam_x, cam_y):
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        r = pygame.Rect(rx, ry, self.rect.w, self.rect.h)
        if r.right < -10 or r.left > SCREEN_W + 10:
            return

        if self.kind == "spike":
            base = pygame.Rect(rx, ry + 10, self.rect.w, self.rect.h - 10)
            pygame.draw.rect(surf, C_PLATFORM, base)
            sw = 14
            for sx in range(rx, rx + self.rect.w, sw):
                pts = [(sx, ry + 10), (sx + sw // 2, ry), (sx + sw, ry + 10)]
                pygame.draw.polygon(surf, C_SPIKE, pts)
        elif self.kind == "ground":
            draw_gradient_rect(surf, r, C_GROUND_T, C_GROUND)
            pygame.draw.rect(surf, (120, 160, 60), pygame.Rect(rx, ry, self.rect.w, 6))
        else:
            draw_gradient_rect(surf, r, C_PLAT_TOP, C_PLAT_DARK)
            pygame.draw.rect(surf, C_PLAT_TOP, pygame.Rect(rx, ry, self.rect.w, 4))