import unittest

from src.pygame_gui.components.base import Base
from src.pygame_gui.components.root import Root
from tests.screen import TestCaseWithScreen


class TestBase(unittest.TestCase):
    def test_init(self):
        base = Base(0,0,0,0)
        self.assertIsInstance(base, Base)

class TestRoot(TestCaseWithScreen):
    def test_init(self):
        root = Root()
        self.assertIsInstance(root, Root)
