from .base import Base


class Selectable(Base):
    '''
    A selectable component only contains one attribute:
    `selected` and two methods: `select` and `unselect`.

    Methods:
    * select() -> None
    * unselect() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)

        self.selected: bool = False

    def select(self) -> None:
        self.selected = True

    def unselect(self) -> None:
        self.selected = False