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
max_monsters = 3
monster_str = 1
max_items = 4

screen = pygame.display.set_mode((screen_width,screen_height))#,FULLSCREEN)
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))
item_map = pygame.Surface((700,700))


gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width - 20,2*tile_height - 20))
equipment = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width - 20,2*tile_height - 20))

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

class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = exit_img
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

class Item():
    def __init__(self,name,kind,val):
        self.name = name
        self.category = kind
        self.value = val

class Equipment(pygame.sprite.Sprite):

    def __init__(self,name,p_img,attk,de,m_attk,m_de,hit,dodge,cha,per,lab,slash,smash,stab,fire,ice,thunder,dark,kind,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.player_img = p_img
        self.blocks = blocks
        self.name = name
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
        self.labor = lab #used in crafting

        self.value = attk+de+m_attk+m_de+hit+dodge+cha+per+lab+slash+smash+stab+fire+ice+thunder+dark


class Character(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,de,m_attk,m_de,hit,dodge,hp,cha,per,lab,wep,arm,inventory,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.blocks = blocks
        self.name = name


        #equipment
        self.armour = arm
        self.weapon = wep
        self.helm = None
        self.boots = None
        self.offhand = None
##        if self.armour == None:
##            self.armour = Equipment(0,0,'rags',armour_img,player_naked_img,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
##        if self.weapon == None:
##            self.weapon = Equipment(0,0,'fists',weapon_img,fists_img,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

        self.stance = None

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
        self.action_points = 10

        self.disease = None #apply stat altering class

        self.inventory = inventory
        self.coin = 0

        self.frozen = False
        self.frozen_timer = 0

        #player spells
        self.heal_spell = 5
        self.fire_spell = 5
        self.ice_spell = 5

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


    def update(self):

        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)

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
            self.frozen_timer -= 1
            if self.frozen_timer == 0:
                self.frozen = False

    def monster_move(self,x,y):

        target = None
        dest_x = self.map_x + x
        dest_y = self.map_y + y

        if dest_x == player.map_x and dest_y == player.map_y:
                target = player

        if target is not None:
            random_num = random.randint(1,100)
            if random_num <= 5 and self.fire_spell !=0:
                self.cast_spell("fire_spell")
            elif random_num <= 20 and self.hp < self.max_hp/4 and self.heal_spell !=0:
                self.cast_spell("heal_spell")
            elif random_num <= 10 and self.ice_spell !=0:
                self.cast_spell("ice_spell")
            else:
                self.attack(target)

        else:
            self.move(x,y)


    def move_or_attack(self,x,y):
        if not self.frozen:

            target = None
            friendly_target = None
            dest_x = self.map_x + x
            dest_y = self.map_y + y

            for monster in monster_group:
                if dest_x == monster.map_x and dest_y == monster.map_y:
                    target = monster
            if target is not None:
                self.attack(target)

            for npc in npc_group:
                if dest_x == npc.map_x and dest_y == npc.map_y:
                    friendly_target = npc
            if friendly_target is not None:
                open_inventory(self.inventory,friendly_target,'trade')

            if my_map[dest_x/tile_width][dest_y/tile_height].door:
                if my_map[dest_x/tile_width][dest_y/tile_height].locked:
                    for i in self.inventory:
                        if i.category == 'key':
                            text = "You unlock the door"
                            my_map[dest_x/tile_width][dest_y/tile_height].locked = False
                            self.inventory.remove(i)
                            break
                        else:
                            text = "The door is locked"
                else:
                    my_map[dest_x/tile_width][dest_y/tile_height].blocked = False
                    my_map[dest_x/tile_width][dest_y/tile_height].door = False
                    my_map[dest_x/tile_width][dest_y/tile_height].block_sight = False
                    tmp_map.blit(floor_img,(dest_x,dest_y))
                    text = "you open the door"
                render_all()
                updateGUI(text,(100,100,10))

            else:
                if y == 100:
                    f1 = ss.image_at((0,0,100,100),-1)
                    f2 = ss.image_at((100,0,100,100),-1)
                    f3 = ss.image_at((200,0,100,100),-1)
                    player_walk_anim = [f2,f2,f2,f2,f2,f2,f3,f3,f3,f3,f3,f3,f2,f2,f2,f2,f2,f2,f1,f1]

                elif x == 100:
                    f1 = ss.image_at((0,100,100,100),-1)
                    f2 = ss.image_at((100,100,100,100),-1)
                    f3 = ss.image_at((200,100,100,100),-1)
                    player_walk_anim = [f2,f2,f2,f2,f2,f2,f1,f1,f1,f1,f1,f1,f3,f3,f3,f3,f3,f3,f1,f1]

                elif x == -100:
                    f1 = ss.image_at((0,200,100,100),-1)
                    f2 = ss.image_at((100,200,100,100),-1)
                    f3 = ss.image_at((200,200,100,100),-1)
                    player_walk_anim = [f2,f2,f2,f2,f2,f2,f1,f1,f1,f1,f1,f1,f3,f3,f3,f3,f3,f3,f1,f1]

                else:
                    f1 = ss.image_at((0,0,100,100),-1)
                    f2 = ss.image_at((100,0,100,100),-1)
                    f3 = ss.image_at((200,0,100,100),-1)
                    player_walk_anim = [f2,f2,f2,f2,f2,f2,f3,f3,f3,f3,f3,f3,f2,f2,f2,f2,f2,f2,f1,f1]




                self.move(x,y,player_walk_anim)

        else:
            self.frozen_timer -= 1
            if self.frozen_timer == 0:
                self.frozen = False



    def cast_spell(self,spell):

        aoe_targets = [(self.map_x + tile_width,self.map_y),(self.map_x - tile_width,self.map_y),\
            (self.map_x,self.map_y + tile_height),(self.map_x,self.map_y-tile_height)]
        spell_targets = []

        if spell == 'heal_spell' and self.heal_spell != 0:
            spell_power = random.randint(10,30)
            heal = spell_power + self.magic_attk
            self.hp += heal
            text = '%s gain %s from heal spell' % (self.name,heal)
            if self.hp >= self.max_hp:
                self.hp = self.max_hp
            self.heal_spell -= 1


            updateGUI(text,(100,100,10))

        elif spell == 'fire_spell' and self.fire_spell != 0:
            text = "%s uses a fire scroll" %self.name
            self.fire_spell -= 1
            updateGUI(text,(100,100,10))
            for target in aoe_targets:
                if target == (player.map_x,player.map_y):
                    spell_target = player
                    spell_targets.append(spell_target)

                for monster in monster_group:
                    if target == (monster.map_x,monster.map_y):
                        spell_target = monster
                        spell_targets.append(spell_target)

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


                tmp_map.blit(scorch_img,(target.map_x,target.map_y))
                updateGUI(text,(100,100,10))



        elif spell == 'ice_spell' and self.ice_spell != 0:
            text = "%s uses an ice scroll" %self.name
            self.ice_spell -= 1
            updateGUI(text,(100,100,10))
            for target in aoe_targets:
                if target == (player.map_x,player.map_y):
                    spell_target = player
                    spell_targets.append(spell_target)

                for monster in monster_group:
                    if target == (monster.map_x,monster.map_y):
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


    def move(self,x,y,anim=None):

        if not is_blocked(self.map_x/tile_width + x/tile_width ,self.map_y/tile_height + y/tile_height ):
            animation = anim
            if x !=0:
                for i in range(20):
                    clock.tick(60)
                    self.map_x += x/20
                    if animation is not None:#remember to remove this later
                        if len(animation) is not 0:
                            img = animation.pop(0)

                            self.image = img
                    render_all()

            if y !=0:
                for i in range(20):
                    clock.tick(60)
                    self.map_y += y/20
                    if animation is not None: #remember to remove this later
                        if len(animation) is not 0:
                            img = animation.pop(0)

                            self.image = img
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

            if target.hp <= 0:
                target.hp = 0
                text = "%s DIE!!!" % target.name
                self.xp += 10
                updateGUI(text,(100,10,10))
                if self.xp >= 100:
                    self.level += 1
                    self.xp = 0
                    self.stat_modifier += 1
                    text = "%s has leveled up!!" %self.name
                    col = (150,150,150)
                    updateGUI(text,(col))
                col = (10,10,10)
                target.death()

            else:

                text = "%s hit %s for %s damage" % (self.name,target.name,dmg)
                col = (10,10,10)
                updateGUI(text,col)
            if is_blocked((target.map_x-100)/tile_width,target.map_y/tile_width) and is_blocked((target.map_x+100)/tile_width,target.map_y/tile_width):
                blood_x = random.randint(target.map_x-10,target.map_x+10)
            elif is_blocked((target.map_x-100)/tile_width,target.map_y/tile_height) and not is_blocked((target.map_x+100)/tile_width,target.map_y/tile_height):
                blood_x = random.randint(target.map_x-10,target.map_x+50)
            elif is_blocked((target.map_x+100)/tile_width,target.map_y/tile_height) and not is_blocked((target.map_x-100)/tile_width,target.map_y/tile_height):
                blood_x = random.randint(target.map_x-50,target.map_x+10)
            else:
                blood_x = random.randint(target.map_x-50,target.map_x+50)

            if is_blocked(target.map_x/tile_width,(target.map_y-100)/tile_width) and is_blocked(target.map_x/tile_width,(target.map_y+100)/tile_width):
                blood_y = random.randint(target.map_y-10,target.map_y+10)
            elif is_blocked(target.map_x/tile_width,(target.map_y-100)/tile_height) and not is_blocked(target.map_x/tile_width,(target.map_y+100)/tile_height):
                blood_y = random.randint(target.map_y-10,target.map_y+50)
            elif is_blocked(target.map_x/tile_width,(target.map_y+100)/tile_height) and not is_blocked(target.map_x/tile_width,(target.map_y-100)/tile_height):
                blood_y = random.randint(target.map_y-50,target.map_y+10)
            else:
                blood_y = random.randint(target.map_y-50,target.map_y+50)
            tmp_map.blit(blood_img,(blood_x,blood_y))
            render_all()

        else:

            text = " %s dodges %s attack" % (target.name,self.name)
            col = (10,10,10)
            updateGUI(text,col)


    def death(self):


        tmp_map.blit(corpse_img, (self.map_x,self.map_y))
        self.kill()

        if self == player:
            self.armour = None
            self.weapon = None
            self.helm = None
            tmp_map.blit(corpse_img, (self.map_x,self.map_y))
            text = "You reached dungeon lvl %s" % monster_str
            updateGUI(text,(10,10,10))
            text = "and gained level %s" %self.level
            updateGUI(text,(10,10,10))
            render_all()
            load_new_level('death')

        loot_list = self.inventory
        if self.weapon is not None:
            loot_list.append(self.weapon)
        if self.armour is not None:
            loot_list.append(self.armour)
        loot = Treasure(self.map_x/tile_width,self.map_y/tile_height,corpse_img,loot_list,'Corpse')
        treasure_group.add(loot)

        render_all()



def move_key(x,y,key):
    timer = 0
    pressed = True

    while pressed:
        timer +=1
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == key:
                    pressed = False
                    break
        if timer >=50:
            player.move_or_attack(x,y)
            monster_group.update()
            timer = 0
            dest_x,dest_y = player.map_x + x,player.map_y+y

            if is_blocked(dest_x/tile_width,dest_y/tile_height):
                pressed = False
                break

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
                move_key(-tile_width,0,K_a)

            elif event.key == K_d:
                move_key(tile_width,0,K_d)

            elif event.key == K_w:
                move_key(0,-tile_height,K_w)

            elif event.key == K_s:
                move_key(0,tile_height,K_s)

            #display level map
            elif event.key == K_m:
                screen.blit(item_map, (0,0))





            #pickup/equip/examine
            elif event.key == K_i:
                open_inventory(player.inventory,None,'trash')
            elif event.key == K_e:
                examine_object()
            elif event.key == K_f:
                pickup_object()
                monster_group.update()
                pygame.event.clear()

            #spell keys
            elif event.key == K_1:
                player.cast_spell('heal_spell')
                monster_group.update()
                #pygame.event.clear()
            elif event.key == K_2:
                player.cast_spell('fire_spell')
                monster_group.update()
                #pygame.event.clear()
            elif event.key == K_3:
                player.cast_spell('ice_spell')
                monster_group.update()
                #pygame.event.clear()




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
            player.inventory.append(player.armour)
        player.armour = item
        text = "you equip %s"%item.name
        player.modify_stats()
    if item.category == 'weapon':
        if player.weapon is not None:
            player.inventory.append(player.weapon)
        player.weapon = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'helm':
        if player.helm is not None:
            player.inventory.append(player.helm)
        player.helm = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'off hand':
        if player.offhand is not None:
            player.inventory.append(player.offhand)
        player.offhand = item
        text = "you wield %s"%item.name
        player.modify_stats()
    if item.category == 'scroll':
        if item.name == 'Fire scroll':
            bonus = player.magic_attk + random.randint(1,10)
            if bonus <=20:
                player.fire_spell+=1
            elif bonus <= 25:
                player.fire_spell+=2
            elif bonus <= 30:
                player.fire_spell +=3
            elif bonus <= 35:
                player.fire_spell +=4
            else:
                player.fire_spell +=5
            text = "you gain knowledge from %s"%item.name

        elif item.name == 'Ice scroll':
            bonus = player.magic_attk + random.randint(1,10)
            if bonus <=20:
                player.ice_spell+=1
            elif bonus <= 25:
                player.ice_spell+=2
            elif bonus <= 30:
                player.ice_spell +=3
            elif bonus <= 35:
                player.ice_spell +=4
            else:
                player.ice_spell +=5
            text = "you gain knowledge from %s"%item.name

        elif item.name == 'Health scroll':
            bonus = player.magic_def + random.randint(1,10)
            if bonus <=20:
                player.heal_spell+=1
            elif bonus <= 25:
                player.heal_spell+=2
            elif bonus <= 30:
                player.heal_spell +=3
            elif bonus <= 35:
                player.heal_spell +=4
            else:
                player.heal_spell +=5
            text = "you gain knowledge from %s"%item.name
    if item.category == 'currency':
        text = "You count your money"
    if item.category == 'key':
        text = "you jingle the key"
    if item.category == 'bandage':
        player.wounds -= 5
        text = "you bandage your wounds"
        if player.wounds <=0:
            player.wounds = 0
        player.modify_stats()

    updateGUI(text,(10,10,100))

def examine_object():

    color = (10,10,150)

    for item in treasure_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            text = "A %s with loot" %item.name
            updateGUI(text,(color))

    if my_map[player.map_x/tile_width][player.map_y/tile_height].stairs_down:
        text = "you have discovered an exit point"
        updateGUI(text,(color))




def is_blocked(x,y): #used for walls monsters etc so they dont walk over eachother

    if my_map[x][y].blocked:
        return True
    if player.blocks and x == player.map_x/tile_width and y == player.map_y/tile_height :
        return True
    for monster in monster_group:
        if monster.blocks and monster.map_x/tile_width == x and monster.map_y/tile_height == y:
            return True
    for npc in npc_group:
        if npc.blocks and npc.map_x/tile_width == x and npc.map_y/tile_height == y:
            return True
    return False

def is_semi_blocked(x,y): #used for placing items so they dont pile up but can still be walked over
    if my_map[x][y].blocked:
        return True
    if player.blocks and x == player.map_x/tile_width and y == player.map_y/tile_height :
        return True
    for monster in monster_group:
        if monster.blocks and monster.map_x/tile_width == x and monster.map_y/tile_height == y:
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
        elif tier ==3:
            list_a = ['of Cunning','of Cruelty','of the Beast']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Cunning','of Cruelty','of the Beast']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Cunning','of Cruelty','of the Beast']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Cunning','of Cruelty','of the Beast']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1


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
        elif tier ==3:
            list_a = ['of Cunning','of Cruelty','of the Beast']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Shadow','of Cruelty','of Assasins']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1

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
        elif tier ==3:
            list_a = ['of Skulls','of Cruelty','of Sorcery']
            name_1 = random.choice(list_a)
            name_2 = random.choice(list_b)
            name = name_2+name_1
    return name

