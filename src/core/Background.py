"""Background — desenha uma imagem de fundo com parallax e loop horizontal.

A imagem e escalada para a altura da tela e repetida lado a lado, deslizando
devagar conforme a camera anda (parallax). Como as imagens usadas fazem loop
lateral perfeito, a repeticao nao mostra emenda.

As surfaces escaladas sao cacheadas por caminho, entao desenhar todo frame nao
recarrega nem reescala a imagem.

Uso (em Hud.draw_background):
    from src.core.Background import draw_image_background
    ok = draw_image_background(surf, cam_x, "src/ui/backgrounds/forest.png")
    if not ok:
        ...  # cai no fundo procedural
"""

import pygame

from src.utilz.Constants import SCREEN_W, SCREEN_H

_PARALLAX = 0.3

_cache = {}


def _get_scaled(path):
    if path in _cache:
        return _cache[path]
    surf = None
    try:
        img = pygame.image.load(path).convert()
        w, h = img.get_size()
        scale = SCREEN_H / h
        new_w = max(1, int(w * scale))
        surf = pygame.transform.smoothscale(img, (new_w, SCREEN_H))
    except Exception:
        surf = None
    _cache[path] = surf
    return surf


def draw_image_background(surf, cam_x, path):
    """Desenha a imagem em loop horizontal com parallax. Retorna True se
    conseguiu desenhar, False se a imagem nao carregou (para o chamador poder
    cair no fundo procedural)."""
    img = _get_scaled(path)
    if img is None:
        return False

    img_w = img.get_width()

    offset = int(cam_x * _PARALLAX) % img_w

    x = -offset
    while x < SCREEN_W:
        surf.blit(img, (x, 0))
        x += img_w
    return True
