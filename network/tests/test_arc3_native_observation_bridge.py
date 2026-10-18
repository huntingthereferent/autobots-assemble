"""Fail-closed boundaries for A/B access to independent native observations."""
import unittest
from io import BytesIO
import numpy as np
from work.arc3.native_observation_bridge import (
    PREFIXES,HISTORICAL_SUFFIXES,NEW_SUFFIXES,KIND,audit,frame_summary
)
from work.arc_like_maze.math import inverse_candidates
from work.arc_like_maze.inverse_observation_engine import Observation as F3Observation
from work.arc_like_maze.window_inverse_observation import Observation as FixedObservation
from work.arc_like_maze.window_rooted_observation import RootEqualityObservation

class NativeEvidenceTests(unittest.TestCase):
    def test_predeclared_new_suffixes_do_not_reuse_historical_suffixes(self):
        self.assertEqual((len(PREFIXES),len(HISTORICAL_SUFFIXES),len(NEW_SUFFIXES)),(3,6,4))
        self.assertFalse(set(NEW_SUFFIXES)&set(HISTORICAL_SUFFIXES))
        self.assertEqual(KIND,"ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION")

    def test_source_F3_bijectivity_survives_every_tested_suffix(self):
        laws=inverse_candidates()
        self.assertEqual(len(laws),9)
        for word in ("A","B","AA","BB","AB","BA"):
            self.assertTrue(all(w.apply("AB"+word)!=w.apply("BA"+word) for w in laws))

    def test_native_frame_hash_and_boolean_cannot_become_F3_evidence(self):
        with self.assertRaises(ValueError):
            F3Observation("AB",("88831de43456eb039e44d1fc7985c636",))
        with self.assertRaises(ValueError):
            FixedObservation("B",True)
        with self.assertRaises(ValueError):
            RootEqualityObservation(("12","21"),True)

    def test_missing_external_raw_data_cannot_pass_gate(self):
        buffer=BytesIO()
        np.savez_compressed(buffer)
        buffer.seek(0)
        with np.load(buffer,allow_pickle=False) as raw:
            with self.assertRaises(ValueError):audit({},raw,kind="historical")
            with self.assertRaises(ValueError):audit({
                "kind":KIND,"game":"ls20",
                "predeclared_prefixes":PREFIXES,
                "predeclared_suffixes":HISTORICAL_SUFFIXES,
                "all_runs_start_at_identical_root_frame":True,
                "comparisons":[]},raw,kind="historical")
            with self.assertRaises(ValueError):audit({},raw,kind="undocumented")

    def test_raw_colors_are_not_silently_reduced_modulo_three(self):
        grid=np.zeros((64,64),dtype=np.uint8)
        grid[0,0]=9
        grid[0,1]=12
        grid[0,2]=11
        first=frame_summary(grid)
        grid[0,0]=0
        second=frame_summary(grid)
        self.assertNotEqual(first["whole"],second["whole"])
        self.assertNotEqual(first["glyph"],second["glyph"])
        self.assertEqual(first["trace_cells"],second["trace_cells"])

if __name__=="__main__":unittest.main()
