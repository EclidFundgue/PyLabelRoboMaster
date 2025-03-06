from typing import Callable, List, Tuple, Union

from .. import logger, timer, utils
from .containers import RectContainer
from .selectable import Selectable


class ListBox(RectContainer):
    '''
    Contains a list of Selectable components. It controls
    the position of each line, and handle mouse scroll and
    click event.

    ListBox(
        w, h, x, y,
        lines,
        on_relative_change
    )
    * on_relative_change(r) -> None

    Method:
    * setRelative(r, smooth) -> None
    * getRelative() -> float

    * select(line) -> None
    * selectPrev() -> None
    * selectNext() -> None
    * getSelected() -> Selectable | None
    * getSelectedIndex() -> int

    * add(line) -> None
    * delete(line) -> None
    '''

    MOUSE_SCROLL_SPEED = 100

    def __init__(self,
        w: int, h: int, x: int, y: int,
        lines: List[Selectable] = None,
        on_relative_change: Callable[[float], None] = None
    ):
        super().__init__(w, h, x, y)
        self.lines = lines if lines is not None else []
        self.on_relative_change = utils.getCallable(on_relative_change)

        self.heights: List[int]
        self.total_height: int
        self._updateLinesHeights(self.lines)

        self.child_top_idx = 0 # line_idx = child_idx + child_top_idx
        self.selected_idx = -1
        self.selected_line: Union[Selectable, None] = None
        self.relative = timer.TimedFloat(0.2, 0, timer.INTERP_POLY2)
        self.current_r_value = self.relative.getCurrentValue()

        self._updateRelativeView(self.current_r_value)

    def __len__(self) -> int:
        return len(self.lines)

    def _updateLinesHeights(self, lines: List[Selectable]) -> None:
        self.total_height = 0
        self.heights = []
        for l in lines:
            self.heights.append(self.total_height)
            self.total_height += l.h

        # avoid zero division
        self.total_height = max(1, self.total_height)

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

    def _updateChildren(self, offset: int, start_idx: int, end_idx: int):
        for i in range(start_idx, end_idx + 1):
            l = self.lines[i]
            l.x = 0
            l.y = self.heights[i] + offset
        self.setChildren(self.lines[start_idx: end_idx + 1])
        self.child_top_idx = start_idx

    def _updateRelativeView(self, r: float) -> None:
        ''' Update childs position and display range. '''
        y_offset = self._getPixelOffset(r)
        start, end = self._searchDisplayRange(y_offset)
        self._updateChildren(y_offset, start, end)

    def setRelative(self, r: float, smooth: bool) -> None:
        if r < 0:
            r = 0
        elif r > 1:
            r = 1
        if abs(r - self.relative.getEndValue()) < 1e-6:
            return

        self.relative.setValue(r, use_smooth=smooth)
        self.current_r_value = self.relative.getCurrentValue()
        self._updateRelativeView(self.current_r_value)
        if smooth:
            self.on_relative_change(self.current_r_value)

    def getRelative(self) -> float:
        return self.current_r_value

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
        self.selected_line: Selectable = l

    def _selectByLine(self, line: Selectable) -> None:
        if line == self.selected_line:
            return

        idx = self.lines.index(line)
        self._selectByIndex(idx)

    def _constrainRelativeByIndex(self, idx: int, smooth: bool) -> float:
        line_top = self.heights[idx]
        line_bottom = line_top + self.lines[idx].h

        min_r = (line_bottom - self.h) / max(self.total_height - self.h, 1e-6)
        min_r = min(max(min_r, 0), 1)
        max_r = min(line_top / max(self.total_height - self.h, 1e-6), 1)

        if self.relative.getEndValue() < min_r:
            self.setRelative(min_r, smooth)
        elif self.relative.getEndValue() > max_r:
            self.setRelative(max_r, smooth)

    def select(self, line: Union[int, Selectable]) -> None:
        if isinstance(line, int):
            self._selectByIndex(line)
        elif isinstance(line, Selectable):
            self._selectByLine(line)
        else:
            logger.warning(f"Invalid line type: {type(line)}", self)

        self._constrainRelativeByIndex(self.selected_idx, True)

    def selectPrev(self) -> None:
        if len(self.lines) == 0:
            return
        if self.selected_idx == -1:
            self._selectByIndex(len(self.lines) - 1)
        else:
            self._selectByIndex(
                (self.selected_idx + len(self.lines) - 1) % len(self.lines)
            )
        self._constrainRelativeByIndex(self.selected_idx, True)

    def selectNext(self) -> None:
        if len(self.lines) == 0:
            return
        if self.selected_idx == -1:
            self._selectByIndex(0)
        else:
            self._selectByIndex((self.selected_idx + 1) % len(self.lines))
        self._constrainRelativeByIndex(self.selected_idx, True)

    def getSelected(self) -> Union[Selectable, None]:
        return self.selected_line

    def getSelectedIndex(self) -> int:
        return self.selected_idx

    def add(self, line: Selectable) -> None:
        self.lines.append(line)

        # update box
        self.removeDeadChildren()
        self.heights = self._updateLinesHeights(self.lines)
        self.total_height = max(1, sum(self.heights)) # avoid zero division
        self._updateRelativeView(self.current_r_value)

        # update selected line index
        if self.selected_line is not None:
            self.selected_idx = self.lines.index(self.selected_line)

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
        self.removeDeadChildren()
        self._updateLinesHeights(self.lines)
        self._updateRelativeView(self.current_r_value)

        # update selected line index
        if self.selected_line is not None:
            self.selected_idx = self.lines.index(self.selected_line)

    def _deleteByLine(self, line: Selectable) -> None:
        idx = self.lines.index(line)
        self._deleteByIndex(idx)

    def delete(self, line: Union[int, Selectable]) -> None:
        ''' Delete line with given index. '''

        if isinstance(line, int):
            self._deleteByIndex(line)
        elif isinstance(line, Selectable):
            self._deleteByLine(line)
        else:
            logger.warning(f"Invalid line type: {type(line)}", self)

    def update(self, x: int, y: int, wheel: int) -> None:
        if abs(self.current_r_value - self.relative.getEndValue()) * self.total_height > 1:
            self.current_r_value = self.relative.getCurrentValue()
            self._updateRelativeView(self.current_r_value)
            self.on_relative_change(self.current_r_value)
            self.redraw()

        if self.active and wheel != 0:
            dr = -self.MOUSE_SCROLL_SPEED * wheel / self.total_height
            self.setRelative(self.relative.getEndValue()+dr, True)
            self.redraw()

    def onResize(self, w, h, x, y):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self._updateRelativeView(self.current_r_value)

    def kill(self) -> None:
        for l in self.lines:
            l.kill()
        self.lines = None
        self.on_relative_change = None
        self.selected_line = None
        super().kill()