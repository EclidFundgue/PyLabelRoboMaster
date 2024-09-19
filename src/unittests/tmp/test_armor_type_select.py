from ..components import armor_type_select
from ..pygame_gui import Surface
from ._test import MessagePrint, MyTest


class TestArmorTypeSelect(MyTest):
    def __init__(self):
        super().__init__(280, 720)

        surf = Surface(280, 720, 0, 0)
        box = armor_type_select.ArmorIconsSelect(10, 10)
        printer = MessagePrint()

        self.screen.addChild(surf)
        surf.addChild(box)
        surf.addChild(printer)

        surf.setBackgroundColor((190, 190, 190))
        box.addObserver(printer)

def test_ArmorTypeSelect():
    demo = TestArmorTypeSelect()
    demo.run()