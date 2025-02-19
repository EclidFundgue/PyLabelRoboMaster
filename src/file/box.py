from typing import Callable, List

from .. import pygame_gui as ui
from ..utils import imgproc
from .line import DesertedFileLine, FileLine, ImageFileLine

BAR_WIDTH = 20
BAR_PAD = 15
LINE_HEIGHT = 50

class FileBox(ui.components.RectContainer):
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        initial_lines: List[FileLine],
        on_file_selected: Callable[[str], None] = None,
    ):
        super().__init__(w, h, x, y)
        self.folder = folder
        self.on_file_selected = ui.utils.getCallable(on_file_selected)

        def on_r_change(r: float):
            self.bar.setRelative(r)
            self.bar.redraw()
        self.listbox = ui.components.ListBox(
            w=w-BAR_WIDTH-BAR_PAD,
            h=h,
            x=0,
            y=0,
            lines=initial_lines,
            on_relative_change=on_r_change
        )

        def on_drag(r: float):
            self.listbox.setRelative(r, False)
            self.listbox.redraw()
        self.bar = ui.components.ScrollBar(
            w=BAR_WIDTH,
            h=h,
            x=w-BAR_WIDTH,
            y=0,
            on_drag=on_drag
        )

        self.addChild(self.listbox)
        self.addChild(self.bar)

    def _onFileSelected(self, line: FileLine) -> None:
        self.listbox.select(line)
        self.listbox.redraw()
        self.on_file_selected(line.filename)

class ImageFileBox(FileBox):
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_deserted: Callable[[str], None] = None
    ):
        self.on_file_deserted = ui.utils.getCallable(on_file_deserted)

        def on_deserted(line: ImageFileLine):
            self.listbox.delete(line)
            self.listbox.redraw()
            self.on_file_deserted(line.filename)
        lines = [
            ImageFileLine(
                w=w-BAR_WIDTH-BAR_PAD,
                h=LINE_HEIGHT,
                filename=filename,
                on_selected=self._onFileSelected,
                on_delete=on_deserted
            ) for filename in imgproc.getImageFiles(folder)
        ]
        super().__init__(w, h, x, y, folder, lines, on_file_selected)

class DesertedFileBox(FileBox):
    def __init__(self,
        w: int, h: int, x: int, y: int,
        folder: str,
        on_file_selected: Callable[[str], None] = None,
        on_file_restored: Callable[[str], None] = None
    ):
        self.on_file_restored = ui.utils.getCallable(on_file_restored)

        def on_restored(line: ImageFileLine):
            self.listbox.delete(line)
            self.listbox.redraw()
            self.on_file_restored(line.filename)
        lines = [
            DesertedFileLine(
                w=w-BAR_WIDTH-BAR_PAD,
                h=LINE_HEIGHT,
                filename=filename,
                on_selected=self._onFileSelected,
                on_restore=on_restored
            ) for filename in imgproc.getImageFiles(folder)
        ]
        super().__init__(w, h, x, y, folder, lines, on_file_selected)