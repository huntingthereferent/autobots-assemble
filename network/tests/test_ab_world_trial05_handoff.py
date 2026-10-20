"""Ledger handoff controls: these tests do not substitute for source-native tests."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial05_handoff import carry
from work.ab_world.verify_construction import verify_receipt

SHA = "7" * 40


def example():
    def row(level, face, velocity):
        return {"initial": [12, level], "source_first_contact": face,
                "outgoing_velocity": velocity, "hit_time": 1.5}
    return {
        "schema": "world-ab-connected-receiver-routing/v1",
        "geometry": {"surfaces": [{"id": "face-a"}, {"id": "face-b"}],
                     "junction": [2.0, 1.0], "topology": {"connected_components": 1}},
        "probe_y_levels": [1.0, 2.0],
        "baseline_first_face_only": [row(1.0, "face-a", [1, 0]),
                                     row(2.0, "face-a", [1, 0])],
        "assembled_two_faces": [row(1.0, "face-b", [0, 1]),
                                row(2.0, "face-a", [1, 0])],
        "route_changed_probe_levels": [1.0],
    }


class WorldTrial05HandoffTests(unittest.TestCase):
    def test_01_preserves_original_baseline_and_changed_path(self):
        original = example()
        snapshot = deepcopy(original)
        result = carry(original, SHA)
        self.assertEqual(original, snapshot)
        self.assertEqual(result["difference_levels"], [1.0])
        self.assertEqual(result["ledger_witness"]["steps_verified"], 11)
        self.assertEqual(result["world_receipt"]["final"]["comparisons"][
            "baseline-contrast-001"]["result"], "DIFFERENT")
        self.assertEqual(result["world_receipt"]["final"]["comparisons"][
            "baseline-contrast-002"]["result"], "MATCH")
        self.assertTrue(verify_receipt(result["world_receipt"])["valid"])
        self.assertFalse(result["physical_measurement_verified"])
        self.assertFalse(result["source_authenticated_by_this_adapter"])

    def test_02_rejects_false_changed_route_claim(self):
        source = example()
        source["route_changed_probe_levels"] = []
        with self.assertRaisesRegex(ValueError, "changed routes"):
            carry(source, SHA)

    def test_03_rejects_misaligned_native_record(self):
        source = example()
        source["assembled_two_faces"][0]["initial"] = [5, 5]
        with self.assertRaisesRegex(ValueError, "share the initial"):
            carry(source, SHA)

    def test_04_rejects_bad_source_identity_and_missing_rows(self):
        with self.assertRaises(ValueError):
            carry(example(), "branch-name")
        source = example()
        source["assembled_two_faces"].pop()
        with self.assertRaisesRegex(ValueError, "do not align"):
            carry(source, SHA)

    def test_05_rejects_tampered_carrier(self):
        result = carry(example(), SHA)
        altered = deepcopy(result["world_receipt"])
        altered["events"][4]["effect"] = {"status": "NOT-A-REAL-MOVE"}
        with self.assertRaises(ValueError):
            verify_receipt(altered)


if __name__ == "__main__":
    unittest.main()
