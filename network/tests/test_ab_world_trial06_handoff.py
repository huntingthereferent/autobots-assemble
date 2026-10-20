"""A/B Trial06 handoff tests: contract/negative controls, not physics proof."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial06_handoff import carry
from work.ab_world.verify_construction import verify_receipt

PIN = "7" * 40


def trajectory(level, last_x=10.0):
    frames = [
        {"time": 0, "position": [12, level], "velocity": [-2, 0],
         "spin": 0, "orientation": 0},
        {"time": 1, "position": [last_x, level], "velocity": [-2, 0],
         "spin": 0, "orientation": 0},
    ]
    return {"entry_y": level, "status": "completed", "frames": frames,
            "contacts": [], "first_contact": None, "exit": deepcopy(frames[-1]),
            "minimum_frame_clearance": 1, "unresolved": None}


def sample():
    original = [trajectory(1.0), trajectory(2.0)]
    changed = [trajectory(1.0, 11.0), trajectory(2.0)]
    return {"schema": "world-ab-connected-continuous-junction/v1",
            "geometry": {"surfaces": [{"id": "original-face-a"}, {"id": "original-face-b"}],
                         "junction": [8, 1.5],
                         "topology": {"connected_components": 1}},
            "probe_levels": [1.0, 2.0],
            "baseline_finite_capsule": original,
            "connected_finite_capsule": changed,
            "completed_cases": 2, "unresolved_cases": []}


class ContinuousMovementCarrierTests(unittest.TestCase):
    def test_01_preserves_sampled_motion_and_difference(self):
        original = sample()
        old = deepcopy(original)
        result = carry(original, PIN)
        self.assertEqual(original, old)
        self.assertEqual(result["trajectories_carried"], 4)
        self.assertEqual(result["sampled_frames_carried"], 8)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 17)
        self.assertEqual(result["difference_probe_levels"], [1.0])
        comparisons = result["world_receipt"]["final"]["comparisons"]
        self.assertEqual(comparisons["source-path-contrast-001"]["result"], "DIFFERENT")
        self.assertEqual(comparisons["source-path-contrast-002"]["result"], "MATCH")
        self.assertTrue(verify_receipt(result["world_receipt"])["valid"])
        self.assertFalse(result["native_dynamics_verified_by_this_adapter"])
        self.assertFalse(result["physical_measurements_verified"])

    def test_02_reported_source_cannot_hide_unresolved_path(self):
        trial = sample()
        trial["connected_finite_capsule"][0]["status"] = "unresolved-multiple-contacts"
        trial["completed_cases"] = 1
        with self.assertRaisesRegex(ValueError, "unresolved contact"):
            carry(trial, PIN)
        trial["unresolved_cases"] = [{"entry_y": 1.0, "status": "unresolved-multiple-contacts"}]
        receipt = carry(trial, PIN)
        self.assertEqual(receipt["connected_unresolved"], trial["unresolved_cases"])
        self.assertEqual(receipt["connected_completed"], 1)

    def test_03_bad_source_identity_and_misaligned_probe_fail(self):
        with self.assertRaises(ValueError):
            carry(sample(), "main")
        trial = sample()
        trial["connected_finite_capsule"].pop()
        with self.assertRaisesRegex(ValueError, "unaligned"):
            carry(trial, PIN)
        trial = sample()
        trial["connected_finite_capsule"][0]["frames"][0]["position"] = [8, 9]
        with self.assertRaisesRegex(ValueError, "different initial"):
            carry(trial, PIN)

    def test_04_frame_chronology_exit_and_contact_identity(self):
        trial = sample()
        trial["baseline_finite_capsule"][0]["frames"][-1]["time"] = -1
        with self.assertRaisesRegex(ValueError, "chronology"):
            carry(trial, PIN)
        trial = sample()
        trial["connected_finite_capsule"][1]["exit"]["position"] = [3, 2]
        with self.assertRaisesRegex(ValueError, "exit"):
            carry(trial, PIN)
        trial = sample()
        trial["connected_finite_capsule"][1]["first_contact"] = "phantom"
        with self.assertRaisesRegex(ValueError, "first contact"):
            carry(trial, PIN)

    def test_05_tampered_continuation_not_witnessed(self):
        receipt = carry(sample(), PIN)["world_receipt"]
        forged = deepcopy(receipt)
        forged["events"][5]["effect"] = {"status": "fake-completed"}
        with self.assertRaises(ValueError):
            verify_receipt(forged)


if __name__ == "__main__":
    unittest.main()
