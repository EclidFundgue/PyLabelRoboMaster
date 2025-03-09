import os
from typing import Callable, Union

from .. import pygame_gui as ui
from ..components.stacked_page import StackedPage, StackedPageView
from .box import DesertedFileBox, FileBox, ImageFileBox
from .navigator import Navigator
from .page_header import PageHeader


class _StackedFileBox(StackedPage):
    '''
    _StackedFileBox(w, h, box)

    Methods:
    * getSelected() -> str | None
    * getSelectedIndex() -> int
    * reload() -> None
    * select(file_idx) -> None
    * selectPrev() -> None
    * selectNext() -> None
    '''
    def __init__(self, w: int, h: int, box: FileBox):
        super().__init__(w, h)

        self.box = box
        self.addChild(box)

    def __len__(self) -> int:
        return len(self.box)

    def getSelected(self) -> Union[str, None]:
        line = self.box.getSelected()
        if line is not None:
            return line.getFilename()
        return line
    
    def getSelectedIndex(self) -> int:
        return self.box.getSelectedIndex()

    def reload(self) -> None:
        self.box.reload()

    def select(self, file_idx: int) -> None:
        self.box.select(file_idx)

    def selectPrev(self) -> None:
        self.box.selectPrev()

    def selectNext(self) -> None:
        self.box.selectNext()

    def kill(self) -> None:
        self.box = None
        super().kill()

class StackedImageFileBox(_StackedFileBox):
    def __init__(self,
        w: int, h: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_deserted: Callable[[str], None] = None
    ):
        super().__init__(
            w, h, ImageFileBox(
                w, h, 0, 0,
                folder,
                on_file_selected,
                on_file_deserted
            )
        )

class StackedDesertedFileBox(_StackedFileBox):
    def __init__(self,
        w: int, h: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_restored: Callable[[str], None] = None
    ):
        super().__init__(
            w, h, DesertedFileBox(
                w, h, 0, 0,
                folder,
                on_file_selected,
                on_file_restored
            )
        )

class SelectionBox(ui.components.RectContainer):
    '''
    SelectionBox(
        w, h, x, y,
        image_folder,
        deserted_folder,
        on_selected
    )
    * on_selected(folder, filename, is_deserted) -> None

    Methods:
    * getSelected() -> str | None
    * setPage(page) -> None
    * select(file_idx) -> None
    * selectPrev() -> None
    * selectNext() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        image_folder: str,
        deserted_folder: str,
        on_selected: Callable[[str, Union[str, None], bool], None] = None
    ):
        super().__init__(w, h, x, y)
        self.image_folder = image_folder
        self.deserted_folder = deserted_folder
        self.on_selected = ui.utils.getCallable(on_selected)

        navigator_h = 30
        header_w = w - 35
        header_h = 30

        def on_prev():
            self.selectPrev()
            self._onSelectNotify()
        def on_next():
            self.selectNext()
            self._onSelectNotify()
        self.navigator = Navigator(
            w=w,
            h=30,
            x=0,
            y=0,
            on_prev=on_prev,
            on_next=on_next
        )
        def on_page_change(page: int) -> None:
            self.file_box.setPage(page)
            self._onSelectNotify()
            self._updataNavigator()
        self.header = PageHeader(header_w, header_h, 0, navigator_h, on_page_change)

        def on_image_selected(filename: str):
            self.on_selected(self.image_folder, filename, False)
            self._updataNavigator()
        def on_image_deserted(filename: str):
            os.makedirs(self.deserted_folder, exist_ok=True)
            os.rename(
                os.path.join(self.image_folder, filename),
                os.path.join(self.deserted_folder, filename)
            )
            self.deserted_box.reload()
        self.image_box = StackedImageFileBox(
            w, h-navigator_h-header_h, image_folder,
            on_file_selected=on_image_selected,
            on_file_deserted=on_image_deserted
        )

        def on_deserted_selected(filename: str):
            self.on_selected(self.deserted_folder, filename, True)
            self._updataNavigator()
        def on_deserted_resotred(filename: str):
            os.makedirs(self.image_folder, exist_ok=True)
            os.rename(
                os.path.join(self.deserted_folder, filename),
                os.path.join(self.image_folder, filename)
            )
            self.image_box.reload()
        self.deserted_box = StackedDesertedFileBox(
            w, h-navigator_h-header_h, deserted_folder,
            on_file_selected=on_deserted_selected,
            on_file_restored=on_deserted_resotred
        )

        self.file_box = StackedPageView(
            w=w,
            h=h-navigator_h-header_h,
            x=0,
            y=navigator_h+header_h,
            pages=[self.image_box, self.deserted_box]
        )
        self.file_box.setPage(0)

        self.addChild(self.navigator)
        self.addChild(self.header)
        self.addChild(self.file_box)

        self._updataNavigator()
    
    def _onSelectNotify(self) -> None:
        page = self.file_box.current_page_index
        if page == 0: # image
            self.on_selected(
                self.image_folder,
                self.image_box.getSelected(),
                False
            )
        elif page == 1: # deserted
            self.on_selected(
                self.deserted_folder,
                self.deserted_box.getSelected(),
                True
            )

    def getSelected(self) -> Union[str, None]:
        box = self._getCurrentBox()
        return box.getSelected()

    def getSelectedIndex(self) -> int:
        box = self._getCurrentBox()
        idx = box.getSelectedIndex()
        return idx

    def setPage(self, page: Union[int, StackedPage]) -> None:
        self.file_box.setPage(page)

    def _getCurrentBox(self) -> _StackedFileBox:
        page_idx = self.file_box.current_page_index
        if page_idx == 0:
            return self.image_box
        if page_idx == 1:
            return self.deserted_box
        ui.logger.error(f'Invalid page_idx: {page_idx}')

    def _updataNavigator(self) -> None:
        box = self._getCurrentBox()
        filename = box.getSelected()
        idx = box.getSelectedIndex() + 1

        self.navigator.setInfo(
            file_name=filename if filename is not None else '-',
            index=idx if idx > 0 else '-',
            total_files=len(box)
        )

        self.navigator.redraw()

    def select(self, file_idx: int) -> None:
        box = self._getCurrentBox()
        box.select(file_idx)
        self._updataNavigator()

    def selectPrev(self) -> None:
        box = self._getCurrentBox()
        box.selectPrev()
        self._updataNavigator()

    def selectNext(self) -> None:
        box = self._getCurrentBox()
        box.selectNext()
        self._updataNavigator()

    def kill(self) -> None:
        self.on_selected = None 
        self.navigator = None
        self.header = None
        self.image_box = None
        self.deserted_box = None
        self.file_box = None
        super().kill()