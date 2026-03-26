import random
import math

import pygame

from src.utilz.Constants import *
from src.objects.Platform import Platform
from src.entities.Enemy import Enemy
from src.entities.Coin import Coin


class Portal:
    """Portal de fim de fase ou checkpoint."""
    W, H = 36, 72

    def __init__(self, x, y, kind="end"):
        self.rect = pygame.Rect(x, y, self.W, self.H)
        self.kind = kind   # "end" ou "mid"
        self.anim = 0.0
        self.active = True

    def update(self):
        self.anim += 0.05

    def draw(self, surf, cam_x, cam_y):
        if not self.active:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        if rx < -60 or rx > SCREEN_W + 60:
            return

        pulse = abs(math.sin(self.anim)) * 0.4 + 0.6

        if self.kind == "mid":
            inner = (int(80 * pulse), int(200 * pulse), int(255 * pulse))
            outer = (20, 80, 140)
            label_color = (120, 220, 255)
        else:
            inner = (int(180 * pulse), int(80 * pulse), int(255 * pulse))
            outer = (80, 20, 140)
            label_color = (220, 160, 255)

        # moldura externa
        pygame.draw.rect(surf, outer,
            pygame.Rect(rx - 4, ry - 4, self.W + 8, self.H + 8), border_radius=8)
        # corpo do portal
        pygame.draw.rect(surf, inner,
            pygame.Rect(rx, ry, self.W, self.H), border_radius=6)
        # brilho central
        cx = rx + self.W // 2
        cy = ry + self.H // 2
        r_glow = int(10 * pulse)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), r_glow)

        # label
        try:
            font = pygame.font.SysFont("arial", 11, bold=True)
        except Exception:
            font = pygame.font.Font(None, 14)
        txt = "LOJA" if self.kind == "mid" else "SAÍDA"
        t = font.render(txt, True, label_color)
        surf.blit(t, (rx + self.W // 2 - t.get_width() // 2, ry - 18))


class LevelGenerator:
    """
    Gerador de mapa procedural para uma fase específica.

    Parâmetros de dificuldade vêm de LevelConfig.
    Gera um portal no chunk mid_chunk (checkpoint do meio)
    e outro portal no chunk length_chunks (saída da fase).
    """

    def __init__(self, config, seed=None):
        self.config = config
        self.seed = seed or random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.generated_chunks = set()
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.portals = []   # Portal "mid" e "end"
        self._mid_portal_placed = False
        self._end_portal_placed = False
        self._gen_chunk(0)

    # ── helpers ────────────────────────────────────────────────

    def chunk_x_start(self, chunk_idx):
        return chunk_idx * CHUNK_WIDTH * TILE_SIZE

    def _place_portal(self, chunk_idx, kind):
        cx = self.chunk_x_start(chunk_idx)
        # Coloca o portal no centro do chunk, em cima do chão
        px = cx + (CHUNK_WIDTH * TILE_SIZE) // 2 - Portal.W // 2
        py = SCREEN_H - TILE_SIZE - Portal.H
        self.portals.append(Portal(px, py, kind))

    # ── geração de chunk ───────────────────────────────────────

    def _gen_chunk(self, chunk_idx):
        if chunk_idx in self.generated_chunks:
            return
        # Não gera além do fim da fase
        if chunk_idx > self.config.length_chunks + 1:
            return
        self.generated_chunks.add(chunk_idx)

        cfg = self.config
        cx = self.chunk_x_start(chunk_idx)
        rng = self.rng
        ground_y = SCREEN_H - TILE_SIZE
        gw = CHUNK_WIDTH * TILE_SIZE

        # ── Portal do meio (checkpoint) ──────────────────────
        if chunk_idx == cfg.mid_chunk and not self._mid_portal_placed:
            self._place_portal(chunk_idx, "mid")
            self._mid_portal_placed = True
            # chunk do portal: só chão limpo, sem buracos
            self.platforms.append(
                Platform(cx, ground_y, gw, TILE_SIZE * 2, "ground"))
            return

        # ── Portal de saída ───────────────────────────────────
        if chunk_idx == cfg.length_chunks and not self._end_portal_placed:
            self._place_portal(chunk_idx, "end")
            self._end_portal_placed = True
            self.platforms.append(
                Platform(cx, ground_y, gw, TILE_SIZE * 2, "ground"))
            return

        # ── Chão com buracos ──────────────────────────────────
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

        # ── Plataformas flutuantes ────────────────────────────
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

            # ── Inimigos ──────────────────────────────────────
            if kind == "normal" and pw >= TILE_SIZE * 2:
                if rng.random() < cfg.enemy_spawn_chance:
                    ex = px + rng.randint(0, pw - Enemy.SIZE_W)
                    ey = py - Enemy.SIZE_H - Enemy.SIZE_H // 2
                    e = Enemy(ex, ey, pygame.Rect(px, py, pw, TILE_SIZE // 2),
                              speed_mult=cfg.enemy_speed_mult,
                              hp=cfg.enemy_hp)
                    self.enemies.append(e)

            # ── Moedas ────────────────────────────────────────
            num_coins = rng.randint(1, 3)
            for c in range(num_coins):
                if kind == "spike":
                    continue
                coin_x = px + (c + 1) * pw // (num_coins + 1)
                coin_y = py - 30
                self.coins.append(Coin(coin_x, coin_y))

        # Moedas nos buracos (recompensa por pular)
        for (g0, g1) in gaps:
            cx_mid = (g0 + g1) // 2
            self.coins.append(Coin(cx_mid, ground_y - 60))

    # ── update / queries ───────────────────────────────────────

    def update_chunks(self, player_x):
        cur_chunk = int(player_x // (CHUNK_WIDTH * TILE_SIZE))
        max_chunk = self.config.length_chunks + 1
        for c in range(cur_chunk - 1, min(cur_chunk + RENDER_CHUNKS + 1, max_chunk + 1)):
            if c >= 0:
                self._gen_chunk(c)

    def get_nearby_platforms(self, cam_x):
        return [
            p for p in self.platforms
            if p.rect.right > cam_x - TILE_SIZE
            and p.rect.left < cam_x + SCREEN_W + TILE_SIZE
        ]

    def get_nearby_enemies(self, cam_x):
        return [
            e for e in self.enemies
            if e.alive
            and e.rect.right > cam_x - 100
            and e.rect.left < cam_x + SCREEN_W + 100
        ]

    def get_nearby_coins(self, cam_x):
        return [
            c for c in self.coins
            if not c.collected
            and c.x > cam_x - 50
            and c.x < cam_x + SCREEN_W + 50
        ]

    def get_nearby_portals(self, cam_x):
        return [
            p for p in self.portals
            if p.active
            and p.rect.right > cam_x - 60
            and p.rect.left < cam_x + SCREEN_W + 60
        ]