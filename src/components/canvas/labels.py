from typing import Callable, List, Tuple

import pygame

from ... import pygame_gui as ui
from ...pygame_gui.components.canvas import CanvasComponent
from ...utils import geometry, imgproc
from ...utils import lbformat as fmt
from .icon import ArmorIcon
from .keypoint import Keypoint


class Label:
    '''This class is used as a container.

    Methods:
    * drawContour(surface, x_start, y_start, closed) -> None
    * inHover(x, y) -> bool
    * kill() -> None
    * setTypeID(type_id) -> None
    * setColorID(color_id) -> None
    * setClassID(cls_id) -> None
    * setSelected(selected) -> None
    * updateIconState() -> None
    '''
    def __init__(self, points: List[Keypoint] = None, cls_id: int = 0):
        if points is None:
            points = []
        self.points = points
        self.icon: ArmorIcon = None
        self.alive = True

        self.cls_id = cls_id
        self.active = False
        self.selected = False

        self.line_color0 = (61, 142, 72)
        self.line_color1 = ui.color.light(self.line_color0, 5)

    def drawContour(self,
        surface: pygame.Surface,
        x_start: int,
        y_start: int,
        closed: bool
    ) -> None:
        if self.selected:
            width = 2
            color = self.line_color1
        elif self.active:
            width = 1
            color = self.line_color1
        else:
            width = 1
            color = self.line_color0
        points = [(p.x + x_start + p.w // 2, p.y + y_start + p.h // 2) for p in self.points]
        pygame.draw.lines(surface, color, closed, points, width)

    def inHover(self, x: int, y: int) -> bool:
        polygon = [(p.x + p.w // 2, p.y + p.h // 2) for p in self.points]
        in_polygon = geometry.in_polygon(polygon, (x, y))
        in_icon = self.icon is not None and self.icon.active
        return in_polygon or in_icon

    def kill(self) -> None:
        for p in self.points:
            p.kill()
        if self.icon is not None:
            self.icon.kill()
        self.points = None
        self.icon = None
        self.alive = False

    def getStateDict(self) -> dict:
        return {
            'points': [p.getCenter() for p in self.points],
            'cls_id': self.cls_id
        }

    def setTypeID(self, type_id: int) -> None:
        color_id = self.cls_id // 8
        self.setClassID(color_id * 8 + type_id)

    def setColorID(self, color_id: int) -> None:
        type_id = self.cls_id % 8
        self.setClassID(color_id * 8 + type_id)

    def setClassID(self, cls_id: int) -> None:
        self.cls_id = cls_id
        self.icon.setClassId(self.cls_id)

    def setSelected(self, selected: bool) -> None:
        self.selected = selected
        self.updateIconState()

    def updateIconState(self) -> None:
        if self.selected:
            self.icon.label_state = self.icon.STATE_SELECTED
        elif self.active:
            self.icon.label_state = self.icon.STATE_ACTIVE
        else:
            self.icon.label_state = self.icon.STATE_NORMAL

def _createKeypoint(cx: int, cy: int, on_click: Callable[[], None] = None) -> Keypoint:
    kpt = Keypoint(on_click)
    kpt.setCenter(cx, cy)
    return kpt

def _createArmorIcon(kpt: Keypoint, cls_id: int) -> ArmorIcon:
    icon = ArmorIcon(cls_id)
    icon.setPos(kpt)
    return icon

class Labels(CanvasComponent):
    '''Methods:
    1. ---------- add & delete & change ----------
    * startAdd() -> None
    * cancelAdd() -> None
    * deleteSelectedLabels() -> None
    * setSelectedClass(cls_id) -> None
    * relabel(img) -> None
    * correctSelectedLabels(img) -> None

    2. ---------- select ----------
    * selectAll() -> None
    * unselectAll() -> None

    3. ---------- save & load ----------
    * undo() -> None
    * redo() -> None
    * load(path, img_rect) -> None
    * saveToPath(path) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        num_keypoints: int,
        on_select: Callable[[Label], None] = None
    ):
        super().__init__(w, h, x, y)

        self.num_keypoints = num_keypoints
        self.on_select = ui.utils.getCallable(on_select)

        self.dragging_point: Keypoint = None
        self.adding_label: Label = None
        self.adding_point: Keypoint = None
        self.labels: List[Label] = []
        self.selected_labels: List[Label] = []

        self.curr_class_id = 0
        self.key_ctrl_pressed = False # multi-selection
        self.curr_mouse_pos = (0, 0) # mouse position before scaled

        self.snapshot_index = 0
        self.snapshots: List[dict] = []

        self.addKeyDownEvent(pygame.K_a, self.startAdd)
        self.addKeyDownEvent(pygame.K_ESCAPE, self.cancelAdd)
        self.addKeyDownEvent(pygame.K_d, self.deleteSelectedLabels)
        self.addKeyDownEvent(pygame.K_DELETE, self.deleteSelectedLabels)
        self.addKeyCtrlEvent(pygame.K_a, self.selectAll)
        self.addKeyDownEvent(pygame.K_ESCAPE, self.unselectAll)
        self.addKeyCtrlEvent(pygame.K_z, self.undo)
        self.addKeyCtrlEvent(pygame.K_y, self.redo)

        self.addKeyDownEvent(pygame.K_0, self._setSelectedTypeIDCallback(0))
        self.addKeyDownEvent(pygame.K_1, self._setSelectedTypeIDCallback(1))
        self.addKeyDownEvent(pygame.K_2, self._setSelectedTypeIDCallback(2))
        self.addKeyDownEvent(pygame.K_3, self._setSelectedTypeIDCallback(3))
        self.addKeyDownEvent(pygame.K_4, self._setSelectedTypeIDCallback(4))
        self.addKeyDownEvent(pygame.K_5, self._setSelectedTypeIDCallback(5))
        self.addKeyDownEvent(pygame.K_6, self._setSelectedTypeIDCallback(6))
        self.addKeyDownEvent(pygame.K_7, self._setSelectedTypeIDCallback(7))

        self.addKeyDownEvent(pygame.K_b, self._setSelectedColorIDCallback(0))
        self.addKeyDownEvent(pygame.K_r, self._setSelectedColorIDCallback(1))

    def _setSelectedTypeIDCallback(self, n: int) -> Callable[[], None]:
        def func():
            # update self
            curr_color_id = self.curr_class_id // 8
            self.curr_class_id = curr_color_id * 8 + n
            # update labels
            if len(self.selected_labels) == 0:
                return
            for label in self.selected_labels:
                label.setTypeID(n)
            self._snapshot()
            self.redraw()
        return func

    def _setSelectedColorIDCallback(self, n: int) -> Callable[[], None]:
        def func():
            # update self
            curr_type_id = self.curr_class_id % 8
            self.curr_class_id = n * 8 + curr_type_id
            # update labels
            if len(self.selected_labels) == 0:
                return
            for label in self.selected_labels:
                label.setColorID(n)
            self._snapshot()
            self.redraw()
        return func

    def _snapshot(self) -> None:
        snapshot = {
            'labels': [l.getStateDict() for l in self.labels],
            'curr_class_id': self.curr_class_id
        }

        if len(self.snapshots) > 0 and snapshot == self.snapshots[self.snapshot_index - 1]:
            return

        if self.snapshot_index < len(self.snapshots):
            self.snapshots = self.snapshots[:self.snapshot_index]
        self.snapshots.append(snapshot)
        self.snapshot_index += 1

    def _loadSnapshot(self, snapshot: dict) -> None:
        self._tryCancelAdd() # load snapshot will terminate add process

        for label in self.labels:
            label.kill()
        self.labels = []
        self.selected_labels = []

        self.curr_class_id = snapshot['curr_class_id']

        for label_dict in snapshot['labels']:
            points = [Keypoint() for _ in range(len(label_dict['points']))]
            for p, p_center in zip(points, label_dict['points']):
                p.on_click = self._getKeypointOnClickFunction(p)
                p.setCenter(*p_center)
                self.addChild(p)

            icon = ArmorIcon(label_dict['cls_id'])
            icon.setPos(points[2])
            self.addChild(icon)

            label_obj = Label(points, label_dict['cls_id'])
            label_obj.icon = icon
            self.labels.append(label_obj)

    def _getLabelsIO(self, orig_img_size: Tuple[int, int]) -> List[fmt.LabelIO]:
        ret = []
        for label in self.labels:
            points = [p.getCenter() for p in label.points]
            points = [(
                (x + self._x) / orig_img_size[0],
                (y + self._y) / orig_img_size[1]
            ) for x, y in points]
            ret.append(fmt.ArmorLabelIO(label.cls_id, points))
        return ret

    def _addLabelsIO(self,
        labels_io: List[fmt.LabelIO],
        orig_img_size: Tuple[int, int]
    ) -> None:
        for label_io in labels_io:
            kpts = []
            for x, y in label_io.kpts:
                cx = int(x * orig_img_size[0] - self._x)
                cy = int(y * orig_img_size[1] - self._y)
                p = _createKeypoint(cx, cy)
                p.on_click = self._getKeypointOnClickFunction(p)
                kpts.append(p)
                self.addChild(p)

            label = Label(kpts, label_io.id)
            label.icon = _createArmorIcon(kpts[2], label_io.id)

            self.addChild(label.icon)
            self.labels.append(label)

    def _getKeypointOnClickFunction(self, kpt: Keypoint) -> Callable[[], None]:
        def func():
            # You can not move a keypoint while adding a new label.
            if self.dragging_point is None and self.adding_point is None:
                self.dragging_point = kpt
        return func

    def _onAddPoint(self) -> None:
        self.adding_point.on_click = self._getKeypointOnClickFunction(self.adding_point)

        # Add process finished.
        if len(self.adding_label.points) >= self.num_keypoints:
            self.adding_label.icon = _createArmorIcon(self.adding_label.points[2], 0)
            self.addChild(self.adding_label.icon)

            self.labels.append(self.adding_label)

            self.adding_point = None
            self.adding_label = None
            self._snapshot()
            self.redraw()
            return

        # Continue add process.
        self.adding_point = _createKeypoint(*self.curr_mouse_pos, self._onAddPoint)
        self.adding_label.points.append(self.adding_point)
        self.addChild(self.adding_point)

    def startAdd(self) -> None:
        if self.adding_label is not None:
            return

        self.adding_point = _createKeypoint(*self.curr_mouse_pos, self._onAddPoint)
        self.adding_label = Label([self.adding_point])
        self.addChild(self.adding_point)

    def _tryCancelAdd(self) -> bool:
        '''Inner function, return if successfully cancelled.'''
        if self.adding_label is None:
            return False
        self.adding_label.kill()
        self.adding_point = None
        self.adding_label = None
        return True

    def cancelAdd(self) -> None:
        if self._tryCancelAdd():
            self.redraw()

    def deleteSelectedLabels(self) -> None:
        if len(self.selected_labels) == 0:
            return

        for label in self.selected_labels:
            label.kill()
            self.labels.remove(label)
        self.selected_labels = []
        self.redraw()

    def setSelectedClass(self, cls_id: int) -> None:
        if len(self.selected_labels) == 0:
            return

        for label in self.selected_labels:
            label.cls_id = cls_id
            label.icon.setClassId(cls_id)
        self._snapshot()
        self.redraw()

    def relabel(self, img: pygame.Surface) -> None:
        cv_img = imgproc.surface2mat(img)
        io_labels = []
        for label in self.labels:
            points = [p.getCenter() for p in label.points]
            io_labels.append(fmt.ArmorLabelIO(label.cls_id, points))
        labels = imgproc.relabel(cv_img, io_labels)

        # clear current labels
        self._tryCancelAdd()
        for label in self.labels:
            label.kill()
        self.labels = []
        self.selected_labels = []

        for label_io in labels:
            points = [Keypoint() for _ in range(len(label_io.kpts))]
            for p, p_center in zip(points, label_io.kpts):
                p.on_click = self._getKeypointOnClickFunction(p)
                p.setCenter(*p_center)
                self.addChild(p)

            icon = ArmorIcon(label_io.id)
            icon.setPos(points[2])
            self.addChild(icon)

            label_obj = Label(points, label_io.id)
            label_obj.icon = icon
            self.labels.append(label_obj)

        self._snapshot()
        self.redraw()

    def correctSelectedLabels(self, img: pygame.Surface) -> None:
        if len(self.selected_labels) == 0:
            return

        cv_img = imgproc.surface2mat(img)
        labels_io = self._getLabelsIO(img.get_size())
        corrected_labels = imgproc.correctLabels(cv_img, labels_io)

        # clear selected labels
        self._tryCancelAdd()
        for label in self.selected_labels:
            label.kill()
        self.labels = list(filter(lambda lb: lb.alive, self.labels))
        self.selected_labels = []

        # add corrected labels
        self._addLabelsIO(corrected_labels, img.get_size())
        self._snapshot()
        self.redraw()

    def selectAll(self) -> None:
        for label in self.labels:
            label.setSelected(True)
        self.selected_labels = self.labels
        self.redraw()

    def unselectAll(self) -> None:
        for label in self.selected_labels:
            label.setSelected(False)
        self.selected_labels = []
        self.redraw()

    def undo(self) -> None:
        if self.snapshot_index <= 1:
            return
        self.snapshot_index -= 1
        self._loadSnapshot(self.snapshots[self.snapshot_index - 1])
        self.redraw()

    def redo(self) -> None:
        if self.snapshot_index >= len(self.snapshots):
            return
        self._loadSnapshot(self.snapshots[self.snapshot_index])
        self.snapshot_index += 1
        self.redraw()

    def load(self, path: str, orig_img_size: Tuple[int, int]) -> None:
        labels_io = fmt.loadLabel(path)
        self._addLabelsIO(labels_io, orig_img_size)
        self._snapshot()
        self.redraw()

    def saveToPath(self, path: str, orig_img_size: Tuple[int, int]) -> None:
        fmt.saveLabel(path, self._getLabelsIO(orig_img_size))

    def _handleAddingPointMovement(self, x: int, y: int) -> None:
        self.adding_point.setCenter(x / self.scale, y / self.scale)
        self.adding_point.redraw()

    def _handleLabelsActive(self, x: int, y: int) -> None:
        active_changed = False

        for label in self.labels:
            active = label.inHover(x, y)
            if label.active != active:
                label.active = active
                label.updateIconState()
                active_changed = True

        if active_changed:
            self.redraw()

    def update(self, x: int, y: int, wheel: int) -> None:
        if not self.active:
            return

        self.curr_mouse_pos = (int(x / self.scale), int(y / self.scale))
        self.key_ctrl_pressed = pygame.key.get_pressed()[pygame.K_LCTRL] \
                             or pygame.key.get_pressed()[pygame.K_RCTRL]

        if self.adding_point is not None:
            self._handleAddingPointMovement(x, y)
        else:
            self._handleLabelsActive(x, y)

    def _oneLabelSelection(self, clicked_labels: List[Label]) -> None:
        for label in self.selected_labels:
            label.setSelected(False)
        for label in clicked_labels:
            label.setSelected(True)
            self.on_select(label)
        self.selected_labels = clicked_labels

    def _multipleLabelSelection(self, clicked_labels: List[Label]) -> None:
        for label in clicked_labels:
            if not label.selected:
                label.setSelected(True)
                self.on_select(label)
                self.selected_labels.append(label)
            else:
                label.setSelected(False)
                self.selected_labels.remove(label)

    def _handleLabelSelection(self, clicked_labels: List[Label]) -> None:
        if not self.key_ctrl_pressed:
            self._oneLabelSelection(clicked_labels)
        else:
            self._multipleLabelSelection(clicked_labels)

    def onLeftClick(self, x, y):
        if self.adding_point is None:
            clicked_labels = list(filter(lambda label: label.inHover(x, y), self.labels))
            self._handleLabelSelection(clicked_labels)
            self.redraw()

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if vx == 0 and vy == 0:
            return

        if self.dragging_point is not None:
            self.dragging_point.move(vx, vy)
            self.redraw()

        for label in self.labels:
            label.icon.setPos(label.points[2])

    def onLeftRelease(self):
        if self.dragging_point is not None:
            self.dragging_point = None
            self._snapshot()

    def onMouseLeave(self):
        if self.dragging_point is not None:
            self.dragging_point = None
            self._snapshot()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        for label in self.labels:
            label.drawContour(surface, x_start, y_start, True)

        if self.adding_label is not None and len(self.adding_label.points) >= 2:
            self.adding_label.drawContour(surface, x_start, y_start, False)