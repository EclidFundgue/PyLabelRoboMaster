import os

import pygame

from .. import pygame_gui as ui
from ..components.armor_type_select import ArmorIconsSelect
from ..components.canvas import Canvas
from ..components.label_controllder import Label, LabelController
from ..components.scroll import stackedview
from ..components.stacked_page import StackedPage
from ..components.switch import Switch
from ..utils import imgproc
from ..utils.config import ConfigManager


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

        toolbar_buttons = {
            'rect_add': (32, 32, 20, 20), # (0, 0)
            'rect_delete': (32, 32, 70, 20), # (0, 1)
            'rect_save': (32, 32, 120, 20), # (0, 2)
            'rect_search': (32, 32, 20, 70), # (1, 0)
            'rect_correct': (32, 32, 70, 70), # (1, 1)
            'rect_preproc': (32, 32, 20, 120), # (2, 0)
            'rect_auto': (86, 32, 70, 120), # (2, 1)
        }

        img_arrow = ui.utils.loadImage('./resources/buttons/arrow.png')
        img_arrow_pressed = ui.utils.loadImage('./resources/buttons/arrow_pressed.png')

        # ----- create components -----
        canvas = ui.components.RectContainer(
            w=canvas_w,
            h=h-navigator_h,
            x=0,
            y=navigator_h
        )
        canvas_canvas = Canvas(
            w=canvas_w,
            h=h-navigator_h,
            x=0,
            y=0
        )
        self.label_controller = LabelController(
            canvas_canvas,
            on_label_selected=self._canvas_onLabelSelected
        )
        navigator = ui.components.RectContainer(
            w=w,
            h=navigator_h,
            x=0,
            y=0
        )
        navigator_button_undo = ui.components.IconButton(
            w=32,
            h=32,
            x=20,
            y=0,
            image='./resources/buttons/undo.png',
            pressed_image='./resources/buttons/undo_pressed.png',
            on_press=self.label_controller.undo,
            cursor_change=True
        )
        navigator_button_redo = ui.components.IconButton(
            w=32,
            h=32,
            x=80,
            y=0,
            image='./resources/buttons/bush_gemer.png',
            pressed_image='./resources/buttons/bush_gemer_pressed.png',
            on_press=self.label_controller.redo,
            cursor_change=True
        )
        navigator_button_back = ui.components.CloseButton(
            w=int(navigator_h*1.5),
            h=navigator_h,
            x=w - int(navigator_h*1.5),
            y=0,
            color=ui.color.dark(color_theme.Surface,3),
            cross_color=color_theme.OnSurface,
            on_press=lambda: self.setPage(page_incides['main_menu'],True)
        )
        toolbar = ui.components.RectContainer(
            w=w-canvas_w,
            h=h-navigator_h,
            x=canvas_w,
            y=navigator_h
        )
        toolbar_button_add = ui.components.IconButton(
            *toolbar_buttons['rect_add'],
            './resources/buttons/add.png',
            './resources/buttons/add_pressed.png',
            on_press=self.label_controller.startAdd,
            cursor_change=True
        )
        toolbar_button_delete = ui.components.IconButton(
            *toolbar_buttons['rect_delete'],
            './resources/buttons/delete.png',
            './resources/buttons/delete_pressed.png',
            on_press=self.label_controller.deleteSelected,
            cursor_change=True
        )
        toolbar_button_search = ui.components.IconButton(
            *toolbar_buttons['rect_search'],
            './resources/buttons/search.png',
            './resources/buttons/search_pressed.png',
            on_press=self.label_controller.relable,
            cursor_change=True
        )
        toolbar_button_save = ui.components.IconButton(
            *toolbar_buttons['rect_save'],
            './resources/buttons/save.png',
            './resources/buttons/save_pressed.png',
            on_press=self.label_controller.save,
            cursor_change=True
        )
        toolbar_button_correct = ui.components.IconButton(
            *toolbar_buttons['rect_correct'],
            './resources/buttons/correct.png',
            './resources/buttons/correct.png',
            on_press=self.label_controller.correct,
            cursor_change=True
        )
        toolbar_switch_preproc = Switch(
            *toolbar_buttons['rect_preproc'],
            './resources/switchs/eye_open.png',
            './resources/switchs/eye_close.png',
            on_turn=self.label_controller.switchPreprocess,
        )
        toolbar_switch_auto = Switch(
            *toolbar_buttons['rect_auto'],
            './resources/switchs/auto_on.png',
            './resources/switchs/auto_off.png',
            on_turn=self._toolbar_onSwitchAuto,
        )
        toolbar_icon_selection = ArmorIconsSelect(
            x=20,
            y=toolbar_h-scroll_h-220,
            on_select=self.label_controller.setSelectedClass
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
        self.navigator_button_back = navigator_button_back
        self.toolbar_icon_selection = toolbar_icon_selection
        self.toolbar_scroll_navigator_index = toolbar_scroll_navigator_index
        self.toolbar_scroll_navigator_filename = toolbar_scroll_navigator_filename
        self.toolbar_scroll_files = toolbar_scroll_files

        canvas.setBackgroundColor(color_theme.Surface)

        navigator.setBackgroundColor(ui.color.dark(color_theme.Surface, 3))
        navigator.alignVerticalCenter(navigator_button_undo)
        navigator.alignVerticalCenter(navigator_button_redo)

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

        # ----- manage component hierarchy -----
        self.addChild(canvas)
        canvas.addChild(canvas_canvas)

        self.addChild(navigator)
        navigator.addChild(navigator_button_undo)
        navigator.addChild(navigator_button_redo)
        navigator.addChild(navigator_button_back)

        self.addChild(toolbar)
        toolbar.addChild(toolbar_button_add)
        toolbar.addChild(toolbar_button_delete)
        toolbar.addChild(toolbar_button_search)
        toolbar.addChild(toolbar_button_save)
        toolbar.addChild(toolbar_button_correct)
        toolbar.addChild(toolbar_switch_preproc)
        toolbar.addChild(toolbar_switch_auto)
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

    def onHide(self):
        self.navigator_button_back.resetState()

    def _canvas_onLabelSelected(self, label: Label) -> None:
        self.toolbar_icon_selection.setType(label.cls_id)

    def _toolbar_onSwitchAuto(self, state: bool) -> None:
        self.auto_labeling = state

    def _toolbar_onPrev(self) -> None:
        self.toolbar_scroll_files.selectPrev()
        line = self.toolbar_scroll_files.getSelectedLine()
        self.selected_image = line.filename
        self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)

        image_path = os.path.join(self.images_folder, self.selected_image)

        self.label_controller.save()
        self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )
        self.toolbar_scroll_navigator_filename.setText(line.filename)
        self.label_controller.canvas.redraw()

    def _toolbar_onNext(self) -> None:
        self.toolbar_scroll_files.selectNext()
        line = self.toolbar_scroll_files.getSelectedLine()
        self.selected_image = line.filename
        self.selected_label = imgproc.getLabelPath(line.filename, self.labels_folder)

        image_path = os.path.join(self.images_folder, self.selected_image)

        self.label_controller.save()
        self.label_controller.reload(image_path, self.selected_label, self.auto_labeling)
        self.toolbar_scroll_navigator_index.setText(
            f'{self.toolbar_scroll_files.getSelectedIndex()+1}/'
            f'{self.toolbar_scroll_files.getCurrentPageFileNumber()}'
        )
        self.toolbar_scroll_navigator_filename.setText(line.filename)
        self.label_controller.canvas.redraw()

    def _toolbarScroll_onPageChange(self, page_index: int) -> None:
        self.scroll_page = page_index

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