"""
Character — DynamicObject com VIDA e lógica de COMBATE.
Base comum de Player e Enemy (a "lógica de batalha" compartilhada).
"""

import random

from src.objects.DynamicObject import DynamicObject
from src.utilz.Constants import Layer


class Character(DynamicObject):
    def __init__(self, x, y, w, h,
                 category=Layer.NONE, mask=Layer.NONE,
                 use_gravity=True, max_health=1):
        super().__init__(x, y, w, h, category, mask, use_gravity)
        self.max_health: int = max_health
        self.health: int = max_health
        self.invincible: float = 0.0
        self.facing: int = 1
        self.anim: float = 0.0

    def tick_timers(self, dt: float) -> None:
        self.invincible = max(0.0, self.invincible - dt)

    def take_damage(self, amount: int = 1, particles=None,
                    color=(200, 60, 60)) -> bool:
        if self.invincible > 0:
            return False
        self.health -= amount
        if particles is not None:
            self._spawn_hit_particles(particles, color)
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False

    def heal(self, amount: int = 1) -> None:
        self.health = min(self.max_health, self.health + amount)

    def _spawn_hit_particles(self, particles, color) -> None:
        from src.objects.Particle import Particle
        for _ in range(10):
            particles.append(Particle(
                self.rect.centerx, self.rect.centery,
                random.uniform(-240, 240), random.uniform(-300, -60),
                0.58, color, 5
            ))
