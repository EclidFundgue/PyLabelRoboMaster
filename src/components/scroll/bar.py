from typing import Callable, Tuple

import pygame
from pygame import Surface as pg_Surface

from ...pygame_gui import BaseComponent, Surface, getCallable


class _ScrollButton(BaseComponent):
    '''
    Inner class of ScrollBar. Generate default scroll button image
    by input size.

    ScrollButton(w, x, y)
    '''
    def __init__(self, w: int, x: int, y: int):
        h = w * 3
        super().__init__(w, h, x, y)

        self.image = _ScrollButton._generateDefaultImage(
            w, h, (17, 153, 158), (48, 227, 202)
        )
        self.active_image = _ScrollButton._generateDefaultImage(
            w, h, (48, 227, 202), (228, 249, 245)
        )

        self.pressed = False

    @staticmethod
    def _generateDefaultImage(
            w: int, h: int,
            outer_color: Tuple[int, int, int],
            inner_color: Tuple[int, int, int]):
        img = pg_Surface((w, h))
        pad = w // 3
        pygame.draw.rect(img, outer_color, pygame.Rect(0, 0, w, h))
        pygame.draw.rect(img, inner_color, pygame.Rect(pad, pad, w - 2 * pad, h - 2 * pad))
        return img

    def draw(self, surface: pg_Surface) -> None:
        if self.active or self.pressed:
            surface.blit(self.active_image, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))

class ScrollBar(Surface):
    '''
    Verticle scroll bar, usually in right side of scroll box.

    It is a little difficult to manage the size. There are two types
    of size: [Display] and [Detect]. [Display] describes where <rail>
    and <button> are shown on screen. [Detect] is wider, to easily
    drag <button> up and down.

    ScrollBar(w, h, x, y, on_drag, padding) [Display]
    * on_drag(r) -> None

    Methods:
    * setRail(rail) -> None
    * setButton(btn) -> None
    * setRelative(r) -> None
    * getRelative() -> float
    '''
    def __init__(self, w: int, h: int, x: int, y: int,
                 on_drag: Callable[[float], None] = None,
                 padding: int = 20):
        self.padding = padding

        self.on_drag: Callable[[float], None] = getCallable(on_drag)

        super().__init__(
            w + 2 * self.padding,
            h + 2 * self.padding,
            x - self.padding,
            y - self.padding
        )

        self.rail = Surface(w, h, self.padding, self.padding)
        self.button = _ScrollButton(w, self.padding, self.padding)

        self.rail.setBackgroundColor((228, 249, 245))

        self.addChild(self.rail)
        self.addChild(self.button)

    def _dragButton(self, dy: int):
        y = self.button.y + dy
        if y < self.padding:
            y = self.padding
        if y + self.button.h > self.h - self.padding:
            y = self.h - self.padding - self.button.h

        if y != self.button.y:
            self.button.y = y
            self.on_drag(self.getRelative())

    def setRail(self, rail: BaseComponent) -> None:
        ''' Customize rail style. '''
        self.rail.kill()
        self.removeDead()

        rail.x = self.padding
        rail.y = self.padding
        self.rail = rail
        self.addChild(self.rail)

    def setButton(self, btn: BaseComponent) -> None:
        ''' Customize button style. '''
        self.button.kill()
        self.removeDead()

        btn.x = self.padding
        btn.y = self.padding
        self.button = btn
        self.addChild(self.button)

    def setRelative(self, r: float) -> None:
        ''' 0 <= r <= 1, relative distace from top '''
        if r < 0:
            r = 0
        if r > 1:
            r = 1
        bar_length = self.h - self.button.h - 2 * self.padding
        dis_to_top = r * bar_length
        self.button.y = self.padding + dis_to_top

    def getRelative(self) -> float:
        ''' return float number between [0, 1] '''
        bar_length = self.h - self.button.h - 2 * self.padding
        dis_to_top = self.button.y - self.padding
        return dis_to_top / bar_length

    def kill(self) -> None:
        self.rail = None
        self.button = None
        self.on_drag = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        if self.button.active:
            self.button.pressed = True

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if self.button.pressed and vy != 0:
            self._dragButton(vy)

    def onLeftRelease(self) -> None:
        self.button.pressed = False

    def offHover(self) -> None:
        self.button.pressed = False