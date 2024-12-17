import os
from typing import Callable, Tuple

import pygame

from ... import pygame_gui as ui
from .canvas import CanvasComponent
from .keypoint import Keypoint


class ArmorIcon(CanvasComponent):
    '''Methods:
    * setClassId(cls_id) -> None
    * setPos(point) -> None
    '''

    IMG_CLASSES = None # 8 classes
    IMG_LIGHTS = None # blue, red

    def __init__(self, x: int, y: int, cls_id: int, on_click: Callable[[], None] = None):
        prefix = './resources/armor_icons'
        if ArmorIcon.IMG_CLASSES is None:
            ArmorIcon.IMG_CLASSES = [
                ui.utils.loadImage(os.path.join(prefix, 'sentry.png')),
                ui.utils.loadImage(os.path.join(prefix, '1.png')),
                ui.utils.loadImage(os.path.join(prefix, '2.png')),
                ui.utils.loadImage(os.path.join(prefix, '3.png')),
                ui.utils.loadImage(os.path.join(prefix, '4.png')),
                ui.utils.loadImage(os.path.join(prefix, '5.png')),
                ui.utils.loadImage(os.path.join(prefix, 'outpost.png')),
                ui.utils.loadImage(os.path.join(prefix, 'base.png')),
            ]
        if ArmorIcon.IMG_LIGHTS is None:
            ArmorIcon.IMG_LIGHTS = [
                ui.utils.loadImage(os.path.join(prefix, 'bg_blue.png')),
                ui.utils.loadImage(os.path.join(prefix, 'bg_red.png')),
            ]

        super().__init__(*self.IMG_CLASSES[0].get_size(), x, y, fix_size=True)
        self.cls_id = cls_id
        self.on_click = ui.utils.getCallable(on_click)

        self.label_state: int = 0 # 0-normal, 1-active, 2-selected

        color_theme = ui.color.LightColorTheme()
        self.icon_colors = [
            color_theme.OnPrimaryContainer,
            ui.color.light(color_theme.OnPrimaryContainer, 5),
            ui.color.light(color_theme.OnPrimaryContainer, 11)
        ]

    def setClassId(self, cls_id: int) -> None:
        self.cls_id = cls_id

    def setPos(self, point: Keypoint):
        self._x = point._x
        self._y = point._y
        self.setCanvasView(self.scale, self.view_x, self.view_y)

    def setCanvasView(self, scale, view_x, view_y):
        super().setCanvasView(scale, view_x, view_y)
        self.x = int(self._x * scale - view_x + 15)
        self.y = int(self._y * scale - view_y + 10)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.fill(self.icon_colors[self.label_state])
        surface.blit(self.IMG_LIGHTS[self.cls_id // 8], (x_start, y_start))
        surface.blit(self.IMG_CLASSES[self.cls_id % 8], (x_start, y_start))