from pygame import *
from config import *
import pyganim
import blocks
import monsters

class Player(sprite.Sprite):
    def __init__(self, x, y, playAnimAmount, maxX, maxY, afterDead):
        sprite.Sprite.__init__(self)
        self.startX = x
        self.startY = y
        self.maxX = maxX
        self.maxY = maxY
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.rect = Rect(x, y, HERO_PHYSICAL_WIDTH, HERO_PHYSICAL_HEIGHT)

        self.immunityStart = 0
        self.immunityValue = 1000
        self.afterDead = afterDead
        self.startDead = -1
        self.dead = False
        self.lives = 3

        self.playAnimAmount = playAnimAmount
        self.points = 0
        self.coins = 0

        self.image = Surface((HERO_WIDTH, HERO_HEIGHT))
        self.image.fill(Color(COLOR))
        # self.indentImage = ((HERO_WIDTH - HERO_PHYSICAL_WIDTH)/2, (HERO_HEIGHT - HERO_PHYSICAL_HEIGHT)/2)
        self.indentImage = (0,0)
        self.image.set_colorkey(Color(COLOR))

        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()
        self.boltAnimRightSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimRightSuperSpeed.play()
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()
        self.boltAnimLeftSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimLeftSuperSpeed.play()
        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_STAY)
        self.boltAnimStay.play()
        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()
        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()
        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.play()

        self.winner = False

    def die(self):
        if self.startDead + 500 > time.get_ticks():
            return
        self.dead = True
        self.lives -= 1
        self.startDead = time.get_ticks()
        self.image = image.load("images/mario/d.png").convert_alpha()
        self.yvel = -JUMP_POWER

    def teleport(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY

    def addPoint(self, amount = 200):
        self.playAnimAmount(amount)
        self.points += amount

    def addLive(self, amount = 1):
        self.playAnimAmount(amount)
        self.lives += amount

    def addCoin(self):
        self.coins += 1

    def update(self, left, right, up, running, slowly, platforms, actPlatforms):
        if self.dead:
            if self.startDead + 1000 > time.get_ticks():
                self.rect.y += self.yvel
                self.yvel += GRAVITY
            else:
                self.dead = False
                self.immunityStart = time.get_ticks()
                self.immunityValue = DEAD_SCREEN_TIME + 1500
                self.teleport(self.startX, self.startY)
                self.image = Surface((HERO_WIDTH, HERO_HEIGHT))
                self.image.fill(Color(COLOR))
                self.image.set_colorkey(Color(COLOR))
                self.afterDead()
            return

        if up:
            if self.onGround:
                self.yvel = -JUMP_POWER
                if slowly:
                    self.yvel += JUMP_SLOW_POWER
                elif running and (left or right):
                    self.yvel -= JUMP_EXTRA_POWER
                self.image.fill(Color(COLOR))
                self.boltAnimJump.blit(self.image, self.indentImage)

        if left:
            self.xvel = -MOVE_SPEED
            self.image.fill(Color(COLOR))
            if running:
                self.xvel -= MOVE_EXTRA_SPEED
                if not up:
                    self.boltAnimLeftSuperSpeed.blit(self.image, self.indentImage)
            else:
                if not up:
                    self.boltAnimLeft.blit(self.image, self.indentImage)
            if up:
                self.boltAnimJumpLeft.blit(self.image, self.indentImage)

        if right:
            self.xvel = MOVE_SPEED
            self.image.fill(Color(COLOR))
            if running:
                self.xvel += MOVE_EXTRA_SPEED
                if not up:
                    self.boltAnimRightSuperSpeed.blit(self.image, self.indentImage)
            else:
                if not up:
                    self.boltAnimRight.blit(self.image, self.indentImage)
            if up:
                self.boltAnimJumpRight.blit(self.image, self.indentImage)

        if not (left or right):
            self.xvel = 0
            if not up:
                self.image.fill(Color(COLOR))
                self.boltAnimStay.blit(self.image, self.indentImage)

        if not self.onGround:
            self.yvel += GRAVITY

        if slowly and (left or right):
            self.xvel = MOVE_SLOW_SPEED * (-1 if left else 1)

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms, actPlatforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms, actPlatforms)

        if self.rect.x + PLATFORM_WIDTH < 0 or self.rect.x - PLATFORM_WIDTH > self.maxX or self.rect.y - PLATFORM_HEIGHT*5 > self.maxY:
            self.die()

    def collide(self, xvel, yvel, platforms,actPlatforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if isinstance(p,monsters.Monster) and not p.dead:
                    if self.immunityStart + self.immunityValue < time.get_ticks():
                        if p.rect.y - HERO_HEIGHT / 2 < self.rect.y:
                            self.die()
                        else:
                            self.addPoint()
                            p.die()
                elif isinstance(p, blocks.BlockTeleport):
                    self.teleport(p.goX, p.goY)
                elif isinstance(p, blocks.Princess):
                    if not self.winner:
                        self.addPoint(10000)
                        self.winner = True
                elif isinstance(p, blocks.Flower):
                    self.addLive(1)
                    p.die()
                elif isinstance(p, monsters.Mushroom):
                    self.addPoint(1000)
                    p.die()
                elif isinstance(p, blocks.PlatformCoin):
                    self.addCoin()
                    self.addPoint()
                    p.die()
                else:
                    if xvel > 0:
                        self.rect.right = p.rect.left

                    if xvel < 0:
                        self.rect.left = p.rect.right

                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0

                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0

                if isinstance(p, blocks.ActPlatform) and p.rect.y + HERO_HEIGHT == self.rect.y:
                    p.act()