def generate_item():

    random_roll = random.randint(1,100)
    if random_roll <= 10:
        item = Item('Health scroll','scroll',30)

    elif random_roll <= 20:
        item = Item('Fire scroll','scroll',30)

    elif random_roll <= 30:
        item = Item('Ice scroll','scroll',30)

    elif random_roll <= 50:
        item = Item('Copper Key','key',1)
    else:
        item = Item('Linen Bandage','bandage',10)
    return item



def generate_equipment(cat):#generate an item at rect with category


    random_tier = random.randint(1,10)
    if random_tier <=6:
        tier = 1
    elif random_tier <=9:
        tier = 2
    else:
        tier = 3

    item_type = cat

    if item_type == 'wep':
        kind = 'weapon'
        #weapon_list = 1=sword 2=spear 3=axe 4=dagger 5=club 6=staff
        weapon_type = random.randint(1,6)
        if weapon_type == 1:

            name = generate_name('sword',tier)
            p_img = sword_img
            img = weapon_img
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
            lab = random.randint(0,0)


        elif weapon_type == 2:
            name = generate_name('spear',tier)
            p_img = spear_img
            img = weapon_img
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
            lab = random.randint(0,0)


        elif weapon_type == 3:
            name = generate_name('axe',tier)
            p_img = axe_img
            img = weapon_img
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
            lab = random.randint(0,4)


        elif weapon_type == 4:
            name = generate_name('dagger',tier)
            p_img = dagger_img
            img = weapon_img
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
            lab = random.randint(0,0)


        elif weapon_type == 5:
            name = generate_name('club',tier)
            p_img = club_img
            img = weapon_img
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
            lab = random.randint(0,2)


        elif weapon_type == 6:
            name = generate_name('staff',tier)
            p_img = staff_img
            img = weapon_img
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
            lab = random.randint(0,4)
        else:
            print "WTF"

    if item_type == 'arm':

        kind = 'armour'
        armour_type = random.randint(1,4)
        if armour_type == 1:
            name = generate_name('robe',tier)
            p_img = robe_img
            img = armour_img
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
            lab = random.randint(2,6)

        elif armour_type == 2:
            name = generate_name('leather',tier)
            p_img = leather_img
            img = armour_img
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
            lab = random.randint(1,4)

        elif armour_type == 3:
            name = generate_name('mail',tier)
            p_img = mail_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif armour_type == 4:
            name = generate_name('plate',tier)
            p_img = plate_img
            img = armour_img
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
            lab = random.randint(0,0)
        else:
            print 'WTF'

    if item_type == 'helm':
        kind = 'helm'
        helm_type = random.randint(1,4)

        if helm_type == 1:
            name = generate_name('metal helm',tier)
            p_img = plate_helm_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif helm_type == 2:
            name = generate_name('cloth helm',tier)
            p_img = cloth_helm_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif helm_type == 3:
            name = generate_name('leather helm',tier)
            p_img = leather_helm_img
            img = armour_img
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
            lab = random.randint(2,5)

        elif helm_type == 4:
            name = generate_name('metal helm',tier)
            p_img = mail_helm_img
            img = armour_img
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
            lab = random.randint(0,0)

    if item_type == 'off hand':
        kind = 'off hand'
        off_hand_type = random.randint(1,4)

        if off_hand_type == 1:
            name = "shield"#generate_name('metal helm',tier)
            p_img = shield_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif off_hand_type == 2:
            name = "relic"#generate_name('metal helm',tier)
            p_img = relic_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif off_hand_type == 3:
            name = "Totem"#generate_name('metal helm',tier)
            p_img = totem_img
            img = armour_img
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
            lab = random.randint(0,0)

        elif off_hand_type == 4:
            name = "Knife"#generate_name('metal helm',tier)
            p_img = knife_img
            img = armour_img
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
            lab = random.randint(0,0)



    item = Equipment(name,p_img,attk,de,m_attk,m_de,hit,dodge,cha,per,lab,slash,smash,stab,fire,ice,thunder,dark,kind)
    return item



