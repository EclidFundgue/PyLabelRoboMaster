from typing import Callable, Tuple

from pygame import Surface as pg_Surface

from ...pygame_gui import Selectable
from ...pygame_gui.decorators import getCallable
from ...resources_loader import ImageLoader
from .canvas import CanvasComponent, Surface
from .keypoint import Keypoint


class TypeIcon(CanvasComponent, Surface, Selectable):
    '''
    Display armor type beside label.

    TypeIcon(w, h, bind_point, type_index)

    Methods:
    * setColorType(idx) -> None
    * setArmorType(idx) -> None
    * setType(idx) -> None

    Theme -> Message:
    * _THEME_ICON_CLICK -> None
    '''
    def __init__(self,
            w: int, h: int,
            bind_point: Keypoint,
            type_index: int = 0,
            on_click: Callable[[], None] = None):
        self.padx = 15
        self.pady = 10
        x = bind_point.x + self.padx
        y = bind_point.y + self.pady
        Surface.__init__(self, w, h, x, y)
        CanvasComponent.__init__(self, w, h, x, y)
        self.selected = False

        self.bind_point = bind_point
        self.on_click = getCallable(on_click)

        loader = ImageLoader()['icon']['type']
        self.type_icons = [
            loader['sentry'],
            loader['1'],
            loader['2'],
            loader['3'],
            loader['4'],
            loader['5'],
            loader['outpost'],
            loader['base']
        ]
        self.color_backgrounds = [
            loader['bg_blue'],
            loader['bg_red']
        ]

        self.img_type = self.type_icons[type_index % 8]
        self.img_color = self.color_backgrounds[type_index // 8]

        self.bg_color = (148, 112, 32)
        self.bg_color_hover = (252, 224, 176)
        self.bg_color_select = (255, 246, 67)

    def setArmorType(self, idx: int) -> None:
        self.img_type = self.type_icons[idx]

    def setColorType(self, idx: int) -> None:
        self.img_color = self.color_backgrounds[idx]

    def setType(self, idx: int) -> None:
        self.setArmorType(idx % 8)
        self.setColorType(idx // 8)

    def getDisplayPos(self, scale: float = None, view_x: float = None, view_y: float = None) -> Tuple[int]:
        scale = scale or self.scale
        view_x = view_x or self.view_x
        view_y = view_y or self.view_y
        return (
            int(self._x * scale - view_x),
            int(self._y * scale - view_y)
        )

    def getDisplaySize(self, scale: float = None) -> Tuple[int]:
        return (self._w, self._h)

    def getScaleByWidth(self, width: int) -> float:
        return 1.0

    def getScaleByHeight(self, height: int) -> float:
        return 1.0

    def kill(self) -> None:
        self.bind_point = None
        self.on_click = None
        super().kill()

    def update(self, events=None) -> None:
        super().update(events)

        self.x = self.bind_point._x + self.padx / self.scale
        self.y = self.bind_point._y + self.pady / self.scale

    def onLeftClick(self, x: int, y: int):
        self.on_click()

    def draw(self, surface: pg_Surface):
        if self.selected:
            self.pg_surface.fill(self.bg_color_select)
        elif self.active:
            self.pg_surface.fill(self.bg_color_hover)
        else:
            self.pg_surface.fill(self.bg_color)

        self.pg_surface.blit(self.img_color, (0, 0))
        self.pg_surface.blit(self.img_type, (0, 0))
        surface.blit(self.pg_surface, (self.x, self.y))