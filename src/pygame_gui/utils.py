import os
import threading
from typing import Callable, Tuple, Union

import pygame

from . import logger


def clipRect(
    rect: Tuple[int, int, int, int],
    surface: pygame.Surface
) -> Tuple[int, int, int, int]:
    w, h, x, y = rect
    x = max(0, min(x, surface.get_width() - 1))
    y = max(0, min(y, surface.get_height() - 1))
    w = max(0, min(w, surface.get_width() - x))
    h = max(0, min(h, surface.get_height() - y))
    return (w, h, x, y)

def __emtpyFunc(*args, **kwargs):
    pass

def getCallable(func: Callable = None) -> Callable:
    '''Returns the function itself or an empty function if None is given. '''
    if func is None:
        return __emtpyFunc
    if not callable(func):
        logger.error("The given function is not callable.", TypeError)
    return func

def loadImage(
    img: Union[str, pygame.Surface],
    w: int = None,
    h: int = None
) -> pygame.Surface:
    ''' Load a image and resize to (w, h). '''
    if isinstance(img, str):
        if not os.path.exists(img):
            logger.error(f'Path {img} not exists.', FileExistsError)
        ret_img = pygame.image.load(img).convert_alpha()
    elif isinstance(img, pygame.Surface):
        ret_img = img
    else:
        logger.error(f'Not accept image type: {type(img)}.', TypeError)

    if w is None:
        w = ret_img.get_size()[0]
    if h is None:
        h = ret_img.get_size()[1]

    img_w, img_h = ret_img.get_size()
    if w == img_w and h == img_h:
        return ret_img
    else:
        return pygame.transform.scale(ret_img, (w, h))

def singleton(cls: type):
    instances = dict()
    _instance_lock = threading.Lock()

    def get_instance(*args, **kwargs):
        if instances.get(cls, None) is None:
            with _instance_lock:
                if instances.get(cls, None) is None:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance