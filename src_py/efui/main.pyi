from typing import Tuple

from . import screen, widgets

class Main:
    def __init__(self, size: Tuple[int, int], title: str) -> None:
        self.screen: screen.Screen
        self.root: widgets.Root

    def run(self) -> None:
        ...