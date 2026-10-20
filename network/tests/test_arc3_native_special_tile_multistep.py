"""Negative evidence contracts for native A/B special-tile multistep hypotheses."""
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from work.arc3.native_special_tile_multistep import (
    PROTOCOL,SUFFIXES,RETURN_SUFFIXES,PRIOR_SHA256,freeze
)
from work.arc3.native_special_tile_multistep_verify import (
    predicted_trace_mask,evaluate
)

class NativeSpecialTileMultistepTests(unittest.TestCase):
    def test_source_locked_suffixes_are_distinct_and_require_three_histories(self):
        self.assertEqual(PROTOCOL,"AB_LS20_SPECIAL_TILE_MULTI_SUFFIX_V1")
        self.assertEqual(len(SUFFIXES),12)
        self.assertEqual(len(set(SUFFIXES)),12)
        self.assertEqual(RETURN_SUFFIXES,("12","21","34","43"))
        self.assertEqual(3*sum(map(len,SUFFIXES)),132)
        self.assertEqual(len(PRIOR_SHA256),4)
        self.assertTrue(all(len(s)==64 for s in PRIOR_SHA256.values()))
    def test_out_of_sample_trace_clock_is_pixel_exact_and_bounded(self):
        for t in range(9,15):
            pixels=predicted_trace_mask(t)
            self.assertEqual(pixels.shape,(64,64))
            self.assertEqual(int(np.count_nonzero(pixels)),84-2*t)
            self.assertTrue(np.all(pixels[61:63,13+t:55]))
            self.assertEqual(int(np.count_nonzero(pixels[:61])),0)
        for bad in (8,15,False,9.0):
            with self.assertRaises(ValueError):predicted_trace_mask(bad)
    def test_source_is_not_inferred_if_original_raw_record_missing(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(Path(folder))
    def test_missing_real_native_frames_cannot_fulfill_predictions(self):
        source=BytesIO()
        np.savez_compressed(source)
        source.seek(0)
        with np.load(source,allow_pickle=False) as archive:
            with self.assertRaises(ValueError):
                evaluate({}, {}, archive)
    def test_previous_falsified_passability_rule_is_not_redefined(self):
        from work.arc3.native_geometry_unknown_edge import predict
        source=np.full((64,64),4,dtype=np.uint8)
        source[30:35,19:24]=3
        source[30,19]=0
        self.assertEqual(predict(source,(30,24),"3"),(30,24))

if __name__=="__main__":
    unittest.main()
