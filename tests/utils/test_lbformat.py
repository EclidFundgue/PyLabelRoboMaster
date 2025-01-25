import os
import tempfile
import unittest

from src.utils.lbformat import (ibxy2line, ixy2line, line2ibxy, line2ixy,
                                loadLabel, saveLabel, xy2box)


class TestLabelIOFunctions(unittest.TestCase):

    def test_line2ixy(self):
        line = "1 1.0 2.0 3.0 4.0"
        expected = (1, [1.0, 3.0], [2.0, 4.0])
        self.assertEqual(line2ixy(line), expected)

    def test_ixy2line(self):
        idx = 1
        xs = [1.0, 3.0]
        ys = [2.0, 4.0]
        expected = "1 1.0 2.0 3.0 4.0"
        self.assertEqual(ixy2line(idx, xs, ys), expected)

    def test_line2ibxy(self):
        line = "1 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0"
        expected = (1, [1.0, 2.0, 3.0, 4.0], [5.0, 7.0], [6.0, 8.0])
        self.assertEqual(line2ibxy(line), expected)

    def test_ibxy2line(self):
        idx = 1
        box = [1.0, 2.0, 3.0, 4.0]
        xs = [5.0, 7.0]
        ys = [6.0, 8.0]
        expected = "1 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0"
        self.assertEqual(ibxy2line(idx, box, xs, ys), expected)

    def test_xy2box(self):
        xs = [1.0, 3.0, 4.0, 2.0]
        ys = [2.0, 4.0, 6.0, 5.0]
        expected = [2.5, 4.0, 3.0, 4.0]
        self.assertEqual(xy2box(xs, ys), expected)

    def test_loadLabel(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write("1 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0\n")
            f.write("2 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0\n")

        labels = loadLabel(f.name)
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0].cls_id, 1)
        self.assertEqual(labels[0].kpts, [(5.0, 6.0), (7.0, 8.0)])
        self.assertEqual(labels[1].cls_id, 2)
        self.assertEqual(labels[1].kpts, [(13.0, 14.0), (15.0, 16.0)])

        os.unlink(f.name)

    def test_saveLabel(self):
        labels = [
            type('LabelIO', (object,), {'cls_id': 1, 'kpts': [(5.0, 6.0), (7.0, 8.0)]})(),
            type('LabelIO', (object,), {'cls_id': 2, 'kpts': [(13.0, 14.0), (15.0, 16.0)]})()
        ]

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            saveLabel(f.name, labels)
            f.seek(0)
            content = f.read()

        expected_lines = [
            "1 6.0 7.0 2.0 2.0 5.0 6.0 7.0 8.0",
            "2 14.0 15.0 2.0 2.0 13.0 14.0 15.0 16.0"
        ]
        self.assertEqual(content.strip(), '\n'.join(expected_lines))

        os.unlink(f.name)
