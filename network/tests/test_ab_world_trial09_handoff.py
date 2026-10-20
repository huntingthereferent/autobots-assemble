"""Trial09 carrier controls: geometry identity, rejection, time-order and tamper."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial09_handoff import (
    ANGLES, OFFSETS, ACCEPTED, carry)
from work.ab_world.verify_construction import verify_receipt

PIN = "e1679c4dd7b810e0539bc619ace32f0fea67814d"


def sample():
    faces = [{"id": "original-A"}, {"id": "original-B"}]
    cases = []
    for offset in OFFSETS:
        for angle in ANGLES:
            accepted = offset == 0 and angle == 0
            controlled = offset != 0
            surface_b = ({
                "id": "controlled-B-" + str(offset), "source_parent_id": "original-B",
                "geometry_role": "explicit-rotated-counterfactual",
                "rotation_degrees": offset
            } if controlled else deepcopy(faces[1]))
            frames = ([{
                "time": round(i * .05, 9),
                "position": [12 - 2 * i * .05, 1.4],
                "velocity": [-2., 0.]
            } for i in range(31)] if accepted else [])
            cases.append({
                "incoming_angle_degrees": angle,
                "surface_B_rotation_degrees": offset,
                "geometry_kind": "controlled-geometry-not-original"
                                 if controlled else "original-source-geometry",
                "surfaces": [deepcopy(faces[0]), surface_b],
                "status": ACCEPTED if accepted else "rejected-unilateral",
                "reason": None if accepted else "contact requires inactive impulse",
                "candidate": {"normal_impulses": [1., 1.]}
                             if accepted else None,
                "frames": frames,
            })
    return {
        "schema": "world-ab-two-contact-incidence-stress/v1",
        "original_source_geometry": {
            "surfaces": faces, "junction": [8.0, 1.4],
            "topology": {"segments": 2}},
        "original_trial07_contact": {"source_ids": ["original-A", "original-B"],
                                     "entry_y": 1.391},
        "original_trial08_outgoing": [2., 0.],
        "incoming_angle_grid": list(ANGLES),
        "surface_rotation_grid": list(OFFSETS),
        "speed": 2., "controlled_contact_lead": .35,
        "original_trial06_friction": .4, "candidate_friction": 0.,
        "original_surface_modified": False,
        "rotated_faces_are_original_source": False,
        "general_two_contact_physics_proven": False,
        "frictional_manifold_solved": False,
        "real_material_equivalence": False,
        "original_blueprint_generated": False,
        "cases": cases,
        "counts": {
            "accepted-local-candidate": 1,
            "rejected-unilateral": 34,
            "rejected-not-incoming": 0,
            "rejected-constraint": 0,
        },
    }


class OriginalSourceStressCarrier(unittest.TestCase):
    def test_01_holds_all_35_cases_and_source_rejections(self):
        example = sample()
        before = deepcopy(example)
        result = carry(example, PIN)
        self.assertEqual(example, before)
        self.assertEqual(result["stress_cases"], 35)
        self.assertEqual(result["candidate_frames_carried"], 31)
        self.assertEqual(result["outcome_counts"]["rejected-unilateral"], 34)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 142)
        self.assertEqual(result["ledger_witness"]["objects_live"], 39)
        self.assertEqual(result["ledger_witness"]["relations_live"], 37)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 35)
        self.assertTrue(verify_receipt(result["ledger_receipt"])["valid"])
        self.assertFalse(result["native_physics_verified_by_adapter"])
        self.assertFalse(result["physical_materials_verified"])

    def test_02_rejected_model_never_acquires_a_trajectory(self):
        candidate = sample()
        candidate["cases"][0]["frames"] = [{"time": 0., "position": [2, 2]}]
        with self.assertRaisesRegex(ValueError, "fabricated motion"):
            carry(candidate, PIN)
        candidate = sample()
        candidate["cases"][0]["candidate"] = {"normal_impulses": [1, 1]}
        with self.assertRaisesRegex(ValueError, "fabricated motion"):
            carry(candidate, PIN)

    def test_03_original_vs_controlled_source_faces_not_interchanged(self):
        test = sample()
        test["cases"][0]["surfaces"][1]["source_parent_id"] = "different"
        with self.assertRaisesRegex(ValueError, "promoted to original"):
            carry(test, PIN)
        test = sample()
        original = next(c for c in test["cases"]
                        if c["surface_B_rotation_degrees"] == 0)
        original["surfaces"][1]["id"] = "forged"
        with self.assertRaisesRegex(ValueError, "original case replaced"):
            carry(test, PIN)

    def test_04_accepted_control_requires_every_bounded_sample(self):
        test = sample()
        actual = next(c for c in test["cases"] if c["status"] == ACCEPTED)
        actual["frames"].pop()
        with self.assertRaisesRegex(ValueError, "31 frames"):
            carry(test, PIN)
        test = sample()
        actual = next(c for c in test["cases"] if c["status"] == ACCEPTED)
        actual["frames"][5]["time"] = .01
        with self.assertRaisesRegex(ValueError, "reordered"):
            carry(test, PIN)

    def test_05_counts_and_statuses_cannot_be_promoted(self):
        test = sample()
        test["counts"]["accepted-local-candidate"] = 35
        with self.assertRaisesRegex(ValueError, "counts rewritten"):
            carry(test, PIN)
        test = sample()
        test["frictional_manifold_solved"] = True
        with self.assertRaisesRegex(ValueError, "unsupported claim"):
            carry(test, PIN)
        test = sample()
        test["cases"][10]["status"] = "accepted-local-candidate"
        with self.assertRaises(ValueError):
            carry(test, PIN)

    def test_06_source_pin_and_independent_record_are_strict(self):
        with self.assertRaisesRegex(ValueError, "exact source"):
            carry(sample(), "original-trial09")
        record = carry(sample(), PIN)["ledger_receipt"]
        broken = deepcopy(record)
        broken["events"][-1]["effect"] = {"status": "ACCEPT_ALL"}
        with self.assertRaises(ValueError):
            verify_receipt(broken)
        broken = deepcopy(record)
        broken["final"]["objects"]["unresolved-original-contact"]["status"] = "solved"
        with self.assertRaises(ValueError):
            verify_receipt(broken)


if __name__ == "__main__":
    unittest.main()
