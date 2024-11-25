from typing import Callable, List

from ... import pygame_gui as ui
from ...global_vars import VarArmorLabels
from .line import DesertedFileLine, ImageFileLine, TextImage
from .line import _GenericFileLine as FileLine
from .scrollview import DesertedScrollView, ImageScrollView, ScrollView


class _Header(ui.components.RectContainer, ui.components.Selectable):
    '''
    _Header(w, h, x, y, text, on_select)
    * on_select() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int,
                 text: str,
                 on_select: Callable[[], None] = None):
        ui.components.RectContainer.__init__(self, w, h, x, y)
        self.selected = False

        color_theme = ui.LightColorTheme()

        self.text = text
        self.text_image = TextImage(text, color_theme.OnPrimaryContainer)
        self.pressed_text_image = TextImage(text, color_theme.PrimaryContainer)
        self.on_select = ui.getCallable(on_select)

        self._alignText(self.text_image)
        self._alignText(self.pressed_text_image)

        self.bg_color = color_theme.PrimaryContainer
        self.bg_color_hover = (self.bg_color[0] - 15, self.bg_color[1] - 29, self.bg_color[2] - 6)
        self.bg_color_selected = color_theme.OnPrimaryContainer

        self.addChild(self.text_image)

    def _alignText(self, text_image: TextImage) -> None:
        text_image.x = (self.w - text_image.w) // 2
        text_image.y = (self.h - text_image.h) // 2

    def kill(self) -> None:
        self.text_image = None
        self.on_select = None
        super().kill()

    def select(self) -> None:
        self.removeChild(self.text_image)
        self.addChild(self.pressed_text_image)
        super().select()
    
    def unselect(self) -> None:
        self.removeChild(self.pressed_text_image)
        self.addChild(self.text_image)
        super().unselect()

    def update(self, events=None) -> None:
        super().update(events)

        if self.selected:
            self.setBackgroundColor(self.bg_color_selected)
        elif self.active:
            self.setBackgroundColor(self.bg_color_hover)
        else:
            self.setBackgroundColor(self.bg_color)

    def onLeftClick(self, x: int, y: int) -> None:
        self.on_select()

class _StackHeader(ui.components.RectContainer):
    '''
    _StackedHeader(w, h, x, y)
    * on_page_changed(idx: int) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int,
                 on_page_changed: Callable[[int], None] = None):
        super().__init__(w, h, x, y)
        self.on_page_changed = ui.getCallable(on_page_changed)

        def on_select_0() -> None:
            if self.current_page == 1:
                self.current_page = 0
                self.header_0.select()
                self.header_1.unselect()
                self.on_page_changed(0)
        def on_select_1() -> None:
            if self.current_page == 0:
                self.current_page = 1
                self.header_0.unselect()
                self.header_1.select()
                self.on_page_changed(1)
        self.header_0 = _Header(w // 2, h, 0, 0, 'image', on_select_0)
        self.header_1 = _Header(w // 2, h, w // 2, 0, 'deserted', on_select_1)

        self.current_page = 0
        self.header_0.select()

        self.addChild(self.header_0)
        self.addChild(self.header_1)

    def kill(self) -> None:
        self.on_page_changed = None
        self.header_0 = None
        self.header_1 = None
        super().kill()

class StackedScrollView(ui.components.RectContainer):
    '''
    page0: ImageScrollView

    page1: DesertedScrollView

    StackedScrollView(
        w, h, x, y,
        line_w, line_h,
        folder,
        on_page_changed,
        on_select,
        on_desert,
        on_restore,
        padding
    )
    * on_page_changed(idx: int) -> None
    * on_selected_changed(idx: int, line: FileLine) -> None
    * on_desert(idx: int, line: ImageFileLine) -> None
    * on_restore(idx: int, line: DesertedFileLine) -> None

    Methods:
    * addLine(page: int, line: FileLine) -> None
    * deleteLine(page: int, line: FileLine) -> None
    * selectPrev() -> None
    * selectNext() -> None
    * getCurrentPageFileNumber() -> int
    * reloadByGlobalVar() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int,
            line_w: int, line_h: int,
            image_folder: str,
            deserted_folder: str,
            on_page_changed: Callable[[int], None] = None,
            on_select: Callable[[int, FileLine], None] = None,
            on_desert: Callable[[int, ImageFileLine], None] = None,
            on_restore: Callable[[int, DesertedFileLine], None] = None,
            padding: int = 300):
        super().__init__(w + padding, h + 2 * padding, x, y - padding)

        self.header_height = 30
        self.header = _StackHeader(
            line_w, self.header_height, 0, padding,
            self._onPageChanged
        )

        self.on_page_changed = ui.getCallable(on_page_changed)

        self.pages: List[ScrollView] = [
            ImageScrollView(
                w, h - self.header_height,
                0, padding + self.header_height,
                line_w, line_h,
                image_folder,
                on_select,
                on_desert,
                padding
            ),
            DesertedScrollView(
                w, h - self.header_height,
                0, padding + self.header_height,
                line_w, line_h,
                deserted_folder,
                on_select,
                on_restore,
                padding
            )
        ]

        self.addChild(self.header)
        self.addChild(self.pages[self.header.current_page])

    def _onPageChanged(self, idx: int) -> None:
        self.removeChild(self.pages[1 - idx])
        self.addChild(self.pages[idx])
        self.header.current_page = idx
        self.on_page_changed(idx)

    def addLine(self, page: int, line: FileLine) -> None:
        self.pages[page].addLine(line)

    def deleteLine(self, page: int, line: FileLine) -> None:
        self.pages[page].deleteLine(line)

    def selectPrev(self) -> None:
        var = VarArmorLabels()
        curr_page = self.pages[var.curr_page]
        curr_page.selectPrev()
        var.select(curr_page.getSelectedLine().filename)

    def selectNext(self) -> None:
        var = VarArmorLabels()
        curr_page = self.pages[var.curr_page]
        curr_page.selectNext()
        var.select(curr_page.getSelectedLine().filename)

    def getCurrentPageFileNumber(self) -> int:
        return self.pages[self.header.current_page].getFileNumber()

    def reloadByGlobalVar(self) -> None:
        var = VarArmorLabels()
        if var.selected_image is not None:
            self.pages[0].select(var.selected_image)

    def kill(self) -> None:
        self.header = None
        self.on_page_changed = None

        for page in self.pages:
            page.kill()
        self.pages = None

        super().kill()