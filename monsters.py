from pygame import *

import blocks
import pyganim
import random
from config import *

class Monster(sprite.Sprite):
    def __init__(self, x, y, left, maxLengthLeft, whenDead, removeSelf):
        sprite.Sprite.__init__(self)
        self.whenDead = whenDead
        self.image = Surface((MONSTER_WIDTH, MONSTER_HEIGHT))
        self.image.fill(Color(MONSTER_COLOR))
        self.image.set_colorkey(Color(MONSTER_COLOR))
        self.rect = Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.startX = x
        self.startY = y
        self.maxLengthLeft = maxLengthLeft
        self.xvel = left
        self.yvel = 0
        self.onGround = False
        self.dead = False
        boltAnim = []
        for anim in ANIMATION_MONSTERHORYSONTAL:
            boltAnim.append((anim, 0.2))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()
        self.removeSelf = removeSelf

    def update(self, platforms):
        if self.dead:
            if self.startDead + 1000 < time.get_ticks():
                self.image = Surface((0,0))
                self.removeSelf(self)
        else:
            self.image.fill(Color(MONSTER_COLOR))
            self.boltAnim.blit(self.image, (0, 0))

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

        if (abs(self.startX - self.rect.x) > self.maxLengthLeft):
            self.xvel = -self.xvel

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p and not isinstance(p, Mushroom) and (not self.dead or not isinstance(p, Monster)):
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = -self.xvel

                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = -self.xvel

                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0

                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.yvel = 0

    def die(self):
        self.image = transform.scale(self.image, (PLATFORM_WIDTH*1.5, PLATFORM_HEIGHT/2))
        self.rect.height -= PLATFORM_HEIGHT/2
        self.xvel = 0
        self.whenDead(self)
        self.startDead = time.get_ticks()
        self.dead = True

class Mushroom(sprite.Sprite):
    def __init__(self, x, y, left, up, maxLengthLeft, maxLengthUp, whenDead, removeSelf):
        sprite.Sprite.__init__(self)
        self.id = random.random()
        self.whenDead = whenDead
        self.image = image.load("images/mushroom.png").convert_alpha()
        self.rect = Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.startX = x
        self.startY = y
        self.maxLengthLeft = maxLengthLeft
        self.maxLengthUp = maxLengthUp
        self.xvel = left
        self.yvel = up
        self.onGround = False
        self.dead = False
        self.removeSelf = removeSelf

    def update(self, platforms):

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

        if (abs(self.startX - self.rect.x) > self.maxLengthLeft):
            self.xvel = -self.xvel

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p and not isinstance(p, Monster):
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.xvel = -self.xvel

                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.xvel = -self.xvel

                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0

                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.yvel = 0


    def die(self):
        self.removeSelf(self)
        self.whenDead(self)
