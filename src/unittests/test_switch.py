from pygame import locals

from ..components import switch
from ..global_vars import VarArmorAutoLabeling
from ..pygame_gui import Surface, UIMain
from ..resources_loader import ImageLoader


class TestSwitch(UIMain):
    def __init__(self):
        super().__init__((640, 640))

        img_loader = ImageLoader()

        var1 = VarArmorAutoLabeling()
        swch1 = switch.Switch(64, 64, 10, 10,
            img_loader['button']['add'],
            img_loader['button']['add_pressed'],
            on_turn=var1.switch
        )
        trig1 = switch.ThemeBasedSwitchTrigger(var1, swch1)
        surf = Surface(640, 640, 0, 0)

        surf.setBackgroundColor((205, 205, 205))

        surf.addChild(var1)
        surf.addChild(swch1)
        surf.addChild(trig1)
        self.screen.addChild(surf)

        self.screen.addKeydownEvent(locals.K_SPACE, var1.switch, 'var1')

def test_Switch():
    demo = TestSwitch()
    demo.run()