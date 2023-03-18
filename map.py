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

    def update(self, dt, events):
        self.mousepos = pygame.Vector2(events["mouse"].get_pos()[0], events["mouse"].get_pos()[1])
        for interactable in self.interactables:
            interactable.update(dt, events)

    def findInteractable(self, codeName):
        for i in range(len(self.interactables)):
            if self.interactables[i].codeName == codeName:
                return i
        return -1

    def load(self, level):
        with open(os.path.join("assets", "levels", f"{level}.json")) as f:
            self.raw = json.load(f)
        # load player position
        self.playerSpawn = pygame.Vector2(self.raw["Player"]["x"], self.raw["Player"]["y"])
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
                    self.interactables.append(Pilar(pygame.Vector2(item["x"], item["y"]), item["name"]))

    def draw(self, window, camera, labelSurf):
        for block in self.map:
            block.draw(window, camera)
        for interactable in self.interactables:
            interactable.draw(window, camera, self.mousepos, labelSurf)


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
    def __init__(self, pos, codename):
        Interactable.__init__(self, codename)
        self.pos = pos
        self.rect = pygame.Rect(pos.x, pos.y, 16, 96)
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
            if self.direction:
                self.pos.y += self.speed * dt
            else:
                self.pos.y -= self.speed * dt
            if (self.direction and self.pos.y > self.targety) or \
                    (not self.direction and self.pos.y < self.targety):
                self.moving = False
                self.direction = not self.direction
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw(self, window, camera, mousepos, labelSurf):
        if self.collision:
            window.blit(self.sprite, (self.rect.x - camera.x, self.rect.y - camera.y))
        screenRect = pygame.Rect(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.width, self.rect.height)
        if screenRect.collidepoint(mousepos / 2):
            labelSurf.blit(self.renderedText, self.renderedText.get_rect(bottomright=mousepos))

    def help(self):
        printConsole("""This object can move up or down.
.activate(): will activate the pilar and move in a direction that have space.""")