def place_objects(room):

    room_type = random.randint(1,100)

    if room_type <=70:#monster room
        print "monster room"
        amount_monsters = random.randint(0,max_monsters)
        for i in range(amount_monsters):
            random_roll = random.randint(1,100)

            if random_roll <= 50:
                name = 'goblin'
                img = goblin_img
                attack = random.randint(12+monster_str,15+monster_str)
                defence = random.randint(2+monster_str,5+monster_str)
                m_attk = random.randint(2+monster_str,5+monster_str)
                m_def = random.randint(4+monster_str,6+monster_str)
                hit = random.randint(15+monster_str,18+monster_str)
                dodge = random.randint(8+monster_str,11+monster_str)
                hp = random.randint(30+(monster_str*10),40+(monster_str*10))
                char = random.randint(1+monster_str,3+monster_str)
                per = random.randint(5+monster_str,8+monster_str)
                lab = random.randint(8+monster_str,11+monster_str)
                weapon = generate_equipment('wep')
                armour = None

            elif random_roll > 50 and random_roll <= 85:
                name = 'orc'
                img = orc_img
                attack = random.randint(8+monster_str,12+monster_str)
                defence = random.randint(9+monster_str,13+monster_str)
                m_attk = random.randint(2+monster_str,5+monster_str)
                m_def = random.randint(7+monster_str,10+monster_str)
                hit = random.randint(10+monster_str,13+monster_str)
                dodge = random.randint(5+monster_str,7+monster_str)
                hp = random.randint(50+(monster_str*10),65+(monster_str*10))
                char = random.randint(1+monster_str,3+monster_str)
                per = random.randint(5+monster_str,8+monster_str)
                lab = random.randint(8+monster_str,11+monster_str)
                weapon = generate_equipment('wep')
                armour = generate_equipment('arm')

            else:
                name = 'troll'
                img = troll_img
                attack = random.randint(16+monster_str,21+monster_str)
                defence = random.randint(10+monster_str,15+monster_str)
                m_attk = random.randint(3+monster_str,6+monster_str)
                m_def = random.randint(10+monster_str,13+monster_str)
                hit = random.randint(5+monster_str,7+monster_str)
                dodge = random.randint(0+monster_str,1+monster_str)
                hp = random.randint(70+(monster_str*10),100+(monster_str*10))
                char = random.randint(1+monster_str,3+monster_str)
                per = random.randint(5+monster_str,8+monster_str)
                lab = random.randint(8+monster_str,11+monster_str)
                weapon = None#generate_equipment(0,0,'wep')
                armour = None#generate_equipment(0,0,'arm')


            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)

            num_found = random.randint(1,5)
            contains = []
            for i in range(num_found):
                item = generate_item()
                contains.append(item)

            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,lab,weapon,armour,contains)
                    monster_group.add(monster)



