from typing import overload

from pygame import Surface as pg_Surface

from .. import constants, draw, logger
from .base import BaseComponent

_KEY_COLOR = constants.CONTAINER_KEY_COLOR


class Container(BaseComponent):
    '''
    Provide a default transparent Container.

    Container(w, h, x, y)

    Methods:
    * clear() -> None
    * setBackgroundColor(color) -> None
    * alignHorizontalCenter(obj) -> None
    * alignVerticalCenter(obj) -> None
    * alignCenter(obj) -> None
    * draw(self, surface) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        self.pg_surface = pg_Surface((w, h))
        self.pg_surface.set_colorkey(_KEY_COLOR)
        self.backgournd_color = _KEY_COLOR

        super().__init__(w, h, x, y)

    def clear(self) -> None:
        ''' Clear pg_surface. '''
        self.pg_surface.fill(_KEY_COLOR)

    def setBackgroundColor(self, color: tuple = _KEY_COLOR) -> None:
        ''' Set KEY_COLOR to be transparent. '''
        self.backgournd_color = color

    def alignHorizontalCenter(self, obj: BaseComponent) -> None:
        ''' Align object horizontally center to self. '''
        obj.x = (self.w - obj.w) // 2

    def alignVerticalCenter(self, obj: BaseComponent) -> None:
        ''' Align object vertically center to self. '''
        obj.y = (self.h - obj.h) // 2

    def alignCenter(self, obj: BaseComponent) -> None:
        ''' Align object center to self. '''
        self.alignHorizontalCenter(obj)
        self.alignVerticalCenter(obj)

    def draw(self, surface: pg_Surface) -> None:
        ''' Draw children to self, then draw self to parent component. '''
        self.clear()
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)
        surface.blit(self.pg_surface, (self.x, self.y))

class RectContainer(Container):
    '''
    RectContainer(w, h, x, y)
    '''
    def clear(self) -> None:
        self.pg_surface.fill(self.backgournd_color)

class RoundedRectContainer(Container):
    '''
    RoundedRectContainer(w, h, x, y, radius)
    '''
    def __init__(self, w: int, h: int, x: int, y: int, radius: int):
        super().__init__(w, h, x, y)
        self.radius = radius

    def clear(self):
        super().clear()
        draw.rounded_rect(
            self.pg_surface,
            self.backgournd_color,
            (0, 0, self.w, self.h),
            self.radius
        )