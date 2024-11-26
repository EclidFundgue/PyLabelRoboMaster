from pygame import Surface

from .. import draw
from .base import BaseComponent


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
        self.pg_surface = Surface((w, h)).convert_alpha()
        self.pg_surface.fill((0, 0, 0, 0))
        self.backgournd_color = (0, 0, 0, 0)

        super().__init__(w, h, x, y)

    def setBackgroundColor(self, color: tuple) -> None:
        self.backgournd_color = color

    def alignHorizontalCenter(self, obj: BaseComponent) -> None:
        obj.setX((self.w - obj.w) // 2)

    def alignVerticalCenter(self, obj: BaseComponent) -> None:
        obj.setY((self.h - obj.h) // 2)

    def alignCenter(self, obj: BaseComponent) -> None:
        self.alignHorizontalCenter(obj)
        self.alignVerticalCenter(obj)

    def setRect(self, w: int, h: int, x: int, y: int) -> None:
        super().setRect(w, h, x, y)
        if w != self.w or h != self.h:
            self.pg_surface = Surface((w, h)).convert_alpha()

    def draw(self, surface: Surface) -> None:
        self.pg_surface.fill(self.backgournd_color)
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)
        surface.blit(self.pg_surface, (self.x, self.y))

class RectContainer(Container):
    '''
    RectContainer(w, h, x, y)
    '''

class RoundedRectContainer(Container):
    '''
    RoundedRectContainer(w, h, x, y, radius)
    '''
    def __init__(self, w: int, h: int, x: int, y: int, radius: int):
        super().__init__(w, h, x, y)
        self.radius = radius

    def draw(self, surface: Surface) -> None:
        self.pg_surface.fill((0, 0, 0, 0))
        draw.rounded_rect(
            surface,
            self.backgournd_color,
            (self.x, self.y, self.w, self.h),
            self.radius
        )
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)
        surface.blit(self.pg_surface, (self.x, self.y))