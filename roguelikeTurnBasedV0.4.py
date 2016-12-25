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
room_max_size = 8
room_min_size = 5
max_rooms = 50

#level difficulty variables can get modified by load_level()
max_monsters = 3
monster_str = 1
max_items = 2
max_armour = 1
max_weapons = 1

screen = pygame.display.set_mode((screen_width,screen_height),FULLSCREEN)
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))

gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width - 20,2*tile_height - 20))
inventory = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width - 20,2*tile_height - 20))


class Tile():
    def __init__(self, blocked, is_exit = None, block_sight = None):
        self.blocked = blocked
        self.exit = is_exit

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.shadow = True
        self.explored = False


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

    def __init__(self,x,y,contains,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = treasure_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.blocks = blocks

        self.contains = contains



class Equipment(pygame.sprite.Sprite):

    def __init__(self,x,y,name,img,p_img,attk,de,m_attk,m_de,hit,dodge,cha,per,lab,slash,smash,stab,fire,ice,thunder,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.player_img = p_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.blocks = blocks
        self.name = name

        #stats
        self.slash = slash
        self.smash = smash
        self.stab = stab
        self.fire = fire
        self.ice = ice
        self.thunder = thunder
        self.dark = 0

        self.attk_pwr = attk
        self.defence = de
        self.hit = hit
        self.dodge = dodge
        self.magic_attk = m_attk
        self.magic_def = m_de
        self.charisma = cha #used in bartering
        self.perception = per
        self.labor = lab #used in crafting



class Character(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,de,m_attk,m_de,hit,dodge,hp,cha,per,lab,wep,arm,blocks=True):
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
        if self.armour == None:
            self.armour = Equipment(0,0,'rags',armour_img,player_naked_img,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        if self.weapon == None:
            self.weapon = Equipment(0,0,'fists',weapon_img,None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

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

        self.c_attk_pwr = attk
        self.c_defence = de
        self.c_hit = hit
        self.c_dodge = dodge
        self.c_magic_attk = m_attk
        self.c_magic_def = m_de
        self.c_charisma = cha #used in bartering
        self.c_perception = per
        self.c_labor = lab #used in crafting

        self.stance = None

        self.max_hp = hp
        self.hp = self.max_hp
        self.wounds = 0 #used to prevent healing to max hp
        self.action_points = 10

        self.disease = None #apply stat altering class

        self.inventory = []
        self.coin = 0

        self.frozen = False
        self.frozen_timer = 0

        #player spells
        self.heal_spell = 5
        self.fire_spell = 5
        self.ice_spell = 5

    def modify_stats(self):

        self.image = self.armour.player_img

        self.attk_pwr = self.c_attk_pwr + self.weapon.attk_pwr + self.armour.attk_pwr
        self.defence = self.c_defence + self.weapon.defence + self.armour.defence
        self.hit = self.c_hit + self.weapon.hit + self.armour.hit
        self.dodge = self.c_dodge + self.weapon.dodge + self.armour.dodge
        self.magic_attk = self.c_magic_attk + self.weapon.magic_attk + self.armour.magic_attk
        self.magic_def = self.c_magic_def + self.weapon.magic_def + self.armour.magic_def
        self.charisma = self.c_charisma + self.weapon.charisma + self.armour.charisma
        self.perception = self.c_perception + self.weapon.perception + self.armour.perception
        self.labor = self.c_labor + self.weapon.labor + self.armour.labor

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
            dest_x = self.map_x + x
            dest_y = self.map_y + y

            for monster in monster_group:
                if dest_x == monster.map_x and dest_y == monster.map_y:
                    target = monster

            if target is not None:
                self.attack(target)

            else:
                self.move(x,y)

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
                fire = self.weapon.fire - target.armour.fire
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
                ice = self.weapon.ice - target.armour.ice
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

        if not is_blocked(self.map_x/tile_width + x/tile_width ,self.map_y/tile_height + y/tile_height ):
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


            slash = self.weapon.slash - target.armour.slash
            if slash <= 0:
                slash = 0
            smash = self.weapon.smash - target.armour.smash
            if smash <= 0:
                smash = 0
            stab = self.weapon.stab - target.armour.stab
            if stab <= 0:
                stab = 0


            target.injured = True

            if attack_roll == 20:
                dmg = attack + slash+smash+stab
                text = "%s perform a critical attack" %self.name
                col = (10,10,10)
                updateGUI(text,col)
            else:
                dmg = (attack - mitigate)+slash+smash+stab

            if dmg <= 0:
                dmg = 1
            target.hp -= dmg
            
            if target.hp < 0:
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
        render_all()
        if self == player:
            text = "You reached dungeon lvl %s" % monster_str
            updateGUI(text,(10,10,10))
            text = "and gained level %s" %self.level
            updateGUI(text,(10,10,10))
            text = "loading new game"
            self.level = 1
            updateGUI(text,(10,10,10))
            load_new_level('death')

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

            #pickup/equip/examine
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


    if is_exit(player.map_x/tile_width,player.map_y/tile_height):
        text = "you descend further into the darkness"
        updateGUI(text,(10,10,10))
        load_new_level('')
        make_map()
        render_all()

    for item in treasure_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            player.inventory.append(item)
            text = "you picked up some magic scrolls"
            col = (10,10,100)
            treasure_group.remove(item)
            item.kill()
            render_all()

            for i in item.contains:
                if i == 'health scroll':
                    player.heal_spell += 1
                elif i == 'fire scroll':
                    player.fire_spell += 1
                elif i == 'ice scroll':
                    player.ice_spell += 1

            updateGUI(text,col)

    for armour in armour_group:
        if player.map_x == armour.map_x and player.map_y == armour.map_y:
            text = "you have equiped %s" %armour.name
            col = (10,10,100)
            player.armour = armour
            player.modify_stats()

            armour_group.remove(armour)
            armour.kill()
            render_all()
            updateGUI(text,col)

    for weapon in weapon_group:
        if player.map_x == weapon.map_x and player.map_y == weapon.map_y:
            text = "you have equiped %s" % weapon.name
            col = (10,10,100)
            player.weapon = weapon
            player.modify_stats()

            weapon_group.remove(weapon)
            weapon.kill()
            render_all()
            updateGUI(text,col)

def examine_object():

    color = (10,10,150)
    for item in armour_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            text = "%s, def %s, m.def %s, ddg%s" % (item.name,item.defence,item.magic_def,item.dodge)
            updateGUI(text,(color))

    for item in treasure_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            text = "A chest of loot"
            updateGUI(text,(color))

    for item in weapon_group:
        if player.map_x == item.map_x and player.map_y == item.map_y:
            text = "%s, att %s, m.att %s, hit%s" % (item.name,item.attk_pwr,item.magic_attk,item.hit)
            updateGUI(text,(color))

    if is_exit(player.map_x/tile_width,player.map_y/tile_height):
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
        if treasure.blocks and treasure.rect.x/tile_width == x and treasure.rect.y/tile_height == y:
            return True
    for armour in armour_group:
        if armour.blocks and armour.rect.x/tile_width == x and armour.rect.y/tile_height == y:
            return True
    for weapon in weapon_group:
        if weapon.blocks and weapon.rect.x/tile_width == x and weapon.rect.y/tile_height == y:
            return True

    return False

def is_exit(x,y):
    if my_map[x][y].exit:
        return True
    else:
        return False

def place_objects(room):

    amount_monsters = random.randint(0,max_monsters)
    amount_items = random.randint(0,max_items)
    amount_weapons = random.randint(0,max_weapons)
    amount_armour = random.randint(0,max_armour)

    for i in range(amount_weapons):
        random_roll = random.randint(1,100)
        if random_roll <= 20:
            name = 'Short Sword'
            img = weapon_img
            p_img = None
            attk = random.randint(5,9)
            de = random.randint(0,0)
            m_attk = random.randint(0,2)
            m_de = random.randint(0,0)
            hit = random.randint(3,6)
            dodge = random.randint(-1,0)
            cha = random.randint(1,4)
            per = random.randint(0,1)
            lab = random.randint(-2,-1)
            slash = random.randint(3,6)
            smash = random.randint(0,0)
            stab = random.randint(4,7)
            fire = random.randint(0,1)
            ice = random.randint(0,0)
            thunder = random.randint(0,1)
        elif random_roll > 20 and random_roll<= 30:
            name = 'Bastard Sword'
            img = weapon_img
            p_img = None
            attk = random.randint(7,13)
            de = random.randint(-2,0)
            m_attk = random.randint(0,3)
            m_de = random.randint(-3,0)
            hit = random.randint(3,7)
            dodge = random.randint(-4,-1)
            cha = random.randint(2,6)
            per = random.randint(0,1)
            lab = random.randint(-4,-2)
            slash = random.randint(6,11)
            smash = random.randint(0,0)
            stab = random.randint(3,5)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,1)
        elif random_roll > 30 and random_roll<= 31:
            name = 'Great Sword'
            img = weapon_img
            p_img = None
            attk = random.randint(10,16)
            de = random.randint(-3,0)
            m_attk = random.randint(0,3)
            m_de = random.randint(-3,0)
            hit = random.randint(3,9)
            dodge = random.randint(-7,-3)
            cha = random.randint(7,10)
            per = random.randint(0,0)
            lab = random.randint(-5,-3)
            slash = random.randint(8,13)
            smash = random.randint(0,2)
            stab = random.randint(0,2)
            fire = random.randint(0,0)
            ice = random.randint(0,2)
            thunder = random.randint(0,0)
        elif random_roll > 31 and random_roll<= 51:
            name = 'Staff'
            img = weapon_img
            p_img = None
            attk = random.randint(1,5)
            de = random.randint(0,0)
            m_attk = random.randint(5,9)
            m_de = random.randint(2,4)
            hit = random.randint(1,5)
            dodge = random.randint(-3,0)
            cha = random.randint(4,7)
            per = random.randint(5,9)
            lab = random.randint(1,4)
            slash = random.randint(0,0)
            smash = random.randint(2,5)
            stab = random.randint(0,0)
            fire = random.randint(1,5)
            ice = random.randint(1,5)
            thunder = random.randint(1,5)
        elif random_roll > 51 and random_roll<= 61:
            name = 'Skull Staff'
            img = weapon_img
            p_img = None
            attk = random.randint(3,6)
            de = random.randint(0,0)
            m_attk = random.randint(7,11)
            m_de = random.randint(3,7)
            hit = random.randint(2,6)
            dodge = random.randint(-1,1)
            cha = random.randint(5,9)
            per = random.randint(7,11)
            lab = random.randint(2,7)
            slash = random.randint(0,0)
            smash = random.randint(2,6)
            stab = random.randint(0,0)
            fire = random.randint(3,8)
            ice = random.randint(3,8)
            thunder = random.randint(3,8)
        elif random_roll > 61 and random_roll<= 62:
            name = 'Staff of Souls'
            img = weapon_img
            p_img = None
            attk = random.randint(5,10)
            de = random.randint(-2,0)
            m_attk = random.randint(9,15)
            m_de = random.randint(5,9)
            hit = random.randint(3,8)
            dodge = random.randint(-1,1)
            cha = random.randint(7,10)
            per = random.randint(9,14)
            lab = random.randint(2,8)
            slash = random.randint(0,0)
            smash = random.randint(5,9)
            stab = random.randint(0,0)
            fire = random.randint(5,10)
            ice = random.randint(5,10)
            thunder = random.randint(5,10)
        elif random_roll > 62 and random_roll<= 82:
            name = 'Iron Dagger'
            img = weapon_img
            p_img = None
            attk = random.randint(4,7)
            de = random.randint(-3,0)
            m_attk = random.randint(2,5)
            m_de = random.randint(0,3)
            hit = random.randint(5,9)
            dodge = random.randint(5,9)
            cha = random.randint(-3,0)
            per = random.randint(4,8)
            lab = random.randint(1,3)
            slash = random.randint(1,3)
            smash = random.randint(0,0)
            stab = random.randint(4,7)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
        elif random_roll > 82 and random_roll<= 92:
            name = 'Steel Blades'
            img = weapon_img
            p_img = None
            attk = random.randint(6,10)
            de = random.randint(-3,0)
            m_attk = random.randint(3,6)
            m_de = random.randint(1,4)
            hit = random.randint(7,11)
            dodge = random.randint(6,10)
            cha = random.randint(-3,0)
            per = random.randint(7,10)
            lab = random.randint(1,3)
            slash = random.randint(3,6)
            smash = random.randint(0,0)
            stab = random.randint(6,9)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,1)
        else:
            name = 'Assasins Blade'
            img = weapon_img
            p_img = None
            attk = random.randint(8,13)
            de = random.randint(-3,0)
            m_attk = random.randint(4,8)
            m_de = random.randint(5,9)
            hit = random.randint(9,13)
            dodge = random.randint(9,13)
            cha = random.randint(-5,0)
            per = random.randint(10,15)
            lab = random.randint(1,6)
            slash = random.randint(4,8)
            smash = random.randint(0,0)
            stab = random.randint(8,12)
            fire = random.randint(0,1)
            ice = random.randint(0,1)
            thunder = random.randint(0,1)

        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not is_exit(x,y):
                weapon = Equipment(x,y,name,img,p_img,attk,de,m_attk,m_de,hit,dodge,cha,per,lab,slash,smash,stab,fire,ice,thunder)
                weapon_group.add(weapon)


    for i in range(amount_armour):
        random_roll = random.randint(1,100)
        if random_roll <= 20:
            name = 'Chain Mail'
            img = armour_img
            p_img = player_warrior_img
            attk = random.randint(0,0)
            de = random.randint(7,10)
            m_attk = random.randint(-5,-2)
            m_de = random.randint(1,5)
            hit = random.randint(-3,0)
            dodge = random.randint(-5,-1)
            cha = random.randint(0,2)
            per = random.randint(-1,0)
            lab = random.randint(-2,0)
            slash = random.randint(3,6)
            smash = random.randint(3,6)
            stab = random.randint(1,5)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
        elif random_roll > 20 and random_roll <= 30:
            name = 'Iron Cuirass'
            img = armour_img
            p_img = player_warrior_img
            attk = random.randint(0,0)
            de = random.randint(9,14)
            m_attk = random.randint(-5,-1)
            m_de = random.randint(2,7)
            hit = random.randint(-4,-1)
            dodge = random.randint(-6,-1)
            cha = random.randint(0,4)
            per = random.randint(-2,0)
            lab = random.randint(-4,0)
            slash = random.randint(4,8)
            smash = random.randint(3,6)
            stab = random.randint(4,7)
            fire = random.randint(0,0)
            ice = random.randint(0,0)
            thunder = random.randint(0,0)
        elif random_roll > 30 and random_roll <= 33:
            name = 'Steel Cuirass'
            img = armour_img
            p_img = player_warrior_img
            attk = random.randint(0,0)
            de = random.randint(11,18)
            m_attk = random.randint(-3,0)
            m_de = random.randint(5,9)
            hit = random.randint(-4,0)
            dodge = random.randint(-6,-2)
            cha = random.randint(1,5)
            per = random.randint(-2,0)
            lab = random.randint(-4,0)
            slash = random.randint(6,11)
            smash = random.randint(5,10)
            stab = random.randint(5,9)
            fire = random.randint(0,1)
            ice = random.randint(0,1)
            thunder = random.randint(0,1)
        elif random_roll > 33 and random_roll<= 53:
            name = 'Common Robe'
            img = armour_img
            p_img = player_mage_img
            attk = random.randint(0,0)
            de = random.randint(1,4)
            m_attk = random.randint(3,7)
            m_de = random.randint(3,7)
            hit = random.randint(1,3)
            dodge = random.randint(3,7)
            cha = random.randint(0,3)
            per = random.randint(4,8)
            lab = random.randint(0,3)
            slash = random.randint(1,3)
            smash = random.randint(1,3)
            stab = random.randint(1,3)
            fire = random.randint(3,7)
            ice = random.randint(3,7)
            thunder = random.randint(3,7)
        elif random_roll > 53 and random_roll <= 63:
            name = 'Silk Robe'
            img = armour_img
            p_img = player_mage_img
            attk = random.randint(0,0)
            de = random.randint(2,6)
            m_attk = random.randint(4,9)
            m_de = random.randint(4,9)
            hit = random.randint(1,3)
            dodge = random.randint(5,9)
            cha = random.randint(5,9)
            per = random.randint(7,10)
            lab = random.randint(1,5)
            slash = random.randint(2,5)
            smash = random.randint(2,5)
            stab = random.randint(2,5)
            fire = random.randint(4,9)
            ice = random.randint(4,9)
            thunder = random.randint(4,9)
        elif random_roll > 63 and random_roll <= 66:
            name = 'Warlocks Embrace'
            img = armour_img
            p_img = player_mage_img
            attk = random.randint(0,0)
            de = random.randint(3,9)
            m_attk = random.randint(8,14)
            m_de = random.randint(6,11)
            hit = random.randint(1,3)
            dodge = random.randint(6,12)
            cha = random.randint(9,15)
            per = random.randint(9,13)
            lab = random.randint(1,6)
            slash = random.randint(3,7)
            smash = random.randint(3,7)
            stab = random.randint(3,7)
            fire = random.randint(6,12)
            ice = random.randint(6,12)
            thunder = random.randint(6,12)
        elif random_roll > 66 and random_roll <= 86:
            name = 'Leather Armour'
            img = armour_img
            p_img = player_rogue_img
            attk = random.randint(0,0)
            de = random.randint(4,7)
            m_attk = random.randint(-2,0)
            m_de = random.randint(2,6)
            hit = random.randint(3,7)
            dodge = random.randint(3,7)
            cha = random.randint(-1,0)
            per = random.randint(5,8)
            lab = random.randint(4,9)
            slash = random.randint(3,6)
            smash = random.randint(3,6)
            stab = random.randint(3,6)
            fire = random.randint(1,3)
            ice = random.randint(1,3)
            thunder = random.randint(1,3)
        elif random_roll > 86 and random_roll <= 97:
            name = 'Assasins Garb'
            img = armour_img
            p_img = player_rogue_img
            attk = random.randint(0,0)
            de = random.randint(6,8)
            m_attk = random.randint(-1,0)
            m_de = random.randint(4,7)
            hit = random.randint(4,9)
            dodge = random.randint(6,11)
            cha = random.randint(-4,-1)
            per = random.randint(7,10)
            lab = random.randint(1,6)
            slash = random.randint(3,6)
            smash = random.randint(3,6)
            stab = random.randint(3,6)
            fire = random.randint(2,5)
            ice = random.randint(2,5)
            thunder = random.randint(2,5)
        else:
            name = 'Shadow cloak'
            img = armour_img
            p_img = player_rogue_img
            attk = random.randint(0,0)
            de = random.randint(7,10)
            m_attk = random.randint(0,2)
            m_de = random.randint(5,9)
            hit = random.randint(6,11)
            dodge = random.randint(10,15)
            cha = random.randint(-2,0)
            per = random.randint(10,15)
            lab = random.randint(1,6)
            slash = random.randint(4,7)
            smash = random.randint(4,7)
            stab = random.randint(4,7)
            fire = random.randint(3,7)
            ice = random.randint(3,7)
            thunder = random.randint(3,7)

        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not is_exit(x,y):
                armour = Equipment(x,y,name,img,p_img,attk,de,m_attk,m_de,hit,dodge,cha,per,lab,slash,smash,stab,fire,ice,thunder)
                armour_group.add(armour)

    for i in range(amount_items):
        num_found = random.randint(1,5)
        contains = []
        for i in range(num_found):
            random_roll = random.randint(1,100)
            if random_roll <= 40:
                item_type = 'health scroll'

            elif random_roll > 40 and random_roll <= 70:
                item_type = 'fire scroll'

            else:
                item_type = 'ice scroll'

            contains.append(item_type)


        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not is_exit(x,y):
                treasure = Treasure(x,y,contains)
                treasure_group.add(treasure)

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
            weapon = Equipment(0,0,'staber',weapon_img,goblin_img,8,0,1,1,5,0,0,0,0,6,0,8,0,0,0)
            armour = Equipment(0,0,'rags',weapon_img,goblin_img,0,3,0,1,0,6,0,0,0,2,2,1,0,2,2)

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
            weapon = Equipment(0,0,'short sword',armour_img,orc_img,9,0,0,1,5,0,1,0,1,6,0,5,0,0,0)
            armour = Equipment(0,0,'iron cuirass',armour_img,orc_img,0,6,0,5,0,-5,0,0,0,7,7,7,4,4,4)
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
            weapon = Equipment(0,0,'maul',weapon_img,troll_img,12,0,0,0,-2,-4,0,0,0,0,10,0,0,0,0)
            armour = Equipment(0,0,'bauldrick',weapon_img,troll_img,0,4,0,3,0,1,0,0,0,5,5,5,5,5,5)


        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)

        if not is_blocked(x,y):
            if not is_exit(x,y):
                monster = Character(x,y,name,img,attack,defence,m_attk,m_def,hit,dodge,hp,char,per,lab,weapon,armour)
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
        player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"you",player_naked_img,8,8,8,8,8,8,100,8,8,8,None,None)
        player_sprite = pygame.sprite.RenderPlain((player))



    else:
        max_monsters += 1
        if max_monsters >=15:
            max_monsters = 15

        monster_str += 1

    make_map()


