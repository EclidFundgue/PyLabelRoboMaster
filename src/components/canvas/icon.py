import os

import pygame

from ... import pygame_gui as ui
from .canvas import CanvasComponent
from .keypoint import Keypoint


class ArmorIcon(CanvasComponent):
    '''Methods:
    * setClassId(cls_id) -> None
    * setPos(point) -> None
    '''

    STATE_NORMAL = 0
    STATE_ACTIVE = 1
    STATE_SELECTED = 2

    IMG_CLASSES = None # 8 classes
    IMG_LIGHTS = None # blue, red
    BACKGROUND_COLORS = None # normal, active, selected

    def __init__(self, cls_id: int):
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
        if ArmorIcon.BACKGROUND_COLORS is None:
            color_theme = ui.color.LightColorTheme()
            ArmorIcon.BACKGROUND_COLORS = [
                color_theme.OnPrimaryContainer,
                ui.color.light(color_theme.OnPrimaryContainer, 5),
                ui.color.light(color_theme.OnPrimaryContainer, 11)
            ]

        super().__init__(*self.IMG_CLASSES[0].get_size(), 0, 0, fix_size=True)
        self.cls_id = cls_id
        self.label_state = self.STATE_NORMAL

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
        surface.fill(self.BACKGROUND_COLORS[self.label_state])
        surface.blit(self.IMG_LIGHTS[self.cls_id // 8], (x_start, y_start))
        surface.blit(self.IMG_CLASSES[self.cls_id % 8], (x_start, y_start))