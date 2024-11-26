from typing import Callable, Union

import pygame
from pygame import Surface as pg_Surface

from .. import constants, time
from ..color import LightColorTheme
from ..decorators import getCallable
from .containers import BaseComponent, RoundedRectContainer
from .label import Label


class _BaseButton(BaseComponent):
    '''
    A base class for buttons, helps to manage the button's state.

    `continue_press` is the threshold time for continue pressing,
    -1 means no continue pressing, for example: 40 means continue
    pressing for 40 frames, then trigger the callback function each
    frame.

    _BaseButton(
        w, h, x, y,
        on_press,
        continue_press,
        cursor_change
    )
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = True):
        super().__init__(w, h, x, y)

        self.on_press = getCallable(on_press)

        # if press time larger than continue_press_thresh
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

class Button(_BaseButton):
    '''
    A button triggers a callback function when clicked on.

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
            w: int, h: int, x: int, y: int,
            image: Union[str, pg_Surface],
            pressed_image: Union[str, pg_Surface] = None,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )

        self.image = self.loadImage(image, w, h)
        if pressed_image is None:
            pressed_image = image
        self.pressed_image = self.loadImage(pressed_image, w, h)

    def draw(self, surface: pg_Surface) -> None:
        if self.pressed:
            surface.blit(self.pressed_image, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))

class TextButton(_BaseButton):
    '''
    A button with text label.

    TextButton(
        w, h, x, y,
        text,
        on_press,
        continue_press,
        cursor_change
    )

    Methods:
    * setFont(font)
    '''

    def __init__(self,
            w: int, h: int, x: int, y: int,
            text: str,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )

        color_theme = LightColorTheme()

        self.text_color = color_theme.PrimaryContainer
        self.pressed_text_color = color_theme.PrimaryContainer
        self.background_color = color_theme.OnPrimaryContainer
        self.hover_color = color_theme.light(self.background_color, 3)
        self.pressed_color = color_theme.light(self.background_color, 8)
        self.smooth_color = time.TimedColor(0.1, self.background_color)

        self.label = Label(
            w, h, 0, 0,
            text=text,
            text_color=self.text_color,
        )
        self.container = RoundedRectContainer(
            w, h, x, y,
            radius=min(w, h) // 4
        )

        self.label.setAlignment(
            align_x=constants.ALIGN_CENTER,
            align_y=constants.ALIGN_CENTER
        )

        self.container.addChild(self.label)
        self.addChild(self.container)

    def setFont(self, font: pygame.font.Font) -> None:
        self.label.setFont(font)

    def kill(self):
        self.label = None
        self.container = None
        super().kill()

    def _updateSmoothColor(self) -> None:
        if self.pressed:
            self.smooth_color.setColor(self.pressed_color)
        elif self.active:
            self.smooth_color.setColor(self.hover_color)
        else:
            self.smooth_color.setColor(self.background_color)

    def _updateTextColor(self) -> None:
        if self.pressed:
            self.label.setColor(self.pressed_text_color)
        else:
            self.label.setColor(self.text_color)

    def update(self, events=None) -> None:
        super().update(events)

        self._updateSmoothColor()
        self._updateTextColor()

        self.container.setBackgroundColor(self.smooth_color.getCurrentColor())

    def setRect(self, w: int, h: int, x: int, y: int) -> None:
        super().setRect(w, h, x, y)
        self.container.setRect(w, h, x, y)

    def draw(self, surface: pg_Surface) -> None:
        self.container.draw(surface)