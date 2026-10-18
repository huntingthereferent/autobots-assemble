"""Negative controls for an uncertain posting interval in the ORIGINAL W13 game.

The original emitted Python supports exact known_at timestamps only. These
tests reject collapsing externally proposed uncertain source posting bounds
into an unverified definitive answer. Fake frames aren't live evidence.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_phase1_world_publication_uncertainty import (
    BOUNDS, CUTOFFS, SCHEMA, POLICY, TARGET, attach,
    source_with_bounds, independent_classification, verify_boundary,
    check_capture, check_grid, run_world,
)

SCOPE_FILE=Path(__file__).resolve().parent/"fixtures/nih_scope_example.json"


def scope():
    return json.loads(SCOPE_FILE.read_text(encoding="utf8"))


def observed_frame(turn, k):
    expected=independent_classification(scope(),known=k,target=TARGET)
    native="2026-01-04" if turn<2 else "2026-01-06"
    return {
        "turn":turn,"known_at":k,"native_game_known_at":native,
        "target_at":TARGET,**expected,
        "source_program_sha256":"a"*64,
        "conservative_dataset_sha256":"b"*64,
        "independent_source_policy_agreement":True,
    }


class UncertainPublicationWorldTests(unittest.TestCase):
    def test_00_requires_real_original_game_and_two_clock_panel(self):
        original='<html><script id="phase1-world-frontier-source"></script><script id="phase1-world-two-clock"></script></body>'
        amended=attach(original)
        self.assertIn("phase1UncertainSourceProbe",amended)
        self.assertEqual(amended.count('id="phase1-publication-uncertainty"'),1)
        with self.assertRaises(ValueError):
            attach(amended)
        with self.assertRaises(ValueError):
            attach('<html><script id="phase1-world-two-clock"></script></body>')

    def test_01_source_bounds_are_constructed_not_exact_original_version(self):
        original=scope()
        adapted=source_with_bounds(original)
        raw={r["id"]:r for r in original["observations"]}
        rows={r["id"]:r for r in adapted["observations"]}
        self.assertEqual(raw["delayed-result"]["known_at"],"2026-01-05")
        self.assertEqual(rows["delayed-result"]["known_at"],"2026-01-07")
        self.assertEqual(rows["prior-note"],raw["prior-note"])
        self.assertEqual(BOUNDS["delayed-result"],("2026-01-04","2026-01-07"))
        self.assertNotEqual(adapted["observations"],original["observations"])
        tampered=deepcopy(original)
        tampered["observations"][1]["known_at"]="2026-01-10"
        with self.assertRaises(ValueError):
            source_with_bounds(tampered)

    def test_02_exact_boundary_states_are_not_two_way_guesses(self):
        explicit=[
            ("2026-01-03",["prior-note"],["delayed-result"],[]),
            ("2026-01-04",["prior-note"],[],["delayed-result"]),
            ("2026-01-06",["prior-note"],[],["delayed-result"]),
            ("2026-01-07",["delayed-result","prior-note"],[],[]),
        ]
        for k,eligible,withheld,unknown in explicit:
            with self.subTest(known_at=k):
                r=independent_classification(scope(),known=k,target=TARGET)
                self.assertEqual(r["admitted_ids"],eligible)
                self.assertEqual(r["definitely_withheld_ids"],withheld)
                self.assertEqual(r["indeterminate_ids"],unknown)
                self.assertEqual(r["static_valid_ids"],["delayed-result","prior-note"])
                self.assertEqual(r["outside_validity_ids"],[])

    def test_03_reject_native_selector_that_treats_unknown_as_admitted(self):
        conservative=source_with_bounds(scope())
        correct={
            "temporal_ids":["prior-note"],
            "future_leakage_ids":["delayed-result"],
            "static_snapshot_ids":["delayed-result","prior-note"],
            "outside_validity_ids":[],
        }
        r=verify_boundary(scope(),conservative,correct,
                          known="2026-01-06",target=TARGET)
        self.assertEqual(r["indeterminate_ids"],["delayed-result"])
        wrong=deepcopy(correct)
        wrong["future_leakage_ids"]=[]
        with self.assertRaises(ValueError):
            verify_boundary(scope(),conservative,wrong,known="2026-01-06",target=TARGET)
        wrong=deepcopy(correct)
        wrong["temporal_ids"]=["delayed-result","prior-note"]
        with self.assertRaises(ValueError):
            verify_boundary(scope(),conservative,wrong,known="2026-01-06",target=TARGET)

    def test_04_browser_labels_and_source_digest_are_not_interchangeable(self):
        expected=independent_classification(scope(),known="2026-01-04",target=TARGET)
        fields={
            "turn":"0","known":"2026-01-04","native_known":"2026-01-04",
            "target":TARGET,"admitted":"prior-note","withheld":"",
            "unknown":"delayed-result","outside":"",
            "static":"delayed-result,prior-note",
            "program_sha":"a"*64,"dataset_sha":"b"*64,
            "policy":POLICY,"clinical":"NOT_EVALUATED",
        }
        checked=check_capture(fields,expected,turn=0,known="2026-01-04",
            native_known="2026-01-04",source_sha="a"*64,dataset_sha="b"*64)
        self.assertEqual(checked["indeterminate_ids"],["delayed-result"])
        for key,value in (
            ("unknown",""),("withheld","delayed-result"),
            ("admitted","delayed-result,prior-note"),
            ("program_sha","c"*64),("dataset_sha","d"*64),
            ("native_known","2026-01-06"),("policy","fake"),
            ("clinical","EVALUATED")):
            tampered=dict(fields);tampered[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):
                check_capture(tampered,expected,turn=0,known="2026-01-04",
                    native_known="2026-01-04",source_sha="a"*64,dataset_sha="b"*64)

    def test_05_replay_requires_all_game_turn_and_cutoff_frames(self):
        frames=[observed_frame(t,k) for t in range(5) for k in CUTOFFS]
        self.assertTrue(check_grid(frames,actions=4,cutover=2))
        with self.assertRaises(ValueError):
            check_grid(frames[:-1],actions=4,cutover=2)
        for index,change in (
            (1,{"indeterminate_ids":[]}),
            (1,{"definitely_withheld_ids":["delayed-result"]}),
            (2,{"source_program_sha256":"e"*64}),
            (6,{"native_game_known_at":"2026-01-06"}),
            (8,{"native_game_known_at":"2026-01-04"}),
            (11,{"admitted_ids":["delayed-result","prior-note"]}),
            (17,{"static_valid_ids":["prior-note"]}),
        ):
            altered=deepcopy(frames)
            altered[index].update(change)
            with self.subTest(index=index,change=change),self.assertRaises(ValueError):
                check_grid(altered,actions=4,cutover=2)

    @unittest.skipUnless(os.environ.get("RUN_PHASE1_UNCERTAIN_PUBLICATION_NATIVE")=="1"
                         and importlib.util.find_spec("playwright") is not None,
                         "independent original-native Chromium test runs in dedicated CI")
    def test_06_real_game_queries_original_python_with_source_uncertainty(self):
        with TemporaryDirectory() as td:
            path=Path(td)
            report=run_world(data_dir=path/"native",output_dir=path/"evidence")
            self.assertEqual(report["schema"],SCHEMA)
            self.assertEqual(report["original_native_jobs"],12)
            self.assertTrue(report["played_original_game_solved"])
            self.assertTrue(report["independent_three_state_policy_verified"])
            self.assertTrue(report["original_native_journals_preserved"])
            self.assertFalse(report["new_native_job"])
            self.assertFalse(report["new_NIH_checkpoint"])
            self.assertFalse(report["real_historical_publication_authenticated"])
            self.assertFalse(report["official_NIH_submission"])
            self.assertEqual(len(report["observed_browser_frames"]),
                             (report["world_actions"]+1)*len(CUTOFFS))
            self.assertGreaterEqual(len(report["actual_original_python_calls"]),
                                    len(report["observed_browser_frames"]))


if __name__=="__main__":
    unittest.main()
