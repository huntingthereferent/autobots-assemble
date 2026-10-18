import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from work.arc3.native_trace_factor_prediction import NATIVE_WORDS,HELD_OUT_DEPTHS,predicted_trace,verify_training_archive
from work.arc3.native_trace_factor_verify import evaluate

class NativeTraceTests(unittest.TestCase):
    def test_frozen_holdout(self):
        self.assertEqual((len(NATIVE_WORDS),len(set(NATIVE_WORDS)),HELD_OUT_DEPTHS),(16,16,(5,6)))
        self.assertTrue(all(len(w) in (5,6) and set(w)<=set("1234") for w in NATIVE_WORDS))
    def test_trace_exact_pixels(self):
        for t in range(7):
            self.assertEqual(int(np.count_nonzero(predicted_trace(t))),84-2*t)
            self.assertTrue(np.all(predicted_trace(t)[61:63,13+t:55]))
        for value in (-1,7,True,6.0):
            with self.assertRaises(ValueError):predicted_trace(value)
    def test_incomplete_source_refused(self):
        with TemporaryDirectory() as d:
            path=Path(d)/"bad.npz"
            np.savez_compressed(path,bad=np.zeros((5,64,64),dtype=np.uint8))
            with self.assertRaises(ValueError):verify_training_archive(path)
        b=BytesIO()
        np.savez_compressed(b)
        b.seek(0)
        with np.load(b,allow_pickle=False) as source:
            with self.assertRaises(ValueError):evaluate({}, {}, source)
if __name__=="__main__":unittest.main()
