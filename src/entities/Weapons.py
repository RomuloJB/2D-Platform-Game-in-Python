"""Armas concretas — valores de balanceamento do pull (colega)."""

from src.entities.Weapon import Weapon


class Pistol(Weapon):
    """Range médio, mata com 3 balas."""
    def __init__(self):
        super().__init__(
            name="Pistol",
            damage=34,
            bullet_speed=12,
            cooldown=30,
            max_range=500,
            spread=1,
            pellets=1,
        )


class Shotgun(Weapon):
    """Range curto, dano alto de perto, 6 pellets por disparo."""
    def __init__(self):
        super().__init__(
            name="Shotgun",
            damage=20,
            bullet_speed=14,
            cooldown=100,
            max_range=350,
            spread=10,
            pellets=6,
        )


class MachineGun(Weapon):
    """Bom range, alta cadência, mata com 2 balas."""
    def __init__(self):
        super().__init__(
            name="MachineGun",
            damage=50,
            bullet_speed=20,
            cooldown=10,
            max_range=600,
            spread=3,
            pellets=1,
        )
