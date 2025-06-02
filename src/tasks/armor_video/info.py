from typing import Callable

from ... import pygame_gui as ui


class InfoButton(ui.components.Base):
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_show: Callable[[], None],
        on_hide: Callable[[], None]
    ):
        super().__init__(w, h, x, y)
        self.on_show = ui.utils.getCallable(on_show)
        self.on_hide = ui.utils.getCallable(on_hide)

        self.show = False
        self.image = ui.utils.loadImage('resources/icons/infomation.png', w * 0.9, h * 0.9, True)
        self.timer = ui.timer.ProgressTimer(0.3)

    def update(self, x, y, wheel):
        if self.active:
            if self.timer.isFinished() and not self.show:
                self.on_show()
                self.show = True
        else:
            self.timer.reset()
            if self.show:
                self.on_hide()
                self.show = False

    def draw(self, surface, x_start, y_start):
        w, h = self.image.get_size()
        x_offset = (self.w - w) // 2
        y_offset = (self.h - h) // 2
        surface.blit(self.image, (x_start + x_offset, y_start + y_offset))