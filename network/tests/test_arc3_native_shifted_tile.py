"""Source boundary checks for shifting LS20 special tile entry depth."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
import numpy as np
from work.arc3.native_shifted_tile_entry import (
    PROTOCOL,LOOPS,CONTROL_ACTION,PRIOR_SHA256,LOOP_SOURCE_SHA256,freeze
)
from work.arc3.native_shifted_tile_verify import evaluate
class ShiftedTileEntryTests(unittest.TestCase):
    def test_predeclared_shifts_and_controls(self):
        self.assertEqual(PROTOCOL,"AB_LS20_SHIFTED_SPECIAL_ENTRY_CLOCK_V1")
        self.assertEqual(LOOPS,("","12","1212","121212"))
        self.assertEqual([8+len(v) for v in LOOPS],[8,10,12,14])
        self.assertEqual(len(CONTROL_ACTION),3)
    def test_sources_pinned_before_native_trial(self):
        self.assertEqual(len(PRIOR_SHA256),4)
        self.assertEqual(len(LOOP_SOURCE_SHA256),4)
        self.assertTrue(all(len(v)==64 for v in (
            *PRIOR_SHA256.values(),*LOOP_SOURCE_SHA256.values()
        )))
    def test_no_source_cannot_freeze_predictions(self):
        with TemporaryDirectory() as d:
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(Path(d),Path(d))
    def test_no_original_native_pixels_no_conclusion(self):
        data=BytesIO()
        np.savez_compressed(data)
        data.seek(0)
        with np.load(data,allow_pickle=False) as frames:
            with self.assertRaises(ValueError):evaluate({}, {}, frames)
if __name__=="__main__":
    unittest.main()
