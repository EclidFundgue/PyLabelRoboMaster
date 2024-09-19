import sys
from typing import Tuple, Union

import pygame
from pygame import Surface as pg_Surface

from .components.surface import BaseComponent, RootSurface
from .f___loger import fuck as f_error


def win32MovePygameWindow(position: Tuple[int, int]) -> None:
    from ctypes import windll
    hwnd = pygame.display.get_wm_info()['window']
    x, y = position
    w, h = pygame.display.get_surface().get_size()
    windll.user32.MoveWindow(hwnd, x, y, w, h, False)

def generateDefaultIcon() -> pg_Surface:
    img = pygame.Surface((32, 32))
    img.fill((0, 0, 0))
    img.set_colorkey((0, 0, 0))
    pygame.draw.circle(img, (255, 102, 102), (16, 16), 12)
    return img

class UIMain:
    '''
    A base class to initialize and run pygame loop. Default screen
    position is center.

    UIMain(size, fps, position, caption, icon)

    Methods:
    * run() -> None
    * onExit() -> None
    '''
    def __init__(self, size: Tuple[int, int], fps: int = 60,
                 position: Tuple[int, int] = None,
                 caption: str = 'default',
                 icon: Union[str, pg_Surface] = None):
        self.fps = fps

        pygame.init()

        # change screen initialize position
        if position is None:
            screen_info = pygame.display.Info()
            resolution = (screen_info.current_w, screen_info.current_h)
            position = ((resolution[0] - size[0]) // 2, (resolution[1] - size[1]) // 2)

        screen = pygame.display.set_mode(size)
        self.screen = RootSurface(screen)
        self.clock = pygame.time.Clock()

        # caption
        pygame.display.set_caption(caption)

        # icon
        if icon is None:
            icon = generateDefaultIcon()
        elif isinstance(icon, str):
            icon = BaseComponent.loadImage(self, icon)

        if isinstance(icon, pg_Surface):
            pygame.display.set_icon(icon)
        else:
            f_error(f'Invalid value of icon: {icon}', ValueError, self)

        # position
        if sys.platform == 'win32':
            win32MovePygameWindow(position)

    def onExit(self) -> None:
        self.screen.kill()

    def run(self) -> None:
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.onExit()
                    return

            self.screen.update(events)
            self.screen.draw()

            pygame.display.flip()
            self.clock.tick(self.fps)

class _UIMainDemo(UIMain):
    '''
    An example to use UIMain in your project. Use

    >>> main = _UIMainDemo()
    >>> main.run()

    to run.
    '''
    def __init__(self):
        super().__init__((640, 640))
        
        from .components.surface import Surface

        # create variables
        navigater = Surface(640, 40, 0, 0)
        canvas = Surface(440, 600, 0, 40)
        control = Surface(200, 600, 440, 40)

        # configure variables
        navigater.setBackgroundColor((190, 190, 220))
        canvas.setBackgroundColor((255, 255, 255))
        control.setBackgroundColor((190, 190, 190))

        # succeed management
        self.screen.addChild(navigater)
        self.screen.addChild(canvas)
        self.screen.addChild(control)