import pygame
from src.entities.Player import Player

class Ui:
    def __init__(self, x, y):
        self.color = (0, 255, 0)
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))