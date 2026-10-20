"""Trial13 controls: coupled-mode rejections remain distinct from model movements."""
from copy import deepcopy
from itertools import product
import unittest

from work.ab_world.world_trial13_handoff import (
    SPINS, FRICTIONS, ANGLES, ROTATIONS, MODES, carry)
from work.ab_world.verify_construction import verify_receipt

PIN = "6179d4e6b6e66a02065e8a5c1ef64b855a2de763"


def sample():
    original_ids = ["original-A", "original-B"]
    cases = []
    for index, (rot, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        ids = [original_ids[0], original_ids[1] if rot == 0
               else "controlled-B-" + str(rot)]
        groups = []
        for spin in SPINS:
            for friction in FRICTIONS:
                modes = ([("frictionless", "frictionless")] if friction == 0.
                         else list(product(MODES, repeat=2)))
                options = []
                for j, mode in enumerate(modes):
                    good = friction == 0. and spin == 0. and j == 0
                    frames = ([{
                        "time": round(i*.05, 9),
                        "position": [12 - .1*i, 1.4],
                        "velocity": [-2., 0.], "spin": 0.,
                        "orientation": 0.,
                    } for i in range(31)] if good else [])
                    options.append({
                        "mode": list(mode), "friction": friction,
                        "incoming_spin": spin, "source_ids": ids,
                        "status": "admissible-coupled-mode" if good
                                  else "rejected-nonpositive-normal",
                        "reason": None if good else "nonpositive-normal",
                        "impulses": [1., 0., 1., 0.] if good else None,
                        "outgoing_velocity": [2., 0.] if good else None,
                        "outgoing_spin": 0. if good else None,
                        "frames": frames,
                        "continuous_clearance_verified": good,
                    })
                groups.append({
                    "starting_spin": spin, "friction": friction,
                    "options": options, "admissible_count": int(
                        friction == 0. and spin == 0.),
                    "classification": "one" if friction == 0. and spin == 0.
                                      else "none",
                    "physical_outcome_selected": False,
                })
        cases.append({
            "original_index": index, "incoming_angle_degrees": angle,
            "surface_B_rotation_degrees": rot,
            "geometry_kind": "original-source-geometry" if rot == 0
                             else "controlled-geometry-not-original",
            "source_ids": ids,
            "trial09_two_active_status": "accepted-local-candidate",
            "groups": groups, "material_behavior_observed": False,
        })
    aggregate = []
    for spin in SPINS:
        for friction in FRICTIONS:
            good = spin == 0. and friction == 0.
            aggregate.append({
                "starting_spin": spin, "friction": friction,
                "admissible_modes": 35 if good else 0,
                "cases_with_one_mode": 35 if good else 0,
                "cases_with_multiple_modes": 0,
                "cases_with_no_mode": 0 if good else 35,
            })
    return {
        "schema": "world-ab-coupled-two-contact-friction-modes/v1",
        "original_source_geometry": {
            "surfaces": [{"id": original_ids[0]}, {"id": original_ids[1]}]},
        "source_trial09_schema": "world-ab-two-contact-incidence-stress/v1",
        "original_trial09_two_active_counts": {},
        "angle_grid": list(ANGLES), "rotation_grid": list(ROTATIONS),
        "friction_grid": list(FRICTIONS), "starting_spin_grid": list(SPINS),
        "hypotheses": list(MODES), "disc_radius": .35,
        "disc_inertia": .02, "normal_restitution": 1.,
        "scenarios": cases, "aggregate": aggregate,
        "original_trial06_friction": .4,
        "source_original_trial06_simultaneous_stop_preserved": True,
        "general_simultaneous_friction_manifold_solved": False,
        "actual_joint_contact_impulses_measured": False,
        "physical_material_law_verified": False,
        "real_blueprint_generated": False,
    }


class Trial13CoupledModeCarrierTests(unittest.TestCase):
    def test_01_preserves_all_1330_attempts_with_35_separate_case_ledgers(self):
        source = sample()
        before = deepcopy(source)
        out = carry(source, PIN)
        self.assertEqual(source, before)
        self.assertEqual(out["mode_attempts"], 1330)
        self.assertEqual(out["admissible_modes"], 35)
        self.assertEqual(out["rejected_modes"], 1295)
        self.assertEqual(out["conditional_motion_frames"], 1085)
        self.assertEqual(out["ledger_witness"]["pages_verified"], 35)
        self.assertEqual(out["ledger_witness"]["observations_recorded"], 1330)
        self.assertEqual(out["ledger_witness"]["steps_verified"], 5670)
        self.assertTrue(out["ledger_witness"]["valid"])
        self.assertFalse(out["original_material_contact_solved"])
        self.assertFalse(out["actual_joint_contact_impulses_measured"])
        self.assertTrue(verify_receipt(out["ledger_pages"][0]["receipt"])["valid"])

    def test_02_rejected_coupled_mode_never_gets_completed_movement(self):
        source = sample()
        source["scenarios"][0]["groups"][1]["options"][0]["frames"] = [
            {"time":0., "position":[7, 7]}]
        with self.assertRaisesRegex(ValueError, "invented motion"):
            carry(source, PIN)
        source = sample()
        source["scenarios"][0]["groups"][1]["options"][0]["outgoing_spin"] = 0.
        with self.assertRaisesRegex(ValueError, "invented motion"):
            carry(source, PIN)

    def test_03_unwitnessed_physics_never_promoted(self):
        source = sample()
        source["general_simultaneous_friction_manifold_solved"] = True
        with self.assertRaisesRegex(ValueError, "unsupported physical claim"):
            carry(source, PIN)
        source = sample()
        source["scenarios"][0]["groups"][0]["physical_outcome_selected"] = True
        with self.assertRaisesRegex(ValueError, "evidence claim"):
            carry(source, PIN)
        source = sample()
        source["source_original_trial06_simultaneous_stop_preserved"] = False
        with self.assertRaisesRegex(ValueError, "simultaneous stop"):
            carry(source, PIN)

    def test_04_source_modes_and_geometry_cannot_be_swapped(self):
        source = sample()
        source["scenarios"][0]["groups"][1]["options"][0]["mode"] = ["invented", "mode"]
        with self.assertRaisesRegex(ValueError, "mode identity"):
            carry(source, PIN)
        source = sample()
        source["scenarios"][0]["source_ids"][0] = "fabricated"
        with self.assertRaisesRegex(ValueError, "synthetic geometry"):
            carry(source, PIN)
        source = sample()
        source["scenarios"][0]["groups"][0]["starting_spin"] = 10.
        with self.assertRaisesRegex(ValueError, "parameter"):
            carry(source, PIN)
        with self.assertRaisesRegex(ValueError, "exact original commit"):
            carry(sample(), "unversioned")

    def test_05_full_candidate_frame_and_summary_counts_reverified(self):
        source = sample()
        source["scenarios"][0]["groups"][0]["options"][0]["frames"].pop()
        with self.assertRaisesRegex(ValueError, "complete source movement"):
            carry(source, PIN)
        source = sample()
        source["scenarios"][0]["groups"][0]["options"][0]["frames"][10]["spin"] = "not-spin"
        with self.assertRaisesRegex(ValueError, "spin-motion frame"):
            carry(source, PIN)
        source = sample()
        source["aggregate"][0]["admissible_modes"] = 1330
        with self.assertRaisesRegex(ValueError, "outcome counts"):
            carry(source, PIN)

    def test_06_independent_chain_rejects_forged_real_contact(self):
        receipt = carry(sample(), PIN)["ledger_pages"][0]["receipt"]
        changed = deepcopy(receipt)
        changed["final"]["objects"]["original-mu04-contact"]["measured_joint_impulse"] = 100.
        with self.assertRaises(ValueError):
            verify_receipt(changed)
        changed = deepcopy(receipt)
        changed["events"][-1]["effect"] = {"status": "material-verified"}
        with self.assertRaises(ValueError):
            verify_receipt(changed)


if __name__ == "__main__":
    unittest.main()
