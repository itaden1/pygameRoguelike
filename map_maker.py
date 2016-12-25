#-------------------------------------------------------------------------------
# Name:        map maker
# Purpose:
#
# Author:      Ethan
#
# Created:     02/02/2012
# Copyright:   (c) Ethan 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys, os, random
import pygame
from pygame.locals import *

pygame.init()

tile_size = 10
map_size_x = 70
map_size_y = 70

play_area = 40

tree_col = ((30,100,30))
mnt_col = ((50,50,50))
grass_col = ((20,200,20))
vill_col = ((20,20,200))

screen = pygame.display.set_mode((700,700))
current_map = pygame.Surface((700,700))

world_map = pygame.Surface((500,500))
village_map = pygame.Surface((200,200))
forest_map = pygame.Surface((500,500))


class Tile():
    def __init__(self, blocked, is_exit = None, block_sight = None):
        self.blocked = blocked

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.forest = False
        self.door = False
        self.village = False
        self.shadow = True
        self.explored = False
        self.stairs_up = False
        self.stairs_down = False
        self.wall = blocked

class Rect():
    def __init__(self,w,h,x,y):
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h
    def center(self):
        center_x = (self.x1 + self.x2)/2
        center_y = (self.y1 + self.y2)/2

        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and\
                self.y1 <= other.y2 and self.y2 >= other.y1)


