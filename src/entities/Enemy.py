import math
import random

import pygame

from src.utilz.Constants import *


class EnemyBullet:
    SIZE = 6

    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.vx = direction * 4
        self.vy = 0
        self.alive = True

    def update(self, platforms):
        self.rect.x += int(self.vx)
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL)
        self.rect.y += int(self.vy)

        for plat in platforms:
            if plat.kind == "spike":
                continue
            if self.rect.colliderect(plat.rect):
                self.alive = False
                return

        if self.rect.x < -200 or self.rect.x > SCREEN_W + 200:
            self.alive = False

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        pygame.draw.circle(surf, (255, 80, 20), (rx + self.SIZE // 2, ry + self.SIZE // 2), self.SIZE // 2)
        pygame.draw.circle(surf, (255, 200, 100), (rx + self.SIZE // 2, ry + self.SIZE // 2), self.SIZE // 4)


class Enemy:
    SIZE_W = 30
    SIZE_H = 32

    MELEE = "melee"
    RANGED = "ranged"

    MELEE_ATTACK_COOLDOWN = 60
    RANGED_ATTACK_COOLDOWN = 120
    RANGED_DETECT_RANGE = 280

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
        self.kind = random.choice([self.MELEE, self.RANGED])
        self.attack_timer = 0
        self.bullets = []
        self.is_shooting = 0

    def _try_melee_attack(self, player_rect):
        if self.attack_timer > 0 or not self.on_ground:
            return
        if self.rect.inflate(20, 0).colliderect(player_rect):
            self.attack_timer = self.MELEE_ATTACK_COOLDOWN
            self.stunned = 8
            return True
        return False

    def _try_ranged_attack(self, player_rect):
        if self.attack_timer > 0 or not self.on_ground:
            return
        dx = (player_rect.centerx - self.rect.centerx)
        dy = abs(player_rect.centery - self.rect.centery)
        if abs(dx) < self.RANGED_DETECT_RANGE and dy < 80:
            direction = 1 if dx > 0 else -1
            bx = self.rect.centerx - EnemyBullet.SIZE // 2
            by = self.rect.centery - EnemyBullet.SIZE // 2
            self.bullets.append(EnemyBullet(bx, by, direction))
            self.attack_timer = self.RANGED_ATTACK_COOLDOWN
            self.is_shooting = 12

    def update(self, platforms, player_rect=None):
        if not self.alive:
            return

        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.is_shooting > 0:
            self.is_shooting -= 1

        if self.stunned > 0:
            self.stunned -= 1
            self.vx *= 0.85

        if self.kind == self.RANGED and self.is_shooting == 0:
            self.rect.x += int(self.vx)
        elif self.kind == self.MELEE:
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

        if player_rect is not None:
            if self.kind == self.MELEE:
                self._try_melee_attack(player_rect)
            else:
                self._try_ranged_attack(player_rect)

        for b in self.bullets:
            b.update(platforms)
        self.bullets = [b for b in self.bullets if b.alive]

        self.anim += 0.1

    def get_bullets(self):
        return self.bullets

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        if rx < -60 or rx > SCREEN_W + 60:
            return

        for b in self.bullets:
            b.draw(surf, cam_x, cam_y)

        squat = int(math.sin(self.anim) * 2)
        body_rect = pygame.Rect(rx, ry + squat, self.SIZE_W, self.SIZE_H - squat)

        if self.kind == self.MELEE:
            base_color = C_ENEMY
        else:
            base_color = (100, 60, 180)

        color = base_color if self.stunned == 0 else (255, 120, 120)

        pygame.draw.rect(surf, color, body_rect, border_radius=4)

        if self.kind == self.RANGED:
            accent_rect = pygame.Rect(rx + 2, ry + squat + 2, self.SIZE_W - 4, 6)
            pygame.draw.rect(surf, (160, 100, 220), accent_rect, border_radius=2)

        eye_offset = 4 if self.vx > 0 else -4
        pygame.draw.circle(surf, C_ENEMY_EY, (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 10), 4)
        pygame.draw.circle(surf, C_ENEMY_EY, (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 10), 4)
        pygame.draw.circle(surf, (0, 0, 0), (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 11), 2)
        pygame.draw.circle(surf, (0, 0, 0), (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 11), 2)

        if self.kind == self.MELEE:
            arm_extend = 10 if self.attack_timer > self.MELEE_ATTACK_COOLDOWN - 10 else 0
            side = 1 if self.vx > 0 else -1
            arm_x = rx + self.SIZE_W // 2 + side * (12 + arm_extend)
            arm_y = ry + 18 + squat
            pygame.draw.line(surf, (160, 40, 40),
                (rx + self.SIZE_W // 2, ry + 18 + squat), (arm_x, arm_y), 3)
            pygame.draw.rect(surf, (200, 60, 40),
                pygame.Rect(arm_x - 3, arm_y - 5, 6, 10), border_radius=2)
        else:
            gun_side = 1 if self.vx > 0 else -1
            gun_x = rx + self.SIZE_W // 2 + gun_side * 8
            gun_y = ry + 20 + squat
            barrel_end = rx + self.SIZE_W // 2 + gun_side * 20
            pygame.draw.line(surf, (80, 80, 80), (gun_x, gun_y), (barrel_end, gun_y), 4)
            pygame.draw.rect(surf, (60, 60, 60),
                pygame.Rect(gun_x - 4, gun_y - 4, 8, 8), border_radius=2)
            if self.is_shooting > 0:
                flash_r = self.is_shooting // 2 + 2
                pygame.draw.circle(surf, (255, 200, 50), (barrel_end, gun_y), flash_r)

        leg = int(math.sin(self.anim) * 5)
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + 4, ry + self.SIZE_H + squat - 2, 8, 8 + leg))
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + self.SIZE_W - 12, ry + self.SIZE_H + squat - 2, 8, 8 - leg))