from typing import Callable, List, Tuple

import pygame

from .. import logger, utils
from .events import KeyboardEvent


class _RedrawNode:
    def __init__(self, component: 'Base', needs_redraw: bool):
        self.component: 'Base' = component
        self.needs_redraw: bool = needs_redraw
        self.needs_redraw_children: List['_RedrawNode'] = []

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'component={self.component}' \
               f'redraw={self.needs_redraw}>'

    def merge(self, other: '_RedrawNode') -> '_RedrawNode':
        if other.component is not self.component:
            logger.error(f'Cannot merge redraw nodes for different components', ValueError, self)

        if other.needs_redraw or self.needs_redraw:
            self.needs_redraw = True
            self.needs_redraw_children = []
            return

        if len(other.needs_redraw_children) == 0:
            logger.error('Leave node needs_redraw == False.', ValueError, self)
        elif len(other.needs_redraw_children) != 1:
            logger.error('Cannot merge redraw nodes with multiple children.', ValueError, self)

        child = other.needs_redraw_children[0]
        for my_child in self.needs_redraw_children:
            if my_child.component is child.component:
                my_child.merge(child)
                return

        self.needs_redraw_children.append(child)
        child.merge(child)

    def _drawChildNode(self, surface: pygame.Surface, child: '_RedrawNode') -> None:
        w, h, x, y = child.component.getRect()
        x += min(0, self.component.x)
        y += min(0, self.component.y)
        x_start = min(0, x)
        y_start = min(0, y)
        w, h, x, y = utils.clipRect((w, h, x, y), surface)
        subsurface = surface.subsurface(pygame.Rect(x, y, w, h))
        child.draw(subsurface, x_start, y_start)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if not self.component.alive:
            return

        if self.needs_redraw:
            self.component.draw(surface, x_start, y_start)
            for child in self.component._children:
                child_node = _RedrawNode(child, True)
                self._drawChildNode(surface, child_node)
            return

        for child in self.needs_redraw_children:
            self._drawChildNode(surface, child)

    def clear(self) -> None:
        self.needs_redraw = False
        self.needs_redraw_children = []

