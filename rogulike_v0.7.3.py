import pygame, sys, os
import random, math
from pygame.locals import *

pygame.init()

#set tile size
tile_width = 100
tile_height = 100

#set level size
tiles_x = 70
tiles_y = 70
map_width = tiles_x * tile_width
map_height = tiles_y * tile_height

#set screen size
display_tiles_x = 10
display_tiles_y = 7
play_area_x = 7
play_area_y = 7
screen_width = tile_width * display_tiles_x
screen_height = tile_height * display_tiles_y

#level creation variables
room_max_size = 7
room_min_size = 4


#level difficulty variables can get modified by load_level()
max_monsters = 6
max_goblins = 6
max_rats = 10
max_spiders = 5
monster_str = 1
max_items = 4

#set up surfaces
screen = pygame.display.set_mode((screen_width,screen_height))#,FULLSCREEN)
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))
item_map = pygame.Surface((700,700))
item_tmp_map = pygame.Surface((700,700))
item_map_open = False

gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width - 20,2*tile_height - 20))
equipment = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width - 20,2*tile_height - 20))

inventory_background = pygame.Surface((5*tile_width,5*tile_height))
inventory_1 = pygame.Surface((240,490))
inventory_2 = pygame.Surface((240,490))
trade_gui = pygame.Surface((460,100))

#load all images
ss = Sprite_sheet('magic_viking_spritesheet.png')
#level images
wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')
door_img = pygame.image.load('door2.png')
door_open_img = pygame.image.load('door_op.png')
exit_img = pygame.image.load('exit.jpg')
treasure_img = pygame.image.load('item.png').convert_alpha()
bag_img = pygame.image.load('bag.png').convert_alpha()

#effect images
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()
corpse_img = pygame.image.load('corpse.png').convert_alpha()
arrow_img = pygame.image.load('arrow.png').convert_alpha()
web_img = pygame.image.load('web.png').convert_alpha()

#enemy images
goblin_img = pygame.image.load('goblin.png').convert_alpha()
orc_img = pygame.image.load('orc2.png').convert_alpha()
troll_img = pygame.image.load('troll.png').convert_alpha()
spider_img = pygame.image.load('spider.png').convert_alpha()
spider_queen_img = pygame.image.load('spider_queen.png').convert_alpha()
broodling_img = pygame.image.load('broodling.png').convert_alpha()
rat_img = pygame.image.load('rat.png').convert_alpha()
web_sac_img = pygame.image.load('websac.png').convert_alpha()

#player images
player_img = pygame.image.load('character_naked.png').convert_alpha()
player_naked_img = pygame.image.load('character_naked.png').convert_alpha()
fists_img = pygame.image.load('fists.png').convert_alpha()
axe_img = pygame.image.load('axe.png').convert_alpha()
sword_img = pygame.image.load('sword.png').convert_alpha()
staff_img = pygame.image.load('staff.png').convert_alpha()
spear_img = pygame.image.load('spear.png').convert_alpha()
club_img = pygame.image.load('club.png').convert_alpha()
dagger_img = pygame.image.load('dagger.png').convert_alpha()
robe_img = pygame.image.load('robe.png').convert_alpha()
leather_img = pygame.image.load('leather.png').convert_alpha()
mail_img = pygame.image.load('mail.png').convert_alpha()
plate_img = pygame.image.load('plate.png').convert_alpha()
plate_helm_img = pygame.image.load('plate_helm.png').convert_alpha()
cloth_helm_img = pygame.image.load('cloth_helm.png').convert_alpha()
leather_helm_img = pygame.image.load('leather_helm.png').convert_alpha()
mail_helm_img = pygame.image.load('mail_helm.png').convert_alpha()
shield_img = pygame.image.load('shield.png').convert_alpha()
totem_img = pygame.image.load('totem.png').convert_alpha()
relic_img = pygame.image.load('relic.png').convert_alpha()
knife_img = pygame.image.load('knife.png').convert_alpha()

#create the player with some basic equipment
starter_cash = Item('Bag of Coin','currency',50)
copper_key = Item('Copper Key','key',1)
poison_cure = Item('Anti Venom','potion',20)
basic_armour = Equipment('Rusty Mail', mail_img,0,5,0,3,0,-1,0,0,0,1,1,1,1,1,1,1,'armour')
basic_weapon = Equipment('Rusty Axe', sword_img,5,0,1,0,1,0,0,0,0,1,1,1,0,0,0,0,'weapon')
player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_img,8,8,8,8,8,8,1000,8,8,8,basic_weapon,basic_armour,[starter_cash,copper_key,poison_cure])

#groups for the different sprites
player_sprite = pygame.sprite.RenderPlain((player))
all_group = pygame.sprite.Group()
all_group.add(player)
npc_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
spawner_group = pygame.sprite.Group()

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 21)


