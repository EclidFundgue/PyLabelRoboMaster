import sys

sys.path.append('.')

import unittest

from src_py.efui import widgets
from src_py.efui.surface import Surface


class TestBase(unittest.TestCase):
    def test_Init(self):
        base = widgets.Base()
        self.assertEqual(base.x, 0)
        self.assertEqual(base.y, 0)
        self.assertEqual(base.w, 0)
        self.assertEqual(base.h, 0)
        self.assertEqual(base.layer, 0)
        self.assertFalse(base.active)
        self.assertTrue(base.alive)

        base1 = widgets.Base(10, 20, 30, 40)
        self.assertEqual(base1.x, 10)
        self.assertEqual(base1.y, 20)
        self.assertEqual(base1.w, 30)
        self.assertEqual(base1.h, 40)

    def test_addChild(self):
        base = widgets.Base()
        a = widgets.Base()

        base.addChild(a)

        with self.assertWarns(Warning):
            base.addChild(a)

    def test_removeChild(self):
        base = widgets.Base()
        a = widgets.Base()

        with self.assertWarns(Warning):
            base.removeChild(a)

        base.addChild(a)
        base.removeChild(a)

class TestRoot(unittest.TestCase):
    def test_init(self):
        root = widgets.Root(Surface((10, 10)))
        self.assertIsInstance(root, widgets.Root)

    def test_redraw_parentFalse(self):
        '''
        root {
            c1 {
                c1_1,
                c1_2
            },
            c2
        }
        '''
        class _Temp(widgets.Base):
            def __init__(self, x, y):
                super().__init__(x, y)
                self.redraw_parent = False
                self.drown = False

            def draw(self, surface, x, y):
                self.drown = True

        root = widgets.Root(Surface((10, 10)))
        c1 = _Temp(1, 0)
        c1_1 = _Temp(1, 1)
        c1_2 = _Temp(1, 2)
        c2 = _Temp(2, 0)
        components = [c1, c1_1, c1_2, c2]

        root.addChild(c1)
        root.addChild(c2)
        c1.addChild(c1_1)
        c1.addChild(c1_2)

        # Redraw c2, only draw c2
        c2.redraw()
        root.draw()
        self.assertFalse(c1.drown)
        self.assertFalse(c1_1.drown)
        self.assertFalse(c1_2.drown)
        self.assertTrue(c2.drown)

        for c in components:
            c.drown = False
        # Redraw c1_1, only draw c1_1
        c1_1.redraw()
        root.draw()
        self.assertFalse(c1.drown)
        self.assertTrue(c1_1.drown)
        self.assertFalse(c1_2.drown)
        self.assertFalse(c2.drown)

        for c in components:
            c.drown = False
        # Redraw c1, draw c1, c1_1, c1_2
        c1.redraw()
        root.draw()
        self.assertTrue(c1.drown)
        self.assertTrue(c1_1.drown)
        self.assertTrue(c1_2.drown)
        self.assertFalse(c2.drown)

    def test_redraw_parentTrue(self):
        '''
        root {
            c1 {
                c1_1
            },
            c2
        }
        '''
        class _Temp(widgets.Base):
            def __init__(self, x, y):
                super().__init__(x, y)
                self.redraw_parent = True
                self.drown = False

            def draw(self, surface, x, y):
                self.drown = True

        root = widgets.Root(Surface((10, 10)))
        c1 = _Temp(1, 0)
        c1_1 = _Temp(1, 1)
        c2 = _Temp(2, 0)
        components = [c1, c1_1, c2]

        root.addChild(c1)
        root.addChild(c2)
        c1.addChild(c1_1)

        # Redraw any chils will draw all components
        for c in components:
            for _c in components:
                _c.drown = False

            c.redraw()
            root.draw()
            self.assertTrue(c1.drown, msg=f'{c}')
            self.assertTrue(c1_1.drown, msg=f'{c}')
            self.assertTrue(c2.drown, msg=f'{c}')

    def test_redraw_parentBoth(self):
        '''
        root {
            c1(False) {
                c1_1(True)
                c1_2(False)
            },
            c2(False)
        }
        '''
        class _Temp(widgets.Base):
            def __init__(self, x, y):
                super().__init__(x, y)
                self.redraw_parent = False
                self.drown = False

            def draw(self, surface, x, y):
                self.drown = True

        root = widgets.Root(Surface((10, 10)))
        c1 = _Temp(1, 0)
        c1_1 = _Temp(1, 1)
        c1_2 = _Temp(1, 2)
        c2 = _Temp(2, 0)
        components = [c1, c1_1, c1_2, c2]

        root.addChild(c1)
        root.addChild(c2)
        c1.addChild(c1_1)
        c1.addChild(c1_2)
        c1_1.redraw_parent = True

        # Redraw c1_1, draw c1, c1_1, c1_2
        c1_1.redraw()
        root.draw()
        self.assertTrue(c1.drown)
        self.assertTrue(c1_1.drown)
        self.assertTrue(c1_2.drown)
        self.assertFalse(c2.drown)

        for c in components:
            c.drown = False
        # Redraw c1_2, only draw c1_2
        c1_2.redraw()
        root.draw()
        self.assertFalse(c1.drown)
        self.assertFalse(c1_1.drown)
        self.assertTrue(c1_2.drown)
        self.assertFalse(c2.drown)