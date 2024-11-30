from pygame import locals
import os

from .. import pygame_gui as ui
from ..components.canvas.label import Label
from ..components.label_controllder import LabelController
from ..components.scroll.line import (DesertedFileLine, ImageFileLine,
                                      _GenericFileLine)
from ..components.stacked_page import StackedPage
from ..global_vars import VarArmorLabels
from ..resources_loader import ConfigLoader, ImageLoader
from ..components.scroll.stackedview import StackedScrollView
from ..components.armor_type_select import ArmorIconsSelect
from ..components.scroll.navigator import Navigator as ToolbarNavigator


class ArmorPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        self.page_incides = page_incides

        # initialize basic variables
        color_theme = ui.color.LightColorTheme()
        img_loader = ImageLoader()
        cfg_loader = ConfigLoader()
        var_path = VarArmorLabels()

        border_width = 1
        navigator_h = 50
        canvas_w = 3 * w // 4

        self.label_controller = LabelController(
            self.canvas_onSingleSelect
        )
        self.var_armor_labels = VarArmorLabels(
            cfg_loader['user_data'],
            cfg_loader['image_folder'],
            cfg_loader['label_folder'],
            cfg_loader['deserted_image_folder']
        )

        # create components
        # on page
        navigator = ui.components.RectContainer(
            w=w,
            h=navigator_h - border_width,
            x=0,
            y=0
        )
        toolbar = ui.components.RectContainer(
            w=w - canvas_w - border_width,
            h=h - navigator_h,
            x=canvas_w,
            y=navigator_h
        )
        canvas = ui.components.RectContainer(
            w=canvas_w,
            h=h - navigator_h,
            x=0,
            y=navigator_h
        )
        border_navigator = ui.components.RectContainer(
            w=w,
            h=border_width,
            x=0,
            y=navigator_h - border_width
        )
        border_toolbar = ui.components.RectContainer(
            w=border_width,
            h=h - navigator_h,
            x=canvas_w,
            y=navigator_h - border_width
        )
        # on navigator
        button_undo = ui.components.Button(
            w=32,
            h=32,
            x=20,
            y=0,
            image=img_loader['button']['undo'],
            pressed_image=img_loader['button']['undo_pressed'],
            on_press=self.toolbar_onUndo,
            cursor_change=True
        )
        button_redo = ui.components.Button(
            w=32,
            h=32,
            x=80,
            y=0,
            image=img_loader['button']['redo'],
            pressed_image=img_loader['button']['redo_pressed'],
            on_press=self.toolbar_onRedo,
            cursor_change=True
        )
        self.button_back = ui.components.Button(
            w=32,
            h=32,
            x=w - 50,
            y=0,
            image=img_loader['button']['back'],
            pressed_image=img_loader['button']['back_pressed'],
            on_press=self.onBack,
            cursor_change=True
        )
        # on toolbar
        self.type_box = ArmorIconsSelect(
            x=20,
            y=270,
            on_select=self.toolbar_onTypeChange
        )
        self.scroll_box = StackedScrollView(
            240, 320, 20, 490,
            line_w=200,
            line_h=30,
            image_folder=var_path.image_folder,
            deserted_folder=var_path.deserted_folder,
            on_page_changed=self.toolbar_onScrollPageChange,
            on_select=self.toolbar_onScrollSelect,
            on_desert=self.toolbar_onScrollDesert,
            on_restore=self.toolbar_onScrollRestore
        )
        self.toolbar_navigator = ToolbarNavigator(
            240, 30, 25, 450,
            num=self.scroll_box.getCurrentPageFileNumber(),
            font_color=(0, 0, 0),
            on_prev=self.toolbar_onNavigatorPrev,
            on_next=self.toolbar_onNavigatorNext
        )

        # set component styles
        navigator.setBackgroundColor(color_theme.dark(color_theme.Surface, 3))
        toolbar.setBackgroundColor(color_theme.dark(color_theme.Surface, 2))
        canvas.setBackgroundColor(color_theme.Surface)
        border_navigator.setBackgroundColor(color_theme.Outline)
        border_toolbar.setBackgroundColor(color_theme.OutlineVariant)

        navigator.alignVerticalCenter(button_undo)
        navigator.alignVerticalCenter(button_redo)
        navigator.alignVerticalCenter(self.button_back)

        self.label_controller.createCanvas(canvas_w, h - navigator_h, 0, 0)

        # manage component hierarchy
        self.addChild(navigator)
        self.addChild(toolbar)
        self.addChild(canvas)
        self.addChild(border_navigator)
        self.addChild(border_toolbar)
        navigator.addChild(button_undo)
        navigator.addChild(button_redo)
        navigator.addChild(self.button_back)
        toolbar.addChild(self.type_box)
        toolbar.addChild(self.scroll_box)
        toolbar.addChild(self.toolbar_navigator)
        canvas.addChild(self.label_controller.getCanvas())

        # # components
        # self.toolbar = ToolBar(
        #     1000, 0,
        #     on_add=self.toolbar_onAdd,
        #     on_delete=self.toolbar_onDelete,
        #     on_undo=self.toolbar_onUndo,
        #     on_redo=self.toolbar_onRedo,
        #     on_find=self.toolbar_onFind,
        #     on_correct=self.toolbar_onCorrect,
        #     on_save=self.toolbar_onSave,
        #     on_switch_preproc=self.toolbar_onSwitchPreproc,
        #     on_switch_auto=self.toolbar_onSwitchAuto,
        #     on_type_change=self.toolbar_onTypeChange,
        #     on_scroll_page_change=self.toolbar_onScrollPageChange,
        #     on_scroll_select=self.toolbar_onScrollSelect,
        #     on_scroll_desert=self.toolbar_onScrollDesert,
        #     on_scroll_restore=self.toolbar_onScrollRestore,
        #     on_navigator_prev=self.toolbar_onNavigatorPrev,
        #     on_navigator_next=self.toolbar_onNavigatorNext
        # )

        # # -------------------- configure components --------------------
        # color_theme = ui.color.LightColorTheme()
        # self.toolbar.setBackgroundColor(color_theme.SurfaceVariant)
        # self.toolbar.scroll_box.reloadByGlobalVar()
        # self._reloadNavigator()
        # self.label_controller.getCanvas().setBackgroundColor(color_theme.Surface)
        # self.label_controller.reload()
        # self.back_button.layer = 10
        # self.setBackgroundColor(color_theme.SurfaceVariant)

        # add event listeners
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

    def _reloadNavigator(self) -> None:
        page = self.scroll_box.pages[self.var_armor_labels.curr_page]
        image_path = self.var_armor_labels.getCurrentImagePath()

        if image_path is None:
            self.toolbar_navigator.setInfomation(filename='', idx=0, num=0)
            return

        image_file = os.path.split(image_path)[1]
        self.toolbar_navigator.setInfomation(
            filename=image_file,
            idx=page.getSelectedIndex(),
            num=page.getFileNumber()
        )

    def onBack(self) -> None:
        self.setPage(self.page_incides['main_menu'])

    def keyboard_PrevImage(self) -> None:
        self.scroll_box.selectPrev()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def keyboard_NextImage(self) -> None:
        self.scroll_box.selectNext()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def keyboard_TypeChange(self, type_id: int) -> None:
        self.var_armor_labels.setType(type_id)
        self.type_box.setType(self.var_armor_labels.curr_type)
        self.label_controller.setSelectedType(self.var_armor_labels.curr_type)

    def keyboard_ColorChange(self, color_id: int) -> None:
        self.var_armor_labels.setColor(color_id)
        self.type_box.setType(self.var_armor_labels.curr_type)
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
        self.scroll_box.addLine(1, DesertedFileLine(
            file_line.w, file_line.h, file_line.filename
        ))
        self.var_armor_labels.saveUserData()

    def toolbar_onScrollRestore(self, idx: int, file_line: DesertedFileLine) -> None:
        self.var_armor_labels.restore(file_line.filename)
        self.scroll_box.addLine(0, ImageFileLine(
            file_line.w, file_line.h, file_line.filename
        ))

    def toolbar_onNavigatorPrev(self) -> None:
        self.scroll_box.selectPrev()
        self._reloadNavigator()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def toolbar_onNavigatorNext(self) -> None:
        self.scroll_box.selectNext()
        self._reloadNavigator()
        self.label_controller.reload()
        self.var_armor_labels.saveUserData()

    def canvas_onSingleSelect(self, label: Label) -> None:
        self.type_box.setType(label.type_id)

    def kill(self) -> None:
        self.toolbar = None
        self.label_controller = None
        super().kill()