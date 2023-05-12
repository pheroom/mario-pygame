from pygame import *
from config import *
import pyganim
import random

class Platform(sprite.Sprite):
    def __init__(self, x, y, img = None):
        sprite.Sprite.__init__(self)
        self.image = img or image.load("images/brick.png").convert_alpha()
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

class PlatformCoin(sprite.Sprite):
    def __init__(self, x, y, remove, img = None):
        sprite.Sprite.__init__(self)
        self.image = img or image.load("images/coin.png").convert_alpha()
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.remove = remove

    def die(self):
        self.remove(self)

class Coin(sprite.Sprite):
    def __init__(self, x, y, remove):
        sprite.Sprite.__init__(self)
        self.startX = x
        self.startY = y
        self.remove = remove
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load("images/coin1.png").convert_alpha()
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        boltAnim = []
        for anim in ANIMATION_COIN:
            boltAnim.append((anim, 0.2))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()
        self.yvel = -7

    def update(self):
        self.boltAnim.blit(self.image, (0, 0))
        self.rect.y += self.yvel
        if self.rect.y + 80 <= self.startY:
            self.yvel = -self.yvel
        if (self.startY < self.rect.y):
            self.remove(self)


class Amount(sprite.Sprite):
    def __init__(self, x, y, amount, remove):
        sprite.Sprite.__init__(self)
        self.startX = x
        self.startY = y
        self.remove = remove
        self.image = font.Font('./emulogic.ttf', 12).render(str(amount), False, '#ffffff')
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.yvel = -5

    def update(self):
        self.rect.y += self.yvel
        if self.rect.y + 80 <= self.startY:
            self.remove(self)

class ActPlatform(Platform):
    def __init__(self, x, y, strength, needAction, img = None):
        Platform.__init__(self, x, y, img)
        self.needAction = needAction
        self.strength = strength
        self.end = False

    def act(self):
        if self.end:
            return

        if self.strength > 0:
            self.strength -= 1
            self.needAction(self.rect.x, self.rect.y)
        if self.strength <= 0:
            self.image = image.load("./images/empty_coin_block.png").convert_alpha()
            self.end = True

class BlockTeleport(Platform):
    def __init__(self, x, y, goX, goY):
        Platform.__init__(self, x, y)
        self.goX = goX
        self.goY = goY
        boltAnim = []
        for anim in ANIMATION_BLOCKTELEPORT:
            boltAnim.append((anim, 0.3))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

    def update(self):
        self.image.fill(Color(PLATFORM_COLOR))
        self.boltAnim.blit(self.image, (0, 0))


class Princess(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        boltAnim = []
        self.image = Surface((HERO_WIDTH, HERO_HEIGHT))
        self.image.fill(Color(COLOR))
        self.image.set_colorkey(Color(COLOR))
        for anim in ANIMATION_PRINCESS:
            boltAnim.append((anim, 0.8))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

    def update(self):
        self.image.fill(Color(COLOR))
        self.boltAnim.blit(self.image, (0, 0))

class Flower(sprite.Sprite):
    def __init__(self, x, y, whenDead, removeDeepPlatform):
        sprite.Sprite.__init__(self)
        self.rect = Rect(x, y - PLATFORM_HEIGHT, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        boltAnim = []
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.set_colorkey(Color(COLOR))
        for anim in ANIMATION_FLOWER:
            boltAnim.append((anim, 0.1))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()
        self.removeDeepPlatform = removeDeepPlatform
        self.whenDead = whenDead
        self.id = random.random()

    def update(self):
        self.image.fill(Color(COLOR))
        self.boltAnim.blit(self.image, (0, 0))

    def die(self):
        self.removeDeepPlatform(self)
        self.whenDead(self)