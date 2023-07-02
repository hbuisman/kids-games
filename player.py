import pygame
import math
import logging

import Box2D
from Box2D.b2 import (world, edgeShape, polygonShape, dynamicBody, staticBody, vec2, bodyDef, staticBody)


from pygame.locals import *
import pygame.mixer

PPM=20


class Player(pygame.sprite.Sprite):
    def __init__(self, screen, screen_width, screen_height):
        super().__init__()
        self.screen = screen
        self.original_image = pygame.image.load("player-transparent.png").convert_alpha()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = pygame.transform.scale(self.original_image, (64, 64))
        self.image.set_colorkey((255, 255, 255))  # Set white as transparent
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 60 - self.rect.height // 2)  # Start on bottom platform
        self.speed = 5
        self.angle = 0
        self.mask = None
        self.is_jumping = False
        self.jump_height = 100
        self.jump_speed = 10
        self.jump_count = 0
        self.gravity = 0.5  # Gravity value
        self.velocity = [0, 0]
        self.ouch_sound = pygame.mixer.Sound('ouch.wav')
        self.body = None 

        self.is_sliding = False  # Flag to indicate if the player is sliding
        self.slide = None  # Reference to the slide object the player is sliding on


    def create_body(self, world):
        # Create the Box2D body for the player
        body_def = bodyDef()
        body_def.type = dynamicBody
        body_def.position = (self.rect.centerx / PPM, self.rect.centery / PPM)  # Convert to Box2D world coordinates
        self.body = world.CreateBody(body_def)
        self.body.userData = self
        f = self.body.CreatePolygonFixture(box=(self.rect.width / 2 / PPM, self.rect.height / 2 / PPM), density=1.0)
        f.userData = "player"


    def update(self, keys):
        if self.is_sliding:
            self.slide_player(keys)
        else:
            self.default_player_behavior(keys)

        # Get the shape of the Box2D fixture
        shape = self.body.fixtures[0].shape
        
        # Calculate the AABB (axis-aligned bounding box) based on the shape and position of the fixture
        lower_bound, upper_bound = shape.get_vertices()
        aabb = b2AABB()
        aabb.lowerBound = self.body.transform * lower_bound
        aabb.upperBound = self.body.transform * upper_bound
        
        # Convert the AABB coordinates to pygame rect
        left = aabb.lowerBound.x * PPM
        top = aabb.lowerBound.y * PPM
        width = (aabb.upperBound.x - aabb.lowerBound.x) * PPM
        height = (aabb.upperBound.y - aabb.lowerBound.y) * PPM
        bounding_rect = pygame.Rect(left, top, width, height)
        
        # Draw the bounding box of the fixture
        pygame.draw.rect(self.screen, (255, 0, 0), bounding_rect, 1)

    def slide_player(self, keys):
        logging.debug("Sliding")
        if keys[K_LEFT]:
            self.body.ApplyLinearImpulse((-self.speed, 0), self.body.worldCenter, True)
        elif keys[K_RIGHT]:
            self.body.ApplyLinearImpulse((self.speed, 0), self.body.worldCenter, True)

        self.rect.x = self.body.position.x * PPM - self.rect.width // 2
        self.rect.y = self.body.position.y * PPM - self.rect.height // 2
        logging.debug((self.rect.x, self.rect.y))

    def default_player_behavior(self, keys):
        if keys[K_LEFT]:
            self.body.ApplyLinearImpulse((-self.speed, 0), self.body.worldCenter, True)
        elif keys[K_RIGHT]:
            self.body.ApplyLinearImpulse((self.speed, 0), self.body.worldCenter, True)

        if keys[K_SPACE]:  # Press space bar to jump
            if not self.is_jumping and not self.is_sliding:  # Only jump if not sliding
                self.body.ApplyLinearImpulse((0, -self.jump_speed), self.body.worldCenter, True)
                self.is_jumping = True
                self.jump_count = 0

        if self.is_jumping:
            # Calculate the vertical position of the jump based on a quadratic function
            if self.jump_count < self.jump_height:
                self.jump_count += 1
            else:
                self.is_jumping = False

        # Apply gravity
        self.body.ApplyForce((0, self.gravity), self.body.worldCenter, True)
        self.rect.x = self.body.position.x * PPM - self.rect.width // 2
        self.rect.y = self.body.position.y * PPM - self.rect.height // 2

        print(self.rect.x, ":", self.rect.y)

        # Create a mask for pixel-perfect collision detection
        self.mask = pygame.mask.from_surface(self.image)

    def bump_head(self):
        self.ouch_sound.play()  # Play the "ouch" audio
        print("Ouch!")