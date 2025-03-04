import time

import pygame

from .. import pygame_gui as ui


class Clock(ui.components.Base):
    def __init__(self, x: int, y: int):
        w = 24
        h = 50
        super().__init__(8 * w, h, x, y)

        font = pygame.font.SysFont('microsoft yahei bold', 50)

        self.h0 = ui.components.Label(w, h, 0, 0, '0', font)
        self.h1 = ui.components.Label(w, h, w, 0, '0', font)
        self.m0 = ui.components.Label(w, h, 3 * w, 0, '0', font)
        self.m1 = ui.components.Label(w, h, 4 * w, 0, '0', font)
        self.s0 = ui.components.Label(w, h, 6 * w, 0, '0', font)
        self.s1 = ui.components.Label(w, h, 7 * w, 0, '0', font)

        texts = [
            self.h0, self.h1,
            ui.components.Label(w, h, 2 * w, 0, ':', font),
            self.m0, self.m1,
            ui.components.Label(w, h, 5 * w, 0, ':', font),
            self.s0, self.s1,
        ]
        for text in texts:
            text.setAlignment(ui.constants.ALIGN_CENTER, ui.constants.ALIGN_CENTER)
            self.addChild(text)

        self.time_seconds: int = 0

    def _setCurrentTime(self) -> None:
        hour, minute, second = time.localtime()[3:6]
        self.h0.setText(str(hour).zfill(2)[0])
        self.h1.setText(str(hour).zfill(2)[1])
        self.m0.setText(str(minute).zfill(2)[0])
        self.m1.setText(str(minute).zfill(2)[1])
        self.s0.setText(str(second).zfill(2)[0])
        self.s1.setText(str(second).zfill(2)[1])

    def update(self, x, y, wheel) -> None:
        if self.time_seconds!= int(time.time()):
            self.time_seconds = int(time.time())
            self._setCurrentTime()
            self.redraw()