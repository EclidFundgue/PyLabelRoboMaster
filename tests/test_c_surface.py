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

    def test_loadImage(self):
        with self.assertRaises(ValueError):
            surface.loadImage("not extists dir .png")

        surf = surface.loadImage("resources/test_dataset/images/00.jpg")
        self.assertEqual(surf.w, 1280)
        self.assertEqual(surf.h, 1024)
        self.assertFalse(surf.is_from_window)