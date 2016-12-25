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
max_armor = 1
max_weapons = 1

screen = pygame.display.set_mode((screen_width,screen_height))
level_map = pygame.Surface((map_width,map_height))
tmp_map = pygame.Surface((map_width,map_height))

gui = pygame.Surface((3*tile_width,7*tile_height))
stats_gui = pygame.Surface((3*tile_width - 20,2*tile_height - 20))
inventory = pygame.Surface((3*tile_width - 20,3*tile_height - 20))
combat = pygame.Surface((3*tile_width - 20,2*tile_height - 20))


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
    def __init__(self, blocked, is_exit = None, block_sight = None):
        self.blocked = blocked
        self.exit = is_exit

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
        self.image, self.rect = load_image('item.png',-1)
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height
        self.blocks = blocks

        self.contains = contains

class Weapon(pygame.sprite.Sprite):

    def __init__(self,x,y,name,img,att,m_att,hit,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img,-1)
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height
        self.blocks = blocks

        #stats
        self.name = name
        self.attack = att
        self.magic_att = m_att
        self.hit = hit

class Armor(pygame.sprite.Sprite):

    def __init__(self,x,y,name,group,img,defence,m_def,ste,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img ,-1)
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height
        self.blocks = blocks


        #stats
        self.armor_group = group
        self.name = name
        self.defence = defence
        self.magic_def = m_def
        self.stealth = ste



