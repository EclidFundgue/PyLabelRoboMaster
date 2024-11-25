import time
from typing import List

from pygame import Surface as pg_Surface

from .. import pygame_gui as ui
from ..resources_loader import ImageLoader


class Clock(ui.components.BaseComponent):
    def __init__(self, x: int, y: int):
        self.number_width = 26
        self.number_height = 46
        self.marker_width = 6
        self.marker_height = 46
        self.padx = 8
        self.pady = 25

        w = 10 * self.number_width + 9 * self.padx
        h = 2 * self.number_height + self.pady
        super().__init__(w, h, x, y)

        loader = ImageLoader()
        self.numbers = [
            self.loadImage(
                loader['clock'][str(i)],
                self.number_width,
                self.number_height
            ) for i in range(10)
        ]

        self.sep = self.loadImage(
            loader['clock']['sep'],
            self.number_width, self.number_height
        )
        self.colon = self.loadImage(
            loader['clock']['colon'],
            self.marker_width, self.marker_height
        )

        # pen position for drawing
        self.pen = [self.x, self.y]

    def drawNumbers(self, surface: pg_Surface, numbers: str, pen: List[int]) -> None:
        for num in numbers:
            surface.blit(self.numbers[int(num)], pen)
            pen[0] += self.number_width + self.padx

    def draw(self, surface: pg_Surface) -> None:
        self.pen = [self.x, self.y]
        year, month, day, hour, minute, second = time.localtime()[:6]

        # hour:minute:second
        self.drawNumbers(surface, str(hour).zfill(2), self.pen)
        surface.blit(self.colon, self.pen)
        self.pen[0] += self.marker_width + self.padx
        self.drawNumbers(surface, str(minute).zfill(2), self.pen)
        surface.blit(self.colon, self.pen)
        self.pen[0] += self.marker_width + self.padx
        self.drawNumbers(surface, str(second).zfill(2), self.pen)

        self.pen[0] = self.x
        self.pen[1] += self.number_height + self.pady

        # year.month.day
        self.drawNumbers(surface, str(year), self.pen)
        surface.blit(self.sep, self.pen)
        self.pen[0] += self.number_width + self.padx
        self.drawNumbers(surface, str(month), self.pen)
        surface.blit(self.sep, self.pen)
        self.pen[0] += self.number_width + self.padx
        self.drawNumbers(surface, str(day), self.pen)