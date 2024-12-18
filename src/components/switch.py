from typing import Any, Callable, List, Tuple, Union

import pygame

from .. import pygame_gui as ui


class Switch(ui.components.Base):
    '''
    A Switch has two states: on and off.

    Switch(
        w, h, x, y,
        image_on,
        image_off,
        on_turn,
        cursor_change
    )

    Methods:
    * turn() -> None
    * turnOn() -> None
    * turnOff() -> None
    '''
    def __init__(self,
            w: int, h: int,
            x: int, y: int,
            image_on: Union[str, pygame.Surface],
            image_off: Union[str, pygame.Surface],
            on_turn: Callable[[bool], None] = None,
            cursor_change: bool = True
        ):
        super().__init__(w, h, x, y)

        self.image_on = ui.utils.loadImage(image_on, w, h)
        self.image_off = ui.utils.loadImage(image_off, w, h)

        self.on_turn = ui.utils.getCallable(on_turn)
        self.cursor_change = cursor_change

        self.on = False

    def turn(self) -> None:
        self.on = not self.on

    def turnOn(self) -> None:
        self.on = True

    def turnOff(self) -> None:
        self.on = False

    def kill(self) -> None:
        self.on_turn = None
        super().kill()

    def onMouseEnter(self) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def onMouseLeave(self) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def onLeftClick(self, x: int, y: int) -> None:
        self.on = not self.on
        self.on_turn(self.on)
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int):
        if self.on:
            surface.blit(self.image_on, (x_start, y_start))
        else:
            surface.blit(self.image_off, (x_start, y_start))

class NTextSwitch(ui.components.Base):
    '''
    A Switch has a specific number of states.

    NTextSwitch(
        w, h, x, y,
        num_states,
        texts,
        font,
        text_color,
        background_color,
        on_turn,
        cursor_change
    )

    Methods:
    * turn() -> None
    * turnTo(state: int) -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            num_states: int,
            texts: List[str],
            font: pygame.font.Font = None,
            text_color: Tuple[int, int, int] = (0, 0, 0),
            background_color: Tuple[int, int, int] = (255, 255, 255),
            on_turn: Callable[[int], None] = None,
            cursor_change: bool = True
        ):
        super().__init__(w, h, x, y)

        self.num_states = num_states
        self.texts = texts
        self.on_turn = ui.utils.getCallable(on_turn)
        self.cursor_change = cursor_change

        self.state = 0

        self.label = ui.components.Label(
            w, h, 0, 0,
            text=texts[0],
            font=font,
            color=text_color,
        )
        self.container = ui.components.RoundedRectContainer(
            w, h, 0, 0,
            radius=min(w, h) // 4,
        )

        self.label.setAlignment(ui.constants.ALIGN_CENTER, ui.constants.ALIGN_CENTER)
        self.container.setBackgroundColor(background_color)

        self.container.addChild(self.label)
        self.addChild(self.container)

    def turn(self) -> None:
        self.state = (self.state + 1) % self.num_states
        self.label.setText(self.texts[self.state])

    def turnTo(self, state: int) -> None:
        if state < 0 or state >= self.num_states:
            ui.logger.warning(f'Invalid state {state}.', self)
            return
        self.state = state
        self.label.setText(self.texts[state])

    def kill(self) -> None:
        self.label = None
        self.container = None
        self.on_turn = None
        super().kill()

    def onMouseEnter(self):
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def onMouseLeave(self):
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def onLeftClick(self, x: int, y: int) -> None:
        self.turn()
        self.on_turn(self.state)
        self.redraw()