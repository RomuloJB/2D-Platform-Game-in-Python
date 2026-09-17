"""
PauseState — menu de pausa exibido POR CIMA da fase congelada.

Diferente do menu principal, aqui não existe "JOGAR": o jogo não é
reiniciado, ele só volta exatamente de onde parou (CONTINUAR).

Ações devolvidas por handle_event():
    "resume"  → voltar de onde parou
    "restart" → recomeçar a fase atual
    "menu"    → salvar a pontuação e voltar ao menu principal
    "quit"    → encerrar o jogo
"""

import math

import pygame

from src.utilz.Constants import SCREEN_W, SCREEN_H


class PauseState:
    # mesma paleta do MenuState, para o visual bater
    C_WHITE    = (220, 220, 200)
    C_YELLOW   = (255, 215,   0)
    C_CYAN     = (110, 170, 220)
    C_GREEN    = ( 60, 220, 120)
    C_RED      = (220,  60,  60)
    C_ORANGE   = (255, 140,   0)
    C_DIM      = ( 80,  80, 100)
    C_PLATFORM = ( 70, 130, 180)

    OPTIONS = [
        ("CONTINUAR",      "resume",  C_GREEN),
        ("REINICIAR FASE", "restart", C_CYAN),
        ("MENU PRINCIPAL", "menu",    C_YELLOW),
        ("SAIR DO JOGO",   "quit",    C_RED),
    ]

    def __init__(self):
        self._sel   = 0
        self._tick  = 0
        self._blink = True

        try:
            self._font_title = pygame.font.SysFont("couriernew", 40, bold=True)
            self._font_opt   = pygame.font.SysFont("couriernew", 24, bold=True)
            self._font_small = pygame.font.SysFont("couriernew", 14)
        except Exception:
            self._font_title = pygame.font.Font(None, 46)
            self._font_opt   = pygame.font.Font(None, 30)
            self._font_small = pygame.font.Font(None, 20)

    # ─────────────────────────────────────────────────────────────
    #  Entrada
    # ─────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel - 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel + 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.OPTIONS[self._sel][1]
        elif event.key in (pygame.K_ESCAPE, pygame.K_p):
            # ESC/P de novo volta direto para o jogo
            return "resume"

        return None

    # ─────────────────────────────────────────────────────────────
    def update(self):
        self._tick += 1
        self._blink = (self._tick % 50) < 25

    # ─────────────────────────────────────────────────────────────
    #  Desenho (sobre o frame congelado da fase)
    # ─────────────────────────────────────────────────────────────
    def draw(self, surf, player=None, level_num=1, level_name=""):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        surf.blit(ov, (0, 0))

        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        pw, ph = 420, 360
        panel  = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((10, 10, 25, 235))
        prect = panel.get_rect(center=(cx, cy))
        surf.blit(panel, prect)

        pygame.draw.rect(surf, self.C_PLATFORM, prect, 2)
        pygame.draw.rect(surf, self.C_DIM, prect.inflate(-8, -8), 1)
        for corner in (prect.topleft, prect.topright,
                       prect.bottomleft, prect.bottomright):
            pygame.draw.rect(surf, self.C_YELLOW,
                             (corner[0] - 4, corner[1] - 4, 8, 8))

        # título com leve pulsação
        pulse = 1.0 + 0.03 * math.sin(self._tick * 0.07)
        self._blit_shadow(surf, "PAUSADO", self._font_title,
                          cx, prect.top + 42,
                          self.C_YELLOW, self.C_ORANGE, 3, pulse)

        # linha de status da partida
        info_y = prect.top + 78
        if player is not None:
            name = getattr(player, "name", "") or "JOGADOR"
            lines = [
                (f"{name}", self.C_WHITE),
                (f"Fase {level_num} — {level_name}", self.C_DIM),
                (f"Score {player.score}   Coins {player.coins}   "
                 f"HP {player.health}/{player.max_health}", self.C_CYAN),
            ]
            for text, color in lines:
                s = self._font_small.render(text, True, color)
                surf.blit(s, s.get_rect(center=(cx, info_y)))
                info_y += 18

        # separador
        sep_y = info_y + 8
        pygame.draw.line(surf, self.C_DIM,
                         (prect.left + 40, sep_y), (prect.right - 40, sep_y), 1)

        # opções
        start_y = sep_y + 34
        spacing = 44
        for i, (label, _action, color) in enumerate(self.OPTIONS):
            self._draw_option(surf, f"[ {label} ]", color, cx,
                              start_y + i * spacing, selected=(i == self._sel))

        hint_color = self.C_ORANGE if self._blink else self.C_DIM
        hint = self._font_small.render(
            "↑↓ NAVEGAR   ENTER CONFIRMAR   ESC CONTINUAR", True, hint_color)
        surf.blit(hint, hint.get_rect(center=(cx, prect.bottom - 22)))

    def _draw_option(self, surf, label, color, cx, cy, selected):
        if selected:
            bw, bh = 300, 34
            box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            box.fill((*color, 28))
            surf.blit(box, box.get_rect(center=(cx, cy)))
            rect = pygame.Rect(0, 0, bw, bh)
            rect.center = (cx, cy)
            pygame.draw.rect(surf, color, rect, 2)
            for corner in (rect.topleft, rect.topright,
                           rect.bottomleft, rect.bottomright):
                pygame.draw.rect(surf, self.C_YELLOW,
                                 (corner[0] - 3, corner[1] - 3, 6, 6))
            self._blit_shadow(surf, label, self._font_opt, cx, cy,
                              color, (0, 0, 0), 2)
        else:
            s = self._font_opt.render(label, True, self.C_DIM)
            surf.blit(s, s.get_rect(center=(cx, cy)))

    def _blit_shadow(self, surf, text, font, cx, cy, color,
                     shadow_color, shadow_offset=3, scale=1.0):
        img = font.render(text, True, color)
        shad = font.render(text, True, shadow_color)
        if scale != 1.0:
            size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img  = pygame.transform.scale(img, size)
            shad = pygame.transform.scale(shad, size)
        surf.blit(shad, shad.get_rect(center=(cx + shadow_offset,
                                              cy + shadow_offset)))
        surf.blit(img, img.get_rect(center=(cx, cy)))
