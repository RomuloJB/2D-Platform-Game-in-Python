import math, random
from .Bullet import Bullet
from .Weapon import Weapon

class Pistol(Weapon):
    """Range médio, mata com 3 balas."""
    def __init__(self):
        super().__init__(
            name="Pistol",
            damage=34,          # 34 * 3 ≈ 100 hp → mata
            bullet_speed=10,
            fire_rate=400,      # ms
            max_range=400,
            bullets_to_kill=3,
            spread=2,           # graus de dispersão leve
        )

    def _create_bullets(self, x, y, direction):
        angle = random.uniform(-self.spread, self.spread)
        return [Bullet(x, y, direction, self.bullet_speed,
                       self.damage, self.max_range, angle_offset=angle)]


class Shotgun(Weapon):
    """Range curto, dano alto de perto, 6 pellets por disparo."""
    def __init__(self):
        super().__init__(
            name="Shotgun",
            damage=20,          # cada pellet faz 20
            bullet_speed=9,
            fire_rate=900,
            max_range=180,      # range BEM curto
            bullets_to_kill=1,  # se todos os pellets acertarem = 120 dmg
            spread=25,
        )
        self.bullets_per_shot = 6

    def _create_bullets(self, x, y, direction):
        bullets = []
        for _ in range(self.bullets_per_shot):
            angle = random.uniform(-self.spread, self.spread)
            bullets.append(
                Bullet(x, y, direction, self.bullet_speed,
                       self.damage, self.max_range, angle_offset=angle)
            )
        return bullets


class MachineGun(Weapon):
    """Bom range, alta cadência, mata com 2 balas."""
    def __init__(self):
        super().__init__(
            name="MachineGun",
            damage=50,          # 50 * 2 = 100 hp → mata
            bullet_speed=14,
            fire_rate=120,      # rápido
            max_range=550,
            bullets_to_kill=2,
            spread=5,
        )

    def _create_bullets(self, x, y, direction):
        angle = random.uniform(-self.spread, self.spread)
        return [Bullet(x, y, direction, self.bullet_speed,
                       self.damage, self.max_range, angle_offset=angle)]