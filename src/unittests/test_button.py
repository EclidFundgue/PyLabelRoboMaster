from ..pygame_gui import Button, RectContainer, UIMain
from ..resources_loader import ImageLoader


class TestButton(UIMain):
    def __init__(self):
        super().__init__((320, 320))

        img_loader = ImageLoader()

        def on_press():
            print('pressed')

        surf = RectContainer(300, 300, 10, 10)
        btn1 = Button(
            32, 32, 20, 20,
            img_loader['button']['add'],
            img_loader['button']['add_pressed'],
            on_press=on_press,
        )
        btn2 = Button(
            32, 32, 60, 20,
            img_loader['button']['add'],
            img_loader['button']['add_pressed'],
            on_press=on_press,
            continue_press=40
        )

        surf.setBackgroundColor((255, 255, 255))
        self.screen.setBackgroundColor((205, 205, 205))

        self.screen.addChild(surf)
        surf.addChild(btn1)
        surf.addChild(btn2)

def test_Button():
    demo = TestButton()
    demo.run()