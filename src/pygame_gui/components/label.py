import pygame
from pygame import Surface

from .. import constants, logger
from .base import BaseComponent


class Label(BaseComponent):
    '''
    Label(w, h, x, y, text, font, color)

    Methods:
    * setText(text) -> None
    * setFont(font) -> None
    * setColor(color) -> None
    * setAlignment(align_x, align_y) -> None
    '''

    DEFAULT_FONT = None

    def __init__(self,
            w: int, h: int, x: int, y: int,
            text: str,
            font: pygame.font.Font = None,
            text_color: tuple = constants.DEFAULT_TEXT_COLOR
        ):
        super().__init__(w, h, x, y)

        # Initialize DEFAULT_FONT after pygame initialized.
        if Label.DEFAULT_FONT is None:
            Label.DEFAULT_FONT = pygame.font.SysFont(
                constants.DEFAULT_FONT_NAME,
                constants.DEFAULT_FONT_SIZE
            )

        self.text = text
        self.font = font if font is not None else Label.DEFAULT_FONT
        self.text_color = text_color

        # default alignment is left-top
        self.align_x = constants.ALIGN_LEFT
        self.align_y = constants.ALIGN_TOP
        self.padx = 0
        self.pady = 0

        self.text_surface = self.font.render(self.text, True, self.text_color)

    def _reloadSurface(self) -> None:
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.setAlignment(self.align_x, self.align_y) # update alignment

    def setText(self, text: str) -> None:
        self.text = text
        self._reloadSurface()

    def setFont(self, font: pygame.font.Font) -> None:
        self.font = font
        self._reloadSurface()

    def setColor(self, color: tuple) -> None:
        self.text_color = color
        self._reloadSurface()

    def setAlignment(self, align_x: int = None, align_y: int = None) -> None:
        if align_x is not None:
            self.align_x = align_x
            if align_x == constants.ALIGN_LEFT:
                self.padx = 0
            elif align_x == constants.ALIGN_CENTER:
                self.padx = (self.w - self.text_surface.get_width()) // 2
            elif align_x == constants.ALIGN_RIGHT:
                self.padx = self.w - self.text_surface.get_width()
            else:
                logger.error(f"Invalid align_x: {align_x}", ValueError, self)

        if align_y is not None:
            self.align_y = align_y
            if align_y == constants.ALIGN_TOP:
                self.pady = 0
            elif align_y == constants.ALIGN_CENTER:
                self.pady = (self.h - self.text_surface.get_height()) // 2
            elif align_y == constants.ALIGN_BOTTOM:
                self.pady = self.h - self.text_surface.get_height()
            else:
                logger.error(f"Invalid align_y: {align_y}", ValueError, self)

    def draw(self, surface: Surface) -> None:
        surface.blit(self.text_surface, (self.x + self.padx, self.y + self.pady))