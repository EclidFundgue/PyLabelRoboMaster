import pygame

from ..components.clock import Clock
from ..components.stacked_page import StackedPage
from ..components.switch import NTextSwitch
from ..pygame_gui import TextButton
from ..resources_loader import ConfigLoader


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
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeLabeling,
            cursor_change=True
        )
        self.addChild(btn_labeling)

        # setting button
        btn_setting = TextButton(
            300, 50, 50, 120,
            text='Setting',
            font=text_font,
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeSetting,
            cursor_change=True
        )
        self.addChild(btn_setting)

        # clock
        clock = Clock(20, 700)
        self.addChild(clock)

        # background
        self.setBackgroundColor((17, 45, 78))

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
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
        self.addChild(btn_back)

        # armor button
        btn_armor = TextButton(
            300, 50, 50, 120,
            text='Armor',
            font=text_font,
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeArmor,
            cursor_change=True
        )
        self.addChild(btn_armor)

        # background
        self.setBackgroundColor((17, 45, 78))

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
            background_color=(219, 226, 239),
            hover_color=(63, 114, 175),
            pressed_color=(249, 247, 247),
            on_press=self._onPageChangeBack,
            cursor_change=True
        )
        self.addChild(btn_back)

        # load network switch
        self.load_network_switch = NTextSwitch(
            300, 50, 500, 50,
            num_states=2,
            texts=['Load Network: Off', 'Load Network: On'],
            background_color=(219, 226, 239),
            on_turn=self._onLoadNetworkSwitch,
            cursor_change=True
        )
        self.addChild(self.load_network_switch)

        # background
        self.setBackgroundColor((17, 45, 78))

    def _onLoadNetworkSwitch(self, state: int) -> None:
        loader = ConfigLoader()
        if state == 1:
            loader['load_network'] = True
        else:
            loader['load_network'] = False

    def _onPageChangeBack(self) -> None:
        self.setPage(self.page_incidies['main_menu'])