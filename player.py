import pygame
import math
import logging

from pygame.locals import *
import pygame.mixer


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.original_image = pygame.image.load("player-transparent.png").convert_alpha()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = pygame.transform.scale(self.original_image, (64, 64))
        self.image.set_colorkey((255, 255, 255))  # Set white as transparent
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 40 - self.rect.height // 2)  # Start on bottom platform
        self.speed = 5
        self.angle = 0
        self.is_jumping = False
        self.jump_height = 100
        self.jump_speed = 10
        self.jump_count = 0
        self.gravity = 0.5  # Gravity value
        self.velocity = [0, 1]
        self.ouch_sound = pygame.mixer.Sound('ouch.wav')

    def update(self, keys):
        if keys[K_LEFT]:
            self.velocity[0] = -self.speed
        elif keys[K_RIGHT]:
            self.velocity[0] = self.speed
        else:
            self.velocity[0] = 0
        if keys[K_SPACE]:  # Press space bar to jump
            if not self.is_jumping:
                self.velocity[1] = -10
                self.is_jumping = True
                self.jump_count = 0

        if self.is_jumping:
            # Calculate the vertical position of the jump based on a quadratic function
            if self.jump_count < self.jump_height:
                self.jump_count += 1
            else:
                self.is_jumping = False
                self.velocity[1] = 0

        # Apply gravity
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if (self.velocity[1] != self.gravity):
            logging.debug(self.velocity)

    def bump_head(self):
        self.ouch_sound.play()  # Play the "ouch" audio
        print("Ouch!")