import pygame
from src.entities.Player import Player

class Inputs:
    def __init__(self, player):
            self.player = player

    def handle_input(self) -> dict:
        keys = pygame.key.get_pressed()
        return {
            "left":  keys[pygame.K_LEFT] or keys[pygame.K_a],
            "right": keys[pygame.K_RIGHT] or keys[pygame.K_d],
            "jump":  keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w],
        }
