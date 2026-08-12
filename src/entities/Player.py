"""
Player — herda Character (-> DynamicObject -> GameObject).
Física com Vector2 + dt. Mantém coyote time, jump buffer, pulo variável,
stomp, coleta de moeda e i-frames. Desenho idêntico ao original.
"""

import math
import random

import pygame

from src.entities.Character import Character
from src.objects.Particle import Particle
from src.entities.Weapons import Pistol, Shotgun, MachineGun
from src.utilz.Constants import (
    Layer, PLAYER_SPEED, PLAYER_FRICTION, JUMP_POWER, JUMP_HOLD_FORCE,
    JUMP_HOLD_TIME, COYOTE_TIME, JUMP_BUFFER, C_PLAYER, C_PLAYER_E,
    C_PLAYER_EY, C_PARTICLE, C_COIN,
)

# Aceleração horizontal: quantos px/s² de empurrão por frame (convertido para /s)
# Original: vx chega em ~8 frames → PLAYER_SPEED / (8/60) ≈ 2250 px/s²
_ACCEL = PLAYER_SPEED / (8 / 60)     # ~2250 px/s²

# Fator de atrito por segundo (0.75 por frame → 0.75^60 em 1 segundo,
# mas isso freia demais; usamos 0.75^60 só quando sem input).
# Na prática: multiplica velocidade por esse fator a cada segundo.
_FRICTION_PER_SEC = pow(0.75, 60)    # ≈ 1.3e-6  (freia quase na hora)



