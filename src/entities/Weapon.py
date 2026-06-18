"""
Weapon — base. Os valores de bullet_speed das armas (Weapons.py) estão em
px/FRAME (calibração antiga); convertemos para px/SEGUNDO ao criar a bala,
multiplicando por FRAME_RATE. O cooldown também: as armas trazem em "frames",
convertido para segundos.
"""

import math
import random

from src.entities.Bullet import Bullet
from src.utilz.Constants import FRAME_RATE


class Weapon:
    def __init__(self, name, damage, bullet_speed, cooldown,
                 max_range, spread=0, pellets=1):
        self.name = name
        self.damage = damage
        self.bullet_speed = bullet_speed        # px/frame (convertido na hora)
        self.cooldown_frames = cooldown         # frames
        self.cooldown = cooldown / FRAME_RATE   # segundos (usado pelo Player)
        self.max_range = max_range
        self.spread = spread
        self.pellets = pellets

    def create_bullets(self, ox, oy, dx, dy, damage=None):
        dmg = self.damage if damage is None else damage
        speed = self.bullet_speed * FRAME_RATE   # px/frame -> px/s
        dist = math.hypot(dx, dy) or 1
        base_vx = dx / dist * speed
        base_vy = dy / dist * speed
        bullets = []
        for _ in range(self.pellets):
            angle = math.radians(random.uniform(-self.spread, self.spread))
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            vx = base_vx * cos_a - base_vy * sin_a
            vy = base_vx * sin_a + base_vy * cos_a
            bullets.append(Bullet(ox, oy, vx, vy,
                                  damage=dmg,
                                  max_range=self.max_range,
                                  weapon_type=self.name))
        return bullets
