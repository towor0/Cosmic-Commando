import pygame
import random


# tracks player's y position and adjust the camera position accordingly
class Camera:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 320, 240)
        self.targety = 0
        self.targetx = 0
        self.shaketime = 0

    def shake(self, time):
        self.shaketime += time

    def update(self, dt, player):
        # camera smoothening
        self.targetx, self.targety = player.center
        self.rect.centery += (self.targety - self.rect.centery) / 9
        self.rect.centerx += (self.targetx - self.rect.centerx) / 9
        # apply camera shakes
        if self.shaketime > 0:
            self.shaketime -= dt
            self.rect.x = random.randint(-4, 4)
            self.rect.y += random.randint(-4, 4)


