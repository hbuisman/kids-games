import pygame
import math

# Slide class
class Slide(pygame.sprite.Sprite):
    def __init__(self, points, angle):
        super().__init__()
        self.points = points
        self.angle = angle
        self.angle_rad = angle * (3.14159 / 180)
        self.image = None
        self.rect = None
        self.update()

    def transform_points(self):
        transformed_points = []
        for point in self.points:
            x = point[0] * math.cos(self.angle_rad) + point[1] * math.sin(self.angle_rad)
            y = -point[0] * math.sin(self.angle_rad) + point[1] * math.cos(self.angle_rad)
            transformed_points.append((x, y))
        return transformed_points

    def update(self):
        transformed_points = self.transform_points()
        min_x = min(transformed_points, key=lambda point: point[0])[0]
        min_y = min(transformed_points, key=lambda point: point[1])[1]
        max_x = max(transformed_points, key=lambda point: point[0])[0]
        max_y = max(transformed_points, key=lambda point: point[1])[1]
        width = max_x - min_x
        height = max_y - min_y

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a transparent surface
        pygame.draw.polygon(self.image, (255, 0, 0), [(x - min_x, y - min_y) for x, y in transformed_points])
        self.rect = self.image.get_rect()
        self.rect.topleft = (min_x, min_y)