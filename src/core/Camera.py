"""Camera — segue o player com suavização estável por dt."""

from src.utilz.Constants import SCREEN_W, SCREEN_H
from src.utilz.Utilz import lerp_dt, clamp


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, player, dt: float):
        target_x = player.rect.centerx - SCREEN_W * 0.35
        target_y = player.rect.centery - SCREEN_H * 0.45
        target_y = clamp(target_y, -200, 0)
        self.x = lerp_dt(self.x, target_x, 0.0067, dt)
        self.y = lerp_dt(self.y, target_y, 0.024, dt)
        self.x = max(0, self.x)
