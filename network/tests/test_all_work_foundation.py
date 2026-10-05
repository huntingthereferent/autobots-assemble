from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CompleteStackFoundationTests(unittest.TestCase):
    def test_complete_stack_separates_problem_capability_layer_and_depth(self):
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("Referent", arch)
        self.assertIn("Capability", arch)
        self.assertIn("Dependency layer", arch)
        self.assertIn("Realization depth", arch)
        self.assertIn("No layer is privileged", arch)

    def test_foundation_is_evidence_and_views_are_read_only(self):
        text = (ROOT / "foundation" / "README.md").read_text(encoding="utf-8")
        self.assertIn("preserved body of **demonstrated evidence**", text)
        self.assertIn("not the repo's top-level goal", text)
        view = (ROOT / "foundation" / "CREDIBILITY_VIEW.md").read_text(encoding="utf-8")
        self.assertIn("read-only projection", view)
        self.assertIn("does not select development", view)

    def test_foundation_protocol_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("foundation.record", index["protocols"])

    def test_foundation_registry_is_consistent(self):
        index = json.loads((ROOT / "foundation" / "index.json").read_text(encoding="utf-8"))
        ids = [int(record["id"].split("-")[1]) for record in index["records"]]
        expected_next = max(ids, default=0) + 1
        self.assertEqual(index["next_id"], expected_next)

        for record in index["records"]:
            path = ROOT / record["path"]
            self.assertTrue(path.exists(), record["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["id"], record["id"])
            self.assertEqual(payload["title"], record["title"])


if __name__ == "__main__":
    unittest.main()
