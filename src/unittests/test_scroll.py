import os

import pygame

from ..components.scroll import bar, line, lines, scrollview, stackedview
from ..pygame_gui import UIMain
from ..utils.constants import ROOT_PATH


class TestScroll_FileLine(UIMain):
    def __init__(self):
        super().__init__((640, 640))

        def on_delete():
            print("deleted")
        l = line.ImageFileLine(200, 50, "test.jpg", on_delete=on_delete)
        def on_select():
            if l.selected:
                l.unselect()
            else:
                l.select()
        l.on_select = on_select
        l.x = 30
        l.y = 30

        self.screen.addChild(l)

def test_Scroll_FileLine():
    demo = TestScroll_FileLine()
    demo.run()

class TestScroll_Bar(UIMain):
    def __init__(self):
        super().__init__((640, 640))

        def on_drag(r: float):
            print(r)
        b = bar.ScrollBar(20, 500, 100, 100, on_drag=on_drag)

        def on_scroll_up():
            b.setRelative(b.getRelative() - 0.05)
        def on_scroll_down():
            b.setRelative(b.getRelative() + 0.05)
        self.screen.addKeyPressEvent(pygame.K_w, on_scroll_up)
        self.screen.addKeyPressEvent(pygame.K_s, on_scroll_down)

        self.screen.addChild(b)

def test_Scroll_Bar():
    demo = TestScroll_Bar()
    demo.run()

class TestScroll_Lines(UIMain):
    def __init__(self):
        super().__init__((640, 640))

        lns = [line.ImageFileLine(400, 50, name) for name in [
            "test1.jpg", "test2.jpg", "test3.jpg", "test4.jpg", "test5.jpg",
            "test6.jpg", "test7.jpg", "test8.jpg", "test9.jpg", "test10.jpg",
            "test11.jpg", "test12.jpg", "test13.jpg", "test14.jpg", "test15.jpg",
        ]]

        def on_relative_changed(r: float):
            print(r)
        lns_box = lines.LinesBox(400, 500, 100, 100, lns, on_relative_changed=on_relative_changed)

        for ln in lns:
            def get_on_select(_line):
                return lambda: lns_box.select(_line)
            def get_on_delete(_line):
                return lambda: lns_box.delete(_line)
            ln.on_select = get_on_select(ln)
            ln.on_delete = get_on_delete(ln)

        lns_box.setBackgroundColor((128, 128, 128))

        self.screen.addChild(lns_box)

def test_Scroll_Lines():
    demo = TestScroll_Lines()
    demo.run()


class TestScroll_ScrollView(UIMain):
    def __init__(self):
        super().__init__((1280, 640))

        def on_select1(idx, _line: line._GenericFileLine):
            print("selected1", idx, _line.filename)
        def on_select2(idx, _line: line._GenericFileLine):
            print("selected2", idx, _line.filename)
        def on_desert(idx, _line: line.ImageFileLine):
            print("command1", idx, _line.filename)
        def on_restore(idx, _line: line.DesertedFileLine):
            print("command2", idx, _line.filename)

        self.view1 = scrollview.ImageScrollView(
            400, 500, 100, 10, 350, 50,
            os.path.join(ROOT_PATH, "resources/test_dataset/images"),
            on_select=on_select1,
            on_desert=on_desert
        )
        self.view2 = scrollview.DesertedScrollView(
            400, 500, 600, 10, 350, 50,
            os.path.join(ROOT_PATH, "resources/test_dataset/images"),
            on_select=on_select2,
            on_restore=on_restore
        )

        self.screen.addChild(self.view1)
        self.screen.addChild(self.view2)

def test_Scroll_ScrollView():
    demo = TestScroll_ScrollView()
    demo.run()

class TestScroll_StackedView(UIMain):
    def __init__(self):
        super().__init__((1280, 640))

        def on_page_changed(idx: int):
            print("page changed", idx)
        def on_select(idx, line: line._GenericFileLine):
            print("selected", idx, line.filename)

        def on_desert(idx, _line: line.ImageFileLine):
            print("desert", idx, _line.filename)
            self.view.addLine(1, line.DesertedFileLine(
                _line.w, _line.h, _line.filename
            ))
        def on_restore(idx, _line: line.DesertedFileLine):
            print("restore", idx, _line.filename)
            self.view.addLine(0, line.ImageFileLine(
                _line.w, _line.h, _line.filename
            ))

        self.view = stackedview.StackedScrollView(
            400, 500, 50, 50, 370, 50,
            os.path.join(ROOT_PATH, "resources/test_dataset/images"),
            os.path.join(ROOT_PATH, "resources/test_dataset/images"),
            on_page_changed,
            on_select,
            on_desert,
            on_restore
        )

        self.screen.addChild(self.view)

def test_Scroll_StackedView():
    demo = TestScroll_StackedView()
    demo.run()