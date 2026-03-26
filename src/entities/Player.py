import math
import random

import pygame

from src.utilz.Constants import *
from src.objects.Particle import Particle
from src.entities.Bullet import Bullet
from src.utilz.Utilz import lerp


class Player:
    W = 28
    H = 36

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.W, self.H)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.coyote = 0
        self.jump_buf = 0
        self.jump_hold = 0
        self.alive = True
        self.invincible = 0
        self.max_health = 3
        self.health = self.max_health
        self.anim = 0
        self.facing = 1
        self.score = 0
        self.was_on_ground = False
        self.land_squash = 0
        self.shoot_cooldown = 0
        self.shoot_anim = 0

        # ── persistem entre mortes ─────────────────────────────
        self.coins = 0
        self.ammo = 999          # munição infinita por padrão (pode limitar depois)
        self.speed_upgraded = False
        self.damage_upgraded = False

    # ── conveniência para speed ────────────────────────────────
    @property
    def move_speed(self):
        return PLAYER_SPEED * (1.2 if self.speed_upgraded else 1.0)

    # ── reset ao morrer (mantém coins, armas, upgrades) ────────
    def soft_reset(self, x, y):
        self.rect.topleft = (x, y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.coyote = 0
        self.jump_buf = 0
        self.jump_hold = 0
        self.alive = True
        self.invincible = 0
        self.health = self.max_health   # reseta HP mas mantém max
        self.anim = 0
        self.was_on_ground = False
        self.land_squash = 0
        self.shoot_cooldown = 0
        self.shoot_anim = 0
        # coins, ammo, upgrades NÃO resetam

    def shoot(self, mouse_screen_x, mouse_screen_y, cam_x, cam_y, bullets):
        if self.shoot_cooldown > 0 or not self.alive:
            return
        ox = self.rect.centerx
        oy = self.rect.centery - 4
        mx = mouse_screen_x + cam_x
        my = mouse_screen_y + cam_y
        dx = mx - ox
        dy = my - oy
        dist = math.hypot(dx, dy) or 1
        speed = BULLET_SPEED
        vx = dx / dist * speed
        vy = dy / dist * speed
        dmg = 2 if self.damage_upgraded else 1
        bullets.append(Bullet(ox, oy, vx, vy, damage=dmg))
        self.shoot_cooldown = BULLET_COOLDOWN
        self.shoot_anim = 6
        if dx > 0:
            self.facing = 1
        elif dx < 0:
            self.facing = -1

    def handle_input(self, keys):
        spd = self.move_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = lerp(self.vx, -spd, PLAYER_ACCEL / spd)
            self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = lerp(self.vx, spd, PLAYER_ACCEL / spd)
            self.facing = 1
        else:
            self.vx *= PLAYER_FRICTION

        if abs(self.vx) < 0.1:
            self.vx = 0

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump_buf = JUMP_BUFFER
        else:
            if self.jump_buf > 0:
                self.jump_buf -= 1

        jump_held = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        if self.jump_hold > 0 and jump_held:
            self.vy -= 0.7
            self.jump_hold -= 1
        elif not jump_held:
            self.jump_hold = 0

    def try_jump(self):
        if self.jump_buf > 0 and (self.on_ground or self.coyote > 0):
            self.vy = JUMP_POWER
            self.jump_buf = 0
            self.coyote = 0
            self.jump_hold = JUMP_HOLD_FRAMES
            return True
        return False

    def update(self, platforms, enemies, coins, particles):
        if not self.alive:
            return

        self.was_on_ground = self.on_ground
        self.invincible = max(0, self.invincible - 1)
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.shoot_anim = max(0, self.shoot_anim - 1)
        if self.jump_buf > 0:
            self.jump_buf -= 1
        if self.coyote > 0:
            self.coyote -= 1

        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL)

        self.rect.x += int(self.vx)

        prev_bottom = self.rect.bottom
        self.rect.y += int(self.vy)
        self.on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if plat.kind == "spike":
                    self.take_damage(particles)
                    continue
                if self.vy > 0 and prev_bottom <= plat.rect.top + 6:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0
                    self.on_ground = True
                    if not self.was_on_ground:
                        self.land_squash = 8
                        for _ in range(6):
                            particles.append(Particle(
                                self.rect.centerx + random.randint(-10, 10),
                                self.rect.bottom,
                                random.uniform(-2, 2), random.uniform(-1, 0.5),
                                20, random.choice(C_PARTICLE[:2]), 3
                            ))
                elif self.vy < 0 and self.rect.top <= plat.rect.bottom:
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

        if self.was_on_ground and not self.on_ground:
            self.coyote = COYOTE_TIME

        self.try_jump()

        if abs(self.vx) > 0.5:
            self.anim += 0.15
        elif self.on_ground:
            self.anim = 0
        if self.land_squash > 0:
            self.land_squash -= 1

        for enemy in enemies:
            if not enemy.alive:
                continue
            if self.rect.colliderect(enemy.rect) and self.invincible == 0:
                if self.vy > 0 and self.rect.bottom - int(self.vy) <= enemy.rect.top + 10:
                    enemy.alive = False
                    self.vy = JUMP_POWER * 0.7
                    self.score += 100
                    self.coins += 5
                    for _ in range(12):
                        particles.append(Particle(
                            enemy.rect.centerx, enemy.rect.centery,
                            random.uniform(-4, 4), random.uniform(-5, -1),
                            30, random.choice(C_PARTICLE), 5
                        ))
                else:
                    self.take_damage(particles)

        for coin in coins:
            if not coin.collected:
                cr = pygame.Rect(coin.x - 8, coin.base_y - 8, 16, 16)
                if self.rect.colliderect(cr):
                    coin.collected = True
                    self.score += 10
                    self.coins += 1
                    for _ in range(8):
                        particles.append(Particle(
                            coin.x, coin.base_y,
                            random.uniform(-3, 3), random.uniform(-4, -0.5),
                            25, C_COIN, 4
                        ))

    def take_damage(self, particles):
        if self.invincible > 0:
            return
        self.health -= 1
        self.invincible = 90
        self.vy = JUMP_POWER * 0.5
        for _ in range(10):
            particles.append(Particle(
                self.rect.centerx, self.rect.centery,
                random.uniform(-4, 4), random.uniform(-5, -1),
                35, C_PLAYER_E, 5
            ))
        if self.health <= 0:
            self.alive = False

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            return

        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y

        squash_x = 0
        squash_y = 0
        if self.land_squash > 0:
            t = self.land_squash / 8
            squash_x = int(6 * t)
            squash_y = int(-6 * t)

        pygame.draw.ellipse(surf, (0, 0, 0, 80),
            pygame.Rect(rx + 2, ry + self.H - 4, self.W - 4, 8))

        body = pygame.Rect(
            rx - squash_x, ry - squash_y + squash_x,
            self.W + squash_x * 2, self.H + squash_y - squash_x
        )
        pygame.draw.rect(surf, C_PLAYER, body, border_radius=6)

        eye_x = rx + (self.W * 3 // 4 if self.facing > 0 else self.W // 4)
        pygame.draw.circle(surf, C_PLAYER_EY, (eye_x, ry + 10), 5)
        pygame.draw.circle(surf, (0, 0, 0), (eye_x + self.facing, ry + 11), 2)

        leg_swing = int(math.sin(self.anim) * 6) if abs(self.vx) > 0.5 else 0
        if self.on_ground:
            pygame.draw.rect(surf, (30, 160, 80),
                pygame.Rect(rx + 4, ry + self.H - 2, 8, 10 + leg_swing))
            pygame.draw.rect(surf, (30, 160, 80),
                pygame.Rect(rx + self.W - 12, ry + self.H - 2, 8, 10 - leg_swing))
        else:
            pygame.draw.rect(surf, (30, 160, 80),
                pygame.Rect(rx + 4, ry + self.H - 2, 8, 12))
            pygame.draw.rect(surf, (30, 160, 80),
                pygame.Rect(rx + self.W - 12, ry + self.H - 2, 8, 12))

        arm_swing = int(math.sin(self.anim) * 5)
        recoil = -4 if self.shoot_anim > 0 else 0
        pygame.draw.rect(surf, (40, 180, 90),
            pygame.Rect(rx - 8, ry + 10 + arm_swing, 8, 16))
        arm_front_x = rx + self.W if self.facing > 0 else rx - 8
        pygame.draw.rect(surf, (40, 180, 90),
            pygame.Rect(arm_front_x + recoil * self.facing, ry + 10 - arm_swing, 8, 16))