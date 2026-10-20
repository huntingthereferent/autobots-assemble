"""No-network provenance and pagination tests for the source-run archive."""
import unittest
from views.traces.workflow_history import SCHEMA, collect, normalize_run


def run(i, **kwargs):
    r = dict(id=i, name="Worker check", head_sha="a"*40, status="completed",
             conclusion="success", html_url=f"https://github.com/huntingthereferent/autobots-assemble/actions/runs/{i}",
             created_at="2026-10-19T00:00:00Z", updated_at="2026-10-19T00:00:00Z",
             run_number=i, head_branch="main", event="push")
    r.update(kwargs)
    return r


class ArchiveTests(unittest.TestCase):
    def test_many_pages_are_automatically_indexed_with_source_ids(self):
        pages = {1: [run(i) for i in range(1, 101)],
                 2: [run(i) for i in range(101, 201)],
                 3: [run(i) for i in range(201, 203)]}
        called = []
        def fetch(page):
            called.append(page)
            return {"total_count": 202, "workflow_runs": pages.get(page, [])}
        result = collect(fetch, collected_at="2026-10-19T00:00:00Z")
        self.assertEqual(called, [1, 2, 3])
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["indexed_count"], 202)
        self.assertTrue(result["complete"])
        self.assertEqual(len({x["id"] for x in result["runs"]}), 202)
        self.assertEqual(result["runs"][0]["id"], 202)

    def test_source_loss_or_page_limit_is_not_reported_as_complete(self):
        def missing(page):
            return {"total_count": 220, "workflow_runs": [run(i) for i in range(1, 101)] if page == 1 else []}
        doc = collect(missing, collected_at="2026-10-19T00:00:00Z")
        self.assertFalse(doc["complete"])
        self.assertEqual(doc["indexed_count"], 100)
        def capped(page):
            return {"total_count": 220, "workflow_runs": [run(i+100*(page-1)) for i in range(1, 101)]}
        self.assertFalse(collect(capped, max_pages=2)["complete"])

    def test_invalid_rows_and_duplicate_ids_cannot_create_false_completion(self):
        rows = [run(1), run(1), run(3, head_sha="bad")]
        result = collect(lambda p: {"total_count": 3, "workflow_runs": rows}, collected_at="2026-10-19T00:00:00Z")
        self.assertEqual(result["indexed_count"], 1)
        self.assertEqual(result["invalid_source_rows"], 1)
        self.assertFalse(result["complete"])
        self.assertIsNone(normalize_run(run(5, status="invented")))
        self.assertIsNone(normalize_run(run(5, id=True)))


if __name__ == "__main__":
    unittest.main()
