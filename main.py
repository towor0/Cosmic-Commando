import pygame
import time
import sys
import os

from controller import Controller

# initialize pygame
pygame.init()
# change application name
pygame.display.set_caption("Cosmic Commando")
# clock and previous time for delta time calculation
clock = pygame.time.Clock()
prev_time = time.time()
# define screen size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
# create pygame window and instance initiation
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
window = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
running = True
# sound setup
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("assets", "bgm.wav"))
# initialize controllers
controller = Controller()

# game loop
while running:
    # 60 fps frame cap
    clock.tick(60)
    # frame rate independency
    now = time.time()
    dt = (now - prev_time) * 60
    prev_time = now
    # check if the player wants to quit
    events = {
        "events": pygame.event.get(),
        "keys": pygame.key.get_pressed(),
        "console": False,
        "mouse": pygame.mouse
    }
    for event in events["events"]:
        if event.type == pygame.QUIT:
            running = False
    # update all instances
    controller.update(dt, events)
    # draw all instances
    window.fill((0, 0, 0))
    controller.draw(window)
    screen.blit(window, (0, 0))
    pygame.display.flip()

# quit
pygame.quit()
sys.exit()
