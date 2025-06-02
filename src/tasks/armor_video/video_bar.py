from typing import Callable

from ... import pygame_gui as ui


def formatTime(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"

def getDurationText(current_time_s: float, total_time_s: float) -> str:
    return f"{formatTime(current_time_s)} / {formatTime(total_time_s)}"

class VideoBar(ui.components.Base):
    '''
    VideoBar(w, h, x, y, on_change)
    * on_change(time_sec) -> None

    Methods:
    * set(time_sec) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        video_length_sec: float,
        on_change: Callable[[float], None] = None
    ):
        super().__init__(w, h, x, y)
        self.on_change = ui.utils.getCallable(on_change)

        self.video_length_sec = video_length_sec
        self.time_sec = 0.0

        time_width = 150

        def _on_change(value: float) -> None:
            self.time_sec = value * self.video_length_sec
            self.time_obj.setText(
                getDurationText(self.time_sec, self.video_length_sec)
            )
            self.on_change(self.time_sec)
        self.bar = ui.components.ProgressBar(
            w - time_width, h, 0, 0, on_change=_on_change
        )

        self.time_obj = ui.components.Label(
            time_width, h, w - time_width, 0,
            text=getDurationText(0, self.video_length_sec)
        )

        self.addChild(self.bar)
        self.addChild(self.time_obj)

    def set(self, time_sec: float) -> None:
        self.time_sec = time_sec
        self.time_obj.setText(
            getDurationText(time_sec, self.video_length_sec)
        )
        self.bar.set(time_sec / self.video_length_sec)

    def kill(self) -> None:
        self.on_change = None
        self.bar = None
        self.time_obj = None
        super().kill()