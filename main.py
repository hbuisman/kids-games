import player
import pygame
import platform_obj
import logging
from pygame.locals import *
import pygame.mixer
import pygame.font
import os
import slide

# Initialize pygame.mixer
pygame.mixer.init()
logging.basicConfig(level=logging.DEBUG)


screen_width = 800
screen_height = 600

# Initialize Pygame
pygame.init()

# Get the current display info
display_info = pygame.display.Info()
screen_width = display_info.current_w
screen_height = display_info.current_h

# Font for mouse coordinates
mouse_font = pygame.font.Font(None, 24)

# Set up the game window
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"  # Set the window position to the top-left corner
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Basic Platform Game")

# Inclined slide attributes
slide_points = [(500, 500), (500, 530), (900, 530), (900, 500)]
slide_angle = -45  # In degrees

# Create the Slide object
slide = slide.Slide(slide_points, slide_angle)
slide.rect.topleft = (slide_points[0][0], slide_points[0][1])


# Create the player
player = player.Player(screen_width, screen_height)

# Create platforms
platform1 = platform_obj.Platform(0, screen_height - 60, screen_width, 60)
platform2 = platform_obj.Platform(200, screen_height - 200, 200, 30)
platform3 = platform_obj.Platform(500, screen_height - 300, 150, 30)

# Create a sprite group for all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(slide, player, platform1, platform2, platform3)

# Create a sprite group for platforms
platforms = pygame.sprite.Group()
platforms.add(platform1, platform2, platform3)

dragging = False  # Flag to indicate if the slide is being dragged
offset_x = 0  # Offset between the mouse cursor and the slide's top-left corner
offset_y = 0


# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button pressed
                if slide.rect.collidepoint(event.pos):  # Check if the mouse is over the slide
                    dragging = True
                    offset_x = event.pos[0] - slide.rect.x
                    offset_y = event.pos[1] - slide.rect.y
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button released
                dragging = False
        elif event.type == MOUSEMOTION:
            if dragging:
                slide.rect.x = event.pos[0] - offset_x
                slide.rect.y = event.pos[1] - offset_y

    # Get keys pressed
    keys = pygame.key.get_pressed()

    # Update game state
    player.update(keys)

    # Check for collisions between player and platforms
    if pygame.sprite.spritecollide(player, platforms, False):
        platform = min([p for p in platforms if pygame.sprite.collide_rect(player, p)], key=lambda p: p.rect.y)
        if player.velocity[1] > 0:
            if player.velocity[1] > 0.5:
                logging.debug("Hit ground.")
            player.is_jumping = False
            player.jump_count = 0
            player.velocity[1] = 0
            # Adjust player's position to be on top of the platform
            player.rect.y = platform.rect.y - player.rect.height

        # Check if the player's head hit the platform
        if player.velocity[1] < 0:
            player.velocity[1] = 0  # Stop the upward motion
            player.bump_head()  # Custom method to handle the head bump
            # Make sure the player doesn't end up on top of the platform in the next loop
            player.rect.y = max(player.rect.y, platform.rect.y - player.rect.height) + 5

    # Draw the screen
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)

    # Display mouse coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_text = mouse_font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, (0, 0, 0))
    screen.blit(mouse_text, (mouse_x, mouse_y))

    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

# Quit the game
pygame.quit()