"""Neutral Trial21 transport tests; synthetic cases do not establish physics.

Original unchanged WORLD21 and its independent source numeric oracle execute
separately in the native evidence workflow before actual records are carried.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial21_handoff import (
    carry, PIN, SOURCE, SOURCE20, ANGLES, ADMITTED, ABSENT, SURFACES
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    recent, earlier = [], []
    for index, angle in enumerate(ANGLES):
        active = index not in (0, 7)
        receiver = ({
            "id": "motion-derived-finite-receiver", "anchor": [10., 2.],
            "normal": [-1., 0.],
            "endpoints": [[10., 1.5], [10., 2.5]],
            "constructed_from":
            "Trial18 conditional outgoing velocity and square rotation",
        } if active else None)
        touch = ({
            "vertex_index": 2, "at_relative_time": .25,
            "absolute_virtual_time": 1.75,
            "point": [10., 2.], "incoming_normal_vertex_rate": -1.,
            "geometric_touch_only": True, "third_impulse_assumed": False,
        } if active else None)
        prev = {
            "schema": SOURCE20, "source_angle": angle,
            "status": "CONDITIONAL_DERIVED_RECEIVER_REACHED"
            if active else "NO_SOURCE_SECOND_IMPULSE",
            "receiver": receiver, "next_contact": touch,
            "frames": ([{"time": j * .025} for j in range(11)]
                       if active else []),
            "third_impulse_calculated": False,
            "receiver_real_material_built": False,
            "third_collision_outcome_unresolved": True if active else False,
        }
        bounds = []
        for face in SURFACES:
            for corner in range(4):
                touching = face == "receiver" and corner == 2
                bounds.append({
                    "surface": face, "corner_index": corner,
                    "starts_touching": touching, "accepted": True,
                    "gap_at_third_contact": 0. if touching else .3,
                    "outgoing_gap_rate": .6,
                    "curvature_upper_bound": .1,
                    "end_gap_lower_bound": .25,
                    "rate_lower_bound": .59,
                    "conservative_margin": .59 if touching else .25,
                })
        impulse = ({
            "receiver_id": receiver["id"],
            "contact_vertex_index": 2,
            "contact_absolute_virtual_time": 1.75,
            "contact_point": [10., 2.],
            "contact_center": [10.25, 2.],
            "contact_orientation": .5,
            "source_receiver_normal": [-1., 0.],
            "incoming_velocity": [-2., 0.],
            "outgoing_velocity": [2., 0.],
            "incoming_spin": .5, "outgoing_spin": -.5,
            "normal_impulse": 4.,
            "incoming_contact_normal_rate": -2.,
            "outgoing_contact_normal_rate": 2.,
            "lever_cross_normal": .1,
            "kinetic_energy_before": 2.,
            "kinetic_energy_after": 2.,
            "law": "original frictionless unit-mass rigid square, restitution 1",
            "materially_witnessed": False,
        } if active else None)
        current = {
            "schema": SOURCE, "angle": angle,
            "source_trial20_schema": SOURCE20,
            "source_trial20_status": prev["status"],
            "source_receiver": deepcopy(receiver),
            "source_third_contact": deepcopy(touch),
            "relative_third_contact_time": .25,
            "local_window": .008,
            "third_impulse_model_hypothesis": True,
            "measured_material_response": False,
            "fourth_contact_selected": False,
            "another_receiver_constructed": False,
            "formal_interval_certificate": False,
            "first_second_contact_sources_unchanged": True,
            "status": ADMITTED if active else ABSENT,
            "third_impulse": impulse,
            "clearance_bounds": bounds if active else [],
        }
        if active:
            current.update({
                "local_separation_only": True,
                "source_finite_faces_unchanged": True,
                "hypothetical_outgoing_motion_only": True,
            })
        earlier.append(prev)
        recent.append(current)
    current_report = {
        "schema": SOURCE, "source_trial20": SOURCE20,
        "angles": list(ANGLES), "cases": recent,
        "candidate_third_impulses": 6,
        "local_conditional_separations": 6,
        "cases_without_qualifying_third_contact": 2,
        "real_material_behavior_verified": False,
        "another_receiver_created": False,
        "general_multicontact_solver_present": False,
    }
    earlier_report = {
        "schema": SOURCE20, "angles": list(ANGLES),
        "cases": earlier, "real_material_receiver_fabricated": False,
        "new_engine_or_world_created": False,
    }
    return current_report, earlier_report


class Trial21CarrierTests(unittest.TestCase):
    def test_six_conditional_contacts_and_two_absent_controls(self):
        native, prior = fixture()
        before = deepcopy((native, prior))
        result = carry(native, prior)
        self.assertEqual((native, prior), before)
        self.assertEqual(result["original_cases"], 8)
        self.assertEqual(result["conditional_third_impulses"], 6)
        self.assertEqual(result["conditional_full_local_separations"], 6)
        self.assertEqual(result["no_qualifying_third_contact_controls"], 2)
        self.assertEqual(result["local_window"], .008)
        self.assertEqual(result["ledger_witness"]["pages_verified"], 8)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 74)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 30)
        self.assertTrue(result["ledger_witness"]["valid"])
        for field in (
            "real_material_receivers_built", "real_impulses_measured",
            "fourth_contacts_solved", "formal_interval_certificates",
            "receivers_of_new_type_created"
        ):
            self.assertEqual(result[field], 0)

        for index, page in enumerate(result["ledger_pages"]):
            receipt = page["receipt"]
            self.assertTrue(verify_receipt(receipt)["valid"])
            active = index not in (0, 7)
            self.assertEqual(
                "existing-virtual-receiver" in receipt["final"]["objects"],
                active)
            self.assertEqual(receipt["final"]["comparisons"]
                             ["third-candidate-vs-absent-hypothesis"]["result"],
                             "DIFFERENT" if active else "MATCH")

    def test_third_impulse_observed_after_prior_virtual_receiver(self):
        native, prior = fixture()
        ops = [e["operation"] for e in
               carry(native, prior)["ledger_pages"][1]["receipt"]["events"]]
        source20 = next(i for i, op in enumerate(ops)
                        if op["id"] == "original-source20-receiver-report")
        receiver = next(i for i, op in enumerate(ops)
                        if op["id"] == "existing-virtual-receiver")
        third = next(i for i, op in enumerate(ops)
                     if op["id"] == "source-conditional-third-impulse")
        bounds = next(i for i, op in enumerate(ops)
                      if op["id"] == "source-local-corner-bounds")
        self.assertLess(source20, receiver)
        self.assertLess(receiver, third)
        self.assertLess(third, bounds)
        self.assertNotIn("fourth-receiver",
                         carry(native, prior)["ledger_pages"][1]
                         ["receipt"]["final"]["objects"])

    def test_absent_original_contact_cannot_gain_impulse_or_receiver(self):
        native, prior = fixture()
        native["cases"][0]["third_impulse"] = deepcopy(native["cases"][1]["third_impulse"])
        with self.assertRaises(ValueError):
            carry(native, prior)
        native, prior = fixture()
        native["cases"][0]["clearance_bounds"] = deepcopy(
            native["cases"][1]["clearance_bounds"])
        with self.assertRaises(ValueError):
            carry(native, prior)
        native, prior = fixture()
        prior["cases"][0]["receiver"] = deepcopy(prior["cases"][1]["receiver"])
        with self.assertRaises(ValueError):
            carry(native, prior)

    def test_false_physical_or_future_claims_refused(self):
        for field, value in (
            ("measured_material_response", True),
            ("fourth_contact_selected", True),
            ("another_receiver_constructed", True),
            ("formal_interval_certificate", True),
            ("third_impulse_model_hypothesis", False),
        ):
            native, prior = fixture()
            native["cases"][1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                carry(native, prior)
        native, prior = fixture()
        native["cases"][1]["third_impulse"]["materially_witnessed"] = True
        with self.assertRaises(ValueError):
            carry(native, prior)

    def test_broken_impulse_and_six_surface_boundaries_refused(self):
        for field, value in (
            ("normal_impulse", -1.),
            ("kinetic_energy_after", 20.),
            ("outgoing_contact_normal_rate", -2.),
            ("contact_vertex_index", 3),
            ("contact_absolute_virtual_time", 1.),
            ("receiver_id", "foreign"),
        ):
            native, prior = fixture()
            native["cases"][1]["third_impulse"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                carry(native, prior)
        for field, value in (
            ("corner_index", 2),
            ("accepted", False),
            ("conservative_margin", -1.),
            ("surface", "invented"),
            ("starts_touching", True),
        ):
            native, prior = fixture()
            native["cases"][1]["clearance_bounds"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                carry(native, prior)
        native, prior = fixture()
        native["cases"][1]["clearance_bounds"].pop()
        with self.assertRaises(ValueError):
            carry(native, prior)

    def test_reordered_sources_and_receipt_tamper_rejected(self):
        native, prior = fixture()
        native["cases"][1], native["cases"][2] = native["cases"][2], native["cases"][1]
        with self.assertRaises(ValueError):
            carry(native, prior)
        native, prior = fixture()
        native["cases"][1]["source_receiver"]["anchor"][0] += 1.
        with self.assertRaises(ValueError):
            carry(native, prior)
        native, prior = fixture()
        with self.assertRaises(ValueError):
            carry(native, prior, source_commit="0"*40)
        good = carry(native, prior, source_commit=PIN)["ledger_pages"][1]["receipt"]
        bad = deepcopy(good)
        bad["events"][-1]["effect"] = {"status":"physically-verified"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        bad = deepcopy(good)
        bad["final"]["objects"]["existing-virtual-receiver"]["actual_material_constructed"] = True
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
