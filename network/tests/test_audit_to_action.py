import unittest
from systems.workspace.audit_to_action import process


class AuditToActionTests(unittest.TestCase):
    def test_preserves_success_without_creating_defect(self):
        r = process({"findings": [{"id": "math-1", "lane": "math", "observation": "Finite witness passed", "source": "work/arc_like_maze/ENGINE_ONE.md", "kind": "verified_result"}]})
        self.assertEqual(r["findings"][0]["action"], "preserve")
        self.assertEqual(r["findings"][0]["state"], "recorded")

    def test_defect_is_not_marked_fixed(self):
        r = process({"findings": [{"id": "ui-1", "lane": "viewer", "observation": "Potential count mismatch", "source": "docs/live/work.html", "kind": "candidate"}]})
        self.assertEqual(r["findings"][0]["state"], "awaiting_verification")
        self.assertEqual(r["findings"][0]["source_status"], "unverified_locator")

    def test_external_boundary_not_fake_failure(self):
        r = process({"findings": [{"id": "ext-1", "lane": "NIH", "observation": "Publication date not established", "source": "source archive", "kind": "external_boundary"}]})
        self.assertEqual(r["findings"][0]["action"], "record_boundary")

    def test_duplicate_ids_rejected(self):
        item = {"id": "x", "lane": "ARC", "observation": "test", "source": "file", "kind": "unknown"}
        with self.assertRaises(ValueError):
            process({"findings": [item, item]})


if __name__ == "__main__":
    unittest.main()
