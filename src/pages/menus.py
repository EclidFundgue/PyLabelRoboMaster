import pygame

from ..components.clock import Clock
from ..components.stacked_page import StackedPage
from ..components.switch import NTextSwitch
from ..pygame_gui import TextButton
from ..resources_loader import ConfigLoader


_TEXT_BUTTON_COLOR = (249, 247, 247)
_TEXT_BUTTON_HOVER_COLOR = (63, 114, 175)
_TEXT_BUTTON_PRESSED_COLOR = (219, 226, 239)
_TEXT_SWITCH_COLOR = _TEXT_BUTTON_COLOR

class MainMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 30)

        # labeling button
        btn_labeling = TextButton(
            300, 50, 50, 50,
            text='Label',
            font=text_font,
            background_color=_TEXT_BUTTON_COLOR,
            hover_color=_TEXT_BUTTON_HOVER_COLOR,
            pressed_color=_TEXT_BUTTON_PRESSED_COLOR,
            on_press=self._onPageChangeLabeling,
            cursor_change=True
        )
        self.addChild(btn_labeling)

        # setting button
        btn_setting = TextButton(
            300, 50, 50, 120,
            text='Setting',
            font=text_font,
            background_color=_TEXT_BUTTON_COLOR,
            hover_color=_TEXT_BUTTON_HOVER_COLOR,
            pressed_color=_TEXT_BUTTON_PRESSED_COLOR,
            on_press=self._onPageChangeSetting,
            cursor_change=True
        )
        self.addChild(btn_setting)

        # clock
        clock = Clock(20, 700)
        self.addChild(clock)

        # background
        self.setBackgroundColor((219, 226, 239))

    def _onPageChangeLabeling(self) -> None:
        self.setPage(self.page_incidies['labeling_menu'])

    def _onPageChangeSetting(self) -> None:
        self.setPage(self.page_incidies['setting_menu'])

class LabelingMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)

        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 30)

        # back button
        btn_back = TextButton(
            300, 50, 50, 50,
            text='Back',
            font=text_font,
            background_color=_TEXT_BUTTON_COLOR,
            hover_color=_TEXT_BUTTON_HOVER_COLOR,
            pressed_color=_TEXT_BUTTON_PRESSED_COLOR,
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
        self.addChild(btn_back)

        # armor button
        btn_armor = TextButton(
            300, 50, 50, 120,
            text='Armor',
            font=text_font,
            background_color=_TEXT_BUTTON_COLOR,
            hover_color=_TEXT_BUTTON_HOVER_COLOR,
            pressed_color=_TEXT_BUTTON_PRESSED_COLOR,
            on_press=self._onPageChangeArmor,
            cursor_change=True
        )
        self.addChild(btn_armor)

        # background
        self.setBackgroundColor((219, 226, 239))

    def _onPageChangeBack(self) -> None:
        self.setPage(self.page_incidies['main_menu'])

    def _onPageChangeArmor(self) -> None:
        self.setPage(self.page_incidies['armor_page'])

class SettingMenu(StackedPage):
    def __init__(self, w: int, h: int, x: int, y: int, page_incidies: dict):
        super().__init__(w, h, x, y)
        
        self.page_incidies = page_incidies

        text_font = pygame.font.SysFont('simsun', 30)

        # back button
        btn_back = TextButton(
            300, 50, 50, 50,
            text='Back',
            font=text_font,
            background_color=_TEXT_BUTTON_COLOR,
            hover_color=_TEXT_BUTTON_HOVER_COLOR,
            pressed_color=_TEXT_BUTTON_PRESSED_COLOR,
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
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
        self.setBackgroundColor((219, 226, 239))

    def _onLoadNetworkSwitch(self, state: int) -> None:
        loader = ConfigLoader()
        if state == 1:
            loader['load_network'] = True
        else:
            loader['load_network'] = False

    def _onPageChangeBack(self) -> None:
        self.setPage(self.page_incidies['main_menu'])