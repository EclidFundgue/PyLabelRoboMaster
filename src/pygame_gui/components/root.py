from typing import List

import pygame

from .base import Base, _RedrawNode
from .events import KeyboardEventHandler, MouseEventHandler


def _interact(
    obj: Base,
    x: int, y: int,
    mouse: MouseEventHandler,
    keyboard: KeyboardEventHandler
) -> None:
    # mouse events callbacks
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

    # Object may be killed during interation.
    if not obj.alive:
        return

    # keyboard events callbacks
    for event in obj._keyboard_events:
        event(keyboard)
    obj._keyboard_events_once = list(
        filter(lambda e: not e(keyboard), obj._keyboard_events_once)
    )

def _updateRecurse(
    obj: Base,
    parent_x: int,
    parent_y: int,
    mouse: MouseEventHandler,
    keyboard: KeyboardEventHandler,
    interactive: bool = True
) -> None:
    if not obj.alive:
        return

    x = mouse.x - parent_x - obj.x
    y = mouse.y - parent_y - obj.y
    obj.removeDeadChildren()

    active = obj.isHovered(x, y)
    on_enter = not obj.active and active
    on_leave = obj.active and not active
    obj.active = active
    if on_enter:
        obj.onMouseEnter()
    elif on_leave:
        obj.onMouseLeave()

    interactive = (obj.active or not obj.interactive_when_active) and interactive
    if interactive:
        _interact(obj, x, y, mouse, keyboard)

    # Object may be killed during interation.
    if not obj.alive:
        return

    obj.update(x, y, mouse.wheel)
    for ch in obj._children:
        _updateRecurse(ch, parent_x + obj.x, parent_y + obj.y, mouse, keyboard, interactive)

class Root(Base):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        w, h = self.screen.get_size()
        super().__init__(w, h, 0, 0)

        self.redraw_tree: _RedrawNode = _RedrawNode(self, False)
        self.mouse = MouseEventHandler()
        self.keyboard = KeyboardEventHandler()

    def _submitDrawStack(self, redraw_stack: List[Base]) -> None:
        redraw_chain = _RedrawNode(redraw_stack[0], True)
        for i in range(1, len(redraw_stack)):
            needs_redraw = redraw_chain.needs_redraw and redraw_chain.component.redraw_parent
            tmp_node = _RedrawNode(redraw_stack[i], needs_redraw)
            tmp_node.needs_redraw_children.append(redraw_chain)
            redraw_chain = tmp_node

        self.redraw_tree.merge(redraw_chain)

    def update(self, events: List[pygame.event.Event]) -> None:
        self.mouse.update(*pygame.mouse.get_pos())
        self.keyboard.update()

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.mouse.wheel = event.y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse.is_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse.is_up = True
            elif event.type == pygame.MOUSEMOTION:
                self.mouse.motion = True
            elif event.type == pygame.KEYDOWN:
                self.keyboard.is_down = True
            elif event.type == pygame.KEYUP:
                self.keyboard.is_up = True

        for ch in self._children:
            _updateRecurse(ch, 0, 0, self.mouse, self.keyboard)

    def redraw(self):
        self.redraw_tree.clear()
        self.redraw_tree.needs_redraw = True

    def draw(self, surface: pygame.Surface = None, x_start: int = 0, y_start: int = 0) -> None:
        # drawRecurse will call this method with surface
        # to avoid infinite recursion, only call drawRecurse with no surface
        if surface is not None:
            return
        self.redraw_tree.draw(self.screen, x_start, y_start)
        self.redraw_tree.clear()
        pygame.display.flip()