def make_map():
    global my_map

    monster_group.empty()
    treasure_group.empty()
    weapon_group.empty()
    armour_group.empty()

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
            #if num_rooms != 0:
                #place_objects(new_room)


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

def updateGUI(text,clr):

    #player info screen
    text1_1 = "HP    %s / %s       LEVEL   %s" % (player.hp,player.max_hp,player.level)
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
    text2_2 = "%s     " % player.weapon.name
    text2_3 = "att %s    m.att %s   hit %s" % (player.weapon.attk_pwr,player.weapon.magic_attk,player.weapon.hit)
    text2_4 = "slash %s smash %s stab %s" % (player.weapon.slash,player.weapon.smash,player.weapon.stab)
    text2_5 = "fire %s ice %s thunder %s" % (player.weapon.fire,player.weapon.ice,player.weapon.thunder)
    text2_6 = "%s     "  % player.armour.name
    text2_7 = "def%s    m.def%s   dodge %s" % (player.armour.defence,player.armour.magic_def,player.armour.dodge)
    text2_8 = "slash %s smash %s stab %s" % (player.armour.slash,player.armour.smash,player.armour.stab)
    text2_9 = "fire %s ice %s thunder %s" % (player.armour.fire,player.armour.ice,player.armour.thunder)

    text2_1 = font1.render(text2_1,1,(10,10,10))
    text2_2 = font1.render(text2_2,1,(10,10,10))
    text2_3 = font1.render(text2_3,1,(10,10,10))
    text2_4 = font1.render(text2_4,1,(10,10,10))
    text2_5 = font1.render(text2_5,1,(10,10,10))
    text2_6 = font1.render(text2_6,1,(10,10,10))
    text2_7 = font1.render(text2_7,1,(10,10,10))
    text2_8 = font1.render(text2_8,1,(10,10,10))
    text2_9 = font1.render(text2_9,1,(10,10,10))

    text2_1_pos = text2_1.get_rect()
    text2_2_pos = text2_2.get_rect()
    text2_3_pos = text2_3.get_rect()
    text2_4_pos = text2_4.get_rect()
    text2_5_pos = text2_5.get_rect()
    text2_6_pos = text2_6.get_rect()
    text2_7_pos = text2_7.get_rect()
    text2_8_pos = text2_8.get_rect()
    text2_9_pos = text2_9.get_rect()

    txt2_x,txt2_y = inventory.get_rect().topleft

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

    txt26_y = txt2_y + 190
    text2_6_pos.topleft = (txt2_x,txt26_y)

    txt27_y = txt2_y + 210
    text2_7_pos.topleft = (txt2_x,txt27_y)

    txt28_y = txt2_y + 230
    text2_8_pos.topleft = (txt2_x,txt28_y)

    txt29_y = txt2_y + 250
    text2_9_pos.topleft = (txt2_x,txt29_y)

    inventory.fill((150,150,150))
    inventory.blit(text2_1,text2_1_pos)
    inventory.blit(text2_2,text2_2_pos)
    inventory.blit(text2_3,text2_3_pos)
    inventory.blit(text2_4,text2_4_pos)
    inventory.blit(text2_5,text2_5_pos)
    inventory.blit(text2_6,text2_6_pos)
    inventory.blit(text2_7,text2_7_pos)
    inventory.blit(text2_8,text2_8_pos)
    inventory.blit(text2_9,text2_9_pos)

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

    render_all()

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
    for w in weapon_group:
        w.rect.x = map_pos_x + w.map_x
        w.rect.y = map_pos_y + w.map_y
    for a in armour_group:
        a.rect.x = map_pos_x + a.map_x
        a.rect.y = map_pos_y + a.map_y

    treasure_group.draw(screen)
    weapon_group.draw(screen)
    armour_group.draw(screen)

    for m in monster_group:
        m.rect.x = map_pos_x + m.map_x
        m.rect.y = map_pos_y + m.map_y
        


    monster_group.draw(screen)
    player_sprite.draw(screen)

    calc_field_of_view()
