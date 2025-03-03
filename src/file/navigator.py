from typing import Callable, Union

import pygame

from .. import pygame_gui as ui


class Navigator(ui.components.RectContainer):
    '''
    Navigator(
        w, h, x, y,
        on_prev,
        on_next
    )
    * on_prev() -> None
    * on_next() -> None

    Methods:
    * setInfo(file_name, index, total_files) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_prev: Callable[[], None],
        on_next: Callable[[], None]
    ):
        super().__init__(w, h, x, y)

        img_arrow = ui.utils.loadImage('./resources/buttons/arrow.png')
        img_arrow_pressed = ui.utils.loadImage('./resources/buttons/arrow_pressed.png')

        button_prev = ui.components.IconButton(
            w=16,
            h=16,
            x=0,
            y=0,
            image=img_arrow,
            pressed_image=img_arrow_pressed,
            on_press=on_prev,
            cursor_change=True
        )
        button_next = ui.components.IconButton(
            w=16,
            h=16,
            x=w-16,
            y=0,
            image=pygame.transform.flip(img_arrow, True, False),
            pressed_image=pygame.transform.flip(img_arrow_pressed, True, False),
            on_press=on_next,
            cursor_change=True
        )
        self.filename_obj = ui.components.Label(
            w=w-32-70-10,
            h=16,
            x=16+10,
            y=0,
            text=''
        )
        self.index_obj = ui.components.Label(
            w=70,
            h=16,
            x=w-16-70,
            y=0,
            text=f'-/-'
        )

        self.alignVerticalCenter(button_prev)
        self.alignVerticalCenter(button_next)

        self.addChild(button_prev)
        self.addChild(button_next)
        self.addChild(self.filename_obj)
        self.addChild(self.index_obj)

    def setInfo(self, file_name: str, index: Union[int, str], total_files: Union[int, str]) -> None:
        self.filename_obj.setText(file_name)
        self.index_obj.setText(f'{index}/{total_files}')
    
    def kill(self):
        self.filename_obj = None
        self.index_obj = None
        super().kill()