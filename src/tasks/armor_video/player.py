import cv2

from ... import pygame_gui as ui
from ...label import Image
from ...utils.imgproc import mat2surface
from .video_bar import VideoBar


class VideoPlayer(ui.components.RectContainer):
    def __init__(self, w: int, h: int, x: int, y: int, video_path: str):
        super().__init__(w, h, x, y)

        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_seconds = self.total_frames / self.fps

        self.current_frame_image = None