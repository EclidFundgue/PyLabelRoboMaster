import json
import os
from typing import Any


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
            'last_image_file': None,
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