class Player(Character):
    W = 28
    H = 36

    def __init__(self, x, y):
        super().__init__(x, y, self.W, self.H,
                         category=Layer.PLAYER,
                         mask=Layer.PLATFORM | Layer.HAZARD,
                         use_gravity=True, max_health=3)
        self.coyote = 0.0
        self.jump_buf = 0.0
        self.jump_hold = 0.0
        self.cooldown = 0.0
        self.shoot_anim = 0.0
        self.land_squash = 0.0
        self.score = 0
        self.was_on_ground = False
        self.weapons = [Pistol()]
        self.weapon_index = 0
        self.unlocked_weapons = {"pistol"}
        self.coins = 0
        self.ammo = 999
        self.speed_upgraded = False
        self.damage_upgraded = False
        self._want_left = False
        self._want_right = False
        self._jump_held = False

    @property
    def current_weapon(self):
        return self.weapons[self.weapon_index]

    def switch_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.weapon_index = index

    @property
    def move_speed(self):
        return PLAYER_SPEED * (1.2 if self.speed_upgraded else 1.0)

    def unlock_weapon(self, weapon_id: str, equip: bool = True) -> bool:
        if weapon_id in self.unlocked_weapons:
            return False
        if weapon_id == "shotgun":
            self.weapons.append(Shotgun())
        elif weapon_id == "machinegun":
            self.weapons.append(MachineGun())
        else:
            return False
        self.unlocked_weapons.add(weapon_id)
        if equip:
            self.weapon_index = len(self.weapons) - 1
        return True

    def soft_reset(self, x, y):
        self.position.update(x, y)
        self.sync_rect()
        self.velocity.update(0, 0)
        self.on_ground = False
        self.coyote = 0.0
        self.jump_buf = 0.0
        self.jump_hold = 0.0
        self.alive = True
        self.invincible = 0.0
        self.health = self.max_health
        self.anim = 0.0
        self.was_on_ground = False
        self.land_squash = 0.0
        self.shoot_anim = 0.0

    # compat: __main__ antigo chama handle_input(keys); apply_input é o novo
    def apply_input(self, input_map: dict) -> None:
        self._want_left = input_map.get("left", False)
        self._want_right = input_map.get("right", False)
        jump = input_map.get("jump", False)
        if jump:
            self.jump_buf = JUMP_BUFFER
        self._jump_held = jump

    def handle_input(self, keys) -> None:
        self.apply_input({
            "left":  keys[pygame.K_LEFT] or keys[pygame.K_a],
            "right": keys[pygame.K_RIGHT] or keys[pygame.K_d],
            "jump":  keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w],
        })

    def shoot(self, mouse_screen_x, mouse_screen_y, cam_x, cam_y, bullets):
        """Tenta atirar. Retorna True se o tiro realmente saiu (para quem
        chamou, o Game, saber se toca o som de tiro), False se não (arma em
        cooldown ou player morto)."""
        if self.cooldown > 0 or not self.alive:
            return False

        weapon = self.current_weapon
        ox = self.rect.centerx
        oy = self.rect.centery - 4
        mx = mouse_screen_x + cam_x
        my = mouse_screen_y + cam_y
        dx = mx - ox
        dy = my - oy
        dmg = weapon.damage * (2 if self.damage_upgraded else 1)
        self.cooldown = weapon.cooldown
        bullets.extend(weapon.create_bullets(ox, oy, dx, dy, damage=dmg))
        self.shoot_anim = 6 / 60
        if dx > 0:
            self.facing = 1
        elif dx < 0:
            self.facing = -1
        return True

    def _try_jump(self):
        if self.jump_buf > 0 and (self.on_ground or self.coyote > 0):
            self.velocity.y = JUMP_POWER
            self.jump_buf = 0.0
            self.coyote = 0.0
            self.jump_hold = JUMP_HOLD_TIME
            return True
        return False

    def update(self, dt: float, world) -> None:
        if not self.alive:
            return

        self.was_on_ground = self.on_ground
        self.tick_timers(dt)
        self.cooldown = max(0.0, self.cooldown - dt)
        self.shoot_anim = max(0.0, self.shoot_anim - dt)
        self.jump_buf = max(0.0, self.jump_buf - dt)
        self.coyote = max(0.0, self.coyote - dt)
        self.land_squash = max(0.0, self.land_squash - dt)

        spd = self.move_speed
        if self._want_left:
            self.velocity.x -= _ACCEL * dt
            if self.velocity.x < -spd:
                self.velocity.x = -spd
            self.facing = -1
        elif self._want_right:
            self.velocity.x += _ACCEL * dt
            if self.velocity.x > spd:
                self.velocity.x = spd
            self.facing = 1
        else:
            # atrito por dt: pow(0.75, dt*60) replica o 0.75/frame original
            self.velocity.x *= pow(0.75, dt * 60)
            if abs(self.velocity.x) < 10:
                self.velocity.x = 0

        if self.jump_hold > 0 and self._jump_held:
            self.velocity.y -= JUMP_HOLD_FORCE * dt
            self.jump_hold = max(0.0, self.jump_hold - dt)
        elif not self._jump_held:
            self.jump_hold = 0.0

        # zera vy se estava no chão no frame anterior, para gravidade não acumular
        if self.was_on_ground:
            self.velocity.y = 0
        self.apply_gravity(dt)
        self.move_and_collide(dt, world.platforms,
                              on_hazard=lambda: self.take_damage(world.particles))

        if self.was_on_ground and not self.on_ground:
            self.coyote = COYOTE_TIME
        # if not self.was_on_ground and self.on_ground:
        #     self.land_squash = 8 / 60

        self._try_jump()

        if abs(self.velocity.x) > 30:
            self.anim += 9 * dt
        elif self.on_ground:
            self.anim = 0

        for enemy in world.enemies:
            if not enemy.alive:
                continue
            if self.rect.colliderect(enemy.rect) and self.invincible == 0:
                falling = self.velocity.y > 0
                above = self.rect.bottom - self.velocity.y * dt <= enemy.rect.top + 10
                if falling and above:
                    enemy.alive = False
                    self.velocity.y = JUMP_POWER * 0.7
                    self.score += 100
                    self.coins += 5
                    for _ in range(12):
                        world.particles.append(Particle(
                            enemy.rect.centerx, enemy.rect.centery,
                            random.uniform(-240, 240), random.uniform(-300, -60),
                            0.5, random.choice(C_PARTICLE), 5
                        ))
                else:
                    self.take_damage(world.particles)

        for coin in world.coins:
            if not coin.collected and self.rect.colliderect(coin.rect):
                coin.collected = True
                self.score += 10
                self.coins += 1
                for _ in range(8):
                    world.particles.append(Particle(
                        coin.center_x, coin.base_y,
                        random.uniform(-180, 180), random.uniform(-240, -30),
                        0.42, C_COIN, 4
                    ))

    def take_damage(self, particles=None, amount=1):
        if self.invincible > 0:
            return False
        self.health -= amount
        self.invincible = 90 / 60
        self.velocity.y = JUMP_POWER * 0.5
        if particles is not None:
            for _ in range(10):
                particles.append(Particle(
                    self.rect.centerx, self.rect.centery,
                    random.uniform(-240, 240), random.uniform(-300, -60),
                    0.58, C_PLAYER_E, 5
                ))
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        if self.invincible > 0 and (int(self.invincible * 60) // 5) % 2 == 0:
            return

        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y

        squash_x = 0
        squash_y = 0
        if self.land_squash > 0:
            t = (self.land_squash * 60) / 8
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

        moving = abs(self.velocity.x) > 30
        leg_swing = int(math.sin(self.anim) * 6) if moving else 0
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