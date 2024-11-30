from typing import List

import pygame

from .. import logger
from .base import Base, _RedrawNode


class Root(Base):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        w, h = self.screen.get_size()
        super().__init__(w, h, 0, 0)

        self.redraw_tree: _RedrawNode = _RedrawNode(self, False)

    def _redrawRecurse(self, redraw_chain: List[_RedrawNode]) -> None:
        self.redraw_tree.needs_redraw = True
        self.redraw_tree.updateRecurse(redraw_chain)

    def redraw(self):
        logger.warning("Root can not be redrawn directly.", self)

    def draw(self, surface: pygame.Surface = None) -> None:
        # drawRecurse will call this method with surface
        # to avoid infinite recursion, only call drawRecurse with no surface
        if surface is not None:
            return
        if not self.redraw_tree.needs_redraw:
            return
        self.redraw_tree.drawRecurse(self.screen)
        pygame.display.flip()