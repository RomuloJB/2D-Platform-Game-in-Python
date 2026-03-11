import pygame
from entities.Player import Player

class Ui:
    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))