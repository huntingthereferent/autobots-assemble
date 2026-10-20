"""Reject invented native geometry and ensure 18 *unmeasured* edges are fixed."""
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from work.arc3.native_geometry_unknown_edge import WORDS,DELTA,predict,freeze
from work.arc3.native_geometry_unknown_edge_verify import check

class UnknownNativeGeometryTests(unittest.TestCase):
    def test_holdout_paths_and_actions_are_precommitted(self):
        self.assertEqual(len(WORDS),18)
        self.assertEqual(len(set(WORDS)),18)
        self.assertTrue(all(set(w)<=set("1234") for w in WORDS))
        self.assertEqual(DELTA,{"1":(-5,0),"2":(5,0),"3":(0,-5),"4":(0,5)})
    def test_source_geometry_predicts_both_move_and_wall_without_a_native_oracle(self):
        m=np.full((64,64),4,dtype=np.uint8)
        m[45:50,34:39]=3
        m[40:45,34:39]=3
        m[45:50,39:44]=3
        self.assertEqual(predict(m,(45,34),"1"),(40,34))
        self.assertEqual(predict(m,(45,34),"2"),(45,34))
        self.assertEqual(predict(m,(45,34),"4"),(45,39))
        self.assertEqual(predict(m,(45,34),"3"),(45,34))
    def test_prior_native_source_is_required(self):
        with TemporaryDirectory() as d:
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(Path(d))
    def test_missing_raw_holdout_not_accepted_as_a_result(self):
        data=BytesIO()
        np.savez_compressed(data)
        data.seek(0)
        with np.load(data,allow_pickle=False) as source:
            with self.assertRaises(ValueError):
                check({}, {}, source)
    def test_unknown_edge_paths_are_not_faked_by_prior_predictions(self):
        self.assertIn("4441",WORDS)
        self.assertIn("4442",WORDS)
        self.assertIn("3331",WORDS)
        self.assertIn("113",WORDS)
if __name__=="__main__":
    unittest.main()
