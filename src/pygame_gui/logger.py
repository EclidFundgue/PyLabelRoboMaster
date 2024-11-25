import inspect
import sys
import time


class __Color:
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    DEFAULT = 38

def __strColor(v: str, color: int) -> str:
    ''' return font with color format '''
    return '\033[%dm' % color + v + '\033[0m'

def __getDateStr() -> str:
    t = time.localtime()
    return '[%d-%d-%d %d:%d:%d]' % (
        t.tm_year, t.tm_mon, t.tm_mday, \
        t.tm_hour, t.tm_min, t.tm_sec
    )

def __getFuncInfoStr(obj: object, f_name: str) -> str:
    ''' return "class.function(args)" '''
    f_obj = obj.__class__.__getattribute__(obj, f_name)
    argspec = inspect.getfullargspec(f_obj)
    return ' %s.%s(%s)' % (
        obj.__class__.__name__,
        f_name,
        ','.join(argspec.args)
    )

def __logGeneric(info: str, level: str, color: int,
                 err_type: Exception = None,
                 self: object = None) -> None:
    f_name = sys._getframe(2).f_code.co_name

    level = __strColor(level, color)
    date = __getDateStr()

    func_info = ''
    if self is not None and hasattr(self, f_name):
        func_info = __getFuncInfoStr(self, f_name)

    print_out_str = f'{level} {date}{func_info}\n{info}'

    if err_type is None:
        print(print_out_str)
    else:
        raise err_type(print_out_str)

def error(info: str, err_type: Exception, self: object = None) -> None:
    __logGeneric(info, 'fuck', __Color.RED, err_type, self)

def warning(info: str, self: object = None) -> None:
    __logGeneric(info, 'damn', __Color.YELLOW, None, self)