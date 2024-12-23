import unittest

from src.pygame_gui import color


class TestColorFunctions(unittest.TestCase):
    def test_dark(self):
        gray = (128, 128, 128)
        dark_gray1 = color.dark(gray, 1)
        dark_gray3 = color.dark(gray, 3)
        for i in range(3):
            self.assertLess(dark_gray1[i], gray[i])
            self.assertLess(dark_gray3[i], dark_gray1[i])

        # Black can not be darker.
        black = (0, 0, 0)
        self.assertEqual(black, color.dark(black, 1))

    def test_light(self):
        gray = (128, 128, 128)
        light_gray1 = color.light(gray, 1)
        light_gray3 = color.light(gray, 3)
        for i in range(3):
            self.assertGreater(light_gray1[i], gray[i])
            self.assertGreater(light_gray3[i], light_gray1[i])

        # White can not be lighter.
        white = (255, 255, 255)
        self.assertEqual(white, color.light(white, 1))