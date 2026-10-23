"""Calendar correspondence verifies source boundaries and cannot create work."""
import unittest
from datetime import datetime

from systems.calendar.daily_correspondence import build, SCHEMA

NOW = datetime.fromisoformat("2026-10-23T09:05:00-05:00")
BASE = {"schema": "workstation-live-projection/v1", "records": [
    {"path": "research/a.json", "label": "ARC evidence", "state": "PARTIAL",
     "source_type": "RESEARCH_DIVE", "next": "Check held-out run", "boundary": "Not solved"},
    {"path": "research/b.json", "label": "NIH archive", "state": "MOVE_WITH_WALL",
     "source_type": "CHECKPOINT", "next": "Verify owner source"},
]}


class DailyCorrespondenceTests(unittest.TestCase):
    def packet(self, **kwargs):
        return build(now=NOW, revision="a" * 40, projection=BASE, **kwargs)

    def test_daily_calendar_gate_and_source_pinning(self):
        p = self.packet()
        self.assertEqual(p["schema"], SCHEMA)
        self.assertEqual(p["local_date"], "2026-10-23")
        self.assertEqual(p["calendar_relation"]["recurrence"], "daily")
        self.assertEqual(p["calendar_relation"]["movement_anchor"], "REOPEN")
        self.assertIn("a" * 40, p["prompt"])
        self.assertIn("Not solved", p["prompt"])

    def test_no_private_journal_fails_explicitly_closed(self):
        p = self.packet()
        self.assertEqual(p["workspace_state"], "UNAVAILABLE_PRIVATE_JOURNAL")
        self.assertIsNone(p["workspace_lanes"])
        self.assertIn("cannot be reconstructed", p["prompt"])
        self.assertIn("historical until independently reverified", p["prompt"])

    def test_distinct_lanes_retain_independent_return_points(self):
        ws = {"lanes": [
            {"lane_id": "arc", "label": "ARC", "referent": "geometry",
             "return_event_id": "event-a", "next_movement": "test A"},
            {"lane_id": "nih", "label": "NIH", "referent": "archive",
             "return_event_id": "event-b", "next_movement": "test B"},
        ], "connections": []}
        p = self.packet(workspace=ws)
        self.assertEqual(len(p["workspace_lanes"]), 2)
        self.assertIn("event-a", p["prompt"])
        self.assertIn("event-b", p["prompt"])
        self.assertIn("test A", p["prompt"])
        self.assertIn("test B", p["prompt"])

    def test_previous_source_index_comparison_is_not_work_completion(self):
        prev = self.packet()
        changed = {"schema": BASE["schema"], "records": [
            {**BASE["records"][0], "state": "MOVE_WITH_WALL"}, BASE["records"][1],
            {"path": "research/new.json", "label": "New receipt", "state": "PARTIAL"}]}
        result = build(now=NOW, revision="b" * 40, projection=changed, previous=prev)
        delta = result["research_delta"]
        self.assertEqual(delta["changed_paths"], ["research/a.json"])
        self.assertEqual(delta["added_paths"], ["research/new.json"])
        self.assertIn("not full research movement", delta["boundary"])

    def test_github_api_sample_is_limited_not_total_execution(self):
        p = self.packet(runs={"total_count": 9000, "workflow_runs": [
            {"id": 1, "name": "ARC", "status": "in_progress", "conclusion": None,
             "head_sha": "abc", "html_url": "https://github.com/example"}]})
        self.assertEqual(p["workflow_sample"]["count"], 1)
        self.assertEqual(p["workflow_sample"]["reported_total"], 9000)
        self.assertEqual(p["workflow_sample"]["availability"], "OBSERVED_LATEST_PAGE")
        self.assertIn("Not all workers", p["prompt"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            build(now=datetime(2026, 10, 23), revision="a" * 40, projection=BASE)
        with self.assertRaises(ValueError):
            build(now=NOW, revision="", projection=BASE)
        with self.assertRaises(ValueError):
            build(now=NOW, revision="a" * 40, projection={"schema": "wrong"})

    def test_no_side_effect_commands_in_renderer(self):
        p = self.packet()
        self.assertIn("no access, authorization, workflow dispatch or task admission", p["prompt"])


if __name__ == "__main__":
    unittest.main()
