from typing import Callable

from .. import pygame_gui as ui
from ..components.light_bar import LightBar


class ToolbarButtons(ui.components.RectContainer):
    '''
    ToolbarButtons(
        w, h, x, y,
        on_add,
        on_delete,
        on_save,
        on_search,
        on_correct,
        turn_light,
        turn_auto
    )
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_add: Callable[[], None] = None,
        on_delete: Callable[[], None] = None,
        on_save: Callable[[], None] = None,
        on_search: Callable[[], None] = None,
        on_correct: Callable[[], None] = None,
        on_autoplay: Callable[[bool], None] = None,
        on_light_change: Callable[[float], None] = None
    ):
        super().__init__(w, h, x, y)

        bs = w // 4 - 10 # button size
        button_rects = {
            'add': (bs, bs, 20, 15), # (0, 0)
            'delete': (bs, bs, bs+40, 15), # (0, 1)
            'save': (bs, bs, 2*bs+60, 15), # (0, 2)
            'search': (bs, bs, 20, bs+30), # (1, 0)
            'correct': (bs, bs, bs+40, bs+30), # (1, 1)
            'auto': (bs, bs, 2*bs+60, bs+30), # (1, 2)
            'light': (w-20, 30, 20, 2*bs+50), # (2, 0)
        }

        button_add = ui.components.IconButton(
            *button_rects['add'],
            'resources/icons/add.png',
            on_press=on_add,
            cursor_change=True
        )
        button_delete = ui.components.IconButton(
            *button_rects['delete'],
            'resources/icons/delete.png',
            on_press=on_delete,
            cursor_change=True
        )
        button_save = ui.components.IconButton(
            *button_rects['save'],
            'resources/icons/save.png',
            on_press=on_save,
            cursor_change=True
        )
        button_search = ui.components.IconButton(
            *button_rects['search'],
            'resources/icons/search.png',
            on_press=on_search,
            cursor_change=True
        )
        button_correct = ui.components.IconButton(
            *button_rects['correct'],
            'resources/icons/correct.png',
            on_press=on_correct,
            cursor_change=True
        )
        button_auto = ui.components.IconButton(
            *button_rects['auto'],
            'resources/icons/autoplay.png',
            on_press=on_autoplay,
            cursor_change=True
        )
        light_bar = LightBar(
            *button_rects['light'],
            on_change=on_light_change
        )

        self.addChild(button_add)
        self.addChild(button_delete)
        self.addChild(button_search)
        self.addChild(button_save)
        self.addChild(button_correct)
        self.addChild(button_auto)
        self.addChild(light_bar)