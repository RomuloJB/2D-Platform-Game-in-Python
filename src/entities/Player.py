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

    def apply_input(self, input_map: dict):
        self.vel_x = 0
        if input_map["left"]:
            self.vel_x = -self.speed
        if input_map["right"]:
            self.vel_x = self.speed
        if input_map["jump"] and self.on_ground:
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
