from src.utilz.Constants import *
from src.utilz import lerp, clamp


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

    def update(self, player):
        self.target_x = player.rect.centerx - SCREEN_W * 0.35
        self.target_y = player.rect.centery - SCREEN_H * 0.45
        self.target_y = clamp(self.target_y, -200, SCREEN_H - SCREEN_H)
        self.x = lerp(self.x, self.target_x, 0.08)
        self.y = lerp(self.y, self.target_y, 0.06)
        self.x = max(0, self.x)