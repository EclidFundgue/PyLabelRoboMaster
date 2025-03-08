import os

import pygame

from ... import pygame_gui as ui
from ...label import Icon


class ArmorIcon(Icon):
    '''
    ArmorIcon(cls_id)
    '''
    IMG_CLASSES = None # 8 classes
    IMG_LIGHTS = None # blue, red
    BACKGROUND_COLORS = None # normal, active, selected

    def __init__(self, cls_id: int):
        prefix = './resources/armor_icons'

        if ArmorIcon.IMG_CLASSES is None:
            filenames = [
                'sentry.png', '1.png', '2.png', '3.png',
                '4.png', '5.png', 'outpost.png', 'base1.png'
            ]
            ArmorIcon.IMG_CLASSES = [
                ui.utils.loadImage(os.path.join(prefix, filename), 32, 32)
                for filename in filenames
            ]

        if ArmorIcon.IMG_LIGHTS is None:
            ArmorIcon.IMG_LIGHTS = [
                ui.utils.loadImage(os.path.join(prefix, 'bg_blue.png'),32, 32),
                ui.utils.loadImage(os.path.join(prefix, 'bg_red.png'), 32, 32),
            ]

        if ArmorIcon.BACKGROUND_COLORS is None:
            color_theme = ui.color.LightColorTheme()
            ArmorIcon.BACKGROUND_COLORS = [
                color_theme.OnPrimaryContainer,
                ui.color.light(color_theme.OnPrimaryContainer, 5),
                ui.color.light(color_theme.OnPrimaryContainer, 11)
            ]

        super().__init__(*self.IMG_CLASSES[0].get_size(), cls_id)

    def setCanvasView(self, scale, view_x, view_y):
        super().setCanvasView(scale, view_x, view_y)
        self.x = int(self._x * scale - view_x + 15)
        self.y = int(self._y * scale - view_y + 10)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.fill(self.BACKGROUND_COLORS[self.label_state])
        surface.blit(self.IMG_LIGHTS[self.cls_id // 8], (x_start, y_start))
        surface.blit(self.IMG_CLASSES[self.cls_id % 8], (x_start, y_start))

def getIcon(kpt, cls_id) -> ArmorIcon:
    icon = ArmorIcon(cls_id)
    icon.setPosToKeypoint(kpt)
    return icon