from typing import Callable

from .. import pygame_gui as ui
from ..pygame_gui.components.canvas import Canvas
from ..utils import imgproc
from .canvas.image import Image
from .canvas.labels25 import Label25, Labels25


class LabelController25:
    '''
    LabelController(w, h, x, y, on_label_selected)

    Methods:
    * createCanvas(w, h, x, y) -> None
    * getCanvas() -> Canvas
    * reload(image_path, label_path, auto_labeling) -> None
    * relabel() -> None
    * correct() -> None
    * startAdd() -> None
    * cancelAdd() -> None
    * deleteSelected() -> None
    * setSelectedClass(cls_id) -> None
    * selectAll() -> None
    * unselectAll() -> None
    * undo() -> None
    * redo() -> None
    * save() -> None
    * switchPreprocess(state) -> None
    '''
    def __init__(self,
        canvas: Canvas,
        on_label_selected: Callable[[Label25], None] = None
    ):
        self.canvas = canvas
        self.on_label_selected = ui.utils.getCallable(on_label_selected)
        self.image: Image = None
        self.labels: Labels25 = None
        self.image_path: str = None
        self.label_path: str = None

    def _loadImage(self, path: str = None):
        preproc_state = False
        if self.image is not None:
            preproc_state = self.image.enable_proc
            self.image.kill()
            self.image = None
            self.image_path = None

        if path is None:
            return

        self.image_path = path
        self.image = Image(path, lambda img: imgproc.gammaTransformation(img, 0.5))
        if preproc_state:
            self.image.enableProc()

        self.canvas.addChild(self.image)

    def _loadLabels(self, path: str = None):
        if self.labels is not None:
            self.labels.kill()
            self.labels = None
            self.label_path = None

        if path is None or self.image is None:
            return

        self.label_path = path
        self.labels = Labels25(
            self.image._w+100, self.image._h+100,
            -50, -50,
            num_keypoints=4,
            on_select=self.on_label_selected
        )
        self.labels.load(path, (self.image._w, self.image._h))
        self.canvas.addChild(self.labels)

    def reload(self, image_path: str, label_path: str, auto_labeling: bool):
        self._loadImage(image_path)
        self._loadLabels(label_path)
        if auto_labeling:
            self.labels.relabel(self.image.orig_image)

    def relable(self):
        if self.labels is not None:
            self.labels.relabel(self.image.orig_image)

    def correct(self):
        if self.labels is not None:
            self.labels.correctSelectedLabels(self.image.orig_image)

    def startAdd(self):
        if self.labels is not None:
            self.labels.startAdd()

    def cancelAdd(self):
        if self.labels is not None:
            self.labels.cancelAdd()

    def deleteSelected(self):
        if self.labels is not None:
            self.labels.deleteSelectedLabels()

    def setSelectedClass(self, cls_id: int):
        if self.labels is not None and cls_id != -1:
            self.labels.setSelectedClass(cls_id)

    def selectAll(self):
        if self.labels is not None:
            self.labels.selectAll()

    def unselectAll(self):
        if self.labels is not None:
            self.labels.unselectAll()

    def undo(self):
        if self.labels is not None:
            self.labels.undo()

    def redo(self):
        if self.labels is not None:
            self.labels.redo()

    def save(self):
        if self.labels is not None:
            orig_size = self.image.orig_image.get_size()
            self.labels.saveToPath(self.label_path, orig_size)

    def switchPreprocess(self, state: bool) -> None:
        if self.image is not None:
            if state:
                self.image.enableProc()
            else:
                self.image.disableProc()
            self.image.redraw()