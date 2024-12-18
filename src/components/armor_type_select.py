from typing import Callable, Union
import os

import pygame

from .. import pygame_gui as ui


class ColorButton(ui.components.Base):
    '''
    Button to select armor color.

    ColorButton(x, y, img, img_hover, img_select, on_click)
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        img: Union[str, pygame.Surface],
        img_hover: Union[str, pygame.Surface],
        img_select: Union[str, pygame.Surface],
        on_click: Callable[[], None] = None
    ):
        super().__init__(w, h, x, y)
        self.selected = False

        self.image = ui.utils.loadImage(img, w, h)
        self.image_hover = ui.utils.loadImage(img_hover, w, h)
        self.image_select = ui.utils.loadImage(img_select, w, h)
        self.on_click = ui.utils.getCallable(on_click)

    def onLeftClick(self, x: int, y: int):
        if not self.active:
            return
        self.on_click()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.selected:
            surface.blit(self.image_select, (x_start, y_start))
        elif self.active:
            surface.blit(self.image_hover, (x_start, y_start))
        else:
            surface.blit(self.image, (x_start, y_start))

class ArmorTypeButton(ui.components.Base):
    '''
    Button to select armor type.

    ArmorTypeButton(x, y, img, type_idx)

    Theme -> Message:
    * _THEME_TYPE_CLICK -> index: int
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            img: Union[str, pygame.Surface],
            img_frame: Union[str, pygame.Surface],
            img_blue: Union[str, pygame.Surface],
            img_red: Union[str, pygame.Surface],
            on_click: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        self.img = ui.utils.loadImage(img, w, h)
        self.img_frame = ui.utils.loadImage(img_frame, w, h)
        self.color_backgrounds = [
            ui.utils.loadImage(img_blue, w, h),
            ui.utils.loadImage(img_red, w, h)
        ]
        self.on_click = ui.utils.getCallable(on_click)

        self.color_idx = -1
        self.selected = False

    def onLeftClick(self, x: int, y: int):
        if not self.active:
            return
        self.on_click()

    def setColor(self, color_idx: int):
        # 0: blue, 1: red
        self.color_idx = color_idx

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.color_idx != -1:
            surface.blit(self.color_backgrounds[self.color_idx], (x_start, y_start))

        surface.blit(self.img, (x_start, y_start))

        if self.selected:
            surface.blit(self.img_frame, (x_start, y_start))

