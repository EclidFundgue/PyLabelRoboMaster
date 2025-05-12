import sys

sys.path.append('.')

import unittest

from src_py.efui import screen, surface


class TestScreen(unittest.TestCase):
    def tearDown(self):
        screen.destroyAllWindows()

    def test_ScreenInit(self):
        # normal
        s = screen.Screen(size=(100, 200), title="my_title1")
        self.assertIsInstance(s, screen.Screen)

        # Invalid argument type.
        with self.assertRaises(TypeError):
            screen.Screen()
        with self.assertRaises(TypeError):
            screen.Screen("123", "my_title12")
        with self.assertRaises(TypeError):
            screen.Screen((100, 200), 1.0)

        # Invalid screen size.
        with self.assertRaises(ValueError):
            screen.Screen((0, 100), "my_title13")
        with self.assertRaises(ValueError):
            screen.Screen((100, 100000), "my_title14")

    def test_ScreenMenbers(self):
        s = screen.Screen(size=(100, 200), title="my_title21")
        self.assertEqual(s.w, 100)
        self.assertEqual(s.h, 200)
        self.assertEqual(s.title, "my_title21")

    def test_ScreenCreateWindow(self):
        s1 = screen.Screen((10, 20), "my_title31")
        s1.createWindow()

        # Raise a warning when create twice.
        with self.assertWarns(RuntimeWarning):
            s1.createWindow()

        s2 = screen.Screen((11, 21), "my_title32")
        s2.createWindow(pos=(10, 10))

    def test_ScreenDestroyWindow(self):
        s1 = screen.Screen((10, 20), "my_title41")

        # Destroy before create.
        with self.assertWarns(RuntimeWarning):
            s1.destroyWindow()

        s1.createWindow()

    def test_ScreenIsCreated(self):
        s = screen.Screen((10, 20), "my_title42")
        self.assertFalse(s.isCreated())
        
        s.createWindow()
        self.assertTrue(s.isCreated())

        s.destroyWindow()
        self.assertFalse(s.isCreated())

    def test_ScreenGetSurface(self):
        s = screen.Screen((10, 20), "my_title43")

        with self.assertWarns(RuntimeWarning):
            self.assertIsNone(s.getSurface())

        s.createWindow()
        surf = s.getSurface()

        self.assertIsInstance(surf, surface.Surface)
        self.assertEqual(surf.w, 10)
        self.assertEqual(surf.h, 20)
        self.assertTrue(surf.is_from_window)

    def test_createWindow(self):
        s = screen.createWindow((10, 20), "my_title51")
        self.assertIsInstance(s, screen.Screen)
        self.assertEqual(s.w, 10)
        self.assertEqual(s.h, 20)
        self.assertEqual(s.title, "my_title51")

        # Raise a warning when create twice.
        with self.assertWarns(RuntimeWarning):
            s.createWindow()

    def test_getAllWindows(self):
        s1 = screen.Screen((10, 20), "my_title61")
        self.assertEqual(len(screen.getAllWindows()), 1,
                         f'current windows: {screen.getAllWindows()}')
        self.assertIn(s1, screen.getAllWindows())

        s2 = screen.Screen((10, 20), "my_title62")
        self.assertEqual(len(screen.getAllWindows()), 2,
                         f'current windows: {screen.getAllWindows()}')
        self.assertIn(s1, screen.getAllWindows())
        self.assertIn(s2, screen.getAllWindows())

        del s1
        self.assertEqual(len(screen.getAllWindows()), 1,
                         f'current windows: {screen.getAllWindows()}')
        self.assertIn(s2, screen.getAllWindows())

        del s2
        self.assertEqual(len(screen.getAllWindows()), 0,
                         f'current windows: {screen.getAllWindows()}')

    def test_getAllWindows2(self):
        # `getAllWindows()` returns a copy of screen object list
        # Change to returned list will not affect origin list
        s = screen.Screen((10, 20), "my_title71")
        ls = screen.getAllWindows()
        ls.append("123")
        self.assertEqual(len(screen.getAllWindows()), 1,
                         f'current windows: {screen.getAllWindows()}')

    def test_getAllWindows3(self):
        # Created window will not be deleted even if there is not ref.
        screen.createWindow((10, 20), "my_title81")
        ls = screen.getAllWindows()
        self.assertEqual(len(ls), 1,
                         f'current windows: {screen.getAllWindows()}')

        ls[0].destroyWindow()
        del ls
        self.assertEqual(len(screen.getAllWindows()), 0,
                         f'current windows: {screen.getAllWindows()}')

    def test_destroyAllWindows(self):
        s1 = screen.createWindow((10, 20), "my_title91")
        s2 = screen.createWindow((20, 30), "my_title92")
        screen.destroyAllWindows()
        self.assertFalse(s1.isCreated())
        self.assertFalse(s2.isCreated())