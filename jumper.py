import pygame
import sys
import os

FPS = 50
GRAVITY = 200

pygame.init()
size = WIDTH, HEIGHT = 1000, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Camera:
    def __init__(self, target=None, limit=500):
        self.x = 0
        self.set_target(target, limit)

    def apply(self, group, k=1):
        for sprite in group:
            if sprite != self.target:
                sprite.rect.x = sprite.start_pos[0] + (self.x - sprite.camera_delta) * k - 2

    def set_target(self, target, limit):
        self.target = target
        self.limit = limit

    def set_position(self, pos):
        if pos[0] > self.limit:
            self.x = -pos[0] + self.limit
        else:
            self.target.rect.x = pos[0]
        self.target.rect.bottom = pos[1]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.start_pos = pos
        self.camera_delta = camera.x


class Background(Sprite):
    def __init__(self, x):
        super().__init__((x, 0), backgrounds_group, all_sprites)
        self.image = background_image
        self.rect = self.image.get_rect()
        self.rect.left = x


class Entity(Sprite):
    def __init__(self, pos):
        super().__init__(pos, player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.pos = list(pos)
        self.move_pos = list(pos)

        self.jump_faze = 0
        self.jump_speed = -200

        self.push_faze = 0
        self.in_pushing = False
        self.push_speed = 500
        self.push_dist = 80
        self.push_acc = self.push_speed ** 2 / (2 * self.push_dist) * -1

    def update(self, time, push=False):
        self.push_faze += time
        self.jump_faze += time
        if push:
            self.push_faze = 0
            self.in_pushing = True
            self.move_pos[0] = self.pos[0]
        if self.in_pushing:
            self.pos[0] = (self.move_pos[0] + self.push_speed * self.push_faze
                           + (self.push_acc * self.push_faze ** 2) / 2)
            if self.pos[0] - self.move_pos[0] >= self.push_dist - 1:
                self.in_pushing = False

        collider = pygame.sprite.spritecollideany(self, platforms_group)
        if collider:
            self.jump_faze = 0
            self.move_pos[1] = collider.rect.topleft[1]

        self.pos[1] = (self.move_pos[1] + self.jump_speed * self.jump_faze +
                       (GRAVITY * self.jump_faze ** 2) / 2)
        camera.set_position(self.pos)


class Platform(Sprite):
    def __init__(self, pos, width):
        super().__init__(pos, platforms_group, all_sprites)
        self.image = pygame.Surface((width, 50))
        pygame.draw.rect(self.image, "gray", (0, 0, width, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


all_sprites = pygame.sprite.Group()
backgrounds_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
platforms_group = pygame.sprite.Group()

player_image = load_image('player.png')
background_image = load_image("background.jpg")

camera = Camera()

back = Background(0)
player = Entity((50, 300))
Platform((10, 390), 200)
Platform((400, 390), 200)
Platform((900, 390), 800)
Platform((1800, 390), 800)

camera.set_target(player, 600)

timer = pygame.time.Clock()
time = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_group.update(time, True)

    screen.fill("black")
    if back.rect.right < WIDTH:
        back = Background(back.rect.right)

    backgrounds_group.draw(screen)
    platforms_group.draw(screen)
    player_group.draw(screen)

    camera.apply(platforms_group)
    camera.apply(backgrounds_group, 0.3)
    player_group.update(time)

    time = timer.tick() / 1000
    pygame.display.flip()