"""Source-verification and negative tests for composed native unknown A/B edges."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from io import BytesIO
import numpy as np
from work.arc3.native_multi_edge_composition import PROTOCOL,FRONTIER_SHA256,freeze
from work.arc3.native_multi_edge_verify import verify

class NativeMultipleUnknownEdgesTests(unittest.TestCase):
    def test_source_pinning(self):
        self.assertEqual(PROTOCOL,"AB_LS20_MULTINEW_EDGE_COMPOSITION_V1")
        self.assertEqual(len(FRONTIER_SHA256),4)
        self.assertTrue(all(len(v)==64 for v in FRONTIER_SHA256.values()))
    def test_no_source_no_predictions(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(root,root,root)
    def test_no_new_raw_pixels_no_success(self):
        data=BytesIO()
        np.savez_compressed(data)
        data.seek(0)
        with np.load(data,allow_pickle=False) as archive:
            with self.assertRaises(ValueError):
                verify({}, {}, archive)
    def test_original_terrain_rule_is_unchanged(self):
        from work.arc3.native_geometry_unknown_edge import predict
        original=np.full((64,64),4,dtype=np.uint8)
        original[40:45,34:39]=3
        self.assertEqual(predict(original,(45,34),"1"),(40,34))
        original[42,36]=9
        self.assertEqual(predict(original,(45,34),"1"),(45,34))

if __name__=="__main__":
    unittest.main()
