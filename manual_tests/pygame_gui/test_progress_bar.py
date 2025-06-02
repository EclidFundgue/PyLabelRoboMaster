import sys

sys.path.append('.')
import pygame

import src.pygame_gui as ui


class TestProgressBar(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        bg = ui.components.RectContainer(640, 640, 0, 0)

        def on_drag(r):
            print('r:', r)
        self.bar = ui.components.ProgressBar(
            550, 30, 40, 40, on_change=on_drag
        )

        bg.setBackgroundColor((0, 0, 0))
        def left() -> None:
            self.bar.set(self.bar.get() - 0.05)
            self.bar.redraw()
        self.bar.addKeyDownEvent(pygame.K_a, left)
        def right() -> None:
            self.bar.set(self.bar.get() + 0.05)
            self.bar.redraw()
        self.bar.addKeyDownEvent(pygame.K_d, right)

        self.root.addChild(bg)
        bg.addChild(self.bar)


if __name__ == '__main__':
    main = TestProgressBar()
    main.run()