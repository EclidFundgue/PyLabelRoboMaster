from typing import Callable, Tuple, Union

import pygame
from pygame import Surface as pg_Surface

from ..decorators import getCallable
from ..smooth import SmoothColor
from .surface import BaseComponent


class Button(BaseComponent):
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

class TextButton(Button):
    '''
    A button with text label.
    '''

    DEFAULT_FONT = None

    def __init__(self,
            w: int, h: int, x: int, y: int,
            text: str,
            font: Union[str, pygame.font.Font] = None,
            text_color: Tuple[int, int, int] = (0, 0, 0),
            background_color: Tuple[int, int, int] = (255, 255, 255),
            hover_color: Tuple[int, int, int] = (255, 255, 255),
            pressed_color: Tuple[int, int, int] = (255, 255, 255),
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        BaseComponent.__init__(self, w, h, x, y)

        # Initialize DEFAULT_FONT after pygame initialized.
        if TextButton.DEFAULT_FONT is None:
            TextButton.DEFAULT_FONT = pygame.font.SysFont('simsun', 16)

        self.text = text
        self.font = font if font is not None else TextButton.DEFAULT_FONT
        self.text_color = text_color
        self.text_image = self.font.render(text, True, text_color)
        self.background_color = background_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color

        self.smooth_color = SmoothColor(0.06, self.background_color)

        self.on_press = getCallable(on_press)

        # if press time larger than continue_press_thresh
        # notify obseervers every frame
        self.continue_press_thresh = continue_press
        self.continue_press_time = 0
        self.pressed = False

        self.cursor_change = cursor_change

    def update(self, events=None) -> None:
        super().update(events)

        if self.pressed:
            self.smooth_color.setColor(self.pressed_color)
        elif self.active:
            self.smooth_color.setColor(self.hover_color)
        else:
            self.smooth_color.setColor(self.background_color)

    def draw(self, surface: pg_Surface) -> None:
        w, h, x, y = self.getRect()
        pygame.draw.rect(surface, self.smooth_color.getCurrentColor(), (x, y, w, h))

        text_x = x + (w - self.text_image.get_width()) // 2
        text_y = y + (h - self.text_image.get_height()) // 2
        surface.blit(self.text_image, (text_x, text_y))