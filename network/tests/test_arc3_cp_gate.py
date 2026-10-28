"""Negative-control regressions for selected original ARC A/B CP boundaries."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from work.arc3.cp_gate import CONTEXT_FILES, LANES, entry, exit_gate, verify_entry


class ARCNativeCPGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        paths = set(CONTEXT_FILES)
        for spec in LANES.values():
            paths.add(spec["source"])
            if "extra_source" in spec:
                paths.add(spec["extra_source"])
        for name in paths:
            f = self.root / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("frozen source: " + name + "\n")

    def _evidence(self, lane: str, obj: dict):
        output = self.root / LANES[lane]["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(obj))
        with ZipFile(output.with_suffix(".npz"), "w") as z:
            z.writestr("raw.npy", b"preserved container placeholder")

    def _stage3(self):
        plans = [[f"candidate-{i}", "5"] for i in range(16)]
        rows = [
            {"frozen_candidate": p[0], "original_verified_stage3_root": {"original_source_sha256": "root"},
             "official_original_final_level": 3, "official_original_level4_or_WIN": False}
            for p in plans for _ in range(2)
        ]
        return {
            "kind": LANES["sp80-stage3"]["kind"],
            "precommitted_candidate_words": plans,
            "all_actual_original_sdk_records": rows,
            "original_source_stage3_entry_hash": "root",
            "actual_original_source_level4_or_WIN": 0,
            "original_source_successes": [],
            "original_sdk_final_levels": {"3": 32},
        }

    def test_realistic_pairwise_negatives_are_retained_as_results(self):
        lane = "sp80-stage3"
        a = entry(lane, root=self.root)
        self._evidence(lane, self._stage3())
        b = exit_gate(lane, a, root=self.root)
        self.assertEqual(b["observed"]["trials"], 32)
        self.assertEqual(b["observed"]["negative_or_unproved"], 32)
        self.assertEqual(b["observed"]["native_level4_or_win"], 0)
        self.assertIn("NOT_INDEPENDENTLY_REPLAYED", b["status"])
        self.assertEqual(b["source_pins"], a["source_pins"])

    def test_stale_source_rejected_at_output_boundary(self):
        lane = "sp80-stage3"
        a = entry(lane, root=self.root)
        self._evidence(lane, self._stage3())
        (self.root / LANES[lane]["source"]).write_text("changed during native work")
        with self.assertRaisesRegex(ValueError, "stale, changed"):
            exit_gate(lane, a, root=self.root)

    def test_missing_cp_and_swapped_lanes_rejected(self):
        a = entry("sp80-stage3", root=self.root)
        bad = deepcopy(a)
        bad["boundary"] = "everything proven"
        with self.assertRaisesRegex(ValueError, "stale, changed"):
            verify_entry("sp80-stage3", bad, root=self.root)
        with self.assertRaisesRegex(ValueError, "stale, changed"):
            verify_entry("window48-sk48", a, root=self.root)

    def test_false_positive_and_missing_frames_fail_closed(self):
        lane = "sp80-stage3"
        a = entry(lane, root=self.root)
        false = self._stage3()
        false["actual_original_source_level4_or_WIN"] = 2
        self._evidence(lane, false)
        with self.assertRaisesRegex(ValueError, "promoted successes differ"):
            exit_gate(lane, a, root=self.root)
        self._evidence(lane, self._stage3())
        (self.root / LANES[lane]["output"]).with_suffix(".npz").unlink()
        with self.assertRaisesRegex(ValueError, "NPZ missing"):
            exit_gate(lane, a, root=self.root)

    def test_native_smoke_wall_retained_as_evidence(self):
        lane = "window48-ft09"
        a = entry(lane, root=self.root)
        self._evidence(lane, {
            "kind": "ORIGINAL_WINDOW48_NATIVE_INTERFACE_WALL", "game": "ft09",
            "source_agent_sha256": a["source_pins"][LANES[lane]["extra_source"]],
            "native_environment_actions": 0,
            "status": "WALL_NO_OBSERVED_NATIVE_A_B_GENERATORS",
        })
        b = exit_gate(lane, a, root=self.root)
        self.assertTrue(b["observed"]["interface_wall"])
        self.assertEqual(b["observed"]["native_environment_actions"], 0)

    def test_no_output_is_not_reported_as_no_progress(self):
        lane = "sp80-stage3"
        a = entry(lane, root=self.root)
        with self.assertRaisesRegex(ValueError, "not emitted"):
            exit_gate(lane, a, root=self.root)


if __name__ == "__main__":
    unittest.main()
