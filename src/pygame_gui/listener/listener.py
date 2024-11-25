from collections import defaultdict
from typing import Callable

from pygame import locals

from .. import logger
from ..decorators import singleton
from .event_types import MouseEventArgs as MArgs
from .keyboard_event import KeyboardEvent
from .mouse_event import MouseEvent


@singleton
class Listener():
    '''
    Events listener. (singleton object)

    Listener()

    Methods:
    * update(events) -> None
    * addEventListener(event_type, func, target, key_type, once) -> None
    * removeEventListener(target) -> None
    '''
    def __init__(self):
        self.__mouse = MouseEvent()
        self.__keyboard = KeyboardEvent()

        # If the condition return True, trigger the event.
        self.__conditions = [
            lambda key_tp: self.__keyboard.down(key_tp) and not \
                (self.__keyboard.pressed(locals.K_LCTRL) or \
                 self.__keyboard.pressed(locals.K_RCTRL)),      # KEY_DOWN
            lambda key_tp: self.__keyboard.up(key_tp),          # KEY_UP
            lambda key_tp: self.__keyboard.pressed(key_tp),     # KEY_PRESS
            lambda key_tp: self.__keyboard.down(key_tp) and \
                (self.__keyboard.pressed(locals.K_LCTRL) or \
                 self.__keyboard.pressed(locals.K_RCTRL)),      # KEY_CTRL
            lambda key_tp: self.__mouse.down(key_tp),           # MOUSE_DOWN
            lambda key_tp: self.__mouse.up(key_tp),             # MOUSE_UP
            lambda key_tp: self.__mouse.pressed(key_tp),        # MOUSE_PRESS
            lambda key_tp: self.__mouse.wheel(),                # MOUSE_WHEEL
            lambda key_tp: True,                                # MOUSE_INFO_GET
        ]

        def getMargs() -> MArgs:
            return (MArgs(self.__mouse.pos(),
                          self.__mouse.velocity(),
                          self.__mouse.wheel()),)
        # Parse arguments to event function.
        self.__arg_parser = [
            tuple,      # KEY_DOWN
            tuple,      # KEY_UP
            tuple,      # KEY_PRESS
            tuple,      # KEY_CTRL
            getMargs,   # MOUSE_DOWN
            getMargs,   # MOUSE_UP
            getMargs,   # MOUSE_PRESS
            getMargs,   # MOUSE_WHEEL
            getMargs,   # MOUSE_INFO_GET
        ]

        self.__events_dict = defaultdict(list)
        self.__events_list_once = []
        self.__targets_to_remove = []
        self.__events_to_add = []
        self.__events_to_add_once = []

    def _popTargetsFromEvents(self) -> None:
        if not self.__targets_to_remove:
            return

        for target in self.__targets_to_remove:
            ret = self.__events_dict.pop(target, None)
            if ret is None:
                logger.warning(f'Target "{target}" not in events dictionary.', self)
        self.__targets_to_remove = []

    def _addTargetToEvents(self) -> None:
        if self.__events_to_add:
            for target, on_occured in self.__events_to_add:
                self.__events_dict[target].append(on_occured)
            self.__events_to_add = []
        
        if self.__events_to_add_once:
            for on_occured in self.__events_to_add_once:
                self.__events_list_once.append(on_occured)
            self.__events_to_add_once = []

    def update(self, events) -> None:
        ''' This function need to be called in the main loop '''
        self.__mouse.update(events)
        self.__keyboard.update(events)

        for ls in self.__events_dict.values():
            for func in ls:
                func()

        for func in self.__events_list_once:
            func()
        self.__events_list_once = []

        # change event queue only if iteration finished
        self._popTargetsFromEvents()
        self._addTargetToEvents()

    def addEventListener(self,
            event_type: int,
            func: Callable,
            target: str = 'default',
            key_type: int = None,
            once = False) -> None:
        '''
        * `event_type`: EventType
        * `func`: Called when event occures.
        * `target`: Used in remove.
        * `key_type`: e.g. K_a, K_SPACE.
        * `once`: Call once then remove it.

        We can not add it directly to avoid change during iteration.
        See `removeEventListener`.
        '''
        def onEventOccured():
            condition_func = self.__conditions[event_type]
            parser = self.__arg_parser[event_type]
            if condition_func(key_type):
                args = parser()
                func(*args)

        if not once:
            self.__events_to_add.append((target, onEventOccured))
        else:
            self.__events_to_add_once.append(onEventOccured)

    def removeEventListener(self, target: str) -> None:
        '''
        * `target`: Used in remove.

        We can not remove it directly. Because in some cases, it may be
        called in event update loop. Then we will receive RuntimeError:
        dictionary changed size during iteration.
        '''
        self.__targets_to_remove.append(target)