import pygame
import sys
from src.entities.Player import Player
from src.input.Inputs import Inputs
from src.ui.Ui import Ui

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
        self.ground_level = self.screen_height - 80

        self.player = Player(100,100)
        self.inputs = Inputs(self.player)
        self.ui = Ui()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        input_map = self.inputs.handle_input()
        self.player.apply_input(input_map)
        self.player.update(self.ground_level)

    def render(self):
        self.screen.fill((0, 0, 0))

        pygame.draw.line(self.screen, (255, 255, 255), (0, self.ground_level), 
                        (self.screen_width, self.ground_level), 2)
        
        self.ui.render(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()