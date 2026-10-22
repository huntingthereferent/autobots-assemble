"""Calendar movement must be sourced from durable workflow health."""
import base64
import datetime as dt
import json
import unittest

from systems.workspace.inspector_gadget_calendar import (
    combine, calendar_plan, load_health,
)

NOW = dt.datetime(2026, 10, 22, 23, 30, tzinfo=dt.timezone.utc)
REPO = "huntingthereferent/autobots-assemble"


def open_lane(wid, run_id, name="NIH source", conclusion="failure"):
    return {"workflow_id": wid, "run_id": run_id, "name": name,
            "conclusion": conclusion, "state": "needs_attention",
            "run_url": f"https://github.com/{REPO}/actions/runs/{run_id}"}


def health(open_items):
    return {"schema": "meta-workstation/current-workflow-health-v1",
            "observed_at": "2026-10-22T22:49:00Z",
            "nodes": {
                "A": {"repo": REPO, "observed": True, "open": open_items},
                "B": {"repo": "other/account", "observed": False},
            }}


def scan(findings=None):
    return {"schema": "inspector-gadget/workflow-scan/v1",
            "since": "2026-10-22T21:00:00Z",
            "scanned": 1000, "findings": findings or []}


class CalendarTests(unittest.TestCase):
    def test_all_persistent_old_open_lanes_move_without_two_hour_limit(self):
        h = health([open_lane(7, 123, "ARC"),
                    open_lane(8, 234, "NIH"),
                    open_lane(9, 345, "WORLD"),
                    open_lane(10, 456, "Meow Lab")])
        plan = calendar_plan(scan(), h, repo=REPO, now=NOW)
        self.assertEqual(plan["calendar"]["current_source_open"], 4)
        self.assertEqual(plan["selected"], 4)
        self.assertEqual(set(x["lane"] for x in plan["matrix"]["include"]),
                         {"ARC", "NIH", "WORLD", "Meow Lab"})
        self.assertEqual(plan["calendar"]["condition"], "start_inspection_lanes")

    def test_no_pending_does_not_spawn(self):
        p = calendar_plan(scan(), health([]), repo=REPO, now=NOW)
        self.assertEqual(p["selected"], 0)
        self.assertEqual(p["calendar"]["condition"], "no_incidents")

    def test_merged_scan_and_health_deduplicate_exact_run(self):
        row = {"id": "inspector-7-failure-123", "lane": "ARC", "event": "failure",
               "kind": "candidate", "run_ids": [123],
               "sources": [f"https://github.com/{REPO}/actions/runs/123"],
               "head_shas": []}
        p = calendar_plan(scan([row]), health([open_lane(7, 123, "ARC")]),
                          repo=REPO, now=NOW)
        self.assertEqual(p["selected"], 1)
        self.assertEqual(p["calendar"]["persisted_walls_added"], 0)

    def test_stale_health_cannot_claim_no_pending(self):
        h = health([open_lane(7, 123)])
        h["observed_at"] = "2026-10-21T22:49:00Z"
        with self.assertRaisesRegex(ValueError, "stale"):
            calendar_plan(scan(), h, repo=REPO, now=NOW)

    def test_unobserved_primary_cannot_be_equated_to_empty(self):
        h = health([])
        h["nodes"]["A"]["observed"] = False
        with self.assertRaisesRegex(ValueError, "not source-observed"):
            combine(scan(), h, repo=REPO, now=NOW)

    def test_source_owned_only_and_no_duplicate_workflow(self):
        h = health([open_lane(7, 123), open_lane(7, 124)])
        with self.assertRaises(ValueError):
            calendar_plan(scan(), h, repo=REPO, now=NOW)
        h = health([open_lane(7, 123)])
        h["nodes"]["A"]["repo"] = "somebody/else"
        with self.assertRaises(ValueError):
            calendar_plan(scan(), h, repo=REPO, now=NOW)

    def test_read_persistent_health_without_mutation(self):
        data = health([open_lane(7, 123)])
        wrapper = {"encoding": "base64", "content": base64.b64encode(
            json.dumps(data).encode()).decode()}
        self.assertEqual(load_health(REPO, "fake", getter=lambda: wrapper), data)

    def test_capacity_is_explicit(self):
        h = health([open_lane(i, 300 + i) for i in range(1, 8)])
        plan = calendar_plan(scan(), h, repo=REPO, now=NOW, max_movements=3)
        self.assertEqual(plan["selected"], 3)
        self.assertEqual(plan["overflow_count"], 4)
        self.assertEqual(plan["calendar"]["current_source_open"], 7)


if __name__ == "__main__":
    unittest.main()
