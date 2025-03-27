import sys

sys.path.append('.')
import src.pygame_gui as ui


class TestProgressBar(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        bg = ui.components.RectContainer(640, 640, 0, 0)

        def on_drag(r):
            print('r:', r)
        bar = ui.components.ProgressBar(
            550, 30, 40, 40, on_change=on_drag
        )

        bg.setBackgroundColor((0, 0, 0))

        self.root.addChild(bg)
        bg.addChild(bar)


if __name__ == '__main__':
    main = TestProgressBar()
    main.run()