import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = (0, 255 ,0)
        self.speed = 5
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_strength = -12
        self.on_ground = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = self.jump_strength

    def update(self, ground_level):
        self.vel_y += self.gravity
        
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Verifica colisão com o chão
        if self.y + self.height >= ground_level:
            self.y = ground_level - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
