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
    '''It's a mysterious ritual to summon icon.'''
    data = (
        b'9EF2\xbf|EF/.>EF:13E06-12+E3616\xe1G8<21\x01:G\x8183109F2+710|F70710/F90?10'
        b'30680.10223* G462,0-G,624\x01)G362422G3)24/3GC>3GC<7GABBB3\xe324<E3\xf324<8'
        b'\x08F;24D80724D80324D80224D8BBBBAC<7GC<3GC>3G362432G,6246)G462,0-G\x08223*0'
        b'G030280.10/F90?10<F?0710xF3+710:G\x81:316\xe1G8|2125G97613*E2-1/EF:1<EF>.'
    )
    p1 = enumerate([b'CD1'*8,b'C<E',b'3524',b'<?1',b'000',b'00',b'11'], 65)
    p2 = enumerate([131,128,192,14,193,127,30,0,255,7,15,12,195,3,31,224,248,240], 41)
    for i, v in [(i, n) for i, n in p1] + [(i, bytes([n])) for i, n in p2]:
        data = data.replace(bytes([i]), v)
    b = bytearray()
    [[b.extend((255-v,v,v,v)) for v in (255*(n>>7-j&1) for j in range(8))] for n in data]
    return pygame.image.frombuffer(b, (64, 64), 'ARGB')

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