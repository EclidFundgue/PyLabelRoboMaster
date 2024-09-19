import os
from typing import Any, Callable, List, Tuple, Union

import pygame
from pygame import Surface as pg_Surface

from ..f___loger import damn as f_warning
from ..f___loger import fuck as f_error
from ..listener import EventType as ET
from ..listener import Listener, MouseEventArgs


class BaseComponent:
    '''
    Base of customized GUI components.

    BaseComponent(w, h, x, y, is_root)

    Methods:
    1. ---------- Succeed ----------
    * addChild(child) -> None
    * removeChild(child) -> None
    * kill() -> None

    2. ---------- Events ----------
    * on [Left/Mid/Right] Click(x, y) -> None
    * on [Left/Mid/Right] Press(x, y) -> None
    * on [Left/Mid/Right] Drag(vx, vy) -> None
    * on [Left/Mid/Right] Release() -> None
    * onHover(x, y) -> None
    * offHover() -> None
    * onMouseWheel(x, y, v) -> None
    * addKeydownEvent(key, func, target, once) -> None
    * addKeyPressEvent(key, func, target, once) -> None
    * addKeyReleaseEvent(key, func, target, once) -> None
    * addKeyCtrlEvent(key, func, target, once) -> None
    * removeEvents(target) -> None

    3. ---------- Display ----------
    * loadImage(img, w, h) -> Surface
    * getRect() -> Tuple[int]
    * draw(surface) -> None

    4. ---------- Observer ----------
    * addObserver(observer) -> None
    * removeObserver(observer) -> None
    * removeAllObservers() -> None
    * notify(theme, message) -> None
    * onReceive(sender_id, theme, message) -> None

    Internal Methods:
    * removeDead() -> None
    * update() -> None
    * update(events) -> None
    '''
    def __init__(self, w: int = 0, h: int = 0,
                 x: int = 0, y: int = 0, is_root: bool = False):
        self.child_components: List[BaseComponent] = []
        self.observers: List[BaseComponent] = []
        self._listener = Listener()
        self.active = False # True when mouse hover on the component
        self.alive = True # Component will be removed when not alive
        self.layer = 0 # Higher layer will cover lower layer when draw
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # One program should only have one root component. Such as root screen.
        # All components are children of root, then update in chain.
        self.is_root = is_root
        if is_root:
            self.active = True # root is always active
            self._initEventsByListener(self._listener)

        self._initMouseButtonEvents()

    def __repr__(self):
        return f'<{self.__class__.__name__} ' \
               f'whxy=({self.w},{self.h},{self.x},{self.y})>'

    def _initEventsByListener(self, _listener: Listener):
        mouse_button_types = [ET.MOUSE_DOWN, ET.MOUSE_UP, ET.MOUSE_PRESS]
        mouse_keys = [0, 1, 2] # left, mid, right
        for tp in mouse_button_types:
            for k in mouse_keys:
                _listener.addEventListener(tp,
                    self._mouseButtonEventsWrapper(tp, k), key_type=k)

        mouse_motion_types = [ET.MOUSE_WHEEL, ET.MOUSE_INFO_GET]
        for tp in mouse_motion_types:
            _listener.addEventListener(tp, self._mouseMotionEventsWrapper(tp))

    def _initMouseButtonEvents(self):
        pos = lambda x, y, vx, vy: (x, y)
        vel = lambda x, y, vx, vy: (vx, vy)
        none = lambda x, y, vx, vy: tuple()

        self.__mouse_button_functions = {
            ET.MOUSE_DOWN:  [[self.onLeftClick],
                             [self.onMidClick],
                             [self.onRightClick]],
            ET.MOUSE_UP:    [[self.onLeftRelease],
                             [self.onMidRelease],
                             [self.onRightRelease]],
            ET.MOUSE_PRESS: [[self.onLeftPress, self.onLeftDrag],
                             [self.onMidPress, self.onMidDrag],
                             [self.onRightPress, self.onRightDrag]]
        }
        self.__mouse_button_interface_parsers = {
            ET.MOUSE_DOWN:  [[pos],
                             [pos],
                             [pos]],
            ET.MOUSE_UP:    [[none],
                             [none],
                             [none]],
            ET.MOUSE_PRESS: [[pos, vel],
                             [pos, vel],
                             [pos, vel]]
        }


    # -------------------- Succeed Management -------------------- #
    def addChild(self, child) -> None:
        self.removeDead()

        if not child.alive:
            f_warning(f'Operation on dead component {child}.', self)
            return

        if child in self.child_components:
            f_warning(f'{child} is already added.')
            return

        self.child_components.append(child)

    def removeChild(self, child) -> None:
        self.removeDead()

        if not child.alive:
            f_warning(f'Operation on dead component {child}.', self)
            return

        if child not in self.child_components:
            f_warning(f'{child} is not child.', self)
            return

        self.child_components.remove(child)

    def removeDead(self) -> None:
        '''
        Remove dead components in child_components and observers.\n
        '''
        self.child_components = list(filter(lambda c: c.alive, self.child_components))
        self.observers = list(filter(lambda c: c.alive, self.observers))

    def kill(self) -> None:
        '''
        Kill the component. This will also kill all children of the component.\n
        Need to be maintained if has other references.
        '''
        self.removeDead()

        if not self.alive:
            f_warning(f'{self} has already been killed.', self)

        for child in self.child_components:
            child.kill()
        self.child_components = []

        self.removeAllObservers()
        self._listener = None
        self.active = False
        self.alive = False


    # -------------------- Events Handler -------------------- #
    # mouse (x, y) is relative position
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

    def onHover(self, x: int, y: int) -> None: ...
    def offHover(self) -> None: ... # call once when mouse leave

    def onMouseWheel(self, x: int, y: int, v: int) -> None: ... # v is speed of wheel

    # keyboard
    def addKeydownEvent(self, key: int, func: Callable, target = 'default', once = False) -> None:
        ''' Note: not supported key type: LCTRL, RCTRL. '''
        self._listener.addEventListener(ET.KEY_DOWN, func, target, key, once)

    def addKeyPressEvent(self, key: int, func: Callable, target = 'default', once = False) -> None:
        self._listener.addEventListener(ET.KEY_PRESS, func, target, key, once)

    def addKeyReleaseEvent(self, key: int, func: Callable, target = 'default', once = False) -> None:
        self._listener.addEventListener(ET.KEY_UP, func, target, key, once)

    def addKeyCtrlEvent(self, key: int, func: Callable, target = 'default', once = False) -> None:
        self._listener.addEventListener(ET.KEY_CTRL, func, target, key, once)

    def removeEvents(self, target: str) -> None:
        self._listener.removeEventListener(target)

    def update(self, events = None) -> None:
        if self.is_root:
            if events is None:
                f_error('Root component should update by events.', ValueError, self)
            self._listener.update(events)

        self.removeDead()
        for ch in self.child_components:
            ch.update()

    def _mouseButtonEventGeneric(self, x: int, y: int, vx: int, vy: int,
                                   event_type, key_type):
        ''' If event occured, call children recursively. '''
        if not self.alive:
            return
        if not self.active:
            return

        self.removeDead()

        func_ls = self.__mouse_button_functions[event_type][key_type]
        parser_ls = self.__mouse_button_interface_parsers[event_type][key_type]

        for ch in self.child_components:
            rel_x = x - ch.x
            rel_y = y - ch.y
            if (0 <= rel_x <= ch.w) and (0 <= rel_y <= ch.h):
                ch._mouseButtonEventGeneric(rel_x, rel_y, vx, vy, event_type, key_type)

        for self_onMouseEvent, parser in zip(func_ls, parser_ls):
            args = parser(x, y, vx, vy)
            self_onMouseEvent(*args)

    def _mouseButtonEventsWrapper(self, event_type, key_type) -> Callable:
        '''
        event_type: MOUSE_DOWN, MOUSE_UP, MOUSE_PRESS\n
        key_type: 0-left, 1-mid, 2-right
        '''
        def onEventOccured(marg: MouseEventArgs) -> None:
            if not self.alive:
                return
            if not self.active:
                return
            x, y = marg.pos
            vx, vy = marg.vel
            self._mouseButtonEventGeneric(x, y, vx, vy, event_type, key_type)

        return onEventOccured

    def _recursiveOffHoverCheck(self):
        '''
        Child is active but father is inactive may happen if Child's area is
        larger than its father. Check if this situation happened.
        '''
        if self.active:
            return

        # self is not active but child is active
        for ch in filter(lambda ch: ch.active, self.child_components):
            ch.active = False
            ch._recursiveOffHoverCheck()
            ch.offHover()

    def _mouseMotionEventsGeneric(self, x: int, y: int, wheel: int, event_type):
        ''' If event occured, call children recursively. '''
        if not self.alive:
            return

        self.removeDead()

        if event_type == ET.MOUSE_INFO_GET:
            for ch in self.child_components:
                rel_x = x - ch.x
                rel_y = y - ch.y
                if (0 <= rel_x <= ch.w) and (0 <= rel_y <= ch.h):
                    ch.active = True
                    ch._mouseMotionEventsGeneric(rel_x, rel_y, wheel, event_type)
                    ch.onHover(rel_x, rel_y)
                elif ch.active: # not hover but active, change to not active
                    ch._mouseMotionEventsGeneric(rel_x, rel_y, wheel, event_type)
                    ch.active = False
                    ch._recursiveOffHoverCheck()
                    ch.offHover()
                else: # not hover and not active, no need to care mouse motion
                    pass

        elif event_type == ET.MOUSE_WHEEL:
            for ch in self.child_components:
                rel_x = x - ch.x
                rel_y = y - ch.y
                if (0 <= rel_x <= ch.w) and (0 <= rel_y <= ch.h):
                    ch._mouseMotionEventsGeneric(rel_x, rel_y, wheel, event_type)
            self.onMouseWheel(x, y, wheel)

    def _mouseMotionEventsWrapper(self, event_type) -> Callable:
        '''
        event_type: MOUSE_WHEEL, MOUSE_INFO_GET
        '''
        def onEventOccured(marg: MouseEventArgs) -> None:
            if not self.alive:
                return
            x, y = marg.pos
            self._mouseMotionEventsGeneric(x, y, marg.wheel, event_type)

        return onEventOccured

    # -------------------- Display -------------------- #
    def loadImage(self, img: Union[str, pg_Surface], w: int = None, h: int = None) -> pg_Surface:
        ''' Load a image and resize to (w, h). '''
        if isinstance(img, str):
            if not os.path.exists(img):
                f_error(f'Path {img} not exists.', FileExistsError, self)
            ret_img = pygame.image.load(img).convert_alpha()

        elif isinstance(img, pg_Surface):
            ret_img = img

        else:
            f_error(f'Not accept image type: {type(img)}.', TypeError, self)

        if w is None:
            w = ret_img.get_size()[0]
        if h is None:
            h = ret_img.get_size()[1]

        img_w, img_h = ret_img.get_size()
        if w == img_w and h == img_h:
            return ret_img
        else:
            return pygame.transform.scale(ret_img, (w, h))

    def getRect(self) -> Tuple[int]:
        ''' (w, h, x, y) '''
        return (self.w, self.h, self.x, self.y)

    def draw(self, surface: pg_Surface) -> None: ...


    # -------------------- Observer Pattern -------------------- #
    def addObserver(self, observer) -> None:
        '''
        Add an observer to this theme. All observers will be noticed when Theme call
        `notify` function. Observer can receive notice by calling `onReceive` function.
        '''
        self.removeDead()

        if not observer.alive:
            f_warning(f'Operation on dead component {observer}.', self)
            return

        if observer in self.observers:
            f_warning(f'Observer {observer} has already attached to {self}.', self)
            return

        self.observers.append(observer)

    def removeObserver(self, observer) -> None:
        ''' Remove observer from this theme. '''
        self.removeDead()

        if not observer.alive:
            f_warning(f'Operation on dead component {observer}.', self)
            return

        if observer not in self.observers:
            f_warning(f'Observer {observer} has not attach to {self} yet.', self)
            return

        self.observers.remove(observer)

    def removeAllObservers(self) -> None:
        ''' Clear all observers. '''
        self.observers = []

    def notify(self, theme: str, message: Any = None) -> None:
        ''' Send message to all observers. '''
        self.removeDead()

        for observer in self.observers:
            observer.onReceive(id(self), theme, message)

    def onReceive(self, sender_id: int, theme: str, message: Any) -> None:
        ''' Receive a mesage. '''
        pass