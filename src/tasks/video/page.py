import os

import cv2
import pygame

from ... import pygame_gui as ui
from ...components.light_bar import LightBar
from ...components.stacked_page import StackedPage
from ...components.switch import Switch
from ...label import Image
from ...utils.config import ConfigManager, openVideo
from ...utils.imgproc import mat2surface, surface2mat
from ...utils.inference import PoseModel
from .info import InfoButton
from .video_bar import VideoBar


def light_to_gamma(light: float) -> float:
    '''Light ranges from -1 to 1'''
    if light < 0:
        return -light + 1.0
    if light > 0:
        return -light * 0.9 + 1.0
    return 1.0

class VideoPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)
        self.page_incides = page_incides
        self.initialized = False

    def onShow(self):
        if self.initialized:
            return
        self.initialized = True

        # variables
        self.config_manager = ConfigManager('./user_data.json')

        self.video_path = "resources/test_dataset/test.mp4" \
            if self.config_manager['last_video_path'] is None \
            else self.config_manager['last_video_path']

        self.image_save_folder = os.path.join(
            os.path.dirname(self.video_path),
            'extract_image'
        )

        self: cv2.VideoCapture
        self.fps: float = 0.0
        self.total_frames: int = 0
        self.video_duration: float  = 0 # seconds
        self.image_size = (0, 0)

        self.current_frame_idx = -1
        self.current_frame: Image = None
        self.current_labeled_frame: Image = None

        self.image_light = 0.0
        self.playing = False
        self.label = False
        self.model = PoseModel('resources/armor.onnx', (416, 416))

        # components
        color_theme = ui.color.LightColorTheme()

        def on_open():
            video_path = openVideo()
            if video_path is None:
                return

            self.video_path = video_path
            self.image_save_folder = os.path.join(
                os.path.dirname(self.video_path),
                'saved_extract_image'
            )
            self.config_manager['last_video_path'] = self.video_path
            self._loadVideoInfo(self.video_path)
            self.redraw()
        button_open = ui.components.IconButton(
            w=40,
            h=40,
            x=20,
            y=0,
            icon='resources/icons/open_file.png',
            on_press=on_open,
            cursor_change=True
        )

        w = self.w
        h = self.h
        video_info = ui.components.RectContainer(w * 0.2, h * 0.5, 20, 60)
        video_info.layer = 10
        video_info.setBackgroundColor((255, 255, 255))

        self.video_info_fps = ui.components.Label(w * 0.2, 40, 5, 0, f'fps: {self.fps}')
        self.video_info_total_frames = ui.components.Label(w * 0.2, 40, 5, 40, f'total frames: {self.total_frames}')
        self.video_info_video_duration = ui.components.Label(w * 0.2, 40, 5, 80, f'length: {self.video_duration}s')
        self.video_info_size = ui.components.Label(w * 0.2, 40, 5, 120, f'size: ({self.image_size[0]}, {self.image_size[1]})')

        self.video_info_fps.setAlignment(ui.constants.ALIGN_LEFT)
        self.video_info_total_frames.setAlignment(ui.constants.ALIGN_LEFT)
        self.video_info_video_duration.setAlignment(ui.constants.ALIGN_LEFT)
        self.video_info_size.setAlignment(ui.constants.ALIGN_LEFT)

        video_info.addChild(self.video_info_fps)
        video_info.addChild(self.video_info_total_frames)
        video_info.addChild(self.video_info_video_duration)
        video_info.addChild(self.video_info_size)

        def on_video_info_show():
            self.addChild(video_info)
            self.redraw()
        def on_video_info_hide():
            self.removeChild(video_info)
            self.redraw()
        button_info = InfoButton(
            w=40,
            h=40,
            x=2*20+40,
            y=0,
            on_show=on_video_info_show,
            on_hide=on_video_info_hide
        )

        def on_save() -> None:
            if not os.path.exists(self.image_save_folder):
                os.makedirs(self.image_save_folder)
            video_name = os.path.splitext(os.path.split(self.video_path)[-1])[0]
            path = os.path.join(self.image_save_folder, f'{video_name}_{self.current_frame_idx}.jpg')
            pygame.image.save(self.current_frame.orig_image, path)
        button_save = ui.components.IconButton(
            w=40,
            h=40,
            x=3*20+2*40,
            y=0,
            icon='resources/icons/save.png',
            on_press=on_save,
            cursor_change=True
        )

        self.button_back = ui.components.CloseButton(
            w=int(40*1.5),
            h=40,
            x=w-int(40*1.5),
            y=0,
            color=ui.color.dark(color_theme.Surface,3),
            cross_color=color_theme.OnSurface,
            on_press=lambda : self.setPage(self.page_incides['main_menu'], True)
        )

        self.canvas = ui.components.Canvas(w, h-40-40-80, 0, 40)

        btn_size = 36
        pad_y = (80 - btn_size) // 2
        btn_y = h - 80 + pad_y

        def on_switch_pause_turn(state: bool) -> None:
            self.playing = state
        self.switch_pause = Switch(
            w=btn_size,
            h=btn_size,
            x=100,
            y=btn_y,
            image_on='resources/icons/play.png',
            image_off='resources/icons/pause.png',
            on_turn=on_switch_pause_turn
        )

        def _on_prev_frame() -> None:
            self._stopPlaying()
            self._setFrame(self.current_frame_idx - 1)
            self.redraw()
        button_prev_frame = ui.components.IconButton(
            w=btn_size,
            h=btn_size,
            x=40,
            y=btn_y,
            icon='resources/icons/arrow_left.png',
            on_press=_on_prev_frame,
            continue_press=40
        )

        def _on_next_frame() -> None:
            self._stopPlaying()
            self._setFrame(self.current_frame_idx + 1)
            self.redraw()
        button_next_frame = ui.components.IconButton(
            w=btn_size,
            h=btn_size,
            x=160,
            y=btn_y,
            icon='resources/icons/arrow_right.png',
            on_press=_on_next_frame,
            continue_press=40
        )

        def on_light_change(light: float) -> None:
            self.image_light = light
            if self.current_frame:
                self.current_frame.setLight(light_to_gamma(light))
        light_bar = LightBar(
            w=400,
            h=btn_size,
            x=300,
            y=btn_y,
            on_change=on_light_change
        )

        show_label_text = ui.components.Label(100, btn_size, 750, btn_y, 'show label:')
        show_label_text.setAlignment(ui.constants.ALIGN_LEFT)

        def on_show_label_switch_turn(state: bool):
            self.label = state
            self._updateImage(state)

        show_label_switch = Switch(
            w=btn_size,
            h=btn_size,
            x=860,
            y=btn_y,
            image_on='resources/icons/check_box_ok.png',
            image_off='resources/icons/check_box.png',
            on_turn=on_show_label_switch_turn
        )

        # configure
        self._loadVideoInfo(self.video_path)
        self._setFrame(0)
        self.setBackgroundColor((255, 255, 255))

        # succeed
        self.addChild(button_open)
        self.addChild(button_info)
        self.addChild(button_save)
        self.addChild(self.button_back)
        self.addChild(self.canvas)
        self.addChild(self.p_bar)
        self.addChild(self.switch_pause)
        self.addChild(button_prev_frame)
        self.addChild(button_next_frame)
        self.addChild(light_bar)
        self.addChild(show_label_text)
        self.addChild(show_label_switch)

    def _clearImage(self) -> None:
        if self.current_frame is not None:
            self.current_frame.kill()
            self.current_frame = None
        if self.current_labeled_frame is not None:
            self.current_labeled_frame.kill()
            self.current_labeled_frame = None

    def _loadVideoInfo(self, video_path) -> None:
        self._clearImage()

        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap.get(cv2.CAP_PROP_FPS) else 30
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.total_frames == 0:
            self.total_frames = 1
            # TODO: load failed
        self.video_duration = self.total_frames / self.fps

        self.video_info_fps.setText(f'fps: {self.fps}')
        self.video_info_total_frames.setText(f'total frames: {self.total_frames}')
        self.video_info_video_duration.setText(f'length: {self.video_duration}s')
 
        self.current_frame_idx = 0.0
        self.current_frame = None
        self.current_labeled_frame = None

        if hasattr(self, 'p_bar') and self.p_bar is not None:
            self.p_bar.kill()

        def on_change(time_sec: float) -> None:
            self._stopPlaying() # Dragging progress bar will terminate playing.
            self._setFrame(int(time_sec / self.video_duration * self.total_frames))
        self.p_bar = VideoBar(
            w=self.w-40,
            h=40,
            x=20,
            y=self.h-40-80,
            video_length_sec=self.video_duration,
            on_change=on_change
        )

        self._setFrame(0)
        if self.current_frame is not None:
            w_scale = self.canvas.w / self.current_frame._w
            h_scale = self.canvas.h / self.current_frame._h
            scale = min(w_scale, h_scale, 1)
            self.canvas.scale_before = scale
            self.canvas.scale_dst = scale
            self.canvas.view_before = (0, 0)
            self.canvas.view_dst = (0, 0)
            self.canvas._updateView(scale, (0, 0), True)

            self.image_size = (self.current_frame._w, self.current_frame._h)
            self.video_info_size.setText(f'size: ({self.image_size[0]}, {self.image_size[1]})')

        self.addChild(self.p_bar)

    def _labelImage(self) -> None:
        if self.current_frame is None:
            return

        frame = surface2mat(self.current_frame.image)
        labels = self.model.inference(frame)
        labeled_frame = frame.copy()
        for l in labels:
            for i, p in enumerate(l.kpts):
                p1 = [int(p[0]), int(p[1])]
                p = l.kpts[(i + 1) % 4]
                p2 = [int(p[0]), int(p[1])]
                cv2.line(labeled_frame, p1, p2, (0, 255, 0), 2)

            p = (int(l.kpts[0][0]), int(l.kpts[0][1]) - 10)
            cv2.putText(labeled_frame, f"id: {l.cls_id}", p, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 0), 2)

        if self.current_labeled_frame is not None:
            self.current_labeled_frame.kill()
        self.current_labeled_frame = Image(mat2surface(labeled_frame))
        self.current_labeled_frame.setLight(light_to_gamma(self.image_light))

    def _updateImage(self, show_label: bool) -> None:
        if show_label and self.current_labeled_frame is None:
            self._labelImage()

        if show_label and self.current_labeled_frame is not None:
            self.canvas.setChildren([self.current_labeled_frame])
        
        if not show_label and self.current_frame is not None:
            self.canvas.setChildren([self.current_frame])

    def _setFrame(self, frame_idx: int) -> None:
        if frame_idx < 0:
            frame_idx = 0
        elif frame_idx > self.total_frames:
            frame_idx = self.total_frames

        self.current_frame_idx = frame_idx
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
        ret, frame = self.cap.read()
        if not ret:
            return

        self._clearImage()

        self.current_frame = Image(mat2surface(frame))
        self.current_frame.setLight(light_to_gamma(self.image_light))
        if self.label:
            self._labelImage()

        self._updateImage(self.label)
        self.p_bar.set(self.current_frame_idx / self.total_frames * self.video_duration)

    def _stopPlaying(self) -> None:
        if not self.playing:
            return
        self.playing = False
        self.switch_pause.turnOff()
        self.switch_pause.redraw()

    def onHide(self):
        self.button_back.resetState()

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.playing:
            if self.current_frame_idx <= self.total_frames:
                self._setFrame(self.current_frame_idx + 1)
                self.canvas.redraw()
            else: # Automatic stop.
                self._stopPlaying()