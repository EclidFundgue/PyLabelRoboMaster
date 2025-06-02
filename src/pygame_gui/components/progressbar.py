from typing import Callable

import pygame

from .. import color, timer, utils
from .base import Base


class _SlideButton(Base):
    '''
    _SlideButton(w, x, y)
    '''
    def __init__(self, w: int, x: int, y: int):
        super().__init__(w, w, x, y)
        self.radius = w / 2

        color_theme = color.LightColorTheme()
        self.color = color.light(color_theme.OnPrimaryContainer, 4)

        self.normal_r = self.radius * 0.6
        self.hover_r = self.radius * 0.8
        self.pressed_r = self.radius * 0.5

        self.pressed = False
        self.smooth_r = timer.TimedFloat(0.08, self.normal_r, timer.INTERP_POLY2)
        self.current_r = self.smooth_r.getCurrentValue()

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.current_r != self.smooth_r.getCurrentValue():
            self.current_r = self.smooth_r.getCurrentValue()
            self.redraw()

    def onLeftClick(self, x: int, y: int):
        if self.active:
            self.pressed = True
            self.smooth_r.setValue(self.pressed_r)
            self.redraw()

    def onLeftRelease(self):
        if self.active:
            self.smooth_r.setValue(self.hover_r)
        else:
            self.smooth_r.setValue(self.normal_r)
        self.pressed = False

    def onMouseEnter(self):
        if not self.pressed:
            self.smooth_r.setValue(self.hover_r)

    def onMouseLeave(self):
        if not self.pressed:
            self.smooth_r.setValue(self.normal_r)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int):
        center = (self.radius + x_start,
                  self.radius + y_start)
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            center,
            self.radius
        )
        pygame.draw.circle(
            surface,
            self.color,
            center,
            self.current_r
        )

class ProgressBar(Base):
    '''
    ProgressBar(w, h, x, y, on_change)
    * on_change(value) -> None

    Methods:
    * get(value) -> float
    * set(value) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_change: Callable[[float], None] = None
    ):
        super().__init__(w, h, x, y)
        self.on_change = utils.getCallable(on_change)

        self.value = 0.0

        color_theme = color.LightColorTheme()
        self.color0 = color_theme.PrimaryContainer
        self.color1 = color.light(color_theme.OnPrimaryContainer, 4)

        self._initButton(w, h)

    def _initButton(self, w: int, h: int) -> None:
        btn_w = int(h * 0.7)
        self.left_border = 0
        self.right_border = w - btn_w
        self.button = _SlideButton(btn_w, 0, (h-btn_w)//2)
        self.addChild(self.button)

    def get(self) -> float:
        return self.value

    def set(self, value: float) -> None:
        if value < 0.0:
            value = 0.0
        if value > 1.0:
            value = 1.0
        self.value = value
        width = self.right_border - self.left_border
        self.button.x = value * width + self.left_border

    def onLeftPress(self, x: int, y: int):
        if not self.active:
            return

        # map to button center
        x -= self.button.w // 2

        if x < self.left_border:
            x = self.left_border
        elif x > self.right_border:
            x = self.right_border
        self.button.x = x

        width = self.right_border - self.left_border
        rel_x = (x - self.left_border) / width
        if self.value != rel_x:
            self.value = rel_x
            self.on_change(self.value)

        self.redraw()

    def onResize(self, w, h, x, y):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.button.kill()
        self._initButton(w, h)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int):
        line_w = 5
        x = [
            line_w + x_start,                             # left
            self.button.x + self.button.w // 2 + x_start, # mid
            self.w - line_w + x_start                     # right
        ]
        y = self.h // 2 + y_start
        pygame.draw.line(surface, self.color1, (x[0], y), (x[1], y), line_w)
        pygame.draw.line(surface, self.color0, (x[1], y), (x[2], y), line_w)

    def kill(self) -> None:
        self.on_change = None
        self.button = None
        super().kill()