import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class ConfigFileScrollBox:
    size_box = (260, 345)

    rect_prev_btn = (30, 26, 0, 2)          # change to previous image
    rect_next_btn = (30, 26, 210, 2)        # change to next image
    rect_navigator = (160, 30, 40, 0)       # current filename infomation

    size_line = (200, 20)                   # size of each line
    rect_scroll = (230, 300, 0, 30)         # rect of scroll box

    font_size = 13
    font_name = 'simsun'
    font_color = (0, 0, 0)
    text_padx = 5

class ConfigArmorTypeSelect:
    size_box = (76, 203)            # whole box

    rect_colors = (76, 27, 0, 0)    # color icons box
    size_color = (27, 27)           # color icon size
    pos_blue = (3, 0)               # blue button
    pos_red = (46, 0)               # red button

    rect_types = (76, 164, 0, 39)   # armor type box
    size_armor_type = (32, 32)
    armor_icon_padding = 12

class ConfigToolBar:
    pos_type = (20, 20)

    pos_btn_resotre = (20, 250)
    pos_btn_undo = (70, 250)

    pos_btn_add = (20, 300)
    pos_btn_delete = (70, 300)

    pos_swch_preproc = (20, 350)
    pos_btn_find = (70, 350)
    pos_btn_correct = (120, 350)

    pos_swch_auto = (20, 400)

    pos_scroll = (20, 490)

CANVAS_SIZE = (1000, 840)
GUI_SIZE = (280, 840)