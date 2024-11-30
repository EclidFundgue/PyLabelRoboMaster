import unittest
from unittest.mock import MagicMock
import pygame

import sys
import os

print(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.pygame_gui.components.root import Root

class TestRoot(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()

    def test_root_initialization(self):
        root = Root()
        self.assertEqual(root.screen, self.screen)
        self.assertIsInstance(root.redraw_tree, _RedrawNode)
        self.assertFalse(root.redraw_tree.needs_redraw)

    def test_redraw_method(self):
        root = Root()
        with self.assertLogs(logger, level='WARNING') as log:
            root.redraw()
        self.assertIn("Root can not be redrawn directly.", log.output[0])

if __name__ == "__main__":
    unittest.main()
