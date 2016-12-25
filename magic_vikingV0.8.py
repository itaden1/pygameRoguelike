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



#level creation variables
room_max_size = 7
room_min_size = 4
#max_rooms = 50

#level difficulty variables can get modified by load_level()
max_monsters = 1
monster_str = 1
max_items = 4



level_up_base = 50
level_up_factor = 50

#hot keys
item_k1 = None
item_k2 = None
item_k3 = None
item_k4 = None
item_k5 = None
item_k6 = None
item_k7 = None
item_k8 = None
item_k9 = None
item_k0 = None

screen = pygame.display.set_mode((screen_width,screen_height))#,FULLSCREEN)
#level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))
item_map = pygame.Surface((700,700))
item_tmp_map = pygame.Surface((700,700))

gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width,3*tile_height+40))
equipment = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width,3*tile_height +40))

inventory_background = pygame.Surface((5*tile_width,5*tile_height))
inventory_1 = pygame.Surface((240,490))
inventory_2 = pygame.Surface((240,490))
trade_gui = pygame.Surface((460,100))

level_up_gui = pygame.Surface((200,200))


class Shadow(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = shadow_img
        self.rect = self.image.get_rect()
        self.rect.x=0
        self.rect.y=0
        self.map_x=x
        self.map_y=y
        
    
        
    
    
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
        self.door_open = False
        self.locked = False
        self.shadow = True
        self.explored = False
        self.stairs_up = False
        self.stairs_down = False
        self.wall = blocked
        
        self.fire_door = False
        self.ice_door = False
        self.skull_door = False
        
class Effect(pygame.sprite.Sprite):
    
    def __init__(self,x,y,anim):
        pygame.sprite.Sprite.__init__(self)
        self.anim = anim
        self.frame = 0
        self.image = self.anim[self.frame]
        self.rect = self.image.get_rect()
        self.map_x = x
        self.map_y = y
        self.rect.x = x
        self.rect.y = y
        
        self.life_time = 30
        self.time = 0

    def update(self):
        
        self.frame +=1
        self.time +=1
        if self.frame>=len(self.anim):
            self.frame = 0
        self.image = self.anim[self.frame]
        if self.time>=self.life_time:
            self.kill()
    
    
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

    def __init__(self,x,y,img,contains,name,locked,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.blocks = blocks
        self.name = name
        self.locked = locked

        self.inventory = contains

class Target(pygame.sprite.Sprite):
    
    def __init__(self):
        self.image = target_img
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y
        self.map_x = player.map_x
        self.map_y = player.map_y
        self.display = False
    
class Spawner(pygame.sprite.Sprite):
    
    def __init__(self,x,y,img,name,hp,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x
        self.map_y = y
        self.category = 'spawner'
        
        self.name = name
        self.blocks = blocks
        
        self.hp = hp
        
    
    
    def can_spawn(self,x,y):
        
        for m in monster_group:
            if m.blocks and m.map_x/tile_width == x and m.map_y/tile_height == y:
                return False
        return True       
        
    def spawn(self):
        
        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)
        if dist_to_player_x <= ((play_area_x*tile_width)/2) and \
                   dist_to_player_y <= ((play_area_y*tile_height)/2):
        
               
            if self.name == 'Egg Sac':
                
                if random.randint(1,10) <= 7:
                    
                    x,y = self.map_x/tile_width, self.map_y/tile_height
                    name = 'broodling'
                    img = broodling_idle
                    attack = 3+monster_str
                    defence = 3+monster_str
                    m_attk = 0
                    m_def = 0
                    hit = 4+monster_str
                    dodge = 6+monster_str
                    hp = 15+monster_str
                    char = 0
                    per = 0
                    xp = 1+monster_str
                    weapon = no_equipment
                    armour = no_equipment
                    if self.can_spawn(x,y):
                        monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,[],xp)
                        monster.current_x = monster.dest_x
                        monster.current_y = monster.dest_y
                        monster_group.add(monster)
                        all_group.add(monster)
                        
            

class Trap(pygame.sprite.Sprite):
    
    def __init__(self,x,y,img,name,effect):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.map_x = x
        self.map_y = y
        self.rect.x = x
        self.rect.y = y
        self.name = name
        
        
        self.effect_str = effect
        
    def trigger(self,target):
        if self.name == 'web'and target.name != 'spinner' and target.name != 'broodling' and target.name != 'spider_queen':
            target.frozen = True
            target.frozen_timer = self.effect_str
        elif self.name == 'ice':
            target.frozen = True
            target.frozen_timer = self.effect_str
            
class Item():
    def __init__(self,name,kind,val,img,weight):
        self.identity = 'item'
        self.name = name
        self.inv_img = img
        self.category = kind
        self.description = "I am an item that needs a proper description"
        self.value = val
        self.stackable = True
        self.counted = False
        self.identified = True
        
        self.weight = weight

class Equipment(pygame.sprite.Sprite):

    def __init__(self,name,p_img,inv_img,slash,smash,stab,fire,ice,thunder,dark,kind,weight,durability,description,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.identity = 'equipment'
        self.inv_img = inv_img
        self.anim = p_img
        self.player_img = self.anim[0]
        self.blocks = blocks
        self.name = name

        self.category = kind

        self.durability = durability
        self.description = description
        
        
        
        
        #stats
        self.slash = slash
        self.smash = smash
        self.stab = stab
        self.fire = fire
        self.ice = ice
        self.thunder = thunder
        self.dark = dark

       
        self.weight = weight
        
        
        self.value = (slash+smash+stab+fire+ice+thunder)*2
        
        if self.value >= 20 and random.randint(0,10) >= 6:
            self.identified = False
        else:
            self.identified = True
        self.stackable = False
        self.counted = False



class Character(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,de,m_attk,m_de,hit,dodge,hp,cha,per,wep,arm,inventory,xp=None,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.anim = img
        self.frame = random.randint(0,len(self.anim)-1)
        self.image = self.anim[self.frame]
        self.rect = self.image.get_rect()
        self.category = 'character'
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.dest_x = self.map_x
        self.dest_y = self.map_y
        self.current_x = self.map_x
        self.current_y = self.map_x
        self.moving = False
        self.blocks = blocks
        self.name = name
        self.target = None
        
        self.frame = 0
        

        self.target_x = self.map_x
        self.target_y = self.map_y
        

        #equipment
        self.helm = no_helm
        self.armour = arm
        self.gloves = no_equipment
        self.r_ring = no_equipment
        self.chain = no_equipment
        self.weapon = wep
        self.offhand = no_equipment
        self.boots = no_equipment
        

        #base stats
        self.strength = 0
        self.wisdom = 0
        self.cunning = 0
        self.ruthless = 0
        self.caution = 0
        self.strategy = 0

        self.xp = xp
        if self.xp == None:
            self.xp = 0
        self.level = 1
        self.level_up_points = 5

        #player base stats based on level and equipment
        self.attk_pwr = attk
        self.defence = de
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = m_attk
        self.magic_def = m_de
        self.charisma = cha #used in bartering
        self.perception = per
        
        

        ##copy of stats used in modify stats when equiping items these go up permanently on level up
        #self.c_attk_pwr = attk
        #self.c_defence = de
        #self.c_hit = hit
        #self.c_dodge = dodge
        #self.c_magic_attk = m_attk
        #self.c_magic_def = m_de
        #self.c_charisma = cha #used in bartering
        #self.c_perception = per
        

        self.c_max_hp = hp
        self.max_hp = hp
        self.hp = self.max_hp
        self.wounds = 0 #prevents healing to max hp
        self.hunger = 0
        self.hunger_timer = 0
        
        self.healing = False
        self.healing_timer = 0

        
        self.poison = False
        self.poison_timer = 0
        
        self.inventory = inventory
        self.current_weight = 0 #based on current inventory
        
        self.max_weight = 30 #based on strength
        

        self.frozen = False
        self.frozen_timer = 0



    def modify_stats(self):#when reecieving wounds debuffs or buffs

        self.current_weight = 0
        for i in self.inventory:
            for j in i:
                self.current_weight +=j.weight
        print "player weight = ", self.current_weight
        
        health = self.wounds+self.hunger
        self.max_hp = self.c_max_hp - health
        
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.hp <=0:
            self.death()

      
        
                
    def decision(self):
        
        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)

        if self.map_x == self.dest_x and self.map_y == self.dest_y:
            if self.poison == True:
                self.hp -= 1
                self.poison_timer -= 1
                if self.poison_timer <= 0:
                    self.poison = False
                if self.hp < 0:
                    self.hp = 0
                    self.death()
                    
            if not self.frozen:
            

                if dist_to_player_x <= ((play_area_x*tile_width)/2) and \
                   dist_to_player_y <= ((play_area_y*tile_height)/2):
                    if self.name == 'lych' and random.randint(1,10)>=6:
                        random_spell = random.randint(1,10)
                        
                        if random_spell <= 2:
                            self.cast_spell('ice_spell',player.current_x,player.current_y)
                        elif random_spell <= 7:
                            x=random.randint((self.dest_x/tile_width)-2,(self.dest_x/tile_width)+2)
                            y=random.randint((self.dest_y/tile_width)-2,(self.dest_y/tile_width)+2)
                            self.cast_spell('summon_spell',x*tile_width,y*tile_height)
                            print "summon"
                        else:
                            no_los = calc_field_of_view(self)
                            player_insight = True
                            for i in no_los:
                                
                                
                                if player.current_x == i.x1 and player.current_y == i.y1:
                                    player_insight = False
                                    
                                    
                                
                            if player_insight:
                                self.cast_spell('fire_spell',player.current_x,player.current_y)
                            
                    elif self.name == 'shaman' and random.randint(1,10)>5:
                        if random.randint(1,10)<= 7:
                            for m in monster_group:
                                if m.hp <= m.max_hp/2:
                                    dist_to_monster_x = abs(self.map_x - m.map_x)
                                    dist_to_monster_y = abs(self.map_y - m.map_y)
                                    if dist_to_monster_x <=(4*tile_width) and dist_to_monster_y <=(4*tile_width):
                                        
                                        self.cast_spell('heal_spell',m.current_x,m.current_y)
                                        break
                        else:
                            no_los = calc_field_of_view(self)
                            player_insight = True
                            for i in no_los:
                                
                                
                                if player.current_x == i.x1 and player.current_y == i.y1:
                                    player_insight = False
                                    
                                    
                                
                            if player_insight:
                                self.cast_spell('fire_spell',player.current_x,player.current_y)

                                
                    elif self.name == 'demon' and random.randint(1,10)>7:
                        
                        no_los = calc_field_of_view(self)
                        player_insight = True
                        for i in no_los:
                            
                            
                            if player.current_x == i.x1 and player.current_y == i.y1:
                                player_insight = False
                                
                                
                            
                        if player_insight:
                            self.cast_spell('fire_spell',player.current_x,player.current_y)
                        
                    else:
                        
                        
                        attacking_monster = False
                        target = None
                        if self.name == "%s's minion"%player.name:
                            
                            
                            for m in monster_group:
                                if m.name != "%s's minion"%player.name:
                                    dist_to_monster_x = abs(self.map_x - m.map_x)
                                    dist_to_monster_y = abs(self.map_y - m.map_y)
                                    if dist_to_monster_x <= (play_area_x*tile_width/2) and \
                                            dist_to_monster_y <= (play_area_y*tile_height/2):
                                        no_los = calc_field_of_view(self)
                                        monster_insight = True
                                        for i in no_los:
                                
                                
                                            if m.current_x == i.x1 and m.current_y == i.y1:
                                                monster_insight = False
                                            if monster_insight:
                                        
                                        
                                        
                                                attacking_monster = True
                                                target = m
                                                new_dist_x = abs(self.map_x + tile_width - m.map_x)
                                                new_dist_y = abs(self.map_y + tile_height - m.map_y)
                                                break
                                
                        if attacking_monster:
                            dist_to_monster_x = abs(self.map_x - target.map_x)
                            dist_to_monster_y = abs(self.map_y - target.map_y)
                            new_dist_x = abs(self.map_x + tile_width - target.map_x)
                            new_dist_y = abs(self.map_y + tile_height - target.map_y)
                            random_num = random.randint(0,1)
                            if random_num == 0:
                                if new_dist_x < dist_to_monster_x and dist_to_monster_x != 0 :
                                    
                                    self.monster_move(tile_width,0)
            
                                elif new_dist_x > dist_to_monster_x and dist_to_monster_x != 0 :
                                    
                                    self.monster_move(-tile_width,0)
            
                                elif dist_to_monster_x == 0 and new_dist_y < dist_to_monster_y:
                                    
                                    self.monster_move(0,tile_height)
            
                                elif dist_to_monster_x == 0 and new_dist_y > dist_to_monster_y:
                                    
                                    self.monster_move(0,-tile_height)
                               
            
                            elif random_num == 1:
                                if new_dist_y < dist_to_monster_y and dist_to_monster_y != 0 :
                                    
                                    self.monster_move(0,tile_height)
            
                                elif new_dist_y > dist_to_monster_y and dist_to_monster_y != 0 :
                                    
                                    self.monster_move(0,-tile_height)
            
                                elif dist_to_monster_y == 0 and new_dist_x < dist_to_monster_x:
                                    
                                    self.monster_move(tile_height,0)
            
                                elif dist_to_monster_y == 0 and new_dist_x > dist_to_monster_x:
                                    
                                    self.monster_move(-tile_height,0)
                                   
                        else:    
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
                    effect_anim = Effect(self.dest_x,self.dest_y,shatter_anim)
                    effect_group.add(effect_anim)
                    all_group.add(effect_anim)
                    for t in trap_group:
                        if t.map_x == self.map_x and t.map_y == self.map_y:
                            t.kill()
                    self.frozen = False
    
    

    def update(self):
        
        self.frame+=1
        if self.frame>=len(self.anim):
            self.frame = 0
        self.image = self.anim[self.frame]
        
        if len(effect_group)<=0:
        
            if self.dest_y > self.current_y:    
                self.current_y +=10
                
    
            elif self.dest_y < self.current_y:                   
                self.current_y -=10 
                      
          
            elif self.dest_x > self.current_x:
                self.current_x +=10
                 
                    
            elif self.dest_x < self.current_x:                   
                self.current_x -=10
            
                
            
            self.map_x = self.current_x
            self.map_y = self.current_y

    def monster_move(self,x,y):

        target = None
        dest_x = self.map_x + x
        dest_y = self.map_y + y
        
        for trap in trap_group:
                if dest_x == trap.map_x and dest_y == trap.map_y:
                    trap.trigger(self)
                    self.moving=False
                    
        if self.name == "%s's minion"%player.name:
            for m in monster_group:
                if (dest_x == m.current_x and dest_y == m.current_y):
                    target = m
                
                
        if self.name != "%s's minion"%player.name:
            for m in monster_group:
                if m.name == "%s's minion"%player.name and \
                           (dest_x == m.current_x and dest_y == m.current_y):
                    
                    target = m
                elif (dest_x == player.current_x and dest_y == player.current_y):
                    target = player
                else:
                    target = None
            
        if target is not None:
            self.attack(target)
            player.moving = False
            
        else:
            if self.name == 'Spinner':
                web_chance = random.randint(1,10)
                if web_chance <= 4:
                    web = Trap(self.map_x,self.map_y,web_img,'web',3)
                    trap_group.add(web)
                    self.move(x,y)
                else:
                    self.move(x,y)
                    
            if self.name == 'Spider Queen':
                sac_chance = random.randint(1,10)
                if sac_chance <=3:
                    
                    if not is_blocked((self.map_x/tile_width)+x/tile_width,(self.map_y/tile_height)+y/tile_height):
                        sac = Spawner(self.map_x,self.map_y,web_sac_img,'Egg Sac',40)
                        spawner_group.add(sac)
                        all_group.add(sac)
                        self.move(x,y)
                    else:
                        print "failed"
                    
                        
                elif sac_chance<=5:
                        hit_chance = (self.hit+random.randint(1,10)) - (player.dodge+random.randint(1,10))
                        if hit_chance >= 1:
                            los = calc_field_of_view(self)
                            player_insight = True
                            for i in los:
                                
                                
                                if player.current_x == i.x1 and player.current_y == i.y1:
                                    player_insight = False
                                    
                                    
                                
                            if player_insight:
                                web = Trap(player.dest_x,player.dest_y,web_img,'web')
                                player.frozen = True
                                player.frozen_timer = 4
                                trap_group.add(web)
                                text = "%s entangles you" %self.name
                            
                            else:
                                text = "%s flings web but misses" %self.name
                        else:
                            text = "%s flings web but misses" %self.name
                        updateGUI(text,(10,10,10))
                else:
                    self.move(x,y)
            else:    
                self.move(x,y)
                    
            #self.dest_x = self.map_x + x
            #self.dest_y = self.map_y + y


    def move_or_attack(self,x,y):
        
        self.hunger_timer+=1
        if self.hunger_timer >= 100:
            self.hunger_timer = 0
            self.hunger+=1
            self.modify_stats()
            if self.hunger >= 1:
                txt = "you feel hungry"
            elif self.hunger >= 10:
                txt = "you feel ravenous"
            elif self.hunger >= 25:
                txt = "you are starving"
            updateGUI(txt,(10,10,10))
            

            
        if not self.frozen:
                
            if self.poison == True:
                self.hp -= 1
                txt = 'you lose hp from poison'
                self.poison_timer -= 1
                if self.poison_timer <= 0:
                    self.poison = False
                if self.hp < 0:
                    self.hp = 0
                    text = "you succumb to the poison"
                    col = (100,100,10)
                    updateGUI(text,col)
                    self.death()
                else:
                    updateGUI(txt,(10,10,10))
            if self.healing == True:
                self.hp += 1
                self.healing_timer -= 1
                if self.healing_timer <= 0:
                    self.healing = False
                if self.hp >= player.max_hp:
                    self.hp = player.max_hp
                    text = "you are fully restored"
                    self.healing = False
                    self.healing_timer = 0
                    col = (100,100,10)
                    updateGUI(text,col)
                updateGUI(None,None)
                    
                

            target = None
            friendly_target = None
            dest_x = self.dest_x +x
            dest_y = self.dest_y +y

            for monster in monster_group:
                if dest_x == monster.map_x and dest_y == monster.map_y:
                    target = monster
                    self.moving = False
                    
            for spawner in spawner_group:
                if dest_x == spawner.map_x and dest_y == spawner.map_y:
                    target = spawner
                    self.moving = False
                    
            if target is not None:
                self.attack(target)
                
            for trap in trap_group:
                if dest_x == trap.map_x and dest_y == trap.map_y:
                    trap.trigger(self)
                    self.moving=False
                

            for npc in npc_group:
                if dest_x == npc.map_x and dest_y == npc.map_y:
                    friendly_target = npc
                    self.moving = False
            if friendly_target is not None:
                open_inventory(self.inventory,friendly_target,'trade')

            if my_map[dest_x/tile_width][dest_y/tile_height].door and my_map[dest_x/tile_width][dest_y/tile_height].door_open == False:
                self.moving = False
                if my_map[dest_x/tile_width][dest_y/tile_height].locked:
                    text = "The door is locked"
                    
                else:
                    
                    my_map[dest_x/tile_width][dest_y/tile_height].blocked = False
                    my_map[dest_x/tile_width][dest_y/tile_height].door_open = True
                    my_map[dest_x/tile_width][dest_y/tile_height].block_sight = False
                    tmp_map.blit(door_open_img,(dest_x,dest_y))
                    text = "you open the door"
                render_all()
                updateGUI(text,(100,100,10))

            else:

                self.move(x,y)
    
        else:
            self.moving = False
            self.frozen_timer -= 1
            if self.frozen_timer == 0:
                self.frozen = False
                effect_anim = Effect(self.dest_x,self.dest_y,shatter_anim)
                effect_group.add(effect_anim)
                all_group.add(effect_anim)
                for t in trap_group:
                    if t.map_x == self.map_x and t.map_y == self.map_y:
                        t.kill()
                        
        
            



    def cast_spell(self,spell,coord_x,coord_y):
        
        map_pos_x = player.rect.x - player.current_x
        map_pos_y = player.rect.y - player.current_y
        aoe_targets = [(coord_x,coord_y),(coord_x + tile_width,coord_y),(coord_x - tile_width,coord_y),\
            (coord_x,coord_y + tile_height),(coord_x,coord_y-tile_height)]
        spell_targets = []

        if spell == 'heal_spell':
            coords = (coord_x,coord_y)
            spell_anim = Effect(coord_x,coord_y,heal_anim)
            effect_group.add(spell_anim)
            
            all_group.add(spell_anim)
            target = None
            for monster in monster_group:
                if coords == (monster.dest_x,monster.dest_y):
                    target = monster
                
                
            if coords == (player.dest_x,player.dest_y):
                target = player
            
                
            if target is not None:
                spell_power = random.randint(1,6)
                holy_modifier = (self.weapon.dark+self.gloves.dark+self.r_ring.dark+self.offhand.dark+self.charisma)+(target.helm.dark+target.armour.dark+target.chain.dark+target.boots.dark)
                print holy_modifier
                heal = spell_power + holy_modifier
                target.hp += heal
                text = '%s gain %s from heal spell' % (target.name,heal)
                if target.hp >= target.max_hp:
                    target.hp = target.max_hp
                
    
    
                updateGUI(text,(100,100,10))
            else:
                text = '%s waste the heal spell'%self.name
                updateGUI(text,(100,100,10))

        elif spell == 'fire_spell':
            
            for t in aoe_targets:
                
                x = t[0]
                y = t[1]
                print x,y
                
                spell_anim = Effect(x,y,fire_anim)
                effect_group.add(spell_anim)
                all_group.add(spell_anim)
         
                    
            for target in aoe_targets:
                if target == (player.dest_x,player.dest_y):
                    spell_target = player
                    spell_targets.append(spell_target)

                for monster in monster_group:
                    if target == (monster.dest_x,monster.dest_y):
                        spell_target = monster
                        spell_targets.append(spell_target)
                        
                for trap in trap_group:
                    if target == (trap.map_x,trap.map_y):
                        trap.kill()

            for target in spell_targets:
                spell_power = random.randint(1,6)
                spell_dmg = (spell_power + self.magic_attk) - (target.magic_def)
                
                fire = (self.weapon.fire + self.gloves.fire +self.offhand.fire + self.r_ring.fire) - \
                       (target.armour.fire + target.helm.fire + target.chain.fire + target.boots.fire)

                
                dmg = spell_dmg+fire
                
                target.hp -= dmg
                text = "%s hits %s with %s fire damage" % (self.name,target.name,dmg)
                
                
                
                if target.hp <= 0:
                    target.hp = 0
                    text = "%s burns to death" % target.name
                    col = (100,100,10)
                    updateGUI(text,col)
                    target.death()


                tmp_map.blit(scorch_img,(target.dest_x,target.dest_y))
                updateGUI(text,(100,100,10))
               
            


        elif spell == 'ice_spell':
            
            for target in aoe_targets:
                x = target[0]
                y = target[1]
                
                ice_trap = Trap(x,y,ice_3,'ice',4)
                trap_group.add(ice_trap)
                if target == (player.dest_x,player.dest_y):
                    spell_target = player
                    spell_targets.append(spell_target)

                for monster in monster_group:
                    if target == (monster.dest_x,monster.dest_y):
                        spell_target = monster
                        spell_targets.append(spell_target)
                
            for target in spell_targets:
                spell_anim = Effect(target.dest_x,target.dest_y,ice_anim)
                effect_group.add(spell_anim)
                all_group.add(spell_anim)
                spell_power = random.randint(1,6)
                spell_dmg = (spell_power + self.magic_attk) - (target.magic_def/2)

                ice = (self.weapon.ice + self.gloves.ice +self.offhand.ice + self.r_ring.ice) - \
                       (target.armour.ice+target.boots.ice + target.chain.ice+ target.helm.ice)

                if ice <=0:
                    ice = 0
                effect = spell_dmg + ice
                if effect <= 0:
                    text = "%s resisted the spell" % target.name
                else:
                    target.frozen = True
                    target.frozen_timer = effect
                    text = " %s freezes in place" % target.name
                
                    
                updateGUI(text,(100,100,10))
        
        
        elif spell == 'thunder_spell':
          
                   
            coords = (coord_x,coord_y)
            spell_anim = Effect(coord_x,coord_y,lightning_anim)
            effect_group.add(spell_anim)
            
            all_group.add(spell_anim)
            
            
            
            target = None
            for monster in monster_group:
                if coords == (monster.dest_x,monster.dest_y):
                    target = monster
            if coords == (player.dest_x,player.dest_y):
                target = player
            
                
            if target is not None:
                bonus = random.randint(5,15)
                dmg = self.magic_attk - target.magic_def/2
                thunder = (self.weapon.thunder + self.gloves.thunder +self.offhand.thunder + self.r_ring.thunder) - \
                       (target.armour.thunder + target.boots.thunder+target.chain.thunder + target.helm.thunder)
                dmg = dmg + thunder + bonus
                target.hp -= dmg
                text = "%s hit %s with %s lightning" %(self.name,target.name,dmg)
                if target.hp < 0:
                    target.hp = 0
                    text = "%s burns to death" % target.name
                    col = (100,100,10)
                    updateGUI(text,col)
                    target.death()
                updateGUI(text,(10,10,10))
           
            
                       
        elif spell == 'poison_spell':
            
            coords = (coord_x,coord_y)
            target = None
            for monster in monster_group:
                if coords == (monster.dest_x,monster.dest_y):
                    target = monster
            if coords == (player.dest_x,player.dest_y):
                target = player
        
            
            if target is not None:
                
                time = self.magic_attk - target.magic_def/2
                time_bonus = random.randint(1,10)
                dark_bonus = (self.weapon.dark - self.gloves.dark - self.offhand.dark -  self.r_ring.dark)-\
                (target.armour.dark - target.boots.dark-target.chain.dark - target.helm.dark) 
                      
                dmg = time + dark_bonus + time_bonus
                target.poison = True
                target.poison_timer = dmg
                text = "%s poison %s for %s moves" %(self.name,target.name,dmg)
                if target.hp < 0:
                    target.hp = 0
                    text = "%s is poisoned to death" % target.name
                    col = (100,100,10)
                    updateGUI(text,col)
                    target.death()
                updateGUI(text,(10,10,10))
             
            else:
                text = "you cast poison on nothing"
                updateGUI(text,(10,10,10))
        
        elif spell == 'ranged':
            coords = (coord_x,coord_y)
            target = None
            for monster in monster_group:
                if coords == (monster.dest_x,monster.dest_y):
                    target = monster
            if coords == (player.dest_x,player.dest_y):
                target = player
            if target is not None:
                dmg_modifier = random.randint(1,20)
                dmg = (self.hit+random.randint(1,10))-(target.dodge+random.randint(1,10)+self.weapon.stab)
                
                if dmg <=0:
                    dmg =1
                target.hp -= dmg
                text = "%s hit %s for %s damage" %(self.name,target.name,dmg)
                if target.hp < 0:
                    target.hp = 0
                    text = "%s succumbs to its wounds" % target.name
                    col = (100,100,10)
                    updateGUI(text,col)
                    target.death()
                updateGUI(text,(100,100,10))
            
        elif spell == 'summon_spell':
            
            target_x = coord_x/tile_width
            target_y = coord_y/tile_width
           
            if not is_blocked(target_x,target_y):
                loyal = random.randint(0,20)-self.charisma
                if loyal<=0:
                    name = "%s's minion" %self.name
                    text = "%s summons a minion"%self.name
                else:
                    name = "enraged minion"
                    text = "%s summons an enraged minion"%self.name
                bonus = (self.weapon.dark-self.armour.dark-self.helm.dark-self.r_ring.dark-self.offhand.dark-self.boots.dark - \
                         self.chain.dark)
                stat_1 = random.randint(1,self.charisma+bonus)
                stat_2 = random.randint(1,self.charisma+bonus)
                stat_3 = random.randint(1,self.charisma+bonus)
                monster = Character(target_x,target_y,name,[skeleton_img],stat_1,stat_2,0,0,stat_3,stat_1,(stat_2+10),stat_3,stat_1,no_equipment,no_equipment,[],5)
                monster.current_x = monster.dest_x
                monster.current_y = monster.dest_y
                monster_group.add(monster)
                updateGUI(text,(0,0,0))
                all_group.add(monster)
        
        elif spell == 'control_spell':
            for m in monster_group:
                if m.dest_x == coord_x and m.dest_y == coord_y:
                    chance = self.charisma-m.charisma
                    if chance >0:
                        text = "%s enslaves %s" %(self.name,m.name)
                        m.name = "%s's minion"%self.name
                        updateGUI(text,(0,0,0))
                        
        elif spell == 'teleport_spell':
            load_new_level('teleport')
            
        else:
            text = '%s fail to cast spell' %self.name
            updateGUI(text,(100,100,10))

        
    def move(self,x,y):
        
        if not is_blocked(self.map_x/tile_width + x/tile_width ,self.map_y/tile_height + y/tile_height):
            if not is_blocked(self.dest_x/tile_width + x/tile_width ,self.dest_y/tile_height + y/tile_height):
            
                self.dest_x += x
                self.dest_y += y
            
            else:
                self.moving = False
        else:
            self.moving = False

    def attack(self,target):
        
        
        if target.category == 'spawner':
            
            attack_roll = random.randint(1,6)
            attack = attack_roll + self.attk_pwr
            
            
            slash = self.weapon.slash 
            smash = self.weapon.smash 
            stab = self.weapon.stab 
            dmg = attack+slash+smash+stab
            if dmg <= 0:
                dmg = 1
            target.hp -= dmg
            self.weapon.durability -=1
            txt = "you hit %s for %s" %(target.name,dmg)
            if target.hp<=0:
                target.hp = 0
                txt = "%s is destroyd" %target.name
                target.kill()
            updateGUI(txt,(10,10,10))
            
        
        else:
            hit_roll = random.randint(1,6)
            hit_chance = hit_roll + self.hit
            miss_roll = random.randint(1,6)
            miss_chance = miss_roll + target.dodge
    
            if hit_chance >= miss_chance:
                effect_anim = Effect(target.current_x,target.current_y,slash_anim)
                effect_group.add(effect_anim)
                all_group.add(effect_anim)
                
                attack_roll = random.randint(1,6)
                attack = attack_roll + self.attk_pwr
                mit_roll = random.randint(1,6)
                mitigate = mit_roll + target.defence
                
                slash_att = self.weapon.slash
                if self.offhand.name != 'Shield':
                    slash_att += self.offhand.slash
                slash_def = target.armour.slash+target.helm.slash+target.gloves.slash+target.boots.slash
                if target.offhand.name == 'Shield':
                    slash_def += target.offhand.slash
                
                smash_att = self.weapon.smash+self.offhand.smash
                smash_def = target.armour.smash+target.helm.smash+target.gloves.smash+target.boots.smash
                if target.offhand.name == 'Shield':
                    smash_def += target.offhand.smash
                    
                stab_att = self.weapon.stab
                if self.offhand.name != 'Shield':
                    stab_att += self.offhand.stab
                stab_def = target.armour.stab+target.helm.stab+target.gloves.stab+target.boots.stab
                if target.offhand.name == 'Shield':
                    smash_def += target.offhand.stab
                
                
                slash = slash_att-slash_def
                stab = stab_att-stab_def
                smash = smash_att-smash_def
    
                if slash <= 0:
                    slash = 0
                if smash <= 0:
                    smash = 0
                if stab <= 0:
                    stab = 0

    
                if attack_roll == 6:
                    dmg = (attack-(mitigate/2))  + slash+smash+stab
                    target.wounds += random.randint(1,5)
                    if target.wounds >= target.max_hp-1:
                        target.wounds = target.max_hp-1
                    if target.hp >target.max_hp:
                        target.hp=target.max_hp
                    target.modify_stats()
                    text = "%s recieves a seriouse wound" %target.name
                    col = (10,10,10)
                    updateGUI(text,col)
                    self.weapon.durability-=1
                    target.armour.durability-=3
                    target.helm.durability-=2
                    target.gloves.durability -=2
                    target.boots.durability -=2
                    target.r_ring.durability -=2
                    target.chain.durability -=2
    
                else:
   
                    dmg = (attack - mitigate)+slash+smash+stab
    
                if dmg <= 0:
                    dmg = 1
                    self.weapon.durability-=2
                    target.offhand.durability-=2
                target.hp -= dmg
                self.weapon.durability-=1
                self.offhand.durability-=1
                target.armour.durability-=3
                target.helm.durability-=1
                target.gloves.durability -=1
                target.boots.durability -=1
                target.r_ring.durability -=1
                target.chain.durability -=1
                if self.name == 'Spinner' or self.name == 'Spider_Queen':
                    if random.randint(1,10) <=3:
                        target.poison = True
                        time = random.randint(9,20)
                        target.poison_timer = time
                        txt = 'you have been poisoned'
                        updateGUI(txt,(10,10,10))
                if target.hp <= 0:
                    target.hp = 0
                    text = "%s DIE!!!" % target.name
                    target.death()
                    updateGUI(text,(100,10,10))
                    
    
                else:
                    text = "%s hit %s for %s damage" % (self.name,target.name,dmg)
                    col = (10,10,10)
                    updateGUI(text,col)
                    
                
    
            else:
    
                text = " %s dodges %s attack" % (target.name,self.name)
                col = (10,10,10)
                updateGUI(text,col)
        if target.category is not 'spawner':
            if self.weapon.durability <=0:
                self.weapon = no_equipment
                self.weapon.durability = 0
            if target.armour.durability<=0:
                target.armour = no_equipment
                target.armour.durability = 0
            if target.helm.durability <=0:
                target.helm = no_equipment
                target.helm.durability = 0
            if target.offhand.durability<=0:
                target.offhand = no_equipment
                target.offhand.durability = 0
        
        

    def death(self):


        tmp_map.blit(corpse_img, (self.current_x,self.current_y))
        self.kill()

        if self == player:
            self.armour = no_equipment
            self.weapon = no_equipment
            self.helm = no_equipment
            self.offhand = no_equipment
            self.gloves = no_equipment
            self.boots = no_equipment
            tmp_map.blit(corpse_img, (self.current_x,self.current_y))
            text = "You reached dungeon lvl %s" % monster_str
            updateGUI(text,(10,10,10))
            text = "and gained level %s" %self.level
            updateGUI(text,(10,10,10))
            render_all()
            load_new_level('death')

        else:
            player.xp += self.xp
            level_up_xp = level_up_base + (level_up_factor*player.level)
            if player.xp >= level_up_xp:
                player.level += 1
                player.xp = 0
                player.level_up_points += 1
                text = "%s has leveled up!!" %self.name
                col = (150,150,150)
                updateGUI(text,(col))
            loot_list = self.inventory
            if len(loot_list) is not 0:
                loot = Treasure(self.map_x/tile_width,self.map_y/tile_height,loot_img,loot_list,'Corpse',False)
                treasure_group.add(loot)
            updateGUI(None,None)
        render_all()



def handle_keys():
    global item_k1
    global item_k2
    global item_k3
    global item_k4
    global item_k5
    global item_k6
    global item_k7
    global item_k8
    global item_k9
    global item_k0
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            elif event.key == K_LEFT:
                player.moving = 'left'

                
            elif event.key == K_RIGHT:
                player.moving = 'right'


            elif event.key == K_UP:
                player.moving = 'up'


            elif event.key == K_DOWN:
                player.moving = 'down'
                

            #display level map
            elif event.key == K_m:
                global item_map_open
                if item_map_open == True:
                    item_map_open = False
                else:
                    item_map_open = True

            #skip level for testing purposes
            elif event.key == K_p:
                load_new_level('')
                updateGUI('going down',(10,10,10))
                render_all()
            elif event.key == K_o:
                load_new_level('retreat')
                updateGUI('going up',(10,10,10))
                render_all()


            #pickup/equip/examine
            elif event.key == K_i:
                open_inventory(player.inventory,None,'trash')
            elif event.key == K_g:
                open_inventory(player.inventory,None,'gear')
            elif event.key == K_l:
                level_up()
            elif event.key == K_e:
                target_mode('examine')
                
            elif event.key == K_f:
                pickup_object()
                if len(effect_group)==0:
                    for m in monster_group:
                        m.decision()
            
            
            elif event.key == K_1:
                if item_k1 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k1 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k1
                        updateGUI(text,(10,10,10))
                
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_2:
                if item_k2 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k2 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k2
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_3:
                if item_k3 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k3 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k3
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_4:
                if item_k4 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k4 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k4
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_5:
                if item_k5 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k5 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k5
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_6:
                if item_k6 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k6 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k6
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_7:
                if item_k7 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k7 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k7
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_8:
                if item_k8 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k8 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k8
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_9:
                if item_k9 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k9 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k9
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
            elif event.key == K_0:
                if item_k0 is not None:
                    found = False
                    for i in player.inventory:
                        if len(i) !=0:
                            if i[0].name == item_k0 :
                                item = i.pop(0)
                                use_equip(item)
                                found = True
                                break
                                
                    if not found:
                        text = "you have no %s"%item_k0
                        updateGUI(text,(10,10,10))
                for m in monster_group:
                    m.decision()
                for s in spawner_group:
                    s.spawn()
        else:
            player.moving = False
    
    if player.moving == 'left':
        if player.map_x == player.dest_x and player.map_y == player.dest_y:
            player.move_or_attack(-tile_width,0)
            for m in monster_group:
                m.decision()
            for s in spawner_group:
                s.spawn()
    elif player.moving == 'right':
        if player.map_x == player.dest_x and player.map_y == player.dest_y:
            player.move_or_attack(tile_width,0)
            for m in monster_group:
                m.decision()
            for s in spawner_group:
                s.spawn()
    elif player.moving == 'up':
        if player.map_x == player.dest_x and player.map_y == player.dest_y:
            player.move_or_attack(0,-tile_height)
            for m in monster_group:
                m.decision()
            for s in spawner_group:
                s.spawn()
    elif player.moving == 'down':
        if player.map_x == player.dest_x and player.map_y == player.dest_y:
            player.move_or_attack(0,tile_height)
            for m in monster_group:
                m.decision()
            for s in spawner_group:
                s.spawn()
        

def target_mode(selected_spell):
    

    target=None
    targetting = True
    reticule.display = True
    map_pos_x = player.rect.x - player.current_x
    map_pos_y = player.rect.y - player.current_y
    
    
    while targetting:
        all_group.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                pygame.quit()
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    targetting = False
                    reticule.display = False
                    
                elif event.key == K_LEFT:
                    if reticule.rect.x > 100:
                        reticule.rect.x -= tile_width
                elif event.key == K_RIGHT:
                    if reticule.rect.x < 500:
                        reticule.rect.x += tile_width
                elif event.key == K_UP:
                    if reticule.rect.y > 100:
                        reticule.rect.y -= tile_height
                elif event.key == K_DOWN:
                    if reticule.rect.y < 500:
                        reticule.rect.y += tile_height
                
                elif event.key == K_RETURN:
                    targetting = False
                    reticule.display = False
                    if selected_spell == 'examine':
                        examine_object(reticule.rect.x - map_pos_x,reticule.rect.y - map_pos_y)
                    else:
                        player.cast_spell(selected_spell,reticule.rect.x - map_pos_x,reticule.rect.y - map_pos_y)
                   
               
                        
                    
        
        render_all()
        
        
    
def pickup_object():

    door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
    door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]

    for y in door_locations_y:
        for x in door_locations_x:
            
            if my_map[x/tile_width][y/tile_height].door_open == False and my_map[x/tile_width][y/tile_height].locked != True\
            and my_map[x/tile_width][y/tile_height].door:
                my_map[x/tile_width][y/tile_height].door_open = True
                my_map[x/tile_width][y/tile_height].block_sight = False
                my_map[x/tile_width][y/tile_height].blocked = False
                tmp_map.blit(door_open_img,(x,y))
                
            

    if my_map[player.map_x/tile_width][player.map_y/tile_height].stairs_down:
        text = "you descend further into the darkness"

        load_new_level('')
        updateGUI(text,(10,10,10))
        render_all()

    elif my_map[player.map_x/tile_width][player.map_y/tile_height].stairs_up:
        text = "you ascend back towards the light"

        load_new_level('retreat')
        updateGUI(text,(10,10,10))
        render_all()


    for item in treasure_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            if not item.locked:
                open_inventory(player.inventory,item,'loot')

                contents = len(item.inventory)
                if contents <=0:
                    treasure_group.remove(item)
                    item.kill()
            else:
                text = "The chest is locked"
                updateGUI(text,(10,10,10))
            render_all()

def unequip_item(item):
    if item.category =='armour':
        player.armour = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'weapon':
        player.weapon = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'helm':
        player.helm = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'off hand':
        player.offhand = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'r_ring':
        player.r_ring = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'chain':
        player.chain = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'gloves':
        player.gloves= no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    elif item.category == 'boots':
        player.boots = no_equipment
        text = "you unequip %s"%item.name
        player.modify_stats()
    else:
        text = "Nothing to unequip"
    player.modify_stats()
    updateGUI(text,(10,10,10))
    
    
def use_equip(item):
    
    if item.category == 'armour':
        if player.armour.category != 'no equipment':
            player.inventory.append([player.armour])
        player.armour = item
        text = "you equip %s"%item.name
        
        player.modify_stats()
    if item.category == 'weapon':
        if player.weapon.category != 'no equipment':
            player.inventory.append([player.weapon])
        player.weapon = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'helm':
        if player.helm.category != 'no equipment':
            player.inventory.append([player.helm])
        player.helm = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'off hand':
        if player.offhand.category != 'no equipment':
            player.inventory.append([player.offhand])
        player.offhand = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'r_ring':
        if player.r_ring.category != 'no equipment':
            player.inventory.append([player.r_ring])
        player.r_ring = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'gloves':
        if player.gloves.category != 'no equipment':
            player.inventory.append([player.gloves])
        player.gloves = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'chain':
        if player.chain.category != 'no equipment':
            player.inventory.append([player.chain])
        player.chain = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'boots':
        if player.boots.category != 'no equipment':
            player.inventory.append([player.boots])
        player.boots = item
        text = "you wield %s"%item.name
        player.modify_stats()
        
    if item.category == 'scroll':
        
        if item.name == 'Fire Scroll':
            target_mode('fire_spell')
            #print "fire"
            #player.cast_spell('fire_spell')
            text = "You use a Fire Scroll"
            #print text
        elif item.name == 'Ice Scroll':
            target_mode('ice_spell')
            #player.cast_spell('ice_spell')
            text = "You use an Ice Scroll" 
        elif item.name == 'Health Scroll':
            target_mode('heal_spell')
            #player.cast_spell('heal_spell')
            text = "You use a Health Scroll"
        elif item.name == 'Thunder Scroll':
            target_mode('thunder_spell')
            #player.cast_spell('thunder_spell')
            text = "You use thunder scroll"
        elif item.name == 'Poison Scroll':
            target_mode('poison_spell')
            #player.cast_spell('thunder_spell')
            text = "You use poison scroll"
        elif item.name == 'Summon Scroll':
            target_mode('summon_spell')
            #player.cast_spell('thunder_spell')
            text = "You use summon scroll"
        elif item.name == 'Tame Scroll':
            target_mode('control_spell')
            #player.cast_spell('thunder_spell')
            text = "You use control scroll"
        elif item.name == 'Teleport Scroll':
            player.cast_spell('teleport_spell',player.dest_x,player.dest_y)
            text = "You use teleport scroll"
    if item.category == 'ranged':
        target_mode('ranged')
        text = "you have thrown a knife"
        
    if item.category == "food":
        player.hunger = 0
        text = "you eat the %s" %item.name
        updateGUI(text,(10,10,10))
        if item.name == 'Mouldy Bread' and random.randint(1,10)>=5:
            player.poison = True
            player.poison_timer = 10
            text = "You feel sick"
            
        player.modify_stats()
        

    if item.category == 'bandage':
        random_roll = random.randint(0,3)
        amount = random_roll+player.charisma/2
        player.wounds -= amount
        text = "you bandage %s wounds" %amount
        if player.wounds <=0:
            player.wounds = 0
        player.modify_stats()
    if item.category == 'potion':
        if item.name == 'Anti Venom':
            player.poison = False
            text = "you cure the poison"
        elif item.name == 'Mystery Potion':
            random_roll = random.randint(1,100)
            if random_roll <=5:
                player.max_hp +=1
                text = "you feel stronger"
            elif random_roll <=10:
                player.max_hp -=1
                text = "you feel weak"
            elif random_roll <=15:
                player.attk_pwr +=1
                text = "you feel stronger"
            elif random_roll <= 20:
                player.attk_pwr -=1
                text = "you feel weak"
            elif random_roll <=25:
                player.defence +=1
                text = "you feel stronger"
            elif random_roll <=30:
                player.defence -=1
                text = "you feel weak"
            elif random_roll <=35:
                player.magic_attk +=1
                text = "you feel powerfull"
            elif random_roll <=40:
                player.magic_attk -=1
                text = "you feel fuzzy"
            elif random_roll <=45:
                player.magic_def +=1
                text = "you feel powerfull"
            elif random_roll <=50:
                player.magic_def -=1
                text = "you feel fuzzy"
            elif random_roll <=55:
                player.hit +=1
                text = "you feel focused"
            elif random_roll <=60:
                player.hit -=1
                text = "you see double"
            elif random_roll <=65:
                player.dodge +=1
                text = "you feel focused"
            elif random_roll <=70:
                player.dodge -=1
                text = "you feel wobbly"
            elif random_roll <=75:
                player.charisma +=1
                text = "you feel in control"
            elif random_roll <=80:
                player.charisma -=1
                text = "you feel woozy"
            elif random_roll <=85:
                player.perception +=1
                text = "you feel focused"
            elif random_roll <=90:
                player.perception -=1
                text = "you see double"
            else:
                player.poison = True
                player.poison_timer = 20
                text = "you feel sick"
        elif item.name == 'Health Potion':
            player.healing = True
            player.healing_timer = player.charisma+random.randint(0,5)
            text = "you feel invigorated"
            
    if item.category == 'key':
        if item.name == 'Copper Key':
            key_used = False
            for i in treasure_group:
                if i.map_x == player.map_x and i.map_y == player.map_y:
                    if i.locked:
                        i.locked = False
                        key_used = True
                        text = "You unlock the chest"
                        break
                else:
                    text = "Nothing to unlock"
            if not key_used:
                door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
                door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]
                for x in door_locations_x:
                    for y in door_locations_y:
                        if not my_map[x/tile_width][y/tile_width].fire_door and not my_map[x/tile_width][y/tile_width].ice_door and not my_map[x/tile_width][y/tile_width].skull_door:
                            if my_map[x/tile_width][y/tile_width].locked:
                                my_map[x/tile_width][y/tile_width].locked = False
                                text = "You unlock the door"
                                key_used = True
                                break
                        else:
                            text = "the key does not fit"
            if not key_used:
                player.inventory.append([item])
        elif item.name == 'Flame Key':
            key_used = False
            
            if not key_used:
                door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
                door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]
                for x in door_locations_x:
                    for y in door_locations_y:
                        if my_map[x/tile_width][y/tile_width].fire_door:
                            if my_map[x/tile_width][y/tile_width].locked:
                                my_map[x/tile_width][y/tile_width].locked = False
                                text = "You unlock the door"
                                key_used = True
                                break
                            else:
                                text = "nothing to unlock"
                        else:
                            text = "key does not fit"
                                 
            if not key_used:
                player.inventory.append([item])
        elif item.name == 'Ice Key':
            key_used = False
            
            if not key_used:
                door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
                door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]
                for x in door_locations_x:
                    for y in door_locations_y:
                        if my_map[x/tile_width][y/tile_width].ice_door:
                            if my_map[x/tile_width][y/tile_width].locked:
                                my_map[x/tile_width][y/tile_width].locked = False
                                text = "You unlock the door"
                                key_used = True
                                break
                            else:
                                text = "nothing to unlock"
                        else:
                            text = "key does not fit"
                                 
            if not key_used:
                player.inventory.append([item])
                
        elif item.name == 'Skull Key':
            key_used = False
            
            if not key_used:
                door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
                door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]
                for x in door_locations_x:
                    for y in door_locations_y:
                        if my_map[x/tile_width][y/tile_width].skull_door:
                            if my_map[x/tile_width][y/tile_width].locked:
                                my_map[x/tile_width][y/tile_width].locked = False
                                text = "You unlock the door"
                                key_used = True
                                break
                            else:
                                text = "nothing to unlock"
                        else:
                            text = "key does not fit"
                                 
            if not key_used:
                player.inventory.append([item])
                    
        elif item.name == 'Lock Pick':
            lock_strength = random.randint(1,20)+monster_str
            key_used = False
            for i in treasure_group:
                if i.map_x == player.map_x and i.map_y == player.map_y:
                    if i.locked:
                        lock_strength = random.randint(1,20)+monster_str
                        chance = player.perception - lock_strength
                        if chance >0:
                            i.locked = False
                            key_used = True
                            text = "You unlock the chest"
                            player.xp+=15
                            break
                        else:
                            key_used = True
                            text = "The lockpick breaks"
                            break
                else:
                    text = "Nothing to unlock"
            if not key_used:
                door_locations_x = [player.map_x-100,player.map_x+100,player.map_x]
                door_locations_y = [player.map_y-100,player.map_y+100,player.map_y]
                for x in door_locations_x:
                    for y in door_locations_y:
                        if my_map[x/tile_width][y/tile_width].locked:
                            lock_strength = random.randint(1,20)+monster_str
                            chance = player.perception - lock_strength
                            if chance >0:
                                my_map[x/tile_width][y/tile_width].locked = False
                                key_used = True
                                text = "You unlock the door"
                                player.xp+=15
                                break
                            else:
                                key_used = True
                                text = "The lockpick breaks"
                                break
                            
                                
                    
            if not key_used:
                player.inventory.append([item])
                text = "Nothing to unlock"
            
    updateGUI(text,(10,10,10))

