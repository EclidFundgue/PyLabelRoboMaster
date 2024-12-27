import math
from typing import List, Tuple

from .. import logger, timer
from .base import Base
from .containers import RectContainer


class CanvasComponent(Base):
    '''Methods:
    * setCanvasView(scale, view_x, view_y) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int, fix_size: bool = False):
        super().__init__(w, h, x, y)
        self._children: List[CanvasComponent]

        # original size and position
        self._w = w
        self._h = h
        self._x = x
        self._y = y

        self.scale = 1.0
        # view start position
        self.view_x = 0
        self.view_y = 0
        self.fix_size = fix_size

    def setCanvasView(self, scale: float, view_x: float, view_y: float) -> None:
        self.scale = scale
        self.view_x = view_x
        self.view_y = view_y

        if self.fix_size:
            self.w = self._w
            self.h = self._h
        else:
            self.w = int(self._w * scale)
            self.h = int(self._h * scale)

        self.x = int(self._x * scale - view_x)
        self.y = int(self._y * scale - view_y)

        for ch in self._children:
            ch.setCanvasView(scale, 0, 0)

    def addChild(self, child: 'CanvasComponent') -> None:
        if not isinstance(child, CanvasComponent):
            logger.error("Child must be CanvasComponent.", ValueError, self)
            return
        child.setCanvasView(self.scale, 0, 0)
        child.redraw()
        super().addChild(child)

class Canvas(RectContainer):
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)
        self._children: List[CanvasComponent]
        self.interactive_when_active = True

        self.smooth_timer = timer.ProgressTimer(0.1, timer.INTERP_POLYN1)

        self.scale_before = 1.0
        self.scale_dst = 1.0

        self.view_before = (0, 0)
        self.view_dst = (0, 0)

        self._updateView(self.scale_dst, self.view_dst, False)

    def _updateView(self, scale: float, view: Tuple[float, float], redraw: bool = False) -> None:
        for ch in self._children:
            ch.setCanvasView(scale, *view)
        if redraw:
            self.redraw()

    def _setMouseWheel(self, x: int, y: int, v: int) -> None:
        rate = math.exp(v * 0.2)
        self.scale_before = self.scale_dst
        self.view_before = self.view_dst

        self.scale_dst *= rate
        view_x, view_y = self.view_dst
        self.view_dst = (
            rate * (view_x + x) - x,
            rate * (view_y + y) - y
        )
        self._updateView(self.scale_before, self.view_before, True)
        self.smooth_timer.reset()

    def onRightDrag(self, vx: int, vy: int) -> None:
        if vx == 0 and vy == 0:
            return
        self.view_dst = (self.view_dst[0] - vx, self.view_dst[1] - vy)

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.active and wheel != 0:
            self._setMouseWheel(x, y, wheel)

        if not self.smooth_timer.isFinished():
            p = self.smooth_timer.getCurrentValue()
            scale = self.scale_before * (1 - p) + self.scale_dst * p
            view = (
                self.view_before[0] * (1 - p) + self.view_dst[0] * p,
                self.view_before[1] * (1 - p) + self.view_dst[1] * p
            )
            self._updateView(scale, view, True)
        elif self.scale_before != self.scale_dst or self.view_before != self.view_dst:
            self.scale_before = self.scale_dst
            self.view_before = self.view_dst
            self._updateView(self.scale_dst, self.view_dst, True)

    def addChild(self, child: CanvasComponent) -> None:
        if not isinstance(child, CanvasComponent):
            logger.error("Child must be CanvasComponent.", ValueError, self)
            return
        child.setCanvasView(self.scale_dst, *self.view_dst)
        super().addChild(child)