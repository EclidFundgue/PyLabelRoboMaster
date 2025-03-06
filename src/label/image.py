from typing import Tuple

import pygame

from .. import pygame_gui as ui
from ..utils import imgproc


class Image(ui.components.CanvasComponent):
    '''Methods:
    * getOrigSize() -> Tuple[int, int]
    * setLight(gamma) -> None
    '''
    def __init__(self, path: str):
        self.orig_image = ui.utils.loadImage(path)
        super().__init__(*self.orig_image.get_size(), 0, 0)

        self.path = path
        self.image = self.orig_image
        self.cut_surface = self.orig_image
        self.blit_offset = (0, 0)

        self.gamma = 0.0
        self.need_update_cut_surface = True

        # image layer is behind other components
        self.layer = -1

    def _getCutRect(self, surface: pygame.Surface) -> pygame.rect.Rect:
        surf_w, surf_h = surface.get_size()

        left = -int(self.x / self.scale) if self.x < 0 else 0
        right = self.orig_image.get_width()
        if self.x < 0 and self.x + self.w > surf_w:
            right = int((surf_w - self.x) / self.scale) + 1
        elif self.x >= 0 and self.w > surf_w:
            right = int(surf_w / self.scale) + 1

        top = -int(self.y / self.scale) if self.y < 0 else 0
        bottom = self.orig_image.get_height()
        if self.y < 0 and self.y + self.h > surf_h:
            bottom = int((surf_h - self.y) / self.scale) + 1
        elif self.y >= 0 and self.h > surf_h:
            bottom = int(surf_h / self.scale) + 1

        return pygame.rect.Rect(left, top, right - left, bottom - top)

    def _getBlitOffset(self, cut_rect: Tuple[int, int, int, int]) -> Tuple[int, int]:
        x, y = cut_rect[:2]
        return (
            self.x + x * self.scale if self.x < 0 else 0,
            self.y + y * self.scale if self.y < 0 else 0
        )

    def getOrigSize(self) -> Tuple[int, int]:
        return (self._w, self._h)

    def setLight(self, gamma: float) -> None:
        if abs(gamma) < 1e-5:
            self.image = self.orig_image
        else:
            self.image = imgproc.mat2surface(
                imgproc.gammaTransformation(
                    imgproc.surface2mat(self.orig_image), gamma
                )
            )
        self.need_update_cut_surface = True

    def setCanvasView(self, scale: float, view_x: float, view_y: float) -> None:
        super().setCanvasView(scale, view_x, view_y)
        self.need_update_cut_surface = True

    def onResize(self, w, h, x, y):
        super().onResize(w, h, x, y)
        self.need_update_cut_surface = True

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if not self.need_update_cut_surface:
            surface.blit(self.cut_surface, self.blit_offset)
            return

        rect = self._getCutRect(surface)
        rect = ui.utils.clipRect(rect, self.image)
        self.blit_offset = self._getBlitOffset(rect)
        self.cut_surface = pygame.transform.scale(
            self.image.subsurface(rect),
            (int(rect[2] * self.scale),
             int(rect[3] * self.scale))
        )
        surface.blit(self.cut_surface, self.blit_offset)
        self.need_update_cut_surface = False