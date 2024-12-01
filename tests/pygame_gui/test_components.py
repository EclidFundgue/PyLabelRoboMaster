import unittest

import pygame

from src.pygame_gui.components.base import Base
from src.pygame_gui.components.root import Root


class TestBase(unittest.TestCase):
    def test_init(self):
        base = Base(0,0,0,0)
        self.assertIsInstance(base, Base)
        
class TestRoot(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()
        
    def test_init(self):
        root = Root()
        self.assertIsInstance(root, Root)
