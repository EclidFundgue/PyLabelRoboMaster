import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.label.keypoint import Keypoint


class TestKeypoint(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        canvas = ui.components.Canvas(640, 640, 0, 0)

        def on_click(kpt: Keypoint):
            print('clicked: ', kpt.getCenter())
        keypoint = Keypoint((50, 50), on_click)

        canvas.setBackgroundColor((255, 255, 255))

        self.root.addChild(canvas)
        canvas.addChild(keypoint)


if __name__ == '__main__':
    main = TestKeypoint()
    main.run()