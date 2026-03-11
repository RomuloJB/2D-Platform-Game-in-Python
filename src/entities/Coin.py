import pygame
from src.utilz.Constants import *
import math
import random

class Coin:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.base_y = y
        self.collected = False
        self.anim = random.uniform(0, math.pi * 2)

    def update(self):
        self.anim += 0.07

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.base_y + math.sin(self.anim) * 4 - cam_y)
        if -20 < sx < SCREEN_W + 20:
            pygame.draw.circle(surf, C_COIN, (sx, sy), 8)
            pygame.draw.circle(surf, C_COIN_S, (sx - 2, sy - 2), 3)