def examine_object(coord_x,coord_y):

    color = (10,10,150)
    text = "nothing of interest"
    for item in treasure_group:
        if coord_x == item.map_x and coord_y == item.map_y:
            text = "An unlooted %s " %item.name
            updateGUI(text,(color))
            
    for monster in monster_group:
        if coord_x == monster.map_x and coord_y == monster.map_y:
            text = "an agressive %s approaches" %monster.name
            updateGUI(text,(color))
            if (random.randint(1,10) + player.perception) - (random.randint(1,10) + monster.perception) >0:
                text = "it has %s hp" %monster.hp
            else:
                text = "Its strength is hard to define"
    
    for npc in npc_group:
        if coord_x == npc.map_x and coord_y == npc.map_y:
            text = "A friendly vendor"
            updateGUI(text,(color))
            if (random.randint(1,10) + player.perception) > (random.randint(1,10) + npc.perception):
                text = "he has %s charisma" %npc.charisma
            else:
                text = "further deatails are hard to define"
        

    if my_map[coord_x/tile_width][coord_y/tile_height].stairs_down:
        text = "Stairs leading down"
        updateGUI(text,(color))
        text = "into the dark and unknown"
        updateGUI(text,(color))
        
    elif my_map[coord_x/tile_width][coord_y/tile_height].stairs_up:
        text = "stairs leading up towards safety"
        updateGUI(text,(color))
        
    elif my_map[coord_x/tile_width][coord_y/tile_height].door:
        if my_map[coord_x/tile_width][coord_y/tile_height].door_open:
            text = "an open doorway"
        elif my_map[coord_x/tile_width][coord_y/tile_height].locked:
            text = "a locked door blocks your path"
        
        else:
            text = "a closed doorway"
        updateGUI(text,(color))
    
    else:
        
        updateGUI(text,(color))




