from typing import Callable, List, Tuple

import pygame

from .. import logger, utils


class _RedrawNode:
    def __init__(self, component: 'Base', needs_redraw: bool):
        self.component: 'Base' = component
        self.needs_redraw: bool = needs_redraw
        self.needs_redraw_children: List['_RedrawNode'] = []

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'component={self.component}'

    def updateRecurse(self, redraw_chain: List['_RedrawNode']) -> None:
        # the last element in redraw_chain is the current node
        if redraw_chain.pop().needs_redraw:
            self.needs_redraw = True

        if len(redraw_chain) == 0:
            return

        child_redraw_node = redraw_chain[-1]
        if not child_redraw_node in self.needs_redraw_children:
            self.needs_redraw_children.append(child_redraw_node)
        child_redraw_node.updateRecurse(redraw_chain)

    def drawRecurse(self, surface: pygame.Surface) -> None:
        if self.needs_redraw:
            self.component.draw(surface)
            self.needs_redraw = False

        for child in self.needs_redraw_children:
            w, h, x, y = utils.clipRect(child.component.getRect(), surface)
            subsurface = surface.subsurface(pygame.Rect(x, y, w, h))
            child.drawRecurse(subsurface)

    def drawAll(self, surface: pygame.Surface) -> None:
        self.component.draw(surface)
        for ch_comp in self.component._children:
            child = _RedrawNode(ch_comp, True)
            w, h, x, y = utils.clipRect(child.component.getRect(), surface)
            subsurface = surface.subsurface(pygame.Rect(x, y, w, h))
            child.drawAll(subsurface)

class Base:
    # ---------- Special Methods ---------- #
    def __init__(self, w: int, h: int, x: int, y: int):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.layer: int = 0
        self.redraw_parent: bool = True
        self.alive: bool = True

        # internal variables
        self._parent: Base = None
        self._children: List[Base] = []

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
    def addKeydownEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        # self._listener.addEventListener(ET.KEY_DOWN, func, target, key, once)

    def addKeyPressEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        # self._listener.addEventListener(ET.KEY_PRESS, func, target, key, once)

    def addKeyReleaseEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        # self._listener.addEventListener(ET.KEY_UP, func, target, key, once)

    def addKeyCtrlEvent(self, key: int, func: Callable, target = None, once = False) -> None:
        if target is None:
            target = str(id(self))
        # self._listener.addEventListener(ET.KEY_CTRL, func, target, key, once)

    def removeEvents(self, target: str = None) -> None:
        if target is None:
            target = str(id(self))

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

    # ---------- Draw ---------- #
    def draw(self, surface: pygame.Surface) -> None:
        ''' Needs to be implemented by child class. '''

    # ---------- Draw ---------- #
    def _redrawRecurse(self, redraw_chain: List[_RedrawNode]) -> None:
        redraw_chain.append(_RedrawNode(self._parent, self.redraw_parent))
        self._parent._redrawRecurse(redraw_chain)

    def redraw(self) -> None:
        if self._parent is None:
            logger.error('No parent set for this component.', AttributeError, self)

        redraw_chain = [_RedrawNode(self, True)]
        self._redrawRecurse(redraw_chain)

    def draw(self, surface: pygame.Surface) -> None:
        ''' Needs to be implemented by child class. '''

    # ---------- Kill ---------- #