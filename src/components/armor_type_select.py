from typing import Callable, Union

from pygame.surface import Surface

from .. import pygame_gui as ui
from ..resources_loader import ImageLoader


class ColorButton(ui.components.Selectable):
    '''
    Button to select armor color.

    ColorButton(x, y, img, img_hover, img_select, on_click)
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            img: Union[str, Surface],
            img_hover: Union[str, Surface],
            img_select: Union[str, Surface],
            on_click: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        self.image = self.loadImage(img, w, h)
        self.image_hover = self.loadImage(img_hover, w, h)
        self.image_select = self.loadImage(img_select, w, h)
        self.on_click = ui.getCallable(on_click)

    def onLeftClick(self, x: int, y: int):
        self.on_click()

    def draw(self, surface: Surface) -> None:
        if self.selected:
            surface.blit(self.image_select, (self.x, self.y))
        elif self.active:
            surface.blit(self.image_hover, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))

class ArmorTypeButton(ui.components.Selectable):
    '''
    Button to select armor type.

    ArmorTypeButton(x, y, img, type_idx)

    Theme -> Message:
    * _THEME_TYPE_CLICK -> index: int
    '''
    def __init__(self,
            w: int, h: int, x: int, y: int,
            img: Union[str, Surface],
            img_frame: Union[str, Surface],
            img_blue: Union[str, Surface],
            img_red: Union[str, Surface],
            on_click: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        self.img = self.loadImage(img, w, h)
        self.img_frame = self.loadImage(img_frame, w, h)
        self.color_backgrounds = [
            self.loadImage(img_blue, w, h),
            self.loadImage(img_red, w, h)
        ]
        self.on_click = ui.getCallable(on_click)

        self.color_idx = -1
        self.selected = False

    def onLeftClick(self, x: int, y: int):
        self.on_click()

    def setColor(self, color_idx: int):
        # 0: blue, 1: red
        self.color_idx = color_idx

    def draw(self, surface: Surface):
        if self.color_idx != -1:
            surface.blit(self.color_backgrounds[self.color_idx], (self.x, self.y))

        surface.blit(self.img, (self.x, self.y))

        if self.selected:
            surface.blit(self.img_frame, (self.x, self.y))

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

        self.on_select = ui.getCallable(on_select)

        loader = ImageLoader()
        def on_click_blue():
            self.setColor(0)
            self.on_select(0)
        def on_click_red():
            self.setColor(1)
            self.on_select(1)
        self.buttons = [
            ColorButton( # blue
                btn_w, btn_h, 0, 0,
                loader['icon']['color']['blue'],
                loader['icon']['color']['blue_hover'],
                loader['icon']['color']['blue_selected'],
                on_click_blue
            ),
            ColorButton( # red
                btn_w, btn_h, btn_w + btn_padding, 0,
                loader['icon']['color']['red'],
                loader['icon']['color']['red_hover'],
                loader['icon']['color']['red_selected'],
                on_click_red
            )
        ]

        for btn in self.buttons:
            self.addChild(btn)

    def setColor(self, color_idx: int):
        for i, btn in enumerate(self.buttons):
            if color_idx == i:
                btn.select()
            else:
                btn.unselect()

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

        self.on_select = ui.getCallable(on_select)

        loader = ImageLoader()['icon']
        loader_type = loader['type']
        type_icons = [
            loader_type['sentry'], loader_type['1'],
            loader_type['2'], loader_type['3'],
            loader_type['4'], loader_type['5'],
            loader_type['outpost'], loader_type['base']
        ]
        self.buttons = [
            ArmorTypeButton(
                icon_w, icon_h,
                (icon_w + icon_padx) * (i % 4),
                (icon_h + icon_pady) * (i // 4),
                icon,
                loader['selected_frame'],
                loader['type']['bg_blue'],
                loader['type']['bg_red']
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
            if type_idx == i:
                btn.select()
            else:
                btn.unselect()

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

        self.on_select = ui.getCallable(on_select)

        def on_color_select(idx: int):
            self.setColorType(idx)
            self.on_select(self.getType())
        def on_type_select(idx: int):
            self.setArmorType(idx)
            self.on_select(self.getType())
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