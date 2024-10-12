import os

from pygame import locals

from ..components.canvas.label import Label
from ..components.label_controllder import LabelController
from ..components.scroll.line import (DesertedFileLine, ImageFileLine,
                                      _GenericFileLine)
from ..components.stacked_page import StackedPage
from ..components.toolbar import ToolBar
from ..global_vars import VarArmorLabels
from ..pygame_gui import Button
from ..resources_loader import ConfigLoader, ImageLoader


class ArmorPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        self.page_incides = page_incides

        cfg_loader = ConfigLoader()
        img_loader = ImageLoader()
        # global variables
        self.var_armor_labels = VarArmorLabels(
            cfg_loader['user_data'],
            cfg_loader['image_folder'],
            cfg_loader['label_folder'],
            cfg_loader['deserted_image_folder']
        )
        # components
        self.toolbar = ToolBar(
            1000, 0,
            on_add=self.toolbar_onAdd,
            on_delete=self.toolbar_onDelete,
            on_undo=self.toolbar_onUndo,
            on_redo=self.toolbar_onRedo,
            on_find=self.toolbar_onFind,
            on_correct=self.toolbar_onCorrect,
            on_save=self.toolbar_onSave,
            on_switch_preproc=self.toolbar_onSwitchPreproc,
            on_switch_auto=self.toolbar_onSwitchAuto,
            on_type_change=self.toolbar_onTypeChange,
            on_scroll_page_change=self.toolbar_onScrollPageChange,
            on_scroll_select=self.toolbar_onScrollSelect,
            on_scroll_desert=self.toolbar_onScrollDesert,
            on_scroll_restore=self.toolbar_onScrollRestore,
            on_navigator_prev=self.toolbar_onNavigatorPrev,
            on_navigator_next=self.toolbar_onNavigatorNext
        )
        self.label_controller = LabelController(
            1000, 840, 0, 0,
            on_single_select=self.canvas_onSingleSelect
        )

        self.back_button = Button(
            32, 32, 1230, 20,
            image=img_loader['button']['back'],
            pressed_image=img_loader['button']['back_pressed'],
            on_press=self.onBack,
            cursor_change=True
        )

        # -------------------- configure components --------------------
        self.toolbar.setBackgroundColor((219, 226, 239))
        self.toolbar.scroll_box.reloadByGlobalVar()
        self._reloadNavigator()
        self.label_controller.getCanvas().setBackgroundColor((17, 45, 78))
        self.label_controller.reload()
        self.back_button.layer = 10

        # -------------------- add event listeners --------------------
        self.addKeydownEvent(locals.K_q, self.keyboard_PrevImage)
        self.addKeydownEvent(locals.K_e, self.keyboard_NextImage)
        self.addKeydownEvent(locals.K_f, self.keyboard_Relabel)
        self.addKeydownEvent(locals.K_c, self.keyboard_Correct)
        self.addKeydownEvent(locals.K_ESCAPE, self.keyboard_UnselectAll)
        self.addKeydownEvent(locals.K_0, lambda: self.keyboard_TypeChange(0))
        self.addKeydownEvent(locals.K_1, lambda: self.keyboard_TypeChange(1))
        self.addKeydownEvent(locals.K_2, lambda: self.keyboard_TypeChange(2))
        self.addKeydownEvent(locals.K_3, lambda: self.keyboard_TypeChange(3))
        self.addKeydownEvent(locals.K_4, lambda: self.keyboard_TypeChange(4))
        self.addKeydownEvent(locals.K_5, lambda: self.keyboard_TypeChange(5))
        self.addKeydownEvent(locals.K_6, lambda: self.keyboard_TypeChange(6))
        self.addKeydownEvent(locals.K_7, lambda: self.keyboard_TypeChange(7))
        self.addKeydownEvent(locals.K_b, lambda: self.keyboard_ColorChange(0))
        self.addKeydownEvent(locals.K_r, lambda: self.keyboard_ColorChange(1))
        self.addKeyCtrlEvent(locals.K_f, self.keyboard_SwitchAuto)

        # -------------------- succeed management --------------------
        self.addChild(self.toolbar)
        self.addChild(self.label_controller.getCanvas())
        self.addChild(self.back_button)

    def _reloadNavigator(self) -> None:
        page = self.toolbar.scroll_box.pages[self.var_armor_labels.curr_page]
        image_path = self.var_armor_labels.getCurrentImagePath()

        if image_path is None:
            self.toolbar.navigator.setInfomation(filename='', idx=0, num=0)
            return

        image_file = os.path.split(image_path)[1]
        self.toolbar.navigator.setInfomation(
            filename=image_file,
            idx=page.getSelectedIndex(),
            num=page.getFileNumber()
        )

    def onBack(self) -> None:
        self.setPage(self.page_incides['main_menu'])

    def keyboard_PrevImage(self) -> None:
        self.toolbar.scroll_box.selectPrev()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def keyboard_NextImage(self) -> None:
        self.toolbar.scroll_box.selectNext()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def keyboard_TypeChange(self, type_id: int) -> None:
        self.var_armor_labels.setType(type_id)
        self.toolbar.type_box.setType(self.var_armor_labels.curr_type)
        self.label_controller.setSelectedType(self.var_armor_labels.curr_type)

    def keyboard_ColorChange(self, color_id: int) -> None:
        self.var_armor_labels.setColor(color_id)
        self.toolbar.type_box.setType(self.var_armor_labels.curr_type)
        self.label_controller.setSelectedType(self.var_armor_labels.curr_type)

    def keyboard_Relabel(self) -> None:
        self.label_controller.relable()

    def keyboard_Correct(self) -> None:
        self.label_controller.correct()

    def keyboard_UnselectAll(self) -> None:
        self.label_controller.unselectAll()

    def keyboard_SwitchAuto(self) -> None:
        if self.var_armor_labels.auto_labeling:
            self.var_armor_labels.auto_labeling = False
            self.toolbar.swch_auto.turnOff()
        else:
            self.var_armor_labels.auto_labeling = True
            self.toolbar.swch_auto.turnOn()

    def toolbar_onAdd(self) -> None:
        self.label_controller.startAdd()

    def toolbar_onDelete(self) -> None:
        self.label_controller.deleteSelected()

    def toolbar_onUndo(self) -> None:
        self.label_controller.undo()

    def toolbar_onRedo(self) -> None:
        self.label_controller.redo()

    def toolbar_onFind(self) -> None:
        self.label_controller.relable()

    def toolbar_onCorrect(self) -> None:
        self.label_controller.correct()

    def toolbar_onSave(self) -> None:
        self.label_controller.save()

    def toolbar_onSwitchPreproc(self, state: bool) -> None:
        self.label_controller.switchPreprocess(state)

    def toolbar_onSwitchAuto(self, state: bool) -> None:
        self.var_armor_labels.auto_labeling = state

    def toolbar_onTypeChange(self, type_id: int) -> None:
        self.var_armor_labels.curr_type = type_id
        self.label_controller.setSelectedType(type_id)

    def toolbar_onScrollPageChange(self, page_id: int) -> None:
        self.var_armor_labels.setPage(page_id)
        self._reloadNavigator()
        self.label_controller.reload()

    def toolbar_onScrollSelect(self, idx: int, file_line: _GenericFileLine) -> None:
        self.var_armor_labels.select(file_line.filename)
        self._reloadNavigator()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def toolbar_onScrollDesert(self, idx: int, file_line: ImageFileLine) -> None:
        self.var_armor_labels.delete(file_line.filename)
        self.toolbar.scroll_box.addLine(1, DesertedFileLine(
            file_line.w, file_line.h, file_line.filename
        ))
        self.var_armor_labels.saveUserData()

    def toolbar_onScrollRestore(self, idx: int, file_line: DesertedFileLine) -> None:
        self.var_armor_labels.restore(file_line.filename)
        self.toolbar.scroll_box.addLine(0, ImageFileLine(
            file_line.w, file_line.h, file_line.filename
        ))

    def toolbar_onNavigatorPrev(self) -> None:
        self.toolbar.scroll_box.selectPrev()
        self._reloadNavigator()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def toolbar_onNavigatorNext(self) -> None:
        self.toolbar.scroll_box.selectNext()
        self._reloadNavigator()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def canvas_onSingleSelect(self, label: Label) -> None:
        self.toolbar.type_box.setType(label.type_id)

    def kill(self) -> None:
        self.toolbar = None
        self.label_controller = None
        super().kill()