def is_blocked(x,y): #used for walls monsters etc so they dont walk over eachother

    if my_map[x][y].blocked:
        return True
    if player.blocks and x == player.dest_x/tile_width and y == player.dest_y/tile_height :
        return True
    for monster in monster_group:
        if monster.blocks and monster.dest_x/tile_width == x and monster.dest_y/tile_height == y:
            return True
    for npc in npc_group:
        if npc.blocks and npc.dest_x/tile_width == x and npc.dest_y/tile_height == y:
            return True
    for spawner in spawner_group:
        if spawner.blocks and spawner.map_x/tile_width == x and spawner.map_y/tile_height == y:
            return True
    return False

def is_semi_blocked(x,y): #used for placing items so they dont pile up but can still be walked over
    if my_map[x][y].blocked:
        return True
    if player.blocks and x == player.dest_x/tile_width and y == player.dest_y/tile_height :
        return True
    for monster in monster_group:
        if monster.blocks and monster.dest_x/tile_width == x and monster.dest_y/tile_height == y:
            return True
    for treasure in treasure_group:
        if treasure.blocks and treasure.map_x/tile_width == x and treasure.map_y/tile_height == y:
            return True

    return False


def generate_item():

    random_roll = random.randint(1,100)
    if random_roll <= 5:
        item = Item('Health Scroll','scroll',20,scroll_img,0.2)

    elif random_roll <= 10:
        item = Item('Poison Scroll','scroll',30,scroll_img,0.2)
        
    elif random_roll <= 15:
        item = Item('Fire Scroll','scroll',20,scroll_img,0.2)

    elif random_roll <= 20:
        item = Item('Ice Scroll','scroll',20,scroll_img,0.2)
        
    elif random_roll <= 25:
        item = Item('Thunder Scroll','scroll',20,scroll_img,0.2)
        
    elif random_roll <= 30:
        item = Item('Summon Scroll','scroll',30,scroll_img,0.2)
        
    elif random_roll <= 33:
        item = Item('Tame Scroll','scroll',30,scroll_img,0.2)
        
    elif random_roll <=35:
        item = Item('Identity Scroll','scroll',50,scroll_img,0.2)

    elif random_roll <= 40:
        item = Item('Copper Key','key',1,key_img,0.2)
        
    elif random_roll <=50:
        item = Item('Lock Pick','key',1,key_img,0.1)
        
    elif random_roll <=52:
        item = Item('Teleport Scroll','scroll',40,scroll_img,0.2)
        
    elif random_roll <= 60:
        item = Item('Anti Venom','potion',20,potion_img,0.3)
    
    elif random_roll <= 70:
        item = Item('Health Potion','potion',20,potion_img,0.3)
        
    elif random_roll <= 75:
        item = Item('Mystery Potion','potion',20,potion_img,0.3)
     
    elif random_roll <= 80:
        item = Item('Throwing Knife','ranged',2,ranged_img,0.1)
        
    elif random_roll <= 90:
        if random.randint(1,10)<=6:
            item = Item('Bread','food',10,bread_img,0.5)
        else:
            item = Item('Mouldy Bread','food',2,bread_img,0.5)
    
    else:
        item = Item('Linen Bandage','bandage',10,scroll_img,0.2)
    return item



def generate_equipment(cat=None):#generate an item at rect with category

    if cat == None:
        cat_roll = random.randint(1,8)
        if cat_roll == 1:
            cat = 'wep'
        elif cat_roll == 2:
            cat = 'arm'
        elif cat_roll == 3:
            cat = 'off hand'
        elif cat_roll == 4:
            cat = 'helm'
        elif cat_roll == 5:
            cat = 'gloves'
        elif cat_roll == 6:
            cat = 'r_ring'
        elif cat_roll == 7:
            cat = 'chain'
        else:
            cat = 'boots'
    
    material_roll = random.randint(1,10)
    if monster_str <=3:
        if material_roll <= 9-monster_str:
            m_name_2 = "Bronze"
            w_name_2 = "Yew"
            l_name_2 = "Hide"
            c_name_2 = "Hemp"
            p_name_2 = "Copper"
            min_quality = 1
        else:
            m_name_2 = "Iron"
            w_name_2 = "Heartwood"
            l_name_2 = "leather"
            c_name_2 = "Cotten"
            p_name_2 = "Silver"
            min_quality = 2
    elif monster_str <= 6:
        
        if material_roll <= 5:
            m_name_2 = "Bronze"
            w_name_2 = "Yew"
            l_name_2 = "Hide"
            c_name_2 = "Hemp"
            p_name_2 = "Copper"
            min_quality = 1
        elif material_roll <=9:
            m_name_2 = "Iron"
            w_name_2 = "Heartwood"
            l_name_2 = "leather"
            c_name_2 = "Cotton"
            p_name_2 = "Silver"
            min_quality = 2
        else:
            m_name_2 = "Steel"
            w_name_2 = "DarkWood"
            l_name_2 = "Leather"
            c_name_2 = "Silk"
            p_name_2 = "Gold"
            min_quality = 3
            
    else:
        
        if material_roll <= 3:
            m_name_2 = "Bronze"
            w_name_2 = "Yew"
            l_name_2 = "Hide"
            c_name_2 = "Hemp"
            p_name_2 = "Copper"
            min_quality = 1+monster_str+player.level
        elif material_roll <=7:
            m_name_2 = "Iron"
            w_name_2 = "Heartwood"
            l_name_2 = "leather"
            c_name_2 = "Cotton"
            p_name_2 = "Silver"
            min_quality = 2+monster_str+player.level
        else:
            m_name_2 = "Steel"
            w_name_2 = "DarkWood"
            l_name_2 = "Boiled Leather"
            c_name_2 = "Silk"
            p_name_2 = "Gold"
            min_quality = 3+monster_str+player.level
    
           
    quality_roll = random.randint(1,10)
    if monster_str <=3:
        if quality_roll<=9:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Ruined"
        else:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Common"
    elif monster_str <=6:
        if quality_roll <= 4:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Ruined"
        elif quality_roll <= 9:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Common"
        else:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Fine"
    elif monster_str <=12:
        if quality_roll <= 1:
            max_quality = min_quality+1
            name_1 = "Ruined"
        elif quality_roll <= 5:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Common"
        else:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Fine"
    else:
        if quality_roll <= 1:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Ruined"
        elif quality_roll <= 5:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Common"
        else:
            max_quality = min_quality+monster_str+player.level
            name_1 = "Fine"
    print max_quality
    

    item_type = cat

    if item_type == 'wep':
        kind = 'weapon'
        #weapon_list = 1=sword 2=spear 3=axe 4=dagger 5=club 6=staff
        weapon_type = random.randint(1,6)
        if weapon_type == 1:

            name = "Sword"
            p_img = sword_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(0,0)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,2)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif weapon_type == 2:
            name = 'Spear'
            p_img = spear_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(min_quality+1,max_quality+2)
            fire = random.randint(0,0)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

           
       
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif weapon_type == 3:
            name = "Axe"
            p_img = axe_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

            
 
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif weapon_type == 4:
            name = "Dagger"
            p_img = dagger_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(0,0)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-4,1)

           
    
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif weapon_type == 5:
            name = "Club"
            p_img = club_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(0,4)

            

            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif weapon_type == 6:
            name = "Staff"
            p_img = staff_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(1,4)
            stab = random.randint(0,0)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(-4,1)

            
  
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,w_name_2)
            
        else:
            print "WTF"

    if item_type == 'arm':

        kind = 'armour'
        armour_type = random.randint(1,4)
        if armour_type == 1:
            name = "Robe"
            p_img = robe_idle
            inv_img = equipment_torso_img
            slash = random.randint(0,3)
            smash = random.randint(0,3)
            stab = random.randint(0,3)
            fire = random.randint(min_quality+1,max_quality+2)
            ice = random.randint(min_quality+1,max_quality+2)
            thunder = random.randint(min_quality+1,max_quality+2)
            dark = random.randint(-2,2)

            
  
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,c_name_2)

        elif armour_type == 2:
            name = 'Jerkin'
            p_img = leather_idle
            inv_img = equipment_torso_img
            slash = random.randint(min_quality-1,max_quality-1)
            smash = random.randint(min_quality-1,max_quality-1)
            stab = random.randint(min_quality-1,max_quality-1)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(-1,1)

           
 
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,l_name_2)

        elif armour_type == 3:
            name = 'Mail'
            p_img = mail_idle
            inv_img = equipment_torso_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(min_quality-1,max_quality-1)
            ice = random.randint(min_quality-1,max_quality-1)
            thunder = random.randint(min_quality-1,max_quality-1)
            dark = random.randint(-1,1)

            
 
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif armour_type == 4:
            name = 'Platemail'
            p_img = plate_idle
            inv_img = equipment_torso_img
            slash = random.randint(min_quality+2,max_quality+2)
            smash = random.randint(min_quality+2,max_quality+2)
            stab = random.randint(min_quality+2,max_quality+2)
            fire = random.randint(0,4)
            ice = random.randint(0,4)
            thunder = random.randint(0,4)
            dark = random.randint(-1,1)

            

            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        else:
            print 'WTF'

    if item_type == 'helm':
        kind = 'helm'
        helm_type = random.randint(1,4)

        if helm_type == 1:
            name = 'Plate Helm'
            p_img = plate_helm_idle
            inv_img = equipment_hat_img
            slash = random.randint(min_quality+2,max_quality+2)
            smash = random.randint(min_quality+2,max_quality+2)
            stab = random.randint(min_quality+2,max_quality+2)
            fire = random.randint(0,2)
            ice = random.randint(0,2)
            thunder = random.randint(0,2)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

        elif helm_type == 2:
            name = 'Hood'
            p_img = hood_idle
            inv_img = equipment_hat_img
            slash = random.randint(0,2)
            smash = random.randint(0,2)
            stab = random.randint(0,2)
            fire = random.randint(min_quality+2,max_quality+2)
            ice = random.randint(min_quality+2,max_quality+2)
            thunder = random.randint(min_quality+2,max_quality+2)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,c_name_2)
        

        elif helm_type == 3:
            name = 'Hat'
            p_img = hat_idle
            inv_img = equipment_hat_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(min_quality+1,max_quality+1)
            ice = random.randint(min_quality+1,max_quality+1)
            thunder = random.randint(min_quality+1,max_quality+1)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,l_name_2)
         

        elif helm_type == 4:
            name = "Mail Helm"
            p_img = mail_helm_idle
            inv_img = equipment_hat_img
            slash = random.randint(min_quality+1,max_quality+1)
            smash = random.randint(min_quality+1,max_quality+1)
            stab = random.randint(min_quality+1,max_quality+1)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)
          

    if item_type == 'off hand':
        kind = 'off hand'
        off_hand_type = random.randint(1,4)

        if off_hand_type == 1:
            name = "Shield"
            p_img = shield_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)
          

        elif off_hand_type == 2:
            name = "Relic"
            p_img = relic_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(1,4)

            
      
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,p_name_2)

        elif off_hand_type == 3:
            name = "Totem"#generate_name('metal helm',tier)
            p_img = totem_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(-4,-1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,p_name_2)
      

        elif off_hand_type == 4:
            name = "Offhand weapon"#generate_name('metal helm',tier)
            p_img = knife_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = 0#random.randint(0,0)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

            
        
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)
    
    if item_type == 'gloves':
        kind = 'gloves'
        glove_type = random.randint(1,2)
        if glove_type == 1:
            name = "leather gloves"#generate_name('metal helm',tier)
            p_img = gloves_idle
            inv_img = equipment_wep_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(min_quality,max_quality)
            ice = random.randint(min_quality,max_quality)
            thunder = random.randint(min_quality,max_quality)
            dark = random.randint(-1,1)

            
            weight = random.randint(1,3)
            description = "A %s %s made from %s"%(name_1,name,l_name_2)
            
        elif glove_type == 2:
            name = "Guantlets"#generate_name('metal helm',tier)
            p_img = guantlet_idle
            inv_img = equipment_wep_img
            slash = random.randint(min_quality,max_quality)
            smash = random.randint(min_quality,max_quality)
            stab = random.randint(min_quality,max_quality)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)

    if item_type == 'r_ring':
        kind = 'r_ring'
        
        name = "Ring"#generate_name('metal helm',tier)
        p_img = [None]
        inv_img = equipment_wep_img
        slash = random.randint(0,0)
        smash = random.randint(0,0)
        stab = random.randint(0,0)
        fire = random.randint(min_quality,max_quality)
        ice = random.randint(min_quality,max_quality)
        thunder = random.randint(min_quality,max_quality)
        dark = random.randint(-1,1)

        
        
        weight = 0.4
        description = "A %s %s made from %s"%(name_1,name,p_name_2)
        
    if item_type == 'chain':
        kind = 'chain'
        name = "Chain"#generate_name('metal helm',tier)
        p_img = [None]
        inv_img = equipment_wep_img
        slash = random.randint(0,0)
        smash = random.randint(0,0)
        stab = random.randint(0,0)
        fire = random.randint(min_quality,max_quality)
        ice = random.randint(min_quality,max_quality)
        thunder = random.randint(min_quality,max_quality)
        dark = random.randint(-1,1)

        
        
        weight = 0.6
        description = "A %s %s made from %s"%(name_1,name,p_name_2)
        

    if item_type == 'boots':
        kind = 'boots'
        boot_type = random.randint(1,3)
        if boot_type == 1:
            name = "Leather Boots"#generate_name('metal helm',tier)
            p_img = [leather_boots_img]
            inv_img = equipment_wep_img
            slash = random.randint(0,1)
            smash = random.randint(0,1)
            stab = random.randint(0,1)
            fire = random.randint(min_quality+1,max_quality+1)
            ice = random.randint(min_quality+1,max_quality+1)
            thunder = random.randint(min_quality+1,max_quality+1)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(2,5)
            description = "A %s %s made from %s"%(name_1,name,l_name_2)
            
        elif boot_type == 2:
            name = "Mail Boots"#generate_name('metal helm',tier)
            p_img = [mail_boots_img]
            inv_img = equipment_wep_img
            slash = random.randint(min_quality-1,max_quality-1)
            smash = random.randint(min_quality-1,max_quality-1)
            stab = random.randint(min_quality-1,max_quality-1)
            fire = random.randint(min_quality-1,max_quality-1)
            ice = random.randint(min_quality-1,max_quality-1)
            thunder = random.randint(min_quality-1,max_quality-1)
            dark = random.randint(-1,1)
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)
            
        elif boot_type == 3:
            name = "Plate Boots"#generate_name('metal helm',tier)
            p_img = [plate_boots_img]
            inv_img = equipment_wep_img
            slash = random.randint(min_quality+1,max_quality+1)
            smash = random.randint(min_quality+1,max_quality+1)
            stab = random.randint(min_quality+1,max_quality+1)
            fire = random.randint(0,1)
            ice = random.randint(0,1)
            thunder = random.randint(0,1)
            dark = random.randint(-1,1)

            
            
            weight = random.randint(5,7)
            description = "A %s %s made from %s"%(name_1,name,m_name_2)
        

    item = Equipment(name,p_img,inv_img,slash,smash,stab,fire,ice,thunder,dark,kind,weight,100,description)
    return item

