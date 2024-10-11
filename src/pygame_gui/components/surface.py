from typing import overload

from pygame import Surface as pg_Surface

from .base import BaseComponent

# never use this color on other place
KEY_COLOR = (11, 45, 14)

class Surface(BaseComponent):
    '''
    Provide a default transparent Surface.

    Surface(pg_surface, x, y)\n
    Surface(w, h, x, y)

    Methods:
    * clear() -> None
    * setBackgroundColor(color) -> None
    * alignHorizontalCenter(obj) -> None
    * alignVerticalCenter(obj) -> None
    * alignCenter(obj) -> None
    * draw(self, surface) -> None
    '''
    @overload
    def __init__(self, pg_surface: pg_Surface, x: int, y: int, /): ...
    @overload
    def __init__(self, w: int, h: int, x: int, y: int, /): ...

    def __init__(self, *args):
        if len(args) != 3 and len(args) != 4:
            raise ValueError('Surface error: illegal arguments')
        if len(args) == 3 and not isinstance(args[0], pg_Surface):
            raise ValueError('Surface error: illegal arguments')

        # args = (surface, x, y)
        if len(args) == 3 and isinstance(args[0], pg_Surface):
            self.pg_surface = args[0]
            x = int(args[1])
            y = int(args[2])
        # args = (w, h, x, y)
        elif len(args) == 4:
            self.pg_surface = pg_Surface((args[0], args[1]))
            x = int(args[2])
            y = int(args[3])

        self.pg_surface.fill(KEY_COLOR)
        self.pg_surface.set_colorkey(KEY_COLOR)
        self.backgournd_color = KEY_COLOR

        w, h = tuple(self.pg_surface.get_size())
        super().__init__(w, h, x, y)
    
    def clear(self) -> None:
        ''' Clear pg_surface. '''
        self.pg_surface.fill(self.backgournd_color)

    def setBackgroundColor(self, color: tuple = KEY_COLOR) -> None:
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


class RootSurface(BaseComponent):
    '''
    Root screen of all components.

    RootSurface(pg_surface)
    '''
    def __init__(self, pg_surface: pg_Surface):
        self.pg_surface = pg_surface

        w, h = tuple(self.pg_surface.get_size())
        super().__init__(w, h, 0, 0, is_root=True)

        self.backgournd_color = (0, 0, 0)

    def setBackgroundColor(self, color: tuple = KEY_COLOR) -> None:
        ''' Set KEY_COLOR to be transparent. '''
        self.backgournd_color = color

    def draw(self) -> None:
        self.pg_surface.fill(self.backgournd_color)
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)