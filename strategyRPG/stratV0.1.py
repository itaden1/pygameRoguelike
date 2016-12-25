import pygame, sys, os
import random, math
from pygame.locals import *

pygame.init()

TILE_SIZE = 64

SCREEN_W = TILE_SIZE * 14
SCREEN_H = TILE_SIZE * 12


MAP_SIZE = 100
MAP = pygame.Surface((MAP_SIZE*TILE_SIZE,MAP_SIZE*TILE_SIZE))
MAP_POS_X = 0
MAP_POS_Y = 0


SCREEN = pygame.display.set_mode((SCREEN_W,SCREEN_H))#,FULLSCREEN)

class Tile():
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.wall = blocked

def make_map():
    global my_map
    my_map = [[Tile(False)
                for y in range(SCREEN_H/TILE_SIZE)]
                    for x in range(SCREEN_W/TILE_SIZE)]
    

    
def draw_map():
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            pygame.draw.rect(MAP, (200,200,200), (x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE),1)
    SCREEN.blit(MAP, (MAP_POS_X,MAP_POS_Y))
    
    
make_map()
draw_map()

left = False
right = False

clock = pygame.time.Clock()
while 1:
    clock.tick(60)
    
   
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                left = True
                
            if event.key == K_RIGHT:
                right = True

        if event.type == KEYUP:
            if event.key == K_LEFT:
                left = False
            if event.key == K_RIGHT:
                right = False
                
        if left:
            if MAP_POS_X != 0:
                MAP_POS_X +=3
        if right:
            if MAP_POS_X+SCREEN_W != MAP_SIZE:
                MAP_POS_X -=3
                
    draw_map()
    pygame.display.flip()
    
    