class Base:
    '''Methods:
    1. ----- Mouse Events -----
    * on [Left/Mid/Right] Click(x, y) -> None
    * on [Left/Mid/Right] Press(x, y) -> None
    * on [Left/Mid/Right] Drag(vx, vy) -> None
    * on [Left/Mid/Right] Release() -> None
    * onMouseEnter() -> None
    * onMouseLeave() -> None

    2. ----- Keyboard Events -----
    * addKeyDownEvent(key, func, target, once) -> None
    * addKeyPressEvent(key, func, target, once) -> None
    * addKeyUpEvent(key, func, target, once) -> None
    * addKeyCtrlEvent(key, func, target, once) -> None
    * removeEvents(target) -> None

    3. ----- Child Management -----
    * removeDeadChildren() -> None
    * addChild(child) -> None
    * removeChild(child) -> None
    * setChildren(children) -> None

    4. ----- Update -----
    * getRect() -> Tuple[int, int, int, int]
    * isHovered(x, y) -> bool
    * update(x, y, wheel) -> None

    5. ----- Draw -----
    * redraw() -> None
    * draw(surface) -> None

    6. ----- Kill -----
    * kill() -> None
    '''
    # ---------- Special Methods ---------- #
    def __init__(self, w: int, h: int, x: int, y: int):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.layer: int = 0
        self.redraw_parent: bool = True
        self.interactive_when_active: bool = False
        self.alive: bool = True
        self.active: bool = False

        # internal variables
        self._parent: Base = None
        self._children: List[Base] = []
        self._keyboard_events: List[KeyboardEvent] = []
        self._keyboard_events_once: List[KeyboardEvent] = []

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'whxy=({self.w},{self.h},{self.x},{self.y})>'

    # ---------- Mouse Events ---------- #
    def onLeftClick(self, x: int, y: int) -> None: ...
    def onMidClick(self, x: int, y: int) -> None: ...
    def onRightClick(self, x: int, y: int) -> None: ...

    def onLeftPress(self, x: int, y: int) -> None: ...
    def onMidPress(self, x: int, y: int) -> None: ...
    def onRightPress(self, x: int, y: int) -> None: ...

    def onLeftDrag(self, vx: int, vy: int) -> None: ...
    def onMidDrag(self, vx: int, vy: int) -> None: ...
    def onRightDrag(self, vx: int, vy: int) -> None: ...

    def onLeftRelease(self) -> None: ...
    def onMidRelease(self) -> None: ...
    def onRightRelease(self) -> None: ...

    def onMouseEnter(self) -> None: ...
    def onMouseLeave(self) -> None: ...

    # ---------- Keyboard Events ---------- #
    def _addEvent(self, event: KeyboardEvent, once: bool) -> None:
        # Use copy to avoid modifying original list during iteration.
        if once:
            events = self._keyboard_events_once[:]
            events.append(event)
            self._keyboard_events_once = events
        else:
            events = self._keyboard_events[:]
            events.append(event)
            self._keyboard_events = events

    def addKeyDownEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        self._addEvent(KeyboardEvent(key, func, KeyboardEvent.DOWN, target), once)

    def addKeyPressEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        self._addEvent(KeyboardEvent(key, func, KeyboardEvent.PRESSED, target), once)

    def addKeyUpEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        self._addEvent(KeyboardEvent(key, func, KeyboardEvent.UP, target), once)

    def addKeyCtrlEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        self._addEvent(KeyboardEvent(key, func, KeyboardEvent.CTRL, target), once)

    def removeEvents(self, target: str = None) -> None:
        if target is None:
            target = str(id(self))
        self._keyboard_events = list(filter(lambda e: e.target != target, self._keyboard_events))

    # ---------- Child Management ---------- #
    def removeDeadChildren(self) -> None:
        self._children = list(filter(lambda c: c.alive, self._children))

    def addChild(self, child: 'Base') -> None:
        self.removeDeadChildren()
        if not child.alive:
            logger.warning(f'Operation not allowed on dead child {child}.', self)
            return
        if child in self._children:
            logger.warning(f'{child} is already added.', self)
            return
        child._parent = self
        self._children.append(child)
        self._children.sort(key=lambda x: x.layer)

    def removeChild(self, child: 'Base') -> None:
        self.removeDeadChildren()
        if not child.alive:
            logger.warning(f'Operation not allowed on dead child {child}.', self)
            return
        if child not in self._children:
            logger.warning(f'{child} is not in children list.', self)
            return
        child._parent = None
        self._children.remove(child)

    def setChildren(self, children: List['Base']) -> None:
        self.removeDeadChildren()
        # remove old children
        for child in self._children:
            child._parent = None
        self._children = []

        for child in children:
            self.addChild(child)
        self._children.sort(key=lambda x: x.layer)

    # ---------- Update ---------- #
    def getRect(self) -> Tuple[int]:
        ''' (w, h, x, y) '''
        return (self.w, self.h, self.x, self.y)
    
    def isHovered(self, x: int, y: int) -> bool:
        return 0 <= x <= self.w and 0 <= y <= self.h
    
    def update(self, x: int, y: int, wheel: int) -> None:
        ''' Needs to be implemented by child class. '''

    # ---------- Draw ---------- #
    def _submitDrawStack(self, redraw_stack: List['Base']) -> None:
        if self._parent is None:
            return
        redraw_stack.append(self._parent)
        self._parent._submitDrawStack(redraw_stack)

    def redraw(self) -> None:
        self._submitDrawStack([self])

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        ''' Needs to be implemented by child class. '''

    # ---------- Kill ---------- #
    def kill(self) -> None:
        self.removeDeadChildren()

        if not self.alive:
            logger.warning(f'{self} has already been killed.', self)

        for ch in self._children:
            ch.kill()
        self._children = None
        self._keyboard_events = None
        self._keyboard_events_once = None

        self.alive = False
        self.active = False

        if self._parent is not None:
            self._parent.removeDeadChildren()
            self._parent = None