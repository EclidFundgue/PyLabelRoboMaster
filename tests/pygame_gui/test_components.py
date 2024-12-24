import unittest

from src.pygame_gui.components.base import Base
from src.pygame_gui.components.root import Root
from tests.screen import TestCaseWithScreen


class TestBase(unittest.TestCase):
    def test_init(self):
        base = Base(0,0,0,0)
        self.assertIsInstance(base, Base)

    def test_addChild(self):
        parent = Base(0, 0, 0, 0)
        child = Base(0, 0, 0, 0)
        self.assertEqual(child._parent, None)

        parent.addChild(child)
        self.assertEqual(child._parent, parent)
        self.assertIn(child, parent._children)

    def test_removeChild(self):
        parent = Base(0, 0, 0, 0)
        child = Base(0, 0, 0, 0)
        parent.addChild(child)

        parent.removeChild(child)
        self.assertEqual(child._parent, None)
        self.assertNotIn(child, parent._children)

    def test_setChildren(self):
        parent = Base(0, 0, 0, 0)
        c1 = Base(0, 0, 0, 0)
        c2 = Base(0, 0, 0, 0)
        c3 = Base(0, 0, 0, 0)

        parent.addChild(c1)
        parent.addChild(c2)
        parent.setChildren([c2, c3])

        # Now c1 is not child, (c2, c3) are children.
        self.assertEqual(c1._parent, None)
        self.assertEqual(c2._parent, parent)
        self.assertEqual(c3._parent, parent)

        self.assertNotIn(c1, parent._children)
        self.assertIn(c2, parent._children)
        self.assertIn(c3, parent._children)

    def test_kill_alive(self):
        component = Base(0, 0, 0, 0)
        self.assertTrue(component.alive)
        component.kill()
        self.assertFalse(component.alive)

    def test_kill_child(self):
        parent = Base(0, 0, 0, 0)
        child = Base(0, 0, 0, 0)
        parent.addChild(child)

        child.kill()
        self.assertIsNone(child._parent)
        self.assertNotIn(child, parent._children)

    def test_kill_parent(self):
        parent = Base(0, 0, 0, 0)
        child = Base(0, 0, 0, 0)
        parent.addChild(child)

        parent.kill()
        self.assertFalse(child.alive)
        self.assertIsNone(child._parent)

class TestRoot(TestCaseWithScreen):
    def test_init(self):
        root = Root()
        self.assertIsInstance(root, Root)

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
        class _TestChild(Base):
            def __init__(self, w, h, x, y):
                super().__init__(w, h, x, y)
                self.redraw_parent = False
                self.drown = False

            def draw(self, surface, x_start, y_start):
                self.drown = True

        root = Root()
        c1 = _TestChild(100, 100, 0, 0)
        c1_1 = _TestChild(50, 50, 0, 0)
        c1_2 = _TestChild(50, 50, 50, 0)
        c2 = _TestChild(100, 100, 50, 0)
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
        class _TestChild(Base):
            def __init__(self, w, h, x, y):
                super().__init__(w, h, x, y)
                self.redraw_parent = True
                self.drown = False

            def draw(self, surface, x_start, y_start):
                self.drown = True

        root = Root()
        c1 = _TestChild(100, 100, 0, 0)
        c1_1 = _TestChild(50, 50, 0, 0)
        c2 = _TestChild(100, 100, 50, 0)
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

    def test_redraw_parentAll(self):
        '''
        root {
            c1(False) {
                c1_1(True)
                c1_2(False)
            },
            c2(False)
        }
        '''
        class _TestChild(Base):
            def __init__(self, w, h, x, y):
                super().__init__(w, h, x, y)
                self.redraw_parent = False
                self.drown = False

            def draw(self, surface, x_start, y_start):
                self.drown = True

        root = Root()
        c1 = _TestChild(100, 100, 0, 0)
        c1_1 = _TestChild(50, 50, 0, 0)
        c1_2 = _TestChild(50, 50, 50, 0)
        c2 = _TestChild(100, 100, 50, 0)
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

    def test_update(self):
        root = Root()

        class _TestChild(Base):
            def __init__(self, w, h, x, y):
                super().__init__(w, h, x, y)
                self.updated = False

            def update(self, x, y, wheel):
                self.updated = True

        c1 = _TestChild(100, 100, 0, 0)
        c1_1 = _TestChild(80, 50, 10, 10)

        root.addChild(c1)
        c1.addChild(c1_1)

        events = []
        root.update(events)
        self.assertTrue(c1.updated)
        self.assertTrue(c1_1.updated)