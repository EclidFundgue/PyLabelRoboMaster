from typing import Callable

import pygame

from .. import pygame_gui as ui


class PageHeaderBlock(ui.components.Selectable):
    '''
    PageHeaderBlock(w, h, x, y)

    Methods:
    * select() -> None
    * unselect() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int, text: str):
        super().__init__(w, h, x, y)

        color_theme = ui.color.LightColorTheme()

        self.text_color0 = color_theme.OnPrimaryContainer
        self.text_color1 = color_theme.PrimaryContainer # selected

        self.bg_color0 = ui.color.dark(color_theme.PrimaryContainer, 3)
        self.bg_color1 = ui.color.dark(self.bg_color0, 5) # hover
        self.bg_color2 = color_theme.OnPrimaryContainer # selected

        self.text_object = ui.components.Label(
            w, h, 0, 0,
            text=text,
            color=self.text_color0
        )
        self.addChild(self.text_object)

    def select(self):
        self.selected = True
        self.text_object.setColor(self.text_color1)

    def unselect(self):
        self.selected = False
        self.text_object.setColor(self.text_color0)

    def onMouseEnter(self):
        self.redraw()

    def onMouseLeave(self):
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.selected:
            surface.fill(self.bg_color2)
        elif self.active:
            surface.fill(self.bg_color1)
        else:
            surface.fill(self.bg_color0)

    def kill(self):
        self.text_object = None
        super().kill()

class PageHeader(ui.components.Base):
    '''
    PageHeader(w, h, x, y, on_page_change)
    * on_page_change(int) -> None

    Methods:
    * select(page) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_page_changed: Callable[[int], None] = None
    ):
        super().__init__(w, h, x, y)
        self.on_page_changed = ui.utils.getCallable(on_page_changed)
        self.current_page = 0

        self.block_0 = PageHeaderBlock(w//2, h, 0, 0, text='image')
        self.block_1 = PageHeaderBlock(w//2, h, w//2, 0, text='deserted')

        self.addChild(self.block_0)
        self.addChild(self.block_1)

        self.select(self.current_page)

    def select(self, page: int) -> None:
        self.current_page = self.current_page
        if page == 0:
            self.block_0.select()
            self.block_1.unselect()
        elif page == 1:
            self.block_0.unselect()
            self.block_1.select()
        else:
            pass

    def onLeftClick(self, x, y):
        if not self.active:
            return

        page = 1
        if self.block_0.active:
            page = 0
            self.on_page_changed(0)
        elif self.block_1.active:
            page = 1
            self.on_page_changed(1)
        self.select(page)

        self.redraw()

    def kill(self) -> None:
        self.on_page_changed = None
        self.block_0 = None
        self.block_1 = None
        super().kill()