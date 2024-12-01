import os
import sys
import unittest
from unittest.mock import MagicMock

import pygame

print(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.pygame_gui.components.base import *
from src.pygame_gui.components.root import *


class TestRoot(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()
        
    def test_init(self):
        root = Root()
        self.assertIsInstance(root, Root)

class TestBase(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()
    def test_init(self):
        base = Base(0,0,0,0)
        self.assertIsInstance(base, Base)
    

if __name__ == "__main__":
    unittest.main()
