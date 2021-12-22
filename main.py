import random as r
import sys as s
import pygame as p
import math as m

  #--------------------------------#
# | tower defense Game             |
# | version 1.0                    |
# | Made by Zente                  |
# | (with the assistance of Peter) |
# | 2021                           |
# | kosikzente@gmail.com           |
  #--------------------------------#
# TO DO 2.0 Zoom and scroll, MUSIC/ SOUND EFFECTS/ BOTH, Sprite class


class Game():
    def __init__(self):
        p.init()
        self.font = p.font.SysFont(p.font.get_default_font(), 50)
        self.large_font = p.font.SysFont(p.font.get_default_font(), 75)
        self.score = 0
        self.tower_types = ["machine gun", "spray", "lightning tower", "bomb tower", "slowness tower", "poison tower"]
        self.health = 100
        self.sizex = 970
        self.sizey = 839
        self.level_limits = {1:250, 2:1050, 3:2050, 4:4000}
        self.level_rewards = {0:600, 1:370, 2:440, 3:500, 4:0}
        self.levelchoices = {
            1:[1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5,],
            2:[1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6],
            3:[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6],
            4:[1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6]
            }
        self.level = 1
        self.stage = p.display.set_mode((self.sizex, self.sizey))
        p.display.set_caption("TOWER DEFENSE")
        self.clock = p.time.Clock()
        self.fps = 30
        self.bullets = []
        #enemy spawn
        self.spawnx = 0
        self.spawny = 0
        self.enemies = []
        self.carried_item = None #carried by mouse
        self.cash = 0
        self.title_on = False
        self.level_outro_on = False
        self.create_menu()

    def create_menu(self):
        self.menu = [Cell(22, 2, "machine gun", self),
                    Cell(22, 4, "spray", self),
                    Cell(22, 6, "lightning tower", self),
                    Cell(22, 8, "bomb tower", self),
                    Cell(22, 10, "slowness tower", self),
                    Cell(22, 12, "poison tower", self)]
                    # things to buy

    def refresh(self):
        self.stage.fill("black")
        for layer in [0,1]:

            for row in self.grid:
                for x in row:
                    if x.layer == layer:
                        x.refresh()
        if self.title_on:
            credit = self.font.render("Made by Zente (with the assistance of Peter)2021",False,(200,170,25))
            self.stage.blit(credit,(20,700))
            objective = self.font.render("defend your base from the evil",False,(200,170,25))
            self.stage.blit(objective,(20,20))
            objective2 = self.font.render("invaders by placeing towers",False,(200,170,25))
            self.stage.blit(objective2,(20,60))
            version = self.font.render("version 1.0",False,(200,170,25))
            self.stage.blit(version,(20,740))

        elif self.level_outro_on:
            outro = self.large_font.render("Level completed Well Done",False,(180,30,30))
            self.stage.blit(outro,(120,380))

        else:
            for s in self.enemies + self.menu + self.bullets:
                s.refresh()
            if self.carried_item != None:
                self.carried_item.refresh()
            self.display_values()
        p.display.flip()

    def display_values(self):
        cash_costume = self.font.render(str(self.cash),False,(250,150,0))
        health_costume = self.font.render(str(self.health),False,(250,150,0))
        self.stage.blit(cash_costume,(880,20))
        self.stage.blit(health_costume,(880,775))

    def clean_dead (self):
        for e in self.enemies:
            if e.health <= 0:
                self.cash += e.reward
                self.score += e.score_reward
        self.bullets = [x for x in self.bullets if x.lives > 0]
        self.enemies = [x for x in self.enemies if x.health > 0]

    def create_level(self):
        self.enemy_choice = self.levelchoices[self.level]
        self.cash += self.level_rewards[self.level - 1]
        with open ("map/level{}.map".format(self.level)) as file:
            levelmap = file.read().split ("\n")
            self.create_grid(levelmap)

    def create_grid(self, map):
        self.grid = []
        y = 0
        for row in map:
            gridrow = []
            x = 0
            for c in row: # c: cell character
                if c == "-":
                    type = "background"
                elif c == "_":
                    type = "pathway"
                elif c == "S":
                    self.spawnx = x
                    self.spawny = y
                    type = "pathway"
                elif c == "o":
                    type = "tower place"
                elif c == "B":
                    type = "Base"

                    self.Base_x = x
                    self.Base_y = y
                else:
                    type = None
                if type != None:
                    gridrow += [Cell(x, y, type, self)]
                x += 1
            self.grid += [gridrow]
            y +=1

    def play (self):
        self.display_title()
        self.create_level()
        self.ispaused = False
        self.frame_counter = 0
        self.game_on = True
        while self.game_on:
            if self.ispaused == False:
                self.frame_counter += 1
                if r.randint (1, self.fps) ==1:
                    self.add_enemy()
                self.clean_dead()
                self.move_sprites()
                self.shoot()
                self.check_level()
            self.handle_events()
            self.refresh()
            self.clock.tick(self.fps)
            if self.health <= 0:
                self.game_on = False
        self.display_end_title()

    def level_outro(self):
        self.cash //= 2
        self.level_outro_on = True
        for e in range(45):
            self.refresh()
            self.handle_events()
            self.clock.tick(self.fps)
        self.level_outro_on = False


    def display_title(self):
        self.title_on = True
        with open("map/title.map") as file:
            titlemap = file.read().split ("\n")
            self.create_grid(titlemap)
        for e in range(120):
            self.refresh()
            self.handle_events()
            self.clock.tick(self.fps)
        self.stage = p.display.set_mode((self.sizex, self.sizey ))
        self.title_on = False

    def display_end_title(self):
        self.title_on = True
        with open("map/end title.map") as file:
            endtitlemap = file.read().split ("\n")
            self.create_grid(endtitlemap)
        for e in range(75):
            self.refresh()
            self.handle_events()
            self.clock.tick(self.fps)
        self.stage = p.display.set_mode((self.sizex, self.sizey ))
        self.title_on = False

    def add_enemy(self):
        self.enemies += [Enemy (r.choice(self.enemy_choice),self)]

    def move_sprites(self):
        for s in self.enemies +self.bullets:
            s.move()

    def shoot(self):
        for row in self.grid:
            for x in row:
                x.shoot()

    def check_level(self):
        if self.score >= self.level_limits[self.level]:
            self.level += 1
            self.enemies = []
            self.level_outro()
            self.create_level()

    def handle_events (self):
        for event in p.event.get():
            if event.type == p.KEYDOWN :
                if event.key == p.K_ESCAPE:
                    s.exit()
                elif event.key == p.K_p:
                    self.ispaused = not self.ispaused
            elif event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.carried_item == None:
                        for item in self.menu:
                            if (item.rect.collidepoint(p.mouse.get_pos())
                                and item.price <= self.cash):
                                self.carried_item = Carried_item(item.type, self)
                                self.cash -= item.price
                    else:
                        for row in self.grid:
                            for cell in row:
                                if (cell.rect.collidepoint(p.mouse.get_pos())
                                    and cell.type == "tower place"):
                                    cell.set_type (self.carried_item.type)
                                    cell.create_costume()
                                    self.carried_item = None
                elif event.button == 3:
                    for row in self.grid:
                        for cell in row:
                            if (cell.rect.collidepoint(p.mouse.get_pos())
                                and cell.type in self.tower_types):
                                self.cash += cell.price // 2
                                cell.set_type ("tower place")
                                cell.create_costume()
            elif event.type == p.QUIT:
                s.exit()


