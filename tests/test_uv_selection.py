import importlib
from pathlib import Path
import sys
import types
import unittest


package = types.ModuleType("uv_selection_test_plugin")
package.__path__ = [str(Path(__file__).resolve().parents[1] / "KritaBlenderLink")]
sys.modules[package.__name__] = package
try:
    rasterize = importlib.import_module(package.__name__ + ".uv_selection").uv_selection_pixels
except ImportError:
    rasterize = None


@unittest.skipIf(rasterize is None, "Requires PyQt5 or PyQt6")
class SelectionTests(unittest.TestCase):
    def test_odd_width_has_no_scanline_padding(self):
        face = [[0, 0], [1, 0], [1, 1], [0, 1]]
        self.assertEqual(rasterize([face], 5, 3), bytes([255]) * 15)
        self.assertEqual(face[2], [1, 1])

    def test_adjacent_triangles_have_no_seam(self):
        faces = [[[0, 0], [1, 0], [0, 1]], [[1, 0], [1, 1], [0, 1]]]
        self.assertEqual(rasterize(faces, 8, 8), bytes([255]) * 64)

    def test_overlaps_are_union_and_coordinates_are_top_down(self):
        face = [[0, 0], [1, 0], [1, 0.5], [0, 0.5]]
        self.assertEqual(rasterize([face, face], 4, 4), bytes([255]) * 8 + bytes(8))

    def test_empty_and_outside_faces(self):
        self.assertEqual(rasterize([], 4, 4), bytes(16))
        self.assertEqual(rasterize([[[2, 2], [3, 2], [3, 3]]], 4, 4), bytes(16))


if __name__ == "__main__":
    unittest.main()
