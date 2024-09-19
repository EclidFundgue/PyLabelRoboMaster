from pygame import locals

from ..components import image
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

        def light_on():
            img.enableTransform()
        def light_off():
            img.disableTransform()
        def darker():
            self.gamma_add()
            img.setGamma(self.gamma)
        def lighter():
            self.gamma_sub()
            img.setGamma(self.gamma)
        
        self.addKeydownEvent(locals.K_o, light_on)
        self.addKeydownEvent(locals.K_f, light_off)
        self.addKeydownEvent(locals.K_a, darker)
        self.addKeydownEvent(locals.K_s, lighter)

    def gamma_add(self):
        self.gamma += 0.05

    def gamma_sub(self):
        self.gamma -= 0.05

    def onRightDrag(self, dx: int, dy: int):
        self.img.move(dx, dy)

    def onMouseWheel(self, x: int, y: int, v: int):
        r = self.img.scale_rate + 0.2 * v * self.img.scale_rate
        self.img.scale(r, (x - self.img.x, y - self.img.y))

class TestImage(MyTest):
    def __init__(self):
        super().__init__(1280, 720)

        surf = TempImageContainer(
            image.Image(ResourcesPath().DATASET_00, False)
        )
        gui = Surface(280, 720, 1000, 0)
        gui.setBackgroundColor((205, 205, 205))
        self.screen.addChild(surf)
        self.screen.addChild(gui)

def test_Image():
    demo = TestImage()
    demo.run()


class TestPosManager(MyTest):
    def __init__(self):
        super().__init__(1280, 720)

        img = image.Image(ResourcesPath().DATASET_00, False)
        surf = TempImageContainer(img)
        pos = image.PotisionManager(img)
        printer = MessagePrint()

        self.screen.addChild(surf)
        self.screen.addChild(pos)
        self.screen.addChild(printer)
        pos.addObserver(printer)

def test_PosManager():
    demo = TestPosManager()
    demo.run()