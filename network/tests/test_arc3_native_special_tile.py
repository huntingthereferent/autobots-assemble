"""Fail-closed tests for source-preregistered official native special-tile successors."""
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from work.arc3.native_special_tile_successor import PREFIXES,ACTIONS,BASELINE_FRAME,BASELINE_GLYPH,SOURCE_SHA256,PROTOCOL,freeze
from work.arc3.native_special_tile_verify import examine,DELTA

class NativeSpecialTileTests(unittest.TestCase):
    def test_real_history_and_action_identity_is_fixed(self):
        self.assertEqual(PREFIXES,("11113323","11113332","33311413"))
        self.assertEqual(ACTIONS,"1234")
        self.assertEqual(BASELINE_GLYPH,(30,19))
        self.assertEqual(BASELINE_FRAME,"94380564157962f5deb754fc81783a1d")
        self.assertEqual(len(SOURCE_SHA256),4)
        self.assertTrue(all(len(d)==64 for d in SOURCE_SHA256.values()))
    def test_cannot_freeze_without_independent_original_raw_source(self):
        with TemporaryDirectory() as d:
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(Path(d),Path(d))
    def test_missing_native_raw_source_is_not_a_witness(self):
        b=BytesIO()
        np.savez_compressed(b)
        b.seek(0)
        with np.load(b,allow_pickle=False) as archive:
            with self.assertRaises(ValueError):
                examine({"protocol":PROTOCOL},{},archive)
    def test_native_cardinal_movement_envelope_is_separate(self):
        self.assertEqual(DELTA,{"1":(-5,0),"2":(5,0),"3":(0,-5),"4":(0,5)})
    def test_original_mixed_color_passability_failure_not_rewritten(self):
        from work.arc3.native_geometry_unknown_edge import predict
        terrain=np.full((64,64),4,dtype=np.uint8)
        terrain[30:35,19:24]=3
        terrain[30,19]=0
        terrain[30,20]=1
        self.assertEqual(predict(terrain,(30,24),"3"),(30,24))

if __name__=="__main__":
    unittest.main()
