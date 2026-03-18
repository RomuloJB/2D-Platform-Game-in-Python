import math
import random

import pygame

from src.utilz.Constants import *


class Enemy:
    SIZE_W = 30
    SIZE_H = 32

    def __init__(self, x, y, platform_rect):
        self.rect = pygame.Rect(x, y, self.SIZE_W, self.SIZE_H)
        self.plat = platform_rect
        self.vx = random.choice([-1.5, 1.5])
        self.vy = 0
        self.on_ground = False
        self.alive = True
        self.health = 1
        self.anim = 0
        self.stunned = 0

    def update(self, platforms):
        if not self.alive:
            return

        if self.stunned > 0:
            self.stunned -= 1
            self.vx *= 0.85

        self.rect.x += int(self.vx)

        if self.rect.left <= self.plat.left or self.rect.right >= self.plat.right:
            self.vx *= -1

        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL)
        self.rect.y += int(self.vy)
        self.on_ground = False

        for plat in platforms:
            if plat.kind == "spike":
                continue
            if self.rect.colliderect(plat.rect):
                if self.vy > 0 and self.rect.bottom - int(self.vy) <= plat.rect.top + 5:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0
                    self.on_ground = True

        self.anim += 0.1

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        if rx < -60 or rx > SCREEN_W + 60:
            return

        squat = int(math.sin(self.anim) * 2)
        body_rect = pygame.Rect(rx, ry + squat, self.SIZE_W, self.SIZE_H - squat)
        color = C_ENEMY if self.stunned == 0 else (255, 120, 120)
        pygame.draw.rect(surf, color, body_rect, border_radius=4)

        eye_offset = 4 if self.vx > 0 else -4
        pygame.draw.circle(surf, C_ENEMY_EY, (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 10), 4)
        pygame.draw.circle(surf, C_ENEMY_EY, (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 10), 4)
        pygame.draw.circle(surf, (0, 0, 0), (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 11), 2)
        pygame.draw.circle(surf, (0, 0, 0), (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 11), 2)

        leg = int(math.sin(self.anim) * 5)
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + 4, ry + self.SIZE_H + squat - 2, 8, 8 + leg))
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + self.SIZE_W - 12, ry + self.SIZE_H + squat - 2, 8, 8 - leg))