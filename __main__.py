import sys

import pygame

from src.utilz.Constants import *
from src.levels.Level1 import WorldGenerator
from src.entities.Player import Player
from src.core.Camera import Camera
from src.core.Hud import (
    draw_background, draw_hud, draw_controls,
    draw_crosshair, draw_game_over
)


def make_game():
    world = WorldGenerator()
    player = Player(80, SCREEN_H - TILE_SIZE - 100)
    camera = Camera()
    camera.x = 0
    particles = []
    bullets = []
    tick = 0
    return world, player, camera, particles, bullets, tick


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Plataforma 2D - MVP")
    clock = pygame.time.Clock()

    try:
        font_big = pygame.font.SysFont("arial", 64, bold=True)
        font     = pygame.font.SysFont("arial", 24, bold=True)
        font_sm  = pygame.font.SysFont("arial", 16)
    except Exception:
        font_big = pygame.font.Font(None, 64)
        font     = pygame.font.Font(None, 28)
        font_sm  = pygame.font.Font(None, 20)

    world, player, camera, particles, bullets, tick = make_game()
    damage_flash = 0
    prev_health = player.health
    pygame.mouse.set_visible(False)

    running = True
    while running:
        clock.tick(FPS)

        # ── Eventos ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    world, player, camera, particles, bullets, tick = make_game()
                    damage_flash = 0
                    prev_health = player.health
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                player.shoot(mx, my, int(camera.x), int(camera.y), bullets)

        # Tiro contínuo segurando o botão
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            player.shoot(mx, my, int(camera.x), int(camera.y), bullets)

        keys = pygame.key.get_pressed()
        tick += 1

        # ── Update ──
        if player.alive:
            player.handle_input(keys)

            world.update_chunks(player.rect.x)
            nearby_plats   = world.get_nearby_platforms(camera.x)
            nearby_enemies = world.get_nearby_enemies(camera.x)
            nearby_coins   = world.get_nearby_coins(camera.x)

            for p in nearby_plats:
                p.update(tick)

            player.update(nearby_plats, nearby_enemies, nearby_coins, particles)

            for b in bullets:
                b.update(nearby_enemies, nearby_plats, particles)
                if b.scored:
                    player.score += 150
                    b.scored = False
            bullets = [b for b in bullets if b.alive]
            bullets = [b for b in bullets
                       if abs(b.x - player.rect.centerx) < SCREEN_W * 1.5]

            for e in nearby_enemies:
                e.update(nearby_plats)

            for c in nearby_coins:
                c.update()

            camera.update(player)

            if player.health < prev_health:
                damage_flash = 20
            prev_health = player.health

            if player.rect.top > SCREEN_H + 200:
                player.alive = False

        # ── Partículas ──
        for p in list(particles):
            p.update()
        particles = [p for p in particles if p.life > 0]

        if damage_flash > 0:
            damage_flash -= 1

        # ── Desenhar ──
        cam_x = int(camera.x)
        cam_y = int(camera.y)

        draw_background(screen, cam_x, cam_y)

        for p in world.get_nearby_platforms(cam_x):
            p.draw(screen, cam_x, cam_y)

        for c in world.get_nearby_coins(cam_x):
            c.draw(screen, cam_x, cam_y)

        for e in world.get_nearby_enemies(cam_x):
            e.draw(screen, cam_x, cam_y)

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
        draw_hud(screen, player, distance, font, font_sm)
        draw_controls(screen, font_sm)

        mx, my = pygame.mouse.get_pos()
        draw_crosshair(screen, mx, my)

        if not player.alive:
            draw_game_over(screen, font_big, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()