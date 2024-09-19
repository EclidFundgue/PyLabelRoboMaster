from .base import BaseComponent


class Selectable(BaseComponent):
    '''
    Selectable component interface.

    Selectable()

    Methods:
    * select() -> None
    * unselect() -> None
    '''
    def __init__(self, w: int = 0, h: int = 0, x: int = 0, y: int = 0):
        super().__init__(w, h, x, y)

        self.selected = False

    def select(self) -> None:
        self.selected = True

    def unselect(self) -> None:
        self.selected = False