class Sprite_sheet(object):
    def __init__(self, file_name):
        self.sheet = pygame.image.load(file_name).convert()

    def image_at(self, rectangle, color_key = None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0,0), rect)
        if color_key is not None:
            if color_key is -1:
                color_key = image.get_at((0,0))
            image.set_colorkey(color_key, pygame.RLEACCEL)

        return image

    def images_at(self, rects, color_key = None):
        return [self.image_at(rect, color_key) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class Tile():
    
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.door = False
        self.locked = False
        self.shadow = True
        self.explored = False
        self.stairs_up = False
        self.stairs_down = False
        self.wall = blocked

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


class Game_object(pygame.sprite.Sprite):
     def __init__(self,x,y,name,img,stats=None,ai=None,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.dest_x = self.map_x
        self.dest_y = self.map_y
        self.current_x = self.map_x
        self.current_y = self.map_x
        self.blocks = blocks
        self.name = name
        
        self.stats = stats #class for stats inheritence
        self.ai = ai #class for ai inheritence

class Fighter_stats():
    def __init__(self,attk,de,m_attk,m_de,hit,dodge,hp,cha,per,lab,wep,arm,inventory):
        #equipment
        self.armour = arm
        self.weapon = wep
        self.helm = None
        self.boots = None
        self.offhand = None

        self.xp = 0
        self.level = 1
        self.stat_modifier = 0

        #player base stats
        self.attk_pwr = attk
        self.defence = de
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = m_attk
        self.magic_def = m_de
        self.charisma = cha #used in bartering
        self.perception = per
        self.labor = lab #used in crafting

        #copy of stats used in modify stats()
        self.c_attk_pwr = attk
        self.c_defence = de
        self.c_hit = hit
        self.c_dodge = dodge
        self.c_magic_attk = m_attk
        self.c_magic_def = m_de
        self.c_charisma = cha #used in bartering
        self.c_perception = per
        self.c_labor = lab #used in crafting
        self.c_max_hp = hp


        self.max_hp = hp
        self.hp = self.max_hp
        self.wounds = 0 #used to prevent healing to max hp

        self.poison = False
        
        self.inventory = inventory
        self.coin = 0

        self.frozen = False
        self.frozen_timer = 0
        
    def modify_stats(self):#when equiping new equipment etc

        attk_pwr = self.c_attk_pwr
        defence = self.c_defence
        hit = self.c_hit
        dodge = self.c_dodge
        magic_attk = self.c_magic_attk
        magic_def = self.c_magic_def
        charisma = self.c_charisma
        perception = self.c_perception
        labor = self.c_labor

        if self.armour is not None:
            attk_pwr = attk_pwr + self.armour.attk_pwr
            defence = defence + self.armour.defence
            hit = hit + self.armour.hit
            dodge = dodge + self.armour.dodge
            magic_attk = magic_attk + self.armour.magic_attk
            magic_def = magic_def + self.armour.magic_def
            charisma = charisma + self.armour.charisma
            perception = perception + self.armour.perception
            labor = labor + self.armour.labor

        if self.helm is not None:
            attk_pwr = attk_pwr + self.helm.attk_pwr
            defence = defence + self.helm.defence
            hit = hit + self.helm.hit
            dodge = dodge + self.helm.dodge
            magic_attk = magic_attk + self.helm.magic_attk
            magic_def = magic_def + self.helm.magic_def
            charisma = charisma + self.helm.charisma
            perception = perception + self.helm.perception
            labor = labor + self.helm.labor

        if self.weapon is not None:
            attk_pwr = attk_pwr + self.weapon.attk_pwr
            defence = defence + self.weapon.defence
            hit = hit + self.weapon.hit
            dodge = dodge + self.weapon.dodge
            magic_attk = magic_attk + self.weapon.magic_attk
            magic_def = magic_def + self.weapon.magic_def
            charisma = charisma + self.weapon.charisma
            perception = perception + self.weapon.perception
            labor = labor + self.weapon.labor

        if self.offhand is not None:
            attk_pwr = attk_pwr + self.offhand.attk_pwr
            defence = defence + self.offhand.defence
            hit = hit + self.offhand.hit
            dodge = dodge + self.offhand.dodge
            magic_attk = magic_attk + self.offhand.magic_attk
            magic_def = magic_def + self.offhand.magic_def
            charisma = charisma + self.offhand.charisma
            perception = perception + self.offhand.perception
            labor = labor + self.offhand.labor

        self.attk_pwr = attk_pwr
        self.defence = defence
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = magic_attk
        self.magic_def = magic_def
        self.charisma = charisma
        self.perception = perception
        self.labor = labor


        self.max_hp = self.c_max_hp - self.wounds

class spider_ai():
    
    def decision(self):
        
        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)

        if not self.frozen:
            if self.map_x == self.dest_x and self.map_y == self.dest_y:

                if dist_to_player_x <= ((play_area_x*tile_width)/2) and \
                   dist_to_player_y <= ((play_area_y*tile_height)/2):
    
                    new_dist_x = abs(self.map_x + tile_width - player.map_x)
                    new_dist_y = abs(self.map_y + tile_height - player.map_y)
    
                    random_num = random.randint(0,1)
                    if random_num == 0:
                        if new_dist_x < dist_to_player_x and dist_to_player_x != 0 :
                            
                            self.monster_move(tile_width,0)
    
                        elif new_dist_x > dist_to_player_x and dist_to_player_x != 0 :
                            
                            self.monster_move(-tile_width,0)
    
                        elif dist_to_player_x == 0 and new_dist_y < dist_to_player_y:
                            
                            self.monster_move(0,tile_height)
    
                        elif dist_to_player_x == 0 and new_dist_y > dist_to_player_y:
                            
                            self.monster_move(0,-tile_height)
    
                    elif random_num == 1:
                        if new_dist_y < dist_to_player_y and dist_to_player_y != 0 :
                            
                            self.monster_move(0,tile_height)
    
                        elif new_dist_y > dist_to_player_y and dist_to_player_y != 0 :
                            
                            self.monster_move(0,-tile_height)
    
                        elif dist_to_player_y == 0 and new_dist_x < dist_to_player_x:
                            
                            self.monster_move(tile_height,0)
    
                        elif dist_to_player_y == 0 and new_dist_x > dist_to_player_x:
                            
                            self.monster_move(-tile_height,0)
        else:
            self.moving = False
            self.frozen_timer -= 1
            if self.frozen_timer == 0:
                self.frozen = False


make_dungeon()#create the level

text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))

render_all()

clock = pygame.time.Clock()

while 1: # main game loop

    clock.tick(60)
    all_group.update()
    handle_keys()
    
    
    render_all()
    pygame.display.flip()
    
