import pygame
import sys
from src.entities.Player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("2D Platform Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        self.player = Player(100,100)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        self.player.handle_input()
        self.player.update(self.screen_height)

    def render(self):
        self.screen.fill((0, 0, 0))  # Tela preta
        self.player.render(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()