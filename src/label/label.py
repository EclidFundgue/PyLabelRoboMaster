from typing import List

import pygame

from .. import pygame_gui as ui
from ..utils import geometry
from .icon import Icon
from .keypoint import Keypoint


class Label:
    '''This class is used as a container. Attributes
    in this class can be accessed directly.

    Attributes\:
    * cls_id: int
    * points: List[Keypoint]
    * icon: Icon
    * alive: bool
    * active: bool
    * selected: bool

    Methods:

    ---------- setter ----------
    * setClass(cls_id) -> None
    * setSelectState(state) -> None
    * updateIconState() -> None
    * kill() -> None

    ---------- getter ----------
    * inHover(x, y) -> bool
    * drawContour(surface, x_start, y_start, closed) -> None
    * getLabelIO(img_size) -> LabelIO
    '''
    def __init__(self,
        cls_id: int = 0,
        points: List[Keypoint] = None,
        icon: Icon = None
    ):
        self.cls_id = cls_id
        self.points = [] if points is None else points
        self.icon: Icon = icon

        self.alive = True
        self.active = False
        self.selected = False

        self.line_color0 = (61, 142, 72)
        self.line_color1 = ui.color.light(self.line_color0, 5)

    # ---------- setter ----------
    def setClass(self, cls_id: int) -> None:
        self.cls_id = cls_id
        if self.icon is not None:
            self.icon.setClass(cls_id)

    def setSelectState(self, state: bool) -> None:
        self.selected = state
        self.updateIconState()

    def updateIconState(self) -> None:
        if self.selected:
            self.icon.label_state = self.icon.STATE_SELECTED
        elif self.active:
            self.icon.label_state = self.icon.STATE_ACTIVE
        else:
            self.icon.label_state = self.icon.STATE_NORMAL

    def kill(self) -> None:
        for p in self.points:
            p.kill()
        if self.icon is not None:
            self.icon.kill()
        self.points = None
        self.icon = None
        self.alive = False

    # ---------- getter ----------
    def inHover(self, x: int, y: int) -> bool:
        polygon = [(p.x + p.w // 2, p.y + p.h // 2) for p in self.points]
        in_polygon = geometry.in_polygon(polygon, (x, y))
        in_icon = self.icon is not None and self.icon.active
        return in_polygon or in_icon

    def drawContour(self,
        surface: pygame.Surface,
        x_start: int,
        y_start: int,
        closed: bool
    ) -> None:
        if self.selected:
            width = 3
            color = self.line_color1
        elif self.active:
            width = 1
            color = self.line_color1
        else:
            width = 1
            color = self.line_color0
        points = [(p.x + x_start + p.w // 2, p.y + y_start + p.h // 2) for p in self.points]
        pygame.draw.lines(surface, color, closed, points, width)