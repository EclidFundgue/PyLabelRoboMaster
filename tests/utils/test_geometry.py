import unittest

from src.utils.geometry import __zero, __positive, __len, __sub, __dot, __constrain, __get_radian, in_polygon

class TestGeometryFunctions(unittest.TestCase):

    def test__zero(self):
        self.assertTrue(__zero(1e-7), "Expected True for very small values")
        self.assertTrue(__zero(-1e-7), "Expected True for very small negative values")
        self.assertFalse(__zero(1e-5), "Expected False for larger values")
        self.assertFalse(__zero(-1e-5), "Expected False for larger negative values")

    def test__positive(self):
        self.assertTrue(__positive(1e-5), "Expected True for positive values")
        self.assertFalse(__positive(-1e-5), "Expected False for negative values")
        self.assertFalse(__positive(0), "Expected False for zero")

    def test__len(self):
        self.assertAlmostEqual(__len((3, 4)), 5.0, places=6, msg="Length of (3,4) should be 5.0")
        self.assertAlmostEqual(__len((0, 0)), 0.0, places=6, msg="Length of (0,0) should be 0.0")

    def test__sub(self):
        self.assertEqual(__sub((3, 4), (1, 2)), (2, 2), "Subtraction of vectors failed")
        self.assertEqual(__sub((-1, -2), (-3, -4)), (2, 2), "Subtraction of vectors failed")

    def test__dot(self):
        self.assertEqual(__dot((1, 2), (3, 4)), 11, "Dot product calculation failed")
        self.assertEqual(__dot((-1, -2), (3, 4)), -11, "Dot product calculation failed")

    def test__constrain(self):
        self.assertEqual(__constrain(5, 1, 10), 5, "Constrain function did not return expected value")
        self.assertEqual(__constrain(-1, 1, 10), 1, "Constrain function did not return expected value")
        self.assertEqual(__constrain(15, 1, 10), 10, "Constrain function did not return expected value")

    def test__get_radian(self):
        # Straight line, should be 0 or None
        self.assertEqual(__get_radian((0, 0), (1, 0), (2, 0)), 0, "Angle on a straight line should be 0")
        self.assertIsNone(__get_radian((0, 0), (0, 0), (1, 0)), "Angle with overlapping points should be None")

        # Right angle
        self.assertAlmostEqual(__get_radian((0, 0), (0, 0), (0, 1)), 1.5708, places=4, msg="Right angle should be PI/2")
        self.assertAlmostEqual(__get_radian((1, 0), (0, 0), (0, 1)), 1.5708, places=4, msg="Right angle should be PI/2")

        # Acute and obtuse angles
        self.assertAlmostEqual(__get_radian((1, 0), (0, 0), (1, 1)), 0.7854, places=4, msg="Acute angle should be PI/4")
        self.assertAlmostEqual(__get_radian((1, 1), (0, 0), (-1, -1)), 3.1416, places=4, msg="Obtuse angle should be PI")

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
