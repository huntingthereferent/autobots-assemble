from pathlib import Path
import importlib.util
import json
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GEMS = ROOT / "money" / "challenges" / "GEMS-001_hidden-fault-mapping"


class GemsActivationTests(unittest.TestCase):
    def test_active_referent(self):
        state = json.loads((ROOT / "state" / "current.json").read_text(encoding="utf-8"))
        self.assertIn("GEMS-001", state["preferred_referent"])

    def test_record_has_data_wall(self):
        rec = json.loads((GEMS / "challenge.json").read_text(encoding="utf-8"))
        self.assertTrue(any("data page" in w.lower() for w in rec["walls"]))

    def test_unmapped_is_not_negative(self):
        text = (GEMS / "BASELINE_DISSECTION.md").read_text(encoding="utf-8")
        self.assertIn("not mapped", text)
        self.assertIn("negative", text)

    def test_metric_synthetic_cases(self):
        spec = importlib.util.spec_from_file_location("gems_metric", GEMS / "metric.py")
        metric = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(metric)

        g = np.zeros((11, 11), dtype=float)
        g[4, 4] = 1.0
        self.assertAlmostEqual(metric.distance_weighted_tversky(g, g), 1.0, places=10)

        p = np.zeros_like(g)
        p[4, 5] = 1.0
        self.assertAlmostEqual(metric.distance_weighted_tversky(p, g), 2 / 3, places=10)

        p = g.copy()
        p[9, 9] = 1.0
        self.assertAlmostEqual(metric.distance_weighted_tversky(p, g), 1 / 1.2, places=10)


if __name__ == "__main__":
    unittest.main()
