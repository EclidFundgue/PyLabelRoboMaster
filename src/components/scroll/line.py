from typing import Callable, Tuple, Union

import pygame
from pygame import Surface as pg_Surface

from ... import pygame_gui as ui
from ...resources_loader import ImageLoader


class TextImage(ui.components.BaseComponent):
    '''
    Provide image of text.

    TextImage(text, color, font, runtime_render)
    '''
    DEFAULT_FONT = None

    def __init__(self, text: str = '',
                 color: Tuple[int] = (0, 0, 0),
                 font: pygame.font.Font = None):
        self._initDefauleFont()

        self.text = text
        self.color = color
        self.font = font if font is not None else TextImage.DEFAULT_FONT
        self.text_img = self.font.render(text, True, self.color)

        super().__init__(*self.text_img.get_size())

    def _initDefauleFont(self) -> None:
        ''' Initialize DEFAULT_FONT after pygame initialized. '''
        if TextImage.DEFAULT_FONT is None:
            TextImage.DEFAULT_FONT = pygame.font.SysFont('simsun', 16)

    def draw(self, surface: pg_Surface) -> None:
        surface.blit(self.text_img, (self.x, self.y))

class _DoubleClickButton(ui.components.BaseComponent):
    '''
    Button that needs double click.

    _DoubleClickButton(w, h, x, y, img, img2, command)
    * command() -> None
    '''
    def __init__(self, w: int, h: int, x: int, y: int,
                 img: Union[str, pg_Surface],
                 img2: Union[str, pg_Surface],
                 command: Callable[[], None] = None):
        super().__init__(w, h, x, y)

        # Load images
        self.img: pg_Surface = self.loadImage(img, w, h)
        self.img2: pg_Surface = self.loadImage(img2, w, h)

        self.command: Callable[[], None] = ui.getCallable(command)
        self.confirmed = False

    def kill(self) -> None:
        self.command = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        if not self.confirmed:
            self.confirmed = True
        else:
            self.command()

    def offHover(self) -> None:
        self.confirmed = False

    def draw(self, surface: pg_Surface) -> None:
        if self.confirmed:
            surface.blit(self.img2, (self.x, self.y))
        else:
            surface.blit(self.img, (self.x, self.y))

class _GenericFileLine(ui.components.Selectable):
    '''
    FileLine shows file name. It calls `on_select` when selected.
    Position will be managed by its parent component.

    This component may be created in large quantities, and inheriting
    the `Surface` object will consume a lot of memory, so inheriting
    `BaseComponent` for optimization here.

    _GenericFileLine(
        w, h, filename,
        button_img,
        button_img2,
        on_select,
        command,
        text_padx,
        smooth_color_change
    )
    * on_select() -> None
    * command() -> None
    '''
    def __init__(self, w: int, h: int,
                 filename: str,
                 button_img: Union[str, pg_Surface],
                 button_img2: Union[str, pg_Surface],
                 on_select: Callable[[], None] = None,
                 command: Callable[[], None] = None,
                 text_padx: int = 5,
                 smooth_color_change: bool = True):
        super().__init__(w, h, 0, 0)

        self.filename = filename
        self.on_select: Callable[[], None] = ui.getCallable(on_select)
        self.command: Callable[[], None] = ui.getCallable(command)
        self.text_padx = text_padx

        # background color
        color_theme = ui.LightColorTheme()
        self.bg_color = color_theme.SecondaryContainer
        self.bg_color_hover = (self.bg_color[0] - 15, self.bg_color[1] - 29, self.bg_color[2] - 6)
        self.bg_color_selected = color_theme.OnSecondaryContainer
        smooth_time_period = 0.03 if smooth_color_change else 0.0
        self.bg_smooth_color = ui.SmoothColor(smooth_time_period, self.bg_color)

        # text image
        self.text_img = TextImage(filename, color_theme.OnSecondaryContainer)
        self.pressed_text_img = TextImage(filename, color_theme.SecondaryContainer)
        self._alignTextImage(self.text_img)
        self._alignTextImage(self.pressed_text_img)

        # command button
        btn_w = 16
        btn_h = 16
        self.command_button = _DoubleClickButton(
            btn_w, btn_h, 2 * w // 3, (self.h - btn_h) // 2,
            button_img, button_img2,
            self._onCommandButtonClick
        )

        # succeed
        self.addChild(self.text_img)
        self.addChild(self.command_button)

    def _onCommandButtonClick(self) -> None:
        self.command()

    def _alignTextImage(self, img: ui.components.BaseComponent) -> None:
        ''' Align x to text_padx and y to center '''
        img.x = self.text_padx
        img.y = (self.h - img.h) // 2

    def kill(self) -> None:
        self.text_img = None
        self.command_button = None
        self.on_select = None
        self.command = None
        return super().kill()

    def select(self):
        self.removeChild(self.text_img)
        self.addChild(self.pressed_text_img)
        super().select()

    def unselect(self):
        self.removeChild(self.pressed_text_img)
        self.addChild(self.text_img)
        super().unselect()

    def onLeftClick(self, x: int, y: int) -> None:
        # This component may be killed when on_delect is called.
        if not self.alive:
            return

        if not self.command_button.active:
            self.on_select()

    def update(self, events=None) -> None:
        super().update(events)

        if self.selected:
            self.bg_smooth_color.setColor(self.bg_color_selected)
        elif self.active:
            self.bg_smooth_color.setColor(self.bg_color_hover)
        else:
            self.bg_smooth_color.setColor(self.bg_color)

    def draw(self, surface: pg_Surface) -> None:
        pygame.draw.rect(
            surface,
            self.bg_smooth_color.getCurrentColor(),
            pygame.Rect(self.x, self.y, self.w, self.h)
        )

        for ch in self.child_components:
            rel_pos = (ch.x, ch.y)
            abs_pos = (self.x + ch.x, self.y + ch.y)
            ch.x, ch.y = abs_pos
            ch.draw(surface)
            ch.x, ch.y = rel_pos

