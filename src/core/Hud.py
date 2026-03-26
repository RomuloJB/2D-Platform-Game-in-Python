import random
import math

import pygame

from src.utilz.Constants import *
from src.utilz.Utilz import draw_gradient_rect


def draw_background(surf, cam_x, cam_y, bg_top=None, bg_btm=None):
    top = bg_top or C_BG_TOP
    btm = bg_btm or C_BG_BTM
    draw_gradient_rect(surf, pygame.Rect(0, 0, SCREEN_W, SCREEN_H), top, btm)

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


def draw_hud(surf, player, distance, font, font_sm,
             level_num=1, level_name="", level_length=None, player_x=None):
    hud_surf = pygame.Surface((320, 80), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 120))
    surf.blit(hud_surf, (10, 10))

    # corações
    for i in range(player.max_health):
        color = (220, 60, 60) if i < player.health else (60, 60, 80)
        heart_x = 20 + i * 28
        pygame.draw.polygon(surf, color, [
            (heart_x, 32), (heart_x - 8, 23), (heart_x - 8, 16),
            (heart_x - 4, 13), (heart_x, 17), (heart_x + 4, 13),
            (heart_x + 8, 16), (heart_x + 8, 23)
        ])

    score_txt  = font.render(f"Score: {player.score}", True, C_HUD)
    coins_txt  = font_sm.render(f"Coins: {player.coins}", True, (255, 215, 0))
    dist_txt   = font_sm.render(f"{int(distance)}m", True, (180, 220, 255))
    level_txt  = font_sm.render(f"Fase {level_num} — {level_name}", True, (200, 200, 255))

    surf.blit(score_txt, (20, 45))
    surf.blit(coins_txt, (180, 48))
    surf.blit(dist_txt,  (270, 48))
    surf.blit(level_txt, (20, 70))

    # barra de progresso da fase
    if level_length and player_x is not None:
        prog = min(1.0, max(0.0, player_x / (level_length * CHUNK_WIDTH * TILE_SIZE)))
        bar_x, bar_y, bar_w, bar_h = 10, SCREEN_H - 18, SCREEN_W - 20, 8
        pygame.draw.rect(surf, (40, 40, 60),
            pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=4)
        filled = int(bar_w * prog)
        if filled > 0:
            pygame.draw.rect(surf, (80, 180, 255),
                pygame.Rect(bar_x, bar_y, filled, bar_h), border_radius=4)
        # marcador de mid-checkpoint
        mid_prog = 0.5
        mx = bar_x + int(bar_w * mid_prog)
        pygame.draw.rect(surf, (255, 200, 50),
            pygame.Rect(mx - 1, bar_y - 2, 3, bar_h + 4))


def draw_controls(surf, font_sm):
    hints = ["← → : mover", "Espaço/↑ : pular", "Clique esq: atirar", "R : reiniciar"]
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


def draw_game_over(surf, font_big, font, level_num):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surf.blit(ov, (0, 0))
    t1 = font_big.render("GAME OVER", True, (220, 60, 60))
    t2 = font.render(f"Fase {level_num} — mapa regenerado", True, (200, 200, 220))
    t3 = font.render("Coins e upgrades mantidos  |  R reiniciar", True, C_HUD)
    surf.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 80))
    surf.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2))
    surf.blit(t3, (SCREEN_W // 2 - t3.get_width() // 2, SCREEN_H // 2 + 40))


def draw_victory(surf, font_big, font, score, coins):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 180))
    surf.blit(ov, (0, 0))
    t1 = font_big.render("VITÓRIA!", True, (255, 215, 0))
    t2 = font.render(f"Score final: {score}", True, (200, 255, 200))
    t3 = font.render(f"Coins restantes: {coins}", True, (255, 215, 0))
    t4 = font.render("Pressione R para jogar novamente", True, C_HUD)
    surf.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 100))
    surf.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 - 20))
    surf.blit(t3, (SCREEN_W // 2 - t3.get_width() // 2, SCREEN_H // 2 + 20))
    surf.blit(t4, (SCREEN_W // 2 - t4.get_width() // 2, SCREEN_H // 2 + 70))


def draw_level_banner(surf, font_big, level_num, level_name, timer):
    """Exibe banner 'Fase N — Nome' por alguns frames ao iniciar fase."""
    alpha = min(255, timer * 6)
    ov = pygame.Surface((SCREEN_W, 100), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 100))
    surf.blit(ov, (0, SCREEN_H // 2 - 50))
    t = font_big.render(f"Fase {level_num}  —  {level_name}", True, (255, 220, 80))
    t.set_alpha(alpha)
    surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 30))