class Player(pygame.sprite.Sprite):


    def __init__(self,x,y,img,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        #self.image, self.rect = load_image(img,-1)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.map_x = x
        self.map_y = y
        self.init_x = x
        self.init_y = y
        self.blocks = blocks

        self.armor = basic_armor
        self.weapon = basic_weapon

        self.xp = 0
        self.level = 1
        self.stat_modifier = 0

        ##player base stats
        self.attk_pwr = 10 + self.stat_modifier
        self.defence = 8 + self.stat_modifier
        self.hit = 10 + self.stat_modifier
        self.dodge = 8 + self.stat_modifier
        self.max_hp = 100 + (self.stat_modifier*10)
        self.hp = self.max_hp
        self.magic_attk = 10 + self.stat_modifier
        self.magic_def = 10 + self.stat_modifier
        self.magic_hit = 10 + self.stat_modifier
        self.magic_dodge = 10 + self.stat_modifier
        self.stealth = 1 + self.stat_modifier

        self.m_attk_pwr = self.attk_pwr
        self.m_magic_att = self.magic_attk
        self.m_hit = self.hit
        self.m_defence = self.defence
        self.m_magic_def = self.magic_def
        self.m_stealth = self.stealth

        ##player spells
        self.heal_spell = 5
        self.fire_spell = 5
        self.ice_spell = 5

    def move_or_attack(self,x,y):

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


    def cast_spell(self,spell):

        aoe_targets = [(self.map_x + tile_width,self.map_y),(self.map_x - tile_width,self.map_y),\
            (self.map_x,self.map_y + tile_height),(self.map_x,self.map_y-tile_height)]

        if spell == 'heal_spell' and self.heal_spell != 0:
            spell_power = random.randint(10,30)
            heal = spell_power + self.m_magic_att
            self.hp += heal
            text = 'you gain %s from heal spell' % heal
            if self.hp >= self.max_hp:
                self.hp = self.max_hp
            self.heal_spell -= 1
            updateGUI(text,(100,100,10))

        elif spell == 'fire_spell' and self.fire_spell != 0:
            text = "You use a fire scroll"
            self.fire_spell -= 1
            updateGUI(text,(100,100,10))
            for target in aoe_targets:
                for monster in monster_group:


                    if target == (monster.map_x,monster.map_y):
                        spell_power = random.randint(10,30)
                        dmg = spell_power + self.m_magic_att - monster.magic_def
                        if dmg <= 0:
                            dmg = 1
                        monster.hp -= dmg
                        text = "you hit %s with %s fire damage" % (monster.name,dmg)
                        if monster.hp < 0:
                            monster.hp = 0
                            text = "The %s burns to death" % monster.name
                            col = (100,100,10)
                            monster.death()
                            updateGUI(text,col)

                        tmp_map.blit(scorch_img,(monster.map_x,monster.map_y))
                        updateGUI(text,(100,100,10))



        elif spell == 'ice_spell' and self.ice_spell != 0:
            text = "you use an ice scroll"
            self.ice_spell -= 1
            updateGUI(text,(100,100,10))
            for target in aoe_targets:
                for monster in monster_group:
                    if target == (monster.map_x,monster.map_y):
                        spell_power = random.randint(1,5)
                        effect = spell_power + self.m_magic_att - monster.magic_def
                        if effect <= 0:
                            text = "%s resisted the spell" % monster.name
                        else:
                            monster.frozen = True
                            monster.frozen_timer = effect
                            text = "you freeze the %s in place" % monster.name
                        updateGUI(text,(100,100,10))




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
        hit_chance = hit_roll + self.m_hit
        miss_roll = random.randint(1,20)
        miss_chance = miss_roll + target.dodge

        if hit_chance >= miss_chance:
            attack_roll = random.randint(1,20)
            attack = attack_roll + self.m_attk_pwr
            mit_roll = random.randint(1,20)
            mitigate = mit_roll + target.defence

            target.injured = True

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
                self.xp += 10
                if self.xp >= 100:
                    self.level += 1
                    self.xp = 0
                    self.stat_modifier += 1
                    text = "you have leveled up!!"
                    col = (150,150,150)
                    updateGUI(text,(col))
                col = (10,100,10)
                target.death()

            else:

                text = "you hit the %s for %s damage" % (target.name,dmg)
                col = (10,100,10)
            tmp_map.blit(blood_img,(target.map_x,target.map_y))
            render_all()

        else:

            text = "the %s dodges your attack" % target.name
            col = (100,10,10)

        updateGUI(text,col)


    def death(self):

        tmp_map.blit(blood_img, (self.map_x,self.map_y))
        self.kill()
        render_all()
        load_new_level('death')



class Monster(pygame.sprite.Sprite):


    def __init__(self,x,y,name,img,attk,defence,hit,dodge,hp,m_def,blocks=True):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img, -1)
        self.name = name
        self.blocks = blocks
        self.map_x = x * tile_width
        self.map_y = y * tile_height
        self.rect.x = 0
        self.rect.x = 0

        self.attk_pwr = attk
        self.defence = defence
        self.hit = hit
        self.dodge = dodge
        self.hp = hp
        self.magic_def = m_def

        self.injured = False
        self.frozen = False
        self.frozen_timer = 0

    def move(self,x,y):


        if not is_blocked(self.map_x/tile_width + x/tile_width ,self.map_y/tile_height + y/tile_height ) and\
         not is_exit(self.map_x/tile_width + x/tile_width ,self.map_y/tile_height + y/tile_height ):


            for i in range(10):
                self.rect.x += x/10
                self.map_x += x/10
                render_all()

            for i in range(10):
                self.rect.y += y/10
                self.map_y += y/10
                render_all()


    def update(self):

        dist_to_player_x = abs(self.map_x - player.map_x)
        dist_to_player_y = abs(self.map_y - player.map_y)

        if not self.frozen:
            if (dist_to_player_x == tile_width and self.map_y == player.map_y)or\
               (dist_to_player_y == tile_height and self.map_x == player.map_x):
                self.attack()


            if dist_to_player_x <= (((play_area_x-player.m_stealth)*tile_width)/2) and \
               dist_to_player_y <= (((play_area_y-player.m_stealth)*tile_height)/2):

                new_dist_x = abs(self.map_x + tile_width - player.map_x)
                new_dist_y = abs(self.map_y + tile_height - player.map_y)

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
            mitigate = mit_roll + player.m_defence

            dmg = attack - mitigate
            if dmg <= 0:
                dmg = 1
            player.hp -= dmg
            if player.hp < 0:
                player.hp = 0
                text = "YOU HAVE DIED!"
                col = (150,10,10)
                updateGUI(text,(col))
                player.death()



            else:

                text = "The %s hits you for %s damage" % (self.name,dmg)
                col = (100,10,10)

        else:

            text = "You dodge the %s's attack" %self.name
            col = (10,100,10)

        updateGUI(text,col)

    def death(self):
        tmp_map.blit(floor_img, (self.rect.x,self.rect.y))
        tmp_map.blit(blood_img, (self.rect.x,self.rect.y))
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
        if player.map_x == item.rect.x and player.map_y == item.rect.y:
            player_inventory.append(item)
            text = "you picked up some magic scrolls"
            col = (10,10,100)
            tmp_map.blit (floor_img,(item.rect.x,item.rect.y))
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

    for armor in armor_group:
        if player.map_x == armor.rect.x and player.map_y == armor.rect.y:
            text = "you have equiped %s" %armor.name
            col = (10,10,100)
            player.armor = armor

            #returns to base stats
            player.m_defence = player.defence
            player.m_magic_def = player.magic_def
            player.m_stealth = player.stealth

            if armor.armor_group == 'wizard':
                player.image = player_mage_img
            elif armor.armor_group == 'warrior':
                player.image = player_warrior_img
            elif armor.armor_group == 'rogue':
                player.image = player_rogue_img
            #adds new equipment stats
            player.m_defence += armor.defence
            player.m_magic_def += armor.magic_def
            player.m_stealth += armor.stealth
            tmp_map.blit (floor_img,(armor.rect.x,armor.rect.y))
            armor_group.remove(armor)
            armor.kill()
            render_all()
            updateGUI(text,col)

    for weapon in weapon_group:
        if player.map_x == weapon.rect.x and player.map_y == weapon.rect.y:
            text = "you have equiped %s" % weapon.name
            col = (10,10,100)
            player.weapon = weapon

            #returns to base stats
            player.m_attk_pwr = player.attk_pwr
            player.m_magic_att = player.magic_attk
            player.m_hit = player.hit

            #adds new equipment stats
            player.m_attk_pwr += weapon.attack
            player.m_magic_att += weapon.magic_att
            player.m_hit += weapon.hit
            tmp_map.blit (floor_img,(weapon.rect.x,weapon.rect.y))
            weapon_group.remove(weapon)
            weapon.kill()
            render_all()
            updateGUI(text,col)

