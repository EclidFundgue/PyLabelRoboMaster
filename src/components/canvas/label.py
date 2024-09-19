from typing import Any, Callable, List, Tuple

import pygame
from pygame import Surface as pg_Surface
from pygame import locals

from ...process.correct import correctLabels, relabel
from ...process.label_io import LabelInputOutput, loadLabel, saveLabel
from ...pygame_gui import f_warning
from ...pygame_gui.decorators import getCallable
from ...utils.dataproc import sortedPoints, surface2mat
from .armor_icon import TypeIcon
from .canvas import Canvas, CanvasComponent
from .contour import Contour
from .keypoint import Keypoint, getKeypointsFromLabelIO


class Label:
    '''
    Used to contain keypoints and other information.

    Label(type_id, keypoints, contour, icon)

    Methods:
    * addToCanvas(canvas) -> None
    '''
    def __init__(self,
            type_id: int = 0,
            keypoints: List[Keypoint] = None,
            contour: Contour = None,
            icon: TypeIcon = None):
        self.type_id = type_id
        if keypoints is None:
            keypoints = []
        self.keypoints = keypoints
        self.contour = contour
        self.icon = icon

        self.alive = True

    def addToCanvas(self, canvas: Canvas) -> None:
        if self.keypoints is not None:
            for p in self.keypoints:
                canvas.addChild(p)

        if self.contour is not None:
            canvas.addChild(self.contour)

        if self.icon is not None:
            canvas.addChild(self.icon)

    def getLabelIO(self, image_size: Tuple[int, int]) -> LabelInputOutput:
        kpts = [(p._x / image_size[0], p._y / image_size[1])
                for p in self.keypoints]
        return LabelInputOutput(
            self.type_id,
            sortedPoints(kpts),
        )

    def kill(self) -> None:
        for p in self.keypoints:
            if p.alive:
                p.kill()

        if self.contour is not None and self.contour.alive:
            self.contour.kill()

        if self.icon is not None and self.icon.alive:
            self.icon.kill()

        self.keypoints = None
        self.contour = None
        self.icon = None

        self.alive = False

class LabelsMemeto:
    ''' Saves infomation of LabelsManager. '''
    def __init__(self):
        self.labels: List[LabelInputOutput] = []
        self.selected_incidies: List[int] = []
        self.curr_type_id = 0

