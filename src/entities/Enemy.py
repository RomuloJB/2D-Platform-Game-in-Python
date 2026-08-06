"""
Enemy — herda Character (lógica de batalha). EnemyBullet — herda DynamicObject.
Física em dt; desenho idêntico ao original.
"""

import math
import random

import pygame
from pygame.math import Vector2

from src.entities.Character import Character
from src.objects.DynamicObject import DynamicObject
from src.utilz.Constants import SCREEN_W, Layer, GRAVITY, MAX_FALL, C_ENEMY, C_ENEMY_EY


class EnemyBullet(DynamicObject):
    SIZE = 6

    def __init__(self, x, y, direction):
        super().__init__(x, y, self.SIZE, self.SIZE,
                         category=Layer.ENEMY_SHOT,
                         mask=Layer.PLATFORM | Layer.PLAYER,
                         use_gravity=True)
        self.velocity = Vector2(direction * 4 * 60, 0)

    def update(self, dt: float, world=None) -> None:
        platforms = world.platforms if world is not None else []
        self.position.x += self.velocity.x * dt
        self.velocity.y += GRAVITY * dt
        if self.velocity.y > MAX_FALL:
            self.velocity.y = MAX_FALL
        self.position.y += self.velocity.y * dt
        self.sync_rect()

        for plat in platforms:
            if plat.kind == "spike":
                continue
            if self.rect.colliderect(plat.rect):
                self.alive = False
                return

        if self.position.x < -200 or self.position.x > SCREEN_W + 4000:
            self.alive = False

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        pygame.draw.circle(surf, (255, 80, 20),
            (rx + self.SIZE // 2, ry + self.SIZE // 2), self.SIZE // 2)
        pygame.draw.circle(surf, (255, 200, 100),
            (rx + self.SIZE // 2, ry + self.SIZE // 2), self.SIZE // 4)


class Enemy(Character):
    SIZE_W = 30
    SIZE_H = 32

    MELEE = "melee"
    RANGED = "ranged"

    MELEE_ATTACK_COOLDOWN = 60 / 60
    RANGED_ATTACK_COOLDOWN = 120 / 60
    RANGED_DETECT_RANGE = 280

    def __init__(self, x, y, platform_rect, speed_mult=1.0, hp=1):
        super().__init__(x, y, self.SIZE_W, self.SIZE_H,
                         category=Layer.ENEMY,
                         mask=Layer.PLATFORM,
                         use_gravity=True, max_health=hp)
        self.plat = platform_rect
        base_speed = random.choice([-1.5, 1.5]) * 60
        self.velocity.x = base_speed * speed_mult
        self.stunned = 0.0
        self.kind = random.choice([self.MELEE, self.RANGED])
        self.attack_timer = 0.0
        self.bullets = []
        self.is_shooting = 0.0

    def _try_melee_attack(self, player_rect):
        if self.attack_timer > 0 or not self.on_ground:
            return False
        if self.rect.inflate(20, 0).colliderect(player_rect):
            self.attack_timer = self.MELEE_ATTACK_COOLDOWN
            self.stunned = 8 / 60
            return True
        return False

    def _try_ranged_attack(self, player_rect):
        if self.attack_timer > 0 or not self.on_ground:
            return
        dx = player_rect.centerx - self.rect.centerx
        dy = abs(player_rect.centery - self.rect.centery)
        if abs(dx) < self.RANGED_DETECT_RANGE and dy < 80:
            direction = 1 if dx > 0 else -1
            bx = self.rect.centerx - EnemyBullet.SIZE // 2
            by = self.rect.centery - EnemyBullet.SIZE // 2
            self.bullets.append(EnemyBullet(bx, by, direction))
            self.attack_timer = self.RANGED_ATTACK_COOLDOWN
            self.is_shooting = 12 / 60

    def take_hit(self, amount=1):
        """Reduz HP; retorna True se morreu."""
        self.health -= amount
        self.stunned = 10 / 60
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False

    def update(self, dt: float, world) -> None:
        if not self.alive:
            return
        player_rect = world.player.rect if world.player else None

        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.is_shooting = max(0.0, self.is_shooting - dt)
        if self.stunned > 0:
            self.stunned = max(0.0, self.stunned - dt)
            self.velocity.x *= pow(0.85, dt * 60)

        moving = not (self.kind == self.RANGED and self.is_shooting > 0)
        if moving:
            self.position.x += self.velocity.x * dt
            self.sync_rect()

        # Patrulha: vira ao chegar na borda da plataforma.
        # So inverte se estiver indo EM DIRECAO a borda (evita re-inverter todo
        # frame quando o inimigo fica preso na zona de borda), e reposiciona o
        # inimigo para dentro dos limites (clamp) para nunca ficar "flicando".
        min_x = self.plat.left
        max_x = self.plat.right - self.rect.w
        # margem minima de patrulha; abaixo disso, nao vale a pena andar (e e
        # onde o flicker aparece). Centraliza e fica parado.
        if max_x - min_x < 4:
            self.rect.x = (self.plat.left + self.plat.right) // 2 - self.rect.w // 2
            self.velocity.x = 0
            self.sync_position()
        else:
            if self.rect.left <= self.plat.left and self.velocity.x < 0:
                self.velocity.x *= -1
            elif self.rect.right >= self.plat.right and self.velocity.x > 0:
                self.velocity.x *= -1
            # mantem o inimigo dentro da plataforma
            if self.rect.x < min_x:
                self.rect.x = min_x
                self.sync_position()
            elif self.rect.x > max_x:
                self.rect.x = max_x
                self.sync_position()

        self.velocity.y += GRAVITY * dt
        if self.velocity.y > MAX_FALL:
            self.velocity.y = MAX_FALL
        self.position.y += self.velocity.y * dt
        self.sync_rect()
        self.on_ground = False
        for plat in world.platforms:
            if plat.kind == "spike":
                continue
            if self.rect.colliderect(plat.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = plat.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.sync_position()

        if player_rect is not None:
            if self.kind == self.MELEE:
                if self._try_melee_attack(player_rect):
                    world.player.take_damage(world.particles)
            else:
                self._try_ranged_attack(player_rect)

        for b in self.bullets:
            b.update(dt, world)
        if player_rect is not None:
            for b in self.bullets:
                if b.alive and b.rect.colliderect(player_rect):
                    world.player.take_damage(world.particles)
                    b.alive = False
        self.bullets = [b for b in self.bullets if b.alive]

        self.anim += 6 * dt

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

        base_color = C_ENEMY if self.kind == self.MELEE else (100, 60, 180)
        color = base_color if self.stunned == 0 else (255, 120, 120)
        pygame.draw.rect(surf, color, body_rect, border_radius=4)

        if self.kind == self.RANGED:
            accent = pygame.Rect(rx + 2, ry + squat + 2, self.SIZE_W - 4, 6)
            pygame.draw.rect(surf, (160, 100, 220), accent, border_radius=2)

        vx = self.velocity.x
        eye_offset = 4 if vx > 0 else -4
        pygame.draw.circle(surf, C_ENEMY_EY,
            (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 10), 4)
        pygame.draw.circle(surf, C_ENEMY_EY,
            (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 10), 4)
        pygame.draw.circle(surf, (0, 0, 0),
            (rx + self.SIZE_W // 2 + eye_offset - 4, ry + 11), 2)
        pygame.draw.circle(surf, (0, 0, 0),
            (rx + self.SIZE_W // 2 + eye_offset + 4, ry + 11), 2)

        if self.max_health > 1:
            bar_w = self.SIZE_W
            filled = int(bar_w * self.health / self.max_health)
            pygame.draw.rect(surf, (60, 20, 20), pygame.Rect(rx, ry - 8, bar_w, 4))
            pygame.draw.rect(surf, (220, 60, 60), pygame.Rect(rx, ry - 8, filled, 4))

        if self.kind == self.MELEE:
            arm_extend = 10 if self.attack_timer > self.MELEE_ATTACK_COOLDOWN - 10 / 60 else 0
            side = 1 if vx > 0 else -1
            arm_x = rx + self.SIZE_W // 2 + side * (12 + arm_extend)
            arm_y = ry + 18 + squat
            pygame.draw.line(surf, (160, 40, 40),
                (rx + self.SIZE_W // 2, ry + 18 + squat), (arm_x, arm_y), 3)
            pygame.draw.rect(surf, (200, 60, 40),
                pygame.Rect(arm_x - 3, arm_y - 5, 6, 10), border_radius=2)
        else:
            gun_side = 1 if vx > 0 else -1
            gun_x = rx + self.SIZE_W // 2 + gun_side * 8
            gun_y = ry + 20 + squat
            barrel_end = rx + self.SIZE_W // 2 + gun_side * 20
            pygame.draw.line(surf, (80, 80, 80), (gun_x, gun_y), (barrel_end, gun_y), 4)
            pygame.draw.rect(surf, (60, 60, 60),
                pygame.Rect(gun_x - 4, gun_y - 4, 8, 8), border_radius=2)
            if self.is_shooting > 0:
                flash_r = int(self.is_shooting * 60) // 2 + 2
                pygame.draw.circle(surf, (255, 200, 50), (barrel_end, gun_y), flash_r)

        leg = int(math.sin(self.anim) * 5)
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + 4, ry + self.SIZE_H + squat - 2, 8, 8 + leg))
        pygame.draw.rect(surf, (180, 40, 40),
            pygame.Rect(rx + self.SIZE_W - 12, ry + self.SIZE_H + squat - 2, 8, 8 - leg))