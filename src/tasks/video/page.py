import os
from datetime import datetime
import pygame

import cv2

from ... import pygame_gui as ui
from ...components.light_bar import LightBar
from ...components.stacked_page import StackedPage
from ...components.switch import Switch
from ...label import Image
from ...utils.config import ConfigManager, openVideo
from ...utils.imgproc import mat2surface
from .video_bar import VideoBar


def light_to_gamma(light: float) -> float:
    '''Light ranges from -1 to 1'''
    if light < 0:
        return -light + 1.0
    if light > 0:
        return -light * 0.9 + 1.0
    return 1.0

def get_current_time_formatted():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]
    return formatted_time

class VideoPage(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incides: dict):
        super().__init__(w, h, x, y)

        # variables
        self.config_manager = ConfigManager('./user_data.json')

        self.video_path = "resources/test_dataset/test.mp4" \
            if self.config_manager['last_video_path'] is None \
            else self.config_manager['last_video_path']

        self.image_save_folder = os.path.join(
            os.path.dirname(self.video_path),
            'saved_extract_image'
        )

        self: cv2.VideoCapture
        self.fps: float
        self.total_frames: int
        self.video_duration: float # seconds

        self.current_frame_idx = -1
        self.current_frame: Image = None
        self.current_labeled_frame: Image = None

        self.image_light = 0.0
        self.playing = False
        self.show_label = False

        # components
        color_theme = ui.color.LightColorTheme()

        def on_open():
            self.video_path = openVideo()
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

        self.button_back = ui.components.CloseButton(
            w=int(40*1.5),
            h=40,
            x=w-int(40*1.5),
            y=0,
            color=ui.color.dark(color_theme.Surface,3),
            cross_color=color_theme.OnSurface,
            on_press=lambda : self.setPage(page_incides['main_menu'], True)
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

        def on_save() -> None:
            path = os.path.join(self.image_save_folder, f'{get_current_time_formatted()}.jpg')
            pygame.image.save(self.current_frame.orig_image, path)
        button_save = ui.components.IconButton(
            w=btn_size,
            h=btn_size,
            x=760,
            y=btn_y,
            icon='resources/icons/save.png',
            on_press=on_save,
            cursor_change=True
        )

        # configure
        self._loadVideoInfo(self.video_path)
        self._setFrame(0)
        self.setBackgroundColor((255, 255, 255))

        # succeed
        self.addChild(button_open)
        self.addChild(self.button_back)
        self.addChild(self.canvas)
        self.addChild(self.p_bar)
        self.addChild(self.switch_pause)
        self.addChild(button_prev_frame)
        self.addChild(button_next_frame)
        self.addChild(light_bar)
        self.addChild(button_save)

    def _clearOldImage(self) -> None:
        if self.current_frame is not None:
            self.current_frame.kill()
            self.current_frame = None
        if self.current_labeled_frame is not None:
            self.current_labeled_frame.kill()
            self.current_labeled_frame = None

    def _loadVideoInfo(self, video_path) -> None:
        self._clearOldImage()

        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_duration = self.total_frames / self.fps

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

        self.addChild(self.p_bar)

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

        self._clearOldImage()

        self.current_frame = Image(mat2surface(frame))
        self.current_frame.setLight(light_to_gamma(self.image_light))
        self.canvas.addChild(self.current_frame)
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