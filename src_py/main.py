from . import efui as ui


class Main(ui.main.Main):
    def __init__(self):
        super().__init__((1080, 720), "PyLabelRoboMaster")

        s = self.screen.getSurface()
        s.fill((255, 200, 220))

        a = ui.surface.Surface((100, 100))
        a.fill((100, 100, 100))
        s.blit(a, (60, 30))

        print(self.screen)
        print(self.root)
        print(self.root.surface)