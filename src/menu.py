import pygame

from . import pygame_gui as ui
from .components.clock import Clock
from .components.stacked_page import StackedPage
from .components.switch import NTextSwitch
from .utils.config import ConfigManager


class MainMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies: dict[str, StackedPage] = page_incidies

        # initialize basic variables
        self.config_manager = ConfigManager('./user_data.json')
        color_theme = ui.color.LightColorTheme()
        font = pygame.font.SysFont('microsoftyaheibold', 40)
        font_small = pygame.font.SysFont('microsoftyaheibold', 30)

        settings_w = w // 3
        settings_h = h - 40
        settings_pad = 20

        button_w = 300
        button_h = 50
        button_padx = 50
        button_pady = 50

        # create components
        clock = Clock(30, self.h - 70)
        self.settings_container = ui.components.RoundedRectContainer(
            w=settings_w,
            h=settings_h,
            x=2 * w // 3 - settings_pad,
            y=settings_pad,
            radius=settings_pad
        )
        settings_label = ui.components.Label(
            w=settings_w,
            h=35,
            x=0,
            y=settings_pad,
            text='Settings',
            font=font,
        )
        load_network_switch = NTextSwitch(
            w=settings_w - 2 * settings_pad,
            h=45,
            x=0,
            y=settings_pad + settings_h // 10,
            num_states=2,
            texts=['Load Network: Off', 'Load Network: On'],
            font=font_small,
            text_color=color_theme.Primary,
            background_color=color_theme.OnPrimary,
            on_turn=self._onLoadNetworkSwitch,
            cursor_change=True
        )
        self.button_armor = ui.components.TextButton(
            w=button_w,
            h=button_h,
            x=button_padx,
            y=button_pady,
            text='Armor',
            font=font,
            on_press=lambda : self.setPage(self.page_incidies['armor_page24'], redraw=True),
            cursor_change=True
        )
        self.button_video = ui.components.TextButton(
            w=button_w,
            h=button_h,
            x=button_padx,
            y=button_pady+button_h+20,
            text='Video',
            font=font,
            on_press=lambda : self.setPage(self.page_incidies['video_validate_page'], redraw=True),
            cursor_change=True
        )

        # set component styles
        self.setBackgroundColor(color_theme.Surface)
        self.settings_container.setBackgroundColor(color_theme.SurfaceVariant)
        settings_label.setAlignment(
            align_x=ui.constants.ALIGN_CENTER,
            align_y=ui.constants.ALIGN_CENTER
        )
        self.settings_container.alignHorizontalCenter(settings_label)
        self.settings_container.alignHorizontalCenter(load_network_switch)

        # manage component hierarchy
        self.addChild(clock)
        self.addChild(self.settings_container)
        self.addChild(self.button_armor)
        self.addChild(self.button_video)
        self.settings_container.addChild(settings_label)
        self.settings_container.addChild(load_network_switch)

    def _onLoadNetworkSwitch(self, state: int) -> None:
        self.config_manager['load_network'] = bool(state)

    def onHide(self):
        self.button_armor.resetState()
        self.button_video.resetState()