class ColorSelectBox(ui.components.RectContainer):
    '''
    Click to select armor color.

    ColorSelectBox(w, h, x, y, btn_w, btn_h, btn_padding, on_select)

    Methods:
    * setColor(idx) -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            btn_w: int, btn_h: int,
            btn_padding: int,
            on_select: Callable[[int], None] = None):
        super().__init__(w, h, x, y)

        self.on_select = ui.utils.getCallable(on_select)

        def on_click_blue():
            self.setColor(0)
            self.on_select(0)
        def on_click_red():
            self.setColor(1)
            self.on_select(1)
        self.buttons = [
            ColorButton( # blue
                btn_w, btn_h, 0, 0,
                './resources/armor_icons/B.png',
                './resources/armor_icons/B_hover.png',
                './resources/armor_icons/B_selected.png',
                on_click_blue
            ),
            ColorButton( # red
                btn_w, btn_h, btn_w + btn_padding, 0,
                './resources/armor_icons/R.png',
                './resources/armor_icons/R_hover.png',
                './resources/armor_icons/R_selected.png',
                on_click_red
            )
        ]

        for btn in self.buttons:
            self.addChild(btn)

    def setColor(self, color_idx: int):
        for i, btn in enumerate(self.buttons):
            btn.selected = (color_idx == i)

    def kill(self) -> None:
        self.buttons = []
        self.on_select = None
        super().kill()

class ArmorTypeSelectBox(ui.components.RectContainer):
    '''
    Click to select armor type.

    ArmorTypeSelectBox(on_select)

    Methods:
    * setColor(idx) -> None
    * setSelect(idx) -> None
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            icon_w: int, icon_h: int,
            icon_padx: int, icon_pady: int,
            on_select: Callable[[int], None] = None):
        super().__init__(w, h, x, y)

        self.on_select = ui.utils.getCallable(on_select)

        prefix = './resources/armor_icons'
        type_icons = [
            ui.utils.loadImage(os.path.join(prefix, 'sentry.png')),
            ui.utils.loadImage(os.path.join(prefix, '1.png')),
            ui.utils.loadImage(os.path.join(prefix, '2.png')),
            ui.utils.loadImage(os.path.join(prefix, '3.png')),
            ui.utils.loadImage(os.path.join(prefix, '4.png')),
            ui.utils.loadImage(os.path.join(prefix, '5.png')),
            ui.utils.loadImage(os.path.join(prefix, 'outpost.png')),
            ui.utils.loadImage(os.path.join(prefix, 'base.png')),
        ]
        self.buttons = [
            ArmorTypeButton(
                icon_w, icon_h,
                (icon_w + icon_padx) * (i % 4),
                (icon_h + icon_pady) * (i // 4),
                icon,
                ui.utils.loadImage(os.path.join(prefix, 'select_frame.png')),
                ui.utils.loadImage(os.path.join(prefix, 'bg_blue.png')),
                ui.utils.loadImage(os.path.join(prefix, 'bg_red.png')),
            ) for i, icon in enumerate(type_icons)
        ]

        def get_on_click(i):
            def on_click():
                self.setSelect(i)
                self.on_select(i)
            return on_click

        for i, btn in enumerate(self.buttons):
            self.addChild(btn)
            btn.on_click = get_on_click(i)

    def setColor(self, color_idx: int):
        for btn in self.buttons:
            btn.setColor(color_idx)

    def setSelect(self, type_idx: int):
        for i, btn in enumerate(self.buttons):
            btn.selected = (type_idx == i)

    def kill(self) -> None:
        self.buttons = []
        self.on_select = None
        super().kill()

class ArmorIconsSelect(ui.components.RectContainer):
    '''
    Manage armor types on labels.

    ArmorIconsSelect(x, y, on_select)

    Methods:
    * setColorType(idx) -> None
    * setArmorType(idx) -> None
    * setType(idx) -> None
    * getType() -> int
    '''
    def __init__(self, x: int, y: int, on_select: Callable[[int], None] = None):
        color_pad = 17
        color_size = 27
        type_pad = 12
        type_size = 32
        pad = 18

        color_w = type_size * 2 + type_pad
        color_x = type_size + type_pad + 3
        type_w = type_size * 4 + type_pad * 3
        type_h = type_size * 2 + type_pad
        type_y = color_size + 16 + pad

        w = type_size * 4 + type_pad * 3 + 2 * pad
        h = color_size + 16 + type_size * 2 + type_pad + 2 * pad
        super().__init__(w, h, x, y)

        self.on_select = ui.utils.getCallable(on_select)

        def on_color_select(idx: int):
            self.setColorType(idx)
            self.on_select(self.getType())
            self.redraw()
        def on_type_select(idx: int):
            self.setArmorType(idx)
            self.on_select(self.getType())
            self.redraw()
        self.color_box = ColorSelectBox(
            w = color_w,
            h = color_size,
            x = color_x + pad,
            y = 8,
            btn_w=color_size,
            btn_h=color_size,
            btn_padding=color_pad,
            on_select=on_color_select
        )
        self.type_box = ArmorTypeSelectBox(
            w = type_w,
            h = type_h,
            x = pad,
            y = type_y,
            icon_w=type_size,
            icon_h=type_size,
            icon_padx=type_pad,
            icon_pady=type_pad,
            on_select=on_type_select
        )
        color_box_bg = ui.components.RectContainer(w, color_size + 16, 0, 0)
        type_box_bg = ui.components.RectContainer(w, type_h + 2 * pad, 0, type_y - pad)

        color_box_bg.layer = -1
        type_box_bg.layer = -1
        color_theme = ui.color.LightColorTheme()
        color_box_bg.setBackgroundColor(color_theme.OnPrimaryContainer)
        type_box_bg.setBackgroundColor(color_theme.PrimaryContainer)

        self.addChild(self.color_box)
        self.addChild(self.type_box)
        self.addChild(color_box_bg)
        self.addChild(type_box_bg)

        self.color_idx = -1
        self.type_idx = -1

    def setColorType(self, idx: int) -> None:
        self.color_idx = idx
        self.color_box.setColor(self.color_idx)
        self.type_box.setColor(self.color_idx)
    
    def setArmorType(self, idx: int) -> None:
        self.type_idx = idx
        self.type_box.setSelect(self.type_idx)

    def setType(self, idx: int) -> None:
        self.setColorType(idx // 8)
        self.setArmorType(idx % 8)

    def getType(self) -> int:
        if self.color_idx == -1:
            return -1
        if self.type_idx == -1:
            return -1
        return self.color_idx * 8 + self.type_idx

    def kill(self) -> None:
        self.color_box = None
        self.type_box = None
        self.on_select = None
        super().kill()