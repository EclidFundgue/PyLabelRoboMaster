from typing import Callable, Tuple

import pygame

from .. import pygame_gui as ui


class Keypoint(ui.components.CanvasComponent):
    '''Its movement is not controlled by itself. We need
    to avoid dragging multiple keypoints at the same time.

    Keypoint(center, on_click)

    Methods:
    * setCenter(x, y) -> None
    * getCenter() -> Tuple[int, int]
    * move(vx, vy) -> None
    '''
    def __init__(self,
        center: Tuple[int, int] = (0, 0),
        on_click: Callable[['Keypoint'], None] = None
    ):
        super().__init__(24, 24, 0, 0, fix_size=True)
        self.interactive_when_active = True

        self.setCenter(*center)
        self.on_click = ui.utils.getCallable(on_click)

    def setCenter(self, x: int, y: int) -> None:
        self._x = x
        self._y = y
        self.setCanvasView(self.scale, self.view_x, self.view_y)

    def getCenter(self) -> Tuple[int, int]:
        return (self._x, self._y)

    def move(self, vx: int, vy: int) -> None:
        self._x += vx / self.scale
        self._y += vy / self.scale
        self.setCanvasView(self.scale, self.view_x, self.view_y)

    def setCanvasView(self, scale: float, view_x: float, view_y: float) -> None:
        super().setCanvasView(scale, view_x, view_y)
        self.x = int(self._x * scale - self.w // 2 - view_x)
        self.y = int(self._y * scale - self.h // 2 - view_y)

    def onLeftClick(self, x: int, y: int) -> None:
        self.on_click(self)

    def kill(self) -> None:
        self.on_click = None
        super().kill()

    def onMouseEnter(self) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.redraw()

    def onMouseLeave(self) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        center = (self.w // 2 + x_start, self.h // 2 + y_start)
        line_color = (229, 73, 59)

        if self.active:
            pygame.draw.circle(surface, (157, 226, 120), center, 2)
            pygame.draw.circle(surface, line_color, center, self.w // 2, 2)
        else:
            left = (center[0] - self.w // 2, center[1])
            top = (center[0], center[1] - self.h // 2)
            right = (center[0] + self.w // 2, center[1])
            button = (center[0], center[1] + self.h // 2)
            pygame.draw.line(surface, line_color, left, right)
            pygame.draw.line(surface, line_color, top, button)
            pygame.draw.circle(surface, (132, 34, 25), center, 2)