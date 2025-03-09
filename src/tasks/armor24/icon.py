import os
from typing import Tuple

import pygame

from ... import pygame_gui as ui
from ...label import Icon


class ArmorIcon(Icon):
    '''
    ArmorIcon(cls_id)
    '''
    IMG_CLASSES = None # 8 classes

    def __init__(self, cls_id: int):
        if ArmorIcon.IMG_CLASSES is None:
            prefix = './resources/armor_icons'
            filenames = [
                'sentry.png', '1.png',
                '2.png', '3.png',
                '4.png', '5.png',
                'outpost.png', 'base1.png'
            ]
            ArmorIcon.IMG_CLASSES = [
                ui.utils.loadImage(
                    img=os.path.join(prefix, filename),
                    w=40,
                    h=40
                ) for filename in filenames
            ]

        self.bg_color_frames = [
            (255, 255, 255),    # normal
            (255, 255, 255),    # hover
            (0, 255, 0)         # selected
        ]
        self.bg_colors = [
            [ # color = 0, blue
                (24, 136, 182),                     # normal
                ui.color.light((24, 136, 182), 3),  # hover
                ui.color.light((24, 136, 182), 8)   # selected
            ],
            [ # color = 1, red
                (219, 73, 34),                      # normal
                ui.color.light((219, 73, 34), 3),   # hover
                ui.color.light((219, 73, 34), 8),   # selected
            ]
        ]

        super().__init__(48, 48, cls_id)

    def setCanvasView(self, scale, view_x, view_y):
        super().setCanvasView(scale, view_x, view_y)
        self.x = int(self._x * scale - view_x + 15)
        self.y = int(self._y * scale - view_y + 10)

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        ui.utils.drawRoundedRect(
            surface = surface,
            color = self.bg_color_frames[self.label_state],
            rect = (x_start, y_start, self.w, self.h),
            radius = self.h // 4
        )
        ui.utils.drawRoundedRect(
            surface = surface,
            color = self.bg_colors[self.cls_id // 8][self.label_state],
            rect = (x_start + 1, y_start + 1, self.w - 2, self.h - 2),
            radius = (self.h - 2) // 4
        )
        surface.blit(
            self.IMG_CLASSES[self.cls_id % 8],
            (x_start + 4, y_start + 4)
        )

def getIcon(kpt, cls_id) -> ArmorIcon:
    icon = ArmorIcon(cls_id)
    icon.setPosToKeypoint(kpt)
    return icon