class Labels(CanvasComponent):
    '''
    Manage Labels for an image.

    Labels(
        w, h, x, y,
        canvas,
        keypoint_size,
        label_path,
        on_single_select,
        pax_x, pax_y
    )

    Methods:
    1. ---------- add & delete & change ----------
    * startAdd() -> None
    * stopAdd() -> None
    * deleteSelectedLabels() -> None
    * setSelectedType(type_id) -> None
    * relabel(img) -> None
    * correctSelectedLabels(img) -> None

    2. ---------- select ----------
    * selectAll() -> None

    3. ---------- save & load ----------
    * undo() -> None
    * redo() -> None
    * saveToFile() -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            canvas: Canvas,
            keypoint_size: int = 4,
            label_path: str = None,
            on_single_select: Callable[[Label], None] = None,
            pax_x: int = 0,
            pax_y: int = 0):
        super().__init__(w + 2 * pax_x, h + 2 * pax_y, x - pax_x, y - pax_y)
        self.image_rect = (w, h, x, y)
        self.canvas = canvas
        self.keypoint_size = keypoint_size
        self.label_path = label_path
        self.on_single_select: Callable[[Label], None] = getCallable(on_single_select)
        self.pax_x = pax_x
        self.pax_y = pax_y

        self.labels: List[Label] = []

        self.selected_labels: List[Label] = []
        self.dragging_point: Keypoint = None
        self.adding_label: Label = None
        self.adding_point: Keypoint = None

        self.curr_type_id = 0
        self.key_ctrl_pressed = False # multi-select

        self.history_index = 0
        self.history: List[LabelsMemeto] = []

        # add event listeners
        self.addKeydownEvent(locals.K_a, self.startAdd)
        self.addKeydownEvent(locals.K_ESCAPE, self.stopAdd)
        self.addKeydownEvent(locals.K_d, self.deleteSelectedLabels)
        self.addKeydownEvent(locals.K_DELETE, self.deleteSelectedLabels)
        self.addKeyCtrlEvent(locals.K_a, self.selectAll)
        self.addKeyCtrlEvent(locals.K_z, self.undo)
        self.addKeyCtrlEvent(locals.K_y, self.redo)
        self.addKeyCtrlEvent(locals.K_s, self.saveToFile)

        # initialize
        self._loadFromFile(self.label_path)
        self._saveToMemento()

    # -------------------- add & delete & change -------------------- #
    def _getKeypointOnClickFunc(self, keypoint: Keypoint) -> Callable:
        def on_click():
            if self.dragging_point is None:
                self.dragging_point = keypoint
                self.dragging_point.select()
        return on_click

    def _getLabelOnClickFunc(self, label: Label) -> Callable:
        def on_click():
            # single select
            if not self.key_ctrl_pressed:
                self._selectedRemoveAll()
                self._selectedAppend(label)
                self.on_single_select(label)
            # multi select
            else:
                if label not in self.selected_labels:
                    self._selectedAppend(label)
                else:
                    self._selectedRemove(label)
        return on_click

    def _addLabelByIO(self, label_io: LabelInputOutput) -> None:
        # create label
        keypoints = getKeypointsFromLabelIO(label_io, self.image_rect[:2])
        contour = Contour(self.keypoint_size, keypoints)
        icon = TypeIcon(32, 32, keypoints[2], label_io.id)
        label = Label(
            type_id=label_io.id,
            keypoints=keypoints,
            contour=contour,
            icon=icon
        )

        # add point click event
        for p in keypoints:
            p.on_click = self._getKeypointOnClickFunc(p)

        # add contour click event
        on_label_click = self._getLabelOnClickFunc(label)
        contour.on_click = on_label_click
        icon.on_click = on_label_click

        # add label to canvas
        self.labels.append(label)
        label.addToCanvas(self.canvas)

    def _addingPointOnClick(self) -> None:
        # add task finished
        if len(self.adding_label.keypoints) >= self.keypoint_size:
            added_label = self.adding_label.getLabelIO(self.image_rect[:2])
            self._addLabelByIO(added_label)
            self._saveToMemento()
            self.adding_label.kill()
            self.adding_label = None
            self.adding_point = None
            return

        # add one keypoint
        self.adding_point.on_click = getCallable()
        self.adding_point = Keypoint(0, 0, self._addingPointOnClick)
        self.canvas.addChild(self.adding_point)
        self.adding_label.keypoints.append(self.adding_point)

    def startAdd(self) -> None:
        if self.adding_label is not None:
            return

        self.adding_point = Keypoint(0, 0, self._addingPointOnClick)
        keypoints = [self.adding_point]
        contour = Contour(self.keypoint_size, keypoints)
        self.adding_label = Label(
            self.curr_type_id,
            keypoints=keypoints,
            contour=contour
        )
        self.adding_label.addToCanvas(self.canvas)

    def stopAdd(self) -> None:
        if self.adding_label is None:
            return

        self.adding_label.kill()
        self.adding_point = None
        self.adding_label = None
        self.removeDead()

    def _deleteLabel(self, label: Label) -> None:
        if not label in self.labels:
            f_warning(f"Label {label} not in labels.", self)
            return

        self.labels.remove(label)
        label.kill()
        self.removeDead()

    def deleteSelectedLabels(self) -> None:
        if len(self.selected_labels) == 0:
            return

        for label in self.selected_labels:
            self._deleteLabel(label)
        self.selected_labels = []
        self._saveToMemento()

    def setSelectedType(self, type_id: int) -> None:
        self.curr_type_id = type_id
        for label in self.selected_labels:
            label.type_id = type_id
            label.icon.setType(type_id)
        self._saveToMemento()

    def relabel(self, img: pg_Surface) -> None:
        cv_img = surface2mat(img)
        original_labels = [lb.getLabelIO(self.image_rect[:2]) for lb in self.labels]
        labels = relabel(cv_img, original_labels)

        # clear current labels
        for label in self.labels:
            label.kill()
        self.removeDead()
        self.labels = []

        # add new labels
        for label_io in labels:
            self._addLabelByIO(label_io)
        self._saveToMemento()

    def correctSelectedLabels(self, img: pg_Surface) -> None:
        if len(self.selected_labels) == 0:
            return

        cv_img = surface2mat(img)
        selected = [lb.getLabelIO(self.image_rect[:2])
                    for lb in self.selected_labels]
        labels = correctLabels(cv_img, selected)

        # clear selected labels
        for lb in self.selected_labels:
            lb.kill()
        self.labels = list(filter(lambda lb: lb.alive, self.labels))
        self.selected_labels = []

        # add corrected labels
        for label_io in labels:
            self._addLabelByIO(label_io)
        self._saveToMemento()

    # -------------------- select -------------------- #
    def _selectedAppend(self, label: Label) -> None:
        if label not in self.selected_labels:
            self.selected_labels.append(label)
            label.contour.select()
            label.icon.select()

    def _selectedRemove(self, label: Label) -> None:
        if label in self.selected_labels:
            self.selected_labels.remove(label)
            label.contour.unselect()
            label.icon.unselect()

    def _selectedRemoveAll(self) -> None:
        for label in self.selected_labels:
            label.contour.unselect()
            label.icon.unselect()
        self.selected_labels = []

    def selectAll(self) -> None:
        self._selectedRemoveAll()
        for label in self.labels:
            self._selectedAppend(label)

    # -------------------- save & load -------------------- #
    def _saveToMemento(self) -> None:
        mem = LabelsMemeto()
        mem.curr_type_id = self.curr_type_id

        for lb in self.labels:
            mem.labels.append(lb.getLabelIO(self.image_rect[:2]))

        for label in self.selected_labels:
            mem.selected_incidies.append(self.labels.index(label))

        # make change to history
        if self.history_index < len(self.history):
            self.history = self.history[:self.history_index]
        self.history.append(mem)
        self.history_index += 1

    def _loadFromMemento(self, mem: LabelsMemeto) -> None:
        # clear current labels
        for lb in self.labels:
            lb.kill()
        self.removeDead()
        self.labels = []
        self.selected_labels = []
        if self.adding_label is not None:
            self.adding_label.kill()
            self.adding_label = None
            self.adding_point = None

        # load labels
        self.curr_type_id = mem.curr_type_id
        for i, lb_io in enumerate(mem.labels):
            self._addLabelByIO(lb_io)
        for i in mem.selected_incidies:
            self._selectedAppend(self.labels[i])

    def undo(self) -> None:
        if self.history_index <= 1:
            return
        # history_index >= 2
        self.history_index -= 1
        self._loadFromMemento(self.history[self.history_index - 1])

    def redo(self) -> None:
        if self.history_index >= len(self.history):
            return
        self._loadFromMemento(self.history[self.history_index])
        self.history_index += 1

    def _loadFromFile(self, path: str = None) -> None:
        if path is None:
            return
        for label_io in loadLabel(path):
            self._addLabelByIO(label_io)

    def saveToFile(self) -> None:
        labels = [lb.getLabelIO(self.image_rect[:2]) for lb in self.labels]
        saveLabel(self.label_path, labels)

    # -------------------- base -------------------- #
    def kill(self) -> None:
        self.saveToFile()

        for label in self.labels:
            label.kill()
        self.removeEvents(target=str(id(self)))
        self.labels = None
        self.selected_labels = None
        self.dragging_point= None
        self.adding_label = None
        self.adding_point = None
        self.on_single_select = None
        super().kill()

    def update(self, events=None) -> None:
        super().update(events)
        self.key_ctrl_pressed = pygame.key.get_pressed()[locals.K_LCTRL] \
                             or pygame.key.get_pressed()[locals.K_RCTRL]

    def addKeydownEvent(self, key: int, func: Callable[..., Any], once=False) -> None:
        return super().addKeydownEvent(key, func, str(id(self)), once)
    def addKeyCtrlEvent(self, key: int, func: Callable[..., Any], once=False) -> None:
        return super().addKeyCtrlEvent(key, func, str(id(self)), once)
    def addKeyPressEvent(self, key: int, func: Callable[..., Any], once=False) -> None:
        return super().addKeyPressEvent(key, func, str(id(self)), once)
    def addKeyReleaseEvent(self, key: int, func: Callable[..., Any], once=False) -> None:
        return super().addKeyReleaseEvent(key, func, str(id(self)), once)

    def onLeftClick(self, x: int, y: int) -> None:
        # click on white space to unselet all labels
        for lb in self.labels:
            if lb.contour.hover or lb.icon.active:
                return
        self._selectedRemoveAll()

    def onLeftDrag(self, vx: int, vy: int) -> None:
        if vx == 0 and vy == 0:
            return

        if self.adding_label is not None:
            return

        if self.dragging_point is not None:
            self.dragging_point.move(vx, vy)

    def onLeftRelease(self) -> None:
        if self.dragging_point is not None:
            self.dragging_point.unselect()
            self.dragging_point = None
            self._saveToMemento()

    def onHover(self, x: int, y: int) -> None:
        if self.adding_point is not None:
            self.adding_point.setCenterByCanvasPos(x, y)

    def offHover(self) -> None:
        if self.dragging_point is not None:
            self.dragging_point.unselect()
            self.dragging_point = None
            self._saveToMemento()