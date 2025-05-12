from typing import Tuple

from . import screen, widget

class Main:
    def __init__(self, size: Tuple[int, int], title: str) -> None:
        self.screen: screen.Screen
        self.root: widget.Root

    def run(self) -> None:
        ...