def create_epic_equipment():
    equipment_roll = random.randint(1,100)
    if equipment_roll <=15:
        item = Equipment('sword of sages',sword_idle,equipment_wep_img,10+monster_str,0,10+monster_str,0,0,0,10+monster_str,'weapon',8,100,"an Ancient sword wielded by warrior monks")
    elif equipment_roll <= 40:
        item = Equipment('thunder hat',[leather_helm_img],equipment_hat_img,10,10,10,0,0,10+monster_str,2,'helm',8,100,"Hat of the lightning god")
    elif equipment_roll <= 60:
        item = Equipment('lightning rod',staff_idle,equipment_wep_img,10,10,10,0,0,10+monster_str,2,'weapon',8,100,"staff of the lightning god")
    else:
        item = Equipment('thunder boots',[mail_boots_img],equipment_torso_img,10,10,10,0,0,10+monster_str,2,'boots',8,100,"boots of the lightning god")
    return item

def create_rat_room(room):
    
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 100:
            name = 'rat'
            img = rat_idle
            attack = 3+monster_str
            defence = 2+monster_str
            m_attk = 0
            m_def = 0
            hit = 4+monster_str
            dodge = 6+monster_str
            hp = 10+monster_str
            char = 0
            per = 5+monster_str
            xp = 10+monster_str
            weapon = Equipment('teeth',[None],equipment_wep_img,0,0,(2+monster_str),0,0,0,0,'wep',0,100,'teeth')
            armour = Equipment('fur',[None],equipment_wep_img,0,0,0,(-7-monster_str),0,0,0,'wep',0,100,'fur')
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            contains = []
            item_stack = []
            for i in range(num_found):
                if random.randint(1,10)<=6:
                    
                
                
                    item = generate_item()
                    item_stack.append(item)
                
                
                
            if len(item_stack)!=0:
                contains.append(item_stack)
            else:
                break
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        else:
            print "other monster types required"
            
        
