"""Inputs — traduz teclado em dicionário de ações tipado."""

import pygame


class Inputs:
    def poll(self) -> dict:
        keys = pygame.key.get_pressed()
        return {
            "left":  keys[pygame.K_LEFT] or keys[pygame.K_a],
            "right": keys[pygame.K_RIGHT] or keys[pygame.K_d],
            "jump":  keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w],
        }

    # compat com chamada antiga
    def handle_input(self) -> dict:
        return self.poll()
