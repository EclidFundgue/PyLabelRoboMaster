from typing import Any, Callable, Union

from pygame import Surface as pg_Surface

from ..global_vars import THEME_VAR_CHANGE
from ..pygame_gui import BaseComponent
from ..pygame_gui.decorators import getCallable


class Switch(BaseComponent):
    '''
    A Switch has two states: on and off.

    Switch(
        w, h, x, y,
        image_on,
        image_off,
        on_turn,
        on_turn_on,
        on_turn_off
    )

    Methods:
    * turn() -> None
    * turnOn() -> None
    * turnOff() -> None
    '''
    def __init__(self,
            w: int, h: int,
            x: int, y: int,
            image_on: Union[str, pg_Surface],
            image_off: Union[str, pg_Surface],
            on_turn: Callable[[bool], None] = None):
        super().__init__(w, h, x, y)

        self.image_on = self.loadImage(image_on, w, h)
        self.image_off = self.loadImage(image_off, w, h)

        self.on_turn = getCallable(on_turn)
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

    def onLeftClick(self, x: int, y: int) -> None:
        self.on = not self.on
        self.on_turn(self.on)

    def draw(self, surface: pg_Surface) -> None:
        if self.on:
            surface.blit(self.image_on, (self.x, self.y))
        else:
            surface.blit(self.image_off, (self.x, self.y))

class ThemeBasedSwitchTrigger(BaseComponent):
    '''
    Bind switch and variables. Change switch when variable changed.

    ThemeBasedSwitchTrigger()
    '''
    def __init__(self, var, switch: Switch):
        super().__init__()

        self.var: BaseComponent = var
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