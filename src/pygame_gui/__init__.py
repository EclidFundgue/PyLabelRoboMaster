# Author: EclidFundgue <1011379214@qq.com>.

__all__ = [
    # UI
    'UIMain',

    # Components
    'BaseComponent',
    'Button',
    'Selectable',
    'SmoothColor',
    'SmoothFloat',
    'SmoothNormFloat',
    'Surface',
    'TextButton',

    # Functions
    'f_error',
    'f_warning',
    'getCallable',
    'singleton'
]

from .components.base import BaseComponent
from .components.button import Button, TextButton
from .components.selectable import Selectable
from .components.surface import Surface
from .decorators import getCallable, singleton
from .f___loger import damn as f_warning
from .f___loger import fuck as f_error
from .smooth import SmoothColor, SmoothFloat, SmoothNormFloat
from .uimain import UIMain
