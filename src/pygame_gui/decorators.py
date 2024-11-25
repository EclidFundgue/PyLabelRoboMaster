import threading
from typing import Callable

from . import logger


def singleton(cls: type):
    ''' A decorator to make a class a singleton. '''
    instances = dict()
    _instance_lock = threading.Lock()

    def get_instance(*args, **kwargs):
        with _instance_lock:
            if instances.get(cls, None) is None:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def __emtpyFunc(*args, **kwargs):
    pass

def getCallable(func: Callable = None) -> Callable:
    '''Returns the function itself or an empty function if None is given. '''
    if func is None:
        return __emtpyFunc
    if not callable(func):
        logger.error("The given function is not callable.", TypeError)
    return func