##    elif room_type <= 75:#trap room
##        print "trap room"

    elif room_type <= 75:#NPC room
        max_npc = 3
        total_npc = 0

        for i in range(max_npc):
            max_inv = 10
            inventory = []
            random_price = random.randint(5,10)
            for i in range (max_inv):
                random_num = random.randint(1,10)
                if random_num <=2:
                    item = generate_equipment('wep')
                elif random_num <=5:
                    item = generate_equipment('arm')
                elif random_num <=7:
                    item = generate_equipment('helm')
                elif random_num <=9:
                    item = Item('Bag of Coin','currency',20)
                else:
                    item = generate_item()#Item('Health scroll','scroll',30+random_price)
                inventory.append(item)


            armour = Equipment('Common Cloths',leather_img,0,5,0,3,0,6,9,5,7,3,3,3,3,3,3,3,'armour')
            x = random.randint(room.x1+1,room.x2-2)
            y = random.randint(room.y1+1,room.y2-2)

            if not is_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    npc = Character(x,y,'Bob',player_naked_img,3,3,1,1,3,2,30,17,10,15,None,armour,inventory)
                    npc.modify_stats()
                    npc_group.add(npc)
                    total_npc +=1

        print "npc room"

    elif room_type <= 99:#treasure room
        amount_items = random.randint(1,max_items)
        for i in range(amount_items):

            num_found = random.randint(1,5)
            contains = []
            for i in range(num_found):

                random_roll = random.randint(1,100)
                if random_roll <= 30:
                    item = generate_item()

                elif random_roll <= 40:
                    item = generate_equipment('wep')
                elif random_roll <= 50:
                    item = generate_equipment('helm')

                elif random_roll <= 90:
                    item = generate_equipment('off hand')

                else:
                    item = generate_equipment('arm')

                contains.append(item)


            x = random.randint(room.x1+1,room.x2-1)
            y = random.randint(room.y1+1,room.y2-1)
            if not is_semi_blocked(x,y):
                if not my_map[x][y].stairs_down:
                    treasure = Treasure(x,y,treasure_img,contains,'Chest')
                    treasure_group.add(treasure)

        print "treasure room"

    else:#boss room
        print "LIKE A BOSS"


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
        basic_armour = Equipment('Rusty Mail', mail_img,0,3,0,3,0,-1,0,0,0,1,1,1,1,1,1,1,'armour')
        basic_weapon = Equipment('Rusty Axe', sword_img,3,0,1,0,1,0,0,0,0,1,1,1,0,0,0,0,'weapon')
        player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_img,8,8,8,8,8,8,100,8,8,8,basic_weapon,basic_armour,[starter_cash,copper_key])
        player_sprite = pygame.sprite.RenderPlain((player))
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

    monster_group.empty()
    treasure_group.empty()
    npc_group.empty()

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



