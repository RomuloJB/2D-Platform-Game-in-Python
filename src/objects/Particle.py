import pygame
from src.utilz.Constants import *

class Particle:
    def __init__(self, x, y, vx, vy, life, color, size=4):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.vx *= 0.95
        self.life -= 1

    def draw(self, surf, cam_x, cam_y):
        alpha = self.life / self.max_life
        s = max(1, int(self.size * alpha))
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
            pygame.draw.circle(surf, self.color, (sx, sy), s)