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
max_monsters = 4
max_goblins = 4
max_rats = 3
max_spiders = 3
monster_str = 1
max_items = 4

level_up_base = 200
level_up_factor = 150

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
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))
item_map = pygame.Surface((700,700))
item_tmp_map = pygame.Surface((700,700))
item_map_open = False


gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width,3*tile_height+40))
equipment = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width,3*tile_height +40))

inventory_background = pygame.Surface((5*tile_width,5*tile_height))
inventory_1 = pygame.Surface((240,490))
inventory_2 = pygame.Surface((240,490))
trade_gui = pygame.Surface((460,100))


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


class Treasure(pygame.sprite.Sprite):

    def __init__(self,x,y,img,contains,name,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.blocks = blocks
        self.name = name

        self.inventory = contains

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
                    img = broodling_img
                    attack = 3+monster_str
                    defence = 3+monster_str
                    m_attk = 0
                    m_def = 0
                    hit = 4+monster_str
                    dodge = 6+monster_str
                    hp = 15+monster_str
                    char = 0
                    per = 0
                    xp = 1
                    weapon = None
                    armour = None
                    if self.can_spawn(x,y):
                        monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,weapon,armour,[],xp)
                        monster.current_x = monster.dest_x
                        monster.current_y = monster.dest_y
                        monster_group.add(monster)
                        all_group.add(monster)
                        
            

class Trap(pygame.sprite.Sprite):
    
    def __init__(self,x,y,img,name):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.map_x = x
        self.map_y = y
        self.rect.x = x
        self.rect.y = y
        self.name = name
        
    def trigger(self):
        if self.name == 'web':
            player.frozen = True
            player.frozen_timer = 2
            
class Item():
    def __init__(self,name,kind,val,img,weight):
        self.name = name
        self.inv_img = img
        self.category = kind
        self.description = "I am an item that needs a proper description"
        self.value = val
        self.stackable = True
        self.counted = False
        
        self.weight = weight

