"""A/B WORLD22 independent neutral ledger/negative tests.

Synthetic source fixtures validate transport only; pinned original WORLD22
numerics and separate independent derivative-root witness run in native CI.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial22_handoff import (
    carry, PIN, SOURCE, SOURCE21, ANGLES,
    NO_SOURCE, NO_CROSSING
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    old=[]
    cases=[]
    for i,angle in enumerate(ANGLES):
        admitted = i not in (0,7)
        crossing = i in (1,2,3)
        impulse = ({
            "contact_absolute_virtual_time":1.75,
            "outgoing_spin":2.,
            "materially_witnessed":False
        } if admitted else None)
        receiver=({"id":"motion-derived-finite-receiver"} if admitted else None)
        parent={"schema":SOURCE21,"angle":angle,
                "status":"CONDITIONAL_LOCAL_SEPARATION" if admitted
                         else "NO_QUALIFYING_THIRD_CONTACT",
                "third_impulse":impulse,
                "source_receiver":receiver}
        old.append(parent)
        candidate=({
            "surface":"original_finite_face",
            "vertex_index":1,
            "dt_after_third_impulse":.1,
            "absolute_virtual_time":1.85,
            "vertex_position":[11.8,1.7],
            "source_face_tangent_coordinate":.2,
            "incoming_normal_vertex_rate":-2.,
            "signed_line_gap_residual":0.,
            "feature_classification":"FINITE_FACE_INTERIOR_CANDIDATE",
            "physical_contact_measured":False,
        } if crossing else None)
        case={
            "schema":SOURCE,"angle":angle,
            "source_trial21_schema":SOURCE21,
            "source_trial21_status":parent["status"],
            "source_third_impulse":deepcopy(impulse),
            "source_receiver":deepcopy(receiver),
            "projection_horizon":.25,
            "source_trial21_local_window":.008,
            "source_original_world":[24.,6.],
            "unselected_conditional_model_only":True,
            "model_motion_not_material_measurement":True,
            "fourth_impulse_solved":False,
            "new_receiver_constructed":False,
            "continuous_real_world_motion_verified":False,
            "formally_outward_rounded_certificate":False,
            "later_forces_and_impacts_assumed_absent":True,
            "monotonic_intervals_checked":24 if admitted else 0,
            "status":("FIRST_MODEL_CONTACT_GEOMETRY_CANDIDATE" if crossing
                      else NO_CROSSING if admitted else NO_SOURCE),
            "first_crossing":deepcopy(candidate),
            "coearliest_crossings":[deepcopy(candidate)] if crossing else [],
            "all_source_line_crossings":[deepcopy(candidate)] if crossing else [],
        }
        cases.append(case)
    native={
        "schema":SOURCE,"angles":list(ANGLES),"cases":cases,
        "conditional_third_impulse_inputs":6,
        "no_third_impulse_controls":2,
        "source_line_crossing_cases":3,
        "source_line_no_crossing_cases":3,
        "physical_contact_measurements":0,
        "selected_fourth_impulses":0,
        "real_receivers_constructed":0,
        "new_world_or_engine":False,
    }
    previous={
        "schema":SOURCE21,"angles":list(ANGLES),"cases":old,
        "real_material_behavior_verified":False,
        "another_receiver_created":False,
    }
    return native,previous


class Trial22NeutralRecordTests(unittest.TestCase):
    def test_all_eight_bounded_original_source_outcomes_are_separate(self):
        source,old=fixture()
        frozen=deepcopy((source,old))
        report=carry(source,old)
        self.assertEqual((source,old),frozen)
        self.assertEqual(report["line_crossing_cases"],3)
        self.assertEqual(report["bounded_no_crossing_cases"],3)
        self.assertEqual(report["without_source_third_impulse"],2)
        self.assertEqual(report["all_source_candidates_retained"],3)
        self.assertEqual(report["ledger_witness"]["pages_verified"],8)
        self.assertEqual(report["ledger_witness"]["steps_verified"],48)
        self.assertEqual(report["ledger_witness"]["observations_recorded"],16)
        self.assertTrue(report["ledger_witness"]["valid"])
        for field in ("real_fourth_impulses","real_material_measurements",
                      "constructed_new_receivers","post_crossing_trajectories_admitted"):
            self.assertEqual(report[field],0)
        for i,page in enumerate(report["ledger_pages"]):
            receipt=page["receipt"]
            self.assertTrue(verify_receipt(receipt)["valid"])
            self.assertEqual(len(receipt["final"]["objects"]),2)
            self.assertEqual(receipt["final"]["comparisons"]
                             ["no-further-line-crossing-hypothesis"]["result"],
                             "DIFFERENT" if i in (1,2,3) else "MATCH")

    def test_all_source_candidates_are_observations_not_fourth_contact_objects(self):
        source,old=fixture()
        receipt=carry(source,old)["ledger_pages"][1]["receipt"]
        self.assertEqual(set(receipt["final"]["objects"]),
                         {"original-source-geometry","conditional-rotating-square"})
        first=receipt["final"]["observations"]["source-owned-crossing-search"]["reading"]
        self.assertEqual(first["source_first_crossing"],
                         source["cases"][1]["first_crossing"])
        self.assertTrue(first["numerical_source_not_material_sensor"])
        self.assertEqual(first["coearliest_alternatives"],
                         source["cases"][1]["coearliest_crossings"])

    def test_no_source_impulse_cannot_acquire_a_crossing(self):
        source,old=fixture()
        source["cases"][0]["first_crossing"]=deepcopy(source["cases"][1]["first_crossing"])
        with self.assertRaises(ValueError):carry(source,old)
        source,old=fixture()
        source["cases"][0]["monotonic_intervals_checked"]=24
        with self.assertRaises(ValueError):carry(source,old)

    def test_later_impulse_or_measured_material_claim_is_refused(self):
        for key,value in (("fourth_impulse_solved",True),
                          ("new_receiver_constructed",True),
                          ("continuous_real_world_motion_verified",True),
                          ("formally_outward_rounded_certificate",True),
                          ("unselected_conditional_model_only",False),
                          ("projection_horizon",1.)):
            source,old=fixture()
            source["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(source,old)
        source,old=fixture()
        source["cases"][1]["first_crossing"]["physical_contact_measured"]=True
        with self.assertRaises(ValueError):carry(source,old)

    def test_bounded_time_feature_order_and_source_ancestry_refused(self):
        for key,value in (
            ("dt_after_third_impulse",.4),
            ("absolute_virtual_time",0.),
            ("incoming_normal_vertex_rate",3.),
            ("vertex_index",9),
            ("source_face_tangent_coordinate",None),
            ("feature_classification","EARTH_MATERIAL_CONTACT"),
        ):
            source,old=fixture()
            value_changed=deepcopy(source["cases"][1]["first_crossing"])
            value_changed[key]=value
            source["cases"][1]["first_crossing"]=value_changed
            source["cases"][1]["all_source_line_crossings"]=[deepcopy(value_changed)]
            source["cases"][1]["coearliest_crossings"]=[deepcopy(value_changed)]
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(source,old)
        source,old=fixture()
        source["cases"][1]["source_third_impulse"]["outgoing_spin"]=123.
        with self.assertRaises(ValueError):carry(source,old)
        source,old=fixture()
        source["cases"][1],source["cases"][2]=source["cases"][2],source["cases"][1]
        with self.assertRaises(ValueError):carry(source,old)

    def test_source_pin_and_receipt_tampering_refused(self):
        source,old=fixture()
        with self.assertRaises(ValueError):
            carry(source,old,source_commit="0"*40)
        good=carry(source,old,source_commit=PIN)["ledger_pages"][1]["receipt"]
        wrong=deepcopy(good)
        wrong["events"][-1]["effect"]={"fourth":"actual"}
        with self.assertRaises(ValueError):verify_receipt(wrong)
        wrong=deepcopy(good)
        wrong["final"]["objects"]["conditional-rotating-square"][
            "material_contact_response_selected"]=True
        with self.assertRaises(ValueError):verify_receipt(wrong)


if __name__=="__main__":
    unittest.main()
