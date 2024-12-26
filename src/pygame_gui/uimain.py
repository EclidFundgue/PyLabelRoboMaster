import sys
from typing import Tuple, Union

import pygame
from pygame import Surface

from . import components, logger


def win32MovePygameWindow(position: Tuple[int, int]) -> None:
    from ctypes import windll
    hwnd = pygame.display.get_wm_info()['window']
    x, y = position
    w, h = pygame.display.get_surface().get_size()
    windll.user32.MoveWindow(hwnd, x, y, w, h, False)

def generateDefaultIcon() -> Surface:
    img = pygame.Surface((32, 32))
    img.fill((0, 0, 0))
    img.set_colorkey((0, 0, 0))
    pygame.draw.circle(img, (255, 102, 102), (16, 16), 12)
    return img

class Main:
    '''
    Methods:
    * run() -> None
    * onExit() -> None
    '''
    def __init__(self,
        size: Tuple[int, int],
        caption: str = 'default',
        fps: int = 60,
        position: Tuple[int, int] = None,
        icon: Union[str, Surface] = None
    ):
        pygame.init()
        if position is None:
            screen_info = pygame.display.Info()
            resolution = (screen_info.current_w, screen_info.current_h)
            position = ((resolution[0] - size[0]) // 2, (resolution[1] - size[1]) // 2)

        self._setIcon(icon)
        pygame.display.set_mode(size)
        pygame.display.set_caption(caption)
        self._setPosition(position)

        self.fps: int = fps
        self.root: components.Root = components.Root()
        self.clock = pygame.time.Clock()

    def _setPosition(self, position: Tuple[int, int]) -> None:
        if sys.platform == 'win32':
            win32MovePygameWindow(position)

    def _setIcon(self, icon: Union[str, Surface] = None) -> None:
        if icon is None:
            icon = generateDefaultIcon()
        elif isinstance(icon, str):
            icon = pygame.image.load(icon)

        if isinstance(icon, Surface):
            pygame.display.set_icon(icon)
        else:
            logger.error(f'Invalid type of icon: {type(icon)}', TypeError, self)

    def onExit(self) -> None:
        self.root.kill()

    def run(self) -> None:
        self.root.redraw()
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.onExit()
                    return

            self.root.update(events)
            self.root.draw()
            self.clock.tick(self.fps)

'''
This is an example to use UIMain in your project:

import pygame_gui as ui

class Demo(ui.Main):
    def __init__(self):
        super().__init__((640, 640))

        # create variables
        navigater = ui.components.RectContainer(640, 40, 0, 0)
        canvas = ui.components.RectContainer(440, 600, 0, 40)
        control = ui.components.RectContainer(200, 600, 440, 40)

        # configure variables
        navigater.setBackgroundColor((190, 190, 220))
        canvas.setBackgroundColor((255, 255, 255))
        control.setBackgroundColor((190, 190, 190))

        # succeed management
        self.root.addChild(navigater)
        self.root.addChild(canvas)
        self.root.addChild(control)


if __name__ == '__main__':
    demo = Demo()
    demo.run()
'''