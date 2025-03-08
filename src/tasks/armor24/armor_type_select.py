import os
from typing import Callable, Tuple, Union

import pygame

from ... import pygame_gui as ui


class ColorButton(ui.components.TextButton):
    '''
    Button to select armor color.

    ColorButton(w, h, x, y, text, color, on_click)
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        text: str,
        color: Tuple[int, int, int],
        on_click: Callable[[], None] = None
    ):
        super().__init__(
            w, h, x, y,
            text=text,
            font=pygame.font.SysFont('simsun bold', 24),
            on_press=on_click,
            cursor_change = True
        )
        self.color = color
        self.color2 = ui.color.light(self.color, 3) # hovered
        self.color3 = ui.color.light(self.color, 8) # pressed

        self.text_color = (0, 0, 0)
        self.text_color2 = (0, 0, 0) # pressed
        self.label.setColor(self.text_color)

class TypeButton(ui.components.Selectable):
    '''
    TypeButton(w, h, x, y, icon, on_click)
    * on_click(type_id) -> None

    Methods:
    * setColor(color_id) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        icon: Union[str, pygame.Surface],
        type_id: int = 0,
        on_click: Callable[[int], None] = None
    ):
        super().__init__(w, h, x, y)
        self.icon = ui.utils.loadImage(icon)
        self.type_id = type_id
        self.on_click = ui.utils.getCallable(on_click)

        color_theme = ui.color.LightColorTheme()
        self.bg_color_blue = (169, 230, 255) # selected
        self.bg_color_red = (255, 158, 158) # selected
        self.bg_color_gray = (190, 190, 190) # normal
        self.bg_color_lightgray = (255, 255, 255) # hover

        self.color_id = 0

    def setColor(self, color_id: int) -> None:
        self.color_id = color_id

    def onLeftClick(self, x: int, y: int):
        if not self.active:
            return
        self.on_click(self.type_id)
        self.redraw()

    def onMouseEnter(self):
        self.redraw()
    
    def onMouseLeave(self):
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int):
        if self.selected:
            if self.color_id == 0:
                bg_color = self.bg_color_blue
            else:
                bg_color = self.bg_color_red
        elif self.active:
            bg_color = self.bg_color_lightgray
        else:
            bg_color = self.bg_color_gray

        ui.utils.drawRoundedRect(
            surface,
            bg_color,
            (x_start, y_start, self.w, self.h),
            self.w // 4
        )

        icon_w, icon_h = self.icon.get_size()
        x = x_start + (self.w - icon_w) // 2
        y = y_start + (self.h - icon_h) // 2
        surface.blit(self.icon, (x, y))

class ArmorClassSelection(ui.components.RectContainer):
    '''
    ArmorClassSelection(w, h, x, y, on_select)
    * on_select(cls_id) -> None

    Methods:
    * setClass(cls_id) -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        on_select: Callable[[int], None] = None
    ):
        super().__init__(w, h, x, y)
        self.on_select = ui.utils.getCallable(on_select)

        self.cls_id = 0

        # Initialize variables
        color_bar_h = h // 4
        color_button_y = 8
        color_button_h = color_bar_h - 2 * color_button_y
        type_button_size = min(
            w // (7 + 4 * 3),
            h // (4 + 2 * 3)
        ) * 3
        type_pixel_w = (w - 4 * type_button_size) // 7
        type_pixel_h = (h - color_bar_h - 2 * type_button_size) // 4

        # Create objects
        color_bar = ui.components.RectContainer(
            w, color_bar_h, 0, 0
        )

        def _set_color_blue():
            _type_id = self.cls_id % 8
            self.cls_id = _type_id
            self.on_select(self.cls_id)
            for i in range(8):
                self.type_buttons[i].setColor(0)
            self.redraw()
        def _set_color_red():
            _type_id = self.cls_id % 8
            self.cls_id = _type_id + 8
            self.on_select(self.cls_id)
            for i in range(8):
                self.type_buttons[i].setColor(1)
            self.redraw()
        btn_blue = ColorButton(
            w=w*2//7,
            h=color_button_h,
            x=w//7,
            y=color_button_y,
            text='Blue',
            color = (169, 230, 255),
            on_click=_set_color_blue
        )
        btn_red = ColorButton(
            w=w*2//7,
            h=color_button_h,
            x=w*4//7,
            y=color_button_y,
            text='Red',
            color = (255, 158, 158),
            on_click=_set_color_red
        )

        type_bar = ui.components.RectContainer(
            w, h-color_bar_h, 0, color_bar_h
        )
        prefix = './resources/armor_icons'
        def _load_image(image: Union[str, pygame.Surface]) -> pygame.Surface:
            return ui.utils.loadImage(
                img=os.path.join(prefix, image),
                w=type_button_size-10,
                h=type_button_size-10,
                smooth_scale=True
            )
        type_icons = [
            _load_image('sentry.png'),
            _load_image('1.png'),
            _load_image('2.png'),
            _load_image('3.png'),
            _load_image('4.png'),
            _load_image('5.png'),
            _load_image('outpost.png'),
            _load_image('base1.png'),
        ]
        def on_type_button_click(type_id: int) -> None:
            for i in range(8):
                if i == type_id:
                    self.type_buttons[i].select()
                else:
                    self.type_buttons[i].unselect()
            color_id = self.cls_id // 8
            self.cls_id = color_id * 8 + type_id
            self.on_select(self.cls_id)
        self.type_buttons = [
            TypeButton(
                w=type_button_size,
                h=type_button_size,
                x=2 * type_pixel_w + (i % 4) * (type_button_size + type_pixel_w),
                y=type_pixel_h + (i // 4) * (type_button_size + type_pixel_h),
                icon=type_icons[i],
                type_id=i,
                on_click=on_type_button_click
            ) for i in range(8)
        ]

        # Configure objects

        # Manage Success
        self.addChild(color_bar)
        color_bar.addChild(btn_blue)
        color_bar.addChild(btn_red)
        self.addChild(type_bar)
        for button in self.type_buttons:
            type_bar.addChild(button)

    def setClass(self, cls_id: int) -> None:
        color_id = cls_id // 8
        type_id = cls_id % 8
        for i in range(8):
            self.type_buttons[i].setColor(color_id)
            if i == type_id:
                self.type_buttons[i].select()
            else:
                self.type_buttons[i].unselect()
        self.cls_id = cls_id