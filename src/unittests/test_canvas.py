import pygame
from pygame import Surface as pg_Surface
from pygame import locals

from ..components.canvas import canvas, image, label
from ..pygame_gui import UIMain
from ..utils.gamma import gammaTransformation


class TestCanvas_Surface(canvas.CanvasComponent):
    def __init__(self, w, h, x, y, color):
        super().__init__(w, h, x, y)
        self.color = color

    def draw(self, surface: pg_Surface) -> None:
        w, h = self.getDisplaySize()
        x, y = self.getDisplayPos()
        pygame.draw.rect(surface, self.color, (x, y, w, h))

class TestCanvas_CanvasComponent(UIMain):
    def __init__(self):
        super().__init__((1280, 720))

        surf1 = TestCanvas_Surface(640, 480, 0, 0, (200, 128, 128))
        surf2 = TestCanvas_Surface(200, 150, 50, 50, (128, 128, 200))
        canv = canvas.Canvas(
            640, 480, 320, 120,
            main_component=surf2,
            default_align=True,
            margin_x=100,
            margin_y=10,
            smooth_factor=0.8
        )

        canv.setBackgroundColor((128, 128, 128))

        canv.addChild(surf1)
        canv.addChild(surf2)
        self.screen.addChild(canv)

def test_Canvas_CanvasComponent():
    demo = TestCanvas_CanvasComponent()
    demo.run()

class TestCanvas_Image(UIMain):
    def __init__(self):
        super().__init__((1280, 720))

        def preproc_func(img):
            return gammaTransformation(img, 0.5)
        img = image.Image(
            'resources/test_dataset/images/00.jpg',
            (640, 480),
            preproc_func
        )
        canv = canvas.Canvas(
            640, 480, 320, 120,
            main_component=img,
            default_align=True,
            margin_x=50,
            margin_y=50,
            smooth_factor=0.8
        )

        canv.setBackgroundColor((128, 128, 128))

        canv.addKeydownEvent(locals.K_a, img.switchProc)

        canv.addChild(img)
        self.screen.addChild(canv)

def test_Canvas_Image():
    demo = TestCanvas_Image()
    demo.run()

class TestCanvas_Label_Keypoint(UIMain):
    def __init__(self):
        super().__init__((1280, 720))

        def on_click():
            print('clicked')
        img = image.Image('resources/test_dataset/images/00.jpg', (1000, 700))
        kpt = label.Keypoint(img.w // 2, img.h // 2, on_click)
        canv = canvas.Canvas(
            1000, 700, 10, 10,
            main_component=img,
            margin_x=100,
            margin_y=100,
            smooth_factor=0.8
        )

        canv.setBackgroundColor((128, 128, 128))

        canv.addChild(img)
        canv.addChild(kpt)
        self.screen.addChild(canv)

def test_Canvas_Label_Keypoint():
    demo = TestCanvas_Label_Keypoint()
    demo.run()

class TestCanvas_Labels(UIMain):
    def __init__(self):
        super().__init__((1280, 720))

        img = image.Image('resources/test_dataset/images/00.jpg', (1000, 700))
        canv = canvas.Canvas(
            1000, 700, 10, 10,
            main_component=img,
            margin_x=200,
            margin_y=150,
            smooth_factor=0.8
        )
        labels = label.Labels(
            img._w, img._h, 0, 0, canv,
            keypoint_size=4,
            label_path='resources/test_dataset/labels/00.txt'
        )
        labels.addKeydownEvent(locals.K_0, lambda: labels.setSelectedType(0))
        labels.addKeydownEvent(locals.K_1, lambda: labels.setSelectedType(1))
        labels.addKeydownEvent(locals.K_2, lambda: labels.setSelectedType(2))

        canv.setBackgroundColor((128, 128, 128))

        self.screen.addChild(canv)
        canv.addChild(img)
        canv.addChild(labels)

def test_Canvas_Labels():
    demo = TestCanvas_Labels()
    demo.run()