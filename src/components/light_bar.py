from typing import Callable

import pygame

from .. import pygame_gui as ui


class _SlideButton(ui.components.Base):
    def __init__(self, w: int, x: int, y: int):
        super().__init__(w, w, x, y)
        self.radius = w / 2

        color_theme = ui.color.LightColorTheme()
        self.color = ui.color.light(color_theme.OnPrimaryContainer, 4)

        self.normal_r = self.radius * 0.6
        self.hover_r = self.radius * 0.8
        self.pressed_r = self.radius * 0.5

        self.pressed = False
        self.smooth_r = ui.timer.TimedFloat(0.08, self.normal_r, ui.timer.INTERP_POLY2)
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

class LightBar(ui.components.Base):
    '''
    The brightness value ranges from -1 to 1, with steps
    of 0.1. Zero represents origional brightness.

    LightBar(w, h, x, y, on_change)
    * on_change(light) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_change: Callable[[float], None] = None
    ):
        super().__init__(w, h, x, y)
        self.on_change = ui.utils.getCallable(on_change)

        self.light = 0.0

        color_theme = ui.color.LightColorTheme()
        self.color0 = color_theme.PrimaryContainer
        self.color1 = ui.color.light(color_theme.OnPrimaryContainer, 4)
        self.light_icon = ui.utils.loadImage(
            'resources/icons/sun.png', h, h,
            smooth_scale=True
        )

        btn_w = int(h * 0.7)
        self.btn_left = h
        self.btn_right = w - h - 20 - btn_w
        self.button = _SlideButton(
            w=btn_w,
            x=(self.btn_left + self.btn_right) // 2,
            y=(h - btn_w) // 2
        )
        self.text_obj = ui.components.Label(
            h+10, h, w-h-10, 0, '0.0',
            font=pygame.font.SysFont('simsun', 20)
        )

        self.addChild(self.button)
        self.addChild(self.text_obj)

    def onLeftPress(self, x: int, y: int):
        if self.button.pressed:
            x -= self.button.w // 2 # map to button center
            if x < self.btn_left:
                self.button.x = self.btn_left
            elif x > self.btn_right:
                self.button.x = self.btn_right
            else:
                self.button.x = x
            rel_x = (self.button.x - self.btn_left) / (self.btn_right - self.btn_left)
            int_x = int(rel_x * 20 - 10) / 10
            if self.light != int_x:
                self.light = int_x
                self.on_change(self.light)
                self.text_obj.setText(str(self.light))
            self.redraw()

    def onResize(self, w, h, x, y):
        self.w = w
        self.h = h
        self.x = x
        self.y = y

        # button
        btn_w = int(h * 0.7)
        self.btn_left = h
        self.btn_right = w - h - 20 - btn_w
        self.button.kill()
        self.button = _SlideButton(
            w=btn_w,
            x=(self.btn_left + self.btn_right) // 2,
            y=(h - btn_w) // 2
        )
        self.addChild(self.button)

        # text
        self.text_obj.kill()
        self.text_obj = ui.components.Label(
            h+10, h, w-h-10, 0, str(self.light),
            font=pygame.font.SysFont('simsun', 20)
        )
        self.addChild(self.text_obj)

        # icons
        self.light_icon = ui.utils.loadImage(
            'resources/icons/sun.png', h, h,
            smooth_scale=True
        )

    def _drawProcess(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        start_x = self.h + 10
        mid_x = self.button.x + self.button.w // 2
        end_x = self.w - self.h - 20
        pygame.draw.line(
            surface,
            self.color1,
            (start_x + x_start, self.h // 2 + y_start),
            (mid_x + x_start, self.h // 2 + y_start),
            5
        )
        pygame.draw.line(
            surface,
            self.color0,
            (mid_x + x_start, self.h // 2 + y_start),
            (end_x + x_start, self.h // 2 + y_start),
            5
        )

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int):
        surface.blit(self.light_icon, (x_start, y_start))
        self._drawProcess(surface, x_start, y_start)

    def kill(self) -> None:
        self.button = None
        super().kill()