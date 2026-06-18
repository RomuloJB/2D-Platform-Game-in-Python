"""Platform — chão/plataforma. Herda GameObject. 'moving' oscila por tempo."""

import math
import random

import pygame

from src.objects.GameObject import GameObject
from src.utilz.Constants import (
    SCREEN_W, Layer, C_PLATFORM, C_PLAT_TOP, C_PLAT_DARK,
    C_GROUND, C_GROUND_T, C_SPIKE,
)
from src.utilz.Utilz import draw_gradient_rect


class Platform(GameObject):
    def __init__(self, x, y, w, h, kind="normal"):
        category = Layer.HAZARD if kind == "spike" else Layer.PLATFORM
        super().__init__(x, y, w, h, category=category, mask=Layer.NONE)
        self.kind = kind
        self.move_range = 0.0
        self.move_speed = 0.0
        self.origin_x = float(x)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, dt: float, world=None) -> None:
        if self.kind == "moving":
            t = world.time_elapsed if world is not None else 0.0
            self.position.x = (
                self.origin_x
                + math.sin(t * self.move_speed * 60 + self.phase) * self.move_range
            )
            self.sync_rect()

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
            for sx in range(int(rx), int(rx) + self.rect.w, sw):
                pts = [(sx, ry + 10), (sx + sw // 2, ry), (sx + sw, ry + 10)]
                pygame.draw.polygon(surf, C_SPIKE, pts)
        elif self.kind == "ground":
            draw_gradient_rect(surf, r, C_GROUND_T, C_GROUND)
            pygame.draw.rect(surf, (120, 160, 60), pygame.Rect(rx, ry, self.rect.w, 6))
        else:
            draw_gradient_rect(surf, r, C_PLAT_TOP, C_PLAT_DARK)
            pygame.draw.rect(surf, C_PLAT_TOP, pygame.Rect(rx, ry, self.rect.w, 4))
