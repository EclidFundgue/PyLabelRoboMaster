import sys

sys.path.append('.')
import src.pygame_gui as ui
from src.components.light_bar import LightBar


class TestLightBar(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        bg = ui.components.RectContainer(640, 640, 0, 0)
        def on_change(light: float) -> None:
            print(light)
        light_bar = LightBar(400, 30, 80, 100, on_change)

        bg.setBackgroundColor((220, 220, 220))

        self.root.addChild(bg)
        bg.addChild(light_bar)

if __name__ == '__main__':
    main = TestLightBar()
    main.run()