"""Trial10 A/B carrier negative evidence, candidate multiplicity and provenance."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial10_handoff import carry, ANGLES, ROTATIONS, ACTIVE
from work.ab_world.verify_construction import verify_receipt

PIN = "e70f4fe80d6345e23771644bc5f86f4adcaea931"


def example():
    face_ids = ["original-A", "original-B"]
    cases = []
    for i, (rot, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        admissible_count = 2 if i < 26 else 1
        source_ids = [face_ids[0], face_ids[1] if rot == 0
                      else "controlled-B-" + str(rot)]
        alts = []
        for j, active in enumerate(ACTIVE):
            good = j < admissible_count
            frames = ([{"time": round(k * .05, 9),
                        "position": [12 - .1 * k, 1.4],
                        "velocity": [-2., 0.]}
                       for k in range(31)] if good else [])
            alts.append({
                "active_indices": list(active),
                "active_ids": [source_ids[k] for k in active],
                "status": "admissible-local-model" if good else "rejected-other-face-inward",
                "reason": None if good else "other-face-inward",
                "normal_impulses": [1., 0.] if good else None,
                "outgoing_velocity": [2., 0.] if good else None,
                "frames": frames,
            })
        cases.append({
            "original_index": i,
            "incoming_angle_degrees": angle,
            "surface_B_rotation_degrees": rot,
            "geometry_kind": ("original-source-geometry"
                              if rot == 0 else "controlled-geometry-not-original"),
            "source_ids": source_ids,
            "trial09_two_active_status": "rejected-unilateral",
            "physical_outcome_independently_observed": False,
            "alternatives": alts,
            "admissible_count": admissible_count,
            "classification": ("multiple-admissible" if admissible_count == 2
                               else "single-admissible"),
        })
    return {
        "schema": "world-ab-two-contact-active-set-enumeration/v1",
        "source_trial09_schema": "world-ab-two-contact-incidence-stress/v1",
        "original_source_geometry": {
            "surfaces": [{"id": face_ids[0]}, {"id": face_ids[1]}],
            "junction": [8, 1.4],
        },
        "angle_grid": list(ANGLES),
        "rotation_grid": list(ROTATIONS),
        "active_sets": [list(x) for x in ACTIVE],
        "original_trial09_two_active_counts": {
            "accepted-local-candidate": 0,
            "rejected-unilateral": 35,
            "rejected-not-incoming": 0,
            "rejected-constraint": 0,
        },
        "cases": cases,
        "counts": {
            "no-local-candidate": 0,
            "single-admissible": 9,
            "multiple-admissible": 26,
        },
        "trial09_rejected_cases_with_local_alternatives": 35,
        "original_trial06_friction": .4,
        "candidate_friction": 0.,
        "comparison_restitution": 1.,
        "simultaneous_multicontact_physics_uniquely_determined": False,
        "physical_active_contacts_observed": False,
        "sequential_impacts_temporally_witnessed": False,
        "original_source_surfaces_modified": False,
        "rotated_faces_are_original_source": False,
        "original_blueprint_generated": False,
        "earth_material_equivalence": False,
    }


class Trial10CarrierTests(unittest.TestCase):
    def test_01_retains_all_alternatives_and_multiple_not_selected(self):
        raw = example()
        untouched = deepcopy(raw)
        output = carry(raw, PIN)
        self.assertEqual(raw, untouched)
        self.assertEqual(output["cases"], 35)
        self.assertEqual(output["alternatives"], 105)
        self.assertEqual(output["admissible_alternatives"], 61)
        self.assertEqual(output["rejected_alternatives"], 44)
        self.assertEqual(output["candidate_frames_carried"], 1891)
        self.assertEqual(output["classifications"]["multiple-admissible"], 26)
        self.assertEqual(output["ledger_witness"]["steps_verified"], 2279)
        self.assertEqual(output["ledger_witness"]["objects_live"], 142)
        self.assertEqual(output["ledger_witness"]["relations_live"], 141)
        self.assertEqual(output["ledger_witness"]["observations_recorded"], 105)
        self.assertFalse(output["physical_outcome_chosen"])
        self.assertFalse(output["original_frictional_contact_solved"])
        self.assertTrue(verify_receipt(output["ledger_receipt"])["valid"])

    def test_02_rejected_branch_cannot_gain_unobserved_motion(self):
        data = example()
        data["cases"][0]["alternatives"][2]["frames"] = [
            {"time": 0, "position": [8, 1.4], "velocity": [1, 0]}]
        with self.assertRaisesRegex(ValueError, "invented movement"):
            carry(data, PIN)
        data = example()
        data["cases"][0]["alternatives"][2]["outgoing_velocity"] = [2, 0]
        with self.assertRaisesRegex(ValueError, "invented movement"):
            carry(data, PIN)

    def test_03_all_active_sets_preserved_in_source_order(self):
        data = example()
        data["cases"][0]["alternatives"].reverse()
        with self.assertRaisesRegex(ValueError, "active-set identity"):
            carry(data, PIN)
        data = example()
        data["cases"][0]["admissible_count"] = 1
        with self.assertRaisesRegex(ValueError, "admissibility count"):
            carry(data, PIN)
        data = example()
        data["cases"][0]["alternatives"][2]["status"] = "admissible-local-model"
        with self.assertRaises(ValueError):
            carry(data, PIN)

    def test_04_original_material_claims_rejected(self):
        data = example()
        data["physical_active_contacts_observed"] = True
        with self.assertRaisesRegex(ValueError, "unsupported physical claim"):
            carry(data, PIN)
        data = example()
        data["cases"][0]["physical_outcome_independently_observed"] = True
        with self.assertRaisesRegex(ValueError, "actual observed material"):
            carry(data, PIN)
        data = example()
        data["cases"][0]["source_ids"][0] = "made-up"
        with self.assertRaises(ValueError):
            carry(data, PIN)
        with self.assertRaisesRegex(ValueError, "exact original source"):
            carry(example(), "unversioned-branch")

    def test_05_invalid_candidate_frame_and_duplicate_counts(self):
        data = example()
        data["cases"][0]["alternatives"][0]["frames"][8]["time"] = .01
        with self.assertRaisesRegex(ValueError, "out of sequence"):
            carry(data, PIN)
        data = example()
        data["counts"]["multiple-admissible"] = 35
        with self.assertRaisesRegex(ValueError, "classification totals"):
            carry(data, PIN)

    def test_06_independent_witness_detects_promoted_solved_contact(self):
        record = carry(example(), PIN)["ledger_receipt"]
        changed = deepcopy(record)
        changed["final"]["objects"]["original-frictional-contact"]["state"] = "SOLVED"
        with self.assertRaises(ValueError):
            verify_receipt(changed)
        changed = deepcopy(record)
        changed["events"][-1]["effect"] = {"status": "physical-outcome-selected"}
        with self.assertRaises(ValueError):
            verify_receipt(changed)


if __name__ == "__main__":
    unittest.main()
