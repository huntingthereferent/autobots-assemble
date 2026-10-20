"""Unit checks for neutral WORLD16 carrier (fixture is NOT a physics oracle).

Pinned original source and independent corner/impulse reconstruction run as a
separate native job in the dedicated CI workflow, not imported from main.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from work.ab_world.world_trial16_handoff import (
    carry, SCHEMA, SOURCE, PIN, ANGLES, OVERLAP, NO_OVERLAP
)
from work.ab_world.verify_construction import verify_receipt


def fixture(angle, overlap):
    original = {
        "hit": True, "reason": "FIRST_CONTACT_SOLVED",
        "angle_degrees": angle, "normal": [-1., 0.],
        "source_wall_center": [12., 1.5], "source_wall_span": 1.,
        "first_contact_center": [11.75, 1.5],
        "velocity_after": [-3., 0.], "angular_velocity_after": 1.5,
        "normal_impulse": 6.,
        "candidate_receiver": {"surface_built": False,
                               "second_contact_witnessed": False,
                               "normal": [1., 0.]},
        "after_look": {"unconstrained_ballistic_projection_only": True},
    }
    first_bad = .01 if overlap else None
    samples = []
    for i in range(61):
        t = round(i * .001, 10)
        bad = bool(overlap and t >= first_bad)
        samples.append({
            "dt": t, "center": [11.75 - 3. * t, 1.5],
            "orientation": round(1.5 * t, 10),
            "minimum_signed_clearance": -0.1 if bad else 0.1,
            "finite_interior_overlap": bad,
            "checked_corners": 4, "worst_corner_index": 2,
        })
    return {
        "schema": SOURCE, "angle": angle,
        "status": OVERLAP if overlap else NO_OVERLAP,
        "first_contact": original, "samples": samples,
        "observation_step": .001, "observation_horizon": .06,
        "first_detected_overlap_at": first_bad,
        "next_receiver_candidate_only": deepcopy(original["candidate_receiver"]),
        "next_receiver_built": False,
        "second_contact_computed": False,
        "unmodeled_recontact_response_refused": overlap,
        "no_overlap_between_samples_proven": False,
        "continuous_clearance_verified": False,
        "physical_observation": False,
        "world_15_fixed_square_source_preserved": True,
    }


def source_fixture():
    cases = [fixture(angle, index not in (0, 7))
             for index, angle in enumerate(ANGLES)]
    return {
        "schema": SOURCE, "angles": list(ANGLES), "cases": cases,
        "counts": {"sampled-overlap": 6, "sampled-no-overlap": 2},
        "physical_world_verified": False,
        "continuous_rotating_polygon_solver_present": False,
        "new_world_or_renderer": False,
    }


class Trial16SourceCarrierTests(unittest.TestCase):
    def test_sampled_counterexamples_and_non_counterexamples_are_distinct(self):
        native = source_fixture()
        before = deepcopy(native)
        result = carry(native)
        self.assertEqual(native, before)
        self.assertEqual(result["schema"], SCHEMA)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["ledger_witness"]["pages_verified"], 8)
        self.assertEqual(result["overlaps_refuting_projection"], 6)
        self.assertEqual(result["sample_windows_without_detected_overlap"], 2)
        self.assertEqual(result["sampled_points_retained"], 488)
        self.assertEqual(result["receiver_constructions"], 0)
        self.assertEqual(result["second_impulses_solved"], 0)
        self.assertEqual(result["real_physical_measurements"], 0)
        self.assertFalse(result["continuous_clearance_proven"])
        for i, page in enumerate(result["pages"]):
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            final = page["receipt"]["final"]
            self.assertEqual(set(final["objects"]),
                             {"original-finite-face", "projected-rotating-square"})
            contrast = final["comparisons"]["unconstrained-no-overlap-prediction"]
            self.assertEqual(contrast["result"],
                             "MATCH" if i in (0, 7) else "DIFFERENT")
            self.assertEqual(page["projected_revisions_before_refutation"],
                             61 if i in (0, 7) else 10)
            self.assertEqual(len(final["observations"]), 4)

    def test_never_continue_body_state_after_first_overlap(self):
        pages = carry(source_fixture())["pages"]
        for page in pages:
            final_body = page["receipt"]["final"]["objects"]["projected-rotating-square"]
            self.assertFalse(final_body["hardware_measured"])
            self.assertEqual(final_body["state_kind"], "unverified-ballistic-projection")
            if page["first_detected_overlap_at"] is not None:
                self.assertLess(final_body["elapsed_after_first_impact"],
                                page["first_detected_overlap_at"])
            self.assertNotIn("next_receiver", page["receipt"]["final"]["objects"])
            self.assertFalse(page["receipt"]["final"]["observations"]
                             ["bounded-continuation-verdict"]["reading"]["receiver_built"])

    def test_negative_source_claims_refused(self):
        for key,value in (("physical_observation",True),
                          ("next_receiver_built",True),
                          ("second_contact_computed",True),
                          ("continuous_clearance_verified",True),
                          ("no_overlap_between_samples_proven",True)):
            native=source_fixture()
            native["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(native)
        native=source_fixture()
        native["cases"][1]["next_receiver_candidate_only"]["surface_built"]=True
        with self.assertRaises(ValueError):carry(native)

    def test_missing_samples_forged_clock_and_overlap_rejected(self):
        native=source_fixture()
        native["cases"][1]["samples"].pop(4)
        with self.assertRaises(ValueError):carry(native)
        native=source_fixture()
        native["cases"][1]["samples"][4]["dt"]=.044
        with self.assertRaises(ValueError):carry(native)
        native=source_fixture()
        native["cases"][1]["samples"][10]["finite_interior_overlap"]=False
        native["cases"][1]["first_detected_overlap_at"]=None
        with self.assertRaises(ValueError):carry(native)
        native=source_fixture()
        native["cases"][1]["first_detected_overlap_at"]=.02
        with self.assertRaises(ValueError):carry(native)

    def test_missing_source_identity_or_altered_counts_rejected(self):
        native=source_fixture()
        native["cases"][1]["first_contact"]["angle_degrees"]=20.
        with self.assertRaises(ValueError):carry(native)
        native=source_fixture()
        native["counts"]["sampled-overlap"]=5
        with self.assertRaises(ValueError):carry(native)
        native=source_fixture()
        native["cases"][1],native["cases"][2]=native["cases"][2],native["cases"][1]
        with self.assertRaises(ValueError):carry(native)
        with self.assertRaises(ValueError):carry(source_fixture(),source_commit="0"*40)

    def test_independent_witness_rejects_receipt_forgery(self):
        receipt=carry(source_fixture(),source_commit=PIN)["pages"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["events"][-1]["effect"]={"physical_contact":"verified"}
        with self.assertRaises(ValueError):verify_receipt(bad)
        bad=deepcopy(receipt)
        bad["final"]["objects"]["projected-rotating-square"]["hardware_measured"]=True
        with self.assertRaises(ValueError):verify_receipt(bad)


if __name__=="__main__":
    unittest.main()
