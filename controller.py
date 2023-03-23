import pygame
from player import Player
from map import Map
from camera import Camera
from console import Console
import os


class Controller:
    def __init__(self):
        self.gamestate = 0
        self.game = GameController(1)
        self.gameOverMenu = GameOverMenuController()

    def update(self, dt, events):
        if self.gamestate == 0:
            self.game.update(dt, events)
        elif self.gamestate == 1:
            self.gameOverMenu.update(dt, events)
        if self.game.map.gameOver:
            self.gamestate = 1
            self.gameOverMenu.start()
            self.game.map.gameOver = False
            pygame.mixer.music.stop()
        if self.gameOverMenu.restart:
            self.gameOverMenu.restart = False
            self.game = GameController(1)
            self.gamestate = 0

    def draw(self, window):
        if self.gamestate == 0:
            self.game.draw(window)
        if self.gamestate == 1:
            self.gameOverMenu.draw(window)


class MenuController:
    def __init__(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, window):
        pass


class GameOverMenuController:
    def __init__(self):
        self.bg = pygame.transform.scale(
            pygame.image.load(
                os.path.join("assets", "backgrounds", "deathbackground.png")).convert_alpha(), (640, 480))
        self.posy = 0
        self.speed = 15
        self.startdisplay = False
        self.displayTimer = 0
        self.strText = "CONNECTION LOST"
        self.prev = ""
        self.textFont = pygame.font.Font(os.path.join("assets", "Meyrin.ttf"), 80)
        self.displayInterval = 5
        self.renderedText = self.textFont.render("", True, (255, 255, 255))
        self.strokeSound = pygame.mixer.Sound(os.path.join("assets", "key.wav"))
        self.restartFont = pygame.font.SysFont("arial", 30)
        self.restartFont.set_bold(True)
        self.restartText = self.restartFont.render("PRESS ENTER TO RESTART", True, (255, 255, 255))
        self.restartVisible = False
        self.restartOp = 0
        self.restart = False

    def start(self):
        self.displayTimer = 0
        self.startdisplay = True
        self.renderedText = self.textFont.render("", True, (255, 255, 255))
        self.restartVisible = False
        self.restartOp = 0
        self.restartText.set_alpha(self.restartOp)

    def update(self, dt, events):
        self.posy = -(abs(self.posy - self.speed * dt) % 480)
        if self.startdisplay:
            self.displayTimer += dt
            if self.displayTimer < (len(self.strText)+1) * self.displayInterval:
                self.renderedText = self.textFont.render(
                    self.strText[0:int(self.displayTimer/self.displayInterval)], True, (255, 255, 255))
                if self.strText[0:int(self.displayTimer / self.displayInterval)] != self.prev:
                    pygame.mixer.Channel(1).play(self.strokeSound)
                self.prev = self.strText[0:int(self.displayTimer / self.displayInterval)]
            else:
                self.startdisplay = False
                self.restartVisible = True
        elif self.restartOp < 255:
            self.restartOp += 10 * dt
            self.restartText.set_alpha(self.restartOp)
        for event in events["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.restart = True

    def draw(self, window):
        window.blit(self.bg, (0, self.posy))
        window.blit(self.bg, (0, self.posy + 480))
        window.blit(self.renderedText, self.renderedText.get_rect(center=(320, 200)))
        if self.restartVisible:
            window.blit(self.restartText, self.restartText.get_rect(center=(320, 270)))


class GameController:
    def __init__(self, level):
        self.map = Map()
        self.map.load(level)
        self.player = Player(self.map.playerSpawn)
        self.gameSurf = pygame.Surface((320, 240)).convert_alpha()
        self.consoleSurf = pygame.Surface((640, 480)).convert_alpha()
        self.guiSurf = pygame.Surface((640, 480)).convert_alpha()
        self.camera = Camera(self.map.playerSpawn)
        self.console = Console()
        f = open("gameConsoleLog.txt", "w")
        f.close()
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.25)

    def update_events(self, events):
        events["console"] = self.console.active
        events["playerRect"] = self.player.rect
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
                    code = code[:code.find(codeName) - 1] + str(r) + code[code.find(codeName) + len(codeName) + 1:]
                code = code[:code.find("Objects")] + "self.map.interactables" + code[code.find("Objects") + 7:]
        try:
            f = open("gameConsoleLog.txt", "w")
            f.close()
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
        self.map.draw(self.gameSurf, self.camera.rect, self.guiSurf)
        self.player.draw(self.gameSurf, self.camera.rect)
        self.console.draw(self.consoleSurf)
        window.blit(pygame.transform.scale(self.gameSurf, (640, 480)), (0, 0))
        window.blit(self.guiSurf, (0, 0))
        window.blit(self.consoleSurf, (0, 0))
