import json
import os
import tkinter as tk
from tkinter import filedialog
from typing import Any, Tuple


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
            'last_image_index': None
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
    root = tk.Tk()
    root.withdraw()

    images_folder = filedialog.askdirectory(title='Images')
    labels_folder = filedialog.askdirectory(title='Labels')
    deserted_folder = os.path.join(images_folder, 'deserted')
    if not os.path.exists(deserted_folder):
        os.makedirs(deserted_folder)
    return images_folder, labels_folder, deserted_folder