def examine_object():

    color = (10,10,150)
    for item in armor_group:
        if player.map_x == item.rect.x and player.map_y == item.rect.y:
            text = "%s, def %s, m.def %s, ste%s" % (item.name,item.defence,item.magic_def,item.stealth)
            updateGUI(text,(color))

    for item in treasure_group:
        if player.map_x == item.rect.x and player.map_y == item.rect.y:
            text = "A chest of loot"
            updateGUI(text,(color))

    for item in weapon_group:
        if player.map_x == item.rect.x and player.map_y == item.rect.y:
            text = "%s, att %s, m.att %s, hit%s" % (item.name,item.attack,item.magic_att,item.hit)
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
    for armor in armor_group:
        if armor.blocks and armor.rect.x/tile_width == x and armor.rect.y/tile_height == y:
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
    amount_armor = random.randint(0,max_armor)

    for i in range(amount_weapons):
        random_roll = random.randint(1,100)
        if random_roll <= 20:
            name = 'short sword'
            img = 'weapon.png'
            attack = random.randint(5,8)
            magic_attk = random.randint(1,3)
            hit = random.randint(1,2)
        elif random_roll > 20 and random_roll<= 30:
            name = 'bastard sword'
            img = 'weapon.png'
            attack = random.randint(7,11)
            magic_attk = random.randint(2,5)
            hit = random.randint(1,3)
        elif random_roll > 30 and random_roll<= 31:
            name = 'Flame blade'
            img = 'weapon.png'
            attack = random.randint(7,14)
            magic_attk = random.randint(5,10)
            hit = random.randint(1,6)
        elif random_roll > 31 and random_roll<= 51:
            name = 'wooden staff'
            img = 'weapon.png'
            attack = random.randint(3,7)
            magic_attk = random.randint(5,8)
            hit = random.randint(1,2)
        elif random_roll > 51 and random_roll<= 61:
            name = 'mage staff'
            img = 'weapon.png'
            attack = random.randint(5,9)
            magic_attk = random.randint(10,15)
            hit = random.randint(1,3)
        elif random_roll > 61 and random_roll<= 62:
            name = 'Thunder Staff'
            img = 'weapon.png'
            attack = random.randint(7,12)
            magic_attk = random.randint(15,25)
            hit = random.randint(1,6)
        elif random_roll > 62 and random_roll<= 82:
            name = 'iron dagger'
            img = 'weapon.png'
            attack = random.randint(2,6)
            magic_attk = random.randint(3,5)
            hit = random.randint(4,7)
        elif random_roll > 82 and random_roll<= 92:
            name = 'Steel dagger'
            img = 'weapon.png'
            attack = random.randint(5,9)
            magic_attk = random.randint(4,7)
            hit = random.randint(5,10)
        else:
            name = 'ninja knives'
            img = 'weapon.png'
            attack = random.randint(8,13)
            magic_attk = random.randint(5,9)
            hit = random.randint(9,18)

        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not is_exit(x,y):
                weapon = Weapon(x,y,name,img,attack,magic_attk,hit)
                weapon_group.add(weapon)


    for i in range(amount_armor):
        random_roll = random.randint(1,100)
        if random_roll <= 20:
            group = 'warrior'
            name = 'mail armor'
            img = 'armor.png'
            defence = random.randint(5,9)
            m_def = random.randint(1,4)
            stealth = -1
        elif random_roll > 20 and random_roll <= 30:
            group = 'warrior'
            name = 'plate armor'
            img = 'armor.png'
            defence = random.randint(8,13)
            m_def = random.randint(3,7)
            stealth = -1
        elif random_roll > 30 and random_roll <= 33:
            group = 'warrior'
            name = 'Dragon armor'
            img = 'armor.png'
            defence = random.randint(12,18)
            m_def = random.randint(7,10)
            stealth = -1
        elif random_roll > 33 and random_roll<= 53:
            group = 'wizard'
            name = 'common robe'
            img = 'armor.png'
            defence = random.randint(1,4)
            m_def = random.randint(7,12)
            stealth = -1
        elif random_roll > 53 and random_roll <= 63:
            group = 'wizard'
            name = 'silk robe'
            img = 'armor.png'
            defence = random.randint(4,7)
            m_def = random.randint(11,15)
            stealth = 0
        elif random_roll > 63 and random_roll <= 66:
            group = 'wizard'
            name = 'Thunder robes'
            img = 'armor.png'
            defence = random.randint(7,11)
            m_def = random.randint(14,18)
            stealth = 0
        elif random_roll > 66 and random_roll <= 86:
            group = 'rogue'
            name = 'fur armor'
            img = 'armor.png'
            defence = random.randint(3,6)
            m_def = random.randint(4,7)
            stealth = 1
        elif random_roll > 86 and random_roll <= 97:
            group = 'rogue'
            name = 'leather armor'
            img = 'armor.png'
            defence = random.randint(5,8)
            m_def = random.randint(4,7)
            stealth = 2
        else:
            group = 'rogue'
            name = 'Shadow cloak'
            img = 'armor.png'
            defence = random.randint(7,10)
            m_def = random.randint(5,9)
            stealth = 2

        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)
        if not is_semi_blocked(x,y):
            if not is_exit(x,y):
                armor = Armor(x,y,name,group,img,defence,m_def,stealth)
                armor_group.add(armor)

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
            img = 'goblin.png'
            attack = random.randint(12+monster_str,15+monster_str)
            defence = random.randint(2+monster_str,5+monster_str)
            hit = random.randint(15+monster_str,18+monster_str)
            dodge = random.randint(8+monster_str,11+monster_str)
            hp = random.randint(30+(monster_str*10),40+(monster_str*10))
            m_def = random.randint(4+monster_str,6+monster_str)
        elif random_roll > 50 and random_roll <= 85:
            name = 'orc'
            img = 'orc.png'
            attack = random.randint(8+monster_str,12+monster_str)
            defence = random.randint(9+monster_str,13+monster_str)
            hit = random.randint(10+monster_str,13+monster_str)
            dodge = random.randint(5+monster_str,7+monster_str)
            hp = random.randint(50+(monster_str*10),65+(monster_str*10))
            m_def = random.randint(7+monster_str,10+monster_str)
        else:
            name = 'troll'
            img = 'troll.png'
            attack = random.randint(16+monster_str,21+monster_str)
            defence = random.randint(10+monster_str,15+monster_str)
            hit = random.randint(5+monster_str,7+monster_str)
            dodge = random.randint(0+monster_str,1+monster_str)
            hp = random.randint(70+(monster_str*10),100+(monster_str*10))
            m_def = random.randint(10+monster_str,13+monster_str)

        x = random.randint(room.x1+1,room.x2-1)
        y = random.randint(room.y1+1,room.y2-1)

        if not is_blocked(x,y):
            if not is_exit(x,y):
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
        player = Player((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,player_naked_img)
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
    armor_group.empty()

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
    treasure_group.draw(tmp_map)
    armor_group.draw(tmp_map)
    weapon_group.draw(tmp_map)


def updateGUI(text,clr):

    #player info screen
    text1_1 = "HP    %s / %s       LEVEL   %s" % (player.hp,player.max_hp,player.level)
    text1_2 = "DEF       %s               M.DEF     %s" % (player.m_defence,player.m_magic_def)
    text1_3 = "ATT       %s             M.ATT     %s" % (player.m_attk_pwr,player.m_magic_att)
    text1_4 = "AVO       %s               M.AVO     %s" % (player.dodge,player.magic_dodge)
    text1_5 = "HIT       %s              M.HIT     %s" % (player.m_hit,player.magic_hit)
    text1_6 = "STEALTH   %s         XP    %s" % (player.m_stealth,player.xp)

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

    #equipment screen
    text2_1 = "health  X %s  fire  X %s  ice X %s" %  (player.heal_spell,player.fire_spell,player.ice_spell)
    text2_2 = "%s     " % player.weapon.name
    text2_3 = "att %s    m.att %s   hit %s" % (player.weapon.attack,player.weapon.magic_att,player.weapon.hit)
    text2_4 = "%s     "  % player.armor.name
    text2_5 = "def%s    m.def%s   ste %s" % (player.armor.defence,player.armor.magic_def,player.armor.stealth)

    text2_1 = font1.render(text2_1,1,(10,10,10))
    text2_2 = font1.render(text2_2,1,(10,10,10))
    text2_3 = font1.render(text2_3,1,(10,10,10))
    text2_4 = font1.render(text2_4,1,(10,10,10))
    text2_5 = font1.render(text2_5,1,(10,10,10))

    text2_1_pos = text2_1.get_rect()
    text2_2_pos = text2_2.get_rect()
    text2_3_pos = text2_3.get_rect()
    text2_4_pos = text2_4.get_rect()
    text2_5_pos = text2_5.get_rect()

    txt2_x,txt2_y = inventory.get_rect().topleft

    txt2_x += 10
    txt21_y = txt2_y + 20
    text2_1_pos.topleft = (txt2_x,txt21_y)

    txt22_y = txt2_y + 100
    text2_2_pos.topleft = (txt2_x,txt22_y)

    txt23_y = txt2_y + 120
    text2_3_pos.topleft = (txt2_x,txt23_y)

    txt24_y = txt2_y + 150
    text2_4_pos.topleft = (txt2_x,txt24_y)

    txt25_y = txt2_y + 170
    text2_5_pos.topleft = (txt2_x,txt25_y)

    inventory.fill((150,150,150))
    inventory.blit(text2_1,text2_1_pos)
    inventory.blit(text2_2,text2_2_pos)
    inventory.blit(text2_3,text2_3_pos)
    inventory.blit(text2_4,text2_4_pos)
    inventory.blit(text2_5,text2_5_pos)

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

def render_all():

    map_pos_x = player.rect.x - player.map_x
    map_pos_y = player.rect.y - player.map_y
    screen.blit(tmp_map, (map_pos_x ,map_pos_y))

    for m in monster_group:
        m.rect.x = map_pos_x + m.map_x
        m.rect.y = map_pos_y + m.map_y

    monster_group.draw(screen)
    player_sprite.draw(screen)


    screen.blit(vision_img, (0,0))

    screen.blit(gui, (tile_width*7,0))
    screen.blit(stats_gui, (tile_width * 7 + 10, 0 + 10))
    screen.blit(combat, (tile_width * 7 + 10, tile_height*2 + 10))
    screen.blit(inventory, (tile_width*7+10, tile_height * 4 + 10))


    pygame.display.flip()


#initialisation
basic_armor = Armor(0,0,"Rags",'naked','armor.png',2,2,0)
basic_weapon = Weapon(0,0,"pointy stick",'weapon.png',2,2,1)

#map images
wall_img = pygame.image.load('wall.jpg')
floor_img = pygame.image.load('floor.jpg')
exit_img = pygame.image.load('exit.jpg')
vision_img = pygame.image.load('fov.png').convert_alpha()

#effect images
blood_img = pygame.image.load('blood.png').convert_alpha()
scorch_img = pygame.image.load('scorch.png').convert_alpha()

#player images
player_naked_img = pygame.image.load('playernaked.png').convert_alpha()
player_warrior_img = pygame.image.load('playerwarrior.png').convert_alpha()
player_mage_img = pygame.image.load('playerwizard.png').convert_alpha()
player_rogue_img = pygame.image.load('playerrogue.png').convert_alpha()

player = Player((play_area_x/2)*tile_width,(play_area_y/2)*tile_height,player_naked_img)

player_sprite = pygame.sprite.RenderPlain((player))
monster_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
armor_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()

player_inventory = []


font1 = pygame.font.Font(None, 21)
font2 = pygame.font.Font(None, 21)

text_list = []
text1 = "You have entered a dark dungeon"
updateGUI(text1,(10,100,10))


make_map()


render_all()

clock = pygame.time.Clock()

while 1:

    clock.tick(60)

    pygame.display.flip()

    keypress = handle_keys()
    if keypress:
        break


#if __name__== '__main__': main()
