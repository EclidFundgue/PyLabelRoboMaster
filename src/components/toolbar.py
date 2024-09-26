from typing import Callable

from ..global_vars import VarArmorLabels
from ..pygame_gui import Button, Surface
from ..pygame_gui.decorators import getCallable
from ..resources_loader import ImageLoader
from .armor_type_select import ArmorIconsSelect
from .scroll.line import DesertedFileLine, ImageFileLine
from .scroll.line import _GenericFileLine as FileLine
from .scroll.navigator import Navigator
from .scroll.stackedview import StackedScrollView
from .switch import Switch, ThemeBasedSwitchTrigger


class ToolBar(Surface):
    '''
    A toolbar for the labeling interface.
    '''
    def __init__(self,
            x: int, y: int,
            on_add: Callable[[], None] = None,
            on_delete: Callable[[], None] = None,
            on_undo: Callable[[], None] = None,
            on_redo: Callable[[], None] = None,
            on_find: Callable[[], None] = None,
            on_correct: Callable[[], None] = None,
            on_save: Callable[[], None] = None,
            on_switch_preproc: Callable[[bool], None] = None,
            on_switch_auto: Callable[[bool], None] = None,
            on_type_change: Callable[[int], None] = None,
            on_scroll_page_change: Callable[[int], None] = None,
            on_scroll_select: Callable[[int, FileLine], None] = None,
            on_scroll_desert: Callable[[int, ImageFileLine], None] = None,
            on_scroll_restore: Callable[[int, DesertedFileLine], None] = None,
            on_navigator_prev: Callable[[], None] = None,
            on_navigator_next: Callable[[], None] = None):
        super().__init__(280, 840, x, y)

        rect_add = (32, 32, 150, 20) # (0, 2)
        rect_delete = (32, 32, 210, 20) # (0, 3)
        rect_undo = (32, 32, 30, 20) # (0, 0)
        rect_redo = (32, 32, 90, 20) # (0, 1)
        rect_find = (32, 32, 30, 80) # (1, 0)
        rect_correct = (32, 32, 90, 80) # (1, 1)
        rect_save = (32, 32, 150, 80) # (1, 2)
        rect_preproc = (32, 32, 30, 140) # (2, 0)
        rect_auto = (96, 32, 90, 140) # (2, 1)

        img_loader = ImageLoader()
        self.btn_add = Button(*rect_add,
            img_loader['button']['add'],
            img_loader['button']['add_pressed'],
            on_press=getCallable(on_add),
            cursor_change=True
        )
        self.addChild(self.btn_add)

        self.btn_delete = Button(*rect_delete,
            img_loader['button']['delete'],
            img_loader['button']['delete_pressed'],
            on_press=getCallable(on_delete),
            cursor_change=True
        )
        self.addChild(self.btn_delete)

        self.btn_undo = Button(*rect_undo,
            img_loader['button']['undo'],
            img_loader['button']['undo_pressed'],
            on_press=getCallable(on_undo),
            cursor_change=True
        )
        self.addChild(self.btn_undo)

        self.btn_redo = Button(*rect_redo,
            img_loader['button']['redo'],
            img_loader['button']['redo_pressed'],
            on_press=getCallable(on_redo),
            cursor_change=True
        )
        self.addChild(self.btn_redo)

        self.btn_find = Button(*rect_find,
            img_loader['button']['search'],
            img_loader['button']['search_pressed'],
            on_press=getCallable(on_find),
            cursor_change=True
        )
        self.addChild(self.btn_find)

        self.btn_save = Button(*rect_save,
            img_loader['button']['save'],
            img_loader['button']['save_pressed'],
            on_press=getCallable(on_save),
            cursor_change=True
        )
        self.addChild(self.btn_save)

        self.btn_correct = Button(*rect_correct,
            img_loader['button']['correct'],
            img_loader['button']['correct_pressed'],
            on_press=getCallable(on_correct),
            cursor_change=True
        )
        self.addChild(self.btn_correct)

        self.swch_preproc = Switch(*rect_preproc,
            img_loader['switch']['eye_open'],
            img_loader['switch']['eye_close'],
            on_turn=getCallable(on_switch_preproc)
        )
        self.addChild(self.swch_preproc)

        self.swch_auto = Switch(*rect_auto,
            img_loader['switch']['auto_on'],
            img_loader['switch']['auto_off'],
            on_turn=getCallable(on_switch_auto)
        )
        self.addChild(self.swch_auto)

        self.type_box = ArmorIconsSelect(
            20, 250,
            on_select=getCallable(on_type_change)
        )
        self.addChild(self.type_box)

        var_path = VarArmorLabels()
        self.scroll_box = StackedScrollView(
            240, 320, 20, 490,
            200, 30,
            var_path.image_folder,
            var_path.deserted_folder,
            on_page_changed=getCallable(on_scroll_page_change),
            on_select=getCallable(on_scroll_select),
            on_desert=getCallable(on_scroll_desert),
            on_restore=getCallable(on_scroll_restore)
        )
        self.addChild(self.scroll_box)

        self.navigator = Navigator(
            240, 30, 25, 450,
            num=self.scroll_box.getCurrentPageFileNumber(),
            font_color=(0, 0, 0),
            on_prev=getCallable(on_navigator_prev),
            on_next=getCallable(on_navigator_next)
        )
        self.addChild(self.navigator)

    def kill(self) -> None:
        self.btn_add = None
        self.btn_delete = None
        self.btn_undo = None
        self.btn_redo = None
        self.btn_find = None
        self.btn_correct = None
        self.btn_save = None
        self.swch_preproc = None
        self.swch_auto = None

        self.type_box = None
        self.scroll_box = None
        self.navigator = None
        super().kill()