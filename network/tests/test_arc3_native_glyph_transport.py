"""Strict source contracts for native LS20 glyph transport (no REA/F3 mapping)."""
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from work.arc3.native_glyph_transport_prediction import (
    WORDS,SOURCES,PROTOCOL,glyph_position,infer_model,
)
from work.arc3.native_glyph_transport_verify import evaluate

class NativeGlyphTransportTests(unittest.TestCase):
    def test_predeclared_8_step_words_never_reuse_earlier_short_trials(self):
        self.assertEqual(len(WORDS),17)
        self.assertEqual(len(set(WORDS)),17)
        self.assertTrue(all(len(w)==8 and set(w)<=set("1234") for w in WORDS))
        self.assertEqual(len(SOURCES),3)
        self.assertEqual(PROTOCOL,"AB_LS20_NATIVE_GLYPH_TRANSPORT_V1")
    def test_raw_glyph_mask_is_exact_2_by_5_block(self):
        frame=np.zeros((64,64),dtype=np.uint8)
        frame[45:47,34:39]=12
        self.assertEqual(glyph_position(frame),(45,34))
        frame[42,30]=12
        with self.assertRaises(ValueError):glyph_position(frame)
        with self.assertRaises(ValueError):glyph_position(np.zeros((8,8),dtype=np.uint8))
    def test_corrupt_or_missing_training_source_is_not_a_model(self):
        with TemporaryDirectory() as root:
            with self.assertRaises((FileNotFoundError,ValueError)):
                infer_model(Path(root),Path(root))
    def test_absent_native_source_is_not_reported_success(self):
        from io import BytesIO
        from work.arc3.native_glyph_transport_prediction import PROTOCOL
        b=BytesIO()
        np.savez_compressed(b)
        b.seek(0)
        with np.load(b,allow_pickle=False) as npz:
            with self.assertRaises(ValueError):
                evaluate({"protocol":PROTOCOL,"new_words_committed_before_native_execution":list(WORDS)},
                         {"protocol":PROTOCOL},npz)

if __name__=="__main__":
    unittest.main()
