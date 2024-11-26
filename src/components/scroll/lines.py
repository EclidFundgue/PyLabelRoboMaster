from typing import Callable, List, Tuple, Union

from ... import pygame_gui as ui
from ...pygame_gui import logger
from .line import _GenericFileLine as FileLine


class LinesBox(ui.components.RectContainer):
    '''
    Contains list of FileLine, display them by relative position.
    Automacically control position of each line, and handle mouse
    scroll and click event.

    LinesBox(w, h, x, y, lines, on_relative_changed, on_selected_changed)
    * on_relative_changed(r: float) -> None
    * on_selected_changed(idx: int, line: FileLine) -> None

    Method:
    * setRelativeWithSmooth(r) -> None
    * setRelativeWithoutSmooth(r) -> None
    * getRelative() -> float
    * getSelectedLine() -> FileLine | None
    * add(line) -> None
    * select(line) -> None
    * selectPrev() -> None
    * selectNext() -> None
    * getMinMaxRelative(line_idx) -> Tuple[float, float]
    * delete(line) -> None
    * index(line) -> int
    '''

    MOUSE_SCROLL_SPEED = 50

    def __init__(self, w: int, h: int, x: int, y: int,
                 lines: List[FileLine] = None,
                 on_relative_changed: Callable[[float], None] = None,
                 on_selected_changed: Callable[[int, FileLine], None] = None,
                 use_smooth_scroll: bool = True):
        super().__init__(w, h, x, y)

        self.lines = lines if lines is not None else []
        self.total_height, self.heights = self._getLinesHieghts(self.lines)
        self.child_top_idx = 0 # line_idx = child_idx + child_top_idx

        self.on_relative_changed: Callable[[float], None] = ui.getCallable(on_relative_changed)
        self.on_selected_changed: Callable[[int, FileLine], None] = ui.getCallable(on_selected_changed)

        self._bindWithLines(self.lines)

        self.selected_idx = -1
        self.selected_line = None

        smooth_time_period = 0.0
        if use_smooth_scroll:
            smooth_time_period = 0.2
        self.relative = ui.timer.TimedFloat(smooth_time_period, 0, ui.timer.INTERP_POLY2)
        self.current_relative_value = self.relative.getCurrentValue()
        self._updateRelativeView(self.current_relative_value)

    def _bindWithLines(self, lines: List[FileLine]):
        def get_on_select(_line: FileLine, orig_on_select: Callable):
            def _ret():
                orig_on_select()
                if self.selected_line != _line:
                    self._selectByLine(_line)
                    self.on_selected_changed(self.lines.index(_line), _line)
            return _ret

        for line in lines:
            line.on_select = get_on_select(line, line.on_select)

    def _getLinesHieghts(self, lines: List[FileLine]) -> Tuple[int, List[int]]:
        h_sum = 0
        h_ls = []
        for l in lines:
            h_ls.append(h_sum)
            h_sum += l.h
        h_sum = max(1, h_sum) # to avoid divide by zero
        return h_sum, h_ls

    def _getPixelOffset(self, r: float) -> int:
        offset = -int(r * (self.total_height - self.h))
        return min(offset, 0)

    def _searchDisplayRange(self, offset: int) -> Tuple[int, int]:
        ''' Return start_idx and end_idx of lines need to display '''
        start = 0
        end = len(self.lines) - 1
        
        while start < end:
            mid = (start + end) // 2

            if self.heights[mid] + offset < 0:
                start = mid
                continue

            if self.heights[mid] + self.lines[mid].h + offset >= self.h:
                end = mid
                continue

            return start, end

        return start, end

    def _updateChilds(self, offset: int, start_idx: int, end_idx: int):
        for i in range(start_idx, end_idx + 1):
            l = self.lines[i]
            l.x = 0
            l.y = self.heights[i] + offset
        self.child_components = self.lines[start_idx: end_idx + 1]
        self.child_top_idx = start_idx

    def _updateRelativeView(self, r: float) -> None:
        ''' Update childs position and display range. '''
        y_offset = self._getPixelOffset(r)
        start, end = self._searchDisplayRange(y_offset)
        self._updateChilds(y_offset, start, end)

    def setRelativeWithSmooth(self, r: float) -> None:
        if r < 0:
            r = 0
        elif r > 1:
            r = 1
        if abs(r - self.relative.getEndValue()) < 1e-6:
            return

        self.relative.setValue(r)
        self.current_relative_value = self.relative.getCurrentValue()

    def setRelativeWithoutSmooth(self, r: float) -> None:
        if r < 0:
            r = 0
        elif r > 1:
            r = 1
        if abs(r - self.relative.getEndValue()) < 1e-6:
            return

        self.relative.setValue(r, use_smooth=False)
        self.current_relative_value = self.relative.getCurrentValue()
        self._updateRelativeView(self.current_relative_value)
        self.on_relative_changed(self.current_relative_value)

    def getRelative(self) -> float:
        return self.current_relative_value

    def getSelectedLine(self) -> Union[FileLine, None]:
        return self.selected_line

    def add(self, line: FileLine) -> None:
        self.lines.append(line)
        self.lines.sort(key=lambda l: l.filename)

        def get_on_select(_line: FileLine, orig_on_select: Callable):
            def _ret():
                orig_on_select()
                if self.selected_line != _line:
                    self._selectByLine(_line)
                    self.on_selected_changed(self.lines.index(_line), _line)
            return _ret
        line.on_select = get_on_select(line, line.on_select)

        # update box
        self.removeDead()
        self.total_height, self.heights = self._getLinesHieghts(self.lines)
        self._updateRelativeView(self.current_relative_value)

        # update selected line index
        if self.selected_line is not None:
            self.selected_idx = self.lines.index(self.selected_line)

    def _selectByIndex(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.lines):
            logger.warning(f"Line index out of range: {idx}", self)
            return

        if idx == self.selected_idx:
            return

        l = self.lines[idx]

        if self.selected_idx == -1:
            l.select()
            self.selected_idx = idx
            self.selected_line = l
            return

        # idx != self.selected_idx
        self.lines[self.selected_idx].unselect()
        l.select()
        self.selected_idx = idx
        self.selected_line: FileLine = l

    def _selectByFilename(self, filename: str) -> None:
        for l in self.lines:
            if l.filename == filename:
                self._selectByLine(l)
                return

    def _selectByLine(self, line: FileLine) -> None:
        if line == self.selected_line:
            return

        idx = self.lines.index(line)
        self._selectByIndex(idx)

    def _constrainRelativeByIndex(self, idx: int) -> float:
        min_r, max_r = self.getMinMaxRelative(idx)
        if self.relative.getEndValue() < min_r:
            self.setRelativeWithSmooth(min_r)
        elif self.relative.getEndValue() > max_r:
            self.setRelativeWithSmooth(max_r)

    def select(self, line: Union[int, str, FileLine]) -> None:
        '''
        Select line with given index. If there is already a selected line,
        unselect it first.
        '''

        if isinstance(line, int):
            self._selectByIndex(line)
        elif isinstance(line, str):
            self._selectByFilename(line)
        elif isinstance(line, FileLine):
            self._selectByLine(line)
        else:
            logger.warning(f"Invalid line type: {type(line)}", self)

        self._constrainRelativeByIndex(self.selected_idx)

    def selectPrev(self) -> None:
        if self.selected_idx == -1:
            self._selectByIndex(len(self.lines) - 1)
        else:
            self._selectByIndex(
                (self.selected_idx + len(self.lines) - 1) % len(self.lines)
            )
        self._constrainRelativeByIndex(self.selected_idx)

    def selectNext(self) -> None:
        if self.selected_idx == -1:
            self._selectByIndex(0)
        else:
            self._selectByIndex((self.selected_idx + 1) % len(self.lines))
        self._constrainRelativeByIndex(self.selected_idx)

    def getMinMaxRelative(self, line_idx: int) -> Tuple[float, float]:
        ''' relative position range that makes this line within view '''
        line_top = self.heights[line_idx]
        line_bottom = line_top + self.lines[line_idx].h

        min_r = (line_bottom - self.h) / max(self.total_height - self.h, 1e-6)
        min_r = min(max(min_r, 0), 1)
        max_r = min(line_top / max(self.total_height - self.h, 1e-6), 1)

        return [min_r, max_r]

    def _deleteByIndex(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.lines):
            logger.warning(f"Line index out of range: {idx}", self)
            return

        # remove line from list
        self.lines[idx].kill()
        self.lines.pop(idx)

        # delete selected line
        if self.selected_idx == idx:
            self.selected_idx = -1
            self.selected_line = None

        # update box
        self.removeDead()
        self.total_height, self.heights = self._getLinesHieghts(self.lines)
        self._updateRelativeView(self.current_relative_value)

        # update selected line index
        if self.selected_line is not None:
            self.selected_idx = self.lines.index(self.selected_line)

    def _deleteByLine(self, line: FileLine) -> None:
        idx = self.lines.index(line)
        self._deleteByIndex(idx)

    def delete(self, line: Union[int, FileLine]) -> None:
        ''' Delete line with given index. '''

        if isinstance(line, int):
            self._deleteByIndex(line)
        elif isinstance(line, FileLine):
            self._deleteByLine(line)
        else:
            logger.warning(f"Invalid line type: {type(line)}", self)

    def index(self, line: FileLine) -> int:
        '''
        Return index of given line in lines list.
        Return -1 on failure.
        '''
        if line not in self.lines:
            return -1
        return self.lines.index(line)

    def kill(self) -> None:
        for l in self.lines:
            l.kill()
        self.lines = None
        self.selected_line = None
        self.on_relative_changed = None
        self.on_selected_changed = None
        super().kill()

    def update(self, events=None) -> None:
        super().update(events)

        if abs(self.current_relative_value - self.relative.getEndValue()) * self.total_height > 1:
            self.current_relative_value = self.relative.getCurrentValue()
            self._updateRelativeView(self.current_relative_value)
            self.on_relative_changed(self.current_relative_value)

    def onMouseWheel(self, x: int, y: int, v: int) -> None:
        dr = -self.MOUSE_SCROLL_SPEED * v / self.total_height
        self.setRelativeWithSmooth(self.relative.getEndValue() + dr)