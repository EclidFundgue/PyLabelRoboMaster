import math
from typing import Callable, List, Tuple

import pygame
from pygame import Surface as pg_Surface

from ... import pygame_gui as ui
from ...pygame_gui import logger
from ...utils.dataproc import sortedPoints
from ...utils.geometry import in_polygon
from .canvas import CanvasComponent
from .keypoint import Keypoint


class Contour(CanvasComponent, ui.components.Selectable):
    '''
    Manage keypoints contour. Initialized by size (max keypoint number) and
    points (optional). Contour will only be close if `len(points) == size`.
    Keypoints is not child of Contour, Contour is only a helper to draw lines
    and calculate click range.

    Contour(size, points)

    Methods:
    * addKeypoint(keypoint) -> None
    '''
    def __init__(self,
            size: int,
            points: List[Keypoint] = None,
            on_click: Callable[[], None] = None,
            line_width: int = 1,
            line_color: Tuple[int] = (237, 71, 255),
            line_color_hover: Tuple[int] = (255, 171, 220),
            line_color_select: Tuple[int] = (59, 250, 81)):
        if points is None:
            points = []
        if size < 2:
            logger.error('size at least 2', ValueError, self)
        if size < len(points):
            logger.error(f'size: {size} is smaller than points: {len(points)}',
                    ValueError, self)

        self.size: int = size
        self.points: List[Keypoint] = points
        self.on_click: Callable[[], None] = ui.getCallable(on_click)
        self.line_width: int = line_width
        self.line_color: Tuple[int] = line_color
        self.line_color_hover: Tuple[int] = line_color_hover
        self.line_color_select: Tuple[int] = line_color_select

        rect = self._getBoundingBox(points)
        CanvasComponent.__init__(self, *rect)
        self.selected = False

        self.hover = False # different from active, decide by polygon

    def _getBoundingBox(self, pts: List[Keypoint]) -> Tuple[int]:
        ''' (w, h, x, y) '''

        if len(pts) == 0:
            return (0, 0, 0, 0)

        xs = [p._x + p._w // 2 for p in pts]
        ys = [p._y + p._h // 2 for p in pts]
        pw = pts[0]._w # point circle width
        ph = pts[0]._h # point circle height

        left = min(xs) - pw
        right = max(xs) + pw
        top = min(ys) - ph
        bottom = max(ys) + ph

        return (right - left, bottom - top, left, top)

    def _updateBoundingBox(self) -> None:
        rect = self._getBoundingBox(self.points)
        self.w, self.h, self.x, self.y = rect

    def addKeypoint(self, keypoint: Keypoint) -> None:
        if len(self.points) >= self.size:
            logger.warning(f'keypoint number already reach size: {self.size}', self)
            return

        self.points.append(keypoint)
        self._updateBoundingBox()

    def kill(self) -> None:
        self.points = None
        self.on_click = None
        super().kill()

    def update(self, events=None) -> None:
        super().update(events)
        self._updateBoundingBox()

    def onHover(self, x: int, y: int) -> None:
        polygon = [p.getDisplayCenter() for p in self.points]
        self.hover = in_polygon(polygon, (self.x + x, self.y + y))

    def onLeftClick(self, x: int, y: int) -> None:
        if self.hover:
            self.on_click()

    def onLeftRelease(self) -> None:
        self.hover = False

    def offHover(self) -> None:
        self.hover = False

    def _lineAvoidActivePoint(self,
            surface: pg_Surface,
            pt1: Keypoint,
            pt2: Keypoint,
            color: Tuple[int]) -> None:

        p1 = pt1.getDisplayCenter()
        p2 = pt2.getDisplayCenter()
        if not (pt1.active or pt2.active):
            pygame.draw.line(surface, color, p1, p2)
            return

        pt_size = pt1.getRect()[0] / 2

        vec = (p2[0] - p1[0], p2[1] - p1[1])
        l = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        if l < pt_size: # too short, no need to draw
            return
        vec = (vec[0] / l * pt_size, vec[1] / l * pt_size) # normalize

        if pt1.active:
            p1 = (int(p1[0] + vec[0]), int(p1[1] + vec[1]))
        if pt2.active:
            p2 = (int(p2[0] - vec[0]), int(p2[1] - vec[1]))

        pygame.draw.line(surface, color, p1, p2)

    def draw(self, surface: pg_Surface) -> None:
        # least 2 points can draw a contour
        if len(self.points) < 2:
            return

        if self.selected:
            color = self.line_color_select
        elif self.hover:
            color = self.line_color_hover
        else:
            color = self.line_color

        pts = [p.getDisplayCenter() for p in self.points]
        if len(pts) == self.size:
            pts = sortedPoints(pts)
        # only 4 points is a complete contour
        if len(self.points) != self.size:
            pygame.draw.lines(surface, color, False, pts)
        else:
            # do not cover active point
            for i in range(len(self.points)):
                pt1 = self.points[i]
                pt2 = self.points[(i + 1) % len(self.points)]
                self._lineAvoidActivePoint(surface, pt1, pt2, color)