class ImageFileLine(_GenericFileLine):
    '''
    Calls `on_delete` when deleted.

    ImageFileLine(
        w, h, filename,
        on_select,
        on_delete,
        text_padx,
        smooth_color_change
    )
    * on_select() -> None
    * on_delete() -> None
    '''

    DELETE_BUTTON_IMG = None
    DELETE_BUTTON_IMG2 = None

    def __init__(self, w: int, h: int,
                 filename: str,
                 on_select: Callable[[], None] = None,
                 on_delete: Callable[[], None] = None,
                 text_padx: int = 5,
                 smooth_color_change: bool = True):
        self._initButtonImages()
        super().__init__(
            w, h, filename,
            ImageFileLine.DELETE_BUTTON_IMG,
            ImageFileLine.DELETE_BUTTON_IMG2,
            on_select,
            on_delete,
            text_padx,
            smooth_color_change
        )

    def _initButtonImages(self):
        if ImageFileLine.DELETE_BUTTON_IMG is not None and \
            ImageFileLine.DELETE_BUTTON_IMG2 is not None:
            return

        btn_w = 16
        btn_h = 16
        loader = ImageLoader()
        ImageFileLine.DELETE_BUTTON_IMG = self.loadImage(
            loader['button']['delete'], btn_w, btn_h
        )
        ImageFileLine.DELETE_BUTTON_IMG2 = self.loadImage(
            loader['button']['delete_confirmed'], btn_w, btn_h
        )

class DesertedFileLine(_GenericFileLine):
    '''
    Calls `on_restore` when restored.

    DesertedFileLine(
        w, h, filename,
        on_select,
        on_restore,
        text_padx,
        smooth_color_change
    )
    * on_select() -> None
    * on_restore() -> None
    '''

    RESTORE_BUTTON_IMG = None
    RESTORE_BUTTON_IMG2 = None

    def __init__(self, w: int, h: int,
                 filename: str,
                 on_select: Callable[[], None] = None,
                 on_restore: Callable[[], None] = None,
                 text_padx: int = 5,
                 smooth_color_change: bool = True):
        self._initButtonImages()
        super().__init__(
            w, h, filename,
            DesertedFileLine.RESTORE_BUTTON_IMG,
            DesertedFileLine.RESTORE_BUTTON_IMG2,
            on_select,
            on_restore,
            text_padx,
            smooth_color_change
        )

    def _initButtonImages(self):
        if DesertedFileLine.RESTORE_BUTTON_IMG is not None and \
            DesertedFileLine.RESTORE_BUTTON_IMG2 is not None:
            return

        btn_w = 16
        btn_h = 16
        loader = ImageLoader()
        DesertedFileLine.RESTORE_BUTTON_IMG = self.loadImage(
            loader['button']['restore'], btn_w, btn_h
        )
        DesertedFileLine.RESTORE_BUTTON_IMG2 = self.loadImage(
            loader['button']['restore_confirmed'], btn_w, btn_h
        )