from typing import Tuple


class EventType:
    # do not change this order
    KEY_DOWN = 0
    KEY_UP = 1
    KEY_PRESS = 2
    KEY_CTRL = 3
    MOUSE_DOWN = 4
    MOUSE_UP = 5
    MOUSE_PRESS = 6
    MOUSE_WHEEL = 7
    MOUSE_INFO_GET = 8

class MouseEventArgs:
    def __init__(self, pos: Tuple[int, int], vel: Tuple[int, int], wheel: int):
        self.pos = pos          # mouse position
        self.vel = vel          # mouse velocity
        self.wheel = wheel      # mouse wheel speed (+:up, -:down)
