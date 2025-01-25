import sys

sys.path.append('.')
import src.pygame_gui as ui


class TestCanvas(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        class _Rect(ui.components.CanvasComponent):
            def draw(self, surface, x_start, y_start):
                surface.fill((255, 255, 255))

        canvas = ui.components.Canvas(640, 640, 0, 0)
        rect = _Rect(160, 160, 20, 20, fix_size=False)

        canvas.setBackgroundColor((30, 30, 30))

        self.root.addChild(canvas)
        canvas.addChild(rect)


if __name__ == '__main__':
    main = TestCanvas()
    main.run()