import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.components.toolbar import ToolbarButtons


class TestLightBar(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        toolbar = ToolbarButtons(
            300, 500, 50, 50,
            on_add=lambda : print('add'),
            on_delete = lambda : print('delete'),
            on_save = lambda : print('save'),
            on_search = lambda : print('search'),
            on_correct = lambda : print('correct'),
            on_autoplay = lambda : print('auto'),
            on_light_change = lambda x : print('light:', x)
        )
        bg = ui.components.RectContainer(640, 640, 0, 0)

        bg.setBackgroundColor((220, 220, 220))

        self.root.addChild(bg)
        bg.addChild(toolbar)

if __name__ == '__main__':
    main = TestLightBar()
    main.run()