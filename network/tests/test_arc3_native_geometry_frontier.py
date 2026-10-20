"""Finite safeguards for native all-frontier observation and time-delay control."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
import numpy as np
from work.arc3.native_geometry_frontier import PROTOCOL, DETOUR, OLD_SOURCE_SHA256, freeze
from work.arc3.native_geometry_frontier_verify import check

class SourceNativeFrontierTests(unittest.TestCase):
    def test_predeclared_roundtrip_and_original_pins(self):
        self.assertEqual(PROTOCOL,"AB_LS20_COMPLETE_REACHABLE_UNKNOWN_FRONTIER_V1")
        self.assertEqual(DETOUR,"121212")
        self.assertEqual(len(OLD_SOURCE_SHA256),4)
        self.assertTrue(all(len(v)==64 for v in OLD_SOURCE_SHA256.values()))
    def test_cannot_infer_without_two_authenticated_native_sources(self):
        with TemporaryDirectory() as root:
            with self.assertRaises((FileNotFoundError,ValueError)):
                freeze(Path(root),Path(root))
    def test_missing_new_raw_frame_source_is_not_verification(self):
        buf=BytesIO()
        np.savez_compressed(buf)
        buf.seek(0)
        with np.load(buf,allow_pickle=False) as archive:
            with self.assertRaises(ValueError):
                check({}, {}, archive)
    def test_existing_geometry_contract_preserves_color_five_and_wall(self):
        from work.arc3.native_geometry_unknown_edge import predict
        background=np.full((64,64),4,dtype=np.uint8)
        background[40:45,34:39]=5
        self.assertEqual(predict(background,(45,34),"1"),(40,34))
        background[40,34]=9
        self.assertEqual(predict(background,(45,34),"1"),(45,34))

if __name__=="__main__":
    unittest.main()
