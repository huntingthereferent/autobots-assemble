"""Standalone WORLD19 record/contrast tests (NOT a geometric oracle).

The dedicated source-native workflow independently verifies Taylor bounds and
stationary corner extrema before carrying the unchanged original source JSON.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial19_handoff import (
    ANGLES, PIN, SOURCE, TRIAL18, SEPARATED, ABSENT, carry
)
from work.ab_world.verify_construction import verify_receipt


def fake_case(angle: float, allowed: bool) -> dict:
    base = {
        "schema": SOURCE, "source_trial18_schema": TRIAL18,
        "original_source_angle": angle,
        "original_first_contact_source_id": "original WORLD Trial04 rigid square",
        "half_extent": .25, "window": .016,
        "finite_face_origin": [12., 1.5],
        "conditional_second_impulse_only": True,
        "actual_hardware_behavior_witnessed": False,
        "further_contact_response_solved": False,
        "derived_receiver_constructed": False,
        "formal_floating_point_interval_certificate": False,
    }
    if not allowed:
        return {**base, "status": ABSENT,
                "source_trial18_status": "NO_ADMITTED_RENEWED_CONTACT",
                "source_candidate_impulse": None,
                "per_vertex_bounds": [],
                "worst_positive_margin": None,
                "all_corner_halfspace_clearance_supported": False}
    corners = [{
        "corner_index": i, "accepted": True,
        "admission_condition": (
            "touching-corner-derivative-positive-entire-window" if i == 2 else
            "noncontact-corner-quadratic-lower-bound-positive"),
        "source_signed_gap_at_contact": 0. if i == 2 else .2,
        "outgoing_signed_gap_derivative": .5,
        "absolute_second_derivative_bound": 1.,
        "quadratic_lower_bound_at_window_end": .19,
        "derivative_lower_bound_at_window_end": .48,
        "conservative_margin": .48 if i == 2 else .19,
    } for i in range(4)]
    return {**base,
            "source_trial18_status": "NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES",
            "source_candidate_impulse": {
                "normal_impulse": 2.0,
                "selected_as_actual_material_response": False},
            "status": SEPARATED, "per_vertex_bounds": corners,
            "bounding_method": "four rotated-corner Taylor lower bounds; whole interval",
            "nominal_real_arithmetic_only": True,
            "postcontact_motion_assumed_ballistic": True,
            "no_additional_contacts_or_forces_in_assumed_window": True,
            "all_corner_halfspace_clearance_supported": True,
            "line_clearance_implies_finite_face_clearance": True,
            "worst_positive_margin": .19}


def sample() -> dict:
    return {
        "schema": SOURCE, "source_trial18": TRIAL18,
        "angles": list(ANGLES),
        "cases": [fake_case(angle, i not in (0,7))
                  for i,angle in enumerate(ANGLES)],
        "conditional_continuous_clearance_count": 6,
        "no_second_impulse_count": 2, "inconclusive_count": 0,
        "physics_engine_created": False,
        "all_earth_physics_verified": False,
        "new_receiver_created": False,
    }


class Trial19CarrierTests(unittest.TestCase):
    def test_complete_source_carried_without_selecting_real_world_motion(self):
        original = sample()
        frozen = deepcopy(original)
        result = carry(original)
        self.assertEqual(original, frozen)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["ledger_witness"]["pages_verified"], 8)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 48)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 16)
        self.assertEqual(result["conditional_nominal_separation_cases"], 6)
        self.assertEqual(result["no_second_impulse_controls"], 2)
        self.assertEqual(result["physical_contacts_measured"], 0)
        self.assertEqual(result["mathematical_intervals_formally_certified"], 0)
        self.assertEqual(result["postcontact_material_trajectories_verified"], 0)
        self.assertEqual(result["receivers_constructed"], 0)
        for i,page in enumerate(result["ledger_pages"]):
            receipt=page["receipt"]
            self.assertTrue(verify_receipt(receipt)["valid"])
            self.assertEqual(len(receipt["final"]["objects"]), 2)
            self.assertEqual(len(receipt["final"]["relations"]), 1)
            observed=receipt["final"]["observations"]["bounded-separation-claim"]["reading"]
            self.assertFalse(observed["hardware_measurement"])
            self.assertFalse(observed["formal_certificate"])
            self.assertFalse(observed["receiver_built"])
            self.assertEqual(
                receipt["final"]["comparisons"]
                ["conditional-separation-versus-no-proof"]["result"],
                "MATCH" if i in (0,7) else "DIFFERENT")

    def test_absent_impulse_stays_without_conditional_proof(self):
        data=sample()
        data["cases"][0]["status"]=SEPARATED
        with self.assertRaises(ValueError):carry(data)
        data=sample()
        data["cases"][0]["source_candidate_impulse"]={
            "normal_impulse":1., "selected_as_actual_material_response":False}
        with self.assertRaises(ValueError):carry(data)

    def test_forged_material_or_formal_certificate_claims_fail(self):
        for key in ("actual_hardware_behavior_witnessed",
                    "further_contact_response_solved",
                    "derived_receiver_constructed",
                    "formal_floating_point_interval_certificate"):
            data=sample()
            data["cases"][1][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):carry(data)
        data=sample()
        data["cases"][1]["source_candidate_impulse"]
        ["selected_as_actual_material_response"]=True
        with self.assertRaises(ValueError):carry(data)

    def test_incomplete_margin_and_changed_source_bounds_fail(self):
        for key,value in (
            ("worst_positive_margin",0.),
            ("all_corner_halfspace_clearance_supported",False),
            ("line_clearance_implies_finite_face_clearance",False),
            ("window",.03),
        ):
            data=sample()
            data["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):carry(data)
        data=sample()
        data["cases"][1]["per_vertex_bounds"][2]["accepted"]=False
        with self.assertRaises(ValueError):carry(data)
        data=sample()
        data["cases"][1]["per_vertex_bounds"][1]["corner_index"]=3
        with self.assertRaises(ValueError):carry(data)
        data=sample()
        data["cases"][1]["per_vertex_bounds"].pop()
        with self.assertRaises(ValueError):carry(data)

    def test_source_grid_and_immutable_pin_fail_closed(self):
        data=sample()
        data["cases"][1],data["cases"][2]=data["cases"][2],data["cases"][1]
        with self.assertRaises(ValueError):carry(data)
        data=sample()
        data["conditional_continuous_clearance_count"]=5
        with self.assertRaises(ValueError):carry(data)
        with self.assertRaises(ValueError):carry(sample(),source_commit="0"*40)

    def test_mutated_ledger_fails_independent_replay(self):
        good=carry(sample(),source_commit=PIN)["ledger_pages"][1]["receipt"]
        forged=deepcopy(good)
        forged["events"][-1]["effect"]={"physical":"certified"}
        with self.assertRaises(ValueError):verify_receipt(forged)
        forged=deepcopy(good)
        forged["final"]["objects"]["conditional-rotating-square"]
        ["physical_response_selected"]=True
        with self.assertRaises(ValueError):verify_receipt(forged)


if __name__ == "__main__":
    unittest.main()
