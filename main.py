from pygame import *

from config import *
from menu import Menu
from level import Level

class MainScreen():
    def __init__(self, surf, switchScreen):
        self.switchScreen = switchScreen
        self.surface = surf
        self.menu = Menu()
        self.bg = transform.scale(image.load('images/bg1.jpeg'), (WIN_WIDTH, WIN_HEIGHT))
        self.menu.append_option('Hello world!', lambda: print('hihihi'))
        self.menu.append_option('Level Selection', lambda: self.switchScreen(lvlSelectionScreen))
        self.menu.append_option('Quit', lambda: self.switchScreen(None))

    def run(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_UP:
                    self.menu.switch(-1)
                elif e.key == K_DOWN:
                    self.menu.switch(1)
                elif e.key == K_SPACE:
                    self.menu.select()

        self.surface.blit(self.bg, (0,0))
        self.menu.draw(self.surface, 100, 100, 75)

class LevelSelectionScreen():
    def __init__(self, surf, switchScreen):
        self.switchScreen = switchScreen
        self.surface = surf
        self.menu = Menu()
        self.bg = transform.scale(image.load('images/bg2.png'), (WIN_WIDTH, WIN_HEIGHT))
        self.menu.append_option('1-1', lambda: self.switchScreen(lvl1Screen))
        self.menu.append_option('Back to menu', lambda: self.switchScreen(MainScreen))

    def run(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_UP:
                    self.menu.switch(-1)
                elif e.key == K_DOWN:
                    self.menu.switch(1)
                elif e.key == K_SPACE:
                    self.menu.select()

        self.surface.blit(self.bg, (0,0))
        self.menu.draw(self.surface, 700, 50, 75)

class Game():
    def __init__(self, surf):
        self.currentScreen = None
        self.surface = surf

    def switchScreen(self, Screen):
        self.currentScreen = Screen and Screen(self.surface, self.switchScreen)

    def run(self, events):
        if(self.currentScreen):
            self.currentScreen.run(events)

init()
size = (WIN_WIDTH, WIN_HEIGHT)
screen = display.set_mode(size)
clock = time.Clock()
game = Game(screen)
display.set_caption("Super Mario Boy")
marioIcon = image.load('./images/smallMushroom.png')
display.set_icon(marioIcon)

def lvl1Screen(screen, switchScreen):
    return Level(screen, switchScreen, lambda: game.switchScreen(lvlSelectionScreen), "levels/1-1.tmx", '1-1')

def lvlSelectionScreen(screen, switchScreen):
    return LevelSelectionScreen(screen, switchScreen)

game.switchScreen(MainScreen)
while game.currentScreen is not None:
    events = event.get()
    for e in events:
        if e.type == QUIT:
            game.switchScreen(None)
    game.run(events)
    display.update()
    clock.tick(60)