def make_dungeon():
    global my_map
    max_features = random.randint(50,400)
    max_halls = 7
    halls = 0
    max_exits = 1
    exits = 0

    features = []
    doors = []
    stairs_up = []
    stairs_down = []
    current_rooms = 0

    my_map = [[Tile(True)
                for y in range(tiles_y)]
                    for x in range(tiles_x)]
    #create first room
    w = random.randint(4,8)
    h = random.randint(4,8)
    x = random.randint(5,38)
    y = random.randint(5,38)
    feature = Rect(w,h,x,y)
    c_x,c_y = feature.center()
    stair_up = Rect(1,1,c_x,c_y)
    stairs_up.append(stair_up)
    features.append(feature)


    for i in range(max_features):
        #make a door on the previouse feeature
        prev_feature = random.choice(features)
        w = prev_feature.x2-prev_feature.x1
        h = prev_feature.y2-prev_feature.y1
        x = prev_feature.x1
        y = prev_feature.y1
        r_wall = random.randint(1,4)
        if r_wall == 1 and w >= 2:
            dx = random.randint((x+1),(x+w-2))
            door = Rect(1,1,dx,y-1)
        elif r_wall == 2 and h >=2:
            dy = random.randint((y+1),(y+h-2))
            door = Rect(1,1,x+w,dy)
        elif r_wall == 3 and w >= 2:
            dx = random.randint((x+1),(x+w-2))
            door = Rect(1,1,dx,y+h)
        elif r_wall == 4 and h >=2:
            dy = random.randint((y+1),(y+h-2))
            door = Rect(1,1,x-1,dy)




        chosen_feature = random.randint(1,2)
        if halls < max_halls and chosen_feature == 2:# corridor
            x = door.x1
            y = door.y1
            if r_wall == 1:
                if random.randint(1,2)==1:
                    w = 1
                    h = random.randint(5,10)
                    x = x
                    y = y-h
                else:
                    w = random.randint(5,10)
                    h = 1
                    x = random.randint(x-w+1,x-1)
                    y = y-1


            elif r_wall == 2:
                if random.randint(1,2)==1:
                    w = 1
                    h = random.randint(5,10)
                    x = x+1
                    y = random.randint(y-h+1,y-1)
                else:
                    w = random.randint(5,10)
                    h = 1
                    x = x+1
                    y = y


            elif r_wall == 3:
                if random.randint(1,2)==1:
                    w = 1
                    h = random.randint(5,10)
                    x = x
                    y = y+1
                else:
                    w = random.randint(5,10)
                    h = 1
                    x = random.randint(x-w+1,x-1)
                    y = y+1

            elif r_wall == 4:
                if random.randint(1,2)==1:
                    w = 1
                    h = random.randint(5,10)
                    x = x-1
                    y = random.randint(y-h+1,y-1)
                else:
                    w = random.randint(5,10)
                    h = 1
                    x = x-w
                    y = y



            scan_area = Rect(w,h,x,y)

            failed = False
            for other_feature in features:
                if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= map_size_x - 3 or \
                scan_area.y1 <= 3 or scan_area.y2 >= map_size_y - 3:
                    failed = True
                    break
            if not failed:
                hall = Rect(w,h,x,y)
                features.append(hall)
                doors.append(door)
                halls+=1

                w = hall.x2-hall.x1
                h = hall.y2-hall.y1
                x = hall.x1
                y = hall.y1

                if r_wall == 1:
                    door = Rect(1,1,x,y-1)
                elif r_wall == 2:
                    door == Rect(1,1,x+1,y)
                elif r_wall == 3:
                    door = Rect(1,1,x,y+1)
                else:
                    door = Rect(1,1,x-1,y)

                x = door.x1
                y = door.y1

                if r_wall == 1:

                    w = random.randint(3,6)
                    h = random.randint(3,6)
                    x = random.randint(door.x1-(w/2),door.x1-1)
                    y = (y-h)

                elif r_wall == 2:

                    w = random.randint(3,6)
                    h = random.randint(3,6)
                    x = (x+1)
                    y = random.randint(door.y1-(h/2),door.y1-1)

                elif r_wall == 3:

                    w = random.randint(3,6)
                    h = random.randint(3,6)
                    x = random.randint(door.x1-(w/2),door.x1-1)
                    y = y+1

                elif r_wall == 4:

                    w = random.randint(3,6)
                    h = random.randint(3,6)
                    x = (x-w)
                    y = random.randint(door.y1-(h/2),door.y1-1)

                scan_area = Rect(w,h,x,y)

                failed = False
                for other_feature in features:
                    if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= map_size_x - 3 or \
                    scan_area.y1 <= 3 or scan_area.y2 >= map_size_y - 3:
                        failed = True
                        break

                if not failed:
                    room = Rect(w,h,x,y)
                    doors.append(door)
                    features.append(room)


        else:#if chosen_feature == 1:#room

            x = door.x1
            y = door.y1

            if r_wall == 1:

                w = random.randint(3,6)
                h = random.randint(3,6)
                x = random.randint(door.x1-(w/2),door.x1-1)
                y = (y-h)

            elif r_wall == 2:

                w = random.randint(3,6)
                h = random.randint(3,6)
                x = (x+1)
                y = random.randint(door.y1-(h/2),door.y1-1)

            elif r_wall == 3:

                w = random.randint(3,6)
                h = random.randint(3,6)
                x = random.randint(door.x1-(w/2),door.x1-1)
                y = y+1

            elif r_wall == 4:

                w = random.randint(3,6)
                h = random.randint(3,6)
                x = (x-w)
                y = random.randint(door.y1-(h/2),door.y1-1)

            scan_area = Rect(w,h,x,y)

            failed = False
            for other_feature in features:
                if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= map_size_x - 3 or \
                scan_area.y1 <= 3 or scan_area.y2 >= map_size_y - 3:
                    failed = True
                    break

            if not failed:
                new_room = Rect(w,h,x,y)
                c_x,c_y = new_room.center()
                if random.randint(1,10)==10:
                    if exits < max_exits:
                        stair_down = Rect(1,1,c_x,c_y)
                        stairs_down.append(stair_down)
                        exits+=1
                doors.append(door)
                features.append(new_room)







    for i in features:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].blocked = False
                my_map[x][y].wall = False


    for i in doors:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].door = True
                my_map[x][y].wall = False
                my_map[x][y].blocked = True#False

    for i in stairs_up:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].stairs_up = True
                my_map[x][y].wall = False
                my_map[x][y].blocked = False

    for i in stairs_down:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].stairs_down = True
                my_map[x][y].wall = False
                my_map[x][y].blocked = False




##    dungeon_map = my_map
    draw_map(my_map,"dungeon")





