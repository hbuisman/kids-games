import pygame
from enum import Enum

class PlatformStyle(Enum):
    GRASS = 1
    CONCRETE = 2
    # Add more styles as needed

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, style=PlatformStyle.GRASS):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.set_style(style)

    def set_style(self, style):
        if style == PlatformStyle.GRASS:
            texture_image = pygame.image.load("grass_block-removebg.png").convert_alpha()
            texture_width = self.rect.height  # New width for the texture
            texture_height = self.rect.height  # New height for the texture
            texture_image = pygame.transform.scale(texture_image, (texture_width, texture_height))
            self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.image.set_colorkey((255, 255, 255))  # Set black as the transparent color
            for x in range(0, self.rect.width, texture_width):
                scaled_texture = pygame.transform.scale(texture_image, (texture_width, self.rect.height))
                self.image.blit(scaled_texture, (x, 0))
        elif style == PlatformStyle.CONCRETE:
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill((128, 128, 128))  # Gray color for concrete platform
        # Add more styles as needed


    def update(self):
        pass  # Add any update logic for the platform