class Equipment(pygame.sprite.Sprite):

    def __init__(self,name,p_img,inv_img,attk,de,m_attk,m_de,hit,dodge,cha,per,slash,smash,stab,fire,ice,thunder,dark,kind,weight,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.inv_img = inv_img
        self.player_img = p_img
        self.blocks = blocks
        self.name = name
        self.description = None
        self.category = kind

        
        
        #stats
        self.slash = slash
        self.smash = smash
        self.stab = stab
        self.fire = fire
        self.ice = ice
        self.thunder = thunder
        self.dark = dark

        self.attk_pwr = attk
        self.defence = de
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = m_attk
        self.magic_def = m_de
        self.charisma = cha #used in bartering
        self.perception = per #used to locate secret doors traps

        self.weight = weight
        
        self.value = attk+de+m_attk+m_de+hit+dodge+cha+per+slash+smash+stab+fire+ice+thunder+dark
        self.stackable = False
        self.counted = False

class Character(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,de,m_attk,m_de,hit,dodge,hp,cha,per,wep,arm,inventory,xp=None,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
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


        #equipment
        self.armour = arm
        self.weapon = wep
        self.helm = None
        self.boots = None
        self.offhand = None

        #base stats
        self.strength = 0
        self.intelligence = 0
        self.cunning = 0

        self.xp = xp
        if self.xp == None:
            self.xp = 0
        self.level = 1
        self.level_up_points = 0

        #player base stats based on level and equipment
        self.attk_pwr = attk
        self.defence = de
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = m_attk
        self.magic_def = m_de
        self.charisma = cha #used in bartering
        self.perception = per
        
        

        #copy of stats used in modify stats when equiping items these go up permanently on level up
        self.c_attk_pwr = attk
        self.c_defence = de
        self.c_hit = hit
        self.c_dodge = dodge
        self.c_magic_attk = m_attk
        self.c_magic_def = m_de
        self.c_charisma = cha #used in bartering
        self.c_perception = per
        self.c_max_hp = hp


        self.max_hp = hp
        self.hp = self.max_hp
        self.wounds = 0 #prevents healing to max hp
        self.action_points = 10

        self.disease = None #apply stat altering class
        self.poison = False
        
        self.inventory = inventory
        self.current_weight = 0 #based on current inventory
        #for i in self.inventory:
        #    for j in i:
        #        self.current_weight +=j.weight
        #print self.current_weight
        self.max_weight = 30 #based on strength
        

        self.frozen = False
        self.frozen_timer = 0



    def modify_stats(self):#when equiping new equipment etc

        self.current_weight = 0
        for i in self.inventory:
            for j in i:
                self.current_weight +=j.weight
        print "player weight = ", self.current_weight
        
        attk_pwr = self.c_attk_pwr
        defence = self.c_defence
        hit = self.c_hit
        dodge = self.c_dodge
        magic_attk = self.c_magic_attk
        magic_def = self.c_magic_def
        charisma = self.c_charisma
        perception = self.c_perception
        

        if self.armour is not None:
            attk_pwr = attk_pwr + self.armour.attk_pwr
            defence = defence + self.armour.defence
            hit = hit + self.armour.hit
            dodge = dodge + self.armour.dodge
            magic_attk = magic_attk + self.armour.magic_attk
            magic_def = magic_def + self.armour.magic_def
            charisma = charisma + self.armour.charisma
            perception = perception + self.armour.perception
            

        if self.helm is not None:
            attk_pwr = attk_pwr + self.helm.attk_pwr
            defence = defence + self.helm.defence
            hit = hit + self.helm.hit
            dodge = dodge + self.helm.dodge
            magic_attk = magic_attk + self.helm.magic_attk
            magic_def = magic_def + self.helm.magic_def
            charisma = charisma + self.helm.charisma
            perception = perception + self.helm.perception
          

        if self.weapon is not None:
            attk_pwr = attk_pwr + self.weapon.attk_pwr
            defence = defence + self.weapon.defence
            hit = hit + self.weapon.hit
            dodge = dodge + self.weapon.dodge
            magic_attk = magic_attk + self.weapon.magic_attk
            magic_def = magic_def + self.weapon.magic_def
            charisma = charisma + self.weapon.charisma
            perception = perception + self.weapon.perception
            

        if self.offhand is not None:
            attk_pwr = attk_pwr + self.offhand.attk_pwr
            defence = defence + self.offhand.defence
            hit = hit + self.offhand.hit
            dodge = dodge + self.offhand.dodge
            magic_attk = magic_attk + self.offhand.magic_attk
            magic_def = magic_def + self.offhand.magic_def
            charisma = charisma + self.offhand.charisma
            perception = perception + self.offhand.perception
            

        self.attk_pwr = attk_pwr
        self.defence = defence
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = magic_attk
        self.magic_def = magic_def
        self.charisma = charisma
        self.perception = perception
        


        self.max_hp = self.c_max_hp - self.wounds

                
    def decision(self):
        
        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)

        if self.map_x == self.dest_x and self.map_y == self.dest_y:
            if not self.frozen:
            

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
             

    def update(self):
        
        
        if self.dest_x > self.current_x:
            self.current_x +=10
        else:
            self.map_x = self.current_x
            self.map_y = self.current_y
 
            
        if self.dest_x < self.current_x:
            
            self.current_x -=10
        else:
            self.map_x = self.current_x
            self.map_y = self.current_y
                
            
        if self.dest_y > self.current_y:
            
            self.current_y +=10
        else:
            self.map_x = self.current_x
            self.map_y = self.current_y
            
            
        if self.dest_y < self.current_y:
            
            self.current_y -=10 
              
        else:
            self.map_x = self.current_x
            self.map_y = self.current_y
            
            

        

    def monster_move(self,x,y):

        target = None
        dest_x = self.map_x + x
        dest_y = self.map_y + y

        if (dest_x == player.current_x and dest_y == player.current_y) or \
        (dest_x == player.dest_x and dest_y == player.dest_y):
                target = player

        if target is not None:
            self.attack(target)
            player.moving = False
            
        else:
            if self.name == 'Spinner':
                web_chance = random.randint(1,10)
                if web_chance <= 4:
                    web = Trap(self.map_x,self.map_y,web_img,'web')
                    trap_group.add(web)
                    self.move(x,y)
                else:
                    self.move(x,y)
                    
            if self.name == 'Spider Queen':
                sac_chance = random.randint(1,10)
                if sac_chance <=3:
                    print "currently at" ,self.map_x,self.map_y
                    print "attempting to lay" ,x,y
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
                            if calc_fov(self.map_x/tile_width,self.map_y/tile_height,player.map_x/tile_width,player.map_y/tile_height):
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
        
        
        if not self.frozen:
                
            if self.poison == True:
                self.hp -= random.randint(1,5)
                txt = 'you lose hp from poison'
                if self.hp < 0:
                    self.hp = 0
                    text = "you succumb to the poison"
                    col = (100,100,10)
                    updateGUI(text,col)
                    self.death()
                else:
                    updateGUI(txt,(10,10,10))

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
                    trap.trigger()
                    self.moving=False
                

            for npc in npc_group:
                if dest_x == npc.map_x and dest_y == npc.map_y:
                    friendly_target = npc
                    self.moving = False
            if friendly_target is not None:
                open_inventory(self.inventory,friendly_target,'trade')

            if my_map[dest_x/tile_width][dest_y/tile_height].door:
                self.moving = False
                if my_map[dest_x/tile_width][dest_y/tile_height].locked:
                    text = "The door is locked"
                    for i in self.inventory:
                        
                        if len(i)>=1:
                            if i[0].category == 'key':
                                
                                text = "You unlock the door"
                                my_map[dest_x/tile_width][dest_y/tile_height].locked = False
                                i.pop()
                                stack_inventory(player)
                                break
                        else:
                            text = "The door is locked"
                else:
                    
                    my_map[dest_x/tile_width][dest_y/tile_height].blocked = False
                    my_map[dest_x/tile_width][dest_y/tile_height].door = False
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
                for t in trap_group:
                    if t.map_x == self.map_x and t.map_y == self.map_y:
                        t.kill()
                    



    def cast_spell(self,spell):

        aoe_targets = [(self.dest_x + tile_width,self.map_y),(self.dest_x - tile_width,self.dest_y),\
            (self.dest_x,self.dest_y + tile_height),(self.dest_x,self.dest_y-tile_height)]
        spell_targets = []

        if spell == 'heal_spell':
            spell_power = random.randint(10,30)
            heal = spell_power + self.magic_attk
            self.hp += heal
            text = '%s gain %s from heal spell' % (self.name,heal)
            if self.hp >= self.max_hp:
                self.hp = self.max_hp
            


            updateGUI(text,(100,100,10))

        elif spell == 'fire_spell':

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
                spell_power = random.randint(10,30)
                spell_dmg = (spell_power + self.magic_attk)- target.magic_def
                if self.weapon is not None:
                    if target.armour is not None:
                        fire = self.weapon.fire - target.armour.fire
                    else:
                        fire = self.weapon.fire
                else:
                    fire = 0
                if fire <=0:
                    fire=0
                dmg = spell_dmg+fire
                if dmg <= 0:
                    dmg = 1
                target.hp -= dmg
                text = "%s hits %s with %s fire damage" % (self.name,target.name,dmg)
                if target.hp < 0:
                    target.hp = 0
                    text = "%s burns to death" % target.name
                    col = (100,100,10)
                    updateGUI(text,col)
                    target.death()


                tmp_map.blit(scorch_img,(target.dest_x,target.dest_y))
                updateGUI(text,(100,100,10))



        elif spell == 'ice_spell':

            for target in aoe_targets:
                if target == (player.dest_x,player.dest_y):
                    spell_target = player
                    spell_targets.append(spell_target)

                for monster in monster_group:
                    if target == (monster.dest_x,monster.dest_y):
                        spell_target = monster
                        spell_targets.append(spell_target)
            for target in spell_targets:
                spell_power = random.randint(5,10)
                spell_dmg = (spell_power + self.magic_attk) - target.magic_def
                if self.weapon is not None:
                    if target.armour is not None:
                        ice = self.weapon.ice - target.armour.ice
                    else:
                        ice = self.weapon.ice
                else:
                    ice = 0
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


        else:
            text = 'you fail to cast spell'
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
            
            attack_roll = random.randint(1,20)
            attack = attack_roll + self.attk_pwr
            
            if self.weapon is not None:
                slash = self.weapon.slash 
                smash = self.weapon.smash 
                stab = self.weapon.stab
            dmg = attack+slash+smash+stab
            if dmg <= 0:
                dmg = 1
            target.hp -= dmg
            txt = "you hit %s for %s" %(target.name,dmg)
            if target.hp<=0:
                target.hp = 0
                txt = "%s is destroyd" %target.name
                target.kill()
            updateGUI(txt,(10,10,10))
            
        
        else:
            hit_roll = random.randint(1,20)
            hit_chance = hit_roll + self.hit
            miss_roll = random.randint(1,20)
            miss_chance = miss_roll + target.dodge
    
            if hit_chance >= miss_chance:
                attack_roll = random.randint(1,20)
                attack = attack_roll + self.attk_pwr
                mit_roll = random.randint(1,20)
                mitigate = mit_roll + target.defence
    
                if self.weapon is not None and target.armour is not None:
                    slash = self.weapon.slash - target.armour.slash
                    smash = self.weapon.smash - target.armour.smash
                    stab = self.weapon.stab - target.armour.stab
                elif self.weapon == None and target.armour is not None:
                    slash = 0
                    smash = 0
                    stab = 0
                elif self.weapon is not None and target.armour == None:
                    slash = self.weapon.slash - 0
                    smash = self.weapon.smash - 0
                    stab = self.weapon.stab - 0
                else:
                    slash = 0
                    smash = 0
                    stab = 0
    
                if slash <= 0:
                    slash = 0
                if smash <= 0:
                    smash = 0
                if stab <= 0:
                    stab = 0
    
    
                target.injured = True
    
                if attack_roll == 20:
                    dmg = (attack-(mitigate/2))  + slash+smash+stab
                    target.wounds += 10
                    if target.wounds >= 80:
                        target.wounds = 80
                    if target.hp >target.max_hp:
                        target.hp=target.max_hp
                    target.modify_stats()
                    text = "%s recieves a seriouse wound" %target.name
                    col = (10,10,10)
                    updateGUI(text,col)
    
                else:
   
                    dmg = (attack - mitigate)+slash+smash+stab
    
                if dmg <= 0:
                    dmg = 1
                target.hp -= dmg
                if self.name == 'Spinner' or self.name == 'Spider_Queen':
                    if random.randint(1,10) <=6:
                        target.poison = True
                        txt = 'you have been poisoned'
                        updateGUI(txt,(10,10,10))
                if target.hp <= 0:
                    target.hp = 0
                    text = "%s DIE!!!" % target.name
                    updateGUI(text,(100,10,10))
                    target.death()
    
                else:
    
                    text = "%s hit %s for %s damage" % (self.name,target.name,dmg)
                    col = (10,10,10)
                    updateGUI(text,col)
                if is_blocked((target.dest_x-100)/tile_width,target.dest_y/tile_width) and is_blocked((target.dest_x+100)/tile_width,target.dest_y/tile_width):
                    blood_x = random.randint(target.dest_x-10,target.dest_x+10)
                elif is_blocked((target.dest_x-100)/tile_width,target.dest_y/tile_height) and not is_blocked((target.dest_x+100)/tile_width,target.dest_y/tile_height):
                    blood_x = random.randint(target.dest_x-10,target.dest_x+50)
                elif is_blocked((target.dest_x+100)/tile_width,target.dest_y/tile_height) and not is_blocked((target.dest_x-100)/tile_width,target.dest_y/tile_height):
                    blood_x = random.randint(target.dest_x-50,target.dest_x+10)
                else:
                    blood_x = random.randint(target.dest_x-50,target.dest_x+50)
    
                if is_blocked(target.dest_x/tile_width,(target.dest_y-100)/tile_width) and is_blocked(target.dest_x/tile_width,(target.dest_y+100)/tile_width):
                    blood_y = random.randint(target.dest_y-10,target.dest_y+10)
                elif is_blocked(target.dest_x/tile_width,(target.dest_y-100)/tile_height) and not is_blocked(target.dest_x/tile_width,(target.dest_y+100)/tile_height):
                    blood_y = random.randint(target.dest_y-10,target.dest_y+50)
                elif is_blocked(target.dest_x/tile_width,(target.dest_y+100)/tile_height) and not is_blocked(target.dest_x/tile_width,(target.dest_y-100)/tile_height):
                    blood_y = random.randint(target.dest_y-50,target.dest_y+10)
                else:
                    blood_y = random.randint(target.dest_y-50,target.dest_y+50)
                tmp_map.blit(blood_img,(blood_x,blood_y))
                render_all()
    
            else:
    
                text = " %s dodges %s attack" % (target.name,self.name)
                col = (10,10,10)
                updateGUI(text,col)


    def death(self):


        tmp_map.blit(corpse_img, (self.current_x,self.current_y))
        self.kill()

        if self == player:
            self.armour = None
            self.weapon = None
            self.helm = None
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
                loot = Treasure(self.map_x/tile_width,self.map_y/tile_height,corpse_img,loot_list,'Corpse')
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
            elif event.key == K_e:
                examine_object()
            elif event.key == K_f:
                pickup_object()
                for m in monster_group:
                    m.decision()

            #hotkeys
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
        


def pickup_object():


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
            open_inventory(player.inventory,item,'loot')

            contents = len(item.inventory)
            if contents <=0:
                treasure_group.remove(item)
                item.kill()
            render_all()



def use_equip(item):
    
    if item.category == 'armour':
        if player.armour is not None:
            player.inventory.append([player.armour])
        player.armour = item
        text = "you equip %s"%item.name
        
        player.modify_stats()
    if item.category == 'weapon':
        if player.weapon is not None:
            player.inventory.append([player.weapon])
        player.weapon = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'helm':
        if player.helm is not None:
            player.inventory.append([player.helm])
        player.helm = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'off hand':
        if player.offhand is not None:
            player.inventory.append([player.offhand])
        player.offhand = item
        text = "you wield %s"%item.name
        player.modify_stats()
        
    if item.category == 'scroll':
        print "scroll"
        print item.name
        if item.name == 'Fire Scroll':
            print "fire"
            player.cast_spell('fire_spell')
            text = "You use a Fire Scroll"
            print text
        elif item.name == 'Ice Scroll':
            player.cast_spell('ice_spell')
            text = "You use an Ice Scroll" 
        elif item.name == 'Health Scroll':
            player.cast_spell('heal_spell')
            text = "You use a Health Scroll"

    if item.category == 'bandage':
        player.wounds -= 5
        text = "you bandage your wounds"
        if player.wounds <=0:
            player.wounds = 0
        player.modify_stats()
    if item.category == 'potion':
        if item.name == 'Anti Venom':
            player.poison = False
            text = "you cure the poison"
    
    updateGUI(text,(10,10,100))

def examine_object():

    color = (10,10,150)

    for item in treasure_group:
        if player.dest_x == item.map_x and player.dest_y == item.map_y:
            text = "A %s with loot" %item.name
            updateGUI(text,(color))

    if my_map[player.dest_x/tile_width][player.dest_y/tile_height].stairs_down:
        text = "you have discovered an exit point"
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


def generate_name(n_type,tier):

    if n_type == 'sword':
        list_b = ['Sword ','Blade ','Saber ','Great Sword ','Bastard Sword ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Steel ', 'Silver ','Honed ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'spear':
        list_b = ['Spear ','Trident ','Halberd ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Steel ', 'Silver ','Honed ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
       
    if n_type == 'axe':
        list_b = ['Axe ','Hatchet ','Great Axe ','Battle Axe ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Steel ', 'Silver ','Honed ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'dagger':
        list_b = ['Dagger ','Dirk ','Knife ','Blade ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Steel ', 'Silver ','Honed ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        


    if n_type == 'club':
        list_b = ['Cudgel ','Maul ','Mace ','Hammer ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Steel ', 'Silver ','Honed ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'staff':
        list_b = ['Staff ','Great Staff ','Totem ']
        if tier == 1:
            list_a = ['Wooden ' ,'Yew ','Magic ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Thunder ', 'Fire ','Ice ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'robe':
        list_b = ['Robe ','Garment ','Cloak ']
        if tier == 1:
            list_a = ['Cotton ' ,'Silk ','Linen ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Thunder ', 'Fire ','Ice ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'leather':
        list_b = ['Vest ','Fatigue ','Huberk ']
        if tier == 1:
            list_a = ['Leather ' ,'Hide ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Foresters ', 'Hunters ','Rogues ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'mail':
        list_b = ['Chainmail ','Mail ','Coif ','Links ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Padded ', 'Fine ','Silver ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        
    if n_type == 'plate':
        list_b = ['Armour ','Platemail ','Huberk ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Splendid ', 'Polished ','Silver ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
       

    if n_type == 'metal helm':
        list_b = ['Helmet ','Gorget ','Skull Cap ']
        if tier == 1:
            list_a = ['Rusty ' ,'Iron ','Steel ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Splendid ', 'Polished ','Silver ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'cloth helm':
        list_b = ['Cowel ','Hood ','Cap ']
        if tier == 1:
            list_a = ['Linen ' ,'Tattered ','Simple ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Splendid ','Silk ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        

    if n_type == 'leather helm':
        list_b = ['Hat ','Cap ']
        if tier == 1:
            list_a = ['Tattered ' ,'Woven ','Straw ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        elif tier == 2:
            list_a = ['Splendid ', 'Fine ','Leather ']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_1+name_2
        
    return name

def generate_item():

    random_roll = random.randint(1,100)
    if random_roll <= 10:
        item = Item('Health Scroll','scroll',30,scroll_img,0.2)

    elif random_roll <= 20:
        item = Item('Fire Scroll','scroll',30,scroll_img,0.2)

    elif random_roll <= 30:
        item = Item('Ice Scroll','scroll',30,scroll_img,0.2)

    elif random_roll <= 31:
        item = Item('Copper Key','key',1,key_img,0.2)
        
    elif random_roll <= 90:
        item = Item('Anti Venom','potion',20,potion_img,0.3)
    else:
        item = Item('Linen Bandage','bandage',10,scroll_img,0.2)
    return item



def generate_equipment(cat):#generate an item at rect with category


    random_tier = random.randint(1,100)
    if random_tier <=90-monster_str:
        tier = 1
    else: 
        tier = 2
    

    item_type = cat

    if item_type == 'wep':
        kind = 'weapon'
        #weapon_list = 1=sword 2=spear 3=axe 4=dagger 5=club 6=staff
        weapon_type = random.randint(1,6)
        if weapon_type == 1:

            name = generate_name('sword',tier)
            p_img = sword_img
            inv_img = equipment_img
            slash = random.randint(3,7+(tier*2))
            smash = random.randint(0,0)
            stab = random.randint(2,6+(tier*2))
            fire = random.randint(0,2)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,1)

            attk = random.randint(3,7+(tier*2))
            de = random.randint(0,0)
            hit = random.randint(3,7+(tier*2))
            dodge = random.randint(-2,0)
            m_attk = random.randint(0,3+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(3,7)
            per = random.randint(0,0)
            
            weight = random.randint(5,7)

        elif weapon_type == 2:
            name = generate_name('spear',tier)
            p_img = spear_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(5,11+(tier*2))
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(-1,3)

            attk = random.randint(3,7+(tier*2))
            de = random.randint(0,2)
            hit = random.randint(4,9+(tier*2))
            dodge = random.randint(0,0)
            m_attk = random.randint(0,2+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(0,3)
            per = random.randint(0,3)
       
            weight = random.randint(5,7)


        elif weapon_type == 3:
            name = generate_name('axe',tier)
            p_img = axe_img
            inv_img = equipment_img
            slash = random.randint(3,8)
            smash = random.randint(2,6)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,2)
            dark = random.randint(-1,3)

            attk = random.randint(3,7+(tier*2))
            de = random.randint(0,0)
            hit = random.randint(1,5+(tier*2))
            dodge = random.randint(-1,0)
            m_attk = random.randint(0,2+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(0,1)
            per = random.randint(0,0)
 
            weight = random.randint(5,7)


        elif weapon_type == 4:
            name = generate_name('dagger',tier)
            p_img = dagger_img
            inv_img = equipment_img
            slash = random.randint(2,6+(tier*2))
            smash = random.randint(0,0)
            stab = random.randint(3,8+(tier*2))
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,4)

            attk = random.randint(3,7+(tier*2))
            de = random.randint(0,0)
            hit = random.randint(5,11+(tier*2))
            dodge = random.randint(0,5)
            m_attk = random.randint(0,4+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(0,0)
            per = random.randint(1,5+(tier*2))
    
            weight = random.randint(5,7)

        elif weapon_type == 5:
            name = generate_name('club',tier)
            p_img = club_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(5,12)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(2,7)
            dark = random.randint(0,0)

            attk = random.randint(3,7+(tier*2))
            de = random.randint(0,0)
            hit = random.randint(2,5+(tier*2))
            dodge = random.randint(0,0)
            m_attk = random.randint(3,7+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(0,0)
            per = random.randint(0,0)

            weight = random.randint(5,7)

        elif weapon_type == 6:
            name = generate_name('staff',tier)
            p_img = staff_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(1,4+(tier*2))
            stab = random.randint(0,0)
            fire = random.randint(5,10+(tier*2))
            ice = random.randint(5,10+(tier*2))
            thunder = random.randint(5,10+(tier*2))
            dark = random.randint(5,10+(tier*2))

            attk = random.randint(1,4)
            de = random.randint(0,0)
            hit = random.randint(5,8+(tier*2))
            dodge = random.randint(0,1)
            m_attk = random.randint(4,8+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(1,6)
            per = random.randint(2,6+(tier*2))
  
            weight = random.randint(5,7)
            
        else:
            print "WTF"

    if item_type == 'arm':

        kind = 'armour'
        armour_type = random.randint(1,4)
        if armour_type == 1:
            name = generate_name('robe',tier)
            p_img = robe_img
            inv_img = equipment_img
            slash = random.randint(0,1+(tier*2))
            smash = random.randint(0,1+(tier*2))
            stab = random.randint(0,1+(tier*2))
            fire = random.randint(4,9+(tier*2))
            ice = random.randint(4,9+(tier*2))
            thunder = random.randint(4,9+(tier*2))
            dark = random.randint(4,9+(tier*2))

            attk = random.randint(0,0)
            de = random.randint(2,3+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(5,9+(tier*2))
            m_attk = random.randint(2,6+(tier*2))
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(4,9)
            per = random.randint(3,7)
  
            weight = random.randint(5,7)

        elif armour_type == 2:
            name = generate_name('leather',tier)
            p_img = leather_img
            inv_img = equipment_img
            slash = random.randint(2,6+(tier*2))
            smash = random.randint(2,6+(tier*2))
            stab = random.randint(2,6+(tier*2))
            fire = random.randint(3,7+(tier*2))
            ice = random.randint(3,7+(tier*2))
            thunder = random.randint(3,7+(tier*2))
            dark = random.randint(3,7+(tier*2))

            attk = random.randint(0,0)
            de = random.randint(5,9+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(3,6+(tier*2))
            m_attk = random.randint(0,0)
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(5,10)
 
            weight = random.randint(5,7)

        elif armour_type == 3:
            name = generate_name('mail',tier)
            p_img = mail_img
            inv_img = equipment_img
            slash = random.randint(4,10+(tier*2))
            smash = random.randint(4,10+(tier*2))
            stab = random.randint(4,10+(tier*2))
            fire = random.randint(3,8+(tier*2))
            ice = random.randint(3,8+(tier*2))
            thunder = random.randint(1,4+(tier*2))
            dark = random.randint(3,7+(tier*2))

            attk = random.randint(0,0)
            de = random.randint(7,11+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(-2,0)
            m_attk = random.randint(0,0)
            m_de = random.randint(4,8+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(0,0)
 
            weight = random.randint(5,7)

        elif armour_type == 4:
            name = generate_name('plate',tier)
            p_img = plate_img
            inv_img = equipment_img
            slash = random.randint(5,12+(tier*2))
            smash = random.randint(5,12+(tier*2))
            stab = random.randint(5,12+(tier*2))
            fire = random.randint(2,7+(tier*2))
            ice = random.randint(2,7+(tier*2))
            thunder = random.randint(2,7+(tier*2))
            dark = random.randint(1,4+(tier*2))

            attk = random.randint(0,0)
            de = random.randint(8,15+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(-8,-4)
            m_attk = random.randint(-6,-2)
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(6,11)
            per = random.randint(0,0)

            weight = random.randint(5,7)

        else:
            print 'WTF'

    if item_type == 'helm':
        kind = 'helm'
        helm_type = random.randint(1,4)

        if helm_type == 1:
            name = generate_name('metal helm',tier)
            p_img = plate_helm_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(5,11+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(-8,-4)
            m_attk = random.randint(-6,-2)
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(-7,-5)
            
            weight = random.randint(5,7)

        elif helm_type == 2:
            name = generate_name('cloth helm',tier)
            p_img = cloth_helm_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(1,4+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(0,0)
            m_attk = random.randint(4,7+(tier*2))
            m_de = random.randint(3,8+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(-3,0)
            
            weight = random.randint(5,7)
        

        elif helm_type == 3:
            name = generate_name('leather helm',tier)
            p_img = leather_helm_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(2,6+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(0,0)
            m_attk = random.randint(2,5+(tier*2))
            m_de = random.randint(3,8+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(-4,-1)
            
            weight = random.randint(5,7)
         

        elif helm_type == 4:
            name = generate_name('metal helm',tier)
            p_img = mail_helm_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(4,9+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(-3,-1)
            m_attk = random.randint(0,0)
            m_de = random.randint(1,3+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(-5,-2)
            
            weight = random.randint(5,7)
          

    if item_type == 'off hand':
        kind = 'off hand'
        off_hand_type = random.randint(1,4)

        if off_hand_type == 1:
            name = "shield"#generate_name('metal helm',tier)
            p_img = shield_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(5,11+(tier*2))
            hit = random.randint(0,0)
            dodge = random.randint(-8,-4)
            m_attk = random.randint(-6,-2)
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(2,6)
            per = random.randint(-7,-5)
            
            weight = random.randint(5,7)
          

        elif off_hand_type == 2:
            name = "relic"#generate_name('metal helm',tier)
            p_img = relic_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(0,0)
            hit = random.randint(0,0)
            dodge = random.randint(0,0)
            m_attk = random.randint(0,0)
            m_de = random.randint(5,11+(tier*2))
            cha = random.randint(7,15+(tier*2))
            per = random.randint(3,7)
      
            weight = random.randint(5,7)

        elif off_hand_type == 3:
            name = "Totem"#generate_name('metal helm',tier)
            p_img = totem_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(0,0)
            de = random.randint(0,0)
            hit = random.randint(0,0)
            dodge = random.randint(0,0)
            m_attk = random.randint(7,11+(tier*2))
            m_de = random.randint(0,0)
            cha = random.randint(0,0)
            per = random.randint(3,7)
            
            weight = random.randint(5,7)
      

        elif off_hand_type == 4:
            name = "Knife"#generate_name('metal helm',tier)
            p_img = knife_img
            inv_img = equipment_img
            slash = random.randint(0,0)
            smash = random.randint(0,0)
            stab = random.randint(0,0)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
            dark = random.randint(0,0)

            attk = random.randint(8,15+(tier*2))
            de = random.randint(0,0)
            hit = random.randint(5,11+(tier*2))
            dodge = random.randint(0,0)
            m_attk = random.randint(0,0)
            m_de = random.randint(0,0)
            cha = random.randint(0,0)
            per = random.randint(3,7)
        
            weight = random.randint(5,7)



    item = Equipment(name,p_img,inv_img,attk,de,m_attk,m_de,hit,dodge,cha,per,slash,smash,stab,fire,ice,thunder,dark,kind,weight)
    return item

def create_rat_room(room):
    
    for i in range(1,max_rats):
        random_roll = random.randint(1,100)
        if random_roll <= 100:
            name = 'rat'
            img = rat_img
            attack = 3+monster_str
            defence = 3+monster_str
            m_attk = 0
            m_def = 0
            hit = 4+monster_str
            dodge = 6+monster_str
            hp = 15+monster_str
            char = 0
            per = 0
            xp = 10
            weapon = None
            armour = None
            
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(0,1)
            contains = []
            item_stack = []
            for i in range(num_found):
                random_num = random.randint(1,100)
                if random_num<=10:
                    item = Item('Copper Key','key',1,key_img,1)
                elif random_num<=70:
                    item = Item('Linen Bandage','bandage',10,scroll_img,1)
                else:
                    break
                
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
            
        
        

def create_goblin_room(room):
    
    for i in range(max_goblins):
        random_roll = random.randint(1,100)
        if random_roll <= 100:
            name = 'goblin'
            img = goblin_img
            attack = 6
            defence = 5
            m_attk = 3
            m_def = 3
            hit = 6
            dodge = 4
            hp = 50
            char = 2
            per = 2
            
            xp = 30
            weapon = Equipment('dagger',dagger_img,equipment_img,3,0,0,0,6,0,0,0,4,0,6,0,0,0,0,'weapon',5)
            armour = Equipment('leather rags',leather_img,equipment_img,0,3,0,2,0,4,0,0,1,1,1,0,1,1,1,'armour',5)
            
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
        
            num_found = random.randint(1,5)
            contains = []
            item_stack = []
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
        else:
            print "other monster types required"
        
        
    
            
def create_spider_room(room):
    
    bosses = 0
    web_sacs = 0
    
    for i in range(max_spiders):
        random_roll = random.randint(1,100)
        if random_roll <= 70:
            name = 'Spinner'
            img = spider_img
            attack = 8+monster_str
            defence = 10+monster_str
            m_attk = 0
            m_def = 4+monster_str
            hit = 6+monster_str
            dodge = 3+monster_str
            hp = 30+monster_str
            char = 0
            per = 0
            weapon = Equipment('fang',knife_img,equipment_img,2,0,0,0,3,0,0,0,0,0,5,0,0,0,0,'dagger',5)
            armour = None
            xp = 20
            
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
                    
        elif random_roll <= 80:
            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    web = Trap(x,y,web_img,'web')
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
                img = spider_queen_img
                attack = 15+monster_str
                defence = 15+monster_str
                m_attk = 0
                m_def = 14+monster_str
                hit = 10+monster_str
                dodge = 3+monster_str
                hp = 100+monster_str
                char = 0
                per = 0
                weapon = Equipment('fang',dagger_img,equipment_img,15,0,0,0,9,0,0,0,0,0,9,0,0,0,0,'weapon',5)
                armour = None
                xp = 70
                
                x = random.randint(room.x1+1,room.x2-1)
                y = random.randint(room.y1+1,room.y2-1)
            
                num_found = random.randint(1,5)
                contains = []
                item_stack = []
                item_stack.append([weapon])
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
    
    max_npc = 3
    total_npc = 0

    for i in range(max_npc):
        random_char = random.randint(14,30)
        max_inv = 10
        amount_coin = random.randint(10,30)
        inventory = []
        for i in range(amount_coin):
            coin = Item('Coin','currency',1,coin_img,0.1)
            inventory.append([coin])
        random_price = random.randint(5,10)
        for i in range (max_inv):
            random_num = random.randint(1,10)
            if random_num <=2:
                item = generate_equipment('wep')
            elif random_num <=5:
                item = generate_equipment('arm')
            elif random_num <=7:
                item = generate_equipment('helm')
            else:
                item = generate_item()#Item('Health scroll','scroll',30+random_price)
            inventory.append([item])


        armour = Equipment('Common Cloths',leather_img,equipment_img,0,5,0,3,0,6,9,5,7,3,3,3,3,3,3,3,'armour',5)
        x = random.randint(room.x1+1,room.x2-2)
        y = random.randint(room.y1+1,room.y2-2)

        if not is_blocked(x,y):
            if not my_map[x][y].stairs_down:
                npc = Character(x,y,'Bob',player_naked_img,3,3,1,1,3,2,30,random_char,10,None,armour,inventory,0)
                npc.modify_stats()
                npc_group.add(npc)
                total_npc +=1

def create_treasure_room(room):
    
    
    amount_items = random.randint(1,max_items)
    
    for i in range(amount_items):

        num_found = random.randint(1,5)
        contains = []
        amount_coins = random.randint(0,5)
        for i in range (amount_coins):
            coin = Item('Coin','currency',1,coin_img,0.1)
            contains.append([coin])
        for i in range(num_found):

            random_roll = random.randint(1,100)
            if random_roll <= 55:
                item = generate_item()

            elif random_roll <= 60:
                item = generate_equipment('wep')
            elif random_roll <= 70:
                item = generate_equipment('helm')

            elif random_roll <= 90:
                item = generate_equipment('off hand')

            else:
                item = generate_equipment('arm')


        
            contains.append([item])
        #print "chest",contains
        #for i in contains:
        #    
        #    for j in i:
        #        print j.name
                


        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not my_map[x][y].stairs_down:
                treasure = Treasure(x,y,treasure_img,contains,'Chest')
                stack_inventory(treasure)
                #print "after sort", treasure.inventory
                #for i in treasure.inventory:
                #    print "#"
                #    for j in i:
                #        print j.name
                    
                treasure_group.add(treasure)

    
def place_objects(room):
    
    room = room
    if monster_str <= 3:
        room_type = random.randint(1,100)
        if room_type <= 50+(monster_str*2):
            create_rat_room(room)
            
        elif room_type <= 52+(monster_str*2+2):
            create_spider_room(room)
            
        elif room_type <= 53+(monster_str*2+2):
            create_goblin_room(room)
            
        #elif room_type <= 85:
        #    pass
            
        elif room_type <= 95:
            create_treasure_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str <= 6:
        room_type = random.randint(1,100)
        if room_type <= 40-monster_str:
            create_rat_room(room)
        elif room_type <= 60+(monster_str):
            create_spider_room(room)
        elif room_type <= 70+monster_str:
            create_goblin_room(room)
        elif room_type <= 90:
            print "empty room"
        elif room_type <= 95:
            create_treasure_room(room)
        else:
            create_npc_room(room)
            
    elif monster_str <=12:
        room_type = random.randint(1,100)
        if room_type <= 5:
            create_rat_room(room)
        elif room_type <= 40+(monster_str):
            create_spider_room(room)
        elif room_type <= 70+monster_str:
            create_goblin_room(room)
        elif room_type <= 90:
            print "empty room"
        elif room_type <= 95:
            create_treasure_room(room)
        else:
            create_npc_room(room)
            
    else:
        room_type = random.randint(1,100)
        if room_type <= 5:
            create_rat_room(room)
        elif room_type <= 40+(monster_str):
            create_spider_room(room)
        elif room_type <= 70+monster_str:
            create_goblin_room(room)
        elif room_type <= 90:
            print "empty room"
        elif room_type <= 95:
            create_treasure_room(room)
        else:
            create_npc_room(room)
#    if room_type <=70:#monster room
#        print "monster room"
#        amount_monsters = random.randint(0,max_monsters)
#        for i in range(amount_monsters):
#            random_roll = random.randint(1,100)
#
#        
#
#            elif random_roll > 50 and random_roll <= 85:
#                name = 'orc'
#                img = orc_img
#                attack = random.randint(8+monster_str,12+monster_str)
#                defence = random.randint(9+monster_str,13+monster_str)
#                m_attk = random.randint(2+monster_str,5+monster_str)
#                m_def = random.randint(7+monster_str,10+monster_str)
#                hit = random.randint(10+monster_str,13+monster_str)
#                dodge = random.randint(5+monster_str,7+monster_str)
#                hp = random.randint(50+(monster_str*10),65+(monster_str*10))
#                char = random.randint(1+monster_str,3+monster_str)
#                per = random.randint(5+monster_str,8+monster_str)
#                lab = random.randint(8+monster_str,11+monster_str)
#                weapon = generate_equipment('wep')
#                armour = generate_equipment('arm')
#
#            else:
#                name = 'troll'
#                img = troll_img
#                attack = random.randint(16+monster_str,21+monster_str)
#                defence = random.randint(10+monster_str,15+monster_str)
#                m_attk = random.randint(3+monster_str,6+monster_str)
#                m_def = random.randint(10+monster_str,13+monster_str)
#                hit = random.randint(5+monster_str,7+monster_str)
#                dodge = random.randint(0+monster_str,1+monster_str)
#                hp = random.randint(70+(monster_str*10),100+(monster_str*10))
#                char = random.randint(1+monster_str,3+monster_str)
#                per = random.randint(5+monster_str,8+monster_str)
#                lab = random.randint(8+monster_str,11+monster_str)
#                weapon = None#generate_equipment(0,0,'wep')
#                armour = None#generate_equipment(0,0,'arm')
#
#
#            x = random.randint(room.x1+1,room.x2-1)
#            y = random.randint(room.y1+1,room.y2-1)
#
#            num_found = random.randint(1,5)
#            contains = []
#            for i in range(num_found):
#                item = generate_item()
#                contains.append(item)
#
#            if not is_blocked(x,y):
#                if not my_map[x][y].stairs_down:
#                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,lab,weapon,armour,contains)
#                    monster_group.add(monster)
#                    all_group.add(monster)
#
#
#
###    elif room_type <= 75:#trap room
###        print "trap room"
#
#    
#    elif room_type <= 99:#treasure room
#        
#
#        print "treasure room"
#
#    else:#boss room
#        print "LIKE A BOSS"


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

    global max_monsters
    global monster_str

    if state == 'death':
        global player
        global player_sprite
        max_monsters = 3
        monster_str = 1
        #basic_armour = Equipment('Rusty Mail', mail_img,0,3,0,3,0,-1,0,0,0,1,1,1,1,1,1,'armour')
        #basic_weapon = Equipment('Rusty Axe', sword_img,3,0,1,0,1,0,0,0,0,1,1,1,0,0,0,'weapon')
        player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_img,8,8,8,8,8,8,100,8,8,basic_weapon,basic_armour,[[starter_cash,copper_key,poison_cure]])
        player_sprite = pygame.sprite.RenderPlain((player))
        all_group.add(player)
        player.modify_stats()
        text = "loading new game"
        updateGUI(text,(10,10,10))
        make_dungeon()


    elif state == 'retreat':
        max_monsters -= 1
        if max_monsters <=1:
            max_monsters = 1

        monster_str -= 1
        if monster_str <= 1:
            monster_str = 1
        make_dungeon()

    else:
        max_monsters += 1
        if max_monsters >=15:
            max_monsters = 15

        monster_str += 1
        make_dungeon()

##    make_map()

def make_dungeon():

    #print "level %s" %monster_str
    monster_group.empty()
    treasure_group.empty()
    npc_group.empty()
    trap_group.empty()
    spawner_group.empty()

    global my_map
    
    
    max_features = 50 * monster_str#random.randint(50,400)
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





##        chosen_feature = random.randint(1,2)
##        if halls < max_halls and chosen_feature == 2:# corridor
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

    for y in range(tiles_y):
            for x in range (tiles_x):
                wall = my_map[x][y].wall
                door = my_map[x][y].door
                stairs_down = my_map[x][y].stairs_down
                stairs_up = my_map[x][y].stairs_up

                if wall:
                    tmp_map.blit(wall_img,(x*tile_width,y*tile_height))
                    pygame.draw.rect(item_map,(50,50,50),(x*10,y*10,10,10))
##                    pygame.draw.rect(tmp_map,(50,50,50),(x*tile_width,y*tile_height,tile_width,tile_height))
                elif door:
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
                    if my_map[x][y+1].blocked:
                        tmp_map.blit(floor_b_img,(x*tile_width,y*tile_height))
                    if my_map[x][y-1].blocked:
                        tmp_map.blit(floor_t_img,(x*tile_width,y*tile_height))
                    if my_map[x-1][y].blocked:
                        tmp_map.blit(floor_l_img,(x*tile_width,y*tile_height))
                    if my_map[x+1][y].blocked:
                        tmp_map.blit(floor_r_img,(x*tile_width,y*tile_height))
                    random_number = random.randint(1,100)
                    if random_number >=98:
                        tmp_map.blit(floor_skull_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
                    elif random_number >=96:
                        tmp_map.blit(floor_skell_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
                    elif random_number >=94:
                        tmp_map.blit(floor_skull2_img,(x*tile_width-random.randint(1,30),y*tile_height-random.randint(1,30)))
##                    pygame.draw.rect(tmp_map,(200,200,200),(x*tile_width,y*tile_height,tile_width,tile_height))
    for r in room_list:
        place_objects(r)
    for m in monster_group:
        m.current_x = m.dest_x
        m.current_y = m.dest_y

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
            


def draw_inventory(name,cont1,cont2,inv1,inv2,selected_item):

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
    inventory_background.fill((100,100,100))
    inventory_1.fill((150,150,150))
    inventory_2.fill((150,150,150))
    trade_gui.fill((100,100,100))
    inventory_1.blit(inv1_name,(inv1_x-30,inv1_y))
    inventory_2.blit(inv2_name,(inv2_x-30,inv2_y))


    for i in selected_contents:
        
        item = i[0]
        value = item.value
        amount = len(i)
        item_img = item.inv_img
        item_name = " %s      X%s"%(item.name,amount)
        text = font1.render(item_name,1,(10,10,10))
        text_pos = text.get_rect()
        txt_x, txt_y = selected_inv.get_rect().topleft
        selected_inv.blit(text,(txt_x+50,txt_y+slot))
        selected_inv.blit(item.inv_img,(txt_x+30,txt_y+slot-5))
        slot+=20
        
    for i in other_contents:
        
        item = i[0]
        value = item.value
        amount = len(i)
        item_name = " %s      X%s"%(item.name,amount)
        text = font1.render(item_name,1,(10,10,10))
        text_pos = text.get_rect()
        txt_x, txt_y = other_inv.get_rect().topleft
        other_inv.blit(text,(txt_x+50,txt_y+slot_2))
        other_inv.blit(item.inv_img,(txt_x+30,txt_y+slot_2-5))
        slot_2+=20

    if selected_item is not None:
        info1 = "Name: %s           Weight: %s" %(item_info.name,item_info.weight)
    else:
        info1 = ""
    info1 = font1.render(info1,1,(10,10,10))
    info1_pos = info1.get_rect()
    info1_x,info1_y = trade_gui.get_rect().topleft
    trade_gui.blit(info1,(info1_x+10,info1_y+10))
    
    if selected_item is not None:
        if item_info.description is not None:
            info2 = "Description: %s"%item_info.description
        else:
            info2 = "Att: %s      M.Att: %s      Hit: %s"%(item_info.attk_pwr,item_info.magic_attk,item_info.hit)
    else:
        info2 = ""
    info2 = font1.render(info2,1,(10,10,10))
    info2_pos = info2.get_rect()
    info2_x,info2_y = trade_gui.get_rect().topleft
    trade_gui.blit(info2,(info2_x+10,info2_y+30))
    pygame.display.flip()
    
    if selected_item is not None:
        if item_info.description == None:
            info3 = "Def: %s      M.Def: %s      Dodge: %s"%(item_info.defence,item_info.magic_def,item_info.dodge)
        else:
            info3 = ""
    else:
        info3 = ""
    info3 = font1.render(info3,1,(10,10,10))
    info3_pos = info3.get_rect()
    info3_x,info3_y = trade_gui.get_rect().topleft
    trade_gui.blit(info3,(info3_x+10,info3_y+50))
    pygame.display.flip()
    
    if selected_item is not None:
        if item_info.description == None:
            info4 = "Per: %s      Char: %s      Value: %s"%(item_info.perception,item_info.charisma,item_info.value)
        else:
            info4 = ""
    else:
        info4 = ""
    info4 = font1.render(info4,1,(10,10,10))
    info4_pos = info4.get_rect()
    info4_x,info4_y = trade_gui.get_rect().topleft
    trade_gui.blit(info4,(info4_x+10,info4_y+70))
    pygame.display.flip()

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

    if target is not None:
        stack_inventory(target)
        stack_inventory(player)
    else:
        stack_inventory(target)
    
 
    if target == None:
        name = 'Trash'
        inv2 = []
        selected_contents = inv1
        other_contents = inv2
        trash = True
        arrow_x = 110
        selected_inv = inventory_1
        other_inv = inventory_2
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
        trash_object = Treasure(player.map_x/tile_width,player.map_y/tile_height,bag_img,dropped_items,'Bag')


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
        
    draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)

    is_open = 1
    while is_open:

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_i:
                    if category == 'trade':
                        if transaction_value !=0:
                            trade_chance = target.charisma - player.charisma + transaction_value
                            if trade_chance <= 0:
                                text = "A fair deal!"
                                updateGUI(text,(10,100,100))
                                is_open = 0
                                render_all()
                            else:
                                text = "No deal!"
                                updateGUI(text,(10,100,100))
                        else:
                            is_open = 0
                            render_all()

                    elif trash:
                        trash_length = len(trash_object.inventory)
                        if trash_length !=0:
                            #trash_object = Treasure(player.map_x/tile_width,player.map_y/tile_height,bag_img,dropped_items,'Bag')
                            treasure_group.add(trash_object)
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
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)


                elif event.key == K_UP:
                    selected_contents_length = len(selected_contents)
                    if arrow_y > arrow_top:
                        arrow_y -= 20
                        arrow_selection -=1
                        selection = arrow_selection -1
                        selected_item = selected_contents[selection]
                        item_info = selected_item[0]
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)


                elif event.key == K_RIGHT:
                    other_contents_length = len(other_contents)
                    if arrow_x < 260 and other_contents_length is not 0:
                        arrow_x += 250
                        arrow_y = 132
                        arrow_selection = 1
                        selection = arrow_selection - 1
                        selected_contents = inv2#target.inventory
                        other_contents = inv1
                        selected_inv = inventory_2
                        other_inv = inventory_1
                        selection = 0
                        selected_item = selected_contents[selection]
                        item_info = selected_item[0]
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)


                elif event.key == K_LEFT:
                    other_contents_length = len(other_contents)
                    if arrow_x > 110 and other_contents_length is not 0:
                        arrow_x -= 250
                        arrow_y = 132
                        arrow_selection = 1
                        selection = arrow_selection - 1
                        selected_contents = inv1
                        other_contents = inv2#target.inventory
                        selected_inv = inventory_1
                        other_inv = inventory_2
                        selection = 0
                        selected_item = selected_contents[selection]
                        item_info = selected_item[0]
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)


                elif event.key == K_t: #trash trade take transfer items
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
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)

                    else:
                        text = "There is no more room"
                        updateGUI(text,(10,10,10))


                elif event.key == K_f:#use item
                    if category != 'trade':
                        selected_contents_length = len(selected_contents)
                        if selected_contents_length is not 0:
                            selected_item = selected_contents[selection]
                            if selected_contents == player.inventory:
                                if selected_item[0].category is not 'currency' and selected_item[0].category is not 'key':
                                    item_used = selected_item.pop()
                                    use_equip(item_used)
                                    stack_inventory(player)
                                    stack_inventory(target)
                                    
                                else:
                                    text = "you cannot use that item"
                                    updateGUI(text,(10,10,10))
                            else:
                                text = "This item does not belong to you"
                                updateGUI(text,(10,10,10))
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
                            draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,item_info)

                #the below is used to assign hotkeys
                elif event.key == K_1:
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency':
                        item_k1 = item[0].name
                        text = "%s assigned to Key 1"%item_k1
                        updateGUI(text,(10,10,10))
                        
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_2:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k2 = item[0].name
                        text = "%s assigned to Key 2"%item_k2
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_3:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k3 = item[0].name
                        text = "%s assigned to Key 3"%item_k3
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_4:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k4 = item[0].name
                        text = "%s assigned to Key 4"%item_k4
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_5:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k5 = item[0].name
                        text = "%s assigned to Key 5"%item_k5
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_6:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k6 = item[0].name
                        text = "%s assigned to Key 6"%item_k6
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_7:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k7 = item[0].name
                        text = "%s assigned to Key 7"%item_k7
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_8:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k8 = item[0].name
                        text = "%s assigned to Key 8"%item_k8
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_9:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
                        item_k9 = item[0].name
                        text = "%s assigned to Key 9"%item_k9
                        updateGUI(text,(10,10,10))
                    else:
                        text = "you cannot use that item"
                        updateGUI(text,(10,10,10))
                elif event.key == K_0:#assign hotkey
                    item = selected_contents[selection]
                    if item[0].category != 'key' and item[0].category!='currency': 
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
        text2_3 = "att %s    m.att %s   hit %s" % (player.weapon.attk_pwr,player.weapon.magic_attk,player.weapon.hit)
        text2_4 = "slash %s smash %s stab %s" % (player.weapon.slash,player.weapon.smash,player.weapon.stab)
        text2_5 = "fire %s ice %s thunder %s" % (player.weapon.fire,player.weapon.ice,player.weapon.thunder)
        text2_2 = font1.render(text2_2,1,(10,10,10))
        text2_3 = font1.render(text2_3,1,(10,10,10))
        text2_4 = font1.render(text2_4,1,(10,10,10))
        text2_5 = font1.render(text2_5,1,(10,10,10))
        text2_2_pos = text2_2.get_rect()
        text2_3_pos = text2_3.get_rect()
        text2_4_pos = text2_4.get_rect()
        text2_5_pos = text2_5.get_rect()
        txt2_x += 10
        txt21_y = txt2_y + 20
        #text2_1_pos.topleft = (txt2_x,txt21_y) this used to be the spell line

        txt22_y = txt2_y + 100
        text2_2_pos.topleft = (txt2_x,txt22_y)

        txt23_y = txt2_y + 120
        text2_3_pos.topleft = (txt2_x,txt23_y)

        txt24_y = txt2_y + 140
        text2_4_pos.topleft = (txt2_x,txt24_y)

        txt25_y = txt2_y + 160
        text2_5_pos.topleft = (txt2_x,txt25_y)

        equipment.blit(text2_2,text2_2_pos)
        equipment.blit(text2_3,text2_3_pos)
        equipment.blit(text2_4,text2_4_pos)
        equipment.blit(text2_5,text2_5_pos)

    if player.armour is not None:
        text2_6 = "%s     "  % player.armour.name
        text2_7 = "def%s    m.def%s   dodge %s" % (player.armour.defence,player.armour.magic_def,player.armour.dodge)
        text2_8 = "slash %s smash %s stab %s" % (player.armour.slash,player.armour.smash,player.armour.stab)
        text2_9 = "fire %s ice %s thunder %s" % (player.armour.fire,player.armour.ice,player.armour.thunder)
        text2_6 = font1.render(text2_6,1,(10,10,10))
        text2_7 = font1.render(text2_7,1,(10,10,10))
        text2_8 = font1.render(text2_8,1,(10,10,10))
        text2_9 = font1.render(text2_9,1,(10,10,10))
        text2_6_pos = text2_6.get_rect()
        text2_7_pos = text2_7.get_rect()
        text2_8_pos = text2_8.get_rect()
        text2_9_pos = text2_9.get_rect()

        txt26_y = txt2_y + 190
        text2_6_pos.topleft = (txt2_x,txt26_y)

        txt27_y = txt2_y + 210
        text2_7_pos.topleft = (txt2_x,txt27_y)

        txt28_y = txt2_y + 230
        text2_8_pos.topleft = (txt2_x,txt28_y)

        txt29_y = txt2_y + 250
        text2_9_pos.topleft = (txt2_x,txt29_y)

        equipment.blit(text2_6,text2_6_pos)
        equipment.blit(text2_7,text2_7_pos)
        equipment.blit(text2_8,text2_8_pos)
        equipment.blit(text2_9,text2_9_pos)

    #combat info screen
    if text is not None and clr is not None:
        text = font2.render(text,1,(clr))
        text_pos = text.get_rect()
        text_list.insert(0,text)
        length = len(text_list)
        if length == 13:
            text_list.pop(12)
    
        coordx,coordy = combat.get_rect().bottomleft
        coordx += 45
        coord1y = coordy - 85
        coord2y = coordy - 110
        coord3y = coordy - 125
        coord4y = coordy - 140
        coord5y = coordy - 155
        coord6y = coordy - 170
        coord7y = coordy - 185
        coord8y = coordy - 200
        coord9y = coordy - 215
        coord10y = coordy - 230
        coord11y = coordy - 245
        coord12y = coordy - 260
    
        combat.blit(gui_back_img,(0,0))
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
                                        if length >=10:
                                            combat.blit(text_list[9],(coordx,coord10y))
                                            if length>=11:
                                                combat.blit(text_list[10],(coordx,coord11y))
                                                if length>=12:
                                                    combat.blit(text_list[11],(coordx,coord12y))
                                                

    gui.fill((10,10,10))

    render_gui()
    
def calc_fov(shooter_x,shooter_y,target_x,target_y):
    
    if shooter_y < target_y and shooter_x < target_x:
        for y in range(shooter_y,target_y):
            for x in range(shooter_x,target_x):
                if my_map[x][y].block_sight:
                    return False
    elif shooter_y < target_y and shooter_x > target_x:
        for y in range(shooter_y,target_y):
            for x in range(target_x,shooter_x):
                if my_map[x][y].block_sight:
                    return False
    elif shooter_y > target_y and shooter_x < target_x:
        for y in range(target_y,shooter_y):
            for x in range(shooter_x,target_x):
                if my_map[x][y].block_sight:
                    return False
    elif shooter_y > target_y and shooter_x > target_x:
        for y in range(target_y,shooter_y):
            for x in range(target_x,shooter_x):
                if my_map[x][y].block_sight:
                    return False
    else:
        return True

    
def calc_field_of_view():
    global my_map
    map_pos_x = player.rect.x - player.map_x
    map_pos_y = player.rect.y - player.map_y

    dark_list = []

    
    for y in range ((player.map_y-100)/tile_width,(player.map_y+200)/tile_width):
        for x in range ((player.map_x-100)/tile_width,(player.map_x+200)/tile_width):
            x_rect = map_pos_x + (x*tile_width)
            y_rect = map_pos_y + (y*tile_height)
            rect = (x_rect,y_rect,tile_width,tile_height)
            my_map[x][y].explored = True
            my_map[x][y].shadow = False
            #upper left
            if x_rect < player.rect.x and y_rect < player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect == player.rect.x and y_rect < player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect > player.rect.x and y_rect < player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect > player.rect.x and y_rect == player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect > player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect == player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect < player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
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
            if x_rect < player.rect.x and y_rect == player.rect.y and my_map[x][y].block_sight == False:
                my_map[x-1][y].shadow = False
                if my_map[x-1][y].block_sight == False:
                    my_map[x-2][y].shadow = False
                    
                my_map[x-1][y+1].shadow = False
                if my_map[x-1][y+1].block_sight == False:
                    my_map[x-2][y+1].shadow = False

                my_map[x-1][y-1].shadow = False
                if my_map[x-1][y-1].block_sight == False:
                    my_map[x-2][y-1].shadow = False


    for y in range ((player.map_y-300)/tile_width,(player.map_y+500)/tile_width):
        for x in range ((player.map_x-300)/tile_width,(player.map_x+500)/tile_width):
            x_rect = map_pos_x + (x*tile_width)
            y_rect = map_pos_y + (y*tile_height)
            rect = (x_rect,y_rect,tile_width,tile_height)

            if my_map[x][y].shadow:
                dark_list.append(rect)
            #if my_map[x][y].explored and my_map[x][y].shadow == True:
            #    explored_list.append((x_rect,y_rect))
                
    

    #for i in dark_list:
    #    screen.fill(col,i)


    for y in range ((player.map_y-300)/tile_width,(player.map_y+400)/tile_width):
        for x in range ((player.map_x-300)/tile_width,(player.map_x+400)/tile_width):
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
        m.rect.x = map_pos_x + m.map_x
        m.rect.y = map_pos_y + m.map_y
    npc_group.draw(screen)
    for n in npc_group:
        if n.armour is not None:
            screen.blit(n.armour.player_img,(n.rect.x,n.rect.y))

    monster_group.draw(screen)
    #for m in monster_group:
        #if m.armour is not None:
        #    screen.blit(m.armour.player_img,(m.rect.x,m.rect.y))
        #if m.weapon is not None:
        #    screen.blit(m.weapon.player_img,(m.rect.x,m.rect.y))

    
    player_sprite.draw(screen)
    if player.armour is not None:
        screen.blit(player.armour.player_img,(player.rect.x,player.rect.y))
    if player.weapon is not None:
        screen.blit(player.weapon.player_img,(player.rect.x,player.rect.y))
    if player.offhand is not None:
        screen.blit(player.offhand.player_img,(player.rect.x,player.rect.y))
    if player.helm is not None:
        screen.blit(player.helm.player_img,(player.rect.x,player.rect.y))

  
    
    dark_list = calc_field_of_view()
    col = (0,0,0)
    for i in dark_list:
        
        screen.fill(col,i)


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
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()
corpse_img = pygame.image.load('corpse.png').convert_alpha()
arrow_img = pygame.image.load('arrow.png').convert_alpha()
web_img = pygame.image.load('web.png').convert_alpha()

#inventory images
key_img = pygame.image.load('key.png').convert_alpha()
coin_img = pygame.image.load('coin.png').convert_alpha()
potion_img = pygame.image.load('anti_venom.png').convert_alpha()
scroll_img = pygame.image.load('scroll.png').convert_alpha()
equipment_img = pygame.image.load('equipment.png').convert_alpha()


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
ss = Sprite_sheet('magic_viking_spritesheet.png')
#player_img = ss.image_at((0,0,100,100),-1)
#player_idle = ss.images_at(((0,0,100,100),(0,0,100,100),(0,0,100,100)),-1)
#player_walk_down = ss.images_at(((0,0,100,100),(100,0,100,100),(200,0,100,100)),-1)
#player_walk_right = ss.images_at(((0,100,100,100),(100,100,100,100),(200,100,100,100)),-1)
#player_walk_left = ss.images_at(((0,200,100,100),(100,200,100,100),(200,200,100,100)),-1)
#player_walk_up = ss.images_at(((0,0,100,100),(100,0,100,100),(200,0,100,100)),-1)

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

starter_cash = Item('Coin','currency',1,coin_img,0.1)
fire_scr = Item('Fire Scroll','scroll',20,scroll_img,3)
copper_key = Item('Copper Key','key',10,key_img,2)
poison_cure = Item('Anti Venom','potion',20,potion_img,5)
bandage = Item('Linen Bandage','bandage',10,scroll_img,2)
basic_armour = Equipment('Rusty Mail', mail_img,equipment_img,0,5,0,3,0,-1,0,0,1,1,1,1,1,1,1,'armour',8)
basic_weapon = Equipment('Rusty Axe', sword_img,equipment_img,5,0,1,0,1,0,0,0,0,1,1,1,0,0,0,'weapon',5)
player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_img,8,8,8,8,8,8,100,8,8,basic_weapon,basic_armour,[[poison_cure,fire_scr,starter_cash,]])

player.modify_stats()


player_sprite = pygame.sprite.RenderPlain((player))
all_group = pygame.sprite.Group()
all_group.add(player)
npc_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
spawner_group = pygame.sprite.Group()

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 18)


make_dungeon()
dark_list = calc_field_of_view()


spawnlings = []


text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))

render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)
    all_group.update()
    handle_keys()
    
    
    render_all()
    pygame.display.flip()
    


#if __name__== '__main__': main()
