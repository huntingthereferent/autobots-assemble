from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
FRONT = ROOT / "runtime" / "http"


class FrontageProjectionTests(unittest.TestCase):
    def test_frontage_has_human_area_catalog(self):
        catalog = json.loads((FRONT / "site_catalog.json").read_text(encoding="utf-8"))
        names = [area["name"] for area in catalog["areas"]]
        self.assertEqual(
            names,
            [
                "Learn",
                "Build",
                "Work",
                "Explore",
                "Connect",
                "World",
                "Organize",
                "Make money",
                "Create",
                "Health / Life",
                "Library",
                "Tools",
            ],
        )

    def test_every_area_has_entries_and_builder_examples(self):
        catalog = json.loads((FRONT / "site_catalog.json").read_text(encoding="utf-8"))
        for area in catalog["areas"]:
            self.assertTrue(area["entries"], area["name"])
            self.assertTrue(area["builders"], area["name"])

    def test_school_is_inside_learning_not_site_root(self):
        catalog = json.loads((FRONT / "site_catalog.json").read_text(encoding="utf-8"))
        learn = next(area for area in catalog["areas"] if area["id"] == "learn")
        self.assertIn("School", learn["entries"])
        html = (FRONT / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>Continuity</title>", html)
        self.assertIn('id="area-grid"', html)

    def test_world_contains_global_place_anchors(self):
        catalog = json.loads((FRONT / "site_catalog.json").read_text(encoding="utf-8"))
        world = next(area for area in catalog["areas"] if area["id"] == "world")
        self.assertIn("Countries", world["entries"])
        self.assertIn("Cities", world["entries"])
        self.assertIn("Local places", world["entries"])

    def test_tools_are_both_area_and_cross_area_capability(self):
        catalog = json.loads((FRONT / "site_catalog.json").read_text(encoding="utf-8"))
        tools = next(area for area in catalog["areas"] if area["id"] == "tools")
        self.assertIn("Build from scratch", tools["builders"])
        for area in catalog["areas"]:
            self.assertTrue(area["builders"])

    def test_human_areas_are_recorded_as_entrances_not_backend_schema(self):
        current = json.loads((ROOT / "state" / "current.json").read_text(encoding="utf-8"))
        self.assertTrue(current["preferred_referent"].startswith("Continuity"))
        self.assertIn("entrances", current["human_areas"]["rule"].lower())
        self.assertIn("LEARN", current["human_areas"]["areas"])
        self.assertIn("TOOLS", current["human_areas"]["areas"])


if __name__ == "__main__":
    unittest.main()
