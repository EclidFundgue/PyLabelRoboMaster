from typing import Callable, List, Union

from ... import pygame_gui as ui
from ...utils import imgproc
from .bar import ScrollBar
from .line import DesertedFileLine, ImageFileLine
from .line import _GenericFileLine as FileLine
from .lines import LinesBox


class ScrollView(ui.components.RectContainer):
    '''
    ScrollView(w, h, x, y, folder, on_selected, on_command, padding)
    * on_selected_changed(idx: int, line: FileLine) -> None
    * on_command(idx: int, line: FileLine) -> None

    Methods:
    * addLine(line: FileLine) -> None
    * deleteLine(line: FileLine) -> None
    * select(line: str) -> None
    * selectPrev() -> None
    * selectNext() -> None
    * selectLine(line) -> None
    * getSelectedLine() -> FileLine | None
    * getFileNumber() -> int
    * getSelectedIndex() -> int
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        line_w: int, line_h: int,
        folder: str,
        on_select: Callable[[int, FileLine], None] = None,
        on_command: Callable[[int, FileLine], None] = None
    ):
        super().__init__(w, h, x, y)

        self.folder = folder

        self.on_select: Callable[[int, FileLine], None] = ui.utils.getCallable(on_select)
        self.on_command: Callable[[int, FileLine], None] = ui.utils.getCallable(on_command)

        self.lines = LinesBox(
            line_w, h, 0, 0,
            self._loadFileLines(line_w, line_h, folder),
            on_relative_changed=self._onLinesBoxRelativeChanged,
            on_selected_changed=self._onSelected
        )
        self.bar = ScrollBar(15, h, w - 15, 0, self._onScrollBarRelativeChanged)

        self.addChild(self.lines)
        self.addChild(self.bar)

    def _getOnCommandFunc(self, line: FileLine):
        def ret():
            self.on_command(self.lines.index(line), line)
        return ret

    def _loadFileLines(self, w: int, h: int, folder: str) -> List[FileLine]:
        ''' Create file lines. Need to be implemented in subclass. '''
        raise NotImplementedError()

    def _onLinesBoxRelativeChanged(self, r: float):
        self.bar.setRelative(r)

    def _onScrollBarRelativeChanged(self, r: float):
        self.lines.setRelativeWithoutSmooth(r)

    def _onSelected(self, idx: int, line: FileLine) -> None:
        self.on_select(idx, line)

    def addLine(self, line: FileLine) -> None:
        self.lines.add(line)
        line.command = self._getOnCommandFunc(line)

    def deleteLine(self, line: FileLine) -> None:
        self.lines.delete(line)

    def select(self, line: str) -> None:
        self.lines.select(line)

    def selectPrev(self) -> None:
        self.lines.selectPrev()

    def selectNext(self) -> None:
        self.lines.selectNext()
    
    def selectLine(self, line: Union[int, str]) -> None:
        self.lines.select(line)

    def getSelectedLine(self) -> Union[FileLine, None]:
        return self.lines.getSelectedLine()
    
    def getFileNumber(self) -> int:
        return len(self.lines.lines)

    def getSelectedIndex(self) -> int:
        return self.lines.index(self.lines.getSelectedLine())

    def kill(self) -> None:
        self.on_select = None
        self.on_command = None
        self.lines = None
        self.bar = None
        super().kill()

class ImageScrollView(ScrollView):
    '''
    ImageScrollView(w, h, x, y, folder, on_selected, on_desert, padding)
    * on_selected_changed(idx: int, line: FileLine) -> None
    * on_desert(idx: int, line: FileLine) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        line_w: int, line_h: int,
        folder: str,
        on_select: Callable[[int, ImageFileLine], None] = None,
        on_desert: Callable[[int, ImageFileLine], None] = None
    ):
        self.on_desert = ui.utils.getCallable(on_desert)

        super().__init__(
            w, h, x, y,
            line_w, line_h,
            folder,
            on_select=on_select,
            on_command=self._onDesert
        )

    def _onDesert(self, idx: int, line: ImageFileLine) -> None:
        self.on_desert(idx, line)

    def _loadFileLines(self, w: int, h: int, folder: str) -> List[ImageFileLine]:
        ''' Create file lines. '''
        ret = [ImageFileLine(w, h, filename) for filename in imgproc.getImageFiles(folder)]
        for line in ret:
            line.command = self._getOnCommandFunc(line)
        return ret
    
    def addLine(self, line: FileLine):
        if isinstance(line, DesertedFileLine):
            line = ImageFileLine(*line.getRect()[:2], line.filename)
        super().addLine(line)

    def kill(self) -> None:
        self.on_desert = None
        super().kill()

class DesertedScrollView(ScrollView):
    '''
    DesertedScrollView(w, h, x, y, folder, on_select, on_restore, padding)
    * on_selected_changed(idx: int, line: FileLine) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        line_w: int, line_h: int,
        folder: str,
        on_select: Callable[[int, DesertedFileLine], None] = None,
        on_restore: Callable[[int, DesertedFileLine], None] = None
    ):
        self.on_restore = ui.utils.getCallable(on_restore)

        super().__init__(
            w, h, x, y,
            line_w, line_h,
            folder,
            on_select=on_select,
            on_command=self._onRestore
        )

    def _onRestore(self, idx: int, line: DesertedFileLine) -> None:
        self.on_restore(idx, line)

    def _loadFileLines(self, w: int, h: int, folder: str) -> List[DesertedFileLine]:
        ''' Create file lines. '''
        ret = [DesertedFileLine(w, h, filename) for filename in imgproc.getImageFiles(folder)]
        for line in ret:
            line.command = self._getOnCommandFunc(line)
        return ret

    def addLine(self, line: FileLine):
        if isinstance(line, ImageFileLine):
            line = DesertedFileLine(*line.getRect()[:2], line.filename)
        super().addLine(line)

    def kill(self) -> None:
        self.on_restore = None
        super().kill()