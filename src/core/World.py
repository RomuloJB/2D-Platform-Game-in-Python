"""
World — agrega o estado de uma fase e serve de "contexto" para os updates
(world.platforms, world.enemies, world.coins, world.player, world.particles),
evitando variáveis globais. Centraliza update/draw e o streaming de chunks.
"""

from src.levels.LevelGenerator import LevelGenerator


class World:
    def __init__(self, config, player, seed=None):
        self.config = config
        self.player = player
        self.generator = LevelGenerator(config, seed)
        self.particles = []
        self.bullets = []
        self.time_elapsed = 0.0

        self.platforms = []
        self.enemies = []
        self.coins = []
        self.portals = []

    def _refresh_active(self, cam_x):
        self.platforms = self.generator.get_nearby_platforms(cam_x)
        self.enemies = self.generator.get_nearby_enemies(cam_x)
        self.coins = self.generator.get_nearby_coins(cam_x)
        self.portals = self.generator.get_nearby_portals(cam_x)

    def update(self, dt: float, cam_x: float):
        self.time_elapsed += dt
        self.generator.update_chunks(self.player.position.x)
        self._refresh_active(cam_x)

        for plat in self.platforms:
            plat.update(dt, self)
        self.player.update(dt, self)
        for enemy in self.enemies:
            enemy.update(dt, self)
        for coin in self.coins:
            coin.update(dt, self)
        for portal in self.portals:
            portal.update(dt, self)

        for bullet in self.bullets:
            bullet.update(dt, self)
            if bullet.scored:
                self.player.score += 150
                bullet.scored = False
        self.bullets = [b for b in self.bullets if b.alive]

        for p in self.particles:
            p.update(dt, self)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surf, cam_x, cam_y):
        for plat in self.platforms:
            plat.draw(surf, cam_x, cam_y)
        for coin in self.coins:
            coin.draw(surf, cam_x, cam_y)
        for portal in self.portals:
            portal.draw(surf, cam_x, cam_y)
        for enemy in self.enemies:
            enemy.draw(surf, cam_x, cam_y)
        for bullet in self.bullets:
            bullet.draw(surf, cam_x, cam_y)
        self.player.draw(surf, cam_x, cam_y)
        for p in self.particles:
            p.draw(surf, cam_x, cam_y)

    def portal_touched(self):
        for portal in self.portals:
            if portal.active and self.player.rect.colliderect(portal.rect):
                return portal
        return None
