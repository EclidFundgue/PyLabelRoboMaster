from typing import Callable

from .. import pygame_gui as ui


class Navigator(ui.components.RectContainer):
    '''
    Navigator(
        w, h, x, y,
        images_folder,
        on_back,
        on_undo,
        on_redo,
        on_open
    )

    Methods:
    * setFolder(folder) -> None
    * resetState() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        images_folder: str,
        on_back: Callable[[], None] = None,
        on_undo: Callable[[], None] = None,
        on_redo: Callable[[], None] = None,
        on_open: Callable[[], None] = None
    ):
        super().__init__(w, h, x, y)

        button_size = int(h * 0.9)
        button_y = (h - button_size) // 2

        self.images_folder_label = ui.components.Label(
            w=w-(3*button_size+80)-int(h*1.5),
            h=h,
            x=3*button_size+80,
            y=0,
            text=images_folder
        )
        button_undo = ui.components.IconButton(
            w=button_size,
            h=button_size,
            x=20,
            y=button_y,
            icon='resources/icons/undo.png',
            on_press=on_undo,
            cursor_change=True
        )
        button_redo = ui.components.IconButton(
            w=button_size,
            h=button_size,
            x=button_size+40,
            y=button_y,
            icon='resources/icons/redo.png',
            on_press=on_redo,
            cursor_change=True
        )
        button_open = ui.components.IconButton(
            w=button_size,
            h=button_size,
            x=2*button_size+60,
            y=button_y,
            icon='resources/icons/open_file.png',
            on_press=on_open,
            cursor_change=True
        )
        color_theme = ui.color.LightColorTheme()
        button_back = ui.components.CloseButton(
            w=int(h*1.5),
            h=h,
            x=w-int(h*1.5),
            y=0,
            color=ui.color.dark(color_theme.Surface,3),
            cross_color=color_theme.OnSurface,
            on_press=on_back
        )

        self.alignVerticalCenter(button_undo)
        self.alignVerticalCenter(button_redo)

        self.addChild(self.images_folder_label)
        self.addChild(button_back)
        self.addChild(button_undo)
        self.addChild(button_redo)
        self.addChild(button_open)

        self.button_back = button_back

    def setFolder(self, folder: str) -> None:
        self.images_folder_label.setText(folder)

    def resetState(self) -> None:
        '''This is called when page change.'''
        self.button_back.resetState()

    def onResize(self, w, h, x, y):
        self.button_back.onResize(
            self.button_back.w,
            self.button_back.h,
            w-int(h*1.5),
            0
        )
        self.w = w
        self.h = h
        self.x = x
        self.y = y