import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.file.box import DesertedFileBox, ImageFileBox


class TestFileBox(ui.Main):
    def __init__(self):
        super().__init__((800, 640))

        def on_selected(filename: str):
            print('select:', filename)
        def on_deserted(filename: str):
            print('desert:', filename)
        image_file_box = ImageFileBox(
            300, 150, 40, 40,
            folder='resources/test_dataset/images',
            on_file_selected=on_selected,
            on_file_deserted=on_deserted
        )

        def on_restore(filename: str):
            print('restore:', filename)
        deserted_file_box = DesertedFileBox(
            300, 500, 350, 40,
            folder='resources/test_dataset/images',
            on_file_selected=on_selected,
            on_file_restored=on_restore
        )

        image_file_box.setBackgroundColor((0, 0, 0))
        deserted_file_box.setBackgroundColor((0, 0, 0))

        self.root.addChild(image_file_box)
        self.root.addChild(deserted_file_box)

if __name__ == '__main__':
    main = TestFileBox()
    main.run()