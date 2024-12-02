from typing import List, Tuple

import pygame

from .. import logger
from .base import Base, _RedrawNode


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

def updateRecurse(
    obj: Base,
    parent_x: int,
    parent_y: int,
    mouse: MouseEventHandler,
) -> None:
    x = mouse.x - parent_x - obj.x
    y = mouse.y - parent_y - obj.y
    obj.update(x, y, mouse.wheel)

    # mouse events callbacks
    active = obj.isHovered(x, y)
    on_enter = obj.active and not active
    on_leave = not obj.active and active
    obj.active = active
    if on_enter:
        obj.onMouseEnter()
    elif on_leave:
        obj.onMouseLeave()

    if mouse.down():
        if mouse.down(mouse.LEFT):
            obj.onLeftClick(x, y)
        if mouse.down(mouse.MID):
            obj.onMidClick(x, y)
        if mouse.down(mouse.RIGHT):
            obj.onRightClick(x, y)

    if mouse.pressed():
        if mouse.pressed(mouse.LEFT):
            obj.onLeftPress(x, y)
            if mouse.motion:
                obj.onLeftDrag(mouse.vx, mouse.vy)
        if mouse.pressed(mouse.MID):
            obj.onMidPress(x, y)
            if mouse.motion:
                obj.onMidDrag(mouse.vx, mouse.vy)
        if mouse.pressed(mouse.RIGHT):
            obj.onRightPress(x, y)
            if mouse.motion:
                obj.onRightDrag(mouse.vx, mouse.vy)

    if mouse.up():
        if mouse.up(mouse.LEFT):
            obj.onLeftRelease()
        if mouse.up(mouse.MID):
            obj.onMidRelease()
        if mouse.up(mouse.RIGHT):
            obj.onRightRelease()

    for ch in obj._children:
        updateRecurse(ch, parent_x + obj.x, parent_y + obj.y, mouse)

class Root(Base):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        w, h = self.screen.get_size()
        super().__init__(w, h, 0, 0)

        self.redraw_tree: _RedrawNode = _RedrawNode(self, False)
        self.mouse = MouseEventHandler()

    def _redrawRecurse(self, redraw_chain: List[_RedrawNode]) -> None:
        self.redraw_tree.needs_redraw = True
        self.redraw_tree.updateRecurse(redraw_chain)

    def update(self, events: List[pygame.event.Event]) -> None:
        self.mouse.update(*pygame.mouse.get_pos())

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.mouse.wheel = event.y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse.is_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse.is_up = True
            elif event.type == pygame.MOUSEMOTION:
                self.mouse.motion = True

        for ch in self._children:
            updateRecurse(ch, 0, 0, self.mouse)

    def redraw(self):
        self.redraw_tree.drawAll(self.screen)
        pygame.display.flip()

    def draw(self, surface: pygame.Surface = None) -> None:
        # drawRecurse will call this method with surface
        # to avoid infinite recursion, only call drawRecurse with no surface
        if surface is not None:
            return
        if not self.redraw_tree.needs_redraw:
            return
        self.redraw_tree.drawRecurse(self.screen)
        pygame.display.flip()