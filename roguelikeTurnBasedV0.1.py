import pygame, sys, os
import random, math
from pygame.locals import *

pygame.init()

tile_width = 100
tile_height = 100

tiles_x = 70
tiles_y = 70

display_tiles_x = 10
display_tiles_y = 7
play_area_x = 7
play_area_y = 7


screen_width = tile_width * display_tiles_x
screen_height = tile_height * display_tiles_y
map_width = tiles_x * tile_width
map_height = tiles_y * tile_height

room_max_size = 8
room_min_size = 5
max_rooms = 50
max_monsters = 15
max_items = 2

screen = pygame.display.set_mode((screen_width,screen_height))
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))

gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width - 20,2*tile_height - 20))
inventory = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width - 20,2*tile_height - 20))


def load_image(name, colorkey=None):

    fullname = os.path.join( name)
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


class Treasure(pygame.sprite.Sprite):

    def __init__(self,x,y,item_type):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('item.png',-1)
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height

        self.contains = item_type


class Player(pygame.sprite.Sprite):


    def __init__(self,x,y,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('player.png',-1)
        self.rect.x = x
        self.rect.y = y
        self.map_x = x
        self.map_y = y
        self.blocks = blocks

        ##player stats
        self.attk_pwr = 12
        self.defence = 6
        self.hit = 10
        self.dodge = 4
        self.max_hp = 1000
        self.hp = 1000
        self.magic_attk = 10
        self.magic_def = 7
        self.magic_hit = 8
        self.magic_dodge = 5
        self.stealth = 1

        ##player spells
        self.heal_spell = 5
        self.fire_spell = 5
        self.ice_spell = 5

    def move_or_attack(self,x,y):

        target = None
        dest_x = self.map_x + x
        dest_y = self.map_y + y

        for monster in monster_group:
            if dest_x == monster.rect.x and dest_y == monster.rect.y:
                target = monster

        if target is not None:
            self.attack(target)

        else:
            self.move(x,y)


    def cast_spell(self,spell):

        aoe_targets = [(self.map_x + tile_width,self.map_y),(self.map_x - tile_width,self.map_y),\
            (self.map_x,self.map_y + tile_height),(self.map_x,self.map_y-tile_height)]

        if spell == 'heal_spell' and self.heal_spell != 0:
            random_roll = random.randint(1,20)
            heal = random_roll + self.magic_attk
            self.hp += heal
            text = 'you gain %s from heal spell' % heal
            self.heal_spell -= 1
            updateGUI(text,(100,100,10))

        elif spell == 'fire_spell' and self.fire_spell != 0:

            for target in aoe_targets:
                for monster in monster_group:

                ##tmp_map.blit(fire_img,(target))

                    if target == (monster.rect.x,monster.rect.y):
                        random_roll = random.randint(1,20)
                        dmg = random_roll + self.magic_attk - monster.magic_def
                        monster.hp -= dmg
                        text = "you hit %s with %s fire damage" % (monster.name,dmg)
                        if monster.hp < 0:
                            monster.hp = 0
                            text = "The %s burns to death" % monster.name
                            col = (100,100,10)
                            monster.death()
                            updateGUI(text,col)

                        updateGUI(text,(100,100,10))

            self.fire_spell -= 1

        elif spell == 'ice_spell' and self.ice_spell != 0:

            for target in aoe_targets:
                for monster in monster_group:
                    if target == (monster.rect.x,monster.rect.y):
                        random_roll = random.randint(1,5)
                        effect = random_roll + self.magic_attk - monster.magic_def
                        if effect <= 0:
                            text = "%s resisted the spell" % monster.name
                        else:
                            monster.frozen = True
                            monster.frozen_timer = effect
                            text = "you freeze the %s in place" % monster.name
                        updateGUI(text,(100,100,10))

            self.ice_spell -= 1


        else:
            text = 'you fail to cast spell'
            updateGUI(text,(100,100,10))


    def move(self,x,y):

        if not my_map[self.map_x/tile_width + x/tile_width ][self.map_y/tile_height + y/tile_height ].blocked:

            for i in range(10):
                self.map_x += x/10
                render_all()

            for i in range(10):
                self.map_y += y/10
                render_all()

    def attack(self,target):

        hit_roll = random.randint(1,20)
        hit_chance = hit_roll + self.hit
        miss_roll = random.randint(1,20)
        miss_chance = miss_roll + target.dodge

        if hit_chance >= miss_chance:
            attack_roll = random.randint(1,20)
            attack = attack_roll + self.attk_pwr
            mit_roll = random.randint(1,20)
            mitigate = mit_roll + target.defence

            if attack_roll == 20:
                dmg = attack + 5
                text = "You perform a critical attack"
                col = (10,100,10)
                updateGUI(text,col)
            else:
                dmg = attack - mitigate
            if dmg <= 0:
                dmg = 1
            target.hp -= dmg
            if target.hp < 0:
                target.hp = 0
                text = "The %s dies to your blow" % target.name
                col = (10,100,10)
                target.death()

            else:

                text = "you hit the %s for %s damage" % (target.name,dmg)
                col = (10,100,10)
        else:

            text = "the %s dodges your attack" % target.name
            col = (100,10,10)

        updateGUI(text,col)


    def death(self):
        tmp_map.blit(floor_img, (self.map_x,self.map_y))
        self.kill()
        render_all()


class Monster(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,defence,hit,dodge,hp,m_def,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img, -1)
        self.name = name
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height
        self.blocks = blocks

        self.attk_pwr = attk
        self.defence = defence
        self.hit = hit
        self.dodge = dodge
        self.hp = hp
        self.magic_def = m_def

        self.frozen = False
        self.frozen_timer = 0

    def move(self,x,y):

        if not is_blocked(self.rect.x/tile_width + x/tile_width ,self.rect.y/tile_height + y/tile_height ):
            old_pos_x = self.rect.x
            old_pos_y = self.rect.y
            new_pos_x = self.rect.x + x
            new_pos_y = self.rect.y + y

            for i in range(10):
                tmp_map.blit(floor_img,(old_pos_x,old_pos_y))
                tmp_map.blit(floor_img,(new_pos_x,new_pos_y))
                self.rect.x += x/10
                render_all()

            for i in range(10):
                tmp_map.blit(floor_img,(old_pos_x,old_pos_y))
                tmp_map.blit(floor_img,(new_pos_x,new_pos_y))
                self.rect.y += y/10
                render_all()



    def update(self):

        dist_to_player_x = abs(self.rect.x - player.map_x)
        dist_to_player_y = abs(self.rect.y - player.map_y)

        if not self.frozen:
            if (dist_to_player_x == tile_width and self.rect.y == player.map_y)or\
               (dist_to_player_y == tile_height and self.rect.x == player.map_x):
                self.attack()


            if dist_to_player_x <= ((play_area_x*tile_width)/2) and \
               dist_to_player_y <= ((play_area_y*tile_height)/2):

                new_dist_x = abs(self.rect.x + tile_width - player.map_x)
                new_dist_y = abs(self.rect.y + tile_height - player.map_y)

                if new_dist_x < dist_to_player_x and dist_to_player_x != 0 :
                    self.move(tile_width,0)

                elif new_dist_x > dist_to_player_x and dist_to_player_x != 0 :
                    self.move(-tile_width,0)

                if new_dist_y < dist_to_player_y and dist_to_player_y != 0 :
                    self.move(0,tile_height)

                elif new_dist_y > dist_to_player_y and dist_to_player_y != 0 :
                    self.move(0,-tile_height)
        else:
            self.frozen_timer -= 1
            if self.frozen_timer == 0:
                self.frozen = False

    def attack(self):

        hit_roll = random.randint(1,20)
        hit_chance = hit_roll + self.hit
        miss_roll = random.randint(1,20)
        miss_chance = miss_roll + player.dodge

        if hit_chance >= miss_chance:

            attack_roll = random.randint(1,20)
            attack = attack_roll + self.attk_pwr
            mit_roll = random.randint(1,20)
            mitigate = mit_roll + player.defence

            dmg = attack - mitigate
            if dmg <= 0:
                dmg = 1
            player.hp -= dmg
            if player.hp < 0:
                player.hp = 0
                player.death()

                text = "YOU HAVE DIED!"
                col = (150,10,10)

            else:

                text = "The %s hits you for %s damage" % (self.name,dmg)
                col = (100,10,10)

        else:

            text = "You dodge the %s's attack" %self.name
            col = (10,100,10)

        updateGUI(text,col)

    def death(self):

        tmp_map.blit(floor_img, (self.rect.x,self.rect.y))
        monster_group.remove(self)
        self.kill()
        render_all()

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
                player.move_or_attack(-tile_width,0)
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_d:
                player.move_or_attack(tile_width,0)
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_w:
                player.move_or_attack(0,-tile_width)
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_s:
                player.move_or_attack(0,tile_width)
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_f:
                pickup_object()
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_1:
                player.cast_spell('heal_spell')
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_2:
                player.cast_spell('fire_spell')
                monster_group.update()
                pygame.event.clear()
            elif event.key == K_3:
                player.cast_spell('ice_spell')
                monster_group.update()
                pygame.event.clear()

def pickup_object():

    for item in treasure_group:
        if player.map_x == item.rect.x and player.map_y == item.rect.y:
            player_inventory.append(item)
            text = "you picked up a %s" % item.contains
            col = (10,10,100)
            updateGUI(text,col)
            tmp_map.blit (floor_img,(item.rect.x,item.rect.y))
            treasure_group.remove(item)
            item.kill()
            render_all()

            if item.contains == 'health scroll':
                player.heal_spell += 1
            elif item.contains == 'fire scroll':
                player.fire_spell += 1
            elif item.contains == 'ice scroll':
                player.ice_spell += 1




def is_blocked(x,y):
    if my_map[x][y].blocked:
        return True
    if player.blocks and x == player.map_x/tile_width and y == player.map_y/tile_height :
        return True
    for monster in monster_group:
        if monster.blocks and monster.rect.x/tile_width == x and monster.rect.y/tile_height == y:
            return True

    return False

def place_objects(room):

    amount_monsters = random.randint(0,max_monsters)
    amount_items = random.randint(0,max_items)

    for i in range(amount_items):
        random_roll = random.randint(1,100)
        if random_roll <= 40:
            item_type = 'health scroll'

        elif random_roll > 40 and random_roll <= 70:
            item_type = 'fire scroll'

        else:
            item_type = 'ice scroll'



        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_blocked(x,y):
            treasure = Treasure(x,y,item_type)
            treasure_group.add(treasure)

    for i in range(amount_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 50:
            name = 'goblin'
            img = 'goblin.png'
            attack = 10
            defence = 1
            hit = 10
            dodge = 7
            hp = 30
            m_def = 7
        elif random_roll > 50 and random_roll <= 85:
            name = 'orc'
            img = 'orc.png'
            attack = 10
            defence = 8
            hit = 8
            dodge = 2
            hp = 40
            m_def = 5
        else:
            name = 'troll'
            img = 'troll.png'
            attack = 15
            defence = 10
            hit = 3
            dodge = 1
            hp = 60
            m_def = 12
        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_blocked(x,y):
            monster = Monster(x,y,name,img,attack,defence,hit,dodge,hp,m_def)
            monster_group.add(monster)

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
            if num_rooms != 0:
                place_objects(new_room)


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

            else:
                floor_tile = Floor(x,y)
                floor_group.add(floor_tile)


    draw_map(wall_group,floor_group)

def draw_map(w,f):
    w.draw(level_map)
    f.draw(level_map)

def updateGUI(text,clr):

    #player info screen
    text1_1 = "HP    %s / %s " % (player.hp,player.max_hp)
    text1_2 = "DEF       %s               M.DEF     %s" % (player.defence,player.magic_def)
    text1_3 = "ATT       %s             M.ATT     %s" % (player.attk_pwr,player.magic_attk)
    text1_4 = "AVO       %s               M.AVO     %s" % (player.dodge,player.magic_dodge)
    text1_5 = "HIT       %s              M.HIT     %s" % (player.hit,player.magic_hit)
    text1_6 = "STEALTH      %s" % player.stealth

    txt11 = font1.render(text1_1,1,(10,10,10))
    txt12 = font1.render(text1_2,1,(10,10,10))
    txt13 = font1.render(text1_3,1,(10,10,10))
    txt14 = font1.render(text1_4,1,(10,10,10))
    txt15 = font1.render(text1_5,1,(10,10,10))
    txt16 = font1.render(text1_6,1,(10,10,10))
    txt11pos = txt11.get_rect()
    txt12pos = txt12.get_rect()
    txt13pos = txt13.get_rect()
    txt14pos = txt14.get_rect()
    txt15pos = txt15.get_rect()
    txt16pos = txt16.get_rect()

    txt_x, txt_y = stats_gui.get_rect().topleft

    txt_x += 40
    txt11_y = txt_y + 10
    txt11pos.topleft = (txt_x,txt11_y)

    txt12_y = txt_y + 40
    txt12pos.topleft = (txt_x,txt12_y)

    txt13_y = txt_y + 70
    txt13pos.topleft = (txt_x,txt13_y)

    txt14_y = txt_y + 100
    txt14pos.topleft = (txt_x,txt14_y)

    txt15_y = txt_y + 130
    txt15pos.topleft = (txt_x,txt15_y)

    txt16_y = txt_y + 160
    txt16pos.topleft = (txt_x,txt16_y)

    stats_gui.fill((150,150,150))
    stats_gui.blit(txt11,txt11pos)
    stats_gui.blit(txt12,txt12pos)
    stats_gui.blit(txt13,txt13pos)
    stats_gui.blit(txt14,txt14pos)
    stats_gui.blit(txt15,txt15pos)
    stats_gui.blit(txt16,txt16pos)


    #combat info screen
    text = font1.render(text,1,(clr))
    text_pos = text.get_rect()
    text_list.insert(0,text)
    length = len(text_list)
    if length == 10:
        text_list.pop(9)

    coordx,coordy = combat.get_rect().bottomleft
    coordx += 10
    coord1y = coordy - 20
    coord2y = coordy - 40
    coord3y = coordy - 60
    coord4y = coordy - 80
    coord5y = coordy - 100
    coord6y = coordy - 120
    coord7y = coordy - 140
    coord8y = coordy - 160
    coord9y = coordy - 180

    combat.fill((150,150,150))
    combat.blit(text_list[0],(coordx,coord1y))
    if length >= 2:
        combat.blit(text_list[1],(coordx,coord2y))
        if length >= 3:
            combat.blit(text_list[2],(coordx,coord3y))
            if length >= 4:
                combat.blit(text_list[3],(coordx,coord4y))
                if length >= 5:
                    combat.blit(text_list[4],(coordx,coord5y))
                    if length >= 6:
                        combat.blit(text_list[5],(coordx,coord6y))
                        if length >= 7:
                            combat.blit(text_list[6],(coordx,coord7y))
                            if length >= 8:
                                combat.blit(text_list[7],(coordx,coord8y))
                                if length >= 9:
                                    combat.blit(text_list[8],(coordx,coord9y))



    inventory.fill((150,150,150))

    gui.fill((100,100,100))

    render_all()

def render_all():

    treasure_group.draw(tmp_map)

    monster_group.draw(tmp_map)

    screen.blit(tmp_map, (player.rect.x-player.map_x ,player.rect.y-player.map_y))

    player_sprite.draw(screen)

    screen.blit(vision_img, (0,0))

    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7 + 10, 0 + 10))
    screen.blit(combat, (tile_width * 7 + 10, tile_height*2 + 10))
    screen.blit(inventory, (tile_width*7+10, tile_height * 4 + 10))


    pygame.display.flip()


#initialisation

player = Player((play_area_x/2)*tile_width,(play_area_y/2)*tile_height)

wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')
vision_img = pygame.image.load('fov.png').convert_alpha()
fire_img = pygame.image.load('fire.png')
player_sprite = pygame.sprite.RenderPlain((player))
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
player_inventory = []

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 21)

text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))


make_map()
tmp_map.blit(level_map, (0,0))
render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)

    pygame.display.flip()

    keypress = handle_keys()
    if keypress:
        break


#if __name__== '__main__': main()
