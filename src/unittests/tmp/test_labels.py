from pygame import Surface, locals

from ..components import image, label
from ..constants import ResourcesPath
from ..pygame_gui import Surface
from ._test import MessagePrint, MyTest


class TempImageContainer(Surface):
    def __init__(self, img: image.Image):
        super().__init__(1280, 720, 0, 0)
        self.setBackgroundColor((255, 255, 255))
        self.addChild(img)
        self.img = img
        self.gamma = 1.0

    def onRightDrag(self, dx: int, dy: int):
        self.img.move(dx, dy)

    def onMouseWheel(self, x: int, y: int, v: int):
        r = self.img.scale_rate + 0.2 * v * self.img.scale_rate
        self.img.scale(r, (x - self.img.x, y - self.img.y))

class KeypointsHandler(Surface):
    def __init__(self, pos_manager: image.PotisionManager):
        super().__init__(1280, 720, 0, 0)
        self.pos_manager = pos_manager
        self.cvt = label.PosConvertor(*pos_manager.getRect())
        self.kpt = label.Keypoint(0.5, 0.5, self.cvt)

        pos_manager.addObserver(self.cvt)
        self.addChild(self.kpt)
        self.addChild(self.cvt)

    def kill(self) -> None:
        self.pos_manager = None
        self.cvt = None
        self.kpt = None
        return super().kill()

class TestKeypoints(MyTest):
    def __init__(self):
        super().__init__(1280, 720)

        img = image.Image(ResourcesPath().DATASET_00, False)
        surf = TempImageContainer(img)
        pos = image.PotisionManager(img)
        kpt_handler = KeypointsHandler(pos)

        self.screen.addChild(surf)
        self.screen.addChild(pos)
        self.screen.addChild(kpt_handler)

def test_Keypoints():
    demo = TestKeypoints()
    demo.run()


class ContourHandler(Surface):
    def __init__(self, pos_manager: image.PotisionManager):
        super().__init__(1280, 720, 0, 0)
        self.pos_manager = pos_manager
        self.cvt = label.PosConvertor(*pos_manager.getRect())
        self.cnt = label.Contour(4)
        printer = MessagePrint()
        kpts = [
            label.Keypoint(0.5, 0.5, self.cvt),
            label.Keypoint(0.5, 0.7, self.cvt),
            label.Keypoint(0.7, 0.6, self.cvt),
            label.Keypoint(0.72, 0.5, self.cvt)
        ]

        for p in kpts:
            self.addChild(p)
            self.cnt.addKeypoint(p)
        self.addChild(self.cnt)
        self.addChild(self.pos_manager)
        self.addChild(printer)

        self.pos_manager.addObserver(self.cvt)
        self.cnt.addObserver(printer)

class TestContour(MyTest):
    def __init__(self):
        super().__init__(1280, 720)

        img = image.Image(ResourcesPath().DATASET_00, False)
        surf = TempImageContainer(img)
        pos = image.PotisionManager(img)
        handler = ContourHandler(pos)

        self.screen.addChild(surf)
        self.screen.addChild(pos)
        self.screen.addChild(handler)

def test_Contour():
    demo = TestContour()
    demo.run()


class LabelsHandler(Surface):
    def __init__(self, pos_manager: image.PotisionManager):
        super().__init__(1000, 720, 0, 0)
        self.pos_manager = pos_manager
        self.cvt = label.PosConvertor(*pos_manager.getRect())
        self.lb = label.LabelsManager(ResourcesPath().LABEL_00, self.cvt)
        printer = MessagePrint()

        self.addChild(self.lb)
        self.addChild(printer)

        self.lb.addObserver(printer)
        pos_manager.addObserver(self)
        self.pos_manager.addObserver(self.cvt)

        self.addKeydownEvent(locals.K_a, self.lb.add)
        self.addKeydownEvent(locals.K_d, self.lb.delete)
        self.addKeyCtrlEvent(locals.K_z, self.lb.restore)
        self.addKeyCtrlEvent(locals.K_y, self.lb.undoRestore)
        self.addKeydownEvent(locals.K_s, self.lb.save)

class TestLabels(MyTest):
    def __init__(self):
        super().__init__(1280, 720)

        img = image.Image(ResourcesPath().DATASET_00, False)
        surf = TempImageContainer(img)
        pos = image.PotisionManager(img)
        label = LabelsHandler(pos)

        self.screen.addChild(surf)
        self.screen.addChild(pos)
        self.screen.addChild(label)

def test_Labels():
    demo = TestLabels()
    demo.run()