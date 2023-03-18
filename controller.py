import pygame
from player import Player
from map import Map
from camera import Camera
from console import Console
import os


class Controller:
    def __init__(self):
        gamestate = 0
        self.game = GameController()

    def update(self, dt, events):
        self.game.update(dt, events)

    def draw(self, window):
        self.game.draw(window)


class MenuController:
    def __init__(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, window):
        pass


class GameController:
    def __init__(self):
        self.map = Map()
        self.map.load(1)
        self.player = Player(self.map.playerSpawn)
        self.gameSurf = pygame.Surface((320, 240)).convert_alpha()
        self.consoleSurf = pygame.Surface((640, 480)).convert_alpha()
        self.guiSurf = pygame.Surface((640, 480)).convert_alpha()
        self.camera = Camera()
        self.console = Console()
        f = open("gameConsoleLog.txt", "w")
        f.close()
        pygame.mixer.music.play(-1)

    def update_events(self, events):
        events["console"] = self.console.active
        return events

    def execute(self):
        code = self.console.code
        # replacing objects and index
        codeName = ""
        while code.find("Objects") != -1:
            if code[code.find("Objects") + 8] == "\"":
                i = code.find("Objects") + 9
                while i < len(code):
                    if code[i] == "\"":
                        break
                    else:
                        codeName += code[i]
                    i += 1
                r = self.map.findInteractable(codeName)
                if r != -1:
                    code = code[:code.find(codeName)-1] + str(r) + code[code.find(codeName) + len(codeName)+1:]
                code = code[:code.find("Objects")] + "self.map.interactables"+ code[code.find("Objects")+7:]
        try:
            exec(code)
            with open("gameConsoleLog.txt", "r") as f:
                feedback = f.read().split("\n")
            if feedback:
                self.console.renderResult(feedback)
        except Exception as e:
            self.console.renderResult("INVALID COMMAND")
            print(e)
        self.console.execute = False
        self.console.code = ""
        self.console.renderedCode = []

    def update(self, dt, events):
        events = self.update_events(events)
        self.player.update(dt, events, {"map": self.map.map, "interactables": self.map.interactables})
        self.camera.update(dt, self.player.rect)
        self.map.update(dt, events)
        self.console.update(dt, events)
        # checking console code
        if self.console.execute:
            self.execute()

    def draw(self, window):
        self.gameSurf.fill((0, 0, 0, 0))
        self.consoleSurf.fill((0, 0, 0, 0))
        self.guiSurf.fill((0, 0, 0, 0))
        self.player.draw(self.gameSurf, self.camera.rect)
        self.map.draw(self.gameSurf, self.camera.rect, self.guiSurf)
        self.console.draw(self.consoleSurf)
        window.blit(pygame.transform.scale(self.gameSurf, (640, 480)), (0, 0))
        window.blit(self.guiSurf, (0, 0))
        window.blit(self.consoleSurf, (0, 0))
