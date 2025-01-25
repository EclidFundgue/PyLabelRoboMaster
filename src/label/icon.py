import pygame

from .. import pygame_gui as ui
from .keypoint import Keypoint


class Icon(ui.components.CanvasComponent):
    '''
    Icon(w, h, cls_id, fix_size)

    Methods:
    * setClass(cls_id) -> None
    * setPosToKeypoint(point) -> None
    '''

    STATE_NORMAL = 0
    STATE_ACTIVE = 1
    STATE_SELECTED = 2

    def __init__(self,
        w: int,
        h: int,
        cls_id: int = 0
    ):
        super().__init__(w, h, 0, 0, fix_size=True)
        self.cls_id = cls_id
        self.label_state = self.STATE_NORMAL

    def setClass(self, cls_id: int) -> None:
        self.cls_id = cls_id

    def setPosToKeypoint(self, point: Keypoint):
        self._x = point._x
        self._y = point._y
        self.setCanvasView(self.scale, self.view_x, self.view_y)

class LabelIcon(Icon):
    '''
    LabelIcon(cls_id, fix_size, font)
    '''
    DEFAULT_FONT = None

    def __init__(self,
        cls_id: int = 0,
        font: pygame.font.Font = None
    ):
        if LabelIcon.DEFAULT_FONT is None:
            LabelIcon.DEFAULT_FONT = pygame.font.SysFont(
                ui.constants.DEFAULT_FONT_NAME,
                ui.constants.DEFAULT_FONT_SIZE
            )

        self.font = font if font is not None else self.DEFAULT_FONT
        self.text_img = self.font.render(str(cls_id), True, (255, 255, 255))

        super().__init__(*self.text_img.get_size(), cls_id)

    def setClass(self, cls_id: int) -> None:
        super().setClass(cls_id)
        self.text_img = self.font.render(str(cls_id), True, (255, 255, 255))

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.blit(self.text_img, (x_start, y_start))