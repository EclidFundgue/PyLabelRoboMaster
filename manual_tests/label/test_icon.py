import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.label.icon import Keypoint, LabelIcon


class _TempContainer(ui.components.CanvasComponent):
    def __init__(self):
        super().__init__(640, 640, 0, 0)

        self.kpt = Keypoint((120, 120))
        self.icon = LabelIcon(2)
        static_kpt = Keypoint((150, 150))

        self.icon.setPosToKeypoint(self.kpt)

        self.addChild(self.kpt)
        self.addChild(self.icon)
        self.addChild(static_kpt)

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if self.kpt.active:
            self.kpt.move(vx, vy)
            self.icon.setPosToKeypoint(self.kpt)
            self.redraw()

class TestIcon(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        canvas = ui.components.Canvas(640, 640, 0, 0)
        container = _TempContainer()

        canvas.setBackgroundColor((30, 30, 30))

        self.root.addChild(canvas)
        canvas.addChild(container)


if __name__ == '__main__':
    main = TestIcon()
    main.run()