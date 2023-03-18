import pygame
import os


class Console:
    def __init__(self):
        self.consoleFont = pygame.font.Font(os.path.join("assets", "Meyrin.ttf"), 30)
        self.consoleSprite = pygame.image.load(os.path.join("assets", "console.png")).convert_alpha()
        self.pos = pygame.Vector2(0, 400)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 640, 480)
        self.textRect = pygame.Rect(self.pos.x, self.pos.y, 530, 480)
        self.active = False
        self.transition = False
        self.targety = 400
        self.code = ""
        self.execute = False
        self.renderedCode = [self.consoleFont.render(self.code, True, (255, 255, 255))]
        self.renderedResult = []

    def update(self, dt, events):
        self.rect.x, self.rect.y = self.pos
        self.textRect.x, self.textRect.y = self.pos
        self.textRect.x += 55
        self.textRect.y += 50
        for event in events["events"]:
            if not self.transition:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.active = not self.active
                        self.transition = True
                        if self.active:
                            self.targety = 50
                        else:
                            self.targety = 400
                    elif self.active:
                        self.renderedResult = []
                        if event.key == pygame.K_BACKSPACE:
                            self.code = self.code[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.execute = True
                        else:
                            self.code += event.unicode
                        self.renderedCode = []
                        for i in range(int(len(self.code) / 38) + 1):
                            if i == int(len(self.code) / 38) + 1:
                                self.renderedCode.append(
                                    self.consoleFont.render(self.code[38 * i:], True, (255, 255, 255)))
                            else:
                                self.renderedCode.append(
                                    self.consoleFont.render(self.code[38 * i: 38 * (i + 1)], True, (255, 255, 255)))
        if self.transition:
            self.pos.y += (self.targety - self.pos.y) / 10 * dt
            if abs(self.pos.y - self.targety) < 1:
                self.transition = False

    def renderResult(self, results):
        if results == "INVALID COMMAND":
            self.renderedResult.append(
                self.consoleFont.render("INVALID COMMAND", True, (255, 0, 0)))
            return 0
        for result in results:
            for i in range(int(len(result) / 38) + 1):
                if i == int(len(self.code) / 38) + 1:
                    self.renderedResult.append(
                        self.consoleFont.render(result[38 * i:], True, (0, 255, 0)))
                else:
                    self.renderedResult.append(
                        self.consoleFont.render(result[38 * i: 38 * (i + 1)], True, (0, 255, 0)))

    def draw(self, window):
        window.blit(self.consoleSprite, self.rect)
        for i in range(len(self.renderedCode)):
            window.blit(self.renderedCode[i],
                        self.renderedCode[i].get_rect(topleft=(self.textRect.x, self.textRect.y + i * 50)))
        for i in range(len(self.renderedResult)):
            window.blit(self.renderedResult[i],
                        self.renderedResult[i].get_rect(
                            topleft=(self.textRect.x, self.textRect.y + i * 50 + len(self.renderedCode) * 50)))
