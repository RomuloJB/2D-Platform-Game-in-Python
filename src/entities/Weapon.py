import math
import random
from src.entities.Bullet import Bullet


class Weapon:
    def __init__(self, name, damage, bullet_speed, cooldown, max_range, spread=0,pellets=1):
        self.name      = name
        self.damage    = damage
        self.bullet_speed     = bullet_speed
        self.cooldown  = cooldown    # frames de cooldown(igual BULLET_COOLDOWN atual)
        self.max_range = max_range
        self.spread    = spread      # graus de dispersão
        self.pellets   = pellets     # projéteis por disparo

    def create_bullets(self, ox, oy, dx, dy):
        dist = math.hypot(dx, dy) or 1
        base_vx = dx / dist * self.bullet_speed
        base_vy = dy / dist * self.bullet_speed
        bullets = []
        for _ in range(self.pellets):
            angle = math.radians(random.uniform(-self.spread, self.spread))
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            vx = base_vx * cos_a - base_vy * sin_a
            vy = base_vx * sin_a + base_vy * cos_a
            bullets.append(Bullet(ox, oy, vx, vy,
                                  damage=self.damage,
                                  max_range=self.max_range,
                                  weapon_type=self.name))
        return bullets

PISTOL      = Weapon("pistol",     damage=34, bullet_speed=12, cooldown=18, max_range=400, spread=2,  pellets=1)
SHOTGUN     = Weapon("shotgun",    damage=20, bullet_speed=10, cooldown=40, max_range=180, spread=25, pellets=6)
MACHINE_GUN = Weapon("machinegun", damage=50, bullet_speed=16, cooldown=6,  max_range=550, spread=5,  pellets=1)