import pygame
import os


def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if tile.colliderect(rect):
            collisions.append(tile)
    return collisions


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.rect = pygame.Rect(pos.x, pos.y, 12, 24)
        self.sprites = {
            "right": [
                pygame.image.load(os.path.join("assets", "player_right0.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right2.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right3.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right4.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right5.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right6.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_right7.png")).convert_alpha()
                      ],
            "left": [
                pygame.image.load(os.path.join("assets", "player_left0.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left2.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left3.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left4.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left5.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left6.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets", "player_left7.png")).convert_alpha()
            ]
        }
        self.speed = 2
        self.momentum = pygame.Vector2(0, 0)
        self.airTime = 0
        self.jumpHeight = 8
        self.direction = "right"
        self.spriteCount = 0

    def update(self, dt, events, gameObjects):
        # temp varaibles
        gameMap = gameObjects["map"]
        interactables = gameObjects["interactables"]
        allObjects = gameMap + interactables
        vel = pygame.Vector2(0, 0)
        # check gliders
        for interactable in interactables:
            if interactable.__class__.__name__ == "Glider":
                if interactable.binded:
                    if interactable.direction:
                        vel.x += interactable.speed * dt
                    else:
                        vel.x -= interactable.speed * dt
        # events management
        if not events["console"]:
            if events["keys"][pygame.K_a] and events["keys"][pygame.K_d]:
                self.spriteCount = 0
            elif events["keys"][pygame.K_a]:
                vel.x -= 2 * dt
                self.direction = "left"
                self.spriteCount = (self.spriteCount + 1) % 40
            elif events["keys"][pygame.K_d]:
                vel.x += 2 * dt
                self.direction = "right"
                self.spriteCount = (self.spriteCount + 1) % 40
            else:
                self.spriteCount = 0
            for event in events["events"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.airTime < 3:
                            self.momentum.y = -self.jumpHeight
        # applying gravity
        self.momentum.y += 0.4 * dt
        # check for collision against tiles
        vel += self.momentum
        self.pos.x += vel.x
        self.rect.x = self.pos.x
        tiles = [tile.rect for tile in gameMap]
        for interactable in interactables:
            if interactable.collision:
                tiles.append(interactable.rect)
        collisions = collision_test(self.rect, tiles)
        for tile in collisions:
            if vel.x > 0:
                self.rect.right = tile.left
                self.pos.x = self.rect.x
            if vel.x < 0:
                self.rect.left = tile.right
                self.pos.x = self.rect.x
        self.pos.y += vel.y
        self.rect.y = self.pos.y
        tiles = [tile.rect for tile in gameMap]
        for interactable in interactables:
            if interactable.collision:
                tiles.append(interactable.rect)
        collisions = collision_test(self.rect, tiles)
        for tile in collisions:
            if vel.y > 0:
                self.rect.bottom = tile.top
                self.pos.y = self.rect.y
                self.airTime = 0
                self.momentum.y = 0
            if vel.y < 0:
                self.rect.top = tile.bottom
                self.pos.y = self.rect.y
                self.momentum.y = 0
        self.airTime += dt
        self.rect.topleft = self.pos

    def draw(self, window, camera):
        window.blit(self.sprites[self.direction][int(self.spriteCount/5)], (self.rect.x - camera.x, self.rect.y - camera.y))
