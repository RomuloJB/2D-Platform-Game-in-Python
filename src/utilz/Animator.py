"""Animator — sistema reutilizavel de animacao por spritesheet.

Uma spritesheet e uma tira horizontal de frames quadrados (ex.: 128x128).
Um Clip representa uma animacao (uma sheet + fps + loop). Um Animator segura
varios clips, controla qual esta tocando, avanca o tempo e devolve o frame
atual ja escalado e (se preciso) espelhado.

Projetado para ser compartilhado entre Player e Enemy. As sheets sao carregadas
uma unica vez por caminho (cache de modulo), entao criar varios Animators com as
mesmas sheets nao recarrega imagem.

Uso tipico:

    anim = Animator(scale=0.55)
    anim.add("idle", "src/ui/player/Idle.png", fps=8)
    anim.add("run",  "src/ui/player/Run.png",  fps=14)
    anim.add("dead", "src/ui/player/Dead.png", fps=10, loop=False)
    ...
    anim.play("run")            # troca de clip (ignora se ja e o atual)
    anim.update(dt)
    anim.draw(surf, cx, cy, facing)   # cx,cy = ponto no chao (pes), em tela

Se as imagens nao carregarem (headless, arquivo ausente), `ok` fica False e o
chamador deve cair no desenho antigo.
"""

import os

import pygame


# Cache de frames por (path, frame_h_alvo). { chave: [Surface, ...] }
_sheet_cache = {}


def _load_sheet(path, frame_size=None):
    """Fatia uma spritesheet horizontal em frames quadrados.

    frame_size: lado do frame em px. Se None, assume que a altura da imagem
    e o lado do frame (sheets deste projeto sao 128 de altura).
    Retorna lista de Surfaces (com alpha) ou [] em caso de falha.
    """
    key = (path, frame_size)
    if key in _sheet_cache:
        return _sheet_cache[key]

    frames = []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        w, h = sheet.get_size()
        fs = frame_size or h
        count = max(1, w // fs)
        for i in range(count):
            frame = sheet.subsurface(pygame.Rect(i * fs, 0, fs, h)).copy()
            frames.append(frame)
    except Exception:
        frames = []

    _sheet_cache[key] = frames
    return frames


class Clip:
    """Uma animacao: lista de frames + fps + loop."""

    def __init__(self, frames, fps=10, loop=True):
        self.frames = frames
        self.fps = float(fps)
        self.loop = loop

    def __len__(self):
        return len(self.frames)


class Animator:
    def __init__(self, scale=1.0):
        """
        scale: fator aplicado a TODOS os frames de TODOS os clips, para manter
        o personagem com tamanho consistente entre animacoes. As sheets deste
        projeto compartilham o mesmo tamanho de personagem, entao uma escala
        global funciona bem.
        """
        self.scale = scale
        self.clips = {}
        self.current = None            # nome do clip atual
        self.time = 0.0                # tempo acumulado no clip atual
        self.frame_index = 0
        self.finished = False          # True quando um clip nao-loop terminou
        self._scaled_cache = {}        # (nome, idx, facing) -> Surface escalada

    @property
    def ok(self):
        """True se ha pelo menos um clip com frames carregados."""
        return any(len(c) for c in self.clips.values())

    def add(self, name, path, fps=10, loop=True, frame_size=None):
        frames = _load_sheet(path, frame_size)
        self.clips[name] = Clip(frames, fps=fps, loop=loop)
        if self.current is None and frames:
            self.current = name
        return self

    def has(self, name):
        return name in self.clips and len(self.clips[name]) > 0

    def play(self, name, restart=False):
        """Troca o clip atual. Ignora se ja e o clip atual (a menos que
        restart=True). Ignora nomes desconhecidos/vazios silenciosamente."""
        if not self.has(name):
            return
        if name == self.current and not restart:
            return
        self.current = name
        self.time = 0.0
        self.frame_index = 0
        self.finished = False

    def update(self, dt):
        clip = self.clips.get(self.current)
        if not clip or not len(clip):
            return
        self.time += dt
        step = 1.0 / clip.fps if clip.fps > 0 else 1e9
        while self.time >= step:
            self.time -= step
            if self.frame_index + 1 < len(clip):
                self.frame_index += 1
            elif clip.loop:
                self.frame_index = 0
            else:
                self.finished = True          # trava no ultimo frame
                break

    def _current_surface(self, facing):
        clip = self.clips.get(self.current)
        if not clip or not len(clip):
            return None
        idx = min(self.frame_index, len(clip) - 1)
        flip = facing < 0
        key = (self.current, idx, flip)
        surf = self._scaled_cache.get(key)
        if surf is None:
            base = clip.frames[idx]
            if self.scale != 1.0:
                w = max(1, int(base.get_width() * self.scale))
                h = max(1, int(base.get_height() * self.scale))
                base = pygame.transform.smoothscale(base, (w, h))
            if flip:
                base = pygame.transform.flip(base, True, False)
            surf = base
            self._scaled_cache[key] = surf
        return surf

    def draw(self, surf, feet_x, feet_y, facing=1):
        """Desenha o frame atual ancorado pelos PES.

        feet_x, feet_y: posicao em tela onde os pes do personagem devem ficar
        (tipicamente centro-x do hitbox e base do hitbox). Como as sheets tem o
        personagem no rodape do frame, ancoramos midbottom nesse ponto.
        """
        img = self._current_surface(facing)
        if img is None:
            return False
        rect = img.get_rect()
        rect.midbottom = (int(feet_x), int(feet_y))
        surf.blit(img, rect)
        return True
