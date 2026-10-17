"""Regression tests: atlas animation depends on real source-owned state."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from views.motion.atlas_dashboard import snapshot, dashboard, generate, ROOT, _load


class AtlasDashboardTests(unittest.TestCase):
    def test_current_sources_compose_validated_cinematic_atlas(self):
        data=snapshot()
        self.assertEqual(sum(n for _,n in data["category_counts"]),data["source_count"])
        self.assertGreaterEqual(data["sampled_probes"],1)
        image=dashboard(data)
        ET.fromstring(image)
        self.assertIn("JAMES",image)
        self.assertIn("MUNEOKA",image)
        self.assertIn("NATIVE FINITE TRACE",image)
        self.assertIn(data["finite"]["left_word"],image)
        self.assertIn(data["finite"]["right_word"],image)
        self.assertIn("NOT JOINED",image)
        self.assertIn("NOT ALL ACTIVE",image)
        self.assertIn("prefers-reduced-motion",image)
        self.assertIn("@keyframes spin",image)
        self.assertNotIn("<script",image)

    def test_missing_source_is_not_zero(self):
        before=_load
        def no_source(rel):
            result=before(rel)
            if rel=="views/traces/internet-map.json":
                result["probes"]=None
            return result
        with patch("views.motion.atlas_dashboard._load",side_effect=no_source):
            with self.assertRaises(ValueError):
                snapshot()

    def test_changed_mathematical_receipt_must_be_rejected(self):
        original=_load
        def modified(rel):
            result=original(rel)
            if rel=="views/motion/convergence-receipt.json":
                result["target"]=[0,0,0]
            return result
        with patch("views.motion.atlas_dashboard._load",side_effect=modified):
            with self.assertRaises(ValueError):
                snapshot()

    def test_false_no_token_traffic_claim_fails(self):
        original=_load
        def bad(rel):
            result=original(rel)
            if rel=="views/traces/internet-map.json":
                result["traffic_state"]="SOURCE_MEASURED"
            return result
        with patch("views.motion.atlas_dashboard._load",side_effect=bad):
            with self.assertRaises(ValueError):
                snapshot()

    def test_render_writes_only_generated_image(self):
        tracked=[ROOT/"views/traces/registry.json",
                 ROOT/"views/traces/internet-map.json",
                 ROOT/"views/motion/convergence-receipt.json",
                 ROOT/"views/work_state.json"]
        orig=[p.read_bytes() for p in tracked]
        with TemporaryDirectory() as d:
            svg=generate(Path(d))
            file=Path(d)/"atlas-dashboard.svg"
            self.assertEqual(file.read_text(),svg+"\n")
            ET.parse(file)
        self.assertEqual(orig,[p.read_bytes() for p in tracked])


if __name__=="__main__":
    unittest.main()