""" TO DO
class Sprite():
    def __init__ (self, type, game):
        self.game = game
        self.kind == dummy
        self.rcostume = p.image.load("cell/" + type + ".png")
        self.costume = p.transform.rotozoom(self.rcostume, 0, 0.5)
        self.rect = self.costume.get_rect()
        self.set_type(type)
        self.create_costume()

    def set_type (self, type):
        self.type = type
        self.size = self.sizes [self.type]


    def create_costume(self):
        self.rcostume = p.image.load("cell/" + self.type + ".png")
        if self.game.title_on:
            self.costume = p.transform.rotozoom(self.rcostume, 0,self.size/2)
        else:
            self.costume = p.transform.rotozoom(self.rcostume, 0,self.size)
        self.rect = self.costume.get_rect()

    def refresh(self):
        if self.game.title_on:
            self.rect.centerx = self.x * 10 + 165
            self.rect.centery = self.y * 20 + 300
        else:
            self.rect.centerx = self.x * 40 + 40
            self.rect.centery = self.y * 40 + 40
        self.game.stage.blit(self.costume, self.rect)
"""


class Cell():
    def __init__ (self, x, y, type, game):
        self.x = x
        self.y = y
        self.game = game
        self.ranges = {
            "machine gun":1, "lightning tower":2, "spray":1,
            "bomb tower":1,"background":None,"pathway":None,
            "tower place":None, "Base":None, "spawn":None,
            "slowness tower":3, "poison tower":1,
        }
        self.sizes = {
            "machine gun":0.5, "lightning tower":0.4, "spray":0.3,
            "bomb tower":0.6, "background":0.5,"pathway":0.5,
            "tower place":0.5, "Base":0.5, "spawn":0.5,
            "slowness tower":0.45, "poison tower":0.5,
        }
        self.prices = {
            "machine gun":350, "spray":150, "lightning tower":450,
            "bomb tower":200, "background":None,"pathway":None,
            "tower place":None, "Base":None, "spawn":None,
            "slowness tower":270, "poison tower":250,
        }
        self.shootrates = {
            "machine gun":10, "spray":17, "lightning tower":18,
            "bomb tower":22, "background":None,"pathway":None,
            "tower place":None, "Base":None, "spawn":None,
            "slowness tower":15, "poison tower":15,
        }
        self.layers = {
            "machine gun":1, "spray":1, "lightning tower":1,
            "bomb tower":1, "background":0,"pathway":0,
            "tower place":0, "Base":0, "spawn":0,
            "slowness tower":1, "poison tower":1,
        }
        self.set_type(type)
        self.create_costume()

    def set_type (self, type):
        self.type = type
        self.range = self.ranges [self.type]
        self.size = self.sizes [self.type]
        self.price = self.prices [self.type]
        self.shootrate = self.shootrates[self.type]
        self.layer = self.layers[self.type]

    def create_costume(self):
        self.rcostume = p.image.load("cell/" + self.type + ".png")
        if self.game.title_on:
            self.costume = p.transform.rotozoom(self.rcostume, 0,self.size/2)
        else:
            self.costume = p.transform.rotozoom(self.rcostume, 0,self.size)
        self.rect = self.costume.get_rect()

    def refresh(self):
        if self.game.title_on:
            self.rect.centerx = self.x * 10 + 165
            self.rect.centery = self.y * 20 + 300
        else:
            self.rect.centerx = self.x * 40 + 40
            self.rect.centery = self.y * 40 + 40
        self.game.stage.blit(self.costume, self.rect)

    def shoot(self):
        if (self.shootrate != None and
                r.randint (1,self.shootrate) == 1 and self.range != None):
            for e in self.game.enemies:
                if (-self.range <= self.x - e.x <= self.range and
                    -self.range <= self.y - e.y <= self.range):
                    b = Bullet(self.type,self.game,
                        self.rect.centerx, self.rect.centery,
                        e.screenx, e.screeny)
                    self.game.bullets +=[b]
                    if self.type == "machine gun" or "lightning tower":
                        break


