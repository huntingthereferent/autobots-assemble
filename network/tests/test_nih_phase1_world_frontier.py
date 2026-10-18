"""Falsification of Phase 1 frontier reading inside original W13/NIH world."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_phase1_world_frontier import (
    SCHEMA, overlay_html, check_frame, check_sequence, run_world,
)


def frame(*, turn, known, visible, withheld, static=("prior-note", "delayed-result")):
    return {
        "turn": str(turn),
        "known": known,
        "target": "2026-01-04",
        "visible": ",".join(visible),
        "withheld": ",".join(withheld),
        "static": ",".join(static),
        "query_sha": "a" * 64,
        "clinical": "NOT_EVALUATED",
    }


def oracle_result(visible, withheld, static=("prior-note", "delayed-result")):
    return {
        "temporal_ids": list(visible),
        "future_leakage_ids": list(withheld),
        "static_snapshot_ids": list(static),
    }


def expected_sequence():
    return [
        {
            "turn": 0, "known_at": "2026-01-04", "target_at": "2026-01-04",
            "visible_ids": ["prior-note"],
            "future_withheld_ids": ["delayed-result"],
            "static_ids": ["delayed-result", "prior-note"],
        },
        {
            "turn": 1, "known_at": "2026-01-04", "target_at": "2026-01-04",
            "visible_ids": ["prior-note"],
            "future_withheld_ids": ["delayed-result"],
            "static_ids": ["delayed-result", "prior-note"],
        },
        {
            "turn": 2, "known_at": "2026-01-06", "target_at": "2026-01-04",
            "visible_ids": ["delayed-result", "prior-note"],
            "future_withheld_ids": [],
            "static_ids": ["delayed-result", "prior-note"],
        },
    ]


class Phase1WorldFrontierTests(unittest.TestCase):
    def test_00_only_overlay_original_native_game(self):
        html='<html><div id="grid"></div><script id="native-temporal-client"></script></body>'
        result=overlay_html(html)
        self.assertIn("phase1-world-frontier-source",result)
        self.assertIn('document.querySelector("#temporal-panel")',result)
        self.assertIn('fetch("/api/query?turn="',result)
        self.assertEqual(result.count("id=\"native-temporal-client\""),1)
        with self.assertRaises(ValueError):
            overlay_html(result)
        with self.assertRaises(ValueError):
            overlay_html('<html><div id="grid"></div></body>')

    def test_01_host_reconstructs_actual_visible_and_withheld_sets(self):
        obs=frame(turn=1,known="2026-01-04",
                  visible=("prior-note",),withheld=("delayed-result",),
                  static=("delayed-result","prior-note"))
        expected=oracle_result(("prior-note",),("delayed-result",),
                               ("delayed-result","prior-note"))
        r=check_frame(obs,turn=1,known="2026-01-04",target="2026-01-04",
                      source_sha="a"*64,expected=expected)
        self.assertTrue(r["independent_scope_agreement"])
        self.assertEqual(r["future_withheld_ids"],["delayed-result"])

    def test_02_reject_false_visible_and_wrong_program_provenance(self):
        obs=frame(turn=1,known="2026-01-04",
                  visible=("prior-note",),withheld=("delayed-result",),
                  static=("delayed-result","prior-note"))
        exp=oracle_result(("prior-note",),("delayed-result",),
                          ("delayed-result","prior-note"))
        for key,value in (
            ("turn","12"),("known","2026-01-06"),
            ("visible","delayed-result,prior-note"),
            ("withheld",""),("static","prior-note"),
            ("query_sha","b"*64),("clinical","EVALUATED"),
        ):
            changed=dict(obs)
            changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                check_frame(changed,turn=1,known="2026-01-04",
                            target="2026-01-04",source_sha="a"*64,expected=exp)

    def test_03_partition_cannot_duplicate_or_omit_source_evidence(self):
        obs=frame(turn=1,known="2026-01-04",
                  visible=("prior-note",),withheld=("delayed-result",),
                  static=("delayed-result","prior-note"))
        for fake in (
            oracle_result(("prior-note",),("prior-note","delayed-result"),
                          ("delayed-result","prior-note")),
            oracle_result(("prior-note",),("delayed-result",),("prior-note",)),
        ):
            with self.assertRaises(ValueError):
                check_frame(obs,turn=1,known="2026-01-04",
                            target="2026-01-04",source_sha="a"*64,expected=fake)

    def test_04_exact_world_cutover_monotonicity_and_negative_controls(self):
        sample=expected_sequence()
        self.assertTrue(check_sequence(sample,expected_cutover=2))
        for change in (
            lambda x: x[2].update(known_at="2026-01-03"),
            lambda x: x[2].update(visible_ids=["prior-note"]),
            lambda x: x[2].update(static_ids=["prior-note"]),
            lambda x: x[2].update(future_withheld_ids=["delayed-result"]),
            lambda x: x[1].update(turn=0),
            lambda x: x[2].update(target_at="2026-01-05"),
        ):
            import copy
            fake=copy.deepcopy(sample)
            change(fake)
            with self.assertRaises(ValueError):
                check_sequence(fake,expected_cutover=2)

    @unittest.skipUnless(importlib.util.find_spec("playwright") is not None and
                         os.environ.get("RUN_PHASE1_WORLD_INTEGRATION") == "1",
                         "real independent browser run is opt-in and runs once in dedicated CI")
    def test_05_replay_original_twelve_with_actual_world_movement(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            report=run_world(data_dir=root/"workstation",output_dir=root/"evidence")
            self.assertEqual(report["schema"],SCHEMA)
            self.assertEqual(report["original_native_jobs"],12)
            self.assertTrue(report["browser_world_solved"])
            self.assertTrue(report["independent_scope_oracle_agreed"])
            self.assertTrue(report["fixed_source_knowledge_monotonicity_observed"])
            self.assertFalse(report["new_native_job_created"])
            self.assertFalse(report["new_NIH_checkpoint_claimed"])
            self.assertFalse(report["official_NIH_submission"])
            self.assertFalse(report["historical_publication_time_authenticated"])
            self.assertEqual(len(report["additional_boundary_queries"]),9)
            self.assertEqual(len(report["browser_frames"]), report["actual_world_actions"]+1)
            self.assertTrue((root/"evidence/nih-phase1-frontier-live-world.png").is_file())


if __name__=="__main__":
    unittest.main()
