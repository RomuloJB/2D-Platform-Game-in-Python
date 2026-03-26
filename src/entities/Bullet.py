import math
import random

import pygame

from src.utilz.Constants import *
from src.objects.Particle import Particle


class Bullet:
    W = 10
    H = 7

    def __init__(self, x, y, vx, vy, damage=10, max_range=500, weapon_type="pistol"):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.max_range = max_range
        self.weapon_type = weapon_type
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.scored = False
        self.trail = []

    def update(self, enemies, platforms, particles):
        if not self.alive:
            return

        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        bullet_rect = pygame.Rect(
            int(self.x - self.W // 2),
            int(self.y - self.H // 2),
            self.W, self.H
        )

        for plat in platforms:
            if plat.kind != "spike" and bullet_rect.colliderect(plat.rect):
                self._impact(particles, hit_enemy=False)
                return

        for enemy in enemies:
            if enemy.alive and bullet_rect.colliderect(enemy.rect):
                enemy.alive = False
                self._impact(particles, hit_enemy=True)
                self.scored = True
                return

    def _impact(self, particles, hit_enemy):
        self.alive = False
        colors = (
            [(255, 200, 50), (255, 140, 0), (255, 80, 0)]
            if not hit_enemy
            else [(255, 220, 80), (255, 160, 30), (220, 60, 60)]
        )
        for _ in range(10):
            particles.append(Particle(
                self.x, self.y,
                random.uniform(-4, 4), random.uniform(-4, 1),
                20, random.choice(colors), random.randint(3, 5)
            ))
        particles.append(Particle(self.x, self.y, 0, 0, 6, (255, 255, 220), 6))

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

        angle = math.degrees(math.atan2(-self.vy, self.vx))
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
            bsurf = pygame.Surface((self.W + 2, self.H + 2), pygame.SRCALPHA)
            pygame.draw.rect(bsurf, C_BULLET,    (0, 0, self.W, self.H), border_radius=3)
            pygame.draw.rect(bsurf, C_BULLET_GL, (2, 1, self.W - 4, self.H - 2), border_radius=2)
            rotated = pygame.transform.rotate(bsurf, angle)
            rr = rotated.get_rect(center=(sx, sy))
            surf.blit(rotated, rr)