##        else:#if chosen_feature == 1:#room
##
##            x = door.x1
##            y = door.y1
##
##            if r_wall == 1:
##
##                w = random.randint(3,6)
##                h = random.randint(3,6)
##                x = random.randint(door.x1-(w/2),door.x1-1)
##                y = (y-h)
##
##            elif r_wall == 2:
##
##                w = random.randint(3,6)
##                h = random.randint(3,6)
##                x = (x+1)
##                y = random.randint(door.y1-(h/2),door.y1-1)
##
##            elif r_wall == 3:
##
##                w = random.randint(3,6)
##                h = random.randint(3,6)
##                x = random.randint(door.x1-(w/2),door.x1-1)
##                y = y+1
##
##            elif r_wall == 4:
##
##                w = random.randint(3,6)
##                h = random.randint(3,6)
##                x = (x-w)
##                y = random.randint(door.y1-(h/2),door.y1-1)
##
##            scan_area = Rect(x,y,w,h)
##
##            failed = False
##            for other_feature in features:
##                if scan_area.intersect(other_feature) or scan_area.x1 <= 3 or scan_area.x2 >= tiles_x - 3 or \
##                scan_area.y1 <= 3 or scan_area.y2 >= tiles_y - 3:
##                    failed = True
##                    break
##
##            if not failed:
##                new_room = Rect(x,y,w,h)
##                create_room(new_room)
##                place_objects(new_room)
##                c_x,c_y = new_room.center()
##                if random.randint(1,10)==10:
##                    if exits < max_exits:
##                        stair_down = Rect(c_x,c_y,1,1)
##                        stairs_down.append(stair_down)
##                        exits+=1
##                doors.append(door)
##                features.append(new_room)

