from pygame import *

class Menu:
    def __init__(self):
        self._option_surfaces = []
        self._callbacks = []
        self._current_option_index = 0
        self.ARIAL_50 = font.SysFont('arial', 50)
        self.font = font.Font('./emulogic.ttf', 30)
        self.point = image.load('images/smallMushroom.png').convert_alpha()

    def append_option(self, option, callback):
        self._option_surfaces.append(self.font.render(option, True, '#ffffff'))
        self._callbacks.append(callback)

    def switch(self, direction):
        self._current_option_index = max(0, min(self._current_option_index + direction,
                                                len(self._option_surfaces) - 1))

    def select(self):
        self._callbacks[self._current_option_index]()

    def draw(self, surf, x, y, option_y_padding):
        for i, option in enumerate(self._option_surfaces):
            option_rect = option.get_rect()
            option_rect.topleft = (x, y + i * option_y_padding)
            if i == self._current_option_index:
                # draw.rect(surf, (0, 50, 0), option_rect)
                surf.blit(self.point, (option_rect.x - 40, option_rect.y + 5))
            surf.blit(option, option_rect)