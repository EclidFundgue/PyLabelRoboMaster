from . import efui as ui


class Main(ui.main.Main):
    def __init__(self):
        super().__init__((1080, 720), "PyLabelRoboMaster")