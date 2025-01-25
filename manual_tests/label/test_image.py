import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.label.image import Image


class TestImage(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        canvas = ui.components.Canvas(640, 640, 0, 0)
        image = Image('./resources/test_dataset/images/00.jpg')

        canvas.setBackgroundColor((30, 30, 30))

        self.root.addChild(canvas)
        canvas.addChild(image)


if __name__ == '__main__':
    main = TestImage()
    main.run()