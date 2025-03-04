import sys

sys.path.append('.')
import src.pygame_gui as ui


class TestScrollBar(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        def on_drag(r):
            print('r:', r)
        bar = ui.components.ScrollBar(
            20, 300, 40, 40, on_drag=on_drag
        )

        self.root.addChild(bar)


if __name__ == '__main__':
    main = TestScrollBar()
    main.run()
