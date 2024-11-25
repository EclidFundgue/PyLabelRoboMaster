import pygame

from .. import pygame_gui as ui
from ..components.clock import Clock
from ..components.stacked_page import StackedPage
from ..components.switch import NTextSwitch
from ..resources_loader import ConfigLoader

_TEXT_SWITCH_COLOR = (249, 247, 247)

class MainMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 32)

        # labeling button
        btn_labeling = ui.components.TextButton(
            300, 50, 50, 50,
            text='Label',
            on_press=self._onPageChangeLabeling,
            cursor_change=True
        )
        btn_labeling.setFont(text_font)
        self.addChild(btn_labeling)

        # setting button
        btn_setting = ui.components.TextButton(
            300, 50, 50, 120,
            text='Setting',
            on_press=self._onPageChangeSetting,
            cursor_change=True
        )
        btn_setting.setFont(text_font)
        self.addChild(btn_setting)

        # clock
        clock = Clock(20, 700)
        self.addChild(clock)

        # background
        color_theme = ui.color.LightColorTheme()
        self.setBackgroundColor(color_theme.Surface)

    def _onPageChangeLabeling(self) -> None:
        self.setPage(self.page_incidies['labeling_menu'])

    def _onPageChangeSetting(self) -> None:
        self.setPage(self.page_incidies['setting_menu'])

    def onHide(self):
        for ch in self.child_components:
            if isinstance(ch, ui.components.TextButton):
                ch.pressed = False

class LabelingMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 30)

        # back button
        btn_back = ui.components.TextButton(
            300, 50, 50, 50,
            text='Back',
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
        btn_back.setFont(text_font)
        self.addChild(btn_back)

        # armor button
        btn_armor = ui.components.TextButton(
            300, 50, 50, 120,
            text='Armor',
            on_press=self._onPageChangeArmor,
            cursor_change=True
        )
        btn_armor.setFont(text_font)
        self.addChild(btn_armor)

        # background
        color_theme = ui.color.LightColorTheme()
        self.setBackgroundColor(color_theme.Surface)

    def _onPageChangeBack(self) -> None:
        self.setPage(self.page_incidies['main_menu'])

    def _onPageChangeArmor(self) -> None:
        self.setPage(self.page_incidies['armor_page'])

    def onHide(self):
        for ch in self.child_components:
            if isinstance(ch, ui.components.TextButton):
                ch.pressed = False

class SettingMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)
        
        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 30)

        # back button
        btn_back = ui.components.TextButton(
            300, 50, 50, 50,
            text='Back',
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
        btn_back.setFont(text_font)
        self.addChild(btn_back)

        # load network switch
        self.load_network_switch = NTextSwitch(
            300, 50, 500, 50,
            num_states=2,
            texts=['Load Network: Off', 'Load Network: On'],
            background_color=_TEXT_SWITCH_COLOR,
            on_turn=self._onLoadNetworkSwitch,
            cursor_change=True
        )
        self.addChild(self.load_network_switch)

        # background
        color_theme = ui.color.LightColorTheme()
        self.setBackgroundColor(color_theme.Surface)

    def _onLoadNetworkSwitch(self, state: int) -> None:
        loader = ConfigLoader()
        if state == 1:
            loader['load_network'] = True
        else:
            loader['load_network'] = False

    def _onPageChangeBack(self) -> None:
        self.setPage(self.page_incidies['main_menu'])

    def onHide(self):
        for ch in self.child_components:
            if isinstance(ch, ui.components.TextButton):
                ch.pressed = False