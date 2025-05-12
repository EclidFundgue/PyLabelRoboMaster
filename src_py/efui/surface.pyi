from typing import Tuple

class Surface:
    def __init__(self, size: Tuple[int, int]):
        self.w: int
        self.h: int
        self.is_from_window: bool

    def fill(self, color: Tuple[int, int, int]) -> None:
        ...

    def blit(self, src: 'Surface', pos: Tuple[int, int]) -> None:
        ...

def loadImage(path: str) -> Surface:
    ...