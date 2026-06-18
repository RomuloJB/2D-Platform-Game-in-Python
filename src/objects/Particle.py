"""Particle — efeito visual. Herda GameObject. Vida/velocidade em por-segundo (dt)."""

import pygame
from pygame.math import Vector2

from src.objects.GameObject import GameObject
from src.utilz.Constants import SCREEN_W, SCREEN_H, Layer

_PARTICLE_GRAVITY = 0.2 * 60 * 60
_PARTICLE_DRAG = pow(0.95, 60)


class Particle(GameObject):
    def __init__(self, x, y, vx, vy, life, color, size=4):
        super().__init__(x, y, size, size, Layer.NONE, Layer.NONE)
        self.velocity = Vector2(vx, vy)
        self.life = self.max_life = life
        self.color = color
        self.size = size

    def update(self, dt: float, world=None) -> None:
        self.position += self.velocity * dt
        self.velocity.y += _PARTICLE_GRAVITY * dt
        self.velocity.x *= pow(_PARTICLE_DRAG, dt)
        self.life -= dt
        if self.life <= 0:
            self.alive = False
        self.sync_rect()

    def draw(self, surf, cam_x, cam_y):
        alpha = max(0.0, self.life / self.max_life)
        s = max(1, int(self.size * alpha))
        sx = int(self.position.x - cam_x)
        sy = int(self.position.y - cam_y)
        if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
            pygame.draw.circle(surf, self.color, (sx, sy), s)
