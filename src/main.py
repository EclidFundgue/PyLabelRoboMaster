from .global_vars import VarArmorLabels
from .pages.armor import ArmorPage
from .pages.menus import MainMenu
from .pygame_gui import UIMain
from .resources_loader import ConfigLoader


class Main(UIMain):
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

        self.pages = [
            MainMenu(
                *cfg_loader['resolution'], 0, 0,
                on_change_labeling=lambda: self.setPageByIndex(1)
            ),
            ArmorPage(
                *cfg_loader['resolution'], 0, 0,
                on_back=lambda: self.setPageByIndex(0)
            )
        ]

        self.current_page_index = 0

        self.screen.addChild(self.pages[self.current_page_index])

    def setPageByIndex(self, idx: int) -> None:
        self.screen.removeChild(self.pages[self.current_page_index])
        self.current_page_index = idx
        self.screen.addChild(self.pages[self.current_page_index])

    def onExit(self) -> None:
        self.screen.removeChild(self.pages[self.current_page_index])

        for page in self.pages:
            page.kill()
        self.pages = None

        super().onExit()

def main():
    main = Main()
    main.run()