import sys

sys.path.append('.')
import src.pygame_gui as ui


class _TempLine(ui.components.Selectable):
    def __init__(self, w, h, text, on_selected):
        super().__init__(w, h, 0, 0)
        self.on_selected = ui.utils.getCallable(on_selected)

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

    def onLeftClick(self, x, y):
        if not self.active:
            return
        self.on_selected(self)
        self.redraw()

class TestListBox(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        def on_selected(line):
            self.box.select(line)
        lines = [
            _TempLine(200+2*i, 30, str(i), on_selected) for i in range(15)
        ]
        def r_changed(r):
            print('r changed:', r)
        self.box = ui.components.ListBox(
            300, 300, 50, 50,
            lines,
            on_relative_change=r_changed
        )
        self.box.setBackgroundColor((100, 100, 100))

        self.root.addChild(self.box)


if __name__ == '__main__':
    main = TestListBox()
    main.run()
