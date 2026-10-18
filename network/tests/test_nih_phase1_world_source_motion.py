"""Refute false source-motion results; native execution requires separate browser run."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_phase1_world_source_motion import (
    SCHEMA, PROFILES, TARGET, extend_world, witness_frame, verify_motion,
    run_source_motion,
)


def expected(visible, withheld, *, conflicts=None):
    static=sorted(set(visible)|set(withheld))
    return {
        "temporal_ids":list(visible),
        "future_leakage_ids":list(withheld),
        "static_snapshot_ids":static,
        "outside_validity_ids":[],
        "declared_conflicts":conflicts or [],
    }


def source_frame(turn, profile, visible, withheld, *, sha=None, conflicts=None):
    knowledge="2026-01-04" if turn<2 else "2026-01-06"
    return {
        "turn":turn,"profile":profile,"known_at":knowledge,
        "target_at":TARGET,"temporal_ids":list(visible),
        "future_leakage_ids":list(withheld),
        "static_snapshot_ids":sorted(set(visible)|set(withheld)),
        "outside_validity_ids":[],
        "declared_conflicts":conflicts or [],
        "source_program_sha256":"a"*64,
        "source_dataset_sha256":sha or {"original":"b"*64,
            "later-knowledge":"c"*64,"additional-conflict":"d"*64}[profile],
        "independent_source_oracle_agreed":True,
    }


def sample_sequence():
    all_rows=[]
    for turn in range(3):
        for profile in PROFILES:
            visible=["prior-note"]
            withheld=["delayed-result"]
            conflicts=[]
            if profile=="original" and turn>=2:
                visible=["delayed-result","prior-note"]
                withheld=[]
            if profile=="additional-conflict":
                visible=["prior-note","synthetic-extra-conflict"]
                conflicts=[["prior-note","synthetic-extra-conflict"]]
                if turn>=2:
                    visible=["delayed-result","prior-note","synthetic-extra-conflict"]
                    withheld=[]
            all_rows.append(source_frame(
                turn,profile,visible,withheld,conflicts=conflicts))
    return all_rows


class SourceMotionUnitTests(unittest.TestCase):
    def test_00_requires_exact_original_world_html(self):
        original='<script id="phase1-world-frontier-source"></script><script id="phase1-world-two-clock"></script></body>'
        amended=extend_world(original)
        self.assertIn("phase1SourceMotionProbe",amended)
        self.assertEqual(amended.count('id="phase1-source-motion"'),1)
        with self.assertRaises(ValueError):
            extend_world(amended)
        with self.assertRaises(ValueError):
            extend_world('<html></body>')

    def test_01_actual_frame_requires_full_native_source_disclosure(self):
        e=expected(["prior-note"],["delayed-result"])
        f={
            "turn":"0","profile":"original",
            "known":"2026-01-04","target":TARGET,
            "visible":"prior-note","withheld":"delayed-result",
            "static":"delayed-result,prior-note","outside":"",
            "conflicts":"[]","program_sha":"a"*64,
            "dataset_sha":"b"*64,"clinical":"NOT_EVALUATED",
        }
        result=witness_frame(
            f,turn=0,profile="original",known="2026-01-04",
            target=TARGET,expected=e,program_sha="a"*64,dataset_sha="b"*64)
        self.assertEqual(result["temporal_ids"],["prior-note"])
        for key,value in (
            ("visible",""),("withheld",""),("static","prior-note"),
            ("conflicts",'[["prior-note","delayed-result"]]'),
            ("dataset_sha","0"*64),("program_sha","0"*64),
            ("profile","later-knowledge"),("known","2026-01-06"),
            ("turn","1"),("clinical","EVALUATED"),
        ):
            tampered=dict(f);tampered[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):
                witness_frame(
                    tampered,turn=0,profile="original",known="2026-01-04",
                    target=TARGET,expected=e,program_sha="a"*64,dataset_sha="b"*64)

    def test_02_exact_three_profile_movement(self):
        rows=sample_sequence()
        self.assertEqual(len(rows),9)
        self.assertTrue(verify_motion(rows,world_actions=2,cutover=2))

    def test_03_reject_source_drift_leakage_conflict_misstatement(self):
        mutations=(
            (0,{"source_dataset_sha256":"0"*64}),
            (1,{"source_dataset_sha256":"0"*64}),
            (2,{"declared_conflicts":[]}),
            (5,{"temporal_ids":["prior-note"]}),
            (7,{"future_leakage_ids":[]}),
            (8,{"source_program_sha256":"e"*64}),
        )
        for i,change in mutations:
            rows=deepcopy(sample_sequence())
            rows[i].update(change)
            with self.subTest(i=i,change=change),self.assertRaises(ValueError):
                verify_motion(rows,world_actions=2,cutover=2)
        with self.assertRaises(ValueError):
            verify_motion(sample_sequence()[:-1],world_actions=2,cutover=2)
        with self.assertRaises(ValueError):
            verify_motion(sample_sequence(),world_actions=2,cutover=1)

    @unittest.skipUnless(os.environ.get("RUN_PHASE1_SOURCE_MOTION_NATIVE")=="1"
                         and importlib.util.find_spec("playwright") is not None,
                         "actual original source + Chromium evidence in dedicated workflow only")
    def test_04_native_original_world_source_controls(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            result=run_source_motion(
                data_dir=root/"native",output_dir=root/"evidence")
            self.assertEqual(result["schema"],SCHEMA)
            self.assertEqual(result["native_jobs"],12)
            self.assertTrue(result["actual_world_solved"])
            self.assertTrue(result["source_partition_verified"])
            self.assertTrue(result["original_journals_preserved"])
            self.assertFalse(result["new_native_job"])
            self.assertFalse(result["new_NIH_checkpoint"])
            self.assertFalse(result["official_NIH_submission"])
            self.assertEqual(len(result["actual_browser_source_frames"]),
                             (result["actual_world_actions"]+1)*len(PROFILES))
            self.assertGreaterEqual(len(result["independently_verified_original_python_calls"]),
                                    len(result["actual_browser_source_frames"]))


if __name__=="__main__":
    unittest.main()
