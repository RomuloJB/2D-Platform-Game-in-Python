"""
DynamicObject — GameObject que se MOVE.

Adiciona velocity (Vector2, px/s), gravidade opcional, integração por dt e
resolução de colisão contra plataformas (eixos X e Y separados).

Usa swept collision no eixo Y para evitar tunneling quando dt é grande.
"""

import pygame
from pygame.math import Vector2

from src.objects.GameObject import GameObject
from src.utilz.Constants import GRAVITY, MAX_FALL, Layer


class DynamicObject(GameObject):
    def __init__(self, x, y, w, h,
                 category=Layer.NONE, mask=Layer.NONE, use_gravity=True):
        super().__init__(x, y, w, h, category, mask)
        self.velocity: Vector2 = Vector2(0.0, 0.0)
        self.use_gravity: bool = use_gravity
        self.on_ground: bool = False

    def apply_gravity(self, dt: float) -> None:
        if self.use_gravity:
            self.velocity.y += GRAVITY * dt
            if self.velocity.y > MAX_FALL:
                self.velocity.y = MAX_FALL

    def move_and_collide(self, dt: float, platforms, on_hazard=None) -> None:
        """Move por velocity*dt resolvendo colisão (X depois Y)."""

        # ── eixo X ────────────────────────────────────────────
        self.position.x += self.velocity.x * dt
        self.sync_rect()
        for plat in platforms:
            if plat.kind == "spike":
                continue
            if self.rect.colliderect(plat.rect):
                if self.velocity.x > 0:
                    self.rect.right = plat.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = plat.rect.right
                self.velocity.x = 0
                self.sync_position()

        # ── eixo Y (swept — divide em passos pequenos) ────────
        self.on_ground = False
        dy = self.velocity.y * dt
        # passo máximo de 8px por iteração para evitar tunneling
        step = 8.0
        remaining = abs(dy)
        direction = 1 if dy >= 0 else -1
        resolved = False

        while remaining > 0 and not resolved:
            move = min(step, remaining)
            remaining -= move
            self.position.y += direction * move
            self.sync_rect()

            for plat in platforms:
                if plat.kind == "spike":
                    if on_hazard and self.rect.colliderect(plat.rect):
                        on_hazard()
                    continue

                if not self.rect.colliderect(plat.rect):
                    continue

                if direction > 0:
                    # caindo — pousa em cima
                    self.rect.bottom = plat.rect.top
                    self.on_ground = True
                else:
                    # subindo — bate na parte de baixo
                    self.rect.top = plat.rect.bottom

                self.velocity.y = 0
                self.sync_position()
                resolved = True
                break