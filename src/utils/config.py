import json
import os
import tkinter as tk
from tkinter import filedialog
from typing import Any, Tuple

from .. import pygame_gui as ui

try:
    root = tk.Tk()
    root.withdraw()
    _has_display_device = True
except tk.TclError:
    _has_display_device = False

@ui.utils.singleton
class ConfigManager:
    def __init__(self, path: str):
        self.path = path

        if not os.path.exists(path):
            self._createJsonFile(path)

        with open(path, 'r') as f:
            self.data = json.load(f)

    def _createJsonFile(self, path) -> None:
        folder, _ = os.path.split(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        default = {
            'load_network': False,
            'last_images_folder': None,
            'last_labels_folder': None,
            'last_image_index': None,
            'last_video_path': None
        }

        with open(path, 'w') as f:
            json.dump(default, f, indent=4)

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

def openDir() -> Tuple[str, str, str]:
    if _has_display_device:
        images_folder = filedialog.askdirectory(title='Images')
        labels_folder = filedialog.askdirectory(title='Labels')
    else:
        ui.logger.error(
            'no display name and no $DISPLAY environment variable',
            tk.TclError
        )
    deserted_folder = os.path.join(images_folder, 'deserted')
    if not os.path.exists(deserted_folder):
        os.makedirs(deserted_folder)
    return images_folder, labels_folder, deserted_folder

def openVideo() -> str:
    if _has_display_device:
        return filedialog.askopenfile(title='Video').name
    else:
        ui.logger.error(
            'no display name and no $DISPLAY environment variable',
            tk.TclError
        )