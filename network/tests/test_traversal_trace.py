from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from runtime.service import EcosystemService
from runtime.trace import TraceStore, TraversalTouch


ROOT = Path(__file__).resolve().parents[2]


class TraversalTraceTests(unittest.TestCase):
    def test_touch_requires_relational_context(self):
        with self.assertRaises(ValueError):
            TraversalTouch.create(
                {
                    "surface_kind": "news",
                    "locator": "https://example.com/story",
                    "relation": "follow report",
                }
            )

    def test_trace_preserves_parent_ancestry_across_unlike_surfaces(self):
        with TemporaryDirectory() as tmp:
            store = TraceStore(Path(tmp) / "trace.jsonl")
            first = store.add(
                TraversalTouch.create(
                    {
                        "trace_id": "t1",
                        "session_id": "s1",
                        "surface_kind": "search",
                        "locator": "https://search.example/?q=company",
                        "referent_before": "understand company closure",
                        "relation": "find reporting",
                        "referent_after": "reported company closure",
                    }
                )
            )
            second = store.add(
                TraversalTouch.create(
                    {
                        "trace_id": "t2",
                        "session_id": "s1",
                        "parent_trace_id": first.trace_id,
                        "surface_kind": "news",
                        "locator": "https://news.example/story",
                        "referent_before": "reported company closure",
                        "relation": "check source details",
                        "referent_after": "closure date and location",
                    }
                )
            )
            third = store.add(
                TraversalTouch.create(
                    {
                        "trace_id": "t3",
                        "session_id": "s1",
                        "parent_trace_id": second.trace_id,
                        "surface_kind": "social",
                        "locator": "https://social.example/post",
                        "referent_before": "closure date and location",
                        "relation": "inspect local reaction",
                    }
                )
            )

            self.assertEqual(
                [touch.trace_id for touch in store.ancestry(third.trace_id)],
                ["t1", "t2", "t3"],
            )
            self.assertEqual(
                [touch.surface_kind for touch in store.ancestry(third.trace_id)],
                ["search", "news", "social"],
            )

    def test_recording_touch_does_not_create_work(self):
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp)
            before = service.status()
            service.add_touch(
                {
                    "surface_kind": "video",
                    "locator": "https://video.example/watch/1",
                    "referent_before": "learn motor control",
                    "relation": "watch explanation",
                    "what_changed": "found a referenced control method",
                }
            )
            after = service.status()

            self.assertEqual(before["systems"]["personal-operations"]["tasks"], 0)
            self.assertEqual(after["systems"]["personal-operations"]["tasks"], 0)
            self.assertEqual(before["runtime"]["handoffs"], after["runtime"]["handoffs"])
            self.assertEqual(after["runtime"]["touches"], 1)

    def test_external_surfaces_are_not_human_areas(self):
        catalog = json.loads(
            (ROOT / "runtime" / "http" / "site_catalog.json").read_text(encoding="utf-8")
        )
        area_ids = {area["id"] for area in catalog["areas"]}
        surface_ids = {
            surface["id"]
            for surface in catalog["external_traversal"]["surfaces"]
        }

        self.assertNotIn("news", area_ids)
        self.assertNotIn("social", area_ids)
        self.assertIn("news", surface_ids)
        self.assertIn("social", surface_ids)
        self.assertIn("search", surface_ids)
        self.assertIn("External state stays external", catalog["external_traversal"]["rule"])

    def test_trace_schema_is_bounded_metadata_not_page_storage(self):
        schema = json.loads(
            (ROOT / "protocols" / "core" / "trace.schema.json").read_text(
                encoding="utf-8"
            )
        )
        properties = schema["properties"]
        self.assertIn("locator", properties)
        self.assertIn("relation", properties)
        self.assertIn("what_changed", properties)
        self.assertNotIn("page_html", properties)
        self.assertNotIn("feed_contents", properties)
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
