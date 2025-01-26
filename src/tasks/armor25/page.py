import os
import tkinter as tk
from tkinter import filedialog

import pygame

from ... import pygame_gui as ui
from ...components.navigator import Navigator
from ...components.scroll import stackedview
from ...components.stacked_page import StackedPage
from ...components.toolbar import ToolbarButtons
from ...label import LabelController, Labels
from ...utils import imgproc
from ...utils.config import ConfigManager
from .armor_type_select import ArmorIconsSelect
from .icon import ArmorIcon


class ArmorPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        self.page_incides = page_incides
        self.scroll_page: int = 0 # 0-normal, 1-deserted
        self.icon_class_id: int = -1
        self.auto_labeling = False

        self.images_folder = './resources/test_dataset/images'
        self.labels_folder = './resources/test_dataset/labels'
        self.deserted_folder = os.path.join(self.images_folder, 'deserted')
        self.selected_image: str = None
        self.selected_deserted: str = None
        self.selected_label: str = None

        self.config_manager = ConfigManager('./user_data.json')
        self._loadPathByConfigManager()

        # ----- initialize basic constants -----
        color_theme = ui.color.LightColorTheme()

        navigator_h = 40
        canvas_w = 3 * w // 4
        toolbar_h = h - navigator_h
        scroll_h = int(toolbar_h * 0.4)
        scroll_w = w - canvas_w - 40

        img_arrow = ui.utils.loadImage('./resources/buttons/arrow.png')
        img_arrow_pressed = ui.utils.loadImage('./resources/buttons/arrow_pressed.png')

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
            on_selected=self._canvas_onLabelSelected
        )
        navigator = Navigator(
            w=w,
            h=navigator_h,
            x=0,
            y=0,
            on_back=lambda: self.setPage(page_incides['main_menu'],True),
            on_undo=self.label_controller.undo,
            on_redo=self.label_controller.redo,
            on_open=self._navigator_onOpenDir
        )
        toolbar = ui.components.RectContainer(
            w=w-canvas_w,
            h=h-navigator_h,
            x=canvas_w,
            y=navigator_h
        )
        toolbar_buttons = ToolbarButtons(
            w, h, x, y,
            on_add=self.label_controller.startAdd,
            on_delete=self.label_controller.delete,
            on_save=self.label_controller.save,
            on_search=self.label_controller.relable,
            on_correct=self.label_controller.correct,
            turn_light=self.label_controller.turnLight,
            turn_auto=self._toolbar_onSwitchAuto
        )
        toolbar_icon_selection = ArmorIconsSelect(
            x=20,
            y=toolbar_h-scroll_h-220,
            on_select=self.label_controller.setClass
        )
        toolbar_scroll_navigator = ui.components.RectContainer(
            w=scroll_w,
            h=30,
            x=20,
            y=toolbar_h-scroll_h-50
        )
        toolbar_scroll_navigator_prev = ui.components.IconButton(
            w=16,
            h=16,
            x=0,
            y=0,
            image=img_arrow,
            pressed_image=img_arrow_pressed,
            on_press=self._toolbar_onPrev,
            continue_press=40,
            cursor_change=True
        )
        toolbar_scroll_navigator_next = ui.components.IconButton(
            w=16,
            h=16,
            x=scroll_w-16,
            y=0,
            image=pygame.transform.flip(img_arrow, True, False),
            pressed_image=pygame.transform.flip(img_arrow_pressed, True, False),
            on_press=self._toolbar_onNext,
            continue_press=40,
            cursor_change=True
        )
        toolbar_scroll_files = stackedview.StackedScrollView(
            w=scroll_w,
            h=scroll_h,
            x=20,
            y=toolbar_h-scroll_h-20,
            line_w=scroll_w-30,
            line_h=30,
            image_folder=self.images_folder,
            deserted_folder=self.deserted_folder,
            on_page_changed=self._toolbarScroll_onPageChange,
            on_select=self._toolbarScroll_onSelect,
            on_desert=self._toolbarScroll_onDesert,
            on_restore=self._toolbarScroll_onRestore,
        )
        toolbar_scroll_navigator_index = ui.components.Label(
            w=70,
            h=16,
            x=scroll_w-16-70,
            y=0,
            text=f'0/{toolbar_scroll_files.getCurrentPageFileNumber()}'
        )
        toolbar_scroll_navigator_filename = ui.components.Label(
            w=scroll_w-32-70-10,
            h=16,
            x=16+10,
            y=0,
            text=''
        )

        # ----- configure components -----
        self.navigator = navigator
        self.toolbar = toolbar
        self.toolbar_icon_selection = toolbar_icon_selection
        self.toolbar_scroll_navigator_index = toolbar_scroll_navigator_index
        self.toolbar_scroll_navigator_filename = toolbar_scroll_navigator_filename
        self.toolbar_scroll_files = toolbar_scroll_files

        canvas.setBackgroundColor(color_theme.Surface)

        navigator.setBackgroundColor(ui.color.dark(color_theme.Surface, 3))

        toolbar.setBackgroundColor(ui.color.dark(color_theme.Surface, 2))
        toolbar_scroll_navigator.alignVerticalCenter(toolbar_scroll_navigator_prev)
        toolbar_scroll_navigator.alignVerticalCenter(toolbar_scroll_navigator_next)
        toolbar_scroll_navigator.alignVerticalCenter(toolbar_scroll_navigator_index)
        toolbar_scroll_navigator.alignVerticalCenter(toolbar_scroll_navigator_filename)
        toolbar_scroll_navigator_index.setAlignment(ui.constants.ALIGN_LEFT)
        toolbar_scroll_navigator_filename.setAlignment(ui.constants.ALIGN_LEFT)

        if self.selected_image is not None:
            self.label_controller.reload(
                os.path.join(self.images_folder, self.selected_image),
                self.selected_label,
                False
            )
            self.toolbar_scroll_files.selectLine(self.selected_image)
            self.toolbar_scroll_navigator_index.setText(
                f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
                f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
            )
            line = self.toolbar_scroll_files.getSelectedLine()
            self.toolbar_scroll_navigator_filename.setText(line.filename)

        self.addKeyCtrlEvent(pygame.K_z, self.label_controller.undo)
        self.addKeyCtrlEvent(pygame.K_y, self.label_controller.redo)

        # ----- manage component hierarchy -----
        self.addChild(canvas)
        self.addChild(navigator)

        self.addChild(toolbar)
        toolbar.addChild(toolbar_buttons)
        toolbar.addChild(toolbar_icon_selection)
        toolbar.addChild(toolbar_scroll_navigator)
        toolbar_scroll_navigator.addChild(toolbar_scroll_navigator_prev)
        toolbar_scroll_navigator.addChild(toolbar_scroll_navigator_next)
        toolbar_scroll_navigator.addChild(toolbar_scroll_navigator_index)
        toolbar_scroll_navigator.addChild(toolbar_scroll_navigator_filename)
        toolbar.addChild(toolbar_scroll_files)

        # ----- keyboard events -----
        self.addKeyDownEvent(pygame.K_c, self.label_controller.correct)
    
    def _loadPathByConfigManager(self) -> None:
        images_folder = self.config_manager['last_images_folder']
        labels_folder = self.config_manager['last_labels_folder']
        image_file = self.config_manager['last_image_file']

        # load folder
        if images_folder is None or not os.path.exists(images_folder):
            return
        if labels_folder is None or not os.path.exists(labels_folder):
            return
        self.images_folder: str = images_folder
        self.labels_folder: str = labels_folder
        self.deserted_folder: str = os.path.join(images_folder, 'deserted')

        # load current file
        if image_file is None:
            return
        if os.path.exists(os.path.join(images_folder, image_file)):
            self.selected_image = image_file
            self.selected_label = imgproc.getLabelPath(image_file, labels_folder)

    def onHide(self) -> None:
        self.navigator.resetState()

    def _canvas_onLabelSelected(self, cls_id) -> None:
        self.toolbar_icon_selection.setType(cls_id)

    def _navigator_onOpenDir(self) -> None:
        root = tk.Tk()
        root.withdraw()

        self.images_folder = filedialog.askdirectory(title='Images')
        self.labels_folder = filedialog.askdirectory(title='Labels')
        self.deserted_folder = os.path.join(self.images_folder, 'deserted')
        if not os.path.exists(self.deserted_folder):
            os.makedirs(self.deserted_folder)

        toolbar_scroll_files = stackedview.StackedScrollView(
            w=self.toolbar_scroll_files.w,
            h=self.toolbar_scroll_files.h,
            x=self.toolbar_scroll_files.x,
            y=self.toolbar_scroll_files.y,
            line_w=self.toolbar_scroll_files.w-30,
            line_h=30,
            image_folder=self.images_folder,
            deserted_folder=self.deserted_folder,
            on_page_changed=self._toolbarScroll_onPageChange,
            on_select=self._toolbarScroll_onSelect,
            on_desert=self._toolbarScroll_onDesert,
            on_restore=self._toolbarScroll_onRestore,
        )
        self.toolbar_scroll_files.kill()
        self.toolbar_scroll_files = toolbar_scroll_files
        self.toolbar.addChild(toolbar_scroll_files)

        self.label_controller.reload(None, None, False)

        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )
        self.toolbar_scroll_navigator_filename.setText('')
        self.redraw()

    def _toolbar_onSwitchAuto(self, state: bool) -> None:
        self.auto_labeling = state

    def _toolbar_onPrev(self) -> None:
        self.toolbar_scroll_files.selectPrev()
        line = self.toolbar_scroll_files.getSelectedLine()
        self.label_controller.save()
        if line is None:
            self.selected_image = None
            self.selected_label = None
            self.label_controller.reload(None, None, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText('')
        else:
            self.selected_image = line.filename
            self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)

            image_path = os.path.join(self.images_folder, self.selected_image)
            self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText(line.filename)

        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )

        self.label_controller.canvas.redraw()

    def _toolbar_onNext(self) -> None:
        self.toolbar_scroll_files.selectNext()
        line = self.toolbar_scroll_files.getSelectedLine()
        self.label_controller.save()
        if line is None:
            self.selected_image = None
            self.selected_label = None
            self.label_controller.reload(None, None, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText('')
        else:
            self.selected_image = line.filename
            self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)

            image_path = os.path.join(self.images_folder, self.selected_image)
            self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText(line.filename)

        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )

        self.label_controller.canvas.redraw()

    def _toolbarScroll_onPageChange(self, page_index: int) -> None:
        self.scroll_page = page_index
        line = self.toolbar_scroll_files.getSelectedLine()
        self.label_controller.save()
        if line is None:
            self.selected_image = None
            self.selected_label = None
            self.label_controller.reload(None, None, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText('')
        else:
            self.selected_image = line.filename
            self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)

            image_path = os.path.join(self.images_folder, self.selected_image)
            self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
            self.toolbar_scroll_navigator_filename.setText(line.filename)

        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )

        self.label_controller.canvas.redraw()

    def _toolbarScroll_onSelect(self, index: int, line: stackedview.FileLine) -> None:
        if self.scroll_page == 0:
            image_path = os.path.join(self.images_folder, line.filename)
            self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)
            self.selected_image = line.filename
        else:
            image_path = os.path.join(self.deserted_folder, line.filename)
            self.selected_label = None
            self.selected_deserted = line.filename

        self.label_controller.save()
        self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
        self.toolbar_scroll_navigator_index.setText(f'{index+1}/{self.toolbar_scroll_files.getCurrentPageFileNumber()}')
        self.toolbar_scroll_navigator_filename.setText(line.filename)
        self.label_controller.canvas.redraw()

    def _toolbarScroll_onDesert(self, index: int, line: stackedview.FileLine) -> None:
        if self.selected_image == line.filename:
            self.selected_image = None
        os.rename(
            os.path.join(self.images_folder, line.filename),
            os.path.join(self.deserted_folder, line.filename)
        )
        self.toolbar_scroll_files.deleteLine(0, line)
        self.toolbar_scroll_files.addLine(1, line)

    def _toolbarScroll_onRestore(self, index: int, line: stackedview.FileLine) -> None:
        if self.selected_deserted == line.filename:
            self.selected_deserted = None
        os.rename(
            os.path.join(self.deserted_folder, line.filename),
            os.path.join(self.images_folder, line.filename)
        )
        self.toolbar_scroll_files.deleteLine(1, line)
        self.toolbar_scroll_files.addLine(0, line)

    def kill(self):
        self.config_manager['last_images_folder'] = self.images_folder
        self.config_manager['last_labels_folder'] = self.labels_folder
        self.config_manager['last_image_file'] = self.selected_image
        super().kill()