import os
from typing import Union

import pygame

from ... import pygame_gui as ui
from ...components.navigator import Navigator
from ...components.stacked_page import StackedPage
from ...components.toolbar import ToolbarButtons
from ...file import SelectionBox
from ...label import LabelController, Labels
from ...utils import imgproc
from ...utils.config import ConfigManager, openDir
from .armor_type_select import ArmorClassSelection
from .icon import getIcon


class ArmorPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)
        self.page_incides = page_incides
        self.initialized = False

    def onShow(self):
        if self.initialized:
            return
        self.initialized = True

        self.icon_class_id = -1

        self.images_folder = './resources/test_dataset/images'
        self.labels_folder = './resources/test_dataset/labels'
        self.deserted_folder = os.path.join(self.images_folder, 'deserted')

        self.config_manager = ConfigManager('./user_data.json')

        # ----- initialize basic constants -----
        color_theme = ui.color.LightColorTheme()

        w = self.w
        h = self.h
        navigator_h = 50
        canvas_w = w - 320
        toolbar_h = h - navigator_h
        scroll_h = int(toolbar_h * 0.4)
        scroll_w = w - canvas_w - 40

        # ----- create components -----
        canvas = ui.components.Canvas(
            w=canvas_w,
            h=h-navigator_h,
            x=0,
            y=navigator_h
        )
        def labels_getter(w, h, x, y, on_select) -> Labels:
            return Labels(
                w, h, x, y,
                num_keypoints=4,
                icon_getter=getIcon,
                on_select=on_select
            )
        self.label_controller = LabelController(
            canvas,
            labels_getter,
            on_selected=self._canvas_onLabelSelected
        )
        navigator = Navigator(
            w=w,
            h=navigator_h,
            x=0,
            y=0,
            images_folder=self.images_folder,
            on_back=lambda: self.setPage(self.page_incides['main_menu'], True),
            on_undo=self.label_controller.undo,
            on_redo=self.label_controller.redo,
            on_open=self._navigator_onOpenDir
        )
        toolbar = ui.components.RectContainer(
            w=320,
            h=h-navigator_h,
            x=canvas_w,
            y=navigator_h
        )
        def light_to_gamma(light: float) -> float:
            '''Light ranges from -1 to 1'''
            if light < 0:
                return -light + 1.0
            if light > 0:
                return -light * 0.9 + 1.0
            return 1.0
        def on_light_change(light) -> None:
            self.label_controller.setLight(
                light_to_gamma(light)
            )
        toolbar_buttons = ToolbarButtons(
            w=w-canvas_w-50,
            h=h-navigator_h,
            x=0,
            y=0,
            on_add=self.label_controller.startAdd,
            on_delete=self.label_controller.delete,
            on_save=self.label_controller.save,
            # on_search=self.label_controller.relable,
            on_correct=self.label_controller.correct,
            on_light_change=on_light_change
        )
        toolbar_icon_selection = ArmorClassSelection(
            w=scroll_w,
            h=scroll_h * 0.7,
            x=0,
            y=toolbar_h-scroll_h-220,
            on_select=self.label_controller.setClass
        )
        toolbar_scroll_files = SelectionBox(
            w=scroll_w,
            h=scroll_h,
            x=20,
            y=toolbar_h-scroll_h-20,
            image_folder=self.images_folder,
            deserted_folder=self.deserted_folder,
            on_selected=self._toolbar_onFileSelection
        )

        # ----- configure components -----
        canvas.setBackgroundColor(color_theme.Surface)
        toolbar.setBackgroundColor(ui.color.dark(color_theme.Surface, 2))
        navigator.setBackgroundColor(ui.color.dark(color_theme.Surface, 5))

        self.canvas = canvas
        self.toolbar = toolbar
        self.navigator = navigator
        self.toolbar_icon_selection = toolbar_icon_selection
        self.toolbar_scroll_files = toolbar_scroll_files

        self._loadPathByConfigManager()

        # ----- manage component hierarchy -----
        self.addChild(canvas)
        self.addChild(navigator)

        self.addChild(toolbar)
        toolbar.addChild(toolbar_buttons)
        toolbar.addChild(toolbar_icon_selection)
        toolbar.addChild(toolbar_scroll_files)

        # ----- keyboard events -----
        self.addKeyDownEvent(pygame.K_a, self.label_controller.startAdd)
        self.addKeyDownEvent(pygame.K_c, self.label_controller.correct)
        self.addKeyDownEvent(pygame.K_d, self.label_controller.delete)
        self.addKeyDownEvent(pygame.K_DELETE, self.label_controller.delete)
        self.addKeyCtrlEvent(pygame.K_z, self.label_controller.undo)
        self.addKeyCtrlEvent(pygame.K_y, self.label_controller.redo)
        self.addKeyDownEvent(pygame.K_ESCAPE, self.label_controller.cancelAdd)
        self.addKeyDownEvent(pygame.K_ESCAPE, self.label_controller.unselectAll)
        self.addKeyCtrlEvent(pygame.K_a, self.label_controller.selectAll)

        def on_prev() -> None:
            self.toolbar_scroll_files.selectPrev()
            folder = self.toolbar_scroll_files.getCurrentFolder()
            filename = self.toolbar_scroll_files.getSelected()
            if filename is not None:
                self.label_controller.reload(
                    os.path.join(folder, filename),
                    imgproc.getLabelPath(filename, self.labels_folder),
                    False
                )
                self.redraw()
        self.addKeyDownEvent(pygame.K_q, on_prev)

        def on_next() -> None:
            self.toolbar_scroll_files.selectNext()
            folder = self.toolbar_scroll_files.getCurrentFolder()
            filename = self.toolbar_scroll_files.getSelected()
            if filename is not None:
                self.label_controller.reload(
                    os.path.join(folder, filename),
                    imgproc.getLabelPath(filename, self.labels_folder),
                    False
                )
                self.redraw()
        self.addKeyDownEvent(pygame.K_e, on_next)

        def on_type_set(type_id: int) -> None:
            cls_id = self.toolbar_icon_selection.getClass()
            color_id = cls_id // 8
            cls_id = color_id * 8 + type_id
            self.toolbar_icon_selection.setClass(cls_id)
            self.label_controller.setClass(cls_id)
        self.addKeyDownEvent(pygame.K_0, lambda : on_type_set(0))
        self.addKeyDownEvent(pygame.K_1, lambda : on_type_set(1))
        self.addKeyDownEvent(pygame.K_2, lambda : on_type_set(2))
        self.addKeyDownEvent(pygame.K_3, lambda : on_type_set(3))
        self.addKeyDownEvent(pygame.K_4, lambda : on_type_set(4))
        self.addKeyDownEvent(pygame.K_5, lambda : on_type_set(5))
        self.addKeyDownEvent(pygame.K_6, lambda : on_type_set(6))
        self.addKeyDownEvent(pygame.K_7, lambda : on_type_set(7))

        def on_color_set(color_id: int) -> None:
            cls_id = self.toolbar_icon_selection.getClass()
            type_id = cls_id % 8
            cls_id = color_id * 8 + type_id
            self.toolbar_icon_selection.setClass(cls_id)
            self.label_controller.setClass(cls_id)
        self.addKeyDownEvent(pygame.K_b, lambda : on_color_set(0))
        self.addKeyDownEvent(pygame.K_r, lambda : on_color_set(1))

    def onResize(self, w: int, h: int, x: int, y: int):
        if not self.initialized:
            return

        navigator_h = 50
        canvas_w = w - 320

        self.navigator.onResize(w, navigator_h, 0, 0)
        self.toolbar.onResize(320, h-navigator_h, canvas_w, navigator_h)
        self.canvas.onResize(canvas_w, h-navigator_h, 0, navigator_h)

        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def onHide(self) -> None:
        self.navigator.resetState()

    def _canvas_onLabelSelected(self, cls_id: int) -> None:
        self.toolbar_icon_selection.setClass(cls_id)
        self.toolbar_icon_selection.redraw()

    def _toolbar_onFileSelection(self,
        folder: str,
        filename: Union[str, None],
        is_deserted: bool
    ) -> None:
        if filename is None:
            self.label_controller.reload(None, None, False)
            self.label_controller.canvas.redraw()
            return

        image_path = os.path.join(folder, filename)
        label_path = imgproc.getLabelPath(filename, self.labels_folder)
        self.label_controller.reload(image_path, label_path, False)

        self.label_controller.canvas.redraw()

    def _reloadSelectionBox(self, selected_idx: int = None) -> None:
        navigator_h = 50
        canvas_w = self.w - 320
        toolbar_h = self.h - navigator_h
        scroll_h = int(toolbar_h * 0.4)
        scroll_w = self.w - canvas_w - 40

        toolbar_scroll_files = SelectionBox(
            w=scroll_w,
            h=scroll_h,
            x=20,
            y=toolbar_h-scroll_h-20,
            image_folder=self.images_folder,
            deserted_folder=self.deserted_folder,
            on_selected=self._toolbar_onFileSelection
        )
        toolbar_scroll_files.select(selected_idx)

        self.toolbar_scroll_files.kill()
        self.toolbar_scroll_files = toolbar_scroll_files
        self.toolbar.addChild(toolbar_scroll_files)

        if selected_idx is None:
            self.label_controller.reload(None, None, False)
            return

        image_filename = self.toolbar_scroll_files.getSelected()
        if image_filename is None:
            return

        image_path = os.path.join(self.images_folder, image_filename)
        label_path = imgproc.getLabelPath(image_filename, self.labels_folder)
        self.label_controller.reload(image_path, label_path, False)

    def _navigator_onOpenDir(self) -> None:
        _images, _labels, _deserted = openDir()
        self.images_folder = _images
        self.labels_folder = _labels
        self.deserted_folder = _deserted

        self.navigator.setFolder(self.images_folder)
        self._reloadSelectionBox()
        self.redraw()

    def _loadPathByConfigManager(self) -> None:
        images_folder = self.config_manager['last_images_folder']
        labels_folder = self.config_manager['last_labels_folder']
        image_index = self.config_manager['last_image_index']

        # load folder
        if images_folder is None or not os.path.exists(images_folder):
            return
        if labels_folder is None or not os.path.exists(labels_folder):
            return
        self.images_folder: str = images_folder
        self.labels_folder: str = labels_folder
        self.deserted_folder: str = os.path.join(images_folder, 'deserted')

        self.navigator.setFolder(self.images_folder)
        self._reloadSelectionBox(image_index)
        self.redraw()

    def kill(self):
        if self.initialized:
            self.label_controller.save()
            selected_idx = self.toolbar_scroll_files.getSelectedIndex()
            if selected_idx == -1:
                selected_idx = None
            self.config_manager['last_images_folder'] = self.images_folder
            self.config_manager['last_labels_folder'] = self.labels_folder
            self.config_manager['last_image_index'] = selected_idx
        super().kill()