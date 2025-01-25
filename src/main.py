from . import pygame_gui as ui
from .components.stacked_page import StackedPageView
from .menu import MainMenu
from .tasks.armor24 import ArmorPage24
from .tasks.armor25 import ArmorPage25


class Main(ui.Main):
    def __init__(self):
        super().__init__((1280, 800), caption='PyLabelRoboMaster')

        page_incidies = {
            'main_menu': 0,
            'armor_page24': 1,
            'armor_page25': 2,
        }
        rect = (1280, 800, 0, 0)
        self.stacked_page_view = StackedPageView(*rect)
        self.stacked_page_view.addPage(MainMenu(*rect, page_incidies))
        self.stacked_page_view.addPage(ArmorPage24(*rect, page_incidies))
        self.stacked_page_view.addPage(ArmorPage25(*rect, page_incidies))
        self.stacked_page_view.setPage(0)

        self.root.addChild(self.stacked_page_view)