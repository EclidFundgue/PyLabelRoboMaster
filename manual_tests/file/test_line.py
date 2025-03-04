import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.file.line import DesertedFileLine, FileLine, ImageFileLine


class TestFileLine(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        def select(line: FileLine):
            print('select:', line.filename)
            line.select()

        def delete_1(line: FileLine):
            print('delete:', line.filename)
            line.unselect()
        l1 = ImageFileLine(200, 50, 'line1.txt', select, delete_1)
        l1.x = 20
        l1.y = 20

        def restore_2(line: FileLine):
            print('delete:', line.filename)
            line.unselect()
        l2 = DesertedFileLine(200, 50, 'line2.txt', select, restore_2)
        l2.x = 20
        l2.y = 90

        self.root.addChild(l1)
        self.root.addChild(l2)

if __name__ == '__main__':
    main = TestFileLine()
    main.run()