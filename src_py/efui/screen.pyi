from typing import List, Tuple, Union

from .surface import Surface

class Screen:
    def __init__(self, size: Tuple[int, int], title: str) -> None:
        self.w: int
        self.h: int
        self.title: int

    def createWindow(self, pos: Tuple[int, int] = (-1, -1)) -> None:
        ...

    def destroyWindow(self) -> None:
        ...

    def isCreated(self) -> bool:
        ...

    def getSurface(self) -> Surface:
        ...

    def update(self) -> None:
        ...

def createWindow(
    size: Tuple[int, int],
    title: str,
    pos: Tuple[int, int] = (-1, -1)
) -> Screen:
    ...

def getAllWindows() -> List[Screen]:
    ...

def destroyAllWindows() -> None:
    ...