class Carried_item():
    def __init__(self, type, game):
        self.type = type
        self.game = game
        self.rcostume = p.image.load("cell/" + type + ".png")
        self.costume = p.transform.rotozoom(self.rcostume, 0, 0.5)
        self.rect = self.costume.get_rect()

    def refresh(self):
        self.rect.center = p.mouse.get_pos()
        self.game.stage.blit(self.costume, self.rect)


class Bullet ():
    def __init__(self, type, game, startx, starty, targetx, targety):
        self.type = type
        self.game = game
        self.damages = {
            "spray":(10, None), "machine gun":(15, None),
            "lightning tower":(60, None), "bomb tower":(12, None),
            "slowness tower": (6, "F"), "poison tower":(10, "P")
        }
        self.sizes = {
            "spray":0.4, "machine gun":0.034,
            "lightning tower":0.6, "bomb tower":0.4,
            "slowness tower":0.3, "poison tower":0.3
        }

        self.area_damages = {
            "spray":1, "machine gun":0,
            "lightning tower":0.2, "bomb tower":1,
            "slowness tower":0.4, "poison tower":0.4
        }
        self.costume_numbers = {
            "spray":1, "machine gun":1,
            "lightning tower":1, "bomb tower":1,
            "slowness tower":21, "poison tower":1
        }
        self.explosions = {
            "spray":False, "machine gun":False,
            "lightning tower":False, "bomb tower":True,
            "slowness tower":False, "poison tower":False
        }
        self.damage = self.damages[type]
        self.size = self.sizes[type]
        self.area_damage = self.area_damages[type]
        self.costume_number = self.costume_numbers[type]
        self.will_explode = self.explosions[type]
        self.costume_number_current = 1
        self.screenx = startx
        self.screeny = starty
        self.targetx = targetx
        self.targety = targety
        self.explode_on = False
        self.explode_counter = 0
        self.lives = 1
        self.dx = targetx - startx
        self.dy = targety - starty
        distance = m.sqrt(self.dx **2 + self.dy **2)#Pythagorean theorem
        self.speed = 5
        self.max_steps = distance / self.speed
        self.steps = 0
        self.speedx = (self.speed/distance)*self.dx#similarity
        self.speedy = (self.speed/distance)*self.dy#similarity
        self.rcostumes = [p.image.load("bullet/{} bullet{}.png" .format(type, i)) for i in range(1, self.costume_number + 1)]
        self.costumes = [p.transform.rotozoom(x, 0, self.size)for x in self.rcostumes]
        self.rect = self.costumes[self.costume_number_current-1].get_rect()


    def set_angle(self, x, y):
        if x == 0:
            if 0 < y:
                self.angle = 90
            else:
                self.angle = -90
        elif 0 < x:
            self.angle = 90 - m.atan(y/x)*180/m.pi
        else:
            self.angle = 270 - m.atan(y/x)*180/m.pi


    def dc (self):
        if self.area_damage == 0:
            for e in self.game.enemies:
                if self.rect.colliderect(e.rect):
                    self.hurt(e)
        else:
            for e in self.game.enemies:
                dx = e.screenx - self.screenx
                dy = e.screeny - self.screeny
                distance = m.sqrt(dx **2 + dy **2)#Pythagorean theorem
                if distance <= self.area_damage*40:
                    self.hurt(e)

    def hurt (self, e):
        e.health -= self.damage[0]
        if self.damage[1] == "F":
            e.frozen = True
            e.frozen_counter = 0
        if self.damage[1] == "P":
            e.poison = True

    def refresh (self):
        self.rect.centerx = self.screenx
        self.rect.centery = self.screeny
        self.set_angle(self.dx, self.dy)
        if self.explode_on:
                rcostume = p.image.load("bullet/bang-{}.png" .format(self.explode_counter))
                costume = p.transform.rotozoom(rcostume, self.angle, 0.13)

        else:
            rcostume = self.rcostumes[ self.costume_number_current -1]
            costume = p.transform.rotozoom(rcostume, self.angle, self.size)
        self.game.stage.blit(costume, self.rect)
        self.costume_number_current += 1
        if self.costume_number < self.costume_number_current:
            self.costume_number_current = 1


    def move(self):
        if not self.explode_on:
            self.screenx += self.speedx
            self.screeny += self.speedy
            self.steps += 1
            if self.steps >= self.max_steps: #if the bullet has arrived
                if self.will_explode:
                    self.explode_on = True
                else:
                    self.dc()
                    self.lives = 0
        else:
            self.explode_counter += 1
            if self.explode_counter > 9:
                self.dc()
                self.explode_on = False
                self.lives = 0

