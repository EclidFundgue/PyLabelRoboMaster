from typing import Callable, Union

import pygame

from ... import pygame_gui as ui


class _DoubleClickButton(ui.components.Base):
    '''
    Button that needs double click.

    _DoubleClickButton(w, h, x, y, img, img2, command)
    * command() -> None
    '''
    def __init__(self,
        w: int, h: int, x: int, y: int,
        img: Union[str, pygame.Surface],
        img2: Union[str, pygame.Surface],
        command: Callable[[], None] = None
    ):
        super().__init__(w, h, x, y)
        self.redraw_parent = False

        # Load images
        self.img: pygame.Surface = ui.utils.loadImage(img, w, h)
        self.img2: pygame.Surface = ui.utils.loadImage(img2, w, h)

        self.command: Callable[[], None] = ui.utils.getCallable(command)
        self.confirmed = False

    def kill(self) -> None:
        self.command = None
        super().kill()

    def onLeftClick(self, x: int, y: int) -> None:
        if not self.active:
            return

        if not self.confirmed:
            self.confirmed = True
        else:
            self.command()

        self.redraw()

    def onMouseEnter(self):
        self.redraw()

    def onMouseLeave(self) -> None:
        self.confirmed = False
        self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        if self.confirmed:
            surface.blit(self.img2, (x_start, y_start))
        else:
            surface.blit(self.img, (x_start, y_start))

class _GenericFileLine(ui.components.Base):
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
        button_img: Union[str, pygame.Surface],
        button_img2: Union[str, pygame.Surface],
        on_select: Callable[[], None] = None,
        command: Callable[[], None] = None,
    ):
        super().__init__(w, h, 0, 0)
        self.selected = False

        self.filename = filename
        self.on_select: Callable[[], None] = ui.utils.getCallable(on_select)
        self.command: Callable[[], None] = ui.utils.getCallable(command)

        # background color
        color_theme = ui.color.LightColorTheme()
        self.bg_color = color_theme.SecondaryContainer
        self.bg_color_hover = ui.color.dark(self.bg_color, 3)
        self.bg_color_selected = color_theme.OnSecondaryContainer
        self.bg_smooth_color = ui.timer.TimedColor(0.05, self.bg_color)
        self.current_bg_color = self.bg_color

        # text image
        self.text_color = color_theme.OnSecondaryContainer
        self.text_color_selected = color_theme.SecondaryContainer
        self.text_img = ui.components.Label(w-5, h, 5, 0, filename, color=self.text_color)
        self.text_img.setAlignment(ui.constants.ALIGN_LEFT, ui.constants.ALIGN_CENTER)

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

    def kill(self) -> None:
        self.text_img = None
        self.command_button = None
        self.on_select = None
        self.command = None
        return super().kill()

    def select(self) -> None:
        self.text_img.setColor(self.text_color_selected)
        self.selected = True

    def unselect(self) -> None:
        self.text_img.setColor(self.text_color)
        self.selected = False

    def onLeftClick(self, x: int, y: int) -> None:
        # This component may be killed when on_delect is called.
        if not self.alive:
            return

        if self.active and not self.command_button.active:
            self.on_select()

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.selected:
            self.bg_smooth_color.setColor(self.bg_color_selected)
        elif self.active:
            self.bg_smooth_color.setColor(self.bg_color_hover)
        else:
            self.bg_smooth_color.setColor(self.bg_color)

        if self.current_bg_color != self.bg_smooth_color.getCurrentColor():
            self.current_bg_color = self.bg_smooth_color.getCurrentColor()
            self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.fill(self.current_bg_color)

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

    def __init__(self,
        w: int, h: int,
        filename: str,
        on_select: Callable[[], None] = None,
        on_delete: Callable[[], None] = None
    ):
        self._initButtonImages()
        super().__init__(
            w, h, filename,
            ImageFileLine.DELETE_BUTTON_IMG,
            ImageFileLine.DELETE_BUTTON_IMG2,
            on_select,
            on_delete
        )

    def _initButtonImages(self):
        if ImageFileLine.DELETE_BUTTON_IMG is not None and \
            ImageFileLine.DELETE_BUTTON_IMG2 is not None:
            return

        btn_w = 16
        btn_h = 16
        ImageFileLine.DELETE_BUTTON_IMG = ui.utils.loadImage(
            './resources/buttons/delete.png', btn_w, btn_h
        )
        ImageFileLine.DELETE_BUTTON_IMG2 = ui.utils.loadImage(
            './resources/buttons/delete_confirmed.png', btn_w, btn_h
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

    def __init__(self,
        w: int, h: int,
        filename: str,
        on_select: Callable[[], None] = None,
        on_restore: Callable[[], None] = None,
    ):
        self._initButtonImages()
        super().__init__(
            w, h, filename,
            DesertedFileLine.RESTORE_BUTTON_IMG,
            DesertedFileLine.RESTORE_BUTTON_IMG2,
            on_select,
            on_restore
        )

    def _initButtonImages(self):
        if DesertedFileLine.RESTORE_BUTTON_IMG is not None and \
            DesertedFileLine.RESTORE_BUTTON_IMG2 is not None:
            return

        btn_w = 16
        btn_h = 16
        DesertedFileLine.RESTORE_BUTTON_IMG = ui.utils.loadImage(
            './resources/buttons/undo.png', btn_w, btn_h
        )
        DesertedFileLine.RESTORE_BUTTON_IMG2 = ui.utils.loadImage(
            './resources/buttons/undo_confirmed.png', btn_w, btn_h
        )