def create_mixed_room(room):
    web_sacs = 0
    
    for i in range(max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 30:
            name = 'skeleton'
            img = [skeleton_img]
            attack = 6+monster_str
            defence = 5+monster_str
            m_attk = 0
            m_def = 0
            hit = 8+monster_str
            dodge = 6+monster_str
            hp = 26+monster_str
            char = 0
            per = 5+monster_str
            xp = 20+monster_str
            weapon = Equipment('bones spear',[None],equipment_wep_img,(0),(0),(8+monster_str),0,0,0,(-5-monster_str),'wep',0,100,'bones')
            armour = Equipment('bones',[None],equipment_wep_img,(5+monster_str),(-4-monster_str),(8+monster_str),0,(7+monster_str),0,(-5-monster_str),'armour',0,100,'bones')
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            amount_coin = random.randint(0,4)
            contains = []
            item_stack = []
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_num = random.randint(1,100)
                if random_num<=20:
                    item = generate_item()
                    item_stack.append(item)
                else:
                    pass
                
                
            if len(item_stack)!=0:
                contains.append(item_stack)
           
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
            
        elif random_roll <= 40:
            name = 'lych'
            img = [lych_img]
            attack = 1+monster_str
            defence = 2+monster_str
            m_attk = 7+monster_str
            m_def = 4+monster_str
            hit = 8+monster_str
            dodge = 6+monster_str
            hp = 36+monster_str
            char = 10+monster_str
            per = 5+monster_str
            xp = 20+monster_str
            weapon = Equipment('wand',[None],equipment_wep_img,0,4+monster_str,0,0,(7+monster_str),(7+monster_str),(7+monster_str),'wep',0,100,'bones')
            armour = Equipment('bones',[None],equipment_wep_img,(5+monster_str),(-4-monster_str),(8+monster_str),0,(7+monster_str),0,(-5-monster_str),'armour',0,100,'bones')
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            contains = []
            item_stack = []
            amount_coin = random.randint(5,9)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                
                
                item = generate_item()
                item_stack.append(item)
                
                
                
            if len(item_stack)!=0:
                contains.append(item_stack)
            
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
                    
        elif random_roll <= 60:
            name = 'goblin'
            img = goblin_idle
            attack = 6+monster_str
            defence = 5+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 25+monster_str
            char = 2+monster_str
            per = 15+monster_str
            
            xp = 30+monster_str
            weapon = Equipment('dagger',[None],equipment_wep_img,4+monster_str,0,6+monster_str,0,0,0,0,'weapon',5,100,'')
            armour = Equipment('leather rags',[None],equipment_wep_img,1+monster_str,1+monster_str,1+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=9:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
                    
                    
        elif random_roll <= 65:
            name = 'shaman'
            img = shaman_idle
            attack = 4+monster_str
            defence = 8+monster_str
            m_attk = 8+monster_str
            m_def = 8+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 20+monster_str
            char = 12+monster_str
            per = 17+monster_str
            
            xp = 50+monster_str
            weapon = Equipment('staff',[None],equipment_wep_img,0,4+monster_str,0,5+monster_str,5+monster_str,5+monster_str,5+monster_str,'weapon',5,100,'')
            armour = Equipment('leather rags',[None],equipment_wep_img,1+monster_str,1+monster_str,1+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(3,9)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=9:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
                    
        elif random_roll <= 75:
            name = 'orc'
            img = [orc_img]
            attack = 6+monster_str
            defence = 10+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 60+monster_str
            char = 8+monster_str
            per = 15+monster_str
            
            xp = 50
            weapon = Equipment('sword',[None],equipment_wep_img,8+monster_str,0,6+monster_str,0,0,0,0,'weapon',5,100,'')
            armour = Equipment('orc_armour',[None],equipment_wep_img,6+monster_str,6+monster_str,6+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Gold Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=9:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)

        elif random_roll <= 85:
            random_num = random.randint(1,100)
            if random_num <= 50:
                name = 'Spinner'
                img = spider_idle
                attack = 8+monster_str
                defence = 10+monster_str
                m_attk = 0
                m_def = 4+monster_str
                hit = 6+monster_str
                dodge = 3+monster_str
                hp = 30+monster_str
                char = 0
                per = 0
                weapon = Equipment('fang',[None],equipment_wep_img,0,0,5+monster_str,0,0,0,0,'dagger',5,100,'')
                armour = Equipment('carapace',[None],equipment_wep_img,2+monster_str,0,2+monster_str,0,4+monster_str,4+monster_str,0,'arm',5,100,'')
                xp = 60
                
                x = random.randint(room.x1+1,room.x2-1)
                y = random.randint(room.y1+1,room.y2-1)
            
                num_found = random.randint(1,5)
                contains = []
                item_stack = []
                for i in range(num_found):
                    item = generate_item()
                    
                    item_stack.append(item)
                contains.append(item_stack)
            
                if not is_blocked(x,y):
                    if not my_map[x][y].stairs_down:
                        monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                        monster_group.add(monster)
                        all_group.add(monster)
                        
            elif random_roll <= 60:
                x = random.randint(room.x1+1,room.x2-1)
                y = random.randint(room.y1+1,room.y2-1)
                if not is_blocked(x,y):
                    if not my_map[x][y].stairs_down:
                        web = Trap(x,y,web_img,'web',3)
                        trap_group.add(web)
                
            else:
                if web_sacs <=3:
                    x = random.randint(room.x1+1,room.x2-1)
                    y = random.randint(room.y1+1,room.y2-1)
                    if not is_blocked(x,y):
                        if not my_map[x][y].stairs_down:
                            web_sac = Spawner(x*tile_width,y*tile_height,web_sac_img,'Egg Sac',40)
                            spawner_group.add(web_sac)
                            all_group.add(web_sac)
                        
        else:   
            name = 'demon'
            img = demon_idle
            attack = 6+monster_str
            defence = 10+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 130+monster_str
            char = 8+monster_str
            per = 15+monster_str
            
            xp = 150
            weapon = Equipment('demon_sword',[None],equipment_wep_img,8+monster_str,0,6+monster_str,6+monster_str,0,0,0,'weapon',5,100,'')
            armour = Equipment('demon_skin',[None],equipment_wep_img,6+monster_str,6+monster_str,6+monster_str,20+monster_str,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(6,12)
            for i in range (amount_coin):
                coin = Item('Gold Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=5:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)

def create_undead_room(room):
    
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 80:
            name = 'skeleton'
            img = [skeleton_img]
            attack = 8+monster_str
            defence = 6+monster_str
            m_attk = 0
            m_def = 0
            hit = 8+monster_str
            dodge = 6+monster_str
            hp = 26+monster_str
            char = 0
            per = 5+monster_str
            xp = 20+monster_str
            weapon = no_equipment
            armour = Equipment('bones',[None],equipment_wep_img,(5+monster_str),(-4-monster_str),(8+monster_str),0,(7+monster_str),0,(-5-monster_str),'armour',0,100,'bones')
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_num = random.randint(1,100)
                if random_num<=20:
                    item = generate_item()
                    item_stack.append(item)
                else:
                    pass
                
                
            if len(item_stack)!=0:
                contains.append(item_stack)
            else:
                break
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        else:
            
            name = 'lych'
            img = [lych_img]
            attack = 1+monster_str
            defence = 2+monster_str
            m_attk = 7+monster_str
            m_def = 4+monster_str
            hit = 8+monster_str
            dodge = 6+monster_str
            hp = 50+monster_str
            char = 10+monster_str
            per = 5+monster_str
            xp = 20+monster_str
            weapon = Equipment('wand',[None],equipment_wep_img,0,4+monster_str,0,0,(7+monster_str),(7+monster_str),(7+monster_str),'wep',0,100,'bones')
            armour = Equipment('bones',[None],equipment_wep_img,(5+monster_str),(-4-monster_str),(8+monster_str),0,(7+monster_str),0,(-5-monster_str),'armour',0,100,'bones')
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            contains = []
            item_stack = []
            amount_coin = random.randint(5,7)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                
                
                item = generate_item()
                item_stack.append(item)
                
                
                
            if len(item_stack)!=0:
                contains.append(item_stack)
            else:
                break
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
            
        
        
def create_goblin_room(room):
    
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 80:
            name = 'goblin'
            img = goblin_idle
            attack = 4+monster_str
            defence = 3+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 20+monster_str
            char = 4+monster_str
            per = 15+monster_str
            
            xp = 30+monster_str
            weapon = Equipment('dagger',[None],equipment_wep_img,1+monster_str,0,2+monster_str,0,0,0,0,'weapon',5,100,'')
            armour = Equipment('leather rags',[None],equipment_wep_img,1+monster_str,1+monster_str,1+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            amount_coin = random.randint(1,9)
            contains = []
            item_stack = []
            for i in range (amount_coin):
                coin = Item('Copper Coin','currency',1,copper_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=6:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        else:
            name = 'shaman'
            img = shaman_idle
            attack = 4+monster_str
            defence = 3+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 15+monster_str
            char = 7+monster_str
            per = 7+monster_str
            
            xp = 50+monster_str
            weapon = Equipment('staff',[None],equipment_wep_img,0,4+monster_str,0,3+monster_str,2+monster_str,2+monster_str,1+monster_str,'weapon',5,100,'')
            armour = Equipment('leather rags',[None],equipment_wep_img,1+monster_str,1+monster_str,1+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            amount_coin = random.randint(4,12)
            contains = []
            item_stack = []
            for i in range (amount_coin):
                coin = Item('Copper Coin','currency',1,copper_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=7:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        
        
        
def create_demon_room(room):
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 80:
            name = 'demon'
            img = demon_idle
            attack = 10+monster_str
            defence = 10+monster_str
            m_attk = 7+monster_str
            m_def = 7+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 130+monster_str
            char = 8+monster_str
            per = 15+monster_str
            
            xp = 150
            weapon = Equipment('demon_sword',[None],equipment_wep_img,8+monster_str,0,6+monster_str,6+monster_str,0,0,0,'weapon',5,100,'')
            armour = Equipment('demon_skin',[None],equipment_wep_img,6+monster_str,6+monster_str,6+monster_str,20+monster_str,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Gold Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=5:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
    
def create_orc_room(room):
    
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 80:
            name = 'orc'
            img = [orc_img]
            attack = 5+monster_str
            defence = 4+monster_str
            m_attk = 3+monster_str
            m_def = 3+monster_str
            hit = 6+monster_str
            dodge = 4+monster_str
            hp = 40+monster_str
            char = 8+monster_str
            per = 15+monster_str
            
            xp = 50
            weapon = Equipment('sword',[None],equipment_wep_img,8+monster_str,0,6+monster_str,0,0,0,0,'weapon',5,100,'')
            armour = Equipment('orc_armour',[None],equipment_wep_img,6+monster_str,6+monster_str,6+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,3)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=5:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        else:
            name = 'troll'
            img = [troll_img]
            attack = 4+monster_str
            defence = 8+monster_str
            m_attk = 8+monster_str
            m_def = 8+monster_str
            hit = 6+monster_str
            dodge = 0+monster_str
            hp = 70+monster_str
            char = 10+monster_str
            per = 17+monster_str
            
            xp = 150
            weapon = Equipment('club',[None],equipment_wep_img,0,14+monster_str,0,0,0,0,0,'weapon',5,100,'')
            armour = Equipment('leather rags',[None],equipment_wep_img,9+monster_str,9+monster_str,9+monster_str,0,1+monster_str,1+monster_str,1+monster_str,'armour',5,100,'')
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            amount_coin = random.randint(1,5)
            for i in range (amount_coin):
                coin = Item('Gold Coin','currency',20,silver_coin_img,0.1)
                item_stack.append(coin)
            for i in range(num_found):
                random_item = random.randint(1,10)
                if random_item <=9:
                    item = generate_item()
                else:
                    if random.randint(1,2)<=1:
                        item=generate_equipment('wep')
                    else:
                        item=generate_equipment('arm')
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
        
        
        
        
def create_final_boss(room):
    name = 'Spider Queen'
    img = [spider_queen_img]
    attack = 15+monster_str
    defence = 15+monster_str
    m_attk = 0
    m_def = 14+monster_str
    hit = 10+monster_str
    dodge = 3+monster_str
    hp = 100+monster_str
    char = 100
    per = 0
    weapon = Equipment('fang',dagger_idle,equipment_wep_img,0,0,25,0,0,0,0,'weapon',5,200,'Fang of the spider queen')
    armour = no_equipment
    xp = 70
    
    x = room.x2/2#random.randint(room.x1+1,room.x2-1)
    y = room.y1+10#random.randint(room.y1+1,room.y2-1)

    num_found = random.randint(1,5)
    contains = []
    item_stack = []
    item_stack.append(weapon)
    for i in range(num_found):
        item = generate_item()
        
        item_stack.append(item)
    contains.append(item_stack)
    
    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
    monster_group.add(monster)
    all_group.add(monster)
    
                        
    
def create_spider_room(room):
    
    bosses = 0
    web_sacs = 0
    
    for i in range(0,max_monsters):
        random_roll = random.randint(1,100)
        if random_roll <= 50:
            name = 'Spinner'
            img = spider_idle
            attack = 6+monster_str
            defence = 8+monster_str
            m_attk = 0
            m_def = 4+monster_str
            hit = 6+monster_str
            dodge = 3+monster_str
            hp = 40+monster_str
            char = 0
            per = 0
            weapon = Equipment('fang',[None],equipment_wep_img,0,0,5+monster_str,0,0,0,0,'dagger',5,100,'')
            armour = Equipment('carapace',[None],equipment_wep_img,2+monster_str,0,2+monster_str,0,4+monster_str,4+monster_str,0,'arm',5,100,'')
            xp = 60
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
            for i in range(num_found):
                item = generate_item()
                
                item_stack.append(item)
            contains.append(item_stack)
        
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                    monster_group.add(monster)
                    all_group.add(monster)
                    
        elif random_roll <= 60:
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    web = Trap(x,y,web_img,'web',3)
                    trap_group.add(web)
            
        elif random_roll <= 99:
            if web_sacs <=3:
                x = random.randint(room.x1+1,room.x2-1)
                y = random.randint(room.y1+1,room.y2-1)
                if not is_blocked(x,y):
                    if not my_map[x][y].stairs_down:
                        web_sac = Spawner(x*tile_width,y*tile_height,web_sac_img,'Egg Sac',40)
                        spawner_group.add(web_sac)
                        all_group.add(web_sac)
                    
            
        else:
            if bosses == 0:
                print "spider queen"
                name = 'Spider Queen'
                img = [spider_queen_img]
                attack = 15+monster_str
                defence = 15+monster_str
                m_attk = 0
                m_def = 14+monster_str
                hit = 10+monster_str
                dodge = 3+monster_str
                hp = 100+monster_str
                char = 0
                per = 0
                weapon = Equipment('fang',dagger_idle,equipment_wep_img,0,0,15,0,0,0,0,'weapon',5,200,'Fang of the spider queen')
                armour = Equipment('carapace',[None],equipment_wep_img,4+monster_str,0,6+monster_str,0,6+monster_str,5+monster_str,0,'arm',5,100,'')
                xp = 70
                
                x = random.randint(room.x1+1,room.x2-1)
                y = random.randint(room.y1+1,room.y2-1)
            
                num_found = random.randint(1,5)
                contains = []
                item_stack = []
                item_stack.append(weapon)
                for i in range(num_found):
                    item = generate_item()
                    
                    item_stack.append(item)
                contains.append(item_stack)
                if not is_blocked(x,y):
                    if not my_map[x][y].stairs_down:
                        monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,contains,xp)
                        monster_group.add(monster)
                        all_group.add(monster)
                        bosses +=1
            else:
                pass
        
    

def create_npc_room(room):
    
    max_npc = 2
    total_npc = 0
    
    
        
        
    for i in range(max_npc):
        random_char = random.randint(14,30)
        random_per = random.randint(10,15)
        max_inv = 10
        amount_copper = random.randint(10,30)
        amount_silver = random.randint(10,30)
        amount_gold = random.randint(10,30)
        inventory = []
        for i in range(amount_copper):
            coin = Item('Copper Coin','currency',1,copper_coin_img,0.1)
            inventory.append([coin])
        for i in range(amount_silver):
            coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
            inventory.append([coin])
        for i in range(amount_gold):
            coin = Item('Gold Coin','currency',50,gold_coin_img,0.1)
            inventory.append([coin])
        
        for i in range (max_inv):
            random_num = random.randint(1,15)
            if random_num <=8:
                item = generate_equipment()
            
            else:
                item = generate_item()
            inventory.append([item])


        armour = Equipment('Common Clothes',[None],equipment_wep_img,7,3,3,3,3,3,3,3,'armour',5,'')
        x = random.randint(room.x1+1,room.x2-2)
        y = random.randint(room.y1+1,room.y2-2)

        if not is_blocked(x,y):
            if not my_map[x][y].stairs_down:
                npc = Character(x,y,'Vendor',player_idle,3,3,1,1,3,2,30,random_char,random_per,no_equipment,armour,inventory,0)
                npc.modify_stats()
                npc_group.add(npc)
                all_group.add(npc)
                
                total_npc +=1


def create_treasure_room(room):
    
    
    amount_items = random.randint(1,max_items)
    
    for i in range(amount_items):

        num_found = random.randint(1,8)
        contains = []
        amount_coins = random.randint(0,10)
        for i in range (amount_coins):
            coin = Item('Copper Coin','currency',1,copper_coin_img,0.1)
            contains.append([coin])
        for i in range(num_found):

            random_roll = random.randint(1,100)
            if random_roll <= 65:
                item = generate_item()

            

            else:
                item = generate_equipment()


        
            contains.append([item])

        if random.randint(1,100)<=5+monster_str:
            locked = True
        else:
            locked =False
                


        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not my_map[x][y].stairs_down:
                treasure = Treasure(x,y,treasure_img,contains,'Chest',locked)
                stack_inventory(treasure)
                #print "after sort", treasure.inventory
                #for i in treasure.inventory:
                #    print "#"
                #    for j in i:
                #        print j.name
                    
                treasure_group.add(treasure)
                

    
def place_objects(room):
    
    room = room
    if monster_str ==1:
        create_final_boss(room)
    elif monster_str <= 2:
        room_type = random.randint(1,100)
       
        if room_type <= 70:
            create_rat_room(room)
        
            
        elif room_type <= 90:
            create_goblin_room(room)
            
        elif room_type <= 98:
            create_treasure_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str == 3:
        room_type = random.randint(1,100)
        if room_type <= 30:
            create_rat_room(room)
        elif room_type <= 85:
            create_goblin_room(room)
        elif room_type <= 90:
            create_treasure_room(room)
        elif room_type <= 97:
            create_orc_room(room)
        
        
        else:
            create_npc_room(room)
            
    elif monster_str ==4:
        room_type = random.randint(1,100)
        if room_type <= 5:
            create_rat_room(room)
        elif room_type <= 50:
            create_goblin_room(room)
        elif room_type <= 85:
            create_orc_room(room)
        elif room_type <= 90:
            create_spider_room(room)

        elif room_type <= 95:
            create_treasure_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str == 5:
        room_type = random.randint(1,100)
        if room_type <= 1:
            create_rat_room(room)
        elif room_type <= 20:
            create_goblin_room(room)
        elif room_type <= 80:
            create_spider_room(room)
        elif room_type <= 85:
            create_treasure_room(room)
        elif room_type <= 95:
            create_mixed_room(room)
        else:
            create_npc_room(room)
    
    elif monster_str == 6:
        room_type = random.randint(1,100)
        if room_type <= 1:
            create_rat_room(room)
        elif room_type <= 5:
            create_goblin_room(room)
        elif room_type <= 50:
            create_spider_room(room)
        elif room_type <= 80:
            create_undead_room(room)
        elif room_type <= 85:
            create_treasure_room(room)
        elif room_type <= 95:
            create_mixed_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str == 7:
        room_type = random.randint(1,100)
        if room_type <= 1:
            create_rat_room(room)
        elif room_type <= 5:
            create_goblin_room(room)
        elif room_type <= 20:
            create_spider_room(room)
        elif room_type <= 70:
            create_undead_room(room)
        elif room_type <= 80:
            create_demon_room(room)
        elif room_type <= 85:
            create_treasure_room(room)
        elif room_type <= 95:
            create_mixed_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str == 8:
        room_type = random.randint(1,100)
        if room_type <= 1:
            create_rat_room(room)
        elif room_type <= 3:
            create_goblin_room(room)
        elif room_type <= 15:
            create_spider_room(room)
        elif room_type <= 40:
            create_undead_room(room)
        elif room_type <= 60:
            create_demon_room(room)
        elif room_type <= 65:
            create_treasure_room(room)
        elif room_type <= 95:
            create_mixed_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str >= 8:
        room_type = random.randint(1,100)
        
        if room_type <= 10:
            create_treasure_room(room)
        elif room_type <= 95:
            create_mixed_room(room)
        else:
            create_npc_room(room)

def create_building(block):
    global my_map

    for x in range(block.x1-1, block.x2+1):
        for y in range(block.y1-1,block.y2+1):
            my_map[x][y].blocked = True
            my_map[x][y].block_sight = True
            my_map[x][y].wall = True
    for x in range(block.x1, block.x2):
        for y in range(block.y1,block.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False
            my_map[x][y].wall = False
            
        
    
def create_room(room):
    global my_map
    for x in range(room.x1, room.x2):
        for y in range(room.y1,room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False
            my_map[x][y].wall = False

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

def create_exit(x,y):
    global my_map
    my_map[x][y].exit = True
    my_map[x][y].blocked = False
    my_map[x][y].block_sight = False

def load_new_level(state):
    global my_map
    global max_monsters
    global monster_str
    global dungeon_1
    print len(all_group)
    

    if state == 'death':
        global player
        global player_sprite
        
        max_monsters = 3
        monster_str = 1
        for a in all_group:
            a.kill()
        player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_idle,8,8,8,8,8,8,30,8,8,no_equipment,no_torso,[[silver_coin],[silver_coin],cash_bag,[bandage],[food],[pick]])
        player_sprite = pygame.sprite.RenderPlain((player))
        all_group.add(player)
        player.modify_stats()
        monster_group.empty()
        treasure_group.empty()
        effect_group.empty()
        
        
        
        npc_group.empty()
        trap_group.empty()
        spawner_group.empty()
        text = "loading new game"
        updateGUI(text,(10,10,10))
        
        make_village()

    elif state == 'teleport':
        pwr = random.randint(2,4)
        monster_group.empty()
        treasure_group.empty()
        
        npc_group.empty()
        trap_group.empty()
        spawner_group.empty()
        for a in all_group:
            if a.name != "Rahnook":
                a.kill()
        monster_str +=pwr
        max_monsters +=pwr
        make_dungeon()
        dungeon_1=my_map
    
    elif state == 'retreat':
        
        max_monsters -= 1
        if max_monsters <=1:
            max_monsters = 1

        monster_str -= 1
        if monster_str <= 1:
            monster_str = 1
        if monster_str == 1:
            my_map=village
            for y in range(tiles_y):
                for x in range(tiles_x):
                    if my_map[x][y].door:
                        my_map[x][y].door_open=False
                        my_map[x][y].blocked = True
                        my_map[x][y].block_sight = True
            find_player_start('up')
            player_copy = player
            monster_group.empty()
            treasure_group.empty()
            npc_group.empty()
            trap_group.empty()
            spawner_group.empty()
            
            for a in all_group:
                if a.name != "Rahnook":
                    a.kill()
            
            for i in village_objects:
                if i.name == 'Bag':
                    treasure_group.add(i)
                elif i.name == 'Spider Queen':
                    monster_group.add(i)
                else:
                    npc_group.add(i)
            if random.randint(1,10)>=6:
                special_rect = Rect(7,13,4,4)
                create_npc_room(special_rect)
                
            draw_map(tiles_x,tiles_y)
            
        else:
            monster_group.empty()
            treasure_group.empty()
            npc_group.empty()
            trap_group.empty()
            spawner_group.empty()
            for a in all_group:
                if a.name != "Rahnook":
                    a.kill()
            make_dungeon()
            
    else:
        max_monsters +=1
        monster_str += 1
        if max_monsters >=15:
            max_monsters = 15
        monster_group.empty()
        treasure_group.empty()
        npc_group.empty()
        trap_group.empty()
        spawner_group.empty()
        for a in all_group:
            if a.name != "Rahnook":
                a.kill()
        make_dungeon()
        dungeon_1=my_map
        

def find_player_start(direction):
    
    for y in range(tiles_y):
        for x in range(tiles_x):
            if direction == 'down':
                if my_map[x][y].stairs_up:
                    player.map_x = x * tile_width
                    player.map_y = y * tile_width
                    
            elif direction =='up':
                if my_map[x][y].stairs_down:
                    player.map_x = x * tile_width
                    player.map_y = y * tile_width
    player.dest_x = player.map_x
    player.dest_y = player.map_y
    player.current_x = player.map_x
    player.current_y = player.map_y
    
def make_village():
    
    (main_sq_w,main_sq_h)=25,25
    global my_map

    
    
    my_map = [[Tile(True)
                for y in range(tiles_y)]
                    for x in range(tiles_x)]
    
    
    #create main square
    w=main_sq_w-4
    h=main_sq_h-4
    x=3
    y=3
    main_square = Rect(x,y,w,h)
    create_room(main_square)
    (c_x,c_y) = main_square.center()
    

    player.map_x = c_x * tile_width
    player.map_y = c_y * tile_width
    player.dest_x = player.map_x
    player.dest_y = player.map_y
    player.current_x = player.map_x
    player.current_y = player.map_y
    
    buildings = []

    building1 = Rect(5,5,3,3)
    building2 = Rect(12,5,5,3)
    building3 = Rect(16,12,3,5)

    create_building(building1)
    my_map[building1.x1+2][building1.y2].door = True#create a door
    my_map[building1.x1+2][building1.y2].wall = False
    create_building(building2)
    my_map[building2.x1+2][building2.y2].door = True#create a door
    my_map[building2.x1+2][building2.y2].wall = False
    create_building(building3)
    my_map[building3.x1-1][building3.y1+3].door = True#create a door
    my_map[building3.x1-1][building3.y1+3].wall = False
    
    
    
    bread = Item('Bread','food',10,bread_img,0.5)
    m_bread = Item('Mouldy Bread','food',2,bread_img,0.5)
    potion_1 = Item('Anti Venom','potion',20,potion_img,0.3)
    potion_2 = Item('Health Potion','potion',20,potion_img,0.3)
    potion_3 = Item('Mystery Potion','potion',20,potion_img,0.3)
    bandage = Item('Linen Bandage','bandage',10,scroll_img,0.2)
    
    
    
    scrolls = []
    for i in range(15):
        health = Item('Health Scroll','scroll',20,scroll_img,0.2)
        scrolls.append(health)
        poison = Item('Poison Scroll','scroll',30,scroll_img,0.2)
        scrolls.append(poison)
        fire = Item('Fire Scroll','scroll',20,scroll_img,0.2)
        scrolls.append(fire)
        ice = Item('Ice Scroll','scroll',20,scroll_img,0.2)
        scrolls.append(ice)
        thun = Item('Thunder Scroll','scroll',20,scroll_img,0.2)
        scrolls.append(thun)
        summon= Item('Summon Scroll','scroll',30,scroll_img,0.2)
        scrolls.append(summon)
        tame = Item('Tame Scroll','scroll',30,scroll_img,0.2)
        scrolls.append(tame)
        identify = Item('Identity Scroll','scroll',50,scroll_img,0.2)
        scrolls.append(identify)
        

    
    knives = []
    for i in range(20):
        knife = Item('Throwing Knife','ranged',2,ranged_img,0.1)
        knives.append(knife)
    
    
   
    weapon_inv = []
    armour_inv = []
    bakery_inv = [[bread,bread,bread,bread,bread,m_bread,m_bread,potion_1,potion_2,potion_2,potion_3,bandage,bandage,bandage,]]
    magic_inventory = [scrolls]
    coin_inv = []
    epic_inv = []
   
    for i in range(4):
        weapon = generate_equipment('wep')
        weapon_inv.append([weapon])
    for i in range(4):
        weapon = generate_equipment('off hand')
        weapon_inv.append([weapon])
    for i in range(10):
        if random.randint(1,10) <=2:
            weapon = generate_equipment('arm')
        elif random.randint(1,10) <=5:
            weapon = generate_equipment('boots')
        elif random.randint(1,10) <=7:
            weapon = generate_equipment('helm')
        else:
            weapon = generate_equipment('gloves')
        armour_inv.append([weapon])
        
    for i in range(5):
        item = create_epic_equipment()
        epic_inv.append([item])
    
    
    for i in range(40,50):
        coin = Item('Copper Coin','currency',1,copper_coin_img,0.1)
        coin_inv.append(coin)
    for i in range(10,15):
        coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
        coin_inv.append(coin)
    for i in range(3,5):
        coin = Item('Gold Coin','currency',50,gold_coin_img,0.1)
        coin_inv.append(coin)
    bakery_inv.append(coin_inv)
    weapon_inv.append(coin_inv)
    armour_inv.append(coin_inv)
    weapon_inv.append(knives)
    magic_inventory.append(coin_inv)
    epic_inv.append(coin_inv)
    
    baker_npc = Character(6,6,'Baker',player_idle,3,3,1,1,3,2,30,13,8,no_equipment,no_equipment,bakery_inv,0)
    baker_npc.modify_stats()
    npc_group.add(baker_npc)
    all_group.add(baker_npc)
    weapon_npc = Character(13,6,'Weapon Smith',player_idle,3,3,1,1,3,2,30,17,8,no_equipment,no_equipment,weapon_inv,0)
    weapon_npc.modify_stats()
    npc_group.add(weapon_npc)
    all_group.add(weapon_npc)
    armour_npc = Character(15,6,'Weapon Smith',player_idle,3,3,1,1,3,2,30,17,8,no_equipment,no_equipment,armour_inv,0)
    armour_npc.modify_stats()
    npc_group.add(armour_npc)
    all_group.add(armour_npc)
    scribe_npc = Character(17,15,'Scribe',player_idle,3,3,1,1,3,2,30,17,8,no_equipment,no_equipment,magic_inventory,0)
    scribe_npc.modify_stats()
    npc_group.add(scribe_npc)
    all_group.add(scribe_npc)
    magister_npc = Character(17,12,'Magister',player_idle,3,3,1,1,3,2,30,37,8,no_equipment,no_equipment,epic_inv,0)
    magister_npc.modify_stats()
    npc_group.add(magister_npc)
    all_group.add(magister_npc)
    

        
    for i in npc_group:
        village_objects.append(i)
        i.current_x = i.dest_x
        i.current_y = i.dest_y
    
    my_map[7][19].stairs_down = True
    
    my_map[main_sq_w/2][main_sq_h-1].fire_door=True
    my_map[main_sq_w/2][main_sq_h-1].wall =False
    my_map[main_sq_w/2][main_sq_h-1].door=True
    my_map[main_sq_w/2][main_sq_h-1].locked=True
    
    first_corridoor = Rect(main_sq_w/2-1,main_sq_h,3,6)
    create_room(first_corridoor)
    
    my_map[main_sq_w/2][main_sq_h+6].ice_door=True
    my_map[main_sq_w/2][main_sq_h+6].wall =False
    my_map[main_sq_w/2][main_sq_h+6].door=True
    my_map[main_sq_w/2][main_sq_h+6].locked=True
    
    second_corridoor = Rect(main_sq_w/2-1,main_sq_h+7,3,6)
    create_room(second_corridoor)
    
    my_map[main_sq_w/2][main_sq_h+13].skull_door=True
    my_map[main_sq_w/2][main_sq_h+13].wall =False
    my_map[main_sq_w/2][main_sq_h+13].door=True
    my_map[main_sq_w/2][main_sq_h+13].locked=True
    
    boss_room = Rect(x,main_sq_h+14,main_sq_w-4,main_sq_h-4)
    create_room(boss_room)
    place_objects(boss_room)
    for i in monster_group:
        for m in monster_group:
            m.current_x = m.dest_x
            m.current_y = m.dest_y
        village_objects.append(i)
    
    draw_map(tiles_x,tiles_y)
    
    

def make_dungeon():

    #print "level %s" %monster_str
    monster_group.empty()
    treasure_group.empty()
    npc_group.empty()
    trap_group.empty()
    spawner_group.empty()
    

    global my_map
    
    
    max_features = random.randint(50,400)
    max_halls = 7
    halls = 0
    max_exits = 1
    exits = 0
    rooms = 0
    room_list = []
    features = []
    doors = []
    stairs_up = []
    stairs_down = []
    current_rooms = 0

    my_map = [[Tile(True)
                for y in range(tiles_y)]
                    for x in range(tiles_x)]
    #create first room
    w = random.randint(room_min_size,room_max_size)
    h = random.randint(room_min_size,room_max_size)
    x = random.randint(4, tiles_x - room_max_size - 4)
    y = random.randint(4, tiles_y - room_max_size - 4)
    first_room = Rect(x,y,w,h)
    create_room(first_room)
    (c_x,c_y) = first_room.center()
    c_y = y-1
    player.map_x = c_x * tile_width
    player.map_y = c_y * tile_width
    player.dest_x = player.map_x
    player.dest_y = player.map_y
    player.current_x = player.map_x
    player.current_y = player.map_y
    stair_up = Rect(c_x,c_y,1,1)
    stairs_up.append(stair_up)
    features.append(first_room)




    for i in range(max_features):
        #make a door on the previouse feature on a random wall
        prev_feature = random.choice(features)
        w = prev_feature.x2-prev_feature.x1
        h = prev_feature.y2-prev_feature.y1
        x = prev_feature.x1
        y = prev_feature.y1
        if prev_feature != first_room:
            r_wall = random.randint(1,4)
        else:
            r_wall = random.randint(2,4)
        if r_wall == 1 and w >= 3:
            dx = random.randint((x+1),(x+w-2))
            door_1 = Rect(dx,y-1,1,1)
        elif r_wall == 2 and h >=3:
            dy = random.randint((y+1),(y+h-2))
            door_1 = Rect(x+w,dy,1,1)
        elif r_wall == 3 and w >= 3:
            dx = random.randint((x+1),(x+w-2))
            door_1 = Rect(dx,y+h,1,1)
        elif r_wall == 4 and h >=3:
            dy = random.randint((y+1),(y+h-2))
            door_1 = Rect(x-1,dy,1,1)




        #make a hallway from the door
        x = door_1.x1
        y = door_1.y1
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



        scan_area = Rect(x,y,w,h)#check for overlap

        failed = False
        for other_feature in features:
            if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= tiles_x - 3 or \
            scan_area.y1 <= 3 or scan_area.y2 >= tiles_y - 3:
                failed = True
                break
        if not failed:
            hall = Rect(x,y,w,h)


            #Make door at end of corridoor
            w = hall.x2-hall.x1
            h = hall.y2-hall.y1
            x = hall.x1
            y = hall.y1

            if r_wall == 1:
                if w >1:
                    door = Rect(x,y-1,1,1)
                    door2 = Rect(x+w-1,y-1,1,1)

                else:
                    door = Rect(x,y-1,1,1)
                    door2 = None

            elif r_wall == 2:
                if h >1:
                    door = Rect(x+w,y,1,1)
                    door2 = Rect(x+w,y+h-1,1,1)

                else:
                    door = Rect(x+w,y,1,1)
                    door2 = None

            elif r_wall == 3:
                if w >1:
                    door = Rect(x,y+h,1,1)
                    door2 = Rect(x+w-1,y+h,1,1)

                else:
                    door = Rect(x,y+h,1,1)
                    door2 = None

            else:
                if h >1:
                    door = Rect(x-1,y,1,1)
                    door2 = Rect(x-1,y+h-1,1,1)

                else:
                    door = Rect(x-1,y,1,1)
                    door2 = None


            #make room beyond door
            if door2 == None:
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
                    y = (y+1)

                elif r_wall == 4:

                    w = random.randint(3,6)
                    h = random.randint(3,6)
                    x = (x-w)
                    y = random.randint(door.y1-(h/2),door.y1-1)

                scan_area = Rect(x,y,w,h)

                failed = False
                for other_feature in features:
                    if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= tiles_x - 3 or \
                    scan_area.y1 <= 3 or scan_area.y2 >= tiles_y - 3:
                        failed = True
                        break

                if not failed:
                    room = Rect(x,y,w,h)
                    rooms+=1

                    if rooms >= 10:
                        if exits <2:
                            (c_x,c_y) = room.center()
                            end_door = Rect(c_x,c_y,1,1)
                            stairs_down.append(end_door)
                            exits +=1

                    create_room(hall)
                    features.append(hall)
                    doors.append(door_1)
                    create_room(room)
                    doors.append(door)
                    features.append(room)
                    room_list.append(room)

            else:
                for d in (door,door2):
                    x = d.x1
                    y = d.y1


                    if r_wall == 1:

                        w = random.randint(3,4)
                        h = random.randint(3,6)
                        x = random.randint(d.x1-(w/2),d.x1-1)
                        y = (y-h)

                    elif r_wall == 2:

                        w = random.randint(3,6)
                        h = random.randint(3,4)
                        x = (x+1)
                        y = random.randint(d.y1-(h/2),d.y1-1)

                    elif r_wall == 3:

                        w = random.randint(3,4)
                        h = random.randint(3,6)
                        x = random.randint(d.x1-(w/2),d.x1-1)
                        y = y+1

                    elif r_wall == 4:

                        w = random.randint(3,6)
                        h = random.randint(3,4)
                        x = (x-w)
                        y = random.randint(d.y1-(h/2),d.y1-1)

                    scan_area = Rect(x,y,w,h)

                    failed = False
                    for other_feature in features:
                        if scan_area.x1 <= 3 or scan_area.x2 >= tiles_x - 3 or \
                        scan_area.y1 <= 3 or scan_area.y2 >= tiles_y - 3:
                            failed = True


                            break

                    if not failed:
                        room = Rect(x,y,w,h)
                        rooms+=1

                        if rooms >= 10:
                            if exits <2:
                                (c_x,c_y) = room.center()
                                end_door = Rect(c_x,c_y,1,1)
                                stairs_down.append(end_door)
                                exits +=1

                        create_room(hall)
                        features.append(hall)
                        doors.append(door_1)
                        create_room(room)

                        doors.append(door)

                        doors.append(door2)
                        features.append(room)
                        room_list.append(room)




    for i in doors:
        if (my_map[i.x1 + 1][i.y1].blocked and my_map[i.x1 - 1][i.y1].blocked)\
        or (my_map[i.x1][i.y1+1].blocked and my_map[i.x1][i.y1-1].blocked):
            lock_roll = random.randint(1,10)
            open_roll = random.randint(1,10)
            is_closed = True
            is_locked = False
            if open_roll <=2:
                is_closed = False
            if is_closed:
                if lock_roll <=3:
                    is_locked = True

            for x in range(i.x1,i.x2):
                for y in range(i.y1,i.y2):
                    my_map[x][y].door = is_closed
                    my_map[x][y].locked = is_locked
                    my_map[x][y].wall = False
                    my_map[x][y].blocked = is_closed
                    my_map[x][y].block_sight = is_closed



    for i in stairs_up:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].stairs_up = True
                my_map[x][y].wall = False
                my_map[x][y].blocked = False
                my_map[x][y].block_sight = False

    for i in stairs_down:
        for x in range(i.x1,i.x2):
            for y in range(i.y1,i.y2):
                my_map[x][y].stairs_down = True
                my_map[x][y].wall = False
                my_map[x][y].blocked = False
                my_map[x][y].block_sight = False
    
    draw_map(tiles_x,tiles_y)
    for r in room_list:
        place_objects(r)
    for m in monster_group:
        m.current_x = m.dest_x
        m.current_y = m.dest_y
    for n in npc_group:
        n.current_x = n.dest_x
        n.current_y = n.dest_y

def draw_map(size_x,size_y):
    
    for y in range(size_y):
        for x in range(size_x):
            wall = my_map[x][y].wall
            door = my_map[x][y].door
            open_door = my_map[x][y].door_open
            stairs_down = my_map[x][y].stairs_down
            stairs_up = my_map[x][y].stairs_up

            if wall:
                tmp_map.blit(wall_img,(x*tile_width,y*tile_height))
                pygame.draw.rect(item_map,(50,50,50),(x*10,y*10,10,10))
##                    pygame.draw.rect(tmp_map,(50,50,50),(x*tile_width,y*tile_height,tile_width,tile_height))
            elif door:
                if open_door:
                    tmp_map.blit(door_open_img,(x*tile_width,y*tile_height))
                else:
                    tmp_map.blit(door_img,(x*tile_width,y*tile_height))
                pygame.draw.rect(item_map,(100,50,50),(x*10,y*10,10,10))
                if my_map[x][y].locked:
                    tmp_map.blit(door_locked_img,(x*tile_width,y*tile_height))
                
                    
##                    pygame.draw.rect(tmp_map,(100,50,50),(x*tile_width,y*tile_height,tile_width,tile_height))
            elif stairs_down:
                pygame.draw.rect(tmp_map,(100,10,10),(x*tile_width,y*tile_height,tile_width,tile_height))
                pygame.draw.rect(item_map,(100,10,10),(x*10,y*10,10,10))
            elif stairs_up:
                pygame.draw.rect(tmp_map,(10,10,200),(x*tile_width,y*tile_height,tile_width,tile_height))
                pygame.draw.rect(item_map,(10,10,200),(x*10,y*10,10,10))
            else:
                tmp_map.blit(floor_img,(x*tile_width,y*tile_height))
                pygame.draw.rect(item_map,(200,200,200),(x*10,y*10,10,10))
                if my_map[x][y+1].blocked or my_map[x][y+1].door:
                    tmp_map.blit(floor_b_img,(x*tile_width,y*tile_height))
                if my_map[x][y-1].blocked or my_map[x][y-1].door:
                    tmp_map.blit(floor_t_img,(x*tile_width,y*tile_height))
                if my_map[x-1][y].blocked or my_map[x-1][y].door:
                    tmp_map.blit(floor_l_img,(x*tile_width,y*tile_height))
                if my_map[x+1][y].blocked or my_map[x+1][y].door:
                    tmp_map.blit(floor_r_img,(x*tile_width,y*tile_height))
                random_number = random.randint(1,100)
                if random_number >=98:
                    tmp_map.blit(floor_skull_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
                elif random_number >=96:
                    tmp_map.blit(floor_skell_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
                elif random_number >=94:
                    tmp_map.blit(floor_skull2_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
##                    pygame.draw.rect(tmp_map,(200,200,200),(x*tile_width,y*tile_height,tile_width,tile_height))


def stack_inventory(target):
    
    if target == None:
        target = player
    
    t_unstacked = []
    
    for stack in target.inventory:
        if len(stack)!=0:
            for item in stack:
                t_unstacked.append(item)
            
        else:
            del stack
        
    
    del target.inventory[:]

    target.inventory.extend(t_unstacked)


    stacks = []
    
    for i in range(len(target.inventory)): #restack all items
        item = target.inventory[i]
        #print item.name
        stack = []
        
        if not item.counted:
            #print item.name
            item.counted = True
            
            if item.stackable:
                stack.append(item)
                #print item.name
                for j in range(i+1, len(target.inventory)):
                    other_item = target.inventory[j]
                    
        
                    if other_item.name == item.name:
                        stack.append(other_item)
                        other_item.counted = True
            else:
                stack.append(item)
                #print item.name
        #else:
        #    item.counted = True       
                   
        if len(stack)!=0:
            
            stacks.append(stack)
       
    del target.inventory[:]  
    for s in stacks:
        target.inventory.append(s)
        for i in s:
            i.counted = False
            
def level_up():
    
    
    options = ['Strength    %s'%player.strength,'Wisdom      %s'%player.wisdom,'Cunning    %s'%player.cunning,'Caution    %s'%player.caution,'Ruthless    %s' %player.ruthless,'Strategy   %s'%player.strategy]
    
    arrow_y,arrow_x = level_up_gui.get_rect().topleft
    arrow_y += 20
    arrow_x +=20
    arrow_selection = 0
    
    leveling = 1
    
    while leveling:
        options = ['Strength    %s'%player.strength,'Wisdom      %s'%player.wisdom,'Cunning    %s'%player.cunning,'Caution    %s'%player.caution,'Ruthless    %s' %player.ruthless,'Strategy   %s'%player.strategy]
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    leveling = 0
                
                elif event.key == K_DOWN:
                    if arrow_selection <= 4:
                        arrow_y+=20
                        arrow_selection +=1
                        #selected_att = options[arrow_selection]
                    
                elif event.key == K_UP:
                    if arrow_selection >=1:
                        arrow_y-=20
                        arrow_selection -=1
                        #selected_att = options[arrow_selection]
                        
                elif event.key == K_RIGHT:
                    if player.level_up_points >0:
                        if arrow_selection == 0:
                            player.strength +=1
                            player.c_max_hp +=1
                            player.attk_pwr +=1
                            player.max_weight +=1
                            player.level_up_points -=1
                        elif arrow_selection == 1:
                            player.wisdom +=1
                            player.magic_attk +=1
                            player.magic_def +=1
                            player.charisma +=1
                            player.level_up_points -=1
                        elif arrow_selection == 2:
                            player.cunning +=1
                            player.hit +=1
                            player.dodge +=1
                            player.perception +=1
                            player.level_up_points -=1
                        elif arrow_selection == 3:
                            player.caution +=1
                            player.c_max_hp +=1
                            player.defence +=1
                            player.magic_def +=1
                            player.level_up_points -=1
                        elif arrow_selection == 4:
                            player.ruthless +=1
                            player.attk_pwr +=1
                            player.magic_attk +=1
                            player.hit +=1
                            player.level_up_points -=1
                        elif arrow_selection == 5:
                            player.strategy +=1
                            player.charisma +=1
                            player.perception +=1
                            player.max_weight +=1
                            player.level_up_points -=1
                        player.modify_stats()
                        updateGUI('you have improved your skills',(10,10,10))       
                        
        
        y_inc = 20
        level_up_gui.fill((100,100,100))
        for i in options:
            text = font1.render(i,1,(10,10,10))
            p_x,p_y = level_up_gui.get_rect().midtop
            p_x -= 30
            p_y +=  y_inc
            y_inc +=20
            level_up_gui.blit(text,(p_x,p_y))
            
        available_points = 'Level Up Points    %s'%player.level_up_points
        points_txt = font1.render(available_points,1,(10,10,10))
        point_x,point_y = level_up_gui.get_rect().bottomleft
        point_x +=30
        point_y -= 30
        level_up_gui.blit(points_txt,(point_x,point_y))
        level_up_gui.blit(arrow_img,(arrow_x,arrow_y))
        screen.blit(level_up_gui,(player.rect.x-50,player.rect.y-50))
        
        pygame.display.flip()
        
    

def draw_inventory(name,cont1,cont2,inv1,inv2,selected_item,category=None):

    if selected_item is not None:
        item_info = selected_item
    selected_contents = cont1
    selected_inv = inv1
    other_contents = cont2
    other_inv = inv2

    inv1_name = font1.render(player.name,1,(50,10,10))
    inv2_name = font1.render(name,1,(50,10,10))
    inv1_name_pos = inv1_name.get_rect()
    inv2_name_pos = inv2_name.get_rect()
    inv1_x,inv1_y = inventory_1.get_rect().midtop
    inv2_x,inv2_y = inventory_2.get_rect().midtop

    slot = 30
    slot_2 = 30
    #inventory_background.fill((100,100,100))
    inventory_1.fill((150,150,150))
    inventory_2.fill((150,150,150))
    trade_gui.fill((100,100,100))
    inventory_1.blit(inv1_name,(inv1_x-30,inv1_y))
    inventory_2.blit(inv2_name,(inv2_x-30,inv2_y))


    for i in selected_contents:
        
        if i[0] is not None:
            item = i[0]
            value = item.value
            amount = len(i)
            if other_contents == player.inventory and category == 'gear':
                item_name = "       %s"%item.name
            else:
                item_name = " %s    x   %s"%(amount,item.name)
            
            
            text = font1.render(item_name,1,(10,10,10))
            text_pos = text.get_rect()
            txt_x, txt_y = selected_inv.get_rect().topleft
            selected_inv.blit(text,(txt_x+50,txt_y+slot))
            selected_inv.blit(item.inv_img,(txt_x+30,txt_y+slot-5))
            slot+=20
    
   
    for i in other_contents:

        if i[0] is not None:
            item = i[0]
            value = item.value
            amount = len(i)
            #if i[0].category == 'helm' and category == 'gear':
            if selected_contents == player.inventory and category == 'gear':
                item_name = "       %s"%item.name
            else:
                item_name = " %s    x   %s"%(amount,item.name)
            text = font1.render(item_name,1,(10,10,10))
            text_pos = text.get_rect()
            txt_x, txt_y = other_inv.get_rect().topleft
            other_inv.blit(text,(txt_x+50,txt_y+slot_2))
            other_inv.blit(item.inv_img,(txt_x+30,txt_y+slot_2-5))
            slot_2+=20
    

                
                

    if selected_item is not None:
        if item_info.identified:
            info1 = "Name: %s          Weight: %s       Value: %s" %(item_info.name,item_info.weight,item_info.value)
        else:
            info1 = "Unidentified item      Weight: %s       Value: %s" %(item_info.weight,item_info.value)
    else:
        info1= "Unidentified item"
    info1 = font2.render(info1,1,(10,10,10))
    info1_pos = info1.get_rect()
    info1_x,info1_y = trade_gui.get_rect().topleft
    trade_gui.blit(info1,(info1_x+10,info1_y+10))
    
    if selected_item is not None:
        if item_info.identified:
            info2 = item_info.description
        else:
            info2 = ''
            #info2 = "Slash: %s      Smash: %s      Stab: %s     Durability: %s"%(item_info.slash,item_info.smash,item_info.stab,item_info.durability)
    else:
        info2 = ""
    info2 = font2.render(info2,1,(10,10,10))
    info2_pos = info2.get_rect()
    info2_x,info2_y = trade_gui.get_rect().topleft
    trade_gui.blit(info2,(info2_x+10,info2_y+30))
    #pygame.display.flip()
    
    if selected_item is not None and selected_item.identity != 'item':
        if item_info.identified:
            info3 = "Slash: %s      Smash: %s      Stab: %s     Durability: %s"%(item_info.slash,item_info.smash,item_info.stab,item_info.durability)
        else:
            info3 = ""
    else:
        info3 = ""
    info3 = font2.render(info3,1,(10,10,10))
    info3_pos = info3.get_rect()
    info3_x,info3_y = trade_gui.get_rect().topleft
    trade_gui.blit(info3,(info3_x+10,info3_y+50))
    #pygame.display.flip()
    
    if selected_item is not None and selected_item.identity != 'item':
        if item_info.identified:
            info4 = "Fire: %s      Ice: %s      Thunder: %s       Holy: %s"%(item_info.fire,item_info.ice,item_info.thunder,item_info.dark)
        else:
            info4 = ""
    else:
        info4 = ""
    info4 = font2.render(info4,1,(10,10,10))
    info4_pos = info4.get_rect()
    info4_x,info4_y = trade_gui.get_rect().topleft
    trade_gui.blit(info4,(info4_x+10,info4_y+70))
    #pygame.display.flip()

def open_inventory(inv1,target,category):
    
    global item_k1
    global item_k2
    global item_k3
    global item_k4
    global item_k5
    global item_k6
    global item_k7
    global item_k8
    global item_k9
    global item_k0

    inventory_background.fill((100,100,100))
    
    if target is not None:
        stack_inventory(target)
        stack_inventory(player)
    else:
        stack_inventory(target)
    
 
    if category == 'trash':
        name = 'Trash'
        inv2 = []
        selected_contents = inv1
        other_contents = inv2
        trash = True
        arrow_x = 110
        selected_inv = inventory_1
        other_inv = inventory_2
    elif category == 'gear':
        selected_contents = inv1
        inv2 = [[player.helm],[player.armour],[player.gloves],[player.weapon],
            [player.offhand],[player.r_ring],[player.chain],[player.boots]]
        other_contents = inv2
        trash = False
        arrow_x = 110
        selected_inv = inventory_1
        other_inv = inventory_2
        name = "Gear"
    else:
        inv2 = target.inventory
        name = target.name
        selected_contents = inv2#target.inventory
        other_contents = inv1
        trash = False
        arrow_x = 360
        selected_inv = inventory_2
        other_inv = inventory_1

    transaction_value = 0

    inv_length = len(selected_contents)
    inv2_length = len(other_contents)
    
    if trash:
        dropped_items = []
        trash_object = Treasure(player.map_x/tile_width,player.map_y/tile_height,bag_img,dropped_items,'Bag',False)


    arrow_top = 132
    arrow_bottom = arrow_top + (20*20)
    arrow_y = 132
    arrow_selection = 1
    selection = arrow_selection -1
    if inv_length != 0:
        selected_item = selected_contents[selection]
        item_info = selected_item[0]#fed to draw inventory to display its stats
    else:
        item_info=None
        
    draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)

    is_open = 1
    while is_open:

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                
                if event.key == K_i or event.key == K_ESCAPE:
                    if category == 'trade':
                        if transaction_value !=0:
                            trade_chance = target.charisma - player.charisma + transaction_value
                            if trade_chance <= 0:
                                text = "A fair deal!"
                                updateGUI(text,(10,100,100))
                                is_open = 0
                                render_all()
                            else:
                                text = "No deal you owe me %s!" %trade_chance
                                updateGUI(text,(10,100,100))
                        else:
                            is_open = 0
                            render_all()

                    elif trash:
                        trash_length = len(trash_object.inventory)
                        if trash_length !=0:
                            #trash_object = Treasure(player.map_x/tile_width,player.map_y/tile_height,bag_img,dropped_items,'Bag')
                            treasure_group.add(trash_object)
                        if monster_str == 1:
                            village_objects.append(trash_object)
                        is_open = 0
                        render_all()
                    else:
                        is_open = 0
                        render_all()



                elif event.key == K_DOWN:
                    selected_contents_length = len(selected_contents)
                    if arrow_y <= arrow_bottom and selected_contents_length>arrow_selection:
                        arrow_y += 20
                        arrow_selection+=1
                        selection = arrow_selection -1
                        selected_item = selected_contents[selection]
                        
                        item_info = selected_item[0]
                        
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)


                elif event.key == K_UP:
                    selected_contents_length = len(selected_contents)
                    if arrow_y > arrow_top:
                        arrow_y -= 20
                        arrow_selection -=1
                        selection = arrow_selection -1
                        selected_item = selected_contents[selection]
                       
                        item_info = selected_item[0]
                    
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)


                elif event.key == K_RIGHT:
                    other_contents_length = len(other_contents)
                    if arrow_x < 260 and other_contents_length is not 0:
                        arrow_x += 250
                        arrow_y = 132
                        arrow_selection = 1
                        selection = arrow_selection - 1
                        if category is not "gear":
                            selected_contents = inv2#target.inventory
                        else:
                            selected_contents = [[player.helm],[player.armour],[player.gloves],[player.weapon],
                                                [player.offhand],[player.r_ring],[player.chain],[player.boots]]
                        other_contents = inv1
                        selected_inv = inventory_2
                        other_inv = inventory_1
                        selection = 0
                        selected_item = selected_contents[selection]
                        
                        item_info = selected_item[0]
                       
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)


                elif event.key == K_LEFT:
                    other_contents_length = len(other_contents)
                    if arrow_x > 110 and other_contents_length is not 0:
                        arrow_x -= 250
                        arrow_y = 132
                        arrow_selection = 1
                        selection = arrow_selection - 1
                        selected_contents = inv1
                        if category is not 'gear':
                            other_contents = inv2#target.inventory
                        else:
                            other_contents = [[player.helm],[player.armour],[player.gloves],[player.weapon],
                                            [player.offhand],[player.r_ring],[player.chain],[player.boots]]
                        selected_inv = inventory_1
                        other_inv = inventory_2
                        selection = 0
                        selected_item = selected_contents[selection]
                      
                        item_info = selected_item[0]
                   
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)


                elif event.key == K_t and category is not "gear": #trash trade take transfer items
                    selected_contents_length = len(selected_contents)
                    other_contents_length = len(other_contents)
                    if selected_contents_length is not 0 and other_contents_length < 18:
                        selected_item = selected_contents[selection]
                        if player.current_weight + selected_item[0].weight <= player.max_weight or selected_contents == inv1:
                            trade_item = selected_item.pop()
                            other_contents.append([trade_item])
                            if selected_contents == inv1:
                                print "dumping", trade_item.weight
                                player.current_weight-=trade_item.weight
                                transaction_value -= trade_item.value
                            else:
                                print "gaining", trade_item.weight
                                player.current_weight+=trade_item.weight
                                transaction_value += trade_item.value
                            if selected_contents == inv1:
                                player.current_weight-=trade_item.weight
                                transaction_value -= trade_item.value
                            else:
                                player.current_weight+=trade_item.weight
                                transaction_value += trade_item.value
                            
                        else:
                            text = "You are carrying too much!"
                            updateGUI(text,(10,10,10))
                            
                        if len(selected_item)<=0:
                            selected_contents.remove(selected_item)
                        
                        
                        inv_length = len(selected_contents)
                        if arrow_selection > inv_length and arrow_selection is not 1:
                            arrow_selection -= 1
                            arrow_y -=20
                            selection = arrow_selection -1
                        if len(selected_contents)!=0:
                            selected_item = selected_contents[selection]
                            item_info = selected_item[0]
                        else:
                            item_info = None
                        
                        if trash:
                            trash_object.inventory = inv2
                            stack_inventory(trash_object)
                            stack_inventory(player)
                            #dropped_items = inv2
                        else:
                            #target.inventory = inv2
                            stack_inventory(player)
                            stack_inventory(target)
                        player.modify_stats()
                        print "player has ",player.current_weight ,"weight in inventory"
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)

                    else:
                        text = "There is no more room"
                        updateGUI(text,(10,10,10))
                    
                   

                elif event.key == K_f:#use item
                    if category != 'trade':
                        selected_contents_length = len(selected_contents)
                        if selected_contents_length != 0:
                            selected_item = selected_contents[selection]
                            if selected_contents == player.inventory:
                                if selected_item[0].category != 'currency' and selected_item[0].name != 'Identity Scroll':
                                    if selected_item[0].identified:
                                        item_used = selected_item.pop()
                                        use_equip(item_used)
                                        if category != 'gear':
                                            is_open = 0
                                    else:
                                        text = "Needs to be identified"
                                        updateGUI(text,(10,10,10))
                                    if category == 'gear':
                                        other_contents = [[player.helm],[player.armour],[player.gloves],[player.weapon],
                                                        [player.offhand],[player.r_ring],[player.chain],[player.boots]]
                                    else:
                                        stack_inventory(target)
                                    stack_inventory(player)
                                    
                                    
                                else:
                                    text = "you cannot use that item directly"
                                    updateGUI(text,(10,10,10))
                            elif category != "gear":
                                text = "This item does not belong to you"
                                updateGUI(text,(10,10,10))
                            else:
                                item_used = selected_item[0]
                                if item_used.category != 'no equipment' and other_contents_length < 18:
                                    other_contents.append([item_used])
                                    unequip_item(item_used)
                                selected_contents = [[player.helm],[player.armour],[player.gloves],[player.weapon],
                                                    [player.offhand],[player.r_ring],[player.chain],[player.boots]]
                            inv_length = len(selected_contents)
                            if arrow_selection > inv_length and arrow_selection is not 1:
                                arrow_selection -= 1
                                arrow_y -=20
                            selection = arrow_selection - 1
                            if len(selected_contents)!=0:
                                selected_item = selected_contents[selection]
                                item_info = selected_item[0]
                            else:
                                item_info = None
                            player.modify_stats()
                            draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)

                elif event.key == K_e and category != 'trade':#examine item
                    items = selected_contents[selection]
                    item = items[0]
                    scroll_present = False
                    for i in player.inventory:
                        if i[0].name == 'Identity Scroll':
                            scroll_present = True
                            i.pop(0)
                            chance_1 = random.randint(5,20)+player.magic_attk
                            
                            if item.value - (player.perception+chance_1)<=0:
                                item.identified = True
                                text = "item identified"
                            else:
                                text = "Failed to identify item"
                            break
                        else:
                            scroll_present=False
                            text = "No scroll of identity"
                    if not scroll_present:
                        if item.value - player.perception<=0:
                            item.identified = True
                            text = "item identified"
                        else:
                            text = "Failed to identify item"
                        
                    updateGUI(text,(10,10,10))
                        
                    stack_inventory(player)
                    inv_length = len(selected_contents)
                    if arrow_selection > inv_length and arrow_selection is not 1:
                        arrow_selection -= 1
                        arrow_y -=20
                    selection = arrow_selection - 1
                    if len(selected_contents)!=0:
                        selected_item = selected_contents[selection]
                        item_info = selected_item[0]
                    else:
                        item_info = None
                    
                    draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info,category)
                    

                #the below is used to assign hotkeys
                elif event.key == K_1:
                    item = selected_contents[selection]
                    if item[0].category!='currency' and item[0].name != 'Identity Scroll':
                        item_k1 = item[0].name
                        text = "%s assigned to Key 1"%item_k1
                        updateGUI(text,(10,10,10))
                        
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_2:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k2 = item[0].name
                        text = "%s assigned to Key 2"%item_k2
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_3:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k3 = item[0].name
                        text = "%s assigned to Key 3"%item_k3
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_4:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k4 = item[0].name
                        text = "%s assigned to Key 4"%item_k4
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_5:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k5 = item[0].name
                        text = "%s assigned to Key 5"%item_k5
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_6:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k6 = item[0].name
                        text = "%s assigned to Key 6"%item_k6
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_7:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k7 = item[0].name
                        text = "%s assigned to Key 7"%item_k7
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_8:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k8 = item[0].name
                        text = "%s assigned to Key 8"%item_k8
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_9:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k9 = item[0].name
                        text = "%s assigned to Key 9"%item_k9
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_0:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category!='currency'and item[0].name != 'Identity Scroll': 
                        item_k0 = item[0].name
                        text = "%s assigned to Key 0"%item_k0
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))

        if is_open == 1:
            #draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)
            screen.blit(inventory_background,(100,100))
            inventory_background.blit(inventory_1,(5,5))
            inventory_background.blit(inventory_2,(255,5))
            inventory_background.blit(trade_gui,(20,390))
            screen.blit(arrow_img,(arrow_x,arrow_y))
            pygame.display.flip()


def updateGUI(text,clr):

    #player info screen
    level_up_xp = level_up_base + (level_up_factor*player.level)
    text1_1 = "HP    %s / %s       Dungeon   %s" % (player.hp,player.max_hp,monster_str)
    text1_2 = "DEF       %s               M.DEF     %s" % (player.defence,player.magic_def)
    text1_3 = "ATT       %s             M.ATT     %s" % (player.attk_pwr,player.magic_attk)
    text1_4 = "AVO       %s             CHAR      %s " % (player.dodge,player.charisma)
    text1_5 = "HIT       %s             PERC      %s" % (player.hit,player.perception)
    text1_6 = "XP     %s/ %s      LEVEL %s" % (player.xp,level_up_xp,player.level)

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

    txt_x += 50
    txt11_y = txt_y + 50
    txt11pos.topleft = (txt_x,txt11_y)

    txt12_y = txt_y + 70
    txt12pos.topleft = (txt_x,txt12_y)

    txt13_y = txt_y + 90
    txt13pos.topleft = (txt_x,txt13_y)

    txt14_y = txt_y + 110
    txt14pos.topleft = (txt_x,txt14_y)

    txt15_y = txt_y +130
    txt15pos.topleft = (txt_x,txt15_y)

    txt16_y = txt_y + 150
    txt16pos.topleft = (txt_x,txt16_y)

    stats_gui.blit(gui_back_img,(0,0))
    stats_gui.blit(txt11,txt11pos)
    stats_gui.blit(txt12,txt12pos)
    stats_gui.blit(txt13,txt13pos)
    stats_gui.blit(txt14,txt14pos)
    stats_gui.blit(txt15,txt15pos)
    stats_gui.blit(txt16,txt16pos)

    #equipment screen
    #text2_1 = "health  X %s  fire  X %s  ice X %s" %  (player.heal_spell,player.fire_spell,player.ice_spell)
    #text2_1 = font1.render(text2_1,1,(10,10,10))
    #
    #text2_1_pos = text2_1.get_rect()
    equipment.fill((150,150,150))
    #equipment.blit(text2_1,text2_1_pos)


    txt2_x,txt2_y = equipment.get_rect().topleft
    if player.weapon is not None:
        text2_2 = "%s     " % player.weapon.name
        #text2_3 = "att %s    m.att %s   hit %s" % (player.weapon.attk_pwr,player.weapon.magic_attk,player.weapon.hit)
        text2_4 = "slash %s smash %s stab %s" % (player.weapon.slash,player.weapon.smash,player.weapon.stab)
        text2_5 = "fire %s ice %s thunder %s" % (player.weapon.fire,player.weapon.ice,player.weapon.thunder)
        text2_2 = font1.render(text2_2,1,(10,10,10))
        #text2_3 = font1.render(text2_3,1,(10,10,10))
        text2_4 = font1.render(text2_4,1,(10,10,10))
        text2_5 = font1.render(text2_5,1,(10,10,10))
        text2_2_pos = text2_2.get_rect()
        #text2_3_pos = text2_3.get_rect()
        text2_4_pos = text2_4.get_rect()
        text2_5_pos = text2_5.get_rect()
        txt2_x += 10
        txt21_y = txt2_y + 20
        #text2_1_pos.topleft = (txt2_x,txt21_y) this used to be the spell line

        txt22_y = txt2_y + 100
        text2_2_pos.topleft = (txt2_x,txt22_y)

        txt23_y = txt2_y + 120
        #text2_3_pos.topleft = (txt2_x,txt23_y)

        txt24_y = txt2_y + 140
        text2_4_pos.topleft = (txt2_x,txt24_y)

        txt25_y = txt2_y + 160
        text2_5_pos.topleft = (txt2_x,txt25_y)

        equipment.blit(text2_2,text2_2_pos)
        #equipment.blit(text2_3,text2_3_pos)
        equipment.blit(text2_4,text2_4_pos)
        equipment.blit(text2_5,text2_5_pos)

    if player.armour is not None:
        text2_6 = "%s     "  % player.armour.name
        #text2_7 = "def%s    m.def%s   dodge %s" % (player.armour.defence,player.armour.magic_def,player.armour.dodge)
        text2_8 = "slash %s smash %s stab %s" % (player.armour.slash,player.armour.smash,player.armour.stab)
        text2_9 = "fire %s ice %s thunder %s" % (player.armour.fire,player.armour.ice,player.armour.thunder)
        text2_6 = font1.render(text2_6,1,(10,10,10))
        #text2_7 = font1.render(text2_7,1,(10,10,10))
        text2_8 = font1.render(text2_8,1,(10,10,10))
        text2_9 = font1.render(text2_9,1,(10,10,10))
        text2_6_pos = text2_6.get_rect()
        #text2_7_pos = text2_7.get_rect()
        text2_8_pos = text2_8.get_rect()
        text2_9_pos = text2_9.get_rect()

        txt26_y = txt2_y + 190
        text2_6_pos.topleft = (txt2_x,txt26_y)

        txt27_y = txt2_y + 210
        #text2_7_pos.topleft = (txt2_x,txt27_y)

        txt28_y = txt2_y + 230
        text2_8_pos.topleft = (txt2_x,txt28_y)

        txt29_y = txt2_y + 250
        text2_9_pos.topleft = (txt2_x,txt29_y)

        equipment.blit(text2_6,text2_6_pos)
        #equipment.blit(text2_7,text2_7_pos)
        equipment.blit(text2_8,text2_8_pos)
        equipment.blit(text2_9,text2_9_pos)

    #combat info screen
    if text is not None and clr is not None:
        text = font2.render(text,1,(clr))
        text_pos = text.get_rect()
        text_list.insert(0,text)
        length = len(text_list)
        if length == 16:
            text_list.pop(15)
    
        coordx,coordy = combat.get_rect().bottomleft
        coordx += 45
        coordy -=65
        index=0
        combat.blit(gui_back_img,(0,0))
        for i in text_list:
            if len(text_list)>=1:
                coordy-=15
                
                
                combat.blit(text_list[index],(coordx,coordy))
                index+=1
        

    gui.fill((10,10,10))

    render_gui()
    

    
def calc_field_of_view(char):
    global my_map
    
    
    dark_list = []

    
    for y in range ((char.map_y-100)/tile_width,(char.map_y+200)/tile_width):
        for x in range ((char.map_x-100)/tile_width,(char.map_x+200)/tile_width):
            
            my_map[x][y].explored = True
            my_map[x][y].shadow = False
            
            #upper left
            if x*tile_width < char.map_x and y*tile_height < char.map_y and my_map[x][y].block_sight == False:
                my_map[x-1][y-1].shadow = False
                if my_map[x-1][y-1].block_sight == False:
                    my_map[x-2][y-2].shadow = False
                    
                my_map[x-1][y].shadow = False
                if my_map[x-1][y].block_sight == False:
                    my_map[x-2][y-1].shadow = False
                my_map[x][y-1].shadow = False
                if my_map[x][y-1].block_sight == False:
                    my_map[x-1][y-2].shadow = False
                
            #upper mid
            if my_map[x][y].block_sight == False:
                my_map[x][y-1].shadow = False
                if my_map[x][y-1].block_sight == False:
                    my_map[x][y-2].shadow = False
                    
                my_map[x+1][y-1].shadow = False
                if my_map[x+1][y-1].block_sight == False:
                    my_map[x+1][y-2].shadow = False
                    

                my_map[x-1][y-1].shadow = False
                if my_map[x-1][y-1].block_sight == False:
                    my_map[x-1][y-2].shadow = False
                    
            #upper right
            if x*tile_width >char.map_x  and y*tile_height < char.map_y and my_map[x][y].block_sight == False:
                my_map[x+1][y-1].shadow = False
                if my_map[x+1][y-1].block_sight == False:
                    my_map[x+2][y-2].shadow = False
                    
                my_map[x+1][y].shadow = False
                if my_map[x+1][y].block_sight == False:
                    my_map[x+2][y-1].shadow = False

                my_map[x][y-1].shadow = False
                if my_map[x][y-1].block_sight == False:
                    my_map[x+1][y-2].shadow = False
                
            #mid right
            if my_map[x][y].block_sight == False:
                my_map[x+1][y].shadow = False
                if my_map[x+1][y].block_sight == False:
                    my_map[x+2][y].shadow = False
                
                
                my_map[x+1][y-1].shadow = False
                if my_map[x+1][y-1].block_sight == False:
                    my_map[x+2][y-1].shadow = False
                
                my_map[x+1][y+1].shadow = False
                if my_map[x+1][y+1].block_sight == False:
                    my_map[x+2][y+1].shadow = False
                    
            #lower right
            if x*tile_width >char.map_x  and y*tile_height > char.map_y and my_map[x][y].block_sight == False:
                my_map[x+1][y+1].shadow = False
                if my_map[x+1][y+1].block_sight == False:
                    my_map[x+2][y+2].shadow = False
                    
                
                my_map[x+1][y].shadow = False
                if my_map[x+1][y].block_sight == False:
                    my_map[x+2][y+1].shadow = False
                
                my_map[x][y+1].shadow = False
                if my_map[x][y+1].block_sight == False:
                    my_map[x+1][y+2].shadow = False
                
            #lower mid
            if my_map[x][y].block_sight == False:
                my_map[x][y+1].shadow = False
                if my_map[x][y+1].block_sight == False:
                    my_map[x][y+2].shadow = False
                    
                my_map[x-1][y+1].shadow = False
                if my_map[x-1][y+1].block_sight == False:
                    my_map[x-1][y+2].shadow = False
                
                my_map[x+1][y+1].shadow = False
                if my_map[x+1][y+1].block_sight == False:
                    my_map[x+1][y+2].shadow = False
                    
            #lower left
            if x*tile_width < char.map_x  and y*tile_height > char.map_y and my_map[x][y].block_sight == False:
                my_map[x-1][y+1].shadow = False
                if my_map[x-1][y+1].block_sight == False:
                    my_map[x-2][y+2].shadow = False
                    
                my_map[x-1][y].shadow = False
                if my_map[x-1][y].block_sight == False:
                    my_map[x-2][y+1].shadow = False
                
                my_map[x][y+1].shadow = False
                if my_map[x][y+1].block_sight == False:
                    my_map[x-1][y+2].shadow = False
                
            #mid left
            if my_map[x][y].block_sight == False:
                my_map[x-1][y].shadow = False
                if my_map[x-1][y].block_sight == False:
                    my_map[x-2][y].shadow = False
                    
                my_map[x-1][y+1].shadow = False
                if my_map[x-1][y+1].block_sight == False:
                    my_map[x-2][y+1].shadow = False

                my_map[x-1][y-1].shadow = False
                if my_map[x-1][y-1].block_sight == False:
                    my_map[x-2][y-1].shadow = False

    
    for y in range ((char.map_y-300)/tile_width,(char.map_y+500)/tile_width):
        for x in range ((char.map_x-300)/tile_width,(char.map_x+500)/tile_width):
            
            rect = Rect(x*tile_width,y*tile_height,tile_width,tile_height)

            if my_map[x][y].shadow:
                dark_list.append(rect)
            #if my_map[x][y].explored and my_map[x][y].shadow == True:
            #    explored_list.append((x_rect,y_rect))
                
    

    #for i in dark_list:
    #    screen.fill(col,i)


    for y in range ((char.map_y-300)/tile_width,(char.map_y+400)/tile_width):
        for x in range ((char.map_x-300)/tile_width,(char.map_x+400)/tile_width):
            my_map[x][y].explored = True
            my_map[x][y].shadow = True

    return dark_list

def render_all():
    
    global dark_list
    map_pos_x = player.rect.x - player.current_x
    map_pos_y = player.rect.y - player.current_y
    screen.blit(tmp_map, (map_pos_x ,map_pos_y))

    for t in treasure_group:
        t.rect.x = map_pos_x + t.map_x
        t.rect.y = map_pos_y + t.map_y

    treasure_group.draw(screen)
    
    for s in spawner_group:
        s.rect.x = map_pos_x + s.map_x
        s.rect.y = map_pos_y + s.map_y
    spawner_group.draw(screen)
    
    for trap in trap_group:
        trap.rect.x = map_pos_x + trap.map_x
        trap.rect.y = map_pos_y + trap.map_y
    trap_group.draw(screen)
    
    for n in npc_group:
        n.rect.x = map_pos_x + n.map_x
        n.rect.y = map_pos_y + n.map_y
    for m in monster_group:
        m.rect.x = map_pos_x + m.current_x
        m.rect.y = map_pos_y + m.current_y
    npc_group.draw(screen)
 

    monster_group.draw(screen)
    

    
    player_sprite.draw(screen)
    if player.boots.player_img is not None:
        screen.blit(player.boots.player_img,(player.rect.x,player.rect.y))
    if player.armour.player_img is not None:
        screen.blit(player.armour.anim[player.frame],(player.rect.x,player.rect.y))
    if player.gloves.player_img is not None:
        screen.blit(player.gloves.anim[player.frame],(player.rect.x,player.rect.y))
    if player.offhand.player_img is not None:
        screen.blit(player.offhand.anim[player.frame],(player.rect.x,player.rect.y))
    if player.weapon.player_img is not None:
        screen.blit(player.weapon.anim[player.frame],(player.rect.x,player.rect.y))
    
    if player.helm.player_img is not None:
        screen.blit(player.helm.anim[player.frame],(player.rect.x,player.rect.y))
    
    if player.frozen:
        if len(effect_group)<=0:
            screen.blit(ice_3,(player.rect.x,player.rect.y))
    
    for e in effect_group:
        e.rect.x = map_pos_x + e.map_x
        e.rect.y = map_pos_y + e.map_y
    effect_group.draw(screen)
       
    
    
    dark_list = calc_field_of_view(player)
    shadow_group.empty()
    for i in dark_list:
        shadow = Shadow(i.x1,i.y1)
        shadow_group.add(shadow)
        
    for i in shadow_group:
        i.rect.x = map_pos_x+i.map_x
        i.rect.y = map_pos_y +i.map_y
        
        #screen.fill(col,(i.x1,i.y1,tile_width,tile_height))
    shadow_group.draw(screen)
        
    
    if reticule.display:
        #reticule.rect.x = map_pos_x + reticule.map_x
        #reticule.rect.y = map_pos_y + reticule.map_y
        screen.blit(reticule.image,(reticule.rect.x,reticule.rect.y))

    if item_map_open:
        item_tmp_map.blit(item_map,(0,0))
        pygame.draw.rect(item_tmp_map,(255,215,0),(player.current_x/tile_width*10,player.current_y/tile_height*10,10,10))
        for t in treasure_group:
            pygame.draw.rect(item_tmp_map,(255,156,0),(t.map_x/tile_width*10,t.map_y/tile_height*10,10,10))
        for n in npc_group:
            pygame.draw.rect(item_tmp_map,(155,56,255),(n.map_x/tile_width*10,n.map_y/tile_height*10,10,10))
        for m in monster_group:
            pygame.draw.rect(item_tmp_map,(20,200,20),(m.current_x/tile_width*10,m.current_y/tile_height*10,10,10))
        screen.blit(item_tmp_map,(0,0))
        #for y in range(tiles_y):
        #    for x in range(tiles_x):
        #        if not my_map[x][y].explored:
        #            screen.fill((0,0,0),(x*10,y*10,10,10))
      
    
  
    
    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7, 0))
    screen.blit(combat, (tile_width * 7 , tile_height*3 + 40))
    #screen.blit(equipment, (tile_width*7+10, tile_height * 4 + 10))


    pygame.display.flip()

