"""Trial08 carrier checks: proposal remains separate from original unresolved source."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial08_handoff import carry
from work.ab_world.verify_construction import verify_receipt

PIN = "2e109a6fc8af766c2bcaa665f1a1898a1d5634bd"
UNKNOWN = "unresolved-multiple-contacts"


def sample():
    level = 1.3910443961
    ids = ["original-face-a", "original-face-b"]
    frames = []
    for index in range(31):
        t = round(index * .05, 9)
        frames.append({
            "time": t, "position": [12. - 2. * t, level],
            "velocity": [-2., 0.], "spin": 0., "orientation": 0.})
    return {
        "schema": "world-ab-two-contact-frictionless-candidate/v1",
        "geometry": {"surfaces": [{"id": ids[0]}, {"id": ids[1]}],
                     "junction": [8, 1.4], "topology": {"segments": 2}},
        "baseline_trial06_status": UNKNOWN,
        "original_trial06_friction": .4, "candidate_friction": 0.,
        "candidate_is_a_new_comparison_not_original_friction_physics": True,
        "simultaneous_frictional_manifold_solved": False,
        "arbitrary_junctions_solved": False,
        "real_material_behavior_verified": False,
        "original_blueprint_generated": False,
        "nearby_trial07_statuses": [
            {"offset": (n - 4) * .01, "status": "completed", "first_contact": ids[0]}
            for n in range(9)
        ],
        "candidate": {
            "source_ids": ids, "original_stop": UNKNOWN,
            "candidate_full_horizon_observed": True,
            "friction": 0., "normal_restitution": 1., "outgoing_spin": 0.,
            "collision_time": 1., "entry_y": level, "normal_impulses": [1., 1.],
            "incoming_velocity": [-2., 0.], "outgoing_velocity": [2., 0.],
            "frames": frames, "kinetic_energy_before": 2.,
            "kinetic_energy_after": 2.,
        }
    }


class Trial08CandidateCarrierTests(unittest.TestCase):
    def test_01_original_unknown_and_candidate_are_distinct(self):
        raw = sample()
        before = deepcopy(raw)
        result = carry(raw, PIN)
        self.assertEqual(raw, before)
        self.assertEqual(result["candidate_frames_carried"], 31)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 39)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 2)
        self.assertEqual(result["ledger_witness"]["relations_live"], 2)
        self.assertTrue(verify_receipt(result["ledger_receipt"])["valid"])
        objects = result["ledger_receipt"]["final"]["objects"]
        self.assertEqual(objects["original-unresolved-contact"]["status"], UNKNOWN)
        self.assertIsNone(objects["original-unresolved-contact"]["outgoing_impulse"])
        self.assertEqual(objects["frictionless-candidate"]["frame"]["time"], 1.5)
        self.assertFalse(result["original_response_known"])
        self.assertFalse(result["candidate_verified_by_adapter_as_physics"])

    def test_02_original_cannot_be_turned_into_candidate(self):
        for key, val in (
            ("baseline_trial06_status", "completed"),
            ("original_trial06_friction", 0.),
            ("candidate_friction", .4),
            ("candidate_is_a_new_comparison_not_original_friction_physics", False),
            ("simultaneous_frictional_manifold_solved", True),
        ):
            altered = sample()
            altered[key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                carry(altered, PIN)

    def test_03_candidate_trajectory_has_bounded_time_order(self):
        altered = sample()
        altered["candidate"]["frames"].pop()
        with self.assertRaisesRegex(ValueError, "31 sample"):
            carry(altered, PIN)
        altered = sample()
        altered["candidate"]["frames"][3]["time"] = .01
        with self.assertRaisesRegex(ValueError, "reordered"):
            carry(altered, PIN)
        altered = sample()
        altered["candidate"]["frames"][0]["position"][0] = 9
        with self.assertRaisesRegex(ValueError, "candidate start"):
            carry(altered, PIN)

    def test_04_negative_native_claim_and_source_identity_controls(self):
        altered = sample()
        altered["candidate"]["original_stop"] = "solved"
        with self.assertRaisesRegex(ValueError, "original stop"):
            carry(altered, PIN)
        altered = sample()
        altered["candidate"]["source_ids"].reverse()
        with self.assertRaisesRegex(ValueError, "source identities"):
            carry(altered, PIN)
        with self.assertRaisesRegex(ValueError, "exact source"):
            carry(sample(), "branch-name")
        altered = sample()
        altered["nearby_trial07_statuses"].pop()
        with self.assertRaisesRegex(ValueError, "Trial07 controls"):
            carry(altered, PIN)

    def test_05_independent_witness_rejects_altered_original_state(self):
        result = carry(sample(), PIN)
        altered = deepcopy(result["ledger_receipt"])
        altered["final"]["objects"]["original-unresolved-contact"]["status"] = "completed"
        with self.assertRaises(ValueError):
            verify_receipt(altered)
        altered = deepcopy(result["ledger_receipt"])
        altered["events"][-1]["effect"] = {"status": "invented-restitution"}
        with self.assertRaises(ValueError):
            verify_receipt(altered)


if __name__ == "__main__":
    unittest.main()
