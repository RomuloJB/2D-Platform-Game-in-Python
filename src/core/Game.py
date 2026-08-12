"""
Game — orquestra o jogo: loop principal (com dt), estados, câmera, HUD.
MenuState -> PLAYING -> CHECKPOINT(loja) -> PLAYING ... -> GAME_OVER / VICTORY.
"""

import sys

import pygame

from src.utilz.Constants import SCREEN_W, SCREEN_H, FPS, TITLE, TILE_SIZE
from src.input.Inputs import Inputs
from src.core.Camera import Camera
from src.core.World import World
from src.entities.Player import Player
from src.gamestates.Gamestate import Gamestate, State
from src.gamestates.MenuState import MenuState
from src.levels.LevelConfig import LEVELS
from src.ui.Shop import Shop
from src.core import Hud
from src.audio.Audio import AudioManager

# Caminho da musica de fundo tocada enquanto o jogo esta rodando (fora do menu).
MUSIC_THEME = "res/audio/music/theme.wav"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        try:
            self.font_big = pygame.font.SysFont("arial", 64, bold=True)
            self.font = pygame.font.SysFont("arial", 24, bold=True)
            self.font_sm = pygame.font.SysFont("arial", 16)
        except Exception:
            self.font_big = pygame.font.Font(None, 64)
            self.font = pygame.font.Font(None, 28)
            self.font_sm = pygame.font.Font(None, 20)

        self.inputs = Inputs()
        self.camera = Camera()
        self.audio = AudioManager()

        self.in_menu = True
        self.menu = MenuState(self.screen)

        self.gs = None
        self.player = None
        self.world = None
        self.shop = None
        self.banner_timer = 0
        self.damage_flash = 0
        self.prev_health = 0

    def _spawn(self):
        return 80, SCREEN_H - TILE_SIZE - 100

    def start_new_game(self):
        self.gs = Gamestate()
        x, y = self._spawn()
        self.player = Player(x, y)
        self._load_level(self.gs.current_level)

    def _load_level(self, level_num):
        config = LEVELS[level_num - 1]
        x, y = self._spawn()
        if self.player is None:
            self.player = Player(x, y)
        else:
            self.player.soft_reset(x, y)
        self.world = World(config, self.player)
        self.camera = Camera()
        self.banner_timer = 90
        self.prev_health = self.player.health
        self.damage_flash = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.in_menu:
                action = self.menu.handle_event(event)
                if action == "play":
                    self.in_menu = False
                    self.start_new_game()
                    self.audio.play_music(MUSIC_THEME)
                elif action == "quit":
                    self.running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.gs.at_checkpoint:
                    self.in_menu = True
                    self.audio.stop_music()
                    continue
                if event.key == pygame.K_r and self.gs.game_over:
                    self._load_level(self.gs.current_level)
                    self.gs.restart_level()
                if event.key == pygame.K_r and self.gs.victory:
                    self.start_new_game()
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.player.switch_weapon(event.key - pygame.K_1)

            if self.gs.at_checkpoint and self.shop is not None:
                if self.shop.handle_event(event, self.player):
                    self.gs.leave_checkpoint()
                    self.shop = None

            if (self.gs.playing and event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1):
                mx, my = pygame.mouse.get_pos()
                fired = self.player.shoot(mx, my, self.camera.x, self.camera.y,
                                          self.world.bullets)
                if fired:
                    self.audio.play_sfx("shot")

        if self.gs and self.gs.playing and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            fired = self.player.shoot(mx, my, self.camera.x, self.camera.y,
                                      self.world.bullets)
            if fired:
                self.audio.play_sfx("shot")

    def update(self, dt):
        if self.in_menu:
            self.menu.update()
            return

        if self.gs.playing:
            input_map = self.inputs.poll()
            self.player.apply_input(input_map)

            self.camera.update(self.player, dt)
            self.world.update(dt, self.camera.x)

            # caiu no vazio
            if self.player.rect.top > SCREEN_H + 200:
                self.player.alive = False

            if self.player.health < self.prev_health:
                self.damage_flash = 20
            self.prev_health = self.player.health

            if not self.player.alive:
                self.gs.player_died()
                return

            portal = self.world.portal_touched()
            if portal is not None:
                portal.active = False
                self.shop = Shop(self.gs.current_level, portal.kind)
                self.gs.enter_checkpoint(portal.kind)

            if self.banner_timer > 0:
                self.banner_timer -= 1
            if self.damage_flash > 0:
                self.damage_flash -= 1

    def render(self):
        if self.in_menu:
            self.menu.draw()
            pygame.display.flip()
            return

        cfg = self.world.config
        cam_x, cam_y = int(self.camera.x), int(self.camera.y)
        Hud.draw_background(self.screen, cam_x, cam_y, cfg.bg_top, cfg.bg_btm,
                            getattr(cfg, "bg_image", None))
        self.world.draw(self.screen, cam_x, cam_y)

        if self.damage_flash > 0:
            flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash.fill((255, 50, 50, int(80 * self.damage_flash / 20)))
            self.screen.blit(flash, (0, 0))

        distance = max(0, self.player.position.x - 80) / 60
        Hud.draw_hud(self.screen, self.player, distance, self.font, self.font_sm,
                     level_num=self.gs.current_level, level_name=cfg.name,
                     level_length=cfg.length_chunks, player_x=self.player.position.x)
        Hud.draw_controls(self.screen, self.font_sm)

        if self.gs.playing or self.gs.game_over:
            mx, my = pygame.mouse.get_pos()
            Hud.draw_crosshair(self.screen, mx, my)

        if self.banner_timer > 0 and self.gs.playing:
            Hud.draw_level_banner(self.screen, self.font_big,
                                  self.gs.current_level, cfg.name, self.banner_timer)

        if self.gs.at_checkpoint and self.shop is not None:
            self.shop.draw(self.screen, self.player)
        elif self.gs.game_over:
            Hud.draw_game_over(self.screen, self.font_big, self.font,
                               self.gs.current_level)
        elif self.gs.victory:
            Hud.draw_victory(self.screen, self.font_big, self.font,
                             self.player.score, self.player.coins)

        pygame.display.flip()

    def run(self):
        prev_level = None
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 1 / 20)

            if self.gs is not None:
                prev_level = self.gs.current_level

            self.handle_events()
            self.update(dt)

            if (self.gs is not None and self.gs.playing
                    and prev_level is not None
                    and self.gs.current_level != prev_level):
                self._load_level(self.gs.current_level)

            self.render()

        pygame.quit()
        sys.exit()