##    for i in features:
##        for x in range(i.x1,i.x2):
##            for y in range(i.y1,i.y2):
##                my_map[x][y].blocked = False
##                my_map[x][y].wall = False
##                my_map[x][y].block_sight = False

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
##                    pygame.draw.rect(tmp_map,(200,200,200),(x*tile_width,y*tile_height,tile_width,tile_height))
    for r in room_list:
        place_objects(r)

def make_map():
    global my_map

    monster_group.empty()
    treasure_group.empty()
    npc_group.empty()

    wall_group = pygame.sprite.Group()
    floor_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()

    my_map = [[ Tile(True)
        for y in range(tiles_y) ]
              for x in range(tiles_x) ]

    rooms = []
    num_rooms = 0
    num_exits = random.randint(2,3)

    for r in range(max_rooms):
        w = random.randint(room_min_size, room_max_size)
        h = random.randint(room_min_size, room_max_size)
        x = random.randint(0, tiles_x - room_max_size - 4)
        y = random.randint(0, tiles_y - room_max_size - 4)

        new_room = Rect(x,y,w,h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:

            create_room(new_room)

            (new_x, new_y) = new_room.center()
##            if num_rooms != 0:
##                place_objects(new_room)


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
                if num_exits != 0:
                    create_exit(new_x,new_y)
                    num_exits -= 1

            rooms.append(new_room)
            num_rooms += 1

    for y in range(tiles_y):
        for x in range(tiles_x):
            wall = my_map[x][y].block_sight
            map_exit = my_map[x][y].exit
            if wall:
                wall_tile = Wall(x,y)
                wall_group.add(wall_tile)
            elif map_exit:
                exit_tile = Exit(x,y)
                exit_group.add(exit_tile)
            else:
                floor_tile = Floor(x,y)
                floor_group.add(floor_tile)

    for r in rooms:
        place_objects(r)

    draw_map(wall_group,floor_group,exit_group)


def draw_map(w,f,e):
    w.draw(tmp_map)
    f.draw(tmp_map)
    e.draw(tmp_map)


def draw_inventory(name,cont1,cont2,inv1,inv2,tranval):

    transaction_value = tranval
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
        item_name = "%s     %s"%(i.value,i.name)
        text = font1.render(item_name,1,(10,10,10))
        text_pos = text.get_rect()
        txt_x, txt_y = selected_inv.get_rect().topleft
        selected_inv.blit(text,(txt_x+30,txt_y+slot))
        slot+=20
    for i in other_contents:
        item_name = "%s     %s"%(i.value,i.name)
        text = font1.render(item_name,1,(10,10,10))
        text_pos = text.get_rect()
        txt_x, txt_y = other_inv.get_rect().topleft
        other_inv.blit(text,(txt_x+30,txt_y+slot_2))
        slot_2+=20

    info1 = "T = transfer    F = use      I = close     E = examine"
    info1 = font1.render(info1,1,(10,10,10))
    info1_pos = info1.get_rect()
    info1_x,info1_y = trade_gui.get_rect().topleft
    trade_gui.blit(info1,(info1_x+50,info1_y+10))
    info2 = "Profit = %s"%transaction_value
    info2 = font1.render(info2,1,(10,10,10))
    info2_pos = info2.get_rect()
    info2_x,info2_y = trade_gui.get_rect().topleft
    trade_gui.blit(info2,(info2_x+180,info2_y+50))

def open_inventory(inv1,target,category):


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

    dropped_items = []


    arrow_top = 132
    arrow_bottom = arrow_top + (20*20)
    arrow_y = 132
    arrow_selection = 1
    selection = arrow_selection -1
    if inv_length != 0:
        selected_item = selected_contents[selection]
    draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,transaction_value)

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
                            print "bob", target.charisma
                            print "player", player.charisma
                            print "value", transaction_value
                            print "result", trade_chance
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
                        trash_length = len(dropped_items)
                        if trash_length !=0:
                            trash_object = Treasure(player.map_x/tile_width,player.map_y/tile_height,bag_img,dropped_items,'Bag')
                            treasure_group.add(trash_object)
                        is_open = 0
                        render_all()
                    else:
                        is_open = 0
                        render_all()



                elif event.key == K_s:
                    selected_contents_length = len(selected_contents)
                    if arrow_y <= arrow_bottom and selected_contents_length>arrow_selection:
                        arrow_y += 20
                        arrow_selection+=1
                        selection = arrow_selection -1
                        selected_item = selected_contents[selection]


                elif event.key == K_w:
                    selected_contents_length = len(selected_contents)
                    if arrow_y > arrow_top:
                        arrow_y -= 20
                        arrow_selection -=1
                        selection = arrow_selection -1
                        selected_item = selected_contents[selection]


                elif event.key == K_d:
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


                elif event.key == K_a:
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


                elif event.key == K_t: #trash trade take transfer items
                    selected_contents_length = len(selected_contents)
                    other_contents_length = len(other_contents)
                    if selected_contents_length is not 0 and other_contents_length < 18:
                        selected_item = selected_contents[selection]
                        other_contents.append(selected_item)
                        selected_contents.remove(selected_item)
                        if selected_contents == inv1:
                            transaction_value -= selected_item.value
                        else:
                            transaction_value += selected_item.value
                        inv_length = len(selected_contents)
                        if arrow_selection > inv_length and arrow_selection is not 1:
                            arrow_selection -= 1
                            arrow_y -=20
                        selection = arrow_selection -1
                        if trash:
                            dropped_items = inv2
                        draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,transaction_value)

                    else:
                        text = "There is no more room"
                        updateGUI(text,(10,10,10))


                elif event.key == K_f:#use item
                    if category != 'trade':
                        selected_contents_length = len(selected_contents)
                        if selected_contents_length is not 0:
                            selected_item = selected_contents[selection]
                            if selected_contents == player.inventory:
                                use_equip(selected_item)
                                if selected_item.category is not 'currency' and selected_item.category is not 'key':
                                    selected_contents.remove(selected_item)
                            else:
                                text = "This item does not belong to you"
                                updateGUI(text,(10,10,10))
                            inv_length = len(selected_contents)
                            if arrow_selection > inv_length and arrow_selection is not 1:
                                arrow_selection -= 1
                                arrow_y -=20
                            selection = arrow_selection -1
                            draw_inventory(name,selected_contents,other_contents,selected_inv,other_inv,transaction_value)




        if is_open == 1:
            screen.blit(inventory_background,(100,100))
            inventory_background.blit(inventory_1,(5,5))
            inventory_background.blit(inventory_2,(255,5))
            inventory_background.blit(trade_gui,(20,390))
            screen.blit(arrow_img,(arrow_x,arrow_y))
            pygame.display.flip()


