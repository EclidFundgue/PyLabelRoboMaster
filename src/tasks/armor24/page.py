import os
import tkinter as tk
from tkinter import filedialog
from typing import Union

import pygame

from ... import pygame_gui as ui
from ...components.navigator import Navigator
from ...components.stacked_page import StackedPage
from ...components.toolbar import ToolbarButtons
from ...file import SelectionBox
from ...label import LabelController, Labels
from ...utils import imgproc
from ...utils.config import ConfigManager
from .armor_type_select import ArmorIconsSelect
from .icon import ArmorIcon


class ArmorPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        self.icon_class_id = -1

        self.images_folder = './resources/test_dataset/images'
        self.labels_folder = './resources/test_dataset/labels'
        self.deserted_folder = os.path.join(self.images_folder, 'deserted')

        self.config_manager = ConfigManager('./user_data.json')

        # ----- initialize basic constants -----
        color_theme = ui.color.LightColorTheme()

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
            def get_icon(kpt, cls_id) -> ArmorIcon:
                icon = ArmorIcon(cls_id)
                icon.setPosToKeypoint(kpt)
                return icon
            return Labels(
                w, h, x, y,
                num_keypoints=4,
                icon_getter=get_icon,
                on_select=on_select
            )
        self.label_controller = LabelController(
            canvas,
            labels_getter,
            # on_selected=self._canvas_onLabelSelected
        )
        navigator = Navigator(
            w=w,
            h=navigator_h,
            x=0,
            y=0,
            on_back=lambda: self.setPage(page_incides['main_menu'],True),
            on_undo=self.label_controller.undo,
            on_redo=self.label_controller.redo,
            # on_open=self._navigator_onOpenDir
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
        toolbar_icon_selection = ArmorIconsSelect(
            x=20,
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

        # ----- manage component hierarchy -----
        self.addChild(canvas)
        self.addChild(navigator)

        self.addChild(toolbar)
        toolbar.addChild(toolbar_buttons)
        toolbar.addChild(toolbar_icon_selection)
        toolbar.addChild(toolbar_scroll_files)

        # ----- keyboard events -----
        self.addKeyDownEvent(pygame.K_c, self.label_controller.correct)
        self.addKeyCtrlEvent(pygame.K_z, self.label_controller.undo)
        self.addKeyCtrlEvent(pygame.K_y, self.label_controller.redo)

    def onResize(self, w: int, h: int, x: int, y: int):
        navigator_h = 50
        canvas_w = w - 320

        self.navigator.onResize(
            w, navigator_h, 0, 0
        )
        self.toolbar.onResize(
            320, h-navigator_h, canvas_w, navigator_h
        )
        self.canvas.onResize(
            canvas_w, h-navigator_h, 0, navigator_h
        )

        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def onHide(self) -> None:
        self.navigator.resetState()

    def _canvas_onLabelSelected(self, cls_id) -> None:
        self.toolbar_icon_selection.setType(cls_id)

    def _toolbar_onFileSelection(self,
        folder: str,
        filename: Union[str, None],
        is_deserted: bool
    ) -> None:
        self.label_controller.save()

        if filename is None:
            self.label_controller.reload(None, None, False)
            self.label_controller.canvas.redraw()
            return

        image_path = os.path.join(folder, filename)
        if not is_deserted:
            label_path = imgproc.getLabelPath(filename, self.labels_folder)
            self.label_controller.reload(image_path, label_path, False)

        self.label_controller.canvas.redraw()


    #     self._loadPathByConfigManager()

    #     self.toolbar = toolbar
    #     self.toolbar_icon_selection = toolbar_icon_selection
    #     self.toolbar_scroll_navigator_index = toolbar_scroll_navigator_index
    #     self.toolbar_scroll_navigator_filename = toolbar_scroll_navigator_filename
    #     self.toolbar_scroll_files = toolbar_scroll_files

    #     if self.selected_image is not None:
    #         self.label_controller.reload(
    #             os.path.join(self.images_folder, self.selected_image),
    #             self.selected_label,
    #             False
    #         )
    #         self.toolbar_scroll_files.selectLine(self.selected_image)
    #         self.toolbar_scroll_navigator_index.setText(
    #             f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
    #             f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
    #         )
    #         line = self.toolbar_scroll_files.getSelectedLine()
    #         self.toolbar_scroll_navigator_filename.setText(line.filename
    
    # def _loadPathByConfigManager(self) -> None:
    #     images_folder = self.config_manager['last_images_folder']
    #     labels_folder = self.config_manager['last_labels_folder']
    #     image_file = self.config_manager['last_image_file']

    #     # load folder
    #     if images_folder is None or not os.path.exists(images_folder):
    #         return
    #     if labels_folder is None or not os.path.exists(labels_folder):
    #         return
    #     self.images_folder: str = images_folder
    #     self.labels_folder: str = labels_folder
    #     self.deserted_folder: str = os.path.join(images_folder, 'deserted')

    #     # load current file
    #     if image_file is None:
    #         return
    #     if os.path.exists(os.path.join(images_folder, image_file)):
    #         self.selected_image = image_file
    #         self.selected_label = imgproc.getLabelPath(image_file, labels_folder)

    # def _navigator_onOpenDir(self) -> None:
    #     root = tk.Tk()
    #     root.withdraw()

    #     self.images_folder = filedialog.askdirectory(title='Images')
    #     self.labels_folder = filedialog.askdirectory(title='Labels')
    #     self.deserted_folder = os.path.join(self.images_folder, 'deserted')
    #     if not os.path.exists(self.deserted_folder):
    #         os.makedirs(self.deserted_folder)

    #     toolbar_scroll_files = stackedview.StackedScrollView(
    #         w=self.toolbar_scroll_files.w,
    #         h=self.toolbar_scroll_files.h,
    #         x=self.toolbar_scroll_files.x,
    #         y=self.toolbar_scroll_files.y,
    #         line_w=self.toolbar_scroll_files.w-30,
    #         line_h=30,
    #         image_folder=self.images_folder,
    #         deserted_folder=self.deserted_folder,
    #         on_page_changed=self._toolbarScroll_onPageChange,
    #         on_select=self._toolbarScroll_onSelect,
    #         on_desert=self._toolbarScroll_onDesert,
    #         on_restore=self._toolbarScroll_onRestore,
    #     )
    #     self.toolbar_scroll_files.kill()
    #     self.toolbar_scroll_files = toolbar_scroll_files
    #     self.toolbar.addChild(toolbar_scroll_files)

    #     self.label_controller.reload(None, None, False)

    #     self.toolbar_scroll_navigator_index.setText(
    #         f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
    #         f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
    #     )
    #     self.toolbar_scroll_navigator_filename.setText('')
    #     self.redraw()

    # def kill(self):
    #     self.config_manager['last_images_folder'] = self.images_folder
    #     self.config_manager['last_labels_folder'] = self.labels_folder
    #     self.config_manager['last_image_file'] = self.selected_image
    #     super().kill()