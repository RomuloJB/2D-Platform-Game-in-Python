"""Coin — item coletável. Herda GameObject (categoria PICKUP). Flutua por tempo.

Usa as sprites em src/ui/coins/Gold_*.png (30 frames). Elas são, na verdade,
tres moedas diferentes intercaladas — numero "1", coracao e estrela — cada uma
com 10 frames de rotacao. O padrao e (n-1) % 3:
    grupo 0 -> Gold_1, 4, 7, ...  (moeda "1")
    grupo 1 -> Gold_2, 5, 8, ...  (moeda coracao)
    grupo 2 -> Gold_3, 6, 9, ...  (moeda estrela)
"""

import math
import os
import random

import pygame

from src.objects.GameObject import GameObject
from src.utilz.Constants import SCREEN_W, Layer, C_COIN, C_COIN_S


class Coin(GameObject):
    R = 8

    # Tamanho em tela da sprite (diametro ~ 2*R, com uma folga p/ dar presenca).
    SPRITE_SIZE = 24

    # Velocidade da animacao de rotacao (frames por segundo).
    ANIM_FPS = 5

    # Tipos de moeda -> indice do grupo (n-1) % 3
    KIND_NUMBER = 0
    KIND_HEART = 1
    KIND_STAR = 2

    # Cache de frames por tipo, carregado uma unica vez e compartilhado por
    # todas as instancias. { kind: [Surface, ...] }  (10 frames cada)
    _frames_by_kind = None

    @classmethod
    def _load_frames(cls):
        """Carrega e agrupa as 30 sprites em 3 tipos de 10 frames.

        Roda so na primeira moeda criada. Se algo falhar (imagens ausentes,
        sem display inicializado, etc.), deixa o cache vazio e o draw cai no
        fallback do circulo desenhado.
        """
        if cls._frames_by_kind is not None:
            return

        cls._frames_by_kind = {cls.KIND_NUMBER: [], cls.KIND_HEART: [], cls.KIND_STAR: []}

        base_dir = os.path.join("src", "ui", "coins")
        for n in range(1, 31):
            path = os.path.join(base_dir, f"Gold_{n}.png")
            if not os.path.exists(path):
                continue
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (cls.SPRITE_SIZE, cls.SPRITE_SIZE))
            except Exception:
                continue
            cls._frames_by_kind[(n - 1) % 3].append(img)

    def __init__(self, x, y, kind=None):
        super().__init__(x - self.R, y - self.R, self.R * 2, self.R * 2,
                         category=Layer.PICKUP, mask=Layer.PLAYER)
        self.base_y = float(y)
        self.center_x = float(x)
        self.collected = False
        self.anim = random.uniform(0, math.pi * 2)     # fase do bob (flutuacao)

        self._load_frames()

        # Tipo da moeda: aleatorio se nao for especificado.
        if kind is None:
            kind = random.choice((self.KIND_NUMBER, self.KIND_HEART, self.KIND_STAR))
        self.kind = kind

        # Estado da animacao de rotacao.
        self.frame_time = random.uniform(0, 1.0)       # dessincroniza as moedas
        self.frame_index = 0

    # compat: alguns lugares antigos liam coin.x
    @property
    def x(self):
        return self.center_x

    def _frames(self):
        if not self._frames_by_kind:
            return []
        return self._frames_by_kind.get(self.kind, [])

    def update(self, dt: float, world=None) -> None:
        # Flutuacao vertical (bob).
        self.anim += 4.2 * dt
        bob = math.sin(self.anim) * 4
        self.position.x = self.center_x - self.R
        self.position.y = self.base_y + bob - self.R
        self.sync_rect()

        # Avanca a animacao de rotacao.
        frames = self._frames()
        if frames:
            self.frame_time += dt
            step = 1.0 / self.ANIM_FPS
            while self.frame_time >= step:
                self.frame_time -= step
                self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.center_x - cam_x)
        sy = int(self.base_y + math.sin(self.anim) * 4 - cam_y)
        if not (-20 < sx < SCREEN_W + 20):
            return

        frames = self._frames()
        if frames:
            img = frames[self.frame_index % len(frames)]
            rect = img.get_rect(center=(sx, sy))
            surf.blit(img, rect)
        else:
            # Fallback: mantem o circulo estatico caso as sprites nao carreguem.
            pygame.draw.circle(surf, C_COIN, (sx, sy), self.R)
            pygame.draw.circle(surf, C_COIN_S, (sx - 2, sy - 2), 3)