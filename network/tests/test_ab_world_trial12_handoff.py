"""Independent A/B record controls for Trial12 finite candidate movements."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial12_handoff import (
    ANGLES, ROTATIONS, SPINS, FRICTIONS, carry)
from work.ab_world.verify_construction import verify_receipt

PIN = "790f81b02a03c79cab8d502dd6e43cf65c29ba4e"
GOOD = "admissible-single-active"
BAD = "rejected-other-face-inward"


def sample():
    original = ["source-A", "source-B"]
    cases = []
    for i, (rotation, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        ids = [original[0], original[1] if rotation == 0
               else "controlled-B-" + str(rotation)]
        options = []
        for k, (spin, mu, face) in enumerate(
                (w, m, f) for w in SPINS for m in FRICTIONS for f in (0, 1)):
            good = k == 0
            frames = [
                {"time": round(t*.05, 9),
                 "position": [12-t*.1, 1.4],
                 "velocity": [-2., 0.],
                 "spin": spin, "orientation": spin*t*.05}
                for t in range(31)
            ] if good else []
            options.append({
                "face_index": face, "face_id": ids[face],
                "friction_coefficient": mu, "incoming_spin": spin,
                "incoming_velocity": [-2., 0.], "normal": [1., 0.],
                "normal_impulse": 2., "tangential_impulse": 0.,
                "incoming_normal_speed": -2.,
                "incoming_tangential_slip": 0.,
                "outgoing_tangential_slip": 0.,
                "slip_regime": "stick-candidate",
                "outgoing_velocity": [2., 0.], "outgoing_spin": spin,
                "energy_before": 2., "energy_after": 2.,
                "friction_cone_satisfied": True,
                "status": GOOD if good else BAD,
                "reason": None if good else "other-face-inward",
                "frames": frames, "finite_horizon_verified": good,
            })
        cases.append({
            "original_index": i, "incoming_angle_degrees": angle,
            "surface_B_rotation_degrees": rotation,
            "geometry_kind": ("original-source-geometry" if rotation == 0
                              else "controlled-geometry-not-original"),
            "source_ids": ids,
            "original_trial10_classification": "multiple-admissible",
            "original_trial09_two_active_status": "rejected-unilateral",
            "options": options,
            "actual_active_contact_observed": False,
            "real_collision_outcome_selected": False,
        })
    by_parameter = []
    for spin in SPINS:
        for mu in FRICTIONS:
            n = 35 if spin == 0 and mu == 0 else 0
            by_parameter.append({
                "starting_spin": spin, "friction_coefficient": mu,
                "accepted_single_face_candidates": n,
                "cases_with_any_admissible_single_face": n,
                "cases_with_two_admissible_single_faces": 0,
                "cases_with_no_admissible_single_face": 35 - n,
            })
    return {
        "schema": "world-ab-single-active-friction-spin-controls/v1",
        "source_trial09_schema": "world-ab-two-contact-incidence-stress/v1",
        "source_trial10_schema": "world-ab-two-contact-active-set-enumeration/v1",
        "original_source_geometry": {
            "surfaces": [{"id": original[0]}, {"id": original[1]}]},
        "original_trial10_counts": {
            "multiple-admissible": 26, "single-admissible": 9,
            "no-local-candidate": 0},
        "original_trial09_two_active_counts": {},
        "incoming_angle_grid": list(ANGLES),
        "source_rotation_grid": list(ROTATIONS),
        "friction_grid": list(FRICTIONS),
        "starting_spin_grid": list(SPINS),
        "restitution": 1., "radius": .25, "inertia": .02,
        "cases": cases, "by_parameter": by_parameter,
        "original_trial06_friction": .4,
        "original_trial06_two_contact_solver_unchanged": True,
        "frictional_simultaneous_two_contact_manifold_solved": False,
        "actual_active_contact_observed": False,
        "sequential_real_contacts_measured": False,
        "real_material_equivalence": False,
        "physical_blueprint_generated": False,
    }


class Trial12CarrierTests(unittest.TestCase):
    def test_01_finited_source_pages_and_real_rejections_preserved(self):
        input_data = sample()
        copy = deepcopy(input_data)
        out = carry(input_data, PIN)
        self.assertEqual(input_data, copy)
        self.assertEqual(out["cases"], 35)
        self.assertEqual(out["source_candidates"], 420)
        self.assertEqual(out["admissible_candidates"], 35)
        self.assertEqual(out["rejected_candidates"], 385)
        self.assertEqual(out["candidate_frames"], 1085)
        self.assertEqual(out["ledger_witness"]["pages_verified"], 35)
        self.assertEqual(out["ledger_witness"]["observations_recorded"], 420)
        self.assertEqual(out["ledger_witness"]["steps_verified"], 2520)
        self.assertTrue(out["ledger_witness"]["valid"])
        self.assertFalse(out["physical_winner_selected"])
        self.assertFalse(out["original_frictional_multicontact_solved"])
        self.assertTrue(verify_receipt(out["ledger_pages"][0]["receipt"])["valid"])
        self.assertEqual([p["case"] for p in out["ledger_pages"]], list(range(35)))

    def test_02_finite_candidate_cannot_gain_or_lose_frames(self):
        x = sample()
        x["cases"][0]["options"][0]["frames"].pop()
        with self.assertRaisesRegex(ValueError, "full finite trajectory"):
            carry(x, PIN)
        x = sample()
        x["cases"][0]["options"][0]["frames"][2]["spin"] = "NO"
        with self.assertRaisesRegex(ValueError, "spin or motion frame"):
            carry(x, PIN)
        x = sample()
        x["cases"][0]["options"][1]["frames"] = [
            {"time": 0., "position": [5., 5.]}]
        with self.assertRaisesRegex(ValueError, "fictional completed motion"):
            carry(x, PIN)

    def test_03_prior_two_contact_and_material_unknown_remain_unknown(self):
        x = sample()
        x["original_trial06_two_contact_solver_unchanged"] = False
        with self.assertRaisesRegex(ValueError, "two-contact source"):
            carry(x, PIN)
        x = sample()
        x["real_material_equivalence"] = True
        with self.assertRaisesRegex(ValueError, "unsupported real-world"):
            carry(x, PIN)
        x = sample()
        x["cases"][0]["real_collision_outcome_selected"] = True
        with self.assertRaisesRegex(ValueError, "promoted"):
            carry(x, PIN)

    def test_04_original_faces_and_candidate_model_identity_never_substituted(self):
        x = sample()
        x["cases"][0]["source_ids"][0] = "forged"
        with self.assertRaisesRegex(ValueError, "controlled geometry"):
            carry(x, PIN)
        x = sample()
        x["cases"][0]["options"][0]["face_id"] = "forged"
        with self.assertRaisesRegex(ValueError, "active face"):
            carry(x, PIN)
        x = sample()
        x["friction_grid"][0] = .8
        with self.assertRaisesRegex(ValueError, "experiment grid"):
            carry(x, PIN)
        with self.assertRaisesRegex(ValueError, "exact original source"):
            carry(sample(), "branch-name")

    def test_05_conclusion_and_summary_mutants(self):
        x = sample()
        x["cases"][0]["options"][1]["finite_horizon_verified"] = True
        with self.assertRaisesRegex(ValueError, "fictional completed motion"):
            carry(x, PIN)
        x = sample()
        x["by_parameter"][0]["accepted_single_face_candidates"] = 420
        with self.assertRaisesRegex(ValueError, "by-parameter"):
            carry(x, PIN)
        x = sample()
        x["cases"][0]["options"][0]["face_index"] = 1
        with self.assertRaisesRegex(ValueError, "active face"):
            carry(x, PIN)

    def test_06_independent_chain_witness_detects_tampering(self):
        receipt = carry(sample(), PIN)["ledger_pages"][0]["receipt"]
        tampered = deepcopy(receipt)
        tampered["final"]["objects"]["original-mu04-junction"]["real_impulse"] = 7.
        with self.assertRaises(ValueError):
            verify_receipt(tampered)
        tampered = deepcopy(receipt)
        tampered["events"][-1]["effect"] = {"status": "material-measurement"}
        with self.assertRaises(ValueError):
            verify_receipt(tampered)


if __name__ == "__main__":
    unittest.main()
