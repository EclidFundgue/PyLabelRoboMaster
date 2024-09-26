from typing import Callable, Union

import pygame
from pygame import Surface as pg_Surface

from ..decorators import getCallable
from .surface import Surface


class Button(Surface):
    '''
    Click, then call `on_press` funcion.

    Button(
        w, h, x, y,
        image,
        pressed_image,
        on_press,
        continue_press,
        cursor_change
    )
    '''
    def __init__(self,
            w: int, h: int,
            x: int, y: int,
            image: Union[str, pg_Surface],
            pressed_image: Union[str, pg_Surface] = None,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(w, h, x, y)

        self.image = self.loadImage(image, w, h)
        if pressed_image is None:
            pressed_image = image
        self.pressed_image = self.loadImage(pressed_image, w, h)

        self.on_press = getCallable(on_press)

        # if press time larger than continue_press_thresh
        # notify obseervers every frame
        self.continue_press_thresh = continue_press
        self.continue_press_time = 0
        self.pressed = False

        self.cursor_change = cursor_change

    def kill(self) -> None:
        self.on_press = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        self.pressed = True
        self.on_press()

    def onLeftPress(self, x: int, y: int) -> None:
        if not self.pressed or self.continue_press_thresh < 0:
            return

        if self.continue_press_time < self.continue_press_thresh:
            self.continue_press_time += 1
        else:
            self.on_press()

    def onLeftRelease(self) -> None:
        self.pressed = False
        self.continue_press_time = 0

    def onHover(self, x: int, y: int) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def offHover(self) -> None:
        self.pressed = False
        self.continue_press_time = 0
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, surface: pg_Surface) -> None:
        if self.pressed:
            surface.blit(self.pressed_image, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))