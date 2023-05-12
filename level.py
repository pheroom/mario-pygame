from pygame import *
import time as pytime
from config import *
from player import Player
from blocks import Platform, BlockTeleport, Princess, ActPlatform, Coin, Flower, Amount, PlatformCoin
from monsters import Monster, Mushroom
import pytmx

class Camera(object):
    def __init__(self, camera_func, width, height, floorY):
        self.camera_func = camera_func
        self.floorY = floorY
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect, self.floorY)


def camera_configure(camera, target_rect, y):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2
    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t, -y+WIN_HEIGHT-PLATFORM_HEIGHT)
    # t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)

def hexToColour( hash_colour ):
    red   = int( hash_colour[1:3], 16 )
    green = int( hash_colour[3:5], 16 )
    blue  = int( hash_colour[5:7], 16 )
    return ( red, green, blue )

LayerNamePlatforms = 'Platforms'
LayerNameActPlatforms = 'ActPlatforms'
LayerNameBackground = 'Background'
LayerNamePlayer = 'Player'
LayerNameMonsters  = 'Monsters'
LayerNamePrincess  = 'Princess'
LayerNameEntity  = 'Entity'

class Level:
    def __init__(self, surf, switchScreen, backToLastScreen, lvl, levelName):
        self.switchScreen = switchScreen
        self.surface = surf
        self.backToLastScreen = backToLastScreen

        self.bg = Surface((WIN_WIDTH, WIN_HEIGHT))
        self.bg.fill(Color(BG_COLOR_SKY))

        self.left = self.right = self.up = False
        self.running = False
        self.slowly = False

        self.entities = sprite.Group()
        self.platforms = []
        self.animatedEntities = sprite.Group()
        self.monsters = sprite.Group()
        self.backgrounds = sprite.Group()
        self.actPlatforms = []

        self.startTime = time.get_ticks()

        self.firstRenderMap(pytmx.load_pygame(lvl))
        self.ui = UI(self.surface, levelName)

        self.deadScreen = False
        self.startDead = 0

        self.winScreen = False
        self.startWin = 0
        self.canSkipWinScreen = False

    def animateCoin(self, x, y):
        def removeCoin(v):
            self.entities.remove(v)
            self.animatedEntities.remove(v)
            self.hero.addPoint()

        self.hero.addCoin()
        coin = Coin(x, y, removeCoin)
        self.entities.add(coin)
        self.animatedEntities.add(coin)

    def createMushroom(self, x, y):
        mr = Mushroom(x, y - PLATFORM_HEIGHT, 3, 0,
                      150, 0, self.removePlatform, self.removeMonster)
        self.entities.add(mr)
        self.platforms.append(mr)
        self.monsters.add(mr)

    def createFlower(self, x, y):
        mr = Flower(x, y, self.removePlatform, self.removeMonster)
        self.entities.add(mr)
        self.animatedEntities.add(mr)
        self.platforms.append(mr)

    def removeActPlatform(self, x, y):
        for pl in self.actPlatforms:
            if pl.rect.x == x and pl.rect.y == y:
                self.entities.remove(pl)
                self.platforms.remove(pl)
                self.actPlatforms.remove(pl)

    def removePlatform(self, obj):
        self.platforms.remove(obj)

    def removeMonster(self, obj):
        self.entities.remove(obj)
        self.monsters.remove(obj)

    def removePlatformAndEntity(self, obj):
        self.platforms.remove(obj)
        self.entities.remove(obj)

    def removeAnimatedEntity(self, obj):
        self.entities.remove(obj)
        self.animatedEntities.remove(obj)

    def playAnimAmount(self, amount):
        amount = Amount(self.hero.rect.x, self.hero.rect.y, amount, self.removeAnimatedEntity)
        self.entities.add(amount)
        self.animatedEntities.add(amount)

    def playDeadScreen(self):
        self.deadScreen = True
        self.startDead = time.get_ticks()

    def firstRenderMap(self, tmxMap):
        self.totalLevelWidth = tmxMap.tilewidth * tmxMap.width
        self.totalLevelHeight = tmxMap.tileheight * tmxMap.height
        self.floor = 0
        for layer in tmxMap.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_bitmap = tmxMap.get_tile_image_by_gid(gid)
                    if tile_bitmap and layer.name.rstrip() == LayerNamePlatforms:
                        pf = Platform(x * tmxMap.tilewidth, y * tmxMap.tileheight, img=tile_bitmap)
                        self.floor = max(self.floor, y * tmxMap.tileheight)
                        self.entities.add(pf)
                        self.platforms.append(pf)
                    if tile_bitmap and layer.name.rstrip() == LayerNameBackground:
                        pf = Platform(x * tmxMap.tilewidth, y * tmxMap.tileheight, img=tile_bitmap)
                        self.entities.add(pf)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name.rstrip() == LayerNamePlayer:
                    self.hero = Player(layer[0].x, layer[0].y, self.playAnimAmount, self.totalLevelWidth, self.totalLevelHeight, self.playDeadScreen)
                    self.entities.add(self.hero)
                if layer.name.rstrip() == LayerNamePrincess:
                    pr = Princess(layer[0].x, layer[0].y)
                    self.platforms.append(pr)
                    self.entities.add(pr)
                    self.animatedEntities.add(pr)
                elif layer.name.rstrip() == LayerNameEntity:
                    for entity in layer:
                        if entity.name == 'flower':
                            self.createFlower(entity.x, entity.y + PLATFORM_HEIGHT)
                        elif entity.name == 'coin':
                            cn = PlatformCoin(entity.x, entity.y, self.removePlatformAndEntity, entity.image)
                            self.platforms.append(cn)
                            self.entities.add(cn)
                elif layer.name.rstrip() == LayerNameActPlatforms:
                    for actPlatform in layer:
                        actObj = actPlatform.properties
                        if actObj.get('mushroom'):
                            pf = ActPlatform(actPlatform.x, actPlatform.y, 1, self.createMushroom,
                                             img=actPlatform.image)
                            self.entities.add(pf)
                            self.platforms.append(pf)
                            self.actPlatforms.append(pf)
                        elif actObj.get('break'):
                            pf = ActPlatform(actPlatform.x, actPlatform.y, actObj.get('break'), self.removeActPlatform,
                                             img=actPlatform.image)
                            self.entities.add(pf)
                            self.platforms.append(pf)
                            self.actPlatforms.append(pf)
                        elif actObj.get('coins'):
                            pf = ActPlatform(actPlatform.x, actPlatform.y, actObj.get('coins'), self.animateCoin,
                                             img=actPlatform.image)
                            self.entities.add(pf)
                            self.platforms.append(pf)
                            self.actPlatforms.append(pf)
                        elif actObj.get('flower'):
                            pf = ActPlatform(actPlatform.x, actPlatform.y, 1, self.createFlower,
                                             img=actPlatform.image)
                            self.entities.add(pf)
                            self.platforms.append(pf)
                            self.actPlatforms.append(pf)
                elif layer.name.rstrip() == LayerNameMonsters:
                    for monster in layer:
                        mn = Monster(monster.x, monster.y, monster.left, monster.maxLeft, self.removePlatform, self.removeMonster)
                        self.entities.add(mn)
                        self.platforms.append(mn)
                        self.monsters.add(mn)
        self.camera = Camera(camera_configure, self.totalLevelWidth, self.totalLevelHeight, self.floor)

    def run(self, events):
        if self.deadScreen:
            if self.canSkipWinScreen:
                self.backToLastScreen()
                return

            if self.startDead + DEAD_SCREEN_TIME > time.get_ticks():
                bg = Surface((WIN_WIDTH, WIN_HEIGHT))
                bg.fill(Color(BG_COLOR_DUNGEON))
                self.surface.blit(bg, (0, 0))
                deadImg = transform.scale(image.load('./images/mario/r5.png').convert_alpha(), (64, 64))
                deadLabel = font.Font('./emulogic.ttf', 45).render('*' + str(self.hero.lives), False, '#ffffff')
                self.surface.blit(deadImg, (WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 - 15))
                self.surface.blit(deadLabel, (WIN_WIDTH // 2 - 32, WIN_HEIGHT // 2 - 15))
                time_diff = time.get_ticks() - self.startTime
                self.ui.draw(self.hero.points, self.hero.coins, (time_diff - time_diff % 400) // 400)
            else:
                if self.hero.lives == 0:
                    self.backToLastScreen()
                self.deadScreen = False
            return

        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.backToLastScreen()
            if e.type == KEYDOWN and e.key == K_UP:
                self.up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                self.left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                self.right = True
            if e.type == KEYDOWN and e.key == K_LSHIFT:
                self.running = True
            if e.type == KEYDOWN and e.key == K_LCTRL:
                self.slowly = True
            if self.canSkipWinScreen and e.type == KEYDOWN and e.key == K_b:
                self.backToLastScreen()

            if e.type == KEYUP and e.key == K_UP:
                self.up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                self.right = False
            if e.type == KEYUP and e.key == K_LEFT:
                self.left = False
            if e.type == KEYUP and e.key == K_LSHIFT:
                self.running = False
            if e.type == KEYUP and e.key == K_LCTRL:
                self.slowly = False

        self.surface.blit(self.bg, (0, 0))
        self.monsters.update(self.platforms)
        self.animatedEntities.update()
        self.camera.update(self.hero)
        self.hero.update(self.left, self.right, self.up, self.running, self.slowly, self.platforms, self.actPlatforms)
        for e in self.entities:
            self.surface.blit(e.image, self.camera.apply(e))

        time_diff = time.get_ticks() - self.startTime
        self.ui.draw(self.hero.points, self.hero.coins, (time_diff - time_diff % 400) // 400)

        if self.hero.winner:
            if not self.winScreen:
                self.winScreen = True
                self.startWin = time.get_ticks()

            if self.startWin + 600 < time.get_ticks():
                label = font.Font('./emulogic.ttf', 30).render('THANK YOU MARIO!', False, '#ffffff')
                self.surface.blit(label, (WIN_WIDTH // 2 - label.get_width()//2, WIN_HEIGHT // 2 - 200))
            if self.startWin + 1200 < time.get_ticks():
                label = font.Font('./emulogic.ttf', 30).render('YOUR QUEST IS OVER.', False, '#ffffff')
                self.surface.blit(label, (WIN_WIDTH // 2 - label.get_width()//2, WIN_HEIGHT // 2 - 120))
            if self.startWin + 1700 < time.get_ticks():
                label = font.Font('./emulogic.ttf', 30).render('WE PRESENT YOU A NEW QUEST.', False, '#ffffff')
                self.surface.blit(label, (WIN_WIDTH // 2 - label.get_width()//2, WIN_HEIGHT // 2 - 70))
            if self.startWin + 2500 < time.get_ticks():
                label = font.Font('./emulogic.ttf', 30).render('PUSH BUTTON B', False, '#ffffff')
                self.surface.blit(label, (WIN_WIDTH // 2 - label.get_width()//2, WIN_HEIGHT // 2 + 10))
            if self.startWin + 3200 < time.get_ticks():
                label = font.Font('./emulogic.ttf', 30).render('TO SELECT A WORLD', False, '#ffffff')
                self.surface.blit(label, (WIN_WIDTH // 2 - label.get_width()//2, WIN_HEIGHT // 2 + 60))

            if self.startWin + WIN_SCREEN_TIME < time.get_ticks():
                self.canSkipWinScreen = True

class UI:
    def __init__(self, surf, world):
        self.surface = surf
        self.world = world
        self.font = font.Font('./emulogic.ttf', 25)
        self.imgCoin = image.load("images/coin.png").convert_alpha()
        self.memo = {}

    def renderFont(self, text):
        return self.font.render(str(text), False, '#ffffff')

    def util(self, num, cur = -1, pre = 1e6):
        if self.memo.get(num) != None:
            return self.memo.get(num)
        if pre == 0 and num == 0:
            return cur-1
        res = num % pre
        if res == num:
            return self.util(num, cur + 1, pre // 10)
        else:
            self.memo[num] = cur
            return cur

    def draw(self, point, coins, time):
        padding = 100
        smallPadding = 25
        x = 100
        pointLabel = self.renderFont('MARIO')
        pointValue = self.renderFont('0' * self.util(point) + str(point))
        self.surface.blit(pointLabel, (x, 20))
        self.surface.blit(pointValue, (x, 45))

        x += pointValue.get_width() + padding
        coins_value = self.renderFont('*' + str(coins))
        self.surface.blit(self.imgCoin, (x, 45))
        self.surface.blit(coins_value, (x + smallPadding, 45))

        x += self.imgCoin.get_width() + coins_value.get_width() + smallPadding + padding
        worldLabel = self.renderFont('WORLD')
        worldValue = self.renderFont(self.world)
        self.surface.blit(worldLabel, (x, 20))
        self.surface.blit(worldValue, (x + (worldLabel.get_size()[0] - worldValue.get_size()[0]) // 2, 45))

        x += worldLabel.get_width() + padding
        timeLabel = self.renderFont('TIME')
        timeValue = self.renderFont(time)
        self.surface.blit(timeLabel, (x, 20))
        self.surface.blit(timeValue, (x + timeLabel.get_size()[0] - timeValue.get_size()[0], 45))

if __name__ == '__main__':
    init()
    size = (WIN_WIDTH, WIN_HEIGHT)
    screen = display.set_mode(size)
    clock = time.Clock()
    lvl1 = Level(screen, lambda: print('switch'), lambda: print('back'), "levels/1-1.tmx")
    running = True
    while running:
        events = event.get()
        for e in events:
            if e.type == QUIT:
                quit()
        lvl1.run(events)
        display.update()
        # print(f"{clock.get_fps():2.0f} FPS")
        clock.tick(60)