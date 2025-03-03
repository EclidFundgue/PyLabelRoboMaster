from typing import Callable, List, Union

from .. import pygame_gui as ui
from ..utils import imgproc
from .line import DesertedFileLine, FileLine, ImageFileLine

BAR_WIDTH = 20
BAR_PAD = 15
LINE_HEIGHT = 50

class FileBox(ui.components.RectContainer):
    '''
    FileBox(
        w, h, x, y,
        folder,
        initial_lines,
        on_file_selected
    )

    Methods:
    * getSelected() -> FileLine | None
    * getSelectedIndex() -> int
    * reload(lines) -> None
    * selectPrev() -> None
    * selectNext() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        initial_lines: List[FileLine],
        on_file_selected: Callable[[str], None] = None,
    ):
        super().__init__(w, h, x, y)
        self.folder = folder
        self.on_file_selected = ui.utils.getCallable(on_file_selected)

        self.listbox = ui.components.ListBox(
            w=w-BAR_WIDTH-BAR_PAD,
            h=h,
            x=0,
            y=0,
            lines=initial_lines,
            on_relative_change=self._onListboxRelativeChange
        )
        self.bar = ui.components.ScrollBar(
            w=BAR_WIDTH,
            h=h,
            x=w-BAR_WIDTH,
            y=0,
            on_drag=self._onBarDrag
        )

        self.addChild(self.listbox)
        self.addChild(self.bar)

    def __len__(self) -> int:
        return len(self.listbox)

    def _onListboxRelativeChange(self, r: float) -> None:
        self.bar.setRelative(r)
        self.bar.redraw()

    def _onBarDrag(self, r: float) -> None:
        self.listbox.setRelative(r, False)
        self.listbox.redraw()

    def _onFileSelected(self, line: FileLine) -> None:
        self.listbox.select(line)
        self.listbox.redraw()
        self.on_file_selected(line.filename)

    def getSelected(self) -> Union[FileLine, None]:
        return self.listbox.getSelected()

    def getSelectedIndex(self) -> int:
        return self.listbox.getSelectedIndex()

    def reload(self, lines: List[FileLine]) -> None:
        self.removeChild(self.listbox)

        self.listbox.kill()
        self.listbox = ui.components.ListBox(
            w=self.w-BAR_WIDTH-BAR_PAD,
            h=self.h,
            x=0,
            y=0,
            lines=lines,
            on_relative_change=self._onListboxRelativeChange
        )

        self.addChild(self.listbox)

    def selectPrev(self) -> None:
        self.listbox.selectPrev()

    def selectNext(self) -> None:
        self.listbox.selectNext()

    def kill(self) -> None:
        self.on_file_selected = None
        self.listbox = None
        self.bar = None
        super().kill()

class ImageFileBox(FileBox):
    '''
    ImageFileBox(
        w, h, x, y,
        folder,
        on_file_selected,
        on_file_deserted
    )

    Methods:
    * getSelected() -> FileLine | None
    * reload() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_deserted: Callable[[str], None] = None
    ):
        self.on_file_deserted = ui.utils.getCallable(on_file_deserted)
        super().__init__(
            w, h, x, y,
            folder=folder,
            initial_lines=self._getLines(w, folder),
            on_file_selected=on_file_selected
        )

    def _getLines(self, width: int, folder: str) -> List[ImageFileLine]:
        lines = [
            ImageFileLine(
                w=width-BAR_WIDTH-BAR_PAD,
                h=LINE_HEIGHT,
                filename=filename,
                on_selected=self._onFileSelected,
                on_delete=self.__onDeserted
            ) for filename in imgproc.getImageFiles(folder)
        ]
        lines.sort(key=lambda l: l.filename)
        return lines

    def __onDeserted(self, line: ImageFileLine):
        self.listbox.delete(line)
        self.listbox.redraw()
        self.on_file_deserted(line.filename)

    def reload(self) -> None:
        super().reload(self._getLines(self.w, self.folder))

    def kill(self) -> None:
        self.on_file_deserted = None
        super().kill()

class DesertedFileBox(FileBox):
    '''
    DesertedFileBox(
        w, h, x, y,
        folder,
        on_file_selected,
        on_file_restored
    )

    Methods:
    * reload() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_restored: Callable[[str], None] = None
    ):
        self.on_file_restored = ui.utils.getCallable(on_file_restored)
        super().__init__(
            w, h, x, y,
            folder=folder,
            initial_lines=self._getLines(w, folder),
            on_file_selected=on_file_selected
        )

    def _getLines(self, width: int, folder: str) -> List[DesertedFileLine]:
        lines = [
            DesertedFileLine(
                w=width-BAR_WIDTH-BAR_PAD,
                h=LINE_HEIGHT,
                filename=filename,
                on_selected=self._onFileSelected,
                on_restore=self.__onRestored
            ) for filename in imgproc.getImageFiles(folder)
        ]
        lines.sort(key=lambda l: l.filename)
        return lines

    def __onRestored(self, line: DesertedFileLine):
        self.listbox.delete(line)
        self.listbox.redraw()
        self.on_file_restored(line.filename)

    def reload(self) -> None:
        super().reload(self._getLines(self.w, self.folder))

    def kill(self) -> None:
        self.on_file_restored = None
        super().kill()