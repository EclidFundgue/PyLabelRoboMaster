import sys

sys.path.append('.')

import unittest

from src_py.efui import surface


class TestSurface(unittest.TestCase):
    def test_SurfaceInit(self):
        surf = surface.Surface((128, 256))
        self.assertIsInstance(surf, surface.Surface)

        with self.assertRaises(TypeError):
            surface.Surface()
        with self.assertRaises(TypeError):
            surface.Surface(None)
        with self.assertRaises(TypeError):
            surface.Surface(("abc", 1))

    def test_SurfaceMenbers(self):
        surf = surface.Surface((128, 256))
        self.assertEqual(surf.w, 128)
        self.assertEqual(surf.h, 256)
        self.assertFalse(surf.is_from_window)

    def test_Subscript(self):
        s = surface.Surface((100, 50))

        with self.assertRaises(TypeError): # invalid value
            s["abc"]
        with self.assertRaises(TypeError): # invalid step
            s[10:20:-1, 10:20]
        with self.assertRaises(ValueError): # invalid range
            s[:-51, 10:20]
        with self.assertRaises(ValueError): # out of range
            s[:, 0:101]
        with self.assertRaises(ValueError): # invalid range
            s[:, 20:10]

        x = s[:, :]
        self.assertEqual(x.w, s.w)
        self.assertEqual(x.h, s.h)

        y = s[20:35, :]
        self.assertEqual(y.h, 15)

    def test_loadImage(self):
        with self.assertRaises(ValueError):
            surface.loadImage("not extists dir .png")

        surf = surface.loadImage("resources/test_dataset/images/00.jpg")
        self.assertEqual(surf.w, 1280)
        self.assertEqual(surf.h, 1024)
        self.assertFalse(surf.is_from_window)