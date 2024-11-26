# Author: EclidFundgue <1011379214@qq.com>.

__all__ = [
    'color',
    'components',
    'constants',
    'draw',
    'logger',
    'timer',

    # UI
    'Main',

    # Functions
    'getCallable',
    'singleton',
]

from . import color, components, constants, draw, logger, timer
from .decorators import getCallable, singleton
from .uimain import UIMain as Main