def render_gui():
    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7, 0))
    screen.blit(combat, (tile_width * 7 , tile_height*3 + 40))
    #screen.blit(equipment, (tile_width*7+10, tile_height * 4 + 10))

#initialisation
#GUI images
gui_back_img = pygame.image.load('rahnok_gui_2.png').convert_alpha()

#map images
wall_img = pygame.image.load('wall_1.png')
floor_img = pygame.image.load('floor_1.png')
floor_b_img = pygame.image.load('floor_b.png')
floor_t_img = pygame.image.load('floor_t.png')
floor_l_img = pygame.image.load('floor_l.png')
floor_r_img = pygame.image.load('floor_r.png')
floor_skull_img = pygame.image.load('floor_skull.png')
floor_skull2_img = pygame.image.load('floor_skull_2.png')
floor_skell_img = pygame.image.load('floor_skell.png')
door_img = pygame.image.load('door2.png')
door_open_img = pygame.image.load('door_op.png')
door_locked_img = pygame.image.load('door_lock.png')
exit_img = pygame.image.load('exit.jpg')
treasure_img = pygame.image.load('chest.png').convert_alpha()
bag_img = pygame.image.load('bag.png').convert_alpha()

#effect images
shadow_img = pygame.image.load('shadow.png').convert_alpha()
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()
corpse_img = pygame.image.load('corpse.png').convert_alpha()
loot_img = pygame.image.load('loot.png').convert_alpha()
arrow_img = pygame.image.load('arrow.png').convert_alpha()
web_img = pygame.image.load('web.png').convert_alpha()
target_img = pygame.image.load('crosshare.png').convert_alpha()

