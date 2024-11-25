from typing import Callable, List, Tuple

import pygame
from pygame import Surface as pg_Surface

from ... import pygame_gui as ui
from ...process.label_io import LabelIO
from ...resources_loader import ImageLoader
from .canvas import CanvasComponent


class Keypoint(CanvasComponent, ui.components.Selectable):
    '''
    Display keypoint on screen.

    Keypoint(rel_x, rel_y, canvas_size, on_click, w, h)

    Methods:
    * getDisplayCenter() -> Tuple[int]
    * setCenterByCanvasPos(x: int, y: int) -> None
    * move(vx, vy) -> None
    '''
    def __init__(self,
            x: int, y: int,
            on_click: Callable[[], None] = None,
            w: int = 24, h: int = 24):
        self.on_click = ui.getCallable(on_click)

        loader = ImageLoader()
        self.image = self.loadImage(loader['label']['keypoint'], w, h)
        self.image_hover = self.loadImage(loader['label']['keypoint_hover'], w, h)

        CanvasComponent.__init__(self, w, h, x, y)
        self.selected = False

    def getDisplayPos(self, scale: float = None, view_x: float = None, view_y: float = None) -> Tuple[int]:
        scale = scale or self.scale
        view_x = view_x or self.view_x
        view_y = view_y or self.view_y
        return (
            int(self._x * scale - self.w // 2 - view_x),
            int(self._y * scale - self.h // 2 - view_y)
        )

    def getDisplaySize(self, scale: float = None) -> Tuple[int]:
        return (self._w, self._h)

    def getScaleByWidth(self, width: int) -> float:
        return 1.0

    def getScaleByHeight(self, height: int) -> float:
        return 1.0
    
    def getDisplayCenter(self) -> Tuple[int]:
        return (
            int(self._x * self.scale - self.view_x),
            int(self._y * self.scale - self.view_y)
        )

    def setCenterByCanvasPos(self, x: int, y: int) -> None:
        self._x = x / self.scale
        self._y = y / self.scale

    def move(self, vx: int, vy: int) -> None:
        self._x += vx / self.scale
        self._y += vy / self.scale

    def onLeftClick(self, x: int, y: int):
        self.on_click()

    def kill(self) -> None:
        self.on_click = None
        super().kill()

    def onHover(self, x: int, y: int) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def offHover(self) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, surface: pg_Surface) -> None:
        if self.active or self.selected:
            surface.blit(self.image_hover, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))

def getKeypointsFromLabelIO(
            label_io: LabelIO,
            image_size: Tuple[int, int]) -> List[Keypoint]:
        img_w, img_h = image_size
        pt_pos = [(pt[0] * img_w, pt[1] * img_h) for pt in label_io.kpts]
        return [Keypoint(pt[0], pt[1]) for pt in pt_pos]