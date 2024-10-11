from typing import Callable

import pygame

from ..components.clock import Clock
from ..pygame_gui import Surface, TextButton, getCallable


class MainMenu(Surface):
    def __init__(self,
            w: int, h: int, x: int, y: int,
            on_change_labeling: Callable[[], None] = None,
            on_change_setting: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        self.on_change_labeling = getCallable(on_change_labeling)
        self.on_change_setting = getCallable(on_change_setting)

        text_font = pygame.font.SysFont('simsun', 30)

        # labeling button
        btn_labeling = TextButton(
            300, 50, 50, 50,
            text='Label',
            font=text_font,
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeLabeling,
            cursor_change=True
        )
        self.addChild(btn_labeling)

        # setting button
        btn_setting = TextButton(
            300, 50, 50, 120,
            text='Setting',
            font=text_font,
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeSetting,
            cursor_change=True
        )
        self.addChild(btn_setting)

        # clock
        clock = Clock(20, 700)
        self.addChild(clock)

        # background
        self.setBackgroundColor((17, 45, 78))

    def _onPageChangeLabeling(self) -> None:
        self.on_change_labeling()

    def _onPageChangeSetting(self) -> None:
        self.on_change_setting()