import pygame

from .. import pygame_gui as ui
from ..components.clock import Clock
from ..components.stacked_page import StackedPage
from ..components.switch import NTextSwitch
from ..resources_loader import ConfigLoader


class MainMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies = page_incidies

        color_theme = ui.color.LightColorTheme()
        font = pygame.font.SysFont('microsoftyaheibold', 40)
        font_small = pygame.font.SysFont('microsoftyaheibold', 30)

        # settings
        container_w = w // 3
        container_h = h - 40
        padding = 20
        self.settings_container = ui.components.RoundedRectContainer(
            container_w, container_h, 2 * w // 3 - padding, padding,
            radius=padding
        )
        settings_label = ui.components.Label(
            container_w, 35, 0, padding,
            text='Settings',
            font=font,
        )
        load_network_switch = NTextSwitch(
            container_w - 2 * padding, 45, 0, padding + container_h // 10,
            num_states=2,
            texts=['Load Network: Off', 'Load Network: On'],
            font=font_small,
            text_color=color_theme.Primary,
            background_color=color_theme.OnPrimary,
            on_turn=self._onLoadNetworkSwitch,
            cursor_change=True
        )

        self.settings_container.setBackgroundColor(color_theme.SurfaceVariant)
        settings_label.setAlignment(
            align_x=ui.constants.ALIGN_CENTER,
            align_y=ui.constants.ALIGN_CENTER
        )
        self.settings_container.alignHorizontalCenter(settings_label)
        self.settings_container.alignHorizontalCenter(load_network_switch)

        self.settings_container.addChild(settings_label)
        self.settings_container.addChild(load_network_switch)
        self.addChild(self.settings_container)

        # labeling button
        paddingx = 50
        paddingy = 40
        btn_armor = ui.components.TextButton(
            300, 50, paddingx, paddingy,
            text='Armor',
            on_press=self._onPageChangeArmor,
            cursor_change=True
        )
        btn_armor.setFont(font)
        self.addChild(btn_armor)

        btn_buff = ui.components.TextButton(
            300, 50, paddingx, paddingy + 70,
            text='Buff',
            cursor_change=True
        )
        btn_buff.setFont(font)
        self.addChild(btn_buff)

        # clock
        clock = Clock(20, 700)
        self.addChild(clock)

        # backgrounds
        self.setBackgroundColor(color_theme.Surface)

    def _onPageChangeLabeling(self) -> None:
        self.setPage(self.page_incidies['labeling_menu'])

    def _onPageChangeSetting(self) -> None:
        self.setPage(self.page_incidies['setting_menu'])

    def _onLoadNetworkSwitch(self, state: int) -> None:
        loader = ConfigLoader()
        if state == 1:
            loader['load_network'] = True
        else:
            loader['load_network'] = False

    def _onLabelTypeSwitch(self, state: int) -> None:
        loader = ConfigLoader()
        if state == 0:
            loader['mode'] = 'armor'
        elif state == 1:
            loader['mode'] = 'buff'

    def _onPageChangeArmor(self) -> None:
        self.setPage(self.page_incidies['armor_page'])

    def onHide(self):
        for ch in self.child_components:
            if isinstance(ch, ui.components.TextButton):
                ch.pressed = False