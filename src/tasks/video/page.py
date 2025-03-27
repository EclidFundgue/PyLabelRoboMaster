from ... import pygame_gui as ui
from ...components.stacked_page import StackedPage


class VideoValidatePage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        self.setBackgroundColor((255, 255, 255))

        color_theme = ui.color.LightColorTheme()
        self.button_back = ui.components.CloseButton(
            w=int(40*1.5),
            h=40,
            x=w-int(40*1.5),
            y=0,
            color=ui.color.dark(color_theme.Surface,3),
            cross_color=color_theme.OnSurface,
            on_press=lambda : self.setPage(page_incides['main_menu'], True)
        )

        self.addChild(self.button_back)

    def onHide(self):
        self.button_back.resetState()