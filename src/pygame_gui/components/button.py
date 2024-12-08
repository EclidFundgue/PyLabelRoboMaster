from typing import Callable, Union

import pygame

from .. import timer, utils
from ..color import LightColorTheme
from .base import Base
from .label import Label


class _Button(Base):
    '''
    A base class for buttons, helps to manage the button's state.

    `continue_press` is the threshold time for continue pressing,
    -1 means no continue pressing, for example: 40 means continue
    pressing for 40 frames, then trigger the callback function each
    frame.

    _Button(
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

        self.on_press = utils.getCallable(on_press)

        # if press time larger than continue_press_thresh
        self.continue_press_thresh = continue_press
        self.continue_press_time = 0
        self.pressed = False

        self.cursor_change = cursor_change

    def kill(self) -> None:
        self.on_press = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        if not self.isHovered(x, y):
            return

        self.pressed = True
        self.on_press()

    def onLeftPress(self, x: int, y: int) -> None:
        if not self.isHovered(x, y):
            return

        if not self.pressed or self.continue_press_thresh < 0:
            return

        if self.continue_press_time < self.continue_press_thresh:
            self.continue_press_time += 1
        else:
            self.on_press()

    def onLeftRelease(self) -> None:
        self.pressed = False
        self.continue_press_time = 0

    def onMouseEnter(self):
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def onMouseLeave(self):
        self.pressed = False
        self.continue_press_time = 0
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class IconButton(_Button):
    '''
    A button triggers a callback function when clicked on.

    IconButton(
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
            image: Union[str, pygame.Surface],
            pressed_image: Union[str, pygame.Surface] = None,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )

        self.image = utils.loadImage(image, w, h)
        if pressed_image is None:
            pressed_image = image
        self.pressed_image = utils.loadImage(pressed_image, w, h)

    def draw(self, surface: pygame.Surface) -> None:
        if self.pressed:
            surface.blit(self.pressed_image, (0, 0))
        else:
            surface.blit(self.image, (0, 0))

class TextButton(_Button):
    '''Methods:
    * setFont(font)
    * setText(text)
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            text: str,
            font: pygame.font.Font,
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )
        self.redraw_parent = False

        color_theme = LightColorTheme()

        self.text_color = color_theme.PrimaryContainer
        self.text_color2 = color_theme.PrimaryContainer # pressed
        self.color = color_theme.OnPrimaryContainer
        self.color2 = color_theme.light(self.color, 3) # hovered
        self.color3 = color_theme.light(self.color, 8) # pressed

        self.smooth_color = timer.TimedColor(0.1, self.color)
        self.current_color = self.smooth_color.getCurrentColor()

        self.label = Label(
            w, h, 0, 0,
            text=text,
            font=font,
            color=self.text_color,
        )
        self.addChild(self.label)

    def setFont(self, font: pygame.font.Font) -> None:
        self.label.setFont(font)

    def setText(self, text: str) -> None:
        self.label.setText(text)

    def kill(self):
        self.label = None
        super().kill()

    def _updateSmoothColor(self) -> None:
        if self.pressed:
            self.smooth_color.setColor(self.color3)
        elif self.active:
            self.smooth_color.setColor(self.color2)
        else:
            self.smooth_color.setColor(self.color)

        if self.smooth_color.getCurrentColor() != self.current_color:
            self.current_color = self.smooth_color.getCurrentColor()
            self.redraw()

    def _updateTextColor(self) -> None:
        color = self.text_color2 if self.pressed else self.text_color
        if color != self.label.color:
            self.label.setColor(color)

    def update(self, x, y, wheel):
        self._updateSmoothColor()
        self._updateTextColor()

    def draw(self, surface: pygame.Surface) -> None:
        utils.drawRoundedRect(
            surface,
            color=self.current_color,
            rect=surface.get_rect(),
            radius=min(self.w, self.h) // 4
        )