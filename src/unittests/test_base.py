import pygame
from pygame import locals

from ..pygame_gui import BaseComponent


class TestRoot(BaseComponent):
    def __init__(self):
        super().__init__(1280, 720, is_root=True)

    def onLeftClick(self, x: int, y: int):
        print(f'left click on root <{x}, {y}>')

    def draw(self, surface: pygame.Surface):
        for ch in self.child_components:
            ch.draw(surface)

class TestClick(BaseComponent):
    def __init__(self):
        super().__init__(100, 100, 50, 20)

    def onLeftClick(self, x: int, y: int):
        print(f'left click on child <{x}, {y}>')

    def onMidClick(self, x: int, y: int):
        print(f'mid click on child <{x}, {y}>')

    def onRightClick(self, x: int, y: int):
        print(f'right click on child <{x}, {y}>')

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.w, self.h))

class TestCtrl(BaseComponent):
    def __init__(self):
        super().__init__()

        def save():
            print('save')
        def copy():
            print('copy')
        def paste():
            print('paste')

        self.addKeyCtrlEvent(locals.K_s, save)
        self.addKeyCtrlEvent(locals.K_c, copy)
        self.addKeyCtrlEvent(locals.K_v, paste)


class TestBaseComponent:
    def __init__(self, w = 640, h = 640):
        pygame.init()
        self.screen = pygame.display.set_mode((w, h), pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        self.root = TestRoot()

        click = TestClick()
        ctrl = TestCtrl()
        self.root.addChild(click)
        self.root.addChild(ctrl)

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return

            self.root.update(events)
            self.root.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

def test_BaseComponent():
    demo = TestBaseComponent()
    demo.run()