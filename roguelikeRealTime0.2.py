import pygame, sys, os
import random
from pygame.locals import *

pygame.init()

tile_width = 100
tile_height = 100

tiles_x = 70
tiles_y = 70

display_tiles_x = 10
display_tiles_y = 7

screen_width = tile_width * display_tiles_x
screen_height = tile_height * display_tiles_y
map_width = tiles_x * tile_width
map_height = tiles_y * tile_height

room_max_size = 10
room_min_size = 5
max_rooms = 70

screen = pygame.display.set_mode((screen_width,screen_height))
level_map = pygame.Surface((map_width,map_height))

def load_image(name, colorkey=None):
    
    fullname = os.path.join('C:/Users/Ethan/Desktop/PythonGames/pygame/MyRoguelike', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'cannot load image', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is -1:
        colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
    rect = image.get_rect()
    return image, rect


class Tile():
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = wall_img
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height

        

class Floor(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = floor_img
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height


class Rect():#helper class for map generation
    def __init__(self,x,y,w,h):
        self.x1 = x
        self.y1 = y 
        self.x2 = x + w 
        self.y2 = y + h 


    def center(self):
        center_x = (self.x1 + self.x2)/2
        center_y = (self.y1 + self.y2)/2
        
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and\
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Player(pygame.sprite.Sprite):

    change_x = 0
    change_y = 0

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('player.png',-1)
        
        self.rect.x = x
        self.rect.y = y
        
        self.map_x =  x
        self.map_y = y

    def update(self):
        
        old_x = self.map_x
        new_x = old_x + self.change_x
        self.map_x = new_x

        old_y = self.map_y
        new_y = old_y + self.change_y
        self.map_y = new_y
        
        
    def move(self,x,y):
        
        self.change_x += x
        self.change_y += y

def handle_keys():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_a:
                player.move(-3,0)
            elif event.key == K_d:               
                player.move(3,0)
            elif event.key == K_w:
                player.move(0,-3)
            elif event.key == K_s:
                player.move(0,3)

        elif event.type == KEYUP:
            if event.key == K_a:
                player.move(3,0)
            elif event.key == K_d:
                player.move(-3,0)
            elif event.key == K_w:
                player.move(0,3)
            elif event.key == K_s:
                player.move(0,-3)

def create_room(room):
    global my_map
    for x in range(room.x1+1, room.x2):
        for y in range(room.y1+1,room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False

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

def make_map():
    global my_map
    wall_group = pygame.sprite.Group()
    floor_group = pygame.sprite.Group()

    #place holder loading screen
    pygame.draw.rect(screen,(100,100,100),(screen_width/2,screen_height/2,tile_width,tile_height))
    pygame.display.flip()
    
    my_map = [[ Tile(True)
        for y in range(tiles_y) ]
              for x in range(tiles_x) ]

    rooms = []
    num_rooms = 0
    
    for r in range(max_rooms):
        w = random.randint(room_min_size, room_max_size)
        h = random.randint(room_min_size, room_max_size)
        x = random.randint(0, tiles_x - room_max_size - 1)
        y = random.randint(0, tiles_y - room_max_size - 1)

        new_room = Rect(x,y,w,h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:

            create_room(new_room)

            (new_x, new_y) = new_room.center()
            
            
            if num_rooms == 0:
                player.map_x = new_x * tile_width
                player.map_y = new_y * tile_width
                
            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()
               
                
                if random.randint(0,1) == 1:
                     create_h_tunnel(prev_x, new_x, prev_y)
                     create_v_tunnel(prev_y, new_y, prev_x)
                else:
                     create_v_tunnel(prev_y, new_y, prev_x)
                     create_h_tunnel(prev_x, new_x, new_y)

            rooms.append(new_room)
            num_rooms += 1
            
    for y in range(tiles_y):
        for x in range(tiles_x):
            wall = my_map[x][y].block_sight
            if wall:
                wall_tile = Wall(x,y)
                wall_group.add(wall_tile)
                wall_sprites.add(wall_tile)               
            else:
                floor_tile = Floor(x,y)
                floor_group.add(floor_tile)
                

    draw_map(wall_group,floor_group)
    
def draw_map(w,f):
    w.draw(level_map)
    f.draw(level_map)

                
def render_all():
    

    screen.blit(level_map, (player.rect.x-player.map_x ,player.rect.y-player.map_y))

    player_sprite.draw(screen)
    
        
#initialisation

player = Player((display_tiles_x/2)*tile_width,(display_tiles_y/2)*tile_height)

wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')

wall_sprites = pygame.sprite.Group()
       
char_objects = [player]
player_sprite = pygame.sprite.RenderPlain((player))

make_map()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)
    player.update()
    render_all()
    
    pygame.display.flip()

    keypress = handle_keys()
    if keypress:
        break
    
