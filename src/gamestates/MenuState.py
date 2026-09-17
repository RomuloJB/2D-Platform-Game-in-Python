import pygame
import math

from src.utilz import Scoreboard


class MenuState:
    """
    Tela de menu principal — estilo pixel art retro.
    Usa as cores e resolução reais do jogo (Constants.py).
    Estados internos: 'main' | 'name' | 'scores' | 'credits'

    'name'   → digitação do nome antes de começar a partida (vai no score)
    'scores' → histórico de pontuações dos jogadores
    """

    # Paleta extraída de Constants.py
    C_BG_TOP   = (10,  10,  30)
    C_BG_BTM   = (20,  20,  60)
    C_WHITE    = (220, 220, 200)
    C_YELLOW   = (255, 215,   0)   # C_COIN
    C_YELLOW_S = (255, 255, 150)   # C_COIN_S
    C_CYAN     = (110, 170, 220)   # C_PLAT_TOP
    C_GREEN    = ( 60, 220, 120)   # C_PLAYER
    C_RED      = (220,  60,  60)   # C_ENEMY
    C_ORANGE   = (255, 140,   0)   # C_BULLET
    C_DIM      = ( 80,  80, 100)
    C_PLATFORM = ( 70, 130, 180)   # C_PLATFORM

    OPTION_PLAY    = 0
    OPTION_SCORES  = 1
    OPTION_CREDITS = 2
    OPTION_QUIT    = 3

    MAX_NAME_LEN = Scoreboard.MAX_NAME_LEN

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width  = screen.get_width()
        self.height = screen.get_height()
        self._sub   = "main"   # 'main' | 'name' | 'scores' | 'credits'
        self._sel   = 0
        self._tick  = 0
        self._blink = True

        # Nome do jogador — é ele que vai gravado no histórico de scores.
        # Começa com o nome da última partida registrada.
        self.player_name = Scoreboard.last_player_name()
        self._name_buf   = self.player_name
        self._scores     = []

        # Fontes monospace — combinam com pixel art
        self._font_title  = pygame.font.SysFont("couriernew", 56, bold=True)
        self._font_option = pygame.font.SysFont("couriernew", 30, bold=True)
        self._font_sub    = pygame.font.SysFont("couriernew", 15)
        self._font_small  = pygame.font.SysFont("couriernew", 13)
        self._font_score  = pygame.font.SysFont("couriernew", 16, bold=True)

        self._options = ["JOGAR", "PONTUAÇÕES", "CRÉDITOS", "SAIR"]
        self._colors  = [self.C_GREEN, self.C_YELLOW, self.C_CYAN, self.C_RED]

        # Estrelas de fundo (semente fixa = sempre igual)
        import random
        rng = random.Random(7)
        self._stars = [
            (rng.randint(0, self.width),
             rng.randint(0, self.height * 2 // 3),
             rng.choice([1, 1, 2]),
             rng.randint(50, 220))
            for _ in range(140)
        ]

        # Scanlines — criadas uma vez
        self._scanlines = self._make_scanlines()

        # Plataformas decorativas flutuantes no rodapé
        self._plat_data = [
            {"x":  60, "w": 180, "speed": 0.4, "y_off":  0},
            {"x": 320, "w": 140, "speed": 0.6, "y_off": 15},
            {"x": 560, "w": 200, "speed": 0.3, "y_off":  8},
            {"x": 820, "w": 120, "speed": 0.5, "y_off": 20},
        ]

    # ─────────────────────────────────────────────────────────────
    def _make_scanlines(self) -> pygame.Surface:
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(s, (0, 0, 0, 45), (0, y), (self.width, y))
        return s

    # ─────────────────────────────────────────────────────────────
    #  Entrada
    # ─────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        """
        Retorna:
            "play"  → iniciar o jogo (self.player_name já está definido)
            "quit"  → encerrar
            None    → sem ação externa
        """
        if event.type != pygame.KEYDOWN:
            return None

        if self._sub == "credits":
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                self._sub = "main"
            return None

        if self._sub == "scores":
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                self._sub = "main"
            return None

        if self._sub == "name":
            return self._handle_name_event(event)

        # sub == "main"
        if event.key in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel - 1) % len(self._options)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel + 1) % len(self._options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return self._confirm()
        elif event.key == pygame.K_ESCAPE:
            # ESC no menu apenas move o cursor para "SAIR"
            self._sel = self.OPTION_QUIT

        return None

    def _confirm(self):
        if self._sel == self.OPTION_PLAY:
            # antes de jogar, pede o nome que será salvo na pontuação
            self._name_buf = self.player_name
            self._sub = "name"
        if self._sel == self.OPTION_SCORES:
            self.refresh_scores()
            self._sub = "scores"
        if self._sel == self.OPTION_CREDITS:
            self._sub = "credits"
        if self._sel == self.OPTION_QUIT:
            return "quit"
        return None

    def _handle_name_event(self, event: pygame.event.Event):
        """Digitação do nome do jogador. ENTER começa a partida."""
        if event.key == pygame.K_ESCAPE:
            self._sub = "main"
            return None

        if event.key == pygame.K_BACKSPACE:
            self._name_buf = self._name_buf[:-1]
            return None

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.player_name = Scoreboard.sanitize_name(self._name_buf)
            self._name_buf = self.player_name
            self._sub = "main"
            return "play"

        char = event.unicode
        if char and char.isprintable() and char != "\t":
            if len(self._name_buf) < self.MAX_NAME_LEN:
                self._name_buf += char.upper()
        return None

    # ─────────────────────────────────────────────────────────────
    def refresh_scores(self):
        """Recarrega o histórico do disco (usado ao abrir a tela)."""
        self._scores = Scoreboard.top_scores(10)

    def reset(self):
        """Volta o menu para a tela inicial — chamado ao sair de uma partida."""
        self._sub = "main"
        self._sel = self.OPTION_PLAY
        self.refresh_scores()

    # ─────────────────────────────────────────────────────────────
    #  Update
    # ─────────────────────────────────────────────────────────────
    def update(self):
        self._tick += 1
        self._blink = (self._tick % 50) < 25

    # ─────────────────────────────────────────────────────────────
    #  Draw
    # ─────────────────────────────────────────────────────────────
    def draw(self):
        self._draw_bg_gradient()
        self._draw_stars()
        self._draw_platforms()

        if self._sub == "main":
            self._draw_main()
        elif self._sub == "name":
            self._draw_name_input()
        elif self._sub == "scores":
            self._draw_scores()
        else:
            self._draw_credits()

        self.screen.blit(self._scanlines, (0, 0))

    # ─────────────────────────────────────────────────────────────
    #  Fundo
    # ─────────────────────────────────────────────────────────────
    def _draw_bg_gradient(self):
        """Gradiente idêntico ao draw_background() do Hud.py."""
        for y in range(self.height):
            t = y / self.height
            r = int(self.C_BG_TOP[0] + (self.C_BG_BTM[0] - self.C_BG_TOP[0]) * t)
            g = int(self.C_BG_TOP[1] + (self.C_BG_BTM[1] - self.C_BG_TOP[1]) * t)
            b = int(self.C_BG_TOP[2] + (self.C_BG_BTM[2] - self.C_BG_TOP[2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))

    def _draw_stars(self):
        t = self._tick * 0.018
        for sx, sy, size, brightness in self._stars:
            twinkle = int(brightness * (0.55 + 0.45 * math.sin(t + sx * 0.09)))
            c = (twinkle, twinkle, min(255, twinkle + 50))
            pygame.draw.rect(self.screen, c, (sx, sy, size, size))

    def _draw_platforms(self):
        """Plataformas decorativas — visual igual ao Level1/Platform.draw."""
        base_y = self.height - 60
        t = self._tick * 0.015
        for pd in self._plat_data:
            x = int(pd["x"] + math.sin(t * pd["speed"]) * 6)
            y = base_y + int(math.sin(t * pd["speed"] + 1.2) * pd["y_off"])
            w = pd["w"]
            h = 16
            pygame.draw.rect(self.screen, self.C_PLATFORM, (x, y, w, h))
            pygame.draw.rect(self.screen, self.C_CYAN,     (x, y, w, 3))
            pygame.draw.rect(self.screen, (40, 80, 120),   (x, y + h - 2, w, 2))

    # ─────────────────────────────────────────────────────────────
    #  Tela Principal
    # ─────────────────────────────────────────────────────────────
    def _draw_main(self):
        cx    = self.width // 2
        pulse = 1.0 + 0.035 * math.sin(self._tick * 0.07)

        # Título
        title_y = self.height // 5
        self._blit_shadow(
            "2D PLATFORM GAME",
            self._font_title, cx, title_y,
            self.C_YELLOW, self.C_ORANGE,
            shadow_offset=4, scale=pulse,
        )

        # Subtítulo piscante
        if self._blink:
            sub = self._font_sub.render("── USE AS SETAS E ENTER ──", True, self.C_DIM)
            self.screen.blit(sub, sub.get_rect(center=(cx, title_y + 60)))

        sep_y = title_y + 88
        self._draw_separator(sep_y)

        # Opções
        start_y = sep_y + 46
        spacing = 50
        for i, (label, color) in enumerate(zip(self._options, self._colors)):
            self._draw_option(f"[ {label} ]", color, cx,
                              start_y + i * spacing, selected=(i == self._sel))

        # Mini-personagem animado
        sel_y = start_y + self._sel * spacing
        self._draw_mini_player(cx - 190, sel_y)

        # Jogador atual (nome que será salvo na pontuação)
        if self.player_name:
            who = self._font_small.render(
                f"JOGADOR:  {self.player_name}", True, self.C_GREEN)
            self.screen.blit(who, who.get_rect(center=(cx, self.height - 40)))

        # Rodapé
        footer = self._font_small.render(
            "↑↓  NAVEGAR     ENTER  CONFIRMAR     ESC  SAIR",
            True, self.C_DIM,
        )
        self.screen.blit(footer, footer.get_rect(center=(cx, self.height - 18)))

    def _draw_option(self, label, color, cx, cy, selected):
        if selected:
            bw, bh = 290, 42
            box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            box.fill((*color, 28))
            self.screen.blit(box, box.get_rect(center=(cx, cy)))
            rect = pygame.Rect(0, 0, bw, bh)
            rect.center = (cx, cy)
            pygame.draw.rect(self.screen, color, rect, 2)
            for corner in (rect.topleft, rect.topright,
                           rect.bottomleft, rect.bottomright):
                pygame.draw.rect(self.screen, self.C_YELLOW,
                                 (corner[0] - 3, corner[1] - 3, 6, 6))
            self._blit_shadow(label, self._font_option, cx, cy,
                              color, (0, 0, 0), shadow_offset=2)
        else:
            s = self._font_option.render(label, True, self.C_DIM)
            self.screen.blit(s, s.get_rect(center=(cx, cy)))

    def _draw_mini_player(self, cx, cy):
        """Mini-sprite do player animado (bobbing), idêntico ao Player.draw)."""
        t   = self._tick
        bob = int(math.sin(t * 0.15) * 3)
        cy += bob
        pygame.draw.rect(self.screen, self.C_GREEN,        (cx - 8, cy - 12, 16, 18))
        pygame.draw.rect(self.screen, (255, 255, 100),     (cx + 2, cy - 9,   4,  4))
        leg = int(math.sin(t * 0.2) * 4)
        pygame.draw.rect(self.screen, self.C_GREEN,        (cx - 6, cy + 6,   5,  6 + leg))
        pygame.draw.rect(self.screen, self.C_GREEN,        (cx + 1, cy + 6,   5,  6 - leg))

    def _draw_separator(self, y):
        cx   = self.width // 2
        half = 150
        pygame.draw.line(self.screen, self.C_DIM, (cx - half, y), (cx + half, y), 1)
        for dx in (-half, half):
            pygame.draw.rect(self.screen, self.C_CYAN, (cx + dx - 3, y - 3, 6, 6))

    # ─────────────────────────────────────────────────────────────
    #  Painel (base das telas de nome / pontuações / créditos)
    # ─────────────────────────────────────────────────────────────
    def _draw_panel(self, pw, ph, title):
        cx, cy = self.width // 2, self.height // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((10, 10, 25, 230))
        prect = panel.get_rect(center=(cx, cy))
        self.screen.blit(panel, prect)

        pygame.draw.rect(self.screen, self.C_PLATFORM, prect, 2)
        pygame.draw.rect(self.screen, self.C_DIM, prect.inflate(-8, -8), 1)

        for corner in (prect.topleft, prect.topright,
                       prect.bottomleft, prect.bottomright):
            pygame.draw.rect(self.screen, self.C_YELLOW,
                             (corner[0] - 4, corner[1] - 4, 8, 8))

        self._blit_shadow(f"── {title} ──", self._font_option,
                          cx, prect.top + 34,
                          self.C_YELLOW, (80, 60, 0), shadow_offset=2)
        return prect

    # ─────────────────────────────────────────────────────────────
    #  Tela de Nome do Jogador
    # ─────────────────────────────────────────────────────────────
    def _draw_name_input(self):
        cx = self.width // 2
        prect = self._draw_panel(460, 230, "QUEM ESTÁ JOGANDO?")

        hint = self._font_small.render(
            "O nome é salvo junto com a sua pontuação", True, self.C_DIM)
        self.screen.blit(hint, hint.get_rect(center=(cx, prect.top + 72)))

        # caixa de digitação
        box = pygame.Rect(0, 0, 340, 52)
        box.center = (cx, prect.top + 124)
        pygame.draw.rect(self.screen, (5, 5, 15), box)
        pygame.draw.rect(self.screen, self.C_GREEN, box, 2)

        shown = self._name_buf or ""
        text  = self._font_option.render(shown, True, self.C_WHITE)
        trect = text.get_rect(midleft=(box.left + 14, box.centery))
        self.screen.blit(text, trect)

        # cursor piscando
        if self._blink and len(shown) < self.MAX_NAME_LEN:
            cur_x = trect.right + 3
            pygame.draw.rect(self.screen, self.C_GREEN,
                             (cur_x, box.centery - 13, 12, 26))

        count = self._font_small.render(
            f"{len(shown)}/{self.MAX_NAME_LEN}", True, self.C_DIM)
        self.screen.blit(count, count.get_rect(midright=(box.right - 10,
                                                        box.bottom + 14)))

        if not shown:
            empty = self._font_small.render(
                f"vazio = {Scoreboard.DEFAULT_NAME}", True, self.C_DIM)
            self.screen.blit(empty, empty.get_rect(midleft=(box.left,
                                                            box.bottom + 14)))

        go_color = self.C_ORANGE if self._blink else self.C_DIM
        go = self._font_small.render("[ ENTER — COMEÇAR ]   [ ESC — VOLTAR ]",
                                     True, go_color)
        self.screen.blit(go, go.get_rect(center=(cx, prect.bottom - 26)))

    # ─────────────────────────────────────────────────────────────
    #  Tela de Histórico de Pontuações
    # ─────────────────────────────────────────────────────────────
    def _draw_scores(self):
        cx = self.width // 2
        prect = self._draw_panel(620, 420, "PONTUAÇÕES")

        # cabeçalho da tabela
        left  = prect.left + 34
        right = prect.right - 34
        head_y = prect.top + 74
        cols = [
            ("#",     left,        "left"),
            ("NOME",  left + 46,   "left"),
            ("SCORE", left + 250,  "right"),
            ("FASE",  left + 330,  "right"),
            ("QUANDO", right,      "right"),
        ]
        for label, x, align in cols:
            s = self._font_small.render(label, True, self.C_DIM)
            rect = s.get_rect()
            if align == "right":
                rect.topright = (x, head_y)
            else:
                rect.topleft = (x, head_y)
            self.screen.blit(s, rect)

        line_y = head_y + 22
        pygame.draw.line(self.screen, self.C_DIM, (left, line_y), (right, line_y), 1)

        if not self._scores:
            empty = self._font_small.render(
                "Nenhuma partida registrada ainda.", True, self.C_WHITE)
            self.screen.blit(empty, empty.get_rect(center=(cx, line_y + 60)))
            hint = self._font_small.render(
                "Jogue uma partida para aparecer aqui!", True, self.C_DIM)
            self.screen.blit(hint, hint.get_rect(center=(cx, line_y + 84)))
        else:
            row_y = line_y + 16
            medals = {0: self.C_YELLOW, 1: (200, 200, 210), 2: (205, 127, 50)}
            for i, entry in enumerate(self._scores):
                color = medals.get(i, self.C_WHITE)

                # destaque da linha do pódio
                if i < 3:
                    hl = pygame.Surface((right - left, 24), pygame.SRCALPHA)
                    hl.fill((*color, 20))
                    self.screen.blit(hl, (left, row_y - 3))

                status = entry.get("status", "")
                name   = str(entry.get("name", "?"))[:self.MAX_NAME_LEN]
                values = [
                    (f"{i + 1}",                 left,       "left",  color,          self._font_score),
                    (name,                       left + 46,  "left",  color,          self._font_score),
                    (f"{entry.get('score', 0)}", left + 250, "right", self.C_YELLOW_S, self._font_score),
                    (f"{entry.get('level', 1)}", left + 330, "right", self.C_CYAN,     self._font_score),
                    (str(entry.get("date", "")), right,      "right", self.C_DIM,      self._font_small),
                ]
                for text, x, align, col, font in values:
                    s = font.render(text, True, col)
                    rect = s.get_rect()
                    if align == "right":
                        rect.topright = (x, row_y)
                    else:
                        rect.topleft = (x, row_y)
                    self.screen.blit(s, rect)

                # marcador de como a partida terminou
                if status:
                    scol = (self.C_GREEN if status == Scoreboard.STATUS_WIN
                            else self.C_RED if status == Scoreboard.STATUS_LOSS
                            else self.C_DIM)
                    pygame.draw.rect(self.screen, scol,
                                     (left + 350, row_y + 6, 8, 8))

                row_y += 26

        back_color = self.C_ORANGE if self._blink else self.C_DIM
        back = self._font_small.render("[ ESC / ENTER  —  VOLTAR ]", True, back_color)
        self.screen.blit(back, back.get_rect(center=(cx, prect.bottom - 24)))

    # ─────────────────────────────────────────────────────────────
    #  Tela de Créditos
    # ─────────────────────────────────────────────────────────────
    def _draw_credits(self):
        cx = self.width // 2
        prect = self._draw_panel(440, 310, "CRÉDITOS")

        lines = [
            ("DESENVOLVIDO POR",       self.C_DIM),
            ("Ariel Machado",          self.C_WHITE),
            ("Rafael Scarpelli",          self.C_WHITE),
            ("Rômulo Jordão",          self.C_WHITE),

            ("",                       None),
            ("ENGINE",                 self.C_DIM),
            ("Python 3  +  Pygame",    self.C_CYAN),
            ("",                       None),
            ("ARTE & DESIGN",          self.C_DIM),
            ("Nós mesmos",         self.C_GREEN),
            ("",                       None),
            ("VERSÃO  1.0.0",          self.C_DIM),
        ]

        ly = prect.top + 74
        for text, color in lines:
            if text and color:
                s = self._font_small.render(text, True, color)
                self.screen.blit(s, s.get_rect(center=(cx, ly)))
            ly += 19

        back_color = self.C_ORANGE if self._blink else self.C_DIM
        back = self._font_small.render("[ ESC / ENTER  —  VOLTAR ]", True, back_color)
        self.screen.blit(back, back.get_rect(center=(cx, prect.bottom - 22)))

    # ─────────────────────────────────────────────────────────────
    #  Helper
    # ─────────────────────────────────────────────────────────────
    def _blit_shadow(self, text, font, cx, cy, color,
                     shadow_color, shadow_offset=3, scale=1.0):
        surf = font.render(text, True, color)
        if scale != 1.0:
            w = int(surf.get_width()  * scale)
            h = int(surf.get_height() * scale)
            surf = pygame.transform.scale(surf, (w, h))
        shad = font.render(text, True, shadow_color)
        if scale != 1.0:
            shad = pygame.transform.scale(shad, (surf.get_width(), surf.get_height()))
        self.screen.blit(shad, shad.get_rect(center=(cx + shadow_offset, cy + shadow_offset)))
        self.screen.blit(surf,  surf.get_rect(center=(cx, cy)))