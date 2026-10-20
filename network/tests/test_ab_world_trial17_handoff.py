"""Standalone transport tests for WORLD17; fixtures do not verify contact physics.

The dedicated CI separately runs immutable original Trial17 source and its
independent numerical/first-impact verifier before A/B carrier admission.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from work.ab_world.world_trial17_handoff import (
    carry, ANGLES, CANDIDATE, NO_RETURN, PIN, SOURCE, SCHEMA
)
from work.ab_world.verify_construction import verify_receipt

SOURCE_NAME = "unchanged original WORLD trial04 first square impact"
METHOD = "analytical corner gap stationary partitions plus numerical bisection"


def source_case(angle, returns):
    original = {
        "hit": True, "reason": "FIRST_CONTACT_SOLVED",
        "angle_degrees": angle,
        "normal": [-1., 0.],
        "source_wall_center": [12., 1.5],
        "source_wall_span": 1.,
        "first_contact_center": [11.75, 1.5],
        "velocity_after": [-3., .2],
        "angular_velocity_after": 0.5,
        "normal_impulse": 4.,
        "first_contact_time": 2.5,
        "candidate_receiver": {"surface_built": False,
                               "second_contact_witnessed": False},
    }
    t = .016
    candidate = None if not returns else {
        "dt_after_initial_contact": t,
        "absolute_virtual_time": 2.5 + t,
        "corner_index": 2,
        "corner_position": [11.6, 1.7],
        "source_face_tangent_coordinate": .2,
        "normal_gap_residual": 1e-10,
        "incoming_normal_vertex_rate": -2.,
        "contact_feature": "square-vertex / original finite face interior",
        "second_impulse_selected": False,
    }
    roots = [] if not returns else [
        {"time": t, "corner_index": 2, "type": "TRANSVERSE_SIGN_CROSSING"},
        {"time": .03, "corner_index": 3, "type": "TRANSVERSE_SIGN_CROSSING"},
    ]
    return {
        "schema": SOURCE, "source": SOURCE_NAME,
        "source_angle": angle, "horizon": .06,
        "source_original_first_contact": original,
        "status": CANDIDATE if returns else NO_RETURN,
        "first_return": candidate,
        "candidate_return_roots": roots,
        "monotonic_segments_checked": 4,
        "method": METHOD, "source_finite_wall_preserved": True,
        "recontact_kinematics_only": True,
        "numerically_bracketed_not_exact_certified": True,
        "second_impulse_or_further_motion_solved": False,
        "derived_receiver_built": False,
        "physical_sensor_evidence": False,
    }


def sample():
    return {
        "schema": SOURCE, "angles": list(ANGLES), "horizon": .06,
        "cases": [source_case(angle, index not in (0, 7))
                  for index, angle in enumerate(ANGLES)],
        "first_return_candidates": 6, "no_return": 2,
        "built_any_new_object": False,
        "actual_physical_impact_verified": False,
    }


class Trial17NeutralCarrierTests(unittest.TestCase):
    def test_source_fixture_carried_separately_with_six_counterexamples(self):
        native = sample()
        original = deepcopy(native)
        result = carry(native)
        self.assertEqual(native, original)
        self.assertEqual(result["schema"], SCHEMA)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["ledger_witness"]["pages_verified"], 8)
        self.assertEqual(result["numerical_first_return_candidates"], 6)
        self.assertEqual(result["no_new_line_crossings_in_window"], 2)
        self.assertEqual(result["receiver_constructions"], 0)
        self.assertEqual(result["second_impulses_solved"], 0)
        self.assertEqual(result["physical_measurements"], 0)
        self.assertFalse(result["continuous_clearance_proven"])
        for i, page in enumerate(result["pages"]):
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            final = page["receipt"]["final"]
            self.assertEqual(set(final["objects"]),
                             {"original-finite-source-face", "original-moving-square"})
            self.assertEqual(len(final["observations"]), 4)
            self.assertEqual(
                final["comparisons"]["hypothetical-no-renewed-contact"]["result"],
                "MATCH" if i in (0, 7) else "DIFFERENT")
            if i in (0, 7):
                self.assertNotIn("candidate_first_return",
                                 final["objects"]["original-moving-square"])
            else:
                self.assertTrue(final["objects"]
                                ["original-moving-square"]["contact_response_not_computed"])

    def test_no_receiver_and_no_second_impulse_created(self):
        for page in carry(sample())["pages"]:
            record=page["receipt"]
            self.assertEqual(len(record["final"]["objects"]),2)
            self.assertEqual(len(record["final"]["relations"]),1)
            self.assertNotIn("receiver",record["final"]["objects"])
            v=record["final"]["observations"]["source-return-verdict"]["reading"]
            self.assertFalse(v["receiver_built"])
            self.assertFalse(v["second_impulse_solved"])
            self.assertFalse(v["physical_measurement"])

    def test_fake_physical_measurements_and_unsupported_continuation_refused(self):
        for key,value in (
            ("physical_sensor_evidence",True),
            ("derived_receiver_built",True),
            ("second_impulse_or_further_motion_solved",True),
            ("numerically_bracketed_not_exact_certified",False),
        ):
            native=sample()
            native["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(native)
        native=sample()
        native["built_any_new_object"]=True
        with self.assertRaises(ValueError):carry(native)

    def test_forged_root_corner_and_timestamp_refused(self):
        def mutated(path, value):
            native=sample()
            target=native["cases"][1]
            item=target
            for field in path[:-1]:
                item=item[field]
            item[path[-1]]=value
            with self.assertRaises(ValueError):carry(native)
        mutated(("first_return","dt_after_initial_contact"),.065)
        mutated(("first_return","corner_index"),5)
        mutated(("first_return","normal_gap_residual"),.005)
        mutated(("first_return","source_face_tangent_coordinate"),.6)
        mutated(("first_return","incoming_normal_vertex_rate"),2.0)
        mutated(("first_return","second_impulse_selected"),True)
        mutated(("first_return","absolute_virtual_time"),3.0)
        mutated(("candidate_return_roots",0,"corner_index"),1)
        mutated(("candidate_return_roots",0,"time"),.04)
        mutated(("source_original_first_contact","angle_degrees"),20.)

    def test_fabricated_return_on_no_return_control_rejected(self):
        native=sample()
        native["cases"][0]["first_return"]=deepcopy(native["cases"][1]["first_return"])
        with self.assertRaises(ValueError):carry(native)
        native=sample()
        native["cases"][0]["candidate_return_roots"]=deepcopy(
            native["cases"][1]["candidate_return_roots"])
        with self.assertRaises(ValueError):carry(native)
        native=sample()
        native["cases"][1]["first_return"]=None
        with self.assertRaises(ValueError):carry(native)

    def test_source_pin_case_grid_and_integrity_guard(self):
        with self.assertRaises(ValueError):
            carry(sample(),source_commit="0"*40)
        native=sample()
        native["cases"][1],native["cases"][2]=native["cases"][2],native["cases"][1]
        with self.assertRaises(ValueError):carry(native)
        native=sample()
        native["no_return"]=3
        with self.assertRaises(ValueError):carry(native)
        receipt=carry(sample(),source_commit=PIN)["pages"][1]["receipt"]
        forged=deepcopy(receipt)
        forged["events"][-1]["effect"]={"physics":"authenticated"}
        with self.assertRaises(ValueError):verify_receipt(forged)


if __name__ == "__main__":
    unittest.main()
