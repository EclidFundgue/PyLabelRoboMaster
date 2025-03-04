import sys

sys.path.append('.')
import pygame

import src.pygame_gui as ui
from src.file.selection import SelectionBox


class TestSelection(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        bg = ui.components.RectContainer(640, 640, 0, 0)

        def on_selected(
            folder: str,
            filename: str,
            is_deserted: bool
        ) -> None:
            print(f'select:({folder}, {filename}), deserted:{is_deserted}')
        box = SelectionBox(
            300, 200, 50, 50,
            'resources/test_dataset/images',
            'resources/test_dataset/images/deserted',
            on_selected=on_selected
        )

        bg.setBackgroundColor((255, 255, 255))
        def set_page_0():
            box.setPage(0)
            box.redraw()
        def set_page_1():
            box.setPage(1)
            box.redraw()
        box.addKeyDownEvent(pygame.K_0, set_page_0)
        box.addKeyDownEvent(pygame.K_1, set_page_1)
        box.addKeyDownEvent(pygame.K_q, box.selectPrev)
        box.addKeyDownEvent(pygame.K_e, box.selectNext)

        self.root.addChild(bg)
        bg.addChild(box)

if __name__ == '__main__':
    main = TestSelection()
    main.run()