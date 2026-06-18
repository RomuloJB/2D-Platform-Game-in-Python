"""
GameObject — classe base de TUDO no mundo. Responsabilidade única: POSIÇÃO.

Posição guardada como pygame.math.Vector2 (o "vetor" pedido, em vez de x/y
soltos). O rect é mantido em sincronia para os testes de colisão do pygame.
"""

import pygame
from pygame.math import Vector2

from src.physics.Collider import Collider
from src.utilz.Constants import Layer


class GameObject:
    def __init__(self, x: float, y: float, w: int, h: int,
                 category: int = Layer.NONE, mask: int = Layer.NONE):
        self.position: Vector2 = Vector2(x, y)
        self.width: int = w
        self.height: int = h
        self.rect: pygame.Rect = pygame.Rect(int(x), int(y), w, h)
        self.alive: bool = True
        self.collider: Collider = Collider(self, self.rect, category, mask)

    def sync_rect(self) -> None:
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def sync_position(self) -> None:
        self.position.x = float(self.rect.x)
        self.position.y = float(self.rect.y)

    @property
    def center(self) -> Vector2:
        return Vector2(self.rect.centerx, self.rect.centery)

    def update(self, dt: float, world) -> None:
        pass

    def draw(self, surf, cam_x: float, cam_y: float) -> None:
        pass
