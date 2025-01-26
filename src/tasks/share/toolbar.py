from typing import Callable

from ... import pygame_gui as ui
from ...components.switch import Switch


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
        on_add: Callable[[], None],
        on_delete: Callable[[], None],
        on_save: Callable[[], None],
        on_search: Callable[[], None],
        on_correct: Callable[[], None],
        turn_light: Callable[[bool], None],
        turn_auto: Callable[[bool], None]
    ):
        super().__init__(w, h, x, y)

        button_rects = {
            'add': (32, 32, 20, 20), # (0, 0)
            'delete': (32, 32, 70, 20), # (0, 1)
            'save': (32, 32, 120, 20), # (0, 2)
            'search': (32, 32, 20, 70), # (1, 0)
            'correct': (32, 32, 70, 70), # (1, 1)
            'light': (32, 32, 20, 120), # (2, 0)
            'auto': (86, 32, 70, 120), # (2, 1)
        }

        button_add = ui.components.IconButton(
            *button_rects['add'],
            './resources/buttons/add.png',
            './resources/buttons/add_pressed.png',
            on_press=on_add,
            cursor_change=True
        )
        button_delete = ui.components.IconButton(
            *button_rects['delete'],
            './resources/buttons/delete.png',
            './resources/buttons/delete_pressed.png',
            on_press=on_delete,
            cursor_change=True
        )
        button_save = ui.components.IconButton(
            *button_rects['save'],
            './resources/buttons/save.png',
            './resources/buttons/save_pressed.png',
            on_press=on_save,
            cursor_change=True
        )
        button_search = ui.components.IconButton(
            *button_rects['search'],
            './resources/buttons/search.png',
            './resources/buttons/search_pressed.png',
            on_press=on_search,
            cursor_change=True
        )
        button_correct = ui.components.IconButton(
            *button_rects['correct'],
            './resources/buttons/correct.png',
            './resources/buttons/correct.png',
            on_press=on_correct,
            cursor_change=True
        )
        switch_preproc = Switch(
            *button_rects['light'],
            './resources/switchs/eye_open.png',
            './resources/switchs/eye_close.png',
            on_turn=turn_light,
        )
        switch_auto = Switch(
            *button_rects['auto'],
            './resources/switchs/auto_on.png',
            './resources/switchs/auto_off.png',
            on_turn=turn_auto,
        )

        self.addChild(button_add)
        self.addChild(button_delete)
        self.addChild(button_search)
        self.addChild(button_save)
        self.addChild(button_correct)
        self.addChild(switch_preproc)
        self.addChild(switch_auto)