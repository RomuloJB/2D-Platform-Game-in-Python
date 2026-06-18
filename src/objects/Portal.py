"""Portal — fim de fase ('end') ou checkpoint/loja ('mid'). Herda GameObject."""

import math

import pygame

from src.objects.GameObject import GameObject
from src.utilz.Constants import SCREEN_W, Layer


class Portal(GameObject):
    W, H = 36, 72

    def __init__(self, x, y, kind="end"):
        super().__init__(x, y, self.W, self.H,
                         category=Layer.PORTAL, mask=Layer.PLAYER)
        self.kind = kind
        self.anim = 0.0
        self.active = True

    def update(self, dt: float, world=None) -> None:
        self.anim += 3 * dt

    def draw(self, surf, cam_x, cam_y):
        if not self.active:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        if rx < -60 or rx > SCREEN_W + 60:
            return

        pulse = abs(math.sin(self.anim)) * 0.4 + 0.6
        if self.kind == "mid":
            inner = (int(80 * pulse), int(200 * pulse), int(255 * pulse))
            outer = (20, 80, 140)
            label_color = (120, 220, 255)
        else:
            inner = (int(180 * pulse), int(80 * pulse), int(255 * pulse))
            outer = (80, 20, 140)
            label_color = (220, 160, 255)

        pygame.draw.rect(surf, outer,
            pygame.Rect(rx - 4, ry - 4, self.W + 8, self.H + 8), border_radius=8)
        pygame.draw.rect(surf, inner,
            pygame.Rect(rx, ry, self.W, self.H), border_radius=6)
        cx = rx + self.W // 2
        cy = ry + self.H // 2
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), int(10 * pulse))

        try:
            font = pygame.font.SysFont("arial", 11, bold=True)
        except Exception:
            font = pygame.font.Font(None, 14)
        txt = "LOJA" if self.kind == "mid" else "SAIDA"
        t = font.render(txt, True, label_color)
        surf.blit(t, (rx + self.W // 2 - t.get_width() // 2, ry - 18))