class Enemy():
    def __init__ (self, type, game,):
        self.type = type # 1, 2, 3, 4, 5, 6
        self.health = type*40+40 # 80, 120, 160, 200, 240, 280
        self.reward = type*4+5 # 8, 11, 14, 17, 20, 23
        self.score_reward = type + 2
        self.poison = False
        self.frozen_counter = 0
        self.frozen_max = 90
        self.frozen = False
        self.game = game
        self.x = self.game.spawnx
        self.y = self.game.spawny
        self.screenx = self.x * 40 + 40
        self.screeny = self.y * 40 + 40
        self.isgliding = False
        self.prevx = None
        self.prevy = None
        self.targetx = None
        self.targety = None
        self.xcorrections = {1:0, 2:0, 3:15, 4:-7, 5:0, 6:0}
        self.xcorrection = self.xcorrections[self.type]
        self.sizes = {1:0.65, 2:0.24, 3:0.65, 4:0.5, 5:1, 6:0.2}
        self.size = self.sizes[self.type]
        self.speeds = {1:1.5, 2:1, 3:0.9, 4:1, 5:1.2, 6:0.8}
        self.speed = self.speeds[self.type]
        self.damages = {1:8, 2:14, 3:20, 4:29, 5:32, 6:40}
        self.damage = self.damages[self.type]
        self.animation_delays = {1:3, 2:1, 3:7, 4:1, 5:1, 6:1}
        self.animation_delay = self.animation_delays[self.type]
        self.costume_numbers = {1:6, 2:1, 3:3, 4:1, 5:11, 6:1}
        self.costume_number = self.costume_numbers[self.type]
        self.costume_number_current = 1
        self.rcostumes = [p.image.load("enemy/enemy{}_{}.png" .format(self.type, i)) for i in range(1, self.costume_number + 1)]
        self.costumes = [p.transform.rotozoom(x, 0, self.size)for x in self.rcostumes]
        self.rect = self.costumes[self.costume_number_current -1].get_rect()

    def refresh (self):
        self.rect.centerx = self.screenx + self.xcorrection
        self.rect.centery = self.screeny
        self.game.stage.blit(self.costumes[self.costume_number_current -1], self.rect)
        if self.game.frame_counter % self.animation_delay == 0:
            self.costume_number_current += 1
            if self.costume_number < self.costume_number_current:
                self.costume_number_current = 1

    def check_poison (self):
        if self.poison == True:
            self.health -= 0.1 # TEST THIS!!!!!!!!!!

    def move (self):
        if self.isgliding == True:
            self.glide()
        else:
            self.select_target()
        self.check_poison()

    def glide (self):
        if self.frozen == True:
            speed = self.speed /3
            self.frozen_counter += 1
            if self.frozen_counter == self.frozen_max:
                self.frozen = False
        else:
            speed = self.speed
        if self.targetx > self.x:
            self.screenx += speed
        elif self.targetx  < self.x:
            self.screenx -= speed
        if self.targety > self.y:
            self.screeny += speed
        elif self.targety  < self.y:
            self.screeny -= speed
        if (-2< self.screenx - (self.targetx*40+40) < 2 and
            -2< self.screeny - (self.targety*40+40) < 2):
            self.isgliding = False
            self.screenx = self.targetx*40+40
            self.screeny = self.targety*40+40
            self.x = self.targetx
            self.y = self.targety
            if (self.x == self.game.Base_x and
                self.y == self.game.Base_y):
                    self.health -= 1000
                    game.health -= self.damage

    def select_target(self):
        self.select_neighbours()
        self.filter_()
        self.choose()

    def select_neighbours(self):
        neighbourcords = [(0,-1),(0,1),(-1,0),(1,0)]
        self.neighbours = []
        for x,y in neighbourcords:
            try:
                self.neighbours += [self.game.grid[self.y + y][self.x + x]]
            except:
                pass

    def filter_(self):
        self.possible_targets = []
        for n in self.neighbours:
            if n.type == "Base":
                self.possible_targets = [n]
        if self.possible_targets == []:
            for n in self.neighbours:
                if (n.type == "pathway" and
                    (n.x, n.y) != (self.prevx, self.prevy) and
                    (n.x, n.y) != (self.game.spawnx, self.game.spawny)):
                    self.possible_targets += [n]

    def choose(self):
        try:
            target = r.choice(self.possible_targets)
            self.targetx = target.x
            self.targety = target.y
            self.prevx = self.x
            self.prevy = self.y
            self.isgliding = True
        except:
            pass


game = Game ()
game.play()
