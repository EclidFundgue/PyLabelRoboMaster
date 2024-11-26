from pygame import Surface

from .base import BaseComponent


class Root(BaseComponent):
    '''
    Root screen of all components.

    Root(surface)
    '''
    def __init__(self, surface: Surface):
        self.pg_surface = surface

        w, h = tuple(self.pg_surface.get_size())
        super().__init__(w, h, 0, 0, is_root=True)

        self.backgournd_color = (0, 0, 0)

    def setBackgroundColor(self, color) -> None:
        self.backgournd_color = color

    def draw(self) -> None:
        self.pg_surface.fill(self.backgournd_color)
        for ch in sorted(self.child_components, key=lambda x: x.layer):
            ch.draw(self.pg_surface)