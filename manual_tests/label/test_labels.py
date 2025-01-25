import sys

sys.path.append('.')
import pygame

import src.pygame_gui as ui
from src.label.icon import LabelIcon
from src.label.keypoint import Keypoint
from src.label.labels import Labels


class TestLabels(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        canvas = ui.components.Canvas(640, 640, 0, 0)

        def get_icon(kpt: Keypoint, cls_id: int) -> LabelIcon:
            icon = LabelIcon(cls_id)
            icon.setPosToKeypoint(kpt)
            return icon
        def on_select(cls_id: int) -> None:
            print('select:', cls_id)
        labels = Labels(320, 320, 20, 20, 4, get_icon, on_select)

        canvas.setBackgroundColor((30, 30, 30))
        canvas.addKeyDownEvent(pygame.K_a, labels.startAdd)
        canvas.addKeyDownEvent(pygame.K_0, lambda : labels.setSelectedClass(0))
        canvas.addKeyDownEvent(pygame.K_1, lambda : labels.setSelectedClass(1))

        self.root.addChild(canvas)
        canvas.addChild(labels)


if __name__ == '__main__':
    main = TestLabels()
    main.run()