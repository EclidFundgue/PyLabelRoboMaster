import math
from typing import List, Tuple

from ...pygame_gui import BaseComponent, Surface, f_error


class CanvasComponent(BaseComponent):
    '''
    Special component responsibe for drawing in canvas.
    You can override `getDisplayPos`, `getDisplaySize`,
    `getScaleByWidth`, `getScaleByHeight` to adjust size
    and position of canvas.

    CanvasComponent(w, h, x, y)

    Methods:
    * getDisplayPos(scale) -> Tuple[float, float]
    * getDisplaySize(scale) -> Tuple[float, float]
    * getScaleByWidth(width) -> float
    * getScaleByHeight(height) -> float
    * onCanvasViewChanged(scale, view_x, view_y) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)
        self._w = w
        self._h = h
        self._x = x
        self._y = y

        self.scale = 1.0
        # view start position
        self.view_x = 0
        self.view_y = 0

    @property
    def w(self) -> int: return int(self.getDisplaySize()[0])
    @property
    def h(self) -> int: return int(self.getDisplaySize()[1])
    @property
    def x(self) -> int: return int(self.getDisplayPos()[0])
    @property
    def y(self) -> int: return int(self.getDisplayPos()[1])
    @w.setter
    def w(self, value: int) -> None: self._w = value
    @h.setter
    def h(self, value: int) -> None: self._h = value
    @x.setter
    def x(self, value: int) -> None: self._x = value
    @y.setter
    def y(self, value: int) -> None: self._y = value

    def getDisplayPos(self,
            scale: float = None,
            view_x: float = None,
            view_y: float = None) -> Tuple[float, float]:
        scale = scale or self.scale
        view_x = view_x or self.view_x
        view_y = view_y or self.view_y
        return (self._x * scale - view_x, self._y * scale - view_y)

    def getDisplaySize(self, scale: float = None) -> Tuple[float, float]:
        scale = scale or self.scale
        return (self._w * scale, self._h * scale)

    def getScaleByWidth(self, width: int) -> float:
        ''' Help componet to adjust size to fit canvas. '''
        return width / self._w

    def getScaleByHeight(self, height: int) -> float:
        ''' Help componet to adjust size to fit canvas. '''
        return height / self._h

    def onCanvasViewChanged(self, scale: float, view_x: float, view_y: float) -> None:
        self.scale = scale
        self.view_x = view_x
        self.view_y = view_y

class Canvas(Surface):
    '''
    Canvas(
        w, h, x, y,
        main_component,
        default_align,
        margin_x,
        margin_y,
        smooth_factor
    )

    Methods:
    * alignCenter() -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            main_component: CanvasComponent = None,
            default_align: bool = True,
            margin_x: int = 0,
            margin_y: int = 0,
            smooth_factor: float = 0.6):
        super().__init__(w, h, x, y)
        self.child_components: List[CanvasComponent]

        self.main_component = main_component
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.smooth_factor = smooth_factor

        self.scale_current = 1.0
        self.scale_dst = 1.0
        self.view_current = (0, 0)
        self.view_dst = (0, 0)

        if default_align:
            self.alignCenter()
        self.updateChildrenView()

    def _constraintedView(self,
            view_x: float,
            view_y: float,
            scale: float) -> Tuple[float, float]:
        if self.main_component is None:
            return (view_x, view_y)

        main_w, main_h = self.main_component.getDisplaySize(scale)
        main_x, main_y = self.main_component.getDisplayPos(scale, view_x, view_y)
        main_xr = main_x + main_w
        main_yr = main_y + main_h

        if main_w + 2 * self.margin_x < self.w:
            view_x += (main_w - self.w) / 2.0 + main_x
        else:
            if main_x > self.margin_x:
                view_x += main_x - self.margin_x
            if main_xr < self.w - self.margin_x:
                view_x += main_xr - (self.w - self.margin_x)
        if main_h + 2 * self.margin_y < self.h:
            view_y += (main_h - self.h) / 2.0 + main_y
        else:
            if main_y > self.margin_y:
                view_y += main_y - self.margin_y
            if main_yr < self.h - self.margin_y:
                view_y += main_yr - (self.h - self.margin_y)

        return (view_x, view_y)

    def alignCenter(self) -> None:
        if self.main_component is None:
            return

        self.scale_dst = min(
            self.main_component.getScaleByWidth(self.w),
            self.main_component.getScaleByHeight(self.h)
        )
        self.scale_current = self.scale_dst
        main_w, main_h = self.main_component.getDisplaySize(self.scale_dst)
        main_x, main_y = self.main_component.getDisplayPos(self.scale_dst)

        view_x = (main_w - self.w) / 2.0 + main_x + self.main_component.view_x
        view_y = (main_h - self.h) / 2.0 + main_y + self.main_component.view_y
        self.view_dst = (view_x, view_y)
        self.view_current = self.view_dst
        self.updateChildrenView()

    def onMouseWheel(self, x: int, y: int, v: int) -> None:
        rate = math.exp(v * 0.2)
        view_x, view_y = self.view_dst

        self.scale_dst *= rate
        self.view_dst = self._constraintedView(
            rate * (view_x + x) - x,
            rate * (view_y + y) - y,
            self.scale_dst
        )
        self.updateChildrenView()

    def onRightDrag(self, vx: int, vy: int) -> None:
        if vx == 0 and vy == 0:
            return

        view_x, view_y = self.view_dst
        self.view_dst = self._constraintedView(
            view_x - vx, view_y - vy, self.scale_dst
        )

        self.scale_current = self.scale_dst
        self.view_current = self.view_dst
        self.updateChildrenView()

    def update(self, events=None) -> None:
        super().update(events)

        if abs(self.scale_current - self.scale_dst) >= 1e-6:
            self.scale_current = self.smooth_factor * self.scale_current \
                               + (1 - self.smooth_factor) * self.scale_dst
            view_x, view_y = self.view_dst
            curr_x, curr_y = self.view_current
            self.view_current = (
                self.smooth_factor * curr_x + (1 - self.smooth_factor) * view_x,
                self.smooth_factor * curr_y + (1 - self.smooth_factor) * view_y
            )
            self.updateChildrenView()
        elif self.view_dst != self.view_current:
            self.scale_current = self.scale_dst
            self.view_current = self.view_dst
            self.updateChildrenView()

    def updateChildrenView(self) -> None:
        for ch in self.child_components:
            ch.onCanvasViewChanged(self.scale_current, *self.view_current)

    def addChild(self, child: CanvasComponent) -> None:
        if not isinstance(child, CanvasComponent):
            f_error("Child must be CanvasComponent.", ValueError, self)
            return
        child.onCanvasViewChanged(self.scale_current, *self.view_current)
        super().addChild(child)