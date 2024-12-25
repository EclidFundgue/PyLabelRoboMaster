import unittest

from src.utils.geometry import in_polygon


class TestGeometryFunctions(unittest.TestCase):
    def test_point_inside_polygon(self):
        polygon = [(0, 0), (5, 0), (5, 5), (0, 5)]
        point_inside = (3, 3)
        self.assertTrue(in_polygon(polygon, point_inside), "Point inside polygon should return True")

    def test_point_outside_polygon(self):
        polygon = [(0, 0), (5, 0), (5, 5), (0, 5)]
        point_outside = (6, 3)
        self.assertFalse(in_polygon(polygon, point_outside), "Point outside polygon should return False")

    def test_point_on_polygon_edge(self):
        polygon = [(0, 0), (5, 0), (5, 5), (0, 5)]
        point_on_edge = (5, 3)
        self.assertIsNone(in_polygon(polygon, point_on_edge), "Point on edge should return None")

    def test_empty_polygon(self):
        polygon = []
        point = (1, 1)
        self.assertFalse(in_polygon(polygon, point), "Empty polygon should always return False")

    def test_polygon_with_one_point(self):
        polygon = [(1, 1)]
        point_inside = (1, 1)
        point_outside = (2, 2)
        self.assertIsNone(in_polygon(polygon, point_inside), "Single-point polygon should return None for any point")
        self.assertIsNone(in_polygon(polygon, point_outside), "Single-point polygon should return None for any point")

    def test_polygon_with_two_points(self):
        polygon = [(0, 0), (2, 0)]
        point_on_edge = (1, 0)
        point_inside = (1, -1)
        point_outside = (1, 1)
        self.assertIsNone(in_polygon(polygon, point_on_edge), "Two-point polygon should return None for points on the line")
        self.assertIsNone(in_polygon(polygon, point_inside), "Two-point polygon should return None for points not on the line")
        self.assertIsNone(in_polygon(polygon, point_outside), "Two-point polygon should return None for points not on the line")
