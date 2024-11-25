from pygame import Surface as pg_Surface

from .. import constants as consts
from .base import BaseComponent


class Root(BaseComponent):
    '''
    Root screen of all components.

    Root(pg_surface)
    '''
    def __init__(self, pg_surface: pg_Surface):
        self.pg_surface = pg_surface

        w, h = tuple(self.pg_surface.get_size())
        super().__init__(w, h, 0, 0, is_root=True)

        self.backgournd_color = (0, 0, 0)

    def setBackgroundColor(self, color: tuple = consts.CONTAINER_KEY_COLOR) -> None:
        ''' Set CONTAINER_KEY_COLOR to be transparent. '''
        self.backgournd_color = color

    def draw(self) -> None:
        self.pg_surface.fill(self.backgournd_color)
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)