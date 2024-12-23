from collections import defaultdict
from typing import Callable, List, Tuple, Union

import pygame

from .. import logger, utils

Condition = Callable[['KeyboardEventHandler'], bool]

@utils.singleton
class MouseEventHandler:
    LEFT = 0
    MID = 1
    RIGHT = 2
    ALL = 3

    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.vx: int = 0
        self.vy: int = 0
        self.wheel: int = 0
        self.buttons_last: Tuple[bool, bool, bool] = (0, 0, 0)
        self.buttons_now: Tuple[bool, bool, bool] = (0, 0, 0)
        self.is_down: bool = False
        self.is_up: bool = False
        self.motion: bool = False

    def update(self, x: int, y: int) -> None:
        self.vx = x - self.x
        self.vy = y - self.y
        self.x = x
        self.y = y
        self.buttons_last = self.buttons_now
        self.buttons_now = pygame.mouse.get_pressed()

        self.wheel = 0
        self.is_down = False
        self.is_up = False
        self.motion = False

    def down(self, key: int = ALL) -> bool:
        if key == self.ALL:
            return self.is_down
        return (not self.buttons_last[key]) and self.buttons_now[key]

    def up(self, key: int = ALL) -> bool:
        if key == self.ALL:
            return self.is_up
        return self.buttons_last[key] and (not self.buttons_now[key])

    def pressed(self, key: int = ALL) -> bool:
        if key == self.ALL:
            return any(self.buttons_now)
        return self.buttons_now[key]

class KeyboardEvent:
    DOWN = 0
    UP = 1
    PRESSED = 2
    CTRL = 3

    def __init__(self, key: int, func: Callable, _type: int, target: str):
        self.func = func
        self.condition: Condition = self._getConditionFunction(key, _type)
        if self.condition is None:
            logger.error(f'Invalid event type: {_type}.', ValueError, self)
        self.target = target

    def __call__(self, handler: 'KeyboardEventHandler') -> bool:
        if self.condition(handler):
            self.func()
            return True
        return False

    @staticmethod
    def _getConditionFunction(key: int, _type: int) -> Union[Condition, None]:
        if _type == KeyboardEvent.DOWN:
            if key == pygame.K_LCTRL or key == pygame.K_RCTRL:
                def condition(handler: 'KeyboardEventHandler') -> bool:
                    return handler.down(key)
            else:
                def condition(handler: 'KeyboardEventHandler') -> bool:
                    return handler.down(key) and not \
                        (handler.keys_now[pygame.K_LCTRL] or \
                        handler.keys_now[pygame.K_RCTRL])
            return condition
        elif _type == KeyboardEvent.UP:
            def condition(handler: 'KeyboardEventHandler') -> bool:
                return handler.up(key)
            return condition
        elif _type == KeyboardEvent.PRESSED:
            def condition(handler: 'KeyboardEventHandler') -> bool:
                return handler.pressed(key)
            return condition
        elif _type == KeyboardEvent.CTRL:
            def condition(handler: 'KeyboardEventHandler') -> bool:
                return handler.down(key) and \
                    (handler.pressed(pygame.K_LCTRL) or \
                     handler.pressed(pygame.K_RCTRL))
            return condition
        else:
            return None

@utils.singleton
class KeyboardEventHandler:
    ALL = None

    def __init__(self):
        self.keys_last: List[bool] = tuple([False] * 256)
        self.keys_now: List[bool] = tuple([False] * 256)

        self.is_down: bool = False
        self.is_up: bool = False

    def down(self, key: int = ALL) -> bool:
        if key is self.ALL:
            return self.is_down
        return (not self.keys_last[key]) and self.keys_now[key]

    def up(self, key: int = ALL) -> bool:
        if key is self.ALL:
            return self.is_up
        return self.keys_last[key] and (not self.keys_now[key])

    def pressed(self, key: int) -> bool:
        return self.keys_now[key]

    def update(self) -> None:
        self.keys_last = self.keys_now
        self.keys_now = pygame.key.get_pressed()

        self.is_down = False
        self.is_up = False