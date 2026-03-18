import random

import pygame

from src.utilz.Constants import *
from src.utilz.Utilz import draw_gradient_rect


def draw_background(surf, cam_x, cam_y):
    draw_gradient_rect(surf, pygame.Rect(0, 0, SCREEN_W, SCREEN_H),
                       C_BG_TOP, C_BG_BTM)

    rng = random.Random(42)
    for _ in range(80):
        sx = (rng.randint(0, 4000) - cam_x * 0.05) % SCREEN_W
        sy = (rng.randint(0, SCREEN_H) - cam_y * 0.02) % SCREEN_H
        r = rng.randint(1, 2)
        b = rng.randint(150, 255)
        pygame.draw.circle(surf, (b, b, 255), (int(sx), int(sy)), r)

    rng2 = random.Random(77)
    for i in range(12):
        mx = (rng2.randint(0, 6000) - cam_x * 0.2) % (SCREEN_W + 200) - 100
        mh = rng2.randint(80, 200)
        mw = rng2.randint(100, 200)
        my = SCREEN_H - mh
        points = [(mx, SCREEN_H), (mx + mw // 2, my), (mx + mw, SCREEN_H)]
        pygame.draw.polygon(surf, (25, 35, 70), points)


def draw_hud(surf, player, distance, font, font_sm):
    hud_surf = pygame.Surface((260, 70), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 120))
    surf.blit(hud_surf, (10, 10))

    for i in range(3):
        color = (220, 60, 60) if i < player.health else (60, 60, 80)
        heart_x = 20 + i * 35
        pygame.draw.polygon(surf, color, [
            (heart_x, 32), (heart_x - 10, 22), (heart_x - 10, 15),
            (heart_x - 5, 12), (heart_x, 16), (heart_x + 5, 12),
            (heart_x + 10, 15), (heart_x + 10, 22)
        ])

    score_txt = font.render(f"Score: {player.score}", True, C_HUD)
    dist_txt = font_sm.render(f"Distância: {int(distance)}m", True, (180, 220, 255))
    surf.blit(score_txt, (20, 45))
    surf.blit(dist_txt, (140, 52))


def draw_controls(surf, font_sm):
    hints = ["← → : mover", "Espaço/↑ : pular", "🖱 Clique esq: atirar", "R : reiniciar"]
    for i, h in enumerate(hints):
        t = font_sm.render(h, True, (150, 150, 200))
        surf.blit(t, (SCREEN_W - t.get_width() - 12, 12 + i * 20))


def draw_crosshair(surf, x, y):
    size = 10
    gap  = 4
    color = C_BULLET
    pygame.draw.line(surf, color, (x - size, y), (x - gap, y), 2)
    pygame.draw.line(surf, color, (x + gap,  y), (x + size, y), 2)
    pygame.draw.line(surf, color, (x, y - size), (x, y - gap), 2)
    pygame.draw.line(surf, color, (x, y + gap),  (x, y + size), 2)
    pygame.draw.circle(surf, color, (x, y), 3, 1)


def draw_game_over(surf, font_big, font):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surf.blit(ov, (0, 0))
    t1 = font_big.render("GAME OVER", True, (220, 60, 60))
    t2 = font.render("Pressione R para reiniciar", True, C_HUD)
    surf.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 60))
    surf.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 + 10))