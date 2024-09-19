from typing import List

from pygame import key, locals
from pygame.event import Event


class KeyboardEvent:
    '''
    Listener of keyboard events.

    @KeyboardEvent()

    APIs:
    * down(key) -> bool
    * up(key) -> bool
    * pressed(key) -> bool
    '''
    def __init__(self):
        self.pressed_prev = key.get_pressed()
        self.pressed_now = key.get_pressed()
        self.on_key_down = False
        self.on_key_up = False

    def update(self, events: List[Event]) -> None:
        ''' This method will be called by Listener. '''

        # update pressed
        self.pressed_prev = self.pressed_now
        self.pressed_now = key.get_pressed()

        # update KeyDown and KeyUp
        self.on_key_down = False
        self.on_key_up = False
        for event in events:
            if event.type == locals.KEYDOWN:
                self.on_key_down = True
            elif event.type == locals.KEYUP:
                self.on_key_up = True

    def down(self, key: int = None) -> bool:
        ''' None: any key '''
        if key is None:
            return self.on_key_down
        return (not self.pressed_prev[key]) and \
                self.pressed_now[key]

    def up(self, key: int = None) -> bool:
        ''' None: any key '''
        if key is None:
            return self.on_key_up
        return self.pressed_prev[key] and \
                (not self.pressed_now[key])

    def pressed(self, key: int) -> bool:
        return self.pressed_now[key]