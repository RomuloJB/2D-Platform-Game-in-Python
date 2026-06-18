"""Bullet — projétil do player. Herda DynamicObject (sem gravidade).
Categoria PLAYER_SHOT; colide com ENEMY e PLATFORM. Limite de alcance por
distância percorrida (max_range), como no pull do colega."""

import math
import random

import pygame
from pygame.math import Vector2

from src.objects.DynamicObject import DynamicObject
from src.objects.Particle import Particle
from src.utilz.Constants import SCREEN_W, SCREEN_H, Layer, C_BULLET, C_BULLET_GL


class Bullet(DynamicObject):
    W = 10
    H = 7

    def __init__(self, x, y, vx, vy, damage=1, max_range=500, weapon_type="pistol"):
        super().__init__(x - self.W / 2, y - self.H / 2, self.W, self.H,
                         category=Layer.PLAYER_SHOT,
                         mask=Layer.ENEMY | Layer.PLATFORM,
                         use_gravity=False)
        self.velocity = Vector2(vx, vy)
        self.damage = damage
        self.max_range = max_range
        self.weapon_type = weapon_type
        self.scored = False
        self.traveled = 0.0
        self.trail = []

    def update(self, dt: float, world) -> None:
        if not self.alive:
            return

        self.trail.append((self.position.x + self.W / 2,
                           self.position.y + self.H / 2))
        if len(self.trail) > 6:
            self.trail.pop(0)

        step = self.velocity * dt
        self.position += step
        self.traveled += step.length()
        self.sync_rect()

        if self.traveled >= self.max_range:
            self.alive = False
            return

        for plat in world.platforms:
            if plat.kind != "spike" and self.rect.colliderect(plat.rect):
                self._impact(world.particles, hit_enemy=False)
                return

        for enemy in world.enemies:
            if enemy.alive and self.rect.colliderect(enemy.rect):
                killed = enemy.take_hit(self.damage)
                self._impact(world.particles, hit_enemy=True)
                self.scored = killed
                return

    def _impact(self, particles, hit_enemy):
        self.alive = False
        cx = self.position.x + self.W / 2
        cy = self.position.y + self.H / 2
        colors = (
            [(255, 200, 50), (255, 140, 0), (255, 80, 0)]
            if not hit_enemy
            else [(255, 220, 80), (255, 160, 30), (220, 60, 60)]
        )
        for _ in range(10):
            particles.append(Particle(
                cx, cy,
                random.uniform(-240, 240), random.uniform(-240, 60),
                0.33, random.choice(colors), random.randint(3, 5)
            ))
        particles.append(Particle(cx, cy, 0, 0, 0.1, (255, 255, 220), 6))

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        for i, (tx, ty) in enumerate(self.trail):
            t = (i + 1) / len(self.trail)
            r = int(255 * t)
            g = int(100 * t)
            s = max(1, int(4 * t))
            sx, sy = int(tx - cam_x), int(ty - cam_y)
            if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
                pygame.draw.circle(surf, (r, g, 0), (sx, sy), s)

        angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        sx = int(self.position.x + self.W / 2 - cam_x)
        sy = int(self.position.y + self.H / 2 - cam_y)
        if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
            col = C_BULLET_GL if self.damage > 1 else C_BULLET
            bsurf = pygame.Surface((self.W + 2, self.H + 2), pygame.SRCALPHA)
            pygame.draw.rect(bsurf, col, (0, 0, self.W, self.H), border_radius=3)
            pygame.draw.rect(bsurf, C_BULLET_GL, (2, 1, self.W - 4, self.H - 2), border_radius=2)
            rotated = pygame.transform.rotate(bsurf, angle)
            rr = rotated.get_rect(center=(sx, sy))
            surf.blit(rotated, rr)
