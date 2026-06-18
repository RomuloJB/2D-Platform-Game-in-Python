"""Coin — item coletável. Herda GameObject (categoria PICKUP). Flutua por tempo."""

import math
import random

import pygame

from src.objects.GameObject import GameObject
from src.utilz.Constants import SCREEN_W, Layer, C_COIN, C_COIN_S


class Coin(GameObject):
    R = 8

    def __init__(self, x, y):
        super().__init__(x - self.R, y - self.R, self.R * 2, self.R * 2,
                         category=Layer.PICKUP, mask=Layer.PLAYER)
        self.base_y = float(y)
        self.center_x = float(x)
        self.collected = False
        self.anim = random.uniform(0, math.pi * 2)

    # compat: alguns lugares antigos liam coin.x
    @property
    def x(self):
        return self.center_x

    def update(self, dt: float, world=None) -> None:
        self.anim += 4.2 * dt
        bob = math.sin(self.anim) * 4
        self.position.x = self.center_x - self.R
        self.position.y = self.base_y + bob - self.R
        self.sync_rect()

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.center_x - cam_x)
        sy = int(self.base_y + math.sin(self.anim) * 4 - cam_y)
        if -20 < sx < SCREEN_W + 20:
            pygame.draw.circle(surf, C_COIN, (sx, sy), self.R)
            pygame.draw.circle(surf, C_COIN_S, (sx - 2, sy - 2), 3)
