"""
Sistema de colisão categorizado.

Cada Collider tem rect, category (a que camada pertence) e mask (com quais
camadas pode colidir). Dois colliders só colidem se os rects se tocam E as
categorias/máscaras forem compatíveis nos dois sentidos. Isso evita, por
exemplo, a bala do player colidir com o próprio player.
"""

import pygame
from src.utilz.Constants import Layer


class Collider:
    def __init__(self, owner, rect: pygame.Rect,
                 category: int = Layer.NONE, mask: int = Layer.NONE):
        self.owner = owner
        self.rect = rect
        self.category = category
        self.mask = mask

    def can_collide_with(self, other: "Collider") -> bool:
        return bool(self.mask & other.category) and bool(other.mask & self.category)

    def collides(self, other: "Collider") -> bool:
        if not self.can_collide_with(other):
            return False
        return self.rect.colliderect(other.rect)

    def collides_rect(self, rect: pygame.Rect) -> bool:
        return self.rect.colliderect(rect)
