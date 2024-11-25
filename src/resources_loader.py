import json
import os
from typing import Any, Union

from pygame import Surface as pg_Surface

from .pygame_gui import BaseComponent, logger, singleton
from .utils.constants import ROOT_PATH


@singleton
class ImageLoader:
    '''
    Just use it as dict. (singleton object)

    ImageLoader()
    '''

    RESOURCES_PREFIX = os.path.join(ROOT_PATH, 'resources')

    def __init__(self):
        image_path = os.path.join(ROOT_PATH, 'config/image_path.json')
        with open(image_path, 'r') as f:
            self.path_dict: dict = json.load(f)

        # load images
        self.image_dict = self._loadImageDict(self.path_dict)

    def _loadImageDict(self, path_dict: dict) -> dict:
        res = dict()
        for key, value in path_dict.items():
            if isinstance(value, dict):
                value = self._loadImageDict(value)
            elif isinstance(value, str):
                path = os.path.join(self.RESOURCES_PREFIX, value)
                value = BaseComponent.loadImage(self, path)
            else:
                logger.error(f'Invalid image path: {value}', ValueError, self)
            res[key] = value
        return res

    def __getitem__(self, key: str) -> Union[pg_Surface, dict]:
        return self.image_dict[key]

@singleton
class ConfigLoader:
    '''
    Just use it as dict. (singleton object)

    ConfigLoader()
    '''

    def __init__(self):
        self.image_path = os.path.join(ROOT_PATH, 'config/config.json')
        with open(self.image_path, 'r', encoding='utf-8') as f:
            self.config_dict: dict = json.load(f)

    def __getitem__(self, key: str) -> Any:
        return self.config_dict[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.config_dict[key] = value
        with open(self.image_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_dict, f, indent=4)