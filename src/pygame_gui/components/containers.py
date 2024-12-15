import pygame

from .. import utils
from .base import Base


class Container(Base):
    '''Methods:
    * setBackgroundColor(color) -> None
    * alignHorizontalCenter(obj) -> None
    * alignVerticalCenter(obj) -> None
    * alignCenter(obj) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)
        self.backgournd_color = None

    def setBackgroundColor(self, color: tuple = None) -> None:
        '''None means transparent background.'''
        self.backgournd_color = color
        self.redraw_parent = color is None

    def alignHorizontalCenter(self, obj: Base) -> None:
        obj.x = (self.w - obj.w) // 2

    def alignVerticalCenter(self, obj: Base) -> None:
        obj.y = (self.h - obj.h) // 2

    def alignCenter(self, obj: Base) -> None:
        self.alignHorizontalCenter(obj)
        self.alignVerticalCenter(obj)

class RectContainer(Container):
    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.backgournd_color is not None:
            surface.fill(self.backgournd_color)

class RoundedRectContainer(Container):
    def __init__(self, w: int, h: int, x: int, y: int, radius: int):
        super().__init__(w, h, x, y)
        self.radius = radius

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.backgournd_color is not None:
            utils.drawRoundedRect(
                surface,
                self.backgournd_color,
                (0, 0, self.w, self.h),
                self.radius
            )