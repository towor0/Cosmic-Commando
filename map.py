import pygame
import os
import json
from helper import printConsole


class Map:
    def __init__(self):
        self.map = []
        self.interactables = []
        self.mousepos = pygame.Vector2(0, 0)
        self.raw = ""
        self.playerSpawn = pygame.Vector2()
        self.ship = None
        self.bg = None
        self.deathY = None
        self.gameOver = False

    def update(self, dt, events):
        self.mousepos = pygame.Vector2(events["mouse"].get_pos()[0], events["mouse"].get_pos()[1])
        for interactable in self.interactables:
            interactable.update(dt, events)
        if events["playerRect"].y > self.deathY:
            self.gameOver = True

    def findInteractable(self, codeName):
        for i in range(len(self.interactables)):
            if self.interactables[i].codeName == codeName:
                return i
        return -1

    def load(self, level):
        with open(os.path.join("assets", "levels", f"{level}.json")) as f:
            self.raw = json.load(f)
        # load variables
        self.playerSpawn = pygame.Vector2(self.raw["Player"]["x"], self.raw["Player"]["y"])
        self.deathY = self.raw["DeathY"]
        # load chunks
        for chunk in self.raw["Chunks"]:
            for row in range(chunk["row"]):
                for col in range(chunk["col"]):
                    place = ""
                    if col == 0:
                        place += "top"
                    elif col == chunk["col"] - 1:
                        place += "bot"
                    if row == 0:
                        place += "left"
                    elif row == chunk["row"] - 1:
                        place += "right"
                    if place == "":
                        place = "mid"
                    self.map.append(
                        Block(pygame.Vector2(row * 16 + chunk["x"], col * 16 + chunk["y"]), self.raw["Base"], place))
        for name in self.raw["Interactables"].keys():
            for item in self.raw["Interactables"][name]:
                if name == "Pilars":
                    self.interactables.append(Pilar(item))
                elif name == "Gliders":
                    self.interactables.append(Glider(item))
        # create instances
        self.ship = Ship(self.playerSpawn)
        self.bg = Background(pygame.Vector2(200, 0))

    def draw(self, window, camera, labelSurf):
        self.bg.draw(window, camera)
        for block in self.map:
            block.draw(window, camera)
        for interactable in self.interactables:
            interactable.draw(window, camera, self.mousepos, labelSurf)
        self.ship.draw(window, camera, self.mousepos, labelSurf)


class Block:
    def __init__(self, pos, base, place):
        self.sprite = pygame.image.load(os.path.join("assets", "blocks", f"{base}_{place}.png")).convert_alpha()
        self.rect = pygame.Rect(pos.x, pos.y, 16, 16)

    def update(self, dt, events):
        pass

    def draw(self, window, camera):
        window.blit(self.sprite, (self.rect.x - camera.x, self.rect.y - camera.y))


class Interactable:
    def __init__(self, codeName):
        self.codeName = codeName
        self.collision = True

    def help(self):
        return ["This is an Interactable Objects"]

    def draw(self, window, camera, mousepos, labelSurf):
        pass


class Pilar(Interactable):
    def __init__(self, item):
        Interactable.__init__(self, item["name"])
        self.pos = pygame.Vector2(item["x"], item["y"])
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 16, 96)
        self.sprite = pygame.image.load(os.path.join("assets", "interactables", "pilar.png")).convert_alpha()
        self.label = False
        labelFont = pygame.font.SysFont("arial", 10)
        self.renderedText = labelFont.render(self.codeName, True, (255, 255, 255))
        self.moving = False
        self.direction = False
        self.targety = 0
        self.speed = 1

    def activate(self):
        if not self.moving:
            self.moving = True
            if self.direction:
                self.targety = self.pos.y + self.rect.height
            else:
                self.targety = self.pos.y - self.rect.height
            printConsole("Activating...")
            return 0
        printConsole("Unable to activate.")

    def update(self, dt, events):
        if self.moving:
            detect = pygame.Rect(0, 0, self.rect.width, events["playerRect"].height)
            if self.direction:
                detect.topleft = self.rect.bottomleft
                if not detect.colliderect(events["playerRect"]):
                    self.pos.y += self.speed * dt
            else:
                detect.bottomleft = self.rect.topleft
                if not detect.colliderect(events["playerRect"]):
                    self.pos.y -= self.speed * dt
            if (self.direction and self.pos.y > self.targety) or \
                    (not self.direction and self.pos.y < self.targety):
                self.moving = False
                self.direction = not self.direction
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw(self, window, camera, mousepos, labelSurf):
        window.blit(self.sprite, (self.rect.x - camera.x, self.rect.y - camera.y))
        screenRect = pygame.Rect(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.width, self.rect.height)
        if screenRect.collidepoint(mousepos / 2):
            labelSurf.blit(self.renderedText, self.renderedText.get_rect(bottomright=mousepos))

    def help(self):
        printConsole("""This object can move up or down.
.activate(): will activate the pilar and move in a direction that have space.""")


