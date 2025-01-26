from typing import Callable

from .. import pygame_gui as ui


class Navigator(ui.components.RectContainer):
    '''
    Navigator(
        w, h, x, y,
        on_back,
        on_undo,
        on_redo,
        on_open
    )

    Methods:
    * resetState() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_back: Callable[[], None],
        on_undo: Callable[[], None],
        on_redo: Callable[[], None],
        on_open: Callable[[], None]
    ):
        super().__init__(w, h, x, y)

        button_undo = ui.components.IconButton(
            w=32,
            h=32,
            x=20,
            y=0,
            image='./resources/buttons/undo.png',
            pressed_image='./resources/buttons/undo_pressed.png',
            on_press=on_undo,
            cursor_change=True
        )
        button_redo = ui.components.IconButton(
            w=32,
            h=32,
            x=80,
            y=0,
            image='./resources/buttons/bush_gemer.png',
            pressed_image='./resources/buttons/bush_gemer_pressed.png',
            on_press=on_redo,
            cursor_change=True
        )
        button_open = ui.components.TextButton(
            w=80,
            h=h-10,
            x=140,
            y=5,
            text='open',
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

        self.addChild(button_back)
        self.addChild(button_undo)
        self.addChild(button_redo)
        self.addChild(button_open)

        self.button_back = button_back

    def resetState(self) -> None:
        '''This is called when page change.'''
        self.button_back.resetState()