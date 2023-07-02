import pygame
import math
from typing import List

import Box2D
from Box2D.b2 import (world, edgeShape, polygonShape, dynamicBody, staticBody, vec2, bodyDef, staticBody)

PPM=20

# Slide class
class Slide(pygame.sprite.Sprite):
    def __init__(self, screen, top_left: List[int], thickness, length, angle):
        super().__init__()
        self.screen = screen
        self.top_left = top_left
        self.thickness = thickness
        self.length = length
        self.angle = angle
        self.angle_rad = math.radians(angle)
        self.image = None
        self.rect = None
        self.mask = None  # Mask for pixel-perfect collision detection
        self.body = None
        self.world = None

        self.update()

    def create_body(self, world):
        # Create the Box2D body for the slide
        body_def = bodyDef()
        body_def.type = staticBody
        body_def.position = (self.rect.x / PPM, self.rect.y / PPM)
        self.body = world.CreateBody(body_def)
        self.body.userData = self

        vertices = self.transform_points()
        f = self.body.CreatePolygonFixture(vertices=vertices)
        f.userData = "slide"

    def get_slide_slope(self):
        slide_angle_rad = self.angle_rad - math.pi / 2  # Subtract 90 degrees (π/2 radians)
        return math.tan(slide_angle_rad)

    def get_slide_intercept(self, slide_slope):
        return self.top_left[1] - slide_slope * self.top_left[0]

    def get_top_slide_y(self, x):
        slide_slope = self.get_slide_slope()
        slide_intercept = self.get_slide_intercept(slide_slope)
        slide_height_offset = 0
        return slide_slope * x + slide_intercept + slide_height_offset

    def transform_points(self):
        transformed_points = []
        for point in [(0, 0), (self.length, 0), (self.length, self.thickness), (0, self.thickness)]:
            x = point[0] * math.cos(self.angle_rad) - point[1] * math.sin(self.angle_rad)
            y = point[0] * math.sin(self.angle_rad) + point[1] * math.cos(self.angle_rad)
            transformed_points.append(vec2(x / PPM, y / PPM))
        return transformed_points

    def update(self):
        transformed_points = self.transform_points()
        min_x = min(transformed_points, key=lambda point: point[0]).x
        min_y = min(transformed_points, key=lambda point: point[1]).y
        max_x = max(transformed_points, key=lambda point: point[0]).x
        max_y = max(transformed_points, key=lambda point: point[1]).y
        width = max_x - min_x
        height = max_y - min_y

        self.image = pygame.Surface((width * PPM, height * PPM), pygame.SRCALPHA)  # Create a transparent surface
        pygame.draw.polygon(self.image, (255, 0, 0), [(x * PPM - min_x * PPM, y * PPM - min_y * PPM) for x, y in transformed_points])
        self.rect = self.image.get_rect()
        self.rect.topleft = (min_x * PPM + self.top_left[0], min_y * PPM + self.top_left[1])

        # Create a mask for pixel-perfect collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Update the Box2D body position
        if self.body:
            self.body.position = (self.rect.x / PPM, self.rect.y / PPM)