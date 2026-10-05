from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AllWorkFoundationTests(unittest.TestCase):
    def test_all_work_axes_are_separate(self):
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("Goal lane", arch)
        self.assertIn("Field / domain", arch)
        self.assertIn("Realization layer", arch)
        self.assertIn("physical is not a goal lane", arch.lower())

    def test_foundation_is_not_goal_lane_and_credibility_is_lens(self):
        text = (ROOT / "foundation" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Foundation is not a fourth goal lane", text)
        self.assertIn("Credibility is derived from Foundation", text)
        lens = (ROOT / "foundation" / "CREDIBILITY_LENS.md").read_text(encoding="utf-8")
        self.assertIn("read-only projection", lens)

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
