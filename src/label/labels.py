from typing import Callable, List, Tuple

import pygame

from .. import pygame_gui as ui
from ..utils import imgproc, lbformat
from ..utils.lbformat import LabelIO
from .icon import Icon
from .keypoint import Keypoint
from .label import Label


class Labels(ui.components.CanvasComponent):
    '''
    Labels(
        w, h, x, y,
        num_keypoints,
        icon_getter,
        on_select
    )
    * icon_getter(kpt, cls_id) -> Icon
    * on_select(cls_id) -> None

    Methods:

    ---------- add & delete & change ----------
    * startAdd() -> None
    * cancelAdd() -> None
    * deleteSelectedLabels() -> None
    * setSelectedClass(cls_id) -> None
    * relabel(img) -> None
    * correctSelectedLabels(img) -> None

    ---------- select ----------
    * selectAll() -> None
    * unselectAll() -> None

    ---------- save & load ----------
    * undo() -> None
    * redo() -> None
    * load(path, orig_img_size) -> None
    * save(path, orig_img_size) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        num_keypoints: int,
        icon_getter: Callable[[Keypoint, int], Icon],
        on_select: Callable[[int], None] = None
    ):
        super().__init__(w, h, x, y)

        self.num_keypoints = num_keypoints
        self.icon_getter = icon_getter
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

    def _getLabelsIO(self,
        labels: List[Label],
        orig_img_size: Tuple[int, int]
    ) -> List[LabelIO]:
        ret = []
        for label in labels:
            points = [p.getCenter() for p in label.points]
            points = [(
                (x + self._x) / orig_img_size[0],
                (y + self._y) / orig_img_size[1]
            ) for x, y in points]
            ret.append(LabelIO(label.cls_id, points))
        return ret

    def _addLabelsIO(self,
        labels_io: List[LabelIO],
        orig_img_size: Tuple[int, int]
    ) -> None:
        for label_io in labels_io:
            label_io.kpts = imgproc.sortedPoints(label_io.kpts)

            kpts = []
            for x, y in label_io.kpts:
                cx = int(x * orig_img_size[0] - self._x)
                cy = int(y * orig_img_size[1] - self._y)
                p = Keypoint((cx, cy), self._keypointOnClick)
                kpts.append(p)
                self.addChild(p)

            icon = self.icon_getter(kpts[2], label_io.cls_id)
            self.addChild(icon)

            label = Label(label_io.cls_id, kpts, icon)
            self.labels.append(label)

    def _snapshot(self) -> None:
        snapshot = {
            'labels': self._getLabelsIO(self.labels, (1, 1)),
            'curr_class_id': self.curr_class_id
        }

        if len(self.snapshots) > 0 and snapshot == self.snapshots[self.snapshot_index-1]:
            return

        if self.snapshot_index < len(self.snapshots):
            self.snapshots = self.snapshots[:self.snapshot_index]
        self.snapshots.append(snapshot)
        self.snapshot_index += 1

    def _deleteLabels(self, label_list: List[Label]) -> None:
        self._tryCancelAdd()

        for label in label_list:
            label.kill()

        self.labels = list(filter(lambda lb: lb.alive, self.labels))
        self.selected_labels = list(filter(lambda lb: lb.alive, self.selected_labels))

    def _loadSnapshot(self, snapshot: dict) -> None:
        self._deleteLabels(self.labels)
        self._addLabelsIO(snapshot['labels'], (1, 1))
        self.curr_class_id = snapshot['curr_class_id']

    # ---------- add & delete & change ----------
    def _keypointOnClick(self, kpt: Keypoint) -> None:
        # You can not move a keypoint while adding a new label.
        if self.dragging_point is None and self.adding_point is None:
            self.dragging_point = kpt

    def _onAddPoint(self, kpt: Keypoint) -> None:
        if kpt is not self.adding_point:
            ui.logger.error(
                'Only adding point can call `_onAddPoint` function.',
                ValueError, self
            )

        kpt.on_click = self._keypointOnClick

        # Add finished.
        if len(self.adding_label.points) >= self.num_keypoints:
            self.adding_label.icon = self.icon_getter(self.adding_label.points[2], self.adding_label.cls_id)
            self.addChild(self.adding_label.icon)

            self.labels.append(self.adding_label)

            self.adding_point = None
            self.adding_label = None
            self._snapshot()
            self.redraw()
            return

        # Add next point.
        self.adding_point = Keypoint(self.curr_mouse_pos, self._onAddPoint)
        self.adding_label.points.append(self.adding_point)
        self.addChild(self.adding_point)

    def startAdd(self) -> None:
        if self.adding_label is not None:
            return

        self.adding_point = Keypoint(self.curr_mouse_pos, self._onAddPoint)
        self.adding_label = Label(self.curr_class_id, [self.adding_point])
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
        self._deleteLabels(self.selected_labels)
        self._snapshot()
        self.redraw()

    def setSelectedClass(self, cls_id: int) -> None:
        self.curr_class_id = cls_id

        if len(self.selected_labels) == 0:
            return

        for label in self.selected_labels:
            label.setClass(cls_id)
        self._snapshot()
        self.redraw()

    def relabel(self, img: pygame.Surface) -> None:
        cv_img = imgproc.surface2mat(img)
        labels_io = self._getLabelsIO(self.labels, img.get_size())
        labels_io = imgproc.relabel(cv_img, labels_io)

        self._deleteLabels(self.labels)
        self._addLabelsIO(labels_io)
        self._snapshot()
        self.redraw()

    def correctSelectedLabels(self, img: pygame.Surface) -> None:
        if len(self.selected_labels) == 0:
            return

        cv_img = imgproc.surface2mat(img)
        labels_io = self._getLabelsIO(self.selected_labels, img.get_size())
        labels_io = imgproc.correctLabels(cv_img, labels_io)

        self._deleteLabels(self.selected_labels)
        self._addLabelsIO(labels_io, img.get_size())
        self._snapshot()
        self.redraw()

    # ---------- select ----------
    def selectAll(self) -> None:
        for label in self.labels:
            label.setSelectState(True)
        self.selected_labels = self.labels.copy()
        self.redraw()

    def unselectAll(self) -> None:
        for label in self.selected_labels:
            label.setSelectState(False)
        self.selected_labels = []
        self.redraw()

    # ---------- save & load ----------
    def undo(self) -> None:
        if self.snapshot_index <= 1:
            return
        self.snapshot_index -= 1
        self._loadSnapshot(self.snapshots[self.snapshot_index-1])
        self.redraw()

    def redo(self) -> None:
        if self.snapshot_index >= len(self.snapshots):
            return
        self._loadSnapshot(self.snapshots[self.snapshot_index])
        self.snapshot_index += 1
        self.redraw()

    def load(self, path: str, orig_img_size: Tuple[int, int]) -> None:
        labels_io = lbformat.loadLabel(path)
        self._addLabelsIO(labels_io, orig_img_size)
        self._snapshot()
        self.redraw()

    def save(self, path: str, orig_img_size: Tuple[int, int]) -> None:
        labels_io = self._getLabelsIO(self.labels, orig_img_size)
        lbformat.saveLabel(path, labels_io)

    # ---------- canvas update ----------
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

    # ---------- events ----------
    def _oneLabelSelection(self, clicked_labels: List[Label]) -> None:
        for label in self.selected_labels:
            label.setSelectState(False)
        for label in clicked_labels:
            label.setSelectState(True)
            self.on_select(label.cls_id)
        self.selected_labels = clicked_labels

    def _multipleLabelSelection(self, clicked_labels: List[Label]) -> None:
        for label in clicked_labels:
            if not label.selected:
                label.setSelectState(True)
                self.on_select(label.cls_id)
                self.selected_labels.append(label)
            else:
                label.setSelectState(False)
                self.selected_labels.remove(label)

    def _handleLabelSelection(self, clicked_labels: List[Label]) -> None:
        if not self.key_ctrl_pressed:
            self._oneLabelSelection(clicked_labels)
        else:
            self._multipleLabelSelection(clicked_labels)

    def onLeftClick(self, x, y):
        if self.adding_point is None:
            clicked_labels = list(filter(
                lambda label: label.inHover(x, y),
                self.labels
            ))
            self._handleLabelSelection(clicked_labels)
            self.redraw()

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if vx == 0 and vy == 0:
            return

        if self.dragging_point is not None:
            self.dragging_point.move(vx, vy)
            self.redraw()

        # TODO: Is all the icons need to update when dragging?
        for label in self.labels:
            label.icon.setPosToKeypoint(label.points[2])

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