class Glider(Interactable):
    def __init__(self, item):
        Interactable.__init__(self, item["name"])
        self.pos = pygame.Vector2(item["x"], item["y"])
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 48, 16)
        self.sprite = pygame.image.load(os.path.join("assets", "interactables", "glider.png")).convert_alpha()
        self.label = False
        self.type = item["type"]
        labelFont = pygame.font.SysFont("arial", 10)
        self.renderedText = labelFont.render(self.codeName, True, (255, 255, 255))
        self.moving = False
        self.direction = item["direction"]
        self.dest = item["dest"]
        self.targetpos = 0
        self.speed = 1
        self.binded = False

    def activate(self):
        if not self.moving:
            self.moving = True
            if self.type == "horizontal":
                if self.direction:
                    self.targetpos = self.pos.x + self.dest
                else:
                    self.targetpos = self.pos.x - self.dest
            elif self.type == "vertical":
                if self.direction:
                    self.targetpos = self.pos.y + self.dest
                else:
                    self.targetpos = self.pos.y - self.dest
            printConsole("Activating...")
            return 0
        printConsole("Unable to activate.")

    def getType(self):
        printConsole(self.type)

    def update(self, dt, events):
        self.binded = False
        if self.moving:
            if self.type == "vertical":
                detect = pygame.Rect(0, 0, self.rect.width, events["playerRect"].height)
                if self.direction:
                    detect.topleft = self.rect.bottomleft
                    if not detect.colliderect(events["playerRect"]):
                        self.pos.y += self.speed * dt
                else:
                    self.pos.y -= self.speed * dt
            elif self.type == "horizontal":
                detect = pygame.Rect(0, 0, events["playerRect"].width, self.rect.height)
                bindRect = pygame.Rect(0, 0, self.rect.width, 3)
                bindRect.bottomleft = self.rect.topleft
                if self.direction:
                    detect.topleft = self.rect.topright
                    if not detect.colliderect(events["playerRect"]):
                        self.pos.x += self.speed * dt
                        if bindRect.colliderect(events["playerRect"]):
                            self.binded = True
                else:
                    detect.topright = self.rect.topleft
                    if not detect.colliderect(events["playerRect"]):
                        self.pos.x -= self.speed * dt
                        if bindRect.colliderect(events["playerRect"]):
                            self.binded = True
            if (self.type == "vertical" and ((self.direction and self.pos.y > self.targetpos) or
                                             (not self.direction and self.pos.y < self.targetpos))) or (
                    self.type == "horizontal" and ((self.direction and self.pos.x > self.targetpos) or
                                                   (not self.direction and self.pos.x < self.targetpos))):
                self.moving = False
                self.direction = not self.direction
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw(self, window, camera, mousepos, labelSurf):
        window.blit(self.sprite, (self.rect.x - camera.x, self.rect.y - camera.y))
        screenRect = pygame.Rect(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.width, self.rect.height)
        if screenRect.collidepoint(mousepos / 2):
            labelSurf.blit(self.renderedText, self.renderedText.get_rect(bottomright=mousepos))

    def help(self):
        printConsole("""Commandos can move along with this object.
.activate(): will move to a designated area.
.getType(): will display the axis that this object can move in.""")


class Ship:
    def __init__(self, pSpawn):
        self.rect = pygame.Rect(pSpawn.x - 32, pSpawn.y - 8, 48, 36)
        self.sprite = pygame.image.load(os.path.join("assets", "ship.png")).convert_alpha()

    def update(self, dt, events):
        pass

    def draw(self, window, camera, mousepos, labelSurf):
        window.blit(self.sprite, (self.rect.x - camera.x, self.rect.y - camera.y))


class Background:
    def __init__(self, pos):
        self.bg = pygame.image.load(os.path.join("assets", "backgrounds", "background.png")).convert_alpha()
        self.planet = pygame.image.load(os.path.join("assets", "backgrounds", "planet.png")).convert_alpha()
        self.spos = pygame.Vector2(pos.x, pos.y)

    def update(self, dt, events):
        pass

    def draw(self, window, camera):
        window.blit(self.bg, (0, 0))
        window.blit(self.planet, (self.spos.x - (camera.x / 10), self.spos.y - (camera.y / 10)))
