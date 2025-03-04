import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.label.image import Image


class TestImage(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        canvas = ui.components.Canvas(640, 640, 0, 0)
        self.image = Image('./resources/test_dataset/images/00.jpg')

        canvas.setBackgroundColor((30, 30, 30))

        self.gamma = 1.0
        def lighter():
            self.gamma -= 0.1
            self.image.setLight(self.gamma)
            self.image.redraw()
        def darker():
            self.gamma += 0.1
            self.image.setLight(self.gamma)
            self.image.redraw()
        canvas.addKeyDownEvent(ui.constants.K_a, lighter)
        canvas.addKeyDownEvent(ui.constants.K_d, darker)

        self.root.addChild(canvas)
        canvas.addChild(self.image)


if __name__ == '__main__':
    main = TestImage()
    main.run()