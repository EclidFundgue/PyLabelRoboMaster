import time
import math
from typing import Tuple

from .f___loger import fuck as f_error


def _interpolate_linear(t: float) -> float:
    ''' Linear interpolation function. '''
    return t

def _interpolate_poly2(t: float) -> float:
    ''' Polynomial 2nd degree interpolation function. '''
    # 1 - (1 - t)^2 = -t^2 + 2t = t(2 - t)
    return (2 - t) * t

def _interpolate_polyn1(t: float) -> float:
    ''' Polynomial -1st degree interpolation function. '''
    # (- 1 / (t * 2 + 0.5) + 2) / 1.6
    return - 0.625 / (t + t + 0.5) + 1.25

class SmoothNormFloat:
    '''
    Value is 0 when object is created, and smoothly transition to 1 over a
    time period using a specified interpolation function.

    SmoothNormFloat(time_period_second, interpolation)

    Methods:
    * getCurrentValue() -> float
    * isFinished() -> bool
    * reset() -> None
    * finish() -> None
    '''

    INTERP_LINEAR = 0
    INTERP_POLY2 = 1
    INTERP_POLYN1 = 2
    INTERP_FUNCTIONS = {
        INTERP_LINEAR: _interpolate_linear,
        INTERP_POLY2: _interpolate_poly2,
        INTERP_POLYN1: _interpolate_polyn1
    }

    def __init__(self, time_period_second: float = 0, interpolation: int = INTERP_LINEAR):
        if time_period_second < 0:
            f_error("Time period must be non-negative.", ValueError, self)

        self.time_period = time_period_second
        self.interpolation = interpolation

        self.start_time = time.time()
        self.end_time = self.start_time + self.time_period

        self.interpolated_start_value = self.INTERP_FUNCTIONS[self.interpolation](0.0)
        self.interpolated_end_value = self.INTERP_FUNCTIONS[self.interpolation](1.0)

    def getCurrentValue(self) -> float:
        ''' Returns the current value between 0 and 1. '''
        current_time = time.time()

        if current_time >= self.end_time:
            return self.interpolated_end_value

        if current_time < self.start_time:
            return self.interpolated_start_value

        time_delta = current_time - self.start_time
        return self.INTERP_FUNCTIONS[self.interpolation](time_delta / self.time_period)

    def isFinished(self) -> bool:
        ''' Returns True if the time period has elapsed. '''
        return time.time() >= self.end_time

    def reset(self) -> None:
        ''' Reset start time to current time. '''
        self.start_time = time.time()
        self.end_time = self.start_time + self.time_period

    def finish(self) -> None:
        ''' Set current value to end value. '''
        self.end_time = time.time()
        self.start_time = self.end_time - self.time_period

class SmoothFloat:
    '''
    A class that smoothly transitions between two values over a specified time period.

    SmoothFloat(time_period_second, value, interpolation)

    Methods:
    * getCurrentValue() -> float
    * getEndValue() -> float
    * isFinished() -> bool
    * setValue(value, use_smooth) -> None
    '''

    INTERP_LINEAR = SmoothNormFloat.INTERP_LINEAR
    INTERP_POLY2 = SmoothNormFloat.INTERP_POLY2
    INTERP_POLYN1 = SmoothNormFloat.INTERP_POLYN1

    def __init__(self, time_period_second: float, value: float, interpolation: int = INTERP_LINEAR):
        self.time_period = time_period_second
        self.start_value = value
        self.end_value = value

        self.value = SmoothNormFloat(time_period_second, interpolation)

    def getCurrentValue(self) -> float:
        ''' Returns the current value between the start and end values. '''
        current_value = self.value.getCurrentValue()
        return self.start_value + (self.end_value - self.start_value) * current_value

    def getEndValue(self) -> float:
        ''' Returns the end value. '''
        return self.end_value

    def isFinished(self) -> bool:
        ''' Returns True if the time period has elapsed. '''
        return self.value.isFinished()

    def setValue(self, value: float, use_smooth: bool = True) -> None:
        ''' Set the end value and reset the start value to the current value. '''
        if value == self.end_value:
            return

        self.start_value = self.getCurrentValue()
        self.end_value = value
        if use_smooth:
            self.value.reset()
        else:
            self.value.finish()

class SmoothColor:
    '''
    A class that smoothly transitions between two colors over a specified time period.

    SmoothColor(time_period_second, color)

    Methods:
    * getCurrentColor() -> Tuple[int, int, int]
    * setColor(color, use_smooth) -> None
    '''
    def __init__(self, time_period_second: float, color: Tuple[int, int, int]):
        self.time_period = time_period_second
        self.start_color = color
        self.end_color = color

        self.value = SmoothNormFloat(time_period_second, SmoothNormFloat.INTERP_LINEAR)

    def getCurrentColor(self) -> Tuple[int, int, int]:
        ''' Returns the current color as a tuple of (r, g, b) values. '''
        current_value = self.value.getCurrentValue()
        if current_value == 1:
            return self.end_color
        if current_value == 0:
            return self.start_color
        return tuple(
            int(self.start_color[i] + (self.end_color[i] - self.start_color[i]) * current_value)
            for i in range(3)
        )

    def setColor(self, color: Tuple[int, int, int], use_smooth: bool = True) -> None:
        ''' Set the end color and reset the start color to the current color. '''
        if color == self.end_color:
            return

        self.start_color = self.getCurrentColor()
        self.end_color = color
        if use_smooth:
            self.value.reset()
        else:
            self.value.finish()