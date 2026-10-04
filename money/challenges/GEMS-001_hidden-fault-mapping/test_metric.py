import importlib.util
from pathlib import Path
import unittest
import numpy as np

P = Path(__file__).with_name("metric.py")
spec = importlib.util.spec_from_file_location("gems_metric", P)
metric = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metric)

class TestGemsMetric(unittest.TestCase):
    def test_perfect(self):
        g = np.zeros((9, 9)); g[4, 4] = 1
        self.assertAlmostEqual(metric.distance_weighted_tversky(g, g), 1.0, places=10)

    def test_empty_prediction(self):
        g = np.zeros((9, 9)); g[4, 4] = 1
        self.assertAlmostEqual(metric.distance_weighted_tversky(np.zeros_like(g), g), 0.0, places=10)

    def test_one_pixel_offset(self):
        g = np.zeros((9, 9)); g[4, 4] = 1
        p = np.zeros_like(g); p[4, 5] = 1
        self.assertAlmostEqual(metric.distance_weighted_tversky(p, g), 2/3, places=10)

    def test_far_false_positive(self):
        g = np.zeros((11, 11)); g[2, 2] = 1
        p = g.copy(); p[9, 9] = 1
        self.assertAlmostEqual(metric.distance_weighted_tversky(p, g), 1/1.2, places=10)

if __name__ == "__main__":
    unittest.main()
