import pygame
import math
import PIL as pil
import numpy as np
import random
import sys

"""
This code is really old and needs to be rewritten for scalability and optimization.
"""

FLAGS = pygame.SCALED | pygame.RESIZABLE
screen = pygame.display.set_mode((640, 360), FLAGS, vsync=1)

# GLOBAL CONSTANTS #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

MAP = ("1111133333333333"
       "1000130000300033"
       "1000100000300003"
       "1011100000000333"
       "2000020000300003"
       "2020002033333303"
       "2020000000300003"
       "2222022330333333"
       "3000000300000004"
       "3000000300040004"
       "3000000300040004"
       "3303333344044044"
       "4000000400005005"
       "4004400000050005"
       "4004400400000005"
       "4444444455555555"
       )

MAP_SIZE = 16
TILE_SIZE = 64
MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)
FOV = math.pi / 3
HALF_FOV = FOV / 2
RAYS_CASTED = 128
ANGLE_STEP = FOV / RAYS_CASTED
PLAYER_SCALE = 20

# textures
RED_BRICK = pygame.image.load("W3D_red_bricks.png").convert()
BLUE_BRICK = pygame.image.load("W3D_blue_bricks.png").convert()
GRAY_BRICK = pygame.image.load("W3D_gray_bricks.png").convert()
CELL = pygame.image.load("W3D_blue_bricks_cell.png").convert()
WOOD = pygame.image.load("W3D_wood.png").convert()

SKY = pygame.image.load("Sky2.png").convert()
SKY = pygame.transform.scale(SKY, (640 * 4, 360))

# GLOBAL VARIABLES #
player_x = 2 * TILE_SIZE
player_y = 2 * TILE_SIZE
player_angle = math.pi

"""
Cast rays and render textures. 
This process is slow because the texture's scale on the y axis gets to be way too much when the player gets too close to the wall.
I remember cropping the texture to the screen height but that didn't work.
"""
def cast_rays():
    start_angle = player_angle - HALF_FOV

    for ray in range(RAYS_CASTED):
        for depth in range(MAX_DEPTH):
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth

            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)

            square = row * MAP_SIZE + col

            if MAP[square] != "0":
                depth *= math.cos(player_angle - start_angle)

                wall_height = (screen_height * TILE_SIZE) / (depth + 0.0001) * 1.6

                """
                if wall_height >= screen_height * 3.5:
                    wall_height = screen_height * 3.5
                """

                # get whether on x or y and where relative to wall.
                # tex_col_modifier is the x of the column of texture that renders for each ray.
                
                if int((target_x + 1) % 64) == 0 or int((target_x + 1) % 64) == 1:
                    tex_col_modifier = int(target_y % 64)
                elif int((target_y + 1) % 64) == 0 or int((target_y + 1) % 64) == 1:
                    tex_col_modifier = int(target_x % 64)
                else:
                    tex_col_modifier = int(target_x % 64)

                
                # different textures
                if MAP[square] == "1":
                    red_brick_rescaled = pygame.transform.scale(RED_BRICK, (int(scale * 64), int(wall_height)))
                    screen.blit(red_brick_rescaled, (0 + ray * scale, (screen_height / 2) - wall_height / 2), (tex_col_modifier * int(scale), 0, int(scale), int(wall_height)))
                elif MAP[square] == "2":
                    blue_brick_rescaled = pygame.transform.scale(BLUE_BRICK, (int(scale * 64), int(wall_height)))
                    screen.blit(blue_brick_rescaled, (0 + ray * scale, (screen_height / 2) - wall_height / 2), (tex_col_modifier * int(scale), 0, int(scale), int(wall_height)))
                elif MAP[square] == "3":
                    gray_brick_rescaled = pygame.transform.scale(GRAY_BRICK, (int(scale * 64), int(wall_height)))
                    screen.blit(gray_brick_rescaled, (0 + ray * scale, (screen_height / 2) - wall_height / 2), (tex_col_modifier * int(scale), 0, int(scale), int(wall_height)))
                elif MAP[square] == "4":
                    cell_rescaled = pygame.transform.scale(CELL, (int(scale * 64), int(wall_height)))
                    screen.blit(cell_rescaled, (0 + ray * scale, (screen_height / 2) - wall_height / 2), (tex_col_modifier * int(scale), 0, int(scale), int(wall_height)))
                elif MAP[square] == "5":
                    wood_rescaled = pygame.transform.scale(WOOD, (int(scale * 64), int(wall_height)))
                    screen.blit(wood_rescaled, (0 + ray * scale, (screen_height / 2) - wall_height / 2), (tex_col_modifier * int(scale), 0, int(scale), int(wall_height)))
                
                break
        start_angle += ANGLE_STEP

