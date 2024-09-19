from .test_base import test_BaseComponent
from .test_button import test_Button
from .test_canvas import (test_Canvas_CanvasComponent, test_Canvas_Image,
                          test_Canvas_Label_Keypoint, test_Canvas_Labels)
from .test_globalvar import test_GlobalVar
from .test_loader import test_Loader
from .test_scroll import (test_Scroll_Bar, test_Scroll_FileLine,
                          test_Scroll_Lines, test_Scroll_ScrollView,
                          test_Scroll_StackedView)
from .test_switch import test_Switch

test_functions = [
    # utils
    test_Loader,                    # 0
    test_GlobalVar,                 # 1

    # basic
    test_BaseComponent,             # 2
    test_Button,                    # 3

    # toolbar
    test_Switch,                    # 4
    test_Scroll_FileLine,           # 5
    test_Scroll_Bar,                # 6
    test_Scroll_Lines,              # 7
    test_Scroll_ScrollView,         # 8
    test_Scroll_StackedView,        # 9

    # canvas
    test_Canvas_CanvasComponent,    # 10
    test_Canvas_Image,              # 11
    test_Canvas_Label_Keypoint,     # 12
    test_Canvas_Labels,             # 13
]