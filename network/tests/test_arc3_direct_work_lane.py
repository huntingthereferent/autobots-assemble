"""Focused ARC-AGI-3 work lane checks. No SDK or bot execution required."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import WorkspaceStore
from work.arc3.lane import LANE_ID, open_arc_lane, record_trace, summarize_operator_trace


def sample_log(*, before_hash=None, changed=1, include_action=True):
    first = {
        "event": "session_start", "game": "ft09",
        "observation": {
            "frame_hash": "a" * 24, "levels_completed": 0, "state": "NOT_FINISHED"
        },
    }
    rows = [first]
    if include_action:
        rows.append({
            "event": "action", "action": [6, 36, 36],
            "before_hash": before_hash if before_hash is not None else "a" * 24,
            "observation": {
                "frame_hash": "b" * 24, "levels_completed": 0,
                "state": "NOT_FINISHED",
                "diff_from_previous": {
                    "changed_cells": changed, "bbox": [36, 36, 36, 36]
                },
            },
        })
    return "\n".join(json.dumps(r) for r in rows) + "\n"


class ARC3DirectWorkLaneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.trace = Path(self.tmp.name) / "run.jsonl"
        self.trace.write_text(sample_log(), encoding="utf-8")

    def test_valid_source_reported_native_step(self):
        summary = summarize_operator_trace(self.trace)
        self.assertEqual(summary["game"], "ft09")
        self.assertEqual(summary["environment_actions"], 1)
        self.assertEqual(summary["frames_reported_after_actions"], 1)
        self.assertEqual(summary["steps"][0]["action"], [6, 36, 36])
        self.assertEqual(summary["steps"][0]["changed_cells"], 1)
        self.assertIn("no raw-frame", summary["boundary"])

    def test_rejects_broken_frame_chain(self):
        self.trace.write_text(sample_log(before_hash="f" * 24), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "broken before/after"):
            summarize_operator_trace(self.trace)

    def test_rejects_impossible_reported_changed_cells(self):
        self.trace.write_text(sample_log(changed=4097), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed-cell"):
            summarize_operator_trace(self.trace)

    def test_open_has_no_fake_movement_job_or_focus_change(self):
        store = WorkspaceStore()
        store.open_lane("math", label="Mathematics", referent="inverse construction",
                        actor_id="james")
        store.set_focus("math")
        first = open_arc_lane(store)
        second = open_arc_lane(store)
        self.assertEqual(first.latest_event_id, second.latest_event_id)
        self.assertEqual(store.get_lane(LANE_ID).movements, 0)
        self.assertEqual(store.focused_lane(), "math")
        self.assertEqual(store.get_lane("math").movements, 0)
        self.assertEqual(len(store.events()), 3)

    def test_record_one_actual_transcript_reference_and_restart(self):
        journal = Path(self.tmp.name) / "journal.jsonl"
        store = WorkspaceStore(journal)
        store.open_lane("research", label="Research", referent="old",
                        actor_id="james")
        initial = store.get_lane("research")
        summary = summarize_operator_trace(self.trace)
        first = record_trace(store, summary)
        second = record_trace(store, summary)
        self.assertEqual(first.latest_event_id, second.latest_event_id)
        self.assertEqual(first.movements, 1)
        self.assertTrue(first.evidence_refs[0].startswith("operator-log-sha256:"))
        self.assertEqual(store.get_lane("research"), initial)
        restarted = WorkspaceStore(journal)
        self.assertEqual(restarted.get_lane(LANE_ID), first)
        self.assertEqual(record_trace(restarted, summary).movements, 1)

    def test_no_move_without_native_post_action_frame(self):
        self.trace.write_text(sample_log(include_action=False), encoding="utf-8")
        summary = summarize_operator_trace(self.trace)
        store = WorkspaceStore()
        with self.assertRaisesRegex(ValueError, "no native post-action observation"):
            record_trace(store, summary)
        self.assertFalse(store.lanes())


if __name__ == "__main__":
    unittest.main()
