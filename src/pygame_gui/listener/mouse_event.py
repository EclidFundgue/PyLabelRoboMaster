from typing import List, Tuple

from pygame import locals, mouse
from pygame.event import Event


class MouseEvent:
    '''
    Listener of mouse events.

    @MouseEvent()

    Methods:
    * down(key) -> bool
    * up(key) -> bool
    * pressed(key) -> bool
    * pos() -> Tuple[int, int]
    * velocity() -> Tuple[int, int]
    * wheel() -> int
    '''
    def __init__(self):
        self.pressed_prev = mouse.get_pressed()
        self.pressed_now = mouse.get_pressed()
        self.pos_prev = mouse.get_pos()
        self.pos_now = mouse.get_pos()
        self.mouse_wheel = 0
        self.on_mouse_down = False
        self.on_mouse_up = False

    def update(self, events: List[Event]) -> None:
        ''' This method will be called by Listener. '''

        # pressed
        self.pressed_prev = self.pressed_now
        self.pressed_now = mouse.get_pressed()

        # position
        self.pos_prev = self.pos_now
        self.pos_now = mouse.get_pos()

        # other states
        self.mouse_wheel = 0
        self.on_mouse_down = False
        self.on_mouse_up = False
        for event in events:
            if event.type == locals.MOUSEWHEEL:
                self.mouse_wheel = event.y
            elif event.type == locals.MOUSEBUTTONDOWN:
                self.on_mouse_down = True
            elif event.type == locals.MOUSEBUTTONUP:
                self.on_mouse_up = True

    def down(self, key: int = None) -> bool:
        ''' key: 0-left, 1-mid, 2-right, None-all '''
        if key is None:
            return self.on_mouse_down
        return (not self.pressed_prev[key]) and \
                self.pressed_now[key]

    def up(self, key: int = None) -> bool:
        ''' key: 0-left, 1-mid, 2-right, None-all '''
        if key is None:
            return self.on_mouse_up
        return self.pressed_prev[key] and \
                (not self.pressed_now[key])
    
    def pressed(self, key: int) -> bool:
        ''' key: 0-left, 1-mid, 2-right '''
        return self.pressed_now[key]

    def pos(self) -> Tuple[int, int]:
        ''' key: 0-left, 1-mid, 2-right '''
        return self.pos_now

    def velocity(self) -> Tuple[int, int]:
        ''' mouse movement in two frames '''
        vel_x = self.pos_now[0] - self.pos_prev[0]
        vel_y = self.pos_now[1] - self.pos_prev[1]
        return vel_x, vel_y

    def wheel(self) -> int:
        ''' mouse wheel speed (+x: up, -x: down) '''
        return self.mouse_wheel