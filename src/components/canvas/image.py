import os
from typing import Callable, Tuple

import cv2
import pygame
from pygame import Surface as pg_Surface

from ...resources_loader import ImageLoader
from ...utils.dataproc import mat2surface, surface2mat
from .canvas import CanvasComponent


class Image(CanvasComponent):
    '''
    Load image and display on canvas.

    Image(path, preproc_func)

    Methods:
    * scale(scale_rate, center) -> None
    * move(vx, vy) -> None
    * enableProc() -> None
    * disableProc() -> None
    * switchProc() -> None
    '''
    def __init__(self,
            path: str,
            canvas_size: Tuple[int, int],
            preproc_func: Callable[[cv2.Mat], cv2.Mat] = None):
        self.path = path
        self.canvas_size = canvas_size
        self.preproc_func = self._getPreprocFunc(preproc_func)
        self.enable_proc = False
        self.found: bool = False

        self._safeLoadImage(path)
        super().__init__(self.orig_w, self.orig_h, 0, 0)
        self.layer = -1 # image layer is behind all other components

        if self.found:
            self._updateDisplaySurface()

    def _getPreprocFunc(self, func: Callable[[cv2.Mat], cv2.Mat] = None) -> Callable[[cv2.Mat], cv2.Mat]:
        def _none(img: cv2.Mat) -> cv2.Mat:
            return img
        if func is None:
            return _none
        return func

    def _getPreprocImage(self) -> pg_Surface:
        return mat2surface(
            self.preproc_func(
                surface2mat(self.orig_image)
            )
        )

    def _safeLoadImage(self, img: str) -> None:
        ''' If path not found, load default image. '''
        if not os.path.exists(img):
            loader = ImageLoader()
            img = loader['other']['not_found']
            self.found = False
        else:
            self.found = True

        self.orig_image = self.loadImage(img)
        if self.found:
            self.proced_image = self._getPreprocImage()

        self.orig_w, self.orig_h = self.orig_image.get_size()

    def _updateDisplaySurface(self) -> None:
        '''
        Calculate display surface and position by:\n
            * self.x, self.y\n
            * self.w, self.h\n
            * self.scale_rate
        '''
        w, h = self.getDisplaySize()
        x, y = self.getDisplayPos()

        # if image is not too large, scale directly
        if w <= self.canvas_size[0] and h <= self.canvas_size[1]:
            if self.enable_proc:
                surf = pygame.transform.scale(self.proced_image, (w, h))
            else:
                surf = pygame.transform.scale(self.orig_image, (w, h))
            self.cut_rect_surface = surf
            self.cut_rect_pos = (x, y)
            return

        # cut the display part of image, then scale the small part
        cut_rect = self._getCutRect()
        if self.enable_proc:
            cut_surf = self.proced_image.subsurface(cut_rect)
        else:
            cut_surf = self.orig_image.subsurface(cut_rect)
        rect_w = int(cut_rect.w * self.scale)
        rect_h = int(cut_rect.h * self.scale)
        self.cut_rect_surface = pygame.transform.scale(cut_surf, (rect_w, rect_h))

        x += cut_rect.left * self.scale
        y += cut_rect.top * self.scale
        self.cut_rect_pos = (int(x), int(y))

    def _getCutRect(self):
        ''' Return a rect on original image to display. '''
        left, right = 0, self.orig_w
        top, bottom = 0, self.orig_h

        w, h = self.getDisplaySize()
        x, y = self.getDisplayPos()

        if x + w > self.canvas_size[0]:
            right = int((self.canvas_size[0] - x) / self.scale + 1)
        if y + h > self.canvas_size[1]:
            bottom = int((self.canvas_size[1] - y) / self.scale + 1)
        if x < 0:
            left = int(-x / self.scale - 1)
        if y < 0:
            top = int(-y / self.scale - 1)

        width = right - left
        height = bottom - top
        return pygame.rect.Rect(left, top, width, height)

    def enableProc(self) -> None:
        self.enable_proc = True
        self._updateDisplaySurface()

    def disableProc(self) -> None:
        self.enable_proc = False
        self._updateDisplaySurface()

    def switchProc(self) -> None:
        self.enable_proc = not self.enable_proc
        self._updateDisplaySurface()

    def onCanvasViewChanged(self, scale: float, view_x: float, view_y: float) -> None:
        super().onCanvasViewChanged(scale, view_x, view_y)
        self._updateDisplaySurface()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.cut_rect_surface, self.cut_rect_pos)