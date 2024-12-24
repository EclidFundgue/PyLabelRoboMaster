import unittest

import pygame

from src.pygame_gui import utils


class TestUtils(unittest.TestCase):
    def test_clipRect(self):
        surface = pygame.Surface((10, 10))

        cases = [
            ((5, 5, 1, 1), (5, 5, 1, 1)),
            ((5, 5, -2, 1), (3, 5, 0, 1)),
            ((13, 5, 1, 1), (9, 5, 1, 1)),
            ((3, 3, -7, -10), (0, 0, 0, 0)),
            ((20, 20, -7, -10), (10, 10, 0, 0)),
        ]

        for before, after in cases:
            ret = utils.clipRect(before, surface)
            self.assertEqual(
                ret, after,
                msg=f'{before} should be cliped to {after} on surface {surface}, not {ret}.'
            )

    def test_getCallable(self):
        called = False
        def f():
            nonlocal called
            called = True
        g = utils.getCallable(f)
        g()
        self.assertTrue(called)

        self.assertTrue(callable(utils.getCallable(None)))

        with self.assertRaises(TypeError):
            utils.getCallable('abc')

    def test_loadImage(self):
        image = pygame.Surface((16, 20))

        # No specific size or same size will return origon object.
        res = utils.loadImage(image)
        self.assertIs(res, image)
        res = utils.loadImage(image, 16, 20)
        self.assertIs(res, image)

        # Different size will scale.
        res = utils.loadImage(image, 8, 10)
        self.assertIsNot(res, image)
        self.assertEqual(res.get_size(), (8, 10))

        with self.assertRaises(TypeError):
            utils.loadImage(69)
        with self.assertRaises(FileExistsError):
            utils.loadImage('I bet this is illigal path\/:*?<>"|')

    def test_singleton(self):
        @utils.singleton
        class A:
            pass

        @utils.singleton
        class B:
            pass

        a1 = A()
        a2 = A()
        self.assertIs(a1, a2)

        b = B()
        self.assertIsNot(a1, b)