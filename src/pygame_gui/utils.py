import os
import threading
from typing import Tuple, TypeVar, Union

import pygame

from . import logger

T = TypeVar('T')


def clipRect(
    rect: Tuple[int, int, int, int],
    surface: pygame.Surface
) -> Tuple[int, int, int, int]:
    w, h, xl, yt = rect
    xr = xl + w
    yb = yt + h
    xl = max(0, min(xl, surface.get_width()))
    yt = max(0, min(yt, surface.get_height()))
    xr = max(0, min(xr, surface.get_width()))
    yb = max(0, min(yb, surface.get_height()))
    return (xr - xl, yb - yt, xl, yt)

def __emtpyFunc(*args, **kwargs):
    pass

def getCallable(func: Union[T, None] = None) -> T:
    '''Returns the function itself or an empty function if None is given. '''
    if func is None:
        return __emtpyFunc
    if not callable(func):
        logger.error("The given function is not callable.", TypeError)
    return func

def loadImage(
    img: Union[str, pygame.Surface],
    w: int = None,
    h: int = None,
    smooth_scale = False
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
    elif smooth_scale:
        return pygame.transform.smoothscale(ret_img, (w, h))
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

def drawRoundedRect(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    rect: Union[pygame.Rect, Tuple[int, int, int, int]],
    radius: float,
) -> None:
    if isinstance(rect, tuple):
        rect = pygame.Rect(rect)

    xl, xr = rect.left + radius, rect.right - radius
    yt, yb = rect.top + radius, rect.bottom - radius
    # draw rounded corners
    pygame.draw.circle(surface, color, (xl, yt), radius)
    pygame.draw.circle(surface, color, (xr, yt), radius)
    pygame.draw.circle(surface, color, (xl, yb), radius)
    pygame.draw.circle(surface, color, (xr, yb), radius)

    # fill center
    pygame.draw.rect(surface, color, (rect.left, yt, rect.width, rect.height - radius * 2))
    pygame.draw.rect(surface, color, (xl, rect.top, rect.width - radius * 2, rect.height))