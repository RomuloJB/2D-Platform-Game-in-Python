import sys
import random

import pygame

from src.utilz.Constants import *
from src.levels.LevelGenerator import LevelGenerator
from src.levels.LevelConfig import LEVELS
from src.gamestates.Gamestate import Gamestate, State
from src.entities.Player import Player
from src.core.Camera import Camera
from src.ui.Shop import Shop
from src.gamestates.MenuState import MenuState
from src.core.Hud import (
    draw_background, draw_hud, draw_controls,
    draw_crosshair, draw_game_over, draw_victory, draw_level_banner,
)


# ── fábricas ───────────────────────────────────────────────────────────────────

def make_world(gs: Gamestate):
    cfg = LEVELS[gs.current_level - 1]
    return LevelGenerator(cfg)


def make_player(x=80, y=None):
    if y is None:
        y = SCREEN_H - TILE_SIZE - 100
    return Player(x, y)


def reset_session(gs: Gamestate):
    world     = make_world(gs)
    camera    = Camera()
    camera.x  = 0
    particles = []
    bullets   = []
    tick      = 0
    return world, camera, particles, bullets, tick


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Plataforma 2D")
    clock = pygame.time.Clock()

    try:
        font_big = pygame.font.SysFont("arial", 64, bold=True)
        font     = pygame.font.SysFont("arial", 24, bold=True)
        font_sm  = pygame.font.SysFont("arial", 16)
    except Exception:
        font_big = pygame.font.Font(None, 64)
        font     = pygame.font.Font(None, 28)
        font_sm  = pygame.font.Font(None, 20)

    # ── estados iniciais ───────────────────────────────────────────────────────
    menu   = MenuState(screen)     # começa no menu
    in_menu = True                 # True = mostrando menu

    gs     = Gamestate()
    player = make_player()
    world, camera, particles, bullets, tick = reset_session(gs)

    shop         = None
    damage_flash = 0
    prev_health  = player.health
    level_banner = 0

    pygame.mouse.set_visible(False)

    running = True
    while running:
        clock.tick(FPS)

        # ── MENU ──────────────────────────────────────────────────────────────
        if in_menu:
            menu.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                result = menu.handle_event(event)
                if result == "play":
                    in_menu      = False
                    level_banner = 50
                    pygame.mouse.set_visible(False)
                elif result == "quit":
                    running = False
            menu.draw()
            pygame.display.flip()
            continue   # pula o resto do loop enquanto estiver no menu

        # ── CONFIG DA FASE ATUAL ───────────────────────────────────────────────
        cfg = LEVELS[gs.current_level - 1]

        # ── EVENTOS ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # ESC volta ao menu (não fecha o jogo)
                if event.key == pygame.K_ESCAPE:
                    in_menu = True
                    pygame.mouse.set_visible(True)

                elif event.key == pygame.K_r:
                    if gs.victory:
                        # reinício total — volta ao menu
                        in_menu = True
                        gs      = Gamestate()
                        player  = make_player()
                        world, camera, particles, bullets, tick = reset_session(gs)
                        shop         = None
                        damage_flash = 0
                        prev_health  = player.health
                        pygame.mouse.set_visible(True)

                    elif gs.game_over:
                        # regenera mapa, mantém player
                        gs.restart_level()
                        world, camera, particles, bullets, tick = reset_session(gs)
                        player.soft_reset(80, SCREEN_H - TILE_SIZE - 100)
                        prev_health  = player.health
                        damage_flash = 0
                        level_banner = 40

            # loja recebe eventos
            if gs.at_checkpoint and shop is not None:
                left_shop = shop.handle_event(event, player)
                if left_shop:
                    gs.leave_checkpoint()
                    shop = None
                    

            # tiro por clique único
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gs.playing:
                    mx, my = event.pos
                    player.shoot(mx, my, int(camera.x), int(camera.y), bullets)

        # tiro contínuo
        if gs.playing and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            player.shoot(mx, my, int(camera.x), int(camera.y), bullets)

        keys = pygame.key.get_pressed()
        tick += 1

        # ── UPDATE ────────────────────────────────────────────────────────────
        if gs.playing and player.alive:
            player.handle_input(keys)

            world.update_chunks(player.rect.x)
            nearby_plats   = world.get_nearby_platforms(camera.x)
            nearby_enemies = world.get_nearby_enemies(camera.x)
            nearby_coins   = world.get_nearby_coins(camera.x)
            nearby_portals = world.get_nearby_portals(camera.x)

            for p in nearby_plats:
                p.update(tick)
            for portal in nearby_portals:
                portal.update()

            player.update(nearby_plats, nearby_enemies, nearby_coins, particles)

            # colisão com portais
            for portal in nearby_portals:
                if portal.active and player.rect.colliderect(portal.rect):
                    portal.active = False
                    shop = Shop(gs.current_level, portal.kind)
                    gs.enter_checkpoint(portal.kind)
                    break

            # balas
            for b in bullets:
                b.update(nearby_enemies, nearby_plats, particles)
                if b.scored:
                    player.score += 150
                    b.scored = False
            bullets = [b for b in bullets if b.alive]
            bullets = [b for b in bullets
                       if abs(b.x - player.rect.centerx) < SCREEN_W * 1.5]

            for e in nearby_enemies:
                e.update(nearby_plats, player.rect)
            for c in nearby_coins:
                c.update()

            camera.update(player)

            if player.health < prev_health:
                damage_flash = 20
            prev_health = player.health

            if player.rect.top > SCREEN_H + 200:
                player.alive = False

        # morte
        if gs.playing and not player.alive:
            gs.player_died()

        # partículas
        for p in list(particles):
            p.update()
        particles = [p for p in particles if p.life > 0]

        if damage_flash > 0:
            damage_flash -= 1
        if level_banner > 0:
            level_banner -= 1

        # ── RENDER ────────────────────────────────────────────────────────────
        cam_x = int(camera.x)
        cam_y = int(camera.y)

        draw_background(screen, cam_x, cam_y,
                        bg_top=cfg.bg_top, bg_btm=cfg.bg_btm)

        for p in world.get_nearby_platforms(cam_x):
            p.draw(screen, cam_x, cam_y)
        for c in world.get_nearby_coins(cam_x):
            c.draw(screen, cam_x, cam_y)
        for e in world.get_nearby_enemies(cam_x):
            e.draw(screen, cam_x, cam_y)
        for portal in world.get_nearby_portals(cam_x):
            portal.draw(screen, cam_x, cam_y)
        for b in bullets:
            b.draw(screen, cam_x, cam_y)
        player.draw(screen, cam_x, cam_y)
        for p in particles:
            p.draw(screen, cam_x, cam_y)

        if damage_flash > 0:
            flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            alpha = int(80 * damage_flash / 20)
            flash_surf.fill((255, 50, 50, alpha))
            screen.blit(flash_surf, (0, 0))

        distance = max(0, player.rect.x - 80) / 60
        draw_hud(
            screen, player, distance, font, font_sm,
            level_num=gs.current_level,
            level_name=cfg.name,
            level_length=cfg.length_chunks,
            player_x=player.rect.x,
        )
        draw_controls(screen, font_sm)

        if gs.playing or gs.game_over:
            mx, my = pygame.mouse.get_pos()
            draw_crosshair(screen, mx, my)

        # overlays
        if gs.game_over:
            draw_game_over(screen, font_big, font, gs.current_level)

        if gs.victory:
            draw_victory(screen, font_big, font, player.score, player.coins)

        if gs.at_checkpoint and shop is not None:
            shop.draw(screen, player)

        if level_banner > 0 and gs.playing:
            draw_level_banner(screen, font_big, gs.current_level, cfg.name, level_banner)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()