def updateGUI(text,clr):

    #player info screen
    text1_1 = "HP    %s / %s       LEVEL   %s" % (player.hp,player.max_hp,monster_str)
    text1_2 = "DEF       %s               M.DEF     %s" % (player.defence,player.magic_def)
    text1_3 = "ATT       %s             M.ATT     %s" % (player.attk_pwr,player.magic_attk)
    text1_4 = "AVO       %s             CHAR      %s " % (player.dodge,player.charisma)
    text1_5 = "HIT       %s             PERC      %s" % (player.hit,player.perception)
    text1_6 = "LABOR    %s" % player.labor

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

    txt_x += 20
    txt11_y = txt_y + 10
    txt11pos.topleft = (txt_x,txt11_y)

    txt12_y = txt_y + 30
    txt12pos.topleft = (txt_x,txt12_y)

    txt13_y = txt_y + 50
    txt13pos.topleft = (txt_x,txt13_y)

    txt14_y = txt_y + 70
    txt14pos.topleft = (txt_x,txt14_y)

    txt15_y = txt_y + 90
    txt15pos.topleft = (txt_x,txt15_y)

    txt16_y = txt_y + 110
    txt16pos.topleft = (txt_x,txt16_y)

    stats_gui.fill((150,150,150))
    stats_gui.blit(txt11,txt11pos)
    stats_gui.blit(txt12,txt12pos)
    stats_gui.blit(txt13,txt13pos)
    stats_gui.blit(txt14,txt14pos)
    stats_gui.blit(txt15,txt15pos)
    stats_gui.blit(txt16,txt16pos)

    #equipment screen
    text2_1 = "health  X %s  fire  X %s  ice X %s" %  (player.heal_spell,player.fire_spell,player.ice_spell)
    text2_1 = font1.render(text2_1,1,(10,10,10))

    text2_1_pos = text2_1.get_rect()
    equipment.fill((150,150,150))
    equipment.blit(text2_1,text2_1_pos)


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
        text2_1_pos.topleft = (txt2_x,txt21_y)

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


    gui.fill((100,100,100))

    render_gui()

