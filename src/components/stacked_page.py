from typing import List, Union

from .. import pygame_gui as ui
from ..pygame_gui import logger


class StackedPage(ui.components.RectContainer):
    '''
    A stacked page is a surface that can be added to a StackedPageView.

    StackedPage(w, h, x, y)

    Methods:
    * setPage(page_index) -> None
    * onShow() -> None
    * onHide() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)

        # this will be set by the StackedPageView when it's added.
        self._StackedPageView_set = None

    def setPage(self, page: Union[int, 'StackedPage'], redraw: bool = False) -> None:
        ''' Set the current page of the stacked page view. '''
        if self._StackedPageView_set is None:
            logger.warning("It should be added to a StackedPageView before setting the page.", self)
        self._StackedPageView_set(page, redraw)

    def onShow(self) -> None: ...
    def onHide(self) -> None: ...

class StackedPageView(ui.components.RectContainer):
    '''Methods:
    * setPage(page: int | StackedPage) -> None
    * addPage(page: StackedPage) -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int):
        super().__init__(w, h, x, y)

        self.pages: List[StackedPage] = []
        self.current_page_index = -1

    def _setPageByIndex(self, page_index: int) -> None:
        if page_index < 0 or page_index >= len(self.pages):
            logger.warning("Invalid page index.", self)
            return

        if self.current_page_index >= 0:
            self.pages[self.current_page_index].onHide()
            self.removeChild(self.pages[self.current_page_index])
        self.current_page_index = page_index
        self.addChild(self.pages[self.current_page_index])

    def _setPageByPage(self, page: StackedPage) -> None:
        if page not in self.pages:
            logger.warning("Page not in stacked pages.", self)
            return

        self._setPageByIndex(self.pages.index(page))

    def setPage(self, page: Union[int, StackedPage], redraw: bool = False) -> None:
        if isinstance(page, int):
            self._setPageByIndex(page)
        elif isinstance(page, StackedPage):
            self._setPageByPage(page)
        else:
            logger.error("Invalid page type.", TypeError, self)
        if redraw:
            self.redraw()

    def addPage(self, page: StackedPage) -> None:
        self.pages.append(page)
        page._StackedPageView_set = self.setPage

    def kill(self) -> None:
        if self.current_page_index >= 0:
            self.pages[self.current_page_index].onHide()

        for page in self.pages:
            page.kill()
        self.pages = None

        super().kill()