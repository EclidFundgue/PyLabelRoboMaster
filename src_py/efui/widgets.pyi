from .surface import Surface

class Base:
    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        self.x: int
        self.y: int
        self.w: int
        self.h: int
        self.layer: int # default 0
        self.redraw_parent: bool # default True
        self.interactive_when_active: bool # default True
        self.alive: bool # default True, read only
        self.active: bool # default False, read only

    def addChild(self, child: Base) -> None: ...
    def removeChild(self, child: Base) -> None: ...
    def redraw(self) -> None: ...

    # slots
    def draw(self, surface: Surface, x: int, y: int) -> None: ...

class Root(Base):
    def __init__(self, surface: Surface):
        self.surface: Surface

    def draw(self) -> None: ...