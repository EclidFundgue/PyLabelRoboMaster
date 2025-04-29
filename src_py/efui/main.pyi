from typing import Tuple

from . import screen

class Main:
    def __init__(self, size: Tuple[int, int], title: str) -> None:
        self.screen: screen.Screen

    def run(self) -> None: ...