def create_h_tunnel(x1,x2,y): #(origin, destination, y position)
    global my_map
    for x in range(min(x1,x2), max(x1,x2) +1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def create_v_tunnel(y1,y2,x): #(origin, destination, x position)
    global my_map
    for y in range(min(y1,y2), max(y1,y2) +1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def make_forest_map():
    global my_map
    max_clearings = 39

    clearings = []
    num_clearings = 0
    my_map = [[Tile(True)
                for y in range(map_size_y)]
                    for x in range(map_size_x)]
    for i in range(max_clearings):
        rect_list = []
        w = random.randint(2,3)
        h = random.randint(2,3)
        x = random.randint(5,38)
        y = random.randint(5,38)
        base_rect = Rect(w,h,x,y)

        failed = False
        for other_clearing in clearings:
            if base_rect.intersect(other_clearing):
                failed = True
                break

        if not failed:
            clearings.append(base_rect)
            num_clearings+=1
            rect_list.append(base_rect)
            for i in range(3):
                w2 = random.randint(3,5)
                h2 = random.randint(3,5)
                x2 = random.randint(x-2,x+2)
                y2 = random.randint(y-2,y+2)

                rect = Rect(w2,h2,x2,y2)
                rect_list.append(rect)
            for i in rect_list:
                for y in range(i.y1,i.y2):
                    for x in range(i.x1,i.x2):
                        my_map[x][y].blocked = False


        (new_x,new_y) = base_rect.center()
        if clearings >= 1:


            (prev_x, prev_y) = clearings[num_clearings-1].center()
            if random.randint(0,1) == 1:
                create_h_tunnel(prev_x, new_x, prev_y)
                create_v_tunnel(prev_y, new_y, prev_x)
            else:
                create_v_tunnel(prev_y, new_y, prev_x)
                create_h_tunnel(prev_x, new_x, new_y)



    forest_map = my_map
    draw_map(forest_map,"forest")



def make_valley(valley):
    global my_map
    for x in range(valley.x1+1,valley.x2):
        for y in range(valley.y1+1,valley.y2):
            my_map[x][y].blocked = False

def make_forest(forest):
    global my_map
    for x in range(forest.x1+1,forest.x2):
        for y in range(forest.y1+1,forest.y2):
            my_map[x][y].forest = True
            my_map[x][y].blocked = False

def make_world_map():
    global my_map
    max_villages = 6

    world_map_save = []


    my_map = [[Tile(True)
        for y in range (map_size_y)]
            for x in range (map_size_x)]

    villages = 0
    for v in range (280):
        w = random.randint(2,5)
        h = random.randint(2,5)
        x = random.randint(2,43)
        y = random.randint(2,43)

        valley = Rect(w,h,x,y)
        make_valley(valley)

        if villages <= max_villages:
            if my_map[x][y].blocked == False:
                my_map[x][y].village = True
                villages +=1

    for f in range (100):
        w = random.randint(2,4)
        h = random.randint(2,4)
        x = random.randint(2,38)
        y = random.randint(2,38)

        forest = Rect(w,h,x,y)
        make_forest(forest)

    world_map = my_map


    draw_map(world_map,"world")


def draw_map(loaded_map,category):


    if category == "world":

        for y in range(map_size_y):
            for x in range (map_size_x):
                mountain = loaded_map[x][y].blocked
                forest = loaded_map[x][y].forest
                village = loaded_map[x][y].village
                if mountain:
                    pygame.draw.rect(current_map,mnt_col,(x*tile_size,y*tile_size,tile_size,tile_size))
                else:
                    pygame.draw.rect(current_map,grass_col,(x*tile_size,y*tile_size,tile_size,tile_size))

                if forest:
                    pygame.draw.rect(current_map,tree_col,(x*tile_size,y*tile_size,tile_size,tile_size))
                if village:
                    pygame.draw.rect(current_map,vill_col,(x*tile_size,y*tile_size,tile_size,tile_size))

    if category == "forest":
        for y in range(map_size_y):
            for x in range (map_size_x):
                tree = loaded_map[x][y].blocked
                if tree:
                    pygame.draw.rect(current_map,tree_col,(x*tile_size,y*tile_size,tile_size,tile_size))
                else:
                    pygame.draw.rect(current_map,grass_col,(x*tile_size,y*tile_size,tile_size,tile_size))

    if category == "dungeon":
        for y in range(map_size_y):
            for x in range (map_size_x):
                wall = loaded_map[x][y].wall
                door = loaded_map[x][y].door
                stairs_down = loaded_map[x][y].stairs_down
                stairs_up = loaded_map[x][y].stairs_up

                if wall:
                    pygame.draw.rect(current_map,mnt_col,(x*tile_size,y*tile_size,tile_size,tile_size))
                elif door:
                    pygame.draw.rect(current_map,tree_col,(x*tile_size,y*tile_size,tile_size,tile_size))
                elif stairs_down:
                    pygame.draw.rect(current_map,(100,40,40),(x*tile_size,y*tile_size,tile_size,tile_size))
                elif stairs_up:
                    pygame.draw.rect(current_map,vill_col,(x*tile_size,y*tile_size,tile_size,tile_size))

                else:
                    pygame.draw.rect(current_map,grass_col,(x*tile_size,y*tile_size,tile_size,tile_size))



##make_forest_map()
##make_world_map()
make_dungeon()

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.blit(current_map,(0,0))
    pygame.display.flip()