##    screen.blit(vision_img, (0,0))

    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7 + 10, 0 + 10))
    screen.blit(combat, (tile_width * 7 + 10, tile_height*2 + 10))
    screen.blit(inventory, (tile_width*7+10, tile_height * 4 + 10))


    pygame.display.flip()


#initialisation

#map images
wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')
exit_img = pygame.image.load('exit.jpg')
vision_img = pygame.image.load('fov.png').convert_alpha()
weapon_img = pygame.image.load('weapon.png').convert_alpha()
armour_img = pygame.image.load('armour.png').convert_alpha()
treasure_img = pygame.image.load('item.png').convert_alpha()
shadow_img = pygame.image.load('shadow.png').convert_alpha()

#effect images
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()
corpse_img = pygame.image.load('corpse.png').convert_alpha()

#enemy images
goblin_img = pygame.image.load('goblin.png').convert_alpha()
orc_img = pygame.image.load('orc.png').convert_alpha()
troll_img = pygame.image.load('troll.png').convert_alpha()

#player images
player_naked_img = pygame.image.load('playernaked.png').convert_alpha()
player_warrior_img = pygame.image.load('playerwarrior.png').convert_alpha()
player_mage_img = pygame.image.load('playerwizard.png').convert_alpha()
player_rogue_img = pygame.image.load('playerrogue.png').convert_alpha()


player = Character((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,"Rahnook",player_naked_img,8,8,8,8,8,8,100,8,8,8,None,None)

player_sprite = pygame.sprite.RenderPlain((player))
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
armour_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()

font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 21)

make_map()
text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))



render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)

    pygame.display.flip()

    keypress = handle_keys()
    if keypress:
        break


#if __name__== '__main__': main()