def calc_field_of_view():
    global my_map
    map_pos_x = player.rect.x - player.map_x
    map_pos_y = player.rect.y - player.map_y
    col = (0,0,0)
    dark_list = []
    shadow_list = []
    explored_list = []

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
                my_map[x-1][y].shadow = False
                my_map[x][y-1].shadow = False
            #upper mid
            if x_rect == player.rect.x and y_rect < player.rect.y and my_map[x][y].block_sight == False:
                my_map[x][y-1].shadow = False
                my_map[x+1][y-1].shadow = False
                my_map[x-1][y-1].shadow = False
            #upper right
            if x_rect > player.rect.x and y_rect < player.rect.y and my_map[x][y].block_sight == False:
                my_map[x+1][y-1].shadow = False
                my_map[x+1][y].shadow = False
                my_map[x][y-1].shadow = False
            #mid right
            if x_rect > player.rect.x and y_rect == player.rect.y and my_map[x][y].block_sight == False:
                my_map[x+1][y].shadow = False
                my_map[x+1][y-1].shadow = False
                my_map[x+1][y+1].shadow = False
            #lower right
            if x_rect > player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
                my_map[x+1][y+1].shadow = False
                my_map[x+1][y].shadow = False
                my_map[x][y+1].shadow = False
            #lower mid
            if x_rect == player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
                my_map[x][y+1].shadow = False
                my_map[x-1][y+1].shadow = False
                my_map[x+1][y+1].shadow = False
            #lower left
            if x_rect < player.rect.x and y_rect > player.rect.y and my_map[x][y].block_sight == False:
                my_map[x-1][y+1].shadow = False
                my_map[x-1][y].shadow = False
                my_map[x][y+1].shadow = False
            #mid left
            if x_rect < player.rect.x and y_rect == player.rect.y and my_map[x][y].block_sight == False:
                my_map[x-1][y].shadow = False
                my_map[x-1][y+1].shadow = False
                my_map[x-1][y-1].shadow = False


    for y in range ((player.map_y-300)/tile_width,(player.map_y+500)/tile_width):
        for x in range ((player.map_x-300)/tile_width,(player.map_x+500)/tile_width):
            x_rect = map_pos_x + (x*tile_width)
            y_rect = map_pos_y + (y*tile_height)
            rect = (x_rect,y_rect,tile_width,tile_height)

            if my_map[x][y].shadow:
                dark_list.append(rect)
            if my_map[x][y].explored and my_map[x][y].shadow == True:
                explored_list.append((x_rect,y_rect))

    for i in dark_list:
        screen.fill(col,i)
##    for i in explored_list:
##        screen.blit(shadow_img,(i))

    for y in range ((player.map_y-200)/tile_width,(player.map_y+300)/tile_width):
        for x in range ((player.map_x-200)/tile_width,(player.map_x+300)/tile_width):
            my_map[x][y].explored = True
            my_map[x][y].shadow = True


def render_all():

    map_pos_x = player.rect.x - player.map_x
    map_pos_y = player.rect.y - player.map_y
    screen.blit(tmp_map, (map_pos_x ,map_pos_y))

    for t in treasure_group:
        t.rect.x = map_pos_x + t.map_x
        t.rect.y = map_pos_y + t.map_y

    treasure_group.draw(screen)

    for n in npc_group:
        n.rect.x = map_pos_x + n.map_x
        n.rect.y = map_pos_y + n.map_y
    for m in monster_group:
        m.rect.x = map_pos_x + m.map_x
        m.rect.y = map_pos_y + m.map_y
    npc_group.draw(screen)

    monster_group.draw(screen)
    for m in monster_group:
        if m.armour is not None:
            screen.blit(m.armour.player_img,(m.rect.x,m.rect.y))
        if m.weapon is not None:
            screen.blit(m.weapon.player_img,(m.rect.x,m.rect.y))

    player_sprite.draw(screen)


    calc_field_of_view()
##    screen.blit(vision_img, (0,0))

    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7 + 10, 0 + 10))
    screen.blit(combat, (tile_width * 7 + 10, tile_height*2 + 10))
    screen.blit(equipment, (tile_width*7+10, tile_height * 4 + 10))





    pygame.display.flip()

def render_gui():
    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7 + 10, 0 + 10))
    screen.blit(combat, (tile_width * 7 + 10, tile_height*2 + 10))
    screen.blit(equipment, (tile_width*7+10, tile_height * 4 + 10))

#initialisation

#map images
wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')
door_img = pygame.image.load('door2.png')
door_open_img = pygame.image.load('door_op.png')
exit_img = pygame.image.load('exit.jpg')
vision_img = pygame.image.load('fov.png').convert_alpha()
weapon_img = pygame.image.load('weapon.png').convert_alpha()
armour_img = pygame.image.load('armour.png').convert_alpha()
treasure_img = pygame.image.load('item.png').convert_alpha()
shadow_img = pygame.image.load('shadow.png').convert_alpha()
bag_img = pygame.image.load('bag.png').convert_alpha()

#effect images
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()
corpse_img = pygame.image.load('corpse.png').convert_alpha()
arrow_img = pygame.image.load('arrow.png').convert_alpha()

#enemy images
goblin_img = pygame.image.load('goblin.png').convert_alpha()
orc_img = pygame.image.load('orc2.png').convert_alpha()
troll_img = pygame.image.load('troll.png').convert_alpha()

#player images
ss = Sprite_sheet('magic_viking_spritesheet.png')
player_img = ss.image_at((0,0,100,100),-1)
##player_walk_anim = [ss.images_at((0,0,100,100)(100,0,100,100)(200,0,100,100)(0,0,100,100),-1)]
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

starter_cash = Item('Bag of Coin','currency',50)
copper_key = Item('Copper Key','key',1)
basic_armour = Equipment('Rusty Mail', mail_img,0,5,0,3,0,-1,0,0,0,1,1,1,1,1,1,1,'armour')
basic_weapon = Equipment('Rusty Axe', sword_img,5,0,1,0,1,0,0,0,0,1,1,1,0,0,0,0,'weapon')
player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook"\
            ,player_img,8,8,8,8,8,8,100,8,8,8,basic_weapon,basic_armour,[starter_cash,copper_key])

player_sprite = pygame.sprite.RenderPlain((player))
npc_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 21)



##make_map()
make_dungeon()


text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))

render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)

    handle_keys()
##    render_all()
    pygame.display.flip()



##    keypress = handle_keys()
##    if keypress:
##        break


#if __name__== '__main__': main()
