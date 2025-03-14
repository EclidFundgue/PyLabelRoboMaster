from typing import Callable, Tuple, Union

import pygame

from .. import color as _color
from .. import timer, utils
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
        self.interactive_when_active = True

        self.on_press = utils.getCallable(on_press)

        # if press time larger than continue_press_thresh
        self.continue_press_thresh = continue_press
        self.continue_press_time = 0
        self.pressed = False

        self.cursor_change = cursor_change

    def resetState(self) -> None:
        self.pressed = False
        self.active = False
        self.continue_press_time = 0
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def kill(self) -> None:
        self.on_press = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        self.pressed = True
        self.on_press()
        self.redraw()

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
        self.redraw()

    def onMouseEnter(self):
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.redraw()

    def onMouseLeave(self):
        if self.pressed:
            self.pressed = False
            self.continue_press_time = 0
            self.redraw()
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class IconButton(_Button):
    '''
    A button triggers a callback function when clicked on.

    IconButton(
        w, h, x, y,
        icon,
        on_press,
        continue_press,
        cursor_change
    )
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            icon: Union[str, pygame.Surface],
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )

        self.normal_icon = utils.loadImage(
            icon,
            int(w * 0.9),
            int(h * 0.9),
            smooth_scale=True
        )
        self.hover_icon = utils.loadImage(
            icon, w, h, smooth_scale=True
        )
        self.pressed_icon = utils.loadImage(
            icon,
            int(w * 0.75),
            int(h * 0.75),
            smooth_scale=True
        )

    def onMouseLeave(self) -> None:
        super().onMouseLeave()
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.pressed:
            image = self.pressed_icon
        elif self.active:
            image = self.hover_icon
        else:
            image = self.normal_icon
        w, h = image.get_size()
        x_offset = (self.w - w) // 2
        y_offset = (self.h - h) // 2
        surface.blit(
            image,
            (x_start + x_offset,
             y_start + y_offset)
        )

class TextButton(_Button):
    '''Methods:
    * setFont(font)
    * setText(text)
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            text: str,
            font: pygame.font.Font = None,
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

        color_theme = _color.LightColorTheme()

        self.text_color = color_theme.PrimaryContainer
        self.text_color2 = color_theme.PrimaryContainer # pressed
        self.color = color_theme.OnPrimaryContainer
        self.color2 = _color.light(self.color, 3) # hovered
        self.color3 = _color.light(self.color, 8) # pressed

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

    def kill(self) -> None:
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

    def update(self, x, y, wheel) -> None:
        self._updateSmoothColor()
        self._updateTextColor()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        utils.drawRoundedRect(
            surface,
            color=self.current_color,
            rect=surface.get_rect(),
            radius=min(self.w, self.h) // 4
        )

class CloseButton(_Button):
    def __init__(self,
            w: int, h: int, x: int, y: int,
            color: Tuple[int, int, int],
            cross_color: Tuple[int, int, int] = (255, 255, 255),
            on_press: Callable = None,
            continue_press = -1,
            cursor_change: bool = False):
        super().__init__(
            w, h, x, y,
            on_press,
            continue_press,
            cursor_change
        )

        color_theme = _color.LightColorTheme()

        self.color = color
        self.color2 = color_theme.Error # hovered
        self.color3 = _color.light(color_theme.Error, 5) # pressed
        self.cross_color = cross_color

        self.smooth_color = timer.TimedColor(0.1, self.color)
        self.current_color = self.smooth_color.getCurrentColor()

    def resetState(self) -> None:
        super().resetState()
        self.smooth_color.setColor(self.color, False)
        self.current_color = self.smooth_color.getCurrentColor()

    def update(self, x, y, wheel) -> None:
        if self.pressed:
            self.smooth_color.setColor(self.color3)
        elif self.active:
            self.smooth_color.setColor(self.color2)
        else:
            self.smooth_color.setColor(self.color)

        if self.smooth_color.getCurrentColor() != self.current_color:
            self.current_color = self.smooth_color.getCurrentColor()
            self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.fill(self.current_color)
        cx = self.w // 2 + x_start
        cy = self.h // 2 + y_start
        r = min(self.w, self.h) // 6
        cross_color = (255, 255, 255) if self.active or self.pressed else self.cross_color
        pygame.draw.line(surface, cross_color, (cx - r, cy - r), (cx + r, cy + r), 2)
        pygame.draw.line(surface, cross_color, (cx - r, cy + r), (cx + r, cy - r), 2)