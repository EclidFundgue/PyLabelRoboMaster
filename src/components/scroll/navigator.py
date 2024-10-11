from typing import Callable, Tuple

import pygame
from pygame import Surface as pg_Surface

from ...pygame_gui import Button, Surface, getCallable
from ...resources_loader import ImageLoader


class Navigator(Surface):
    '''
    Show current selected image filename and index infomation.

    Navigator(w, h, x, y, num, font_color)

    Methods:
    setInfomation(filename, idx, num) -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            num: int,
            font_color: Tuple[int, int, int],
            on_prev: Callable[[], None] = None,
            on_next: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        self.font_color = font_color
        self.font = pygame.font.SysFont('simsun', 13)
        self.on_prev = getCallable(on_prev)
        self.on_next = getCallable(on_next)

        self.filename_img = self.font.render('', False, self.font_color)
        self.index_img = self.font.render(f'0/{num}', False, self.font_color)

        loader = ImageLoader()
        btn_w = 16
        btn_h = 16
        self.btn_prev = Button(
            btn_w, btn_h, 0, (h - btn_h) // 2,
            loader['button']['arrow'],
            loader['button']['arrow_pressed'],
            on_press=self._onButtonPrev,
            continue_press=40,
            cursor_change=True
        )
        self.btn_next = Button(
            btn_w, btn_h, self.w - btn_w, (h - btn_h) // 2,
            pygame.transform.flip(loader['button']['arrow'], True, False),
            pygame.transform.flip(loader['button']['arrow_pressed'], True, False),
            on_press=self._onButtonNext,
            continue_press=40,
            cursor_change=True
        )

        self.padx = 15

        self.addChild(self.btn_prev)
        self.addChild(self.btn_next)

    def _onButtonPrev(self):
        self.on_prev()

    def _onButtonNext(self):
        self.on_next()

    def setInfomation(self, filename: str, idx: int, num: int) -> None:
        self.filename_img = self.font.render(filename, False, self.font_color)
        self.index_img = self.font.render(f'{idx + 1}/{num}', False, self.font_color)

    def kill(self) -> None:
        self.btn_prev = None
        self.btn_next = None
        self.on_prev = None
        self.on_next = None
        super().kill()

    def draw(self, surface: pg_Surface) -> None:
        self.clear()

        img_w, img_h = self.index_img.get_size()
        pady = (self.h - img_h) // 2
        self.pg_surface.blit(
            self.filename_img,
            (self.padx + self.btn_prev.w, pady)
        )
        self.pg_surface.blit(
            self.index_img,
            (self.w - self.padx - img_w - self.btn_next.w, pady)
        )

        for ch in self.child_components:
            ch.draw(self.pg_surface)

        surface.blit(self.pg_surface, (self.x, self.y))