"""Negative controls for real original-world two-clock research experiment.

Unit fixtures establish rejection behaviors, never replace native Chromium or
independent subprocess execution of the emitted temporal_query.py.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import importlib.util
import os

from systems.workspace.nih_phase1_world_two_clock import (
    TARGETS, SCHEMA, check_axes, extend_world_html, run_two_clock,
)


def sample_grid():
    frames=[]
    for turn in range(3):
        knowledge="2026-01-06" if turn>=2 else "2026-01-04"
        for target in TARGETS:
            if target=="2026-01-02":
                visible=["prior-note"]
                hidden=[]
                static=["prior-note"]
                outside=["delayed-result"]
            elif target=="2026-01-04":
                if turn<2:
                    visible=["prior-note"]
                    hidden=["delayed-result"]
                else:
                    visible=["delayed-result","prior-note"]
                    hidden=[]
                static=["delayed-result","prior-note"]
                outside=[]
            else:
                visible=[]
                hidden=[]
                static=[]
                outside=["delayed-result","prior-note"]
            frames.append({
                "turn":turn,"known_at":knowledge,"target_at":target,
                "visible_ids":visible,"future_withheld_ids":hidden,
                "static_ids":static,"outside_validity_ids":outside,
                "source_program_sha256":"a"*64,
                "independent_scope_agreement":True,
            })
    return frames


class OriginalWorldTwoClockTests(unittest.TestCase):
    def test_00_requires_existing_original_frontier_html(self):
        source='<html><script id="native-temporal-client"></script><script id="phase1-world-frontier-source"></script></body>'
        wrapped=extend_world_html(source)
        self.assertEqual(wrapped.count("id=\"phase1-world-two-clock\""),1)
        self.assertIn("phase1OriginalPythonProbe",wrapped)
        self.assertIn("#phase1-frontier",wrapped)
        with self.assertRaises(ValueError):
            extend_world_html(wrapped)
        with self.assertRaises(ValueError):
            extend_world_html('<html><script id="native-temporal-client"></script></body>')

    def test_01_complete_grid_known_and_valid_clocks_verified(self):
        rows=sample_grid()
        self.assertTrue(check_axes(rows,plan_length=2,cutover=2))
        self.assertEqual(len(rows),9)
        self.assertEqual(len({x["target_at"] for x in rows}),3)
        self.assertEqual(len({x["known_at"] for x in rows}),2)

    def test_02_reject_missing_duplicate_or_renamed_frames(self):
        rows=sample_grid()
        with self.assertRaises(ValueError):
            check_axes(rows[:-1],plan_length=2,cutover=2)
        fake=deepcopy(rows)
        fake[1]["target_at"]="2026-01-02"
        with self.assertRaises(ValueError):
            check_axes(fake,plan_length=2,cutover=2)
        fake=deepcopy(rows)
        fake[1]["source_program_sha256"]="b"*64
        with self.assertRaises(ValueError):
            check_axes(fake,plan_length=2,cutover=2)

    def test_03_reject_missing_validity_partition_or_future_leakage(self):
        cases=(
            (1,{"static_ids":["prior-note"]}),
            (0,{"outside_validity_ids":[]}),
            (1,{"visible_ids":["delayed-result","prior-note"]}),
            (7,{"future_withheld_ids":["delayed-result"]}),
            (8,{"static_ids":["prior-note"]}),
            (2,{"static_ids":["delayed-result","prior-note"]}),
        )
        for index,change in cases:
            fake=deepcopy(sample_grid())
            fake[index].update(change)
            with self.subTest(index=index,change=change),self.assertRaises(ValueError):
                check_axes(fake,plan_length=2,cutover=2)

    def test_04_reject_known_time_forgery_and_clock_regressions(self):
        for index,known in ((0,"2026-01-06"),(3,"2026-01-07"),
                            (6,"2026-01-03"),(8,"2026-01-03")):
            fake=deepcopy(sample_grid())
            fake[index]["known_at"]=known
            with self.subTest(index=index,known=known),self.assertRaises(ValueError):
                check_axes(fake,plan_length=2,cutover=2)
        with self.assertRaises(ValueError):
            check_axes(sample_grid(),plan_length=2,cutover=1)

    @unittest.skipUnless(os.environ.get("RUN_PHASE1_TWO_CLOCK_NATIVE")=="1" and
                         importlib.util.find_spec("playwright") is not None,
                         "original twelve-job plus live dual-clock Chromium run is dedicated CI only")
    def test_05_actual_world_controls_trigger_original_emitted_python(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            result=run_two_clock(data_dir=root/"native",output_dir=root/"receipts")
            self.assertEqual(result["schema"],SCHEMA)
            self.assertEqual(result["original_native_jobs"],12)
            self.assertTrue(result["both_clock_dimensions_observed"])
            self.assertTrue(result["independent_source_oracle_agreed"])
            self.assertTrue(result["preserved_original_native_ancestry"])
            self.assertFalse(result["native_worker_created"])
            self.assertFalse(result["new_cp_witnessed"])
            self.assertFalse(result["official_NIH_submission"])
            self.assertEqual(len(result["browser_target_query_frames"]),
                             (result["world_actions"]+1)*len(TARGETS))
            self.assertGreaterEqual(result["actual_original_python_probe_calls"],
                                    len(result["browser_target_query_frames"]))


if __name__=="__main__":
    unittest.main()
