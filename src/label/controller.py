from typing import Callable

from .. import pygame_gui as ui
from .image import Image
from .labels import Labels

# The input is class index of selected label
_OnSelected = Callable[[int], None]
_LabelsGetter = Callable[[int, int, int, int, _OnSelected], Labels]

class LabelController:
    '''
    LabelController(
        canvas,
        labels_getter,
        on_selected
    )
    * labels_getter(w, h, x, y) -> Labels
    * on_selected(class_index) -> None

    Methods:

    ---------- toolbar ----------
    * startAdd() -> None
    * cancelAdd() -> None
    * delete() -> None
    * relabel() -> None
    * correct() -> None
    * setLight(gamma) -> None
    * save() -> None

    ---------- class & selection ----------
    * setClass(cls_id) -> None
    * selectAll() -> None
    * unselectAll() -> None

    ---------- other ----------
    * reload(image_path, label_path, relabel) -> None
    * undo() -> None
    * redo() -> None
    '''
    def __init__(self,
        canvas: ui.components.Canvas,
        labels_getter: _LabelsGetter,
        on_selected: _OnSelected = None,
    ):
        self.canvas: ui.components.Canvas = canvas
        self.labels_getter: _LabelsGetter = labels_getter
        self.on_selected: _OnSelected = ui.utils.getCallable(on_selected)
        self.current_class_id = 0

        self.image: Image = None
        self.labels: Labels = None
        self.image_gamma: float = 0.0

        self.image_path: str = None
        self.label_path: str = None

    # ---------- toolbar ----------
    def startAdd(self) -> None:
        if self.labels is not None:
            self.labels.startAdd(self.current_class_id)

    def cancelAdd(self) -> None:
        if self.labels is not None:
            self.labels.cancelAdd()

    def delete(self) -> None:
        if self.labels is not None:
            self.labels.deleteSelectedLabels()

    def relable(self) -> None:
        if self.labels is not None:
            self.labels.relabel(self.image.orig_image)

    def correct(self) -> None:
        if self.labels is not None:
            self.labels.correctSelectedLabels(self.image.orig_image)

    def setLight(self, gamma: bool) -> None:
        self.image_gamma = gamma

        if self.image is None:
            return

        self.image.setLight(gamma)
        self.image.redraw()

    def save(self) -> None:
        if self.labels is None:
            return

        orig_size = self.image.orig_image.get_size()
        self.labels.save(self.label_path, orig_size)

    # ---------- class & selection ----------
    def setClass(self, cls_id: int) -> None:
        if self.labels is not None and cls_id != -1:
            self.labels.setSelectedClass(cls_id)
            self.current_class_id = cls_id

    def selectAll(self) -> None:
        if self.labels is not None:
            self.labels.selectAll()

    def unselectAll(self) -> None:
        if self.labels is not None:
            self.labels.unselectAll()

    # ---------- other ----------
    def _loadImage(self, path: str = None):
        if self.image is not None:
            self.image.kill()
            self.image = None
            self.image_path = None

        if path is None:
            return

        self.image_path = path
        self.image = Image(path)
        self.image.setLight(self.image_gamma)

        self.canvas.addChild(self.image)

    def _loadLabels(self, path: str = None):
        if self.labels is not None:
            self.labels.kill()
            self.labels = None
            self.label_path = None

        if self.image_path is None:
            return
        if self.image_path is not None and path is None:
            ui.logger.error(
                'Received image path, but label path is None.',
                ValueError, self
            )

        self.label_path = path
        self.labels = self.labels_getter(
            self.image._w+100,  # w
            self.image._h+100,  # h
            -50,                # x
            -50,                # y
            lambda cls_id: self.on_selected(cls_id) # on_selected
        )
        self.labels.load(path, self.image.getOrigSize())
        self.canvas.addChild(self.labels)

    def reload(self,
        image_path: str = None,
        label_path: str = None,
        relabel: bool = False
    ) -> None:
        self.save()
        self._loadImage(image_path)
        self._loadLabels(label_path)

        if self.image is None or self.labels is None:
            return
        if relabel:
            self.labels.relabel(self.image.orig_image)

    def undo(self) -> None:
        if self.labels is not None:
            self.labels.undo()

    def redo(self) -> None:
        if self.labels is not None:
            self.labels.redo()