from typing import Callable, Union

import pygame

from .. import pygame_gui as ui


class _DoubleClickButton(ui.components.Base):
    '''
    _DoubleClickButton(w, h, x, y, img, img2, command)

    Methods:
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

class FileLine(ui.components.Selectable):
    '''
    _GenericFileLine(
        w, h,
        filename,
        command_button,
        on_selected,
        padx
    )

    Methods:
    * setFilename(filename) -> None
    * getFilename() -> str
    '''
    def __init__(self,
        w: int, h: int,
        filename: str,
        command_button: _DoubleClickButton = None,
        on_selected: Callable[['FileLine'], None] = None,
        padx: int = 5
    ):
        super().__init__(w, h, 0, 0)

        self.filename = filename
        self.command_button = command_button
        self.on_selected = ui.utils.getCallable(on_selected)
        self.padx = padx

        # background color
        color_theme = ui.color.LightColorTheme()
        self.bg_color = color_theme.SecondaryContainer
        self.bg_color_hover = ui.color.dark(self.bg_color, 3)
        self.bg_color_selected = color_theme.OnSecondaryContainer
        self.smooth_bg_color = ui.timer.TimedColor(0.05, self.bg_color)
        self.current_bg_color = self.bg_color

        # text image
        self.text_color = color_theme.OnSecondaryContainer
        self.text_color_selected = color_theme.SecondaryContainer
        self.text_object = ui.components.Label(
            w=w-padx,
            h=h,
            x=padx,
            y=0,
            text=filename,
            color=self.text_color
        )
        self.text_object.setAlignment(
            ui.constants.ALIGN_LEFT,
            ui.constants.ALIGN_CENTER
        )

        # succeed
        self.addChild(self.text_object)
        self.addChild(self.command_button)

    def setFilename(self, filename: str) -> None:
        self.filename = filename
        self.text_object.setText(filename)

    def getFilename(self) -> str:
        return self.filename

    def kill(self) -> None:
        self.text_object = None
        self.on_selected = None
        return super().kill()

    def select(self) -> None:
        self.text_object.setColor(self.text_color_selected)
        self.selected = True

    def unselect(self) -> None:
        self.text_object.setColor(self.text_color)
        self.selected = False

    def onLeftClick(self, x: int, y: int) -> None:
        # This component may be killed when on_delect is called.
        if not self.active or not self.alive:
            return

        if self.active and not self.command_button.active:
            self.on_selected(self)

    def update(self, x: int, y: int, wheel: int) -> None:
        if self.selected:
            self.smooth_bg_color.setColor(self.bg_color_selected)
        elif self.active:
            self.smooth_bg_color.setColor(self.bg_color_hover)
        else:
            self.smooth_bg_color.setColor(self.bg_color)

        if self.current_bg_color != self.smooth_bg_color.getCurrentColor():
            self.current_bg_color = self.smooth_bg_color.getCurrentColor()
            self.redraw()

    def draw(self, surface: pygame.Surface, x_start: int, y_start: int) -> None:
        surface.fill(self.current_bg_color)

class ImageFileLine(FileLine):
    '''
    ImageFileLine(
        w, h, filename,
        on_selected,
        on_delete
    )
    * on_selected(fileline) -> None
    * on_delete(fileline) -> None
    '''

    DELETE_BUTTON_IMG = None
    DELETE_BUTTON_IMG2 = None

    def __init__(self,
        w: int, h: int,
        filename: str,
        on_selected: Callable[[FileLine], None] = None,
        on_delete: Callable[[FileLine], None] = None
    ):
        btn_w = 16
        btn_h = 16

        if ImageFileLine.DELETE_BUTTON_IMG is None or \
            ImageFileLine.DELETE_BUTTON_IMG2 is None:
            ImageFileLine.DELETE_BUTTON_IMG = ui.utils.loadImage(
                './resources/buttons/delete.png', btn_w, btn_h
            )
            ImageFileLine.DELETE_BUTTON_IMG2 = ui.utils.loadImage(
                './resources/buttons/delete_confirmed.png', btn_w, btn_h
            )

        on_delete = ui.utils.getCallable(on_delete)
        def on_command():
            on_delete(self)
        desert_button = _DoubleClickButton(
            w=btn_w,
            h=btn_h,
            x=2*w//3,
            y=(h-btn_h)//2,
            img=self.DELETE_BUTTON_IMG,
            img2=self.DELETE_BUTTON_IMG2,
            command=on_command
        )

        super().__init__(
            w, h,
            filename=filename,
            command_button=desert_button,
            on_selected=on_selected
        )

class DesertedFileLine(FileLine):
    '''
    DesertedFileLine(
        w, h,
        filename,
        on_selected,
        on_restore
    )
    * on_select(fileline) -> None
    * on_restore(fileline) -> None
    '''

    RESTORE_BUTTON_IMG = None
    RESTORE_BUTTON_IMG2 = None

    def __init__(self,
        w: int, h: int,
        filename: str,
        on_selected: Callable[[FileLine], None] = None,
        on_restore: Callable[[FileLine], None] = None,
    ):
        btn_w = 16
        btn_h = 16

        if DesertedFileLine.RESTORE_BUTTON_IMG is None or \
            DesertedFileLine.RESTORE_BUTTON_IMG2 is None:
            DesertedFileLine.RESTORE_BUTTON_IMG = ui.utils.loadImage(
                './resources/buttons/undo.png', btn_w, btn_h
            )
            DesertedFileLine.RESTORE_BUTTON_IMG2 = ui.utils.loadImage(
                './resources/buttons/undo_confirmed.png', btn_w, btn_h
            )

        def on_command():
            on_restore(self)
        restore_button = _DoubleClickButton(
            w=btn_w,
            h=btn_h,
            x=2*w//3,
            y=(h-btn_h)//2,
            img=self.RESTORE_BUTTON_IMG,
            img2=self.RESTORE_BUTTON_IMG2,
            command=on_command
        )
        super().__init__(
            w, h,
            filename=filename,
            command_button=restore_button,
            on_selected=on_selected
        )