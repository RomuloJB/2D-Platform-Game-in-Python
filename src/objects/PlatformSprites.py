"""PlatformSprites — renderiza plataformas usando as sprites tematicas.

Cada tema tem duas variantes:
    "safe"   -> plataforma normal (Pad_XX_1.png)
    "hazard" -> plataforma com perigo, da dano (Pad_XX_2.png)

As sprites tem largura fixa (~840px), mas as plataformas do jogo tem largura
variavel. Para nao distorcer, usamos 3-slice horizontal: as duas pontas ficam
com tamanho fixo e o miolo e esticado para preencher qualquer largura.

Alinhamento: a superficie pisavel da arte fica no topo da imagem, entao
ancoramos o TOPO da sprite no TOPO do hitbox e deixamos o "corpo" da plataforma
pendurar por baixo (o visual de ilha flutuante). O hitbox de colisao nao muda.

Uso:
    from src.objects import PlatformSprites as PS
    surface = PS.render("grass", "safe", width_px, height_px)
    if surface:  # None se as imagens nao carregaram
        surf.blit(surface, (rx, ry))
"""

import os

import pygame


# tema -> (arquivo_seguro, arquivo_hazard)
_THEME_FILES = {
    "metal": ("Pad_01_1.png", "Pad_01_2.png"),
    "wood":  ("Pad_02_1.png", "Pad_02_2.png"),
    "sand":  ("Pad_03_1.png", "Pad_03_2.png"),
    "grass": ("Pad_04_1.png", "Pad_04_2.png"),
}

_BASE_DIR = os.path.join("src", "ui", "platforms")

# Fracao da largura da sprite usada para cada ponta no 3-slice.
_EDGE_FRAC = 0.28

# Caches
_raw_cache = {}        # path -> Surface original (ou None se falhou)
_render_cache = {}     # (theme, variant, w, h) -> Surface renderizada


def _load_raw(path):
    if path in _raw_cache:
        return _raw_cache[path]
    surf = None
    try:
        surf = pygame.image.load(path).convert_alpha()
    except Exception:
        surf = None
    _raw_cache[path] = surf
    return surf


def _sprite_for(theme, variant):
    files = _THEME_FILES.get(theme)
    if not files:
        return None
    fname = files[0] if variant == "safe" else files[1]
    return _load_raw(os.path.join(_BASE_DIR, fname))


def render(theme, variant, width, height):
    """Devolve uma Surface (width x height) da plataforma, ou None se as
    imagens nao carregarem. Resultado e cacheado por (theme, variant, w, h)."""
    width = max(1, int(width))
    height = max(1, int(height))
    key = (theme, variant, width, height)
    cached = _render_cache.get(key)
    if cached is not None:
        return cached

    sprite = _sprite_for(theme, variant)
    if sprite is None:
        return None

    sw, sh = sprite.get_size()

    # 1) escala a sprite inteira para a altura alvo (preserva proporcao vertical)
    scale = height / sh
    scaled_w = max(2, int(sw * scale))
    sprite_h = pygame.transform.smoothscale(sprite, (scaled_w, height))

    out = pygame.Surface((width, height), pygame.SRCALPHA)

    if width >= scaled_w:
        # 2a) alvo mais largo que a sprite: 3-slice esticando o miolo
        edge = int(scaled_w * _EDGE_FRAC)
        edge = max(1, min(edge, width // 2))
        left = sprite_h.subsurface(pygame.Rect(0, 0, edge, height))
        right = sprite_h.subsurface(pygame.Rect(scaled_w - edge, 0, edge, height))
        mid_src = sprite_h.subsurface(
            pygame.Rect(edge, 0, scaled_w - 2 * edge, height))
        mid_w = width - 2 * edge
        mid = pygame.transform.smoothscale(mid_src, (max(1, mid_w), height))
        out.blit(mid, (edge, 0))
        out.blit(left, (0, 0))
        out.blit(right, (width - edge, 0))
    else:
        # 2b) alvo mais estreito: encolhe a sprite inteira para caber
        squeezed = pygame.transform.smoothscale(sprite_h, (width, height))
        out.blit(squeezed, (0, 0))

    _render_cache[key] = out
    return out


def available():
    """True se pelo menos uma sprite de tema carregou (para fallback)."""
    for files in _THEME_FILES.values():
        if _load_raw(os.path.join(_BASE_DIR, files[0])) is not None:
            return True
    return False
