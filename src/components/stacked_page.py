from typing import List, Union

from .. import pygame_gui as ui


class StackedPage(ui.components.RectContainer):
    '''
    A stacked page is a surface that can be added to a StackedPageView.

    StackedPage(w, h, x, y)

    Methods:
    * setPage(page_index) -> None
    * onShow() -> None
    * onHide() -> None
    '''
    def __init__(self, w: int, h: int, x: int = 0, y: int = 0):
        super().__init__(w, h, x, y)

        # this will be set by the StackedPageView when it's added.
        self._StackedPageView_set = None

    def setPage(self, page: Union[int, 'StackedPage'], redraw: bool = False) -> None:
        ''' Set the current page of the stacked page view. '''
        if self._StackedPageView_set is None:
            ui.logger.warning("It should be added to a StackedPageView before setting the page.", self)
        self._StackedPageView_set(page, redraw)

    def onShow(self) -> None: ...
    def onHide(self) -> None: ...

class StackedPageView(ui.components.RectContainer):
    '''Methods:
    * setPage(page: int | StackedPage) -> None
    * addPage(page: StackedPage) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        pages: List[StackedPage] = None
    ):
        super().__init__(w, h, x, y)

        self.pages: List[StackedPage] = [] if pages is None else pages
        self.current_page_index = -1

    def _setPageByIndex(self, page_index: int) -> None:
        if page_index < 0 or page_index >= len(self.pages):
            ui.logger.warning("Invalid page index.", self)
            return

        if self.current_page_index >= 0:
            self.pages[self.current_page_index].onHide()
            self.removeChild(self.pages[self.current_page_index])
        self.current_page_index = page_index
        self.pages[self.current_page_index].onShow()
        self.addChild(self.pages[self.current_page_index])

    def _setPageByPage(self, page: StackedPage) -> None:
        if page not in self.pages:
            ui.logger.warning("Page not in stacked pages.", self)
            return

        self._setPageByIndex(self.pages.index(page))

    def setPage(self, page: Union[int, StackedPage], redraw: bool = False) -> None:
        if isinstance(page, int):
            self._setPageByIndex(page)
        elif isinstance(page, StackedPage):
            self._setPageByPage(page)
        else:
            ui.logger.error("Invalid page type.", TypeError, self)
        if redraw:
            self.redraw()

    def addPage(self, page: StackedPage) -> None:
        self.pages.append(page)
        page._StackedPageView_set = self.setPage

    def onResize(self, w, h, x, y):
        w_ratio = w / self.w
        h_ratio = h / self.h
        for page in self.pages:
            page.onResize(
                int(page.w * w_ratio),
                int(page.h * h_ratio),
                int(page.x * w_ratio),
                int(page.y * h_ratio)
            )
        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def kill(self) -> None:
        if self.current_page_index >= 0:
            self.pages[self.current_page_index].onHide()

        for page in self.pages:
            page.kill()
        self.pages = None

        super().kill()