lightning_1 = pygame.image.load('lightning_1.png').convert_alpha()
lightning_2 = pygame.image.load('lightning_2.png').convert_alpha()
heal_1 = pygame.image.load('heal_1.png').convert_alpha()
heal_2 = pygame.image.load('heal_2.png').convert_alpha()
fire_1 = pygame.image.load('fire_1.png').convert_alpha()
fire_2 = pygame.image.load('fire_2.png').convert_alpha()
fire_3 = pygame.image.load('fire_3.png').convert_alpha()
ice_1 = pygame.image.load('ice_1.png').convert_alpha()
ice_2 = pygame.image.load('ice_2.png').convert_alpha()
ice_3 = pygame.image.load('ice_3.png').convert_alpha()
shatter_2 = pygame.image.load('shatter_2.png').convert_alpha()
shatter_3 = pygame.image.load('shatter_3.png').convert_alpha()
shatter_4 = pygame.image.load('shatter_4.png').convert_alpha()
slash_1 = pygame.image.load('slash_1.png').convert_alpha()
slash_2 = pygame.image.load('slash_2.png').convert_alpha()
slash_3 = pygame.image.load('slash_3.png').convert_alpha()

ice_anim = []
fire_anim = []
lightning_anim = []
heal_anim = []
shatter_anim = []
slash_anim = []

for i in range(10):
    lightning_anim.append(lightning_1)
    fire_anim.append(fire_1)
    heal_anim.append(heal_1)
    ice_anim.append(ice_1)
    shatter_anim.append(shatter_2)
    slash_anim.append(slash_1)
for i in range(10):
    lightning_anim.append(lightning_2)
    fire_anim.append(fire_2)
    heal_anim.append(heal_2)
    ice_anim.append(ice_2)
    shatter_anim.append(shatter_3)
    slash_anim.append(slash_2)
for i in range(10):
    lightning_anim.append(lightning_1)
    fire_anim.append(fire_3)
    heal_anim.append(heal_1)
    ice_anim.append(ice_3)
    shatter_anim.append(shatter_4)
    slash_anim.append(slash_3)

#inventory images
key_img = pygame.image.load('key.png').convert_alpha()
gold_coin_img = pygame.image.load('coin.png').convert_alpha()
silver_coin_img = pygame.image.load('silver_coin.png').convert_alpha()
copper_coin_img = pygame.image.load('copper_coin.png').convert_alpha()
potion_img = pygame.image.load('anti_venom.png').convert_alpha()
scroll_img = pygame.image.load('scroll.png').convert_alpha()
equipment_wep_img = pygame.image.load('equipment.png').convert_alpha()
equipment_hat_img = pygame.image.load('equipment_helm.png').convert_alpha()
equipment_torso_img = pygame.image.load('equipment_torso.png').convert_alpha()
ranged_img = pygame.image.load('throwing_knife.png').convert_alpha()
bread_img = pygame.image.load('bread.png').convert_alpha()

