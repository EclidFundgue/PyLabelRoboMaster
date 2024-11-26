from typing import Any, Callable, List, Tuple, Union

import pygame
from pygame import Surface

from .. import pygame_gui as ui
from ..global_vars import THEME_VAR_CHANGE
from ..pygame_gui import logger


class Switch(ui.components.BaseComponent):
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
            image_on: Union[str, Surface],
            image_off: Union[str, Surface],
            on_turn: Callable[[bool], None] = None,
            cursor_change: bool = True
        ):
        super().__init__(w, h, x, y)

        self.image_on = self.loadImage(image_on, w, h)
        self.image_off = self.loadImage(image_off, w, h)

        self.on_turn = ui.getCallable(on_turn)
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

    def onHover(self, x: int, y: int) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def offHover(self) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def onLeftClick(self, x: int, y: int) -> None:
        self.on = not self.on
        self.on_turn(self.on)

    def draw(self, surface: Surface) -> None:
        if self.on:
            surface.blit(self.image_on, (self.x, self.y))
        else:
            surface.blit(self.image_off, (self.x, self.y))

    def addObserver(self, observer) -> None:
        '''
        Add an observer to this theme. All observers will be noticed when Theme call
        `notify` function. Observer can receive notice by calling `onReceive` function.
        '''
        self.removeDead()

        if not observer.alive:
            logger.warning(f'Operation on dead component {observer}.', self)
            return

        if observer in self.observers:
            logger.warning(f'Observer {observer} has already attached to {self}.', self)
            return

        self.observers.append(observer)

    def removeObserver(self, observer) -> None:
        ''' Remove observer from this theme. '''
        self.removeDead()

        if not observer.alive:
            logger.warning(f'Operation on dead component {observer}.', self)
            return

        if observer not in self.observers:
            logger.warning(f'Observer {observer} has not attach to {self} yet.', self)
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

class NTextSwitch(ui.components.BaseComponent):
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
        self.on_turn = ui.getCallable(on_turn)
        self.cursor_change = cursor_change

        self.state = 0

        self.label = ui.components.Label(
            w, h, 0, 0,
            text=texts[0],
            font=font,
            text_color=text_color,
        )
        self.container = ui.components.RoundedRectContainer(
            w, h, x, y,
            radius=min(w, h) // 4,
        )

        self.label.setAlignment(
            align_x=ui.constants.ALIGN_CENTER,
            align_y=ui.constants.ALIGN_CENTER
        )
        self.container.setBackgroundColor(background_color)

        self.container.addChild(self.label)
        self.addChild(self.container)

    def turn(self) -> None:
        self.state = (self.state + 1) % self.num_states
        self.label.setText(self.texts[self.state])

    def turnTo(self, state: int) -> None:
        if state < 0 or state >= self.num_states:
            logger.warning(f'Invalid state {state}.', self)
            return
        self.state = state
        self.label.setText(self.texts[state])

    def kill(self) -> None:
        self.label = None
        self.container = None
        self.on_turn = None
        super().kill()

    def onHover(self, x: int, y: int) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def offHover(self) -> None:
        if self.cursor_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def onLeftClick(self, x: int, y: int) -> None:
        self.turn()
        self.on_turn(self.state)

    def setRect(self, w: int, h: int, x: int, y: int):
        super().setRect(w, h, x, y)
        self.container.setRect(w, h, x, y)

    def draw(self, surface: Surface) -> None:
        self.container.draw(surface)

class ThemeBasedSwitchTrigger(ui.components.BaseComponent):
    '''
    Bind switch and variables. Change switch when variable changed.

    ThemeBasedSwitchTrigger()
    '''
    def __init__(self, var, switch: Switch):
        super().__init__()

        self.var: ui.components.BaseComponent = var
        self.switch = switch

        self.var.addObserver(self)

    def kill(self) -> None:
        if self.var.alive:
            self.var.removeObserver(self)
        self.var = None
        self.switch = None
        return super().kill()
    
    def onReceive(self, sender_id: int, theme: str, message: Any) -> None:
        if theme == THEME_VAR_CHANGE and sender_id == id(self.var):
            state: bool = message
            if state:
                self.switch.turnOn()
            else:
                self.switch.turnOff()