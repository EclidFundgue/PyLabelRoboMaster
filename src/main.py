from . import pygame_gui as ui
from .components.stacked_page import StackedPageView
from .global_vars import VarArmorLabels
from .pages.armor import ArmorPage
from .pages.menu import MainMenu
from .resources_loader import ConfigLoader


class Main(ui.Main):
    def __init__(self):
        cfg_loader = ConfigLoader()

        super().__init__(
            size=cfg_loader['resolution'],
            caption='PyLabelRoboMaster',
            icon='resources/icon.png'
        )

        self.var_armor_labels = VarArmorLabels(
            cfg_loader['user_data'],
            cfg_loader['image_folder'],
            cfg_loader['label_folder'],
            cfg_loader['deserted_image_folder']
        )

        rect = (cfg_loader['resolution'][0], cfg_loader['resolution'][1], 0, 0)
        page_incidies = {
            'main_menu': 0,
            'armor_page': 1,
        }
        self.stacked_page_view = StackedPageView(*rect)
        self.stacked_page_view.addPage(MainMenu(*rect, page_incidies))
        self.stacked_page_view.addPage(ArmorPage(*rect, page_incidies))
        self.stacked_page_view.setPage(0)

        self.screen.addChild(self.stacked_page_view)

    def onExit(self) -> None:
        self.stacked_page_view = None
        super().onExit()

def main():
    main = Main()
    main.run()