#enemy images
demon_1 = pygame.image.load('demon_1.png').convert_alpha()
demon_2 = pygame.image.load('demon_2.png').convert_alpha()
demon_3 = pygame.image.load('demon_3.png').convert_alpha()
demon_4 = pygame.image.load('demon_4.png').convert_alpha()
demon_idle = []

skeleton_img = pygame.image.load('skeleton.png').convert_alpha()
lych_img = pygame.image.load('lych.png').convert_alpha()
goblin_1 = pygame.image.load('goblin_1.png').convert_alpha()
goblin_2 = pygame.image.load('goblin_2.png').convert_alpha()
goblin_3 = pygame.image.load('goblin_3.png').convert_alpha()
goblin_idle = []

shaman_1 = pygame.image.load('shaman_1.png').convert_alpha()
shaman_2 = pygame.image.load('shaman_2.png').convert_alpha()
shaman_3 = pygame.image.load('shaman_3.png').convert_alpha()
shaman_idle = []

spider_1 = pygame.image.load('spider_1.png').convert_alpha()
spider_2 = pygame.image.load('spider_2.png').convert_alpha()

spider_idle = []

broodling_1 = pygame.image.load('broodling_1.png').convert_alpha()
broodling_2 = pygame.image.load('broodling_2.png').convert_alpha()
broodling_3 = pygame.image.load('broodling_3.png').convert_alpha()
broodling_idle = []

orc_img = pygame.image.load('orc.png').convert_alpha()
troll_img = pygame.image.load('troll.png').convert_alpha()
spider_img = pygame.image.load('spider.png').convert_alpha()
spider_queen_img = pygame.image.load('spider_queen.png').convert_alpha()
broodling_img = pygame.image.load('broodling.png').convert_alpha()
rat_1 = pygame.image.load('rat_1.png').convert_alpha()
rat_2 = pygame.image.load('rat_2.png').convert_alpha()
rat_3 = pygame.image.load('rat_3.png').convert_alpha()
rat_4 = pygame.image.load('rat_4.png').convert_alpha()
rat_idle = []
web_sac_img = pygame.image.load('websac.png').convert_alpha()

for i in range(10):
    rat_idle.append(rat_1)
    goblin_idle.append(goblin_1)
    shaman_idle.append(shaman_1)
    spider_idle.append(spider_1)
    broodling_idle.append(broodling_1)
    demon_idle.append(demon_1)
for i in range(10):
    rat_idle.append(rat_2)
    goblin_idle.append(goblin_2)
    shaman_idle.append(shaman_2)
    spider_idle.append(spider_1)
    broodling_idle.append(broodling_2)
    demon_idle.append(demon_3)
for i in range(10):
    rat_idle.append(rat_3)
    goblin_idle.append(goblin_3)
    shaman_idle.append(shaman_1)
    spider_idle.append(spider_2)
    broodling_idle.append(broodling_3)
    demon_idle.append(demon_4)
for i in range(10):
    rat_idle.append(rat_4)
    goblin_idle.append(goblin_2)
    shaman_idle.append(shaman_3)
    spider_idle.append(spider_2)
    broodling_idle.append(broodling_2)
    demon_idle.append(demon_2)
    
player_img_1 = pygame.image.load('character_1.png').convert_alpha()
player_img_2 = pygame.image.load('character_2.png').convert_alpha()
player_img_3 = pygame.image.load('character_3.png').convert_alpha()
player_img_4 = pygame.image.load('character_4.png').convert_alpha()
player_img_5 = pygame.image.load('character_5.png').convert_alpha()
player_img_6 = pygame.image.load('character_6.png').convert_alpha()
player_img_7 = pygame.image.load('character_7.png').convert_alpha()

sword_1 = pygame.image.load('sword_1.png').convert_alpha()
sword_2 = pygame.image.load('sword_2.png').convert_alpha()
sword_3 = pygame.image.load('sword_3.png').convert_alpha()
sword_4 = pygame.image.load('sword_4.png').convert_alpha()
sword_5 = pygame.image.load('sword_5.png').convert_alpha()
sword_6 = pygame.image.load('sword_6.png').convert_alpha()
sword_7 = pygame.image.load('sword_7.png').convert_alpha()

staff_1 = pygame.image.load('staff_1.png').convert_alpha()
staff_3 = pygame.image.load('staff_3.png').convert_alpha()
staff_4 = pygame.image.load('staff_4.png').convert_alpha()
staff_7 = pygame.image.load('staff_7.png').convert_alpha()

spear_1 = pygame.image.load('spear_1.png').convert_alpha()
spear_3 = pygame.image.load('spear_3.png').convert_alpha()
spear_4 = pygame.image.load('spear_4.png').convert_alpha()
spear_6 = pygame.image.load('spear_6.png').convert_alpha()

axe_1 = pygame.image.load('axe_1.png').convert_alpha()
axe_3 = pygame.image.load('axe_3.png').convert_alpha()
axe_4 = pygame.image.load('axe_4.png').convert_alpha()
axe_6 = pygame.image.load('axe_6.png').convert_alpha()

club_1 = pygame.image.load('club_1.png').convert_alpha()
club_3 = pygame.image.load('club_3.png').convert_alpha()
club_4 = pygame.image.load('club_4.png').convert_alpha()
club_6 = pygame.image.load('club_6.png').convert_alpha()

dagger_1 = pygame.image.load('dagger_1.png').convert_alpha()
dagger_3 = pygame.image.load('dagger_3.png').convert_alpha()
dagger_4 = pygame.image.load('dagger_4.png').convert_alpha()
dagger_6 = pygame.image.load('dagger_6.png').convert_alpha()

shield_1 = pygame.image.load('shield_1.png').convert_alpha()
shield_2 = pygame.image.load('shield_2.png').convert_alpha()
shield_3 = pygame.image.load('shield_3.png').convert_alpha()
shield_4 = pygame.image.load('shield_4.png').convert_alpha()
shield_5 = pygame.image.load('shield_5.png').convert_alpha()
shield_6 = pygame.image.load('shield_6.png').convert_alpha()
shield_7 = pygame.image.load('shield_7.png').convert_alpha()

relic_1 = pygame.image.load('relic_1.png').convert_alpha()
relic_3 = pygame.image.load('relic_3.png').convert_alpha()
relic_4 = pygame.image.load('relic_4.png').convert_alpha()
relic_6 = pygame.image.load('relic_6.png').convert_alpha()

totem_1 = pygame.image.load('totem_1.png').convert_alpha()
totem_2 = pygame.image.load('totem_2.png').convert_alpha()
totem_3 = pygame.image.load('totem_3.png').convert_alpha()
totem_4 = pygame.image.load('totem_4.png').convert_alpha()
totem_5 = pygame.image.load('totem_5.png').convert_alpha()
totem_6 = pygame.image.load('totem_6.png').convert_alpha()
totem_7 = pygame.image.load('totem_7.png').convert_alpha()

knife_1 = pygame.image.load('knife_1.png').convert_alpha()
knife_3 = pygame.image.load('knife_3.png').convert_alpha()
knife_4 = pygame.image.load('knife_4.png').convert_alpha()
knife_6 = pygame.image.load('knife_6.png').convert_alpha()

plate_1 = pygame.image.load('plate_1.png').convert_alpha()
plate_2 = pygame.image.load('plate_2.png').convert_alpha()
plate_3 = pygame.image.load('plate_3.png').convert_alpha()
plate_4 = pygame.image.load('plate_4.png').convert_alpha()
plate_5 = pygame.image.load('plate_5.png').convert_alpha()
plate_6 = pygame.image.load('plate_6.png').convert_alpha()
plate_7 = pygame.image.load('plate_7.png').convert_alpha()

leather_1 = pygame.image.load('leather_1.png').convert_alpha()
leather_2 = pygame.image.load('leather_2.png').convert_alpha()
leather_3 = pygame.image.load('leather_3.png').convert_alpha()
leather_4 = pygame.image.load('leather_4.png').convert_alpha()
leather_6 = pygame.image.load('leather_6.png').convert_alpha()

robe_1 = pygame.image.load('robe_1.png').convert_alpha()
robe_2 = pygame.image.load('robe_2.png').convert_alpha()
robe_3 = pygame.image.load('robe_3.png').convert_alpha()
robe_4 = pygame.image.load('robe_4.png').convert_alpha()
robe_5 = pygame.image.load('robe_5.png').convert_alpha()
robe_6 = pygame.image.load('robe_6.png').convert_alpha()

mail_1 = pygame.image.load('mail_1.png').convert_alpha()
mail_2 = pygame.image.load('mail_2.png').convert_alpha()
mail_3 = pygame.image.load('mail_3.png').convert_alpha()
mail_4 = pygame.image.load('mail_4.png').convert_alpha()
mail_5 = pygame.image.load('mail_5.png').convert_alpha()
mail_6 = pygame.image.load('mail_6.png').convert_alpha()
mail_7 = pygame.image.load('mail_7.png').convert_alpha()

plate_helm_1 = pygame.image.load('plate_helm_1.png').convert_alpha()
plate_helm_5 = pygame.image.load('plate_helm_5.png').convert_alpha()
plate_helm_6 = pygame.image.load('plate_helm_6.png').convert_alpha()

mail_helm_1 = pygame.image.load('mail_helm_1.png').convert_alpha()
mail_helm_5 = pygame.image.load('mail_helm_5.png').convert_alpha()
mail_helm_6 = pygame.image.load('mail_helm_6.png').convert_alpha()

hat_1 = pygame.image.load('hat_1.png').convert_alpha()
hat_5 = pygame.image.load('hat_5.png').convert_alpha()
hat_6 = pygame.image.load('hat_6.png').convert_alpha()

hood_1 = pygame.image.load('hood_1.png').convert_alpha()
hood_5 = pygame.image.load('hood_5.png').convert_alpha()
hood_6 = pygame.image.load('hood_6.png').convert_alpha()

guantlet_1 = pygame.image.load('guantlet_1.png').convert_alpha()
guantlet_3 = pygame.image.load('guantlet_3.png').convert_alpha()
guantlet_4 = pygame.image.load('guantlet_4.png').convert_alpha()
guantlet_6 = pygame.image.load('guantlet_6.png').convert_alpha()

gloves_1 = pygame.image.load('gloves_1.png').convert_alpha()
gloves_3 = pygame.image.load('gloves_3.png').convert_alpha()
gloves_4 = pygame.image.load('gloves_4.png').convert_alpha()
gloves_6 = pygame.image.load('gloves_6.png').convert_alpha()



plate_helm_idle = []
plate_idle = []
leather_idle = []
guantlet_idle = []
gloves_idle = []
mail_idle = []
player_idle = []
sword_idle = []
axe_idle = []
spear_idle = []
staff_idle = []
dagger_idle = []
shield_idle = []
relic_idle = []
knife_idle = []
totem_idle = []
club_idle = []
hat_idle = []
hood_idle = []
robe_idle = []
mail_helm_idle = []

for i in range(10):
    player_idle.append(player_img_1)
    plate_idle.append(plate_1)
    mail_idle.append(mail_1)
    sword_idle.append(sword_1)
    shield_idle.append(shield_1)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_1)
    relic_idle.append(relic_1)
    dagger_idle.append(dagger_1)
    knife_idle.append(knife_1)
    spear_idle.append(spear_1)
    totem_idle.append(totem_1)
    guantlet_idle.append(guantlet_1)
    gloves_idle.append(gloves_1)
    axe_idle.append(axe_1)
    club_idle.append(club_1)
    leather_idle.append(leather_1)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_1)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_2)
    plate_idle.append(plate_2)
    mail_idle.append(mail_2)
    sword_idle.append(sword_2)
    shield_idle.append(shield_2)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_1)
    relic_idle.append(relic_1)
    dagger_idle.append(dagger_1)
    knife_idle.append(knife_1)
    spear_idle.append(spear_1)
    totem_idle.append(totem_2)
    guantlet_idle.append(guantlet_1)
    gloves_idle.append(gloves_1)
    axe_idle.append(axe_1)
    club_idle.append(club_1)
    leather_idle.append(leather_2)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_2)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_3)
    plate_idle.append(plate_3)
    mail_idle.append(mail_3)
    sword_idle.append(sword_3)
    shield_idle.append(shield_3)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_3)
    relic_idle.append(relic_3)
    dagger_idle.append(dagger_3)
    knife_idle.append(knife_3)
    spear_idle.append(spear_3)
    totem_idle.append(totem_3)
    guantlet_idle.append(guantlet_3)
    gloves_idle.append(gloves_3)
    axe_idle.append(axe_3)
    club_idle.append(club_3)
    leather_idle.append(leather_3)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_3)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_4)
    plate_idle.append(plate_4)
    mail_idle.append(mail_4)
    sword_idle.append(sword_4)
    shield_idle.append(shield_4)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_4)
    relic_idle.append(relic_4)
    dagger_idle.append(dagger_4)
    knife_idle.append(knife_4)
    spear_idle.append(spear_4)
    totem_idle.append(totem_4)
    guantlet_idle.append(guantlet_4)
    gloves_idle.append(gloves_4)
    axe_idle.append(axe_4)
    club_idle.append(club_4)
    leather_idle.append(leather_4)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_4)
    mail_helm_idle.append(mail_helm_1)
for i in range(13):
    player_idle.append(player_img_5)
    plate_idle.append(plate_5)
    mail_idle.append(mail_5)
    sword_idle.append(sword_5)
    shield_idle.append(shield_5)
    plate_helm_idle.append(plate_helm_5)
    staff_idle.append(staff_1)
    relic_idle.append(relic_4)
    dagger_idle.append(dagger_1)
    knife_idle.append(knife_4)
    spear_idle.append(spear_1)
    totem_idle.append(totem_5)
    guantlet_idle.append(guantlet_4)
    gloves_idle.append(gloves_4)
    axe_idle.append(axe_1)
    club_idle.append(club_1)
    leather_idle.append(leather_4)
    hat_idle.append(hat_5)
    hood_idle.append(hood_5)
    robe_idle.append(robe_5)
    mail_helm_idle.append(mail_helm_5)
for i in range(10):
    player_idle.append(player_img_1)
    plate_idle.append(plate_1)
    mail_idle.append(mail_1)
    sword_idle.append(sword_1)
    shield_idle.append(shield_1)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_1)
    relic_idle.append(relic_1)
    dagger_idle.append(dagger_1)
    knife_idle.append(knife_1)
    spear_idle.append(spear_1)
    totem_idle.append(totem_1)
    guantlet_idle.append(guantlet_1)
    gloves_idle.append(gloves_1)
    axe_idle.append(axe_1)
    club_idle.append(club_1)
    leather_idle.append(leather_1)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_1)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_2)
    plate_idle.append(plate_2)
    mail_idle.append(mail_2)
    sword_idle.append(sword_2)
    shield_idle.append(shield_2)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_1)
    relic_idle.append(relic_1)
    dagger_idle.append(dagger_1)
    knife_idle.append(knife_1)
    spear_idle.append(spear_1)
    totem_idle.append(totem_2)
    guantlet_idle.append(guantlet_1)
    gloves_idle.append(gloves_1)
    axe_idle.append(axe_1)
    club_idle.append(club_1)
    leather_idle.append(leather_2)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_2)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_3)
    plate_idle.append(plate_3)
    mail_idle.append(mail_3)
    sword_idle.append(sword_3)
    shield_idle.append(shield_3)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_3)
    relic_idle.append(relic_3)
    dagger_idle.append(dagger_3)
    knife_idle.append(knife_3)
    spear_idle.append(spear_3)
    totem_idle.append(totem_3)
    guantlet_idle.append(guantlet_3)
    gloves_idle.append(gloves_3)
    axe_idle.append(axe_3)
    club_idle.append(club_3)
    leather_idle.append(leather_3)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_3)
    mail_helm_idle.append(mail_helm_1)
for i in range(10):
    player_idle.append(player_img_4)
    plate_idle.append(plate_4)
    mail_idle.append(mail_4)
    sword_idle.append(sword_4)
    shield_idle.append(shield_4)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_4)
    relic_idle.append(relic_4)
    dagger_idle.append(dagger_4)
    knife_idle.append(knife_4)
    spear_idle.append(spear_4)
    totem_idle.append(totem_4)
    guantlet_idle.append(guantlet_4)
    gloves_idle.append(gloves_4)
    axe_idle.append(axe_4)
    club_idle.append(club_4)
    leather_idle.append(leather_4)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_4)
    mail_helm_idle.append(mail_helm_1)
for i in range(15):
    player_idle.append(player_img_6)
    plate_idle.append(plate_6)
    mail_idle.append(mail_6)
    sword_idle.append(sword_6)
    shield_idle.append(shield_6)
    plate_helm_idle.append(plate_helm_6)
    staff_idle.append(staff_7)
    relic_idle.append(relic_6)
    dagger_idle.append(dagger_6)
    knife_idle.append(knife_6)
    spear_idle.append(spear_6)
    totem_idle.append(totem_6)
    guantlet_idle.append(guantlet_6)
    gloves_idle.append(gloves_6)
    axe_idle.append(axe_6)
    club_idle.append(club_6)
    leather_idle.append(leather_6)
    hat_idle.append(hat_6)
    hood_idle.append(hood_6)
    robe_idle.append(robe_6)
    mail_helm_idle.append(mail_helm_6)
for i in range(7):
    player_idle.append(player_img_7)
    plate_idle.append(plate_7)
    mail_idle.append(mail_7)
    sword_idle.append(sword_7)
    shield_idle.append(shield_7)
    plate_helm_idle.append(plate_helm_1)
    staff_idle.append(staff_7)
    relic_idle.append(relic_6)
    dagger_idle.append(dagger_6)
    knife_idle.append(knife_6)
    spear_idle.append(spear_6)
    totem_idle.append(totem_7)
    guantlet_idle.append(guantlet_6)
    gloves_idle.append(gloves_6)
    axe_idle.append(axe_6)
    club_idle.append(club_6)
    leather_idle.append(leather_6)
    hat_idle.append(hat_1)
    hood_idle.append(hood_1)
    robe_idle.append(robe_6)
    mail_helm_idle.append(mail_helm_1)
    


axe_img = pygame.image.load('axe.png').convert_alpha()
club_img = pygame.image.load('club.png').convert_alpha()
robe_img = pygame.image.load('robe.png').convert_alpha()
leather_img = pygame.image.load('leather.png').convert_alpha()
cloth_helm_img = pygame.image.load('cloth_helm.png').convert_alpha()
leather_helm_img = pygame.image.load('hat.png').convert_alpha()
mail_helm_img = pygame.image.load('mail_helm.png').convert_alpha()
mail_boots_img = pygame.image.load('mail_boots.png').convert_alpha()
plate_boots_img = pygame.image.load('plate_boots.png').convert_alpha()
leather_boots_img = pygame.image.load('leather_boots.png').convert_alpha()
leather_gloves_img = pygame.image.load('leather_gloves.png').convert_alpha()
plate_gloves_img = pygame.image.load('plate_gloves.png').convert_alpha()
totem_img = pygame.image.load('totem.png').convert_alpha()

#used when player has nothing equiped
no_equipment = Equipment('    ',[None],equipment_wep_img,0,0,0,0,0,0,0,'no equipment',0,0,'')
no_helm = Equipment('    ',[None],equipment_hat_img,0,0,0,0,0,0,0,'no equipment',0,0,'')
no_torso = Equipment('    ',[None],equipment_torso_img,0,0,0,0,0,0,0,'no equipment',0,0,'')

cash_bag = []
for i in range(1,31):
    starter_cash = Item('Copper Coin','currency',1,copper_coin_img,0.1)
    cash_bag.append(starter_cash)
silver_coin = Item('Silver Coin','currency',20,silver_coin_img,0.1)
bandage = Item('Linen Bandage','bandage',10,scroll_img,2)
food = Item('Bread','food',10,bread_img,0.3)
pick = Item('Lock Pick','key',1,key_img,0.1)
test_fire = Item('Fire Scroll','scroll',30,scroll_img,0.2)
test_thunder = Item('Thunder Scroll','scroll',30,scroll_img,0.2)
flame_key = Item('Flame Key','key',100,key_img,0.1)
ice_key = Item('Ice Key','key',100,key_img,0.1)
skull_key = Item('Skull Key','key',100,key_img,0.1)
key = Item('Copper Key','key',100,key_img,0.1)


player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_idle,8,8,8,8,8,8,30,8,8,no_equipment,no_torso,[[silver_coin],[silver_coin],[test_fire],cash_bag,[bandage],[food],[pick]])

player.modify_stats()

shadow_group = pygame.sprite.Group()
player_sprite = pygame.sprite.RenderPlain((player))
all_group = pygame.sprite.Group()
all_group.add(player)
effect_group = pygame.sprite.Group()
npc_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
spawner_group = pygame.sprite.Group()
reticule = Target()


village_objects = []

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 18)
font3 = pygame.font.Font(None,18)

item_map_open = False
make_village()
village = my_map
#make_dungeon()
dungeon_1 = None
dark_list = calc_field_of_view(player)
    

shadow_group.empty()
for i in dark_list:
    
    shadow = Shadow(i.x1,i.y1)
    shadow_group.add(shadow)
    print shadow.map_x,shadow.map_y
    


spawnlings = []


text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))

render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)
    render_all()
    effect_group.update()
    all_group.update()
    if len(effect_group)<=0:
        
        handle_keys()
    
    
    
    pygame.display.flip()
    


#if __name__== '__main__': main()
