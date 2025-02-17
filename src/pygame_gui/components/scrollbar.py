from typing import Callable, Tuple

import pygame

from .. import color, utils
from .base import Base
from .containers import RectContainer


def _generateDefaultButton(
    w: int, h: int,
    outer_color: Tuple[int, int, int],
    inner_color: Tuple[int, int, int]
) -> pygame.Surface:
    img = pygame.Surface((w, h))
    pad = w // 3
    pygame.draw.rect(img, outer_color, pygame.Rect(0, 0, w, h))
    pygame.draw.rect(img, inner_color, pygame.Rect(pad, pad, w - 2 * pad, h - 2 * pad))
    return img

class _ScrollButton(Base):
    '''
    Inner class of ScrollBar. Generate default scroll button image
    by input size.

    ScrollButton(w, x, y)
    '''
    def __init__(self, w: int, x: int, y: int):
        h = w * 2.7
        super().__init__(w, h, x, y)

        color_theme = color.LightColorTheme()
        self.image = _generateDefaultButton(
            w, h,
            color_theme.Secondary,
            color_theme.OnSecondary
        )
        self.active_image = _generateDefaultButton(
            w, h,
            color.light(color_theme.Secondary, 5),
            color.light(color_theme.OnSecondary, 5)
        )
        self.pressed = False

    def onMouseEnter(self):
        self.redraw()

    def onMouseLeave(self):
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.active or self.pressed:
            surface.blit(self.active_image, (x_start, y_start))
        else:
            surface.blit(self.image, (x_start, y_start))

class ScrollBar(RectContainer):
    '''
    Verticle scroll bar, usually in right side of scroll box.

    ScrollBar(w, h, x, y, on_drag)
    * on_drag(r) -> None

    Methods:
    * setRelative(r) -> None
    * getRelative() -> float
    '''
    def __init__(self, w: int, h: int, x: int, y: int, on_drag: Callable[[float], None] = None):
        super().__init__(w, h, x, y)

        self.on_drag: Callable[[float], None] = utils.getCallable(on_drag)
        self.padding = 200

        self.rail = RectContainer(w, h, 0, 0)
        self.button = _ScrollButton(w, 0, 0)

        color_theme = color.LightColorTheme()
        self.rail.setBackgroundColor(color_theme.Surface)

        self.addChild(self.rail)
        self.addChild(self.button)

    def _dragButton(self, dy: int):
        if dy == 0:
            return

        self.button.y += dy
        if self.button.y < 0:
            self.button.y = 0
        if self.button.y + self.button.h > self.h:
            self.button.y = self.h - self.button.h

        self.on_drag(self.getRelative())

    def setRelative(self, r: float) -> None:
        ''' 0 <= r <= 1, relative distace from top '''
        if r < 0:
            r = 0
        if r > 1:
            r = 1
        bar_length = self.h - self.button.h
        self.button.y = r * bar_length

    def getRelative(self) -> float:
        ''' return float number between [0, 1] '''
        bar_length = self.h - self.button.h
        return self.button.y / bar_length

    def kill(self) -> None:
        self.rail = None
        self.button = None
        self.on_drag = None
        super().kill()

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.button.pressed:
            if x < -self.padding or x > self.w + self.padding:
                self.button.pressed = False
            elif y < -self.padding or y > self.h + self.padding:
                self.button.pressed = False

    def onLeftClick(self, x: int, y: int) -> None:
        if self.button.active:
            self.button.pressed = True
            self.redraw()

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if self.button.pressed and vy != 0:
            self._dragButton(vy)
            self.redraw()

    def onLeftRelease(self) -> None:
        self.button.pressed = False
        self.redraw()