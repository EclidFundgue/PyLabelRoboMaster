import sys

sys.path.append('.')
import src.pygame_gui as ui


class _TempLine(ui.components.Selectable):
    def __init__(self, w, h, text):
        super().__init__(w, h, 0, 0)

        self.label = ui.components.Label(w, h, 0, 0, text)
        self.bg = ui.components.RectContainer(w, h, 0, 0)

        self.label.layer = 1
        self.bg.layer = 0
        self.bg.setBackgroundColor((255, 255, 255))

        self.addChild(self.label)
        self.addChild(self.bg)

    def select(self):
        super().select()
        self.label.setColor((255, 255, 255))
        self.bg.setBackgroundColor((60, 60, 60))

    def unselect(self):
        super().unselect()
        self.label.setColor((0, 0, 0))
        self.bg.setBackgroundColor((255, 255, 255))

class TestListBox(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        lines = [
            _TempLine(200+2*i, 30, str(i)) for i in range(15)
        ]
        def r_changed(r):
            print('r changed:', r)
        def on_select(idx, line):
            print('selected:', idx, line)
        box = ui.components.ListBox(
            300, 300, 50, 50,
            lines,
            on_relative_change=r_changed,
            on_select=on_select
        )
        box.setBackgroundColor((100, 100, 100))

        self.root.addChild(box)


if __name__ == '__main__':
    main = TestListBox()
    main.run()