# Detect if there was a collision in a certain direction
def collision(direction):

    
    pygame.draw.circle(screen, GREEN, (int((player_x + PLAYER_SCALE) / 4), int(player_y / 4)), 1)
    pygame.draw.circle(screen, GREEN, (int((player_x - PLAYER_SCALE) / 4), int(player_y / 4)), 1)
    pygame.draw.circle(screen, GREEN, (int(player_x / 4), int((player_y - PLAYER_SCALE) / 4)), 1)
    pygame.draw.circle(screen, GREEN, (int(player_x / 4), int((player_y + PLAYER_SCALE) / 4)), 1)
    

    east = False
    west = False
    north = False
    south = False

    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            square = x + y * MAP_SIZE
            if MAP[square] != "0":
                tile = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                #pygame.draw.rect(screen, MAGENTA, tile)

                if not east:
                    east = tile.collidepoint(player_x + PLAYER_SCALE, player_y) # direction 0
                if not west:
                    west = tile.collidepoint(player_x - PLAYER_SCALE, player_y) # direction 1
                if not north:
                    north = tile.collidepoint(player_x, player_y - PLAYER_SCALE) # direction 2
                if not south:
                    south = tile.collidepoint(player_x, player_y + PLAYER_SCALE) # direction 3

    if direction == 0:
        return east
    elif direction == 1:
        return west
    elif direction == 2:
        return north
    elif direction == 3:
        return south
    else:
        raise Exception("Must be an integer between 0 and 3")

pygame.font.init()
FONT = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen_width, screen_height = screen.get_size()
    
    scale = screen_width / RAYS_CASTED

    # define player rect
    player_rect = pygame.Rect(player_x - PLAYER_SCALE / 2, player_y - PLAYER_SCALE / 2, PLAYER_SCALE, PLAYER_SCALE)

    # key inputs
    if player_angle <= -math.pi:
        player_angle = math.pi
    if player_angle >= math.pi * 3:
        player_angle = math.pi
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_angle -= 0.1

    if keys[pygame.K_d]:
        player_angle += 0.1

    if keys[pygame.K_w]:
        
        if player_x - math.sin(player_angle) * 4 > player_x:
            if not collision(0):
                player_x -= math.sin(player_angle) * 4
        if player_x - math.sin(player_angle) * 4 < player_x:
            if not collision(1):
                player_x -= math.sin(player_angle) * 4
        
        if player_y + math.cos(player_angle) * 4 > player_y:
            if not collision(3):
                player_y += math.cos(player_angle) * 4
        if player_y + math.cos(player_angle) * 4 < player_y:
            if not collision(2):
                player_y += math.cos(player_angle) * 4
        
    if keys[pygame.K_s]:
        if player_x + math.sin(player_angle) * 4 > player_x:
            if not collision(0):
                player_x += math.sin(player_angle) * 4
        if player_x + math.sin(player_angle) * 4 < player_x:
            if not collision(1):
                player_x += math.sin(player_angle) * 4
        
        if player_y - math.cos(player_angle) * 4 > player_y:
            if not collision(3):
                player_y -= math.cos(player_angle) * 4
        if player_y - math.cos(player_angle) * 4 < player_y:
            if not collision(2):
                player_y -= math.cos(player_angle) * 4

    # rendering everything
    screen.fill(BLACK)
    
    screen.blit(SKY, (0 - player_angle * 640, 0))
    screen.blit(SKY, (0 - player_angle * 640 + 640 * 4, 0))
    screen.blit(SKY, (0 - player_angle * 640 + 640 * 8, 0))
    screen.blit(SKY, (0 - player_angle * 640 - 640 * 4, 0))

    ground = pygame.Surface((640, 180))
    ground.set_alpha(128)
    ground.fill((32, 64, 0))
    screen.blit(ground, (0, 180))

    cast_rays()
    
    clock.tick(60)
    # get and display fps:
    
    fps = clock.get_fps()
    debug_text = FONT.render("fps: " + str(fps) + " | " + "Player Angle: " + str(player_angle), False, WHITE, BLACK)
    debug_rect = debug_text.get_rect()
    screen.blit(debug_text, debug_rect)
    collision(0)
    
    pygame.display.flip()

pygame.quit()
sys.exit()
