import player
import pygame
import platform_obj
import logging
from pygame.locals import *
import pygame.mixer
import pygame.font
import os
import slide
import math
import Box2D
from Box2D.b2 import (world, edgeShape, polygonShape, dynamicBody, staticBody)
import os

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


# Create the Box2D world
world = world(gravity=(0, 9.81))

# Create the Slide object
slide_top_left = [500, 500]
slide_thickness = 30
slide_length = 400
slide_angle = -45

slide = slide.Slide(screen, slide_top_left, slide_thickness, slide_length, slide_angle)
slide.create_body(world)
slide.update()


# Create the player
player = player.Player(screen, screen_width, screen_height)
player.create_body(world)

# Create platforms
platform1 = platform_obj.Platform(0, screen_height - 60, screen_width, 60)
platform1.create_body(world)
platform2 = platform_obj.Platform(200, screen_height - 200, 200, 30)
platform2.create_body(world)
platform3 = platform_obj.Platform(500, screen_height - 300, 150, 30)
platform3.create_body(world)

# Create a sprite group for all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(slide, player, platform1, platform2, platform3)

# Create a sprite group for platforms
platforms = pygame.sprite.Group()
platforms.add(platform1, platform2, platform3)

# Create a sprite group for slides
slides = pygame.sprite.Group()
slides.add(slide)

dragging = False  # Flag to indicate if the slide is being dragged
offset_x = 0  # Offset between the mouse cursor and the slide's top-left corner
offset_y = 0


# Game loop
running = True
clock = pygame.time.Clock()
intersection_points = []

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button pressed
                if slide.rect.collidepoint(event.pos):  # Check if the mouse is over the slide
                    dragging = True
                    offset_x = event.pos[0] - slide.top_left[0]
                    offset_y = event.pos[1] - slide.top_left[1]
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button released
                dragging = False

        elif event.type == MOUSEMOTION:
            if dragging:
                slide.top_left[0] = event.pos[0] - offset_x
                slide.top_left[1] = event.pos[1] - offset_y
                slide.update()

    # Step the Box2D world
    world.Step(1 / 60, 6, 2)

    # Get keys pressed
    keys = pygame.key.get_pressed()

    # Update game state
    player.update(keys)

    # Check for collisions between player and platforms
    for contact in world.contacts:
        print("Found a contact!")
        if contact.touching:
            print("It is touching!")
            fixtureA = contact.fixtureA
            fixtureB = contact.fixtureB
            print(fixtureA.userData, "<->", fixtureB.userData)
            if (fixtureA.userData == 'player' and fixtureB.userData == 'platform') or \
                    (fixtureA.userData == 'platform' and fixtureB.userData == 'player'):
                platform = fixtureA.body.userData if fixtureA.userData == 'platform' else fixtureB.body.userData
                player = fixtureA.body.userData if fixtureA.userData == 'player' else fixtureB.body.userData

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

            if (fixtureA.userData == 'player' and fixtureB.userData == 'slide') or \
                    (fixtureA.userData == 'slide' and fixtureB.userData == 'player'):
                slide = fixtureA.body.userData if fixtureA.userData == 'slide' else fixtureB.body.userData
                player = fixtureA.body.userData if fixtureA.userData == 'player' else fixtureB.body.userData

                logging.debug("Found colliding slide")
                player.is_sliding = True
                player.slide = s

    # Draw the screen
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)

    for s in slides:
        # Draw get_slide_y line
        slide_y_points = []
        for x in range(screen_width):
            y = s.get_top_slide_y(x)
            slide_y_points.append((x, y))
        pygame.draw.lines(screen, (0, 0, 255), False, slide_y_points, 2)

    # Display mouse coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_text = mouse_font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, (0, 0, 0))
    screen.blit(mouse_text, (mouse_x, mouse_y))

    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

# Quit the game
pygame.quit()