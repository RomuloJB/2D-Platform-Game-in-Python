"""LevelGenerator — geração procedural (mesma lógica; imports POO novos)."""

import random

import pygame

from src.utilz.Constants import SCREEN_W, SCREEN_H, TILE_SIZE, CHUNK_WIDTH, RENDER_CHUNKS
from src.objects.Platform import Platform
from src.objects.Portal import Portal
from src.entities.Coin import Coin
from src.entities.Enemy import Enemy


class LevelGenerator:
    def __init__(self, config, seed=None):
        self.config = config
        self.seed = seed or random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.generated_chunks = set()
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.portals = []
        self._mid_portal_placed = False
        self._end_portal_placed = False
        self._gen_chunk(0)

    def chunk_x_start(self, chunk_idx):
        return chunk_idx * CHUNK_WIDTH * TILE_SIZE

    def _place_portal(self, chunk_idx, kind):
        cx = self.chunk_x_start(chunk_idx)
        px = cx + (CHUNK_WIDTH * TILE_SIZE) // 2 - Portal.W // 2
        py = SCREEN_H - TILE_SIZE - Portal.H
        self.portals.append(Portal(px, py, kind))

    def _gen_chunk(self, chunk_idx):
        if chunk_idx in self.generated_chunks:
            return
        if chunk_idx > self.config.length_chunks + 1:
            return
        self.generated_chunks.add(chunk_idx)

        cfg = self.config
        cx = self.chunk_x_start(chunk_idx)
        rng = self.rng
        ground_y = SCREEN_H - TILE_SIZE
        gw = CHUNK_WIDTH * TILE_SIZE

        if chunk_idx == cfg.mid_chunk and not self._mid_portal_placed:
            self._place_portal(chunk_idx, "mid")
            self._mid_portal_placed = True
            self.platforms.append(Platform(cx, ground_y, gw, TILE_SIZE * 2, "ground"))
            return

        if chunk_idx == cfg.length_chunks and not self._end_portal_placed:
            self._place_portal(chunk_idx, "end")
            self._end_portal_placed = True
            self.platforms.append(Platform(cx, ground_y, gw, TILE_SIZE * 2, "ground"))
            return

        gaps = []
        if chunk_idx > 0:
            num_gaps = rng.randint(0, cfg.num_gaps_max)
            for _ in range(num_gaps):
                gx = rng.randint(2, CHUNK_WIDTH - 4) * TILE_SIZE + cx
                gw_gap = rng.randint(1, cfg.gap_max) * TILE_SIZE
                gaps.append((gx, gx + gw_gap))

        seg_start = cx
        for (g0, g1) in gaps:
            if g0 > seg_start:
                self.platforms.append(Platform(
                    seg_start, ground_y, g0 - seg_start, TILE_SIZE * 2, "ground"))
            seg_start = g1
        if seg_start < cx + gw:
            self.platforms.append(Platform(
                seg_start, ground_y, cx + gw - seg_start, TILE_SIZE * 2, "ground"))

        if chunk_idx == 0:
            return

        num_plats = rng.randint(3, 7)
        last_x = cx + TILE_SIZE
        level_y_min = SCREEN_H - 320
        level_y_max = SCREEN_H - 120

        for _ in range(num_plats):
            pw = rng.randint(3, 8) * TILE_SIZE
            px = last_x + rng.randint(1, 4) * TILE_SIZE
            py = rng.randint(level_y_min, level_y_max)

            if px + pw > cx + gw + TILE_SIZE * 3:
                break

            kind = "normal"
            r = rng.random()
            if r < cfg.spike_chance and chunk_idx > 2:
                kind = "spike"
            elif r < cfg.spike_chance + cfg.moving_chance and chunk_idx > 1:
                kind = "moving"

            plat = Platform(px, py, pw, TILE_SIZE // 2, kind)
            if kind == "moving":
                plat.move_range = rng.randint(40, 110)
                plat.move_speed = rng.uniform(0.02, 0.05) * cfg.enemy_speed_mult * 0.5
            self.platforms.append(plat)
            last_x = px + pw

            if kind == "normal" and pw >= TILE_SIZE * 2:
                if rng.random() < cfg.enemy_spawn_chance:
                    ex = px + rng.randint(0, pw - Enemy.SIZE_W)
                    ey = py - Enemy.SIZE_H - Enemy.SIZE_H // 2
                    e = Enemy(ex, ey, pygame.Rect(px, py, pw, TILE_SIZE // 2),
                              speed_mult=cfg.enemy_speed_mult, hp=cfg.enemy_hp)
                    self.enemies.append(e)

            num_coins = rng.randint(1, 3)
            for c in range(num_coins):
                if kind == "spike":
                    continue
                coin_x = px + (c + 1) * pw // (num_coins + 1)
                coin_y = py - 30
                self.coins.append(Coin(coin_x, coin_y))

        for (g0, g1) in gaps:
            cx_mid = (g0 + g1) // 2
            self.coins.append(Coin(cx_mid, ground_y - 60))

    def update_chunks(self, player_x):
        cur_chunk = int(player_x // (CHUNK_WIDTH * TILE_SIZE))
        max_chunk = self.config.length_chunks + 1
        for c in range(cur_chunk - 1, min(cur_chunk + RENDER_CHUNKS + 1, max_chunk + 1)):
            if c >= 0:
                self._gen_chunk(c)

    def get_nearby_platforms(self, cam_x):
        return [p for p in self.platforms
                if p.rect.right > cam_x - TILE_SIZE
                and p.rect.left < cam_x + SCREEN_W + TILE_SIZE]

    def get_nearby_enemies(self, cam_x):
        return [e for e in self.enemies
                if e.alive and e.rect.right > cam_x - 100
                and e.rect.left < cam_x + SCREEN_W + 100]

    def get_nearby_coins(self, cam_x):
        return [c for c in self.coins
                if not c.collected and c.center_x > cam_x - 50
                and c.center_x < cam_x + SCREEN_W + 50]

    def get_nearby_portals(self, cam_x):
        return [p for p in self.portals
                if p.active and p.rect.right > cam_x - 60
                and p.rect.left < cam_x + SCREEN_W + 60]
