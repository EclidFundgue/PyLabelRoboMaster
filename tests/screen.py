import unittest

import pygame


class TestCaseWithScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((640, 640))