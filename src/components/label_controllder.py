from typing import Callable

from ..global_vars import VarArmorLabels
from ..pygame_gui import getCallable
from ..utils.gamma import gammaTransformation
from .canvas.canvas import Canvas
from .canvas.image import Image
from .canvas.label import Label, Labels


class LabelController:
    '''
    LabelController(w: int, h: int, x: int, y: int)

    Methods:
    * getCanvas() -> Canvas
    * loadImage(path) -> None
    * loadLabels(path) -> None
    * reload() -> None
    * relabel() -> None
    * correct() -> None
    * startAdd() -> None
    * stopAdd() -> None
    * deleteSelected() -> None
    * setSelectedType(type: int) -> None
    * selectAll() -> None
    * unselectAll() -> None
    * undo() -> None
    * redo() -> None
    * save() -> None
    * switchPreprocess(state) -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            on_single_select: Callable[[Label], None] = None):
        self.canvas_size = (w, h)
        self.canvas = Canvas(
            w, h, x, y,
            margin_x=200,
            margin_y=200,
            smooth_factor=0.8
        )
        self.image: Image = None
        self.labels: Labels = None
        self.on_single_select = getCallable(on_single_select)

        self.var_armor_labels = VarArmorLabels()

    def getCanvas(self) -> Canvas:
        return self.canvas

    def loadImage(self, path: str = None):
        preproc_state = False
        if self.image is not None:
            preproc_state = self.image.enable_proc
            self.image.kill()
            self.image = None

        if path is None:
            return

        def preproc_func(img):
            return gammaTransformation(img, 0.5)
        self.image = Image(path, self.canvas_size, preproc_func)
        if preproc_state:
            self.image.enableProc()

        self.canvas.main_component = self.image
        self.canvas.addChild(self.image)
        self.canvas.alignCenter()

    def loadLabels(self, path: str = None):
        if self.labels is not None:
            self.labels.kill(only_self=False)
            self.labels = None

        if path is None or self.image is None:
            return

        self.labels = Labels(
            self.image._w, self.image._h, 0, 0,
            canvas=self.canvas,
            keypoint_size=4,
            label_path=path,
            on_single_select=self.on_single_select
        )
        self.canvas.addChild(self.labels)

    def reload(self):
        self.loadImage(
            self.var_armor_labels.getCurrentImagePath()
        )
        self.loadLabels(
            self.var_armor_labels.getCurrentLabelPath()
        )
        if self.var_armor_labels.auto_labeling:
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

    def stopAdd(self):
        if self.labels is not None:
            self.labels.stopAdd()

    def deleteSelected(self):
        if self.labels is not None:
            self.labels.deleteSelectedLabels()

    def setSelectedType(self, type: int):
        if self.labels is not None:
            self.labels.setSelectedType(type)

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
            self.labels.saveToFile()
    
    def switchPreprocess(self, state: bool) -> None:
        if self.image is not None:
            if state:
                self.image.enableProc()
            else:
                self.image.disableProc()