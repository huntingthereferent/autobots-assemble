"""Independent neutral A/B WORLD31 event/refusal tests.

Fixtures concern source-transport integrity only. Original numerical bisection
and independent analytic limit witness run separately at the immutable source.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial31_handoff import (
    carry,PIN,SOURCE,PRIOR,ANGLES,SCHEMA,KNOWN_PLANES
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    native=[]
    old=[]
    for i,angle in enumerate(ANGLES):
        admitted=i in (1,2,3)
        candidate={"source_vertex_index":2,
                   "materially_witnessed":False,
                   "response_selected_as_actual":False} if admitted else None
        parent_bounds=[]
        if admitted:
            for plane in KNOWN_PLANES:
                for index in range(4):
                    touch=plane=="original_finite_face" and index==2
                    parent_bounds.append({
                        "surface":plane,"corner_index":index,
                        "starts_at_qualified_contact":touch,
                        "gap_at_candidate":0. if touch else .1,
                        "outgoing_normal_rate":.5,
                        "curvature_upper_bound":.02,
                        "accepted":True,
                    })
        parent={
            "schema":PRIOR,"angle":angle,
            "status":"CONDITIONAL_LOCAL_OUTGOING_SEPARATION" if admitted
                     else "NO_QUALIFIED_SOURCE_FOURTH_RESPONSE",
            "source_candidate_response":deepcopy(candidate),
            "clearance_bounds":parent_bounds,
        }
        limits=[]
        if admitted:
            for index,original in enumerate(parent_bounds):
                t=.1 if index==0 else .25
                limits.append({
                    "source_plane":original["surface"],
                    "source_corner_index":original["corner_index"],
                    "source_starts_at_qualified_contact":
                    original["starts_at_qualified_contact"],
                    "original_gap_at_contact":original["gap_at_candidate"],
                    "original_outgoing_normal_rate":original["outgoing_normal_rate"],
                    "original_curvature_bound":original["curvature_upper_bound"],
                    "max_supported_prefix":t,
                    "constraint_restricts_declared_horizon":t<.25,
                    "at_short_window":True,
                    "at_declared_horizon":t==.25,
                })
        current={
            "schema":SOURCE,"angle":angle,
            "source_trial30_schema":PRIOR,
            "source_trial30_status":parent["status"],
            "original_source30_case":deepcopy(parent),
            "source_qualified_fourth_response":deepcopy(candidate),
            "original_24_by_6_world":[24.,6.],
            "source_original_minimum_horizon":.008,
            "declared_followup_horizon":.25,
            "positive_separation_margin":1e-5,
            "original_24_halfplane_constraints":24,
            "same_original_two_finite_source_faces":True,
            "original_model_response_only":True,
            "physical_fourth_impulse_selected":False,
            "fifth_impulse_solved":False,
            "fifth_contact_feature_observed":False,
            "physical_trajectory_recorded":False,
            "exact_interval_arithmetic_certificate":False,
            "post_limit_continuation_admitted":False,
            "status":"FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT" if admitted
                     else "NO_QUALIFIED_FOURTH_RESPONSE",
            "per_original_constraint_limits":limits,
            "max_common_nominal_clearance_prefix":.1 if admitted else None,
            "first_limiting_constraints":[deepcopy(limits[0])] if admitted else [],
            "original_constraints_checked":24 if admitted else 0,
        }
        old.append(parent)
        native.append(current)
    return ({
        "schema":SOURCE,"angles":list(ANGLES),"cases":native,
        "contact_features_solved":0,"fifth_impulses_computed":0,
        "real_material_measurements":0,"new_receivers_built":0,
        "new_engine_or_world":False,"cases_with_prior_envelope_limit":3,
        "cases_clear_through_horizon":0,
        "without_qualified_response":5,
        "qualified_original_responses":3,
    },{
        "schema":PRIOR,"angles":list(ANGLES),"cases":old,
        "real_material_impacts_witnessed":0,
        "selected_actual_fourth_impulses":0,
        "fifth_impulses_computed":0,
    })


class Trial31NeutralEvidenceTests(unittest.TestCase):
    def test_three_original_limits_and_five_inactive_controls(self):
        newer,prior=fixture()
        frozen=deepcopy((newer,prior))
        result=carry(newer,prior)
        self.assertEqual((newer,prior),frozen)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["source_cases"],8)
        self.assertEqual(result["source_bound_limit_cases"],3)
        self.assertEqual(result["without_qualified_fourth_response"],5)
        self.assertEqual(result["source_full_horizon_cases"],0)
        self.assertEqual(result["ledger_witness"]["pages_verified"],8)
        self.assertEqual(result["ledger_witness"]["steps_verified"],56)
        self.assertEqual(result["ledger_witness"]["observations_recorded"],24)
        self.assertTrue(result["ledger_witness"]["valid"])
        for key in ("real_fifth_contacts","fifth_impulses_selected",
                    "authenticated_postlimit_movements","new_receivers"):
            self.assertEqual(result[key],0)
        for page in result["ledger_pages"]:
            receipt=page["receipt"]
            self.assertTrue(verify_receipt(receipt)["valid"])
            self.assertEqual(len(receipt["final"]["objects"]),2)
            compared=receipt["final"]["comparisons"][
                "first-source-limit-versus-none"]["result"]
            self.assertEqual(compared,"DIFFERENT" if page["first_limit_reported"]
                             else "MATCH")

    def test_full_original_constraint_set_observed_without_impact_rewrite(self):
        newer,older=fixture()
        receipt=carry(newer,older)["ledger_pages"][1]["receipt"]
        events=[r["operation"] for r in receipt["events"]]
        prior=next(i for i,v in enumerate(events)
                   if v["id"]=="source-short-local-clearance")
        later=next(i for i,v in enumerate(events)
                   if v["id"]=="source-first-bound-limit")
        self.assertLess(prior,later)
        self.assertFalse(any(ev["op"]=="revise" for ev in events))
        observation=receipt["final"]["observations"]["source-first-bound-limit"]["reading"]
        self.assertEqual(observation["individual_constraint_limits"],
                         newer["cases"][1]["per_original_constraint_limits"])
        self.assertTrue(observation["limit_is_not_fifth_contact"])

    def test_no_source_response_cannot_acquire_future_time(self):
        newer,older=fixture()
        newer["cases"][0]["max_common_nominal_clearance_prefix"]=.2
        with self.assertRaises(ValueError):carry(newer,older)
        newer,older=fixture()
        newer["cases"][4]["per_original_constraint_limits"]=[
            deepcopy(newer["cases"][1]["per_original_constraint_limits"][0])]
        with self.assertRaises(ValueError):carry(newer,older)

    def test_changed_original_limiting_identity_or_fifth_impulse_refused(self):
        for key,value in (
            ("fifth_impulse_solved",True),
            ("fifth_contact_feature_observed",True),
            ("physical_fourth_impulse_selected",True),
            ("post_limit_continuation_admitted",True),
            ("exact_interval_arithmetic_certificate",True),
            ("declared_followup_horizon",3.),
        ):
            newer,older=fixture()
            newer["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(newer,older)
        newer,older=fixture()
        newer["cases"][1]["first_limiting_constraints"]=[]
        with self.assertRaises(ValueError):carry(newer,older)
        newer,older=fixture()
        newer["cases"][1]["per_original_constraint_limits"][0]["source_plane"]="new receiver"
        with self.assertRaises(ValueError):carry(newer,older)

    def test_pin_angle_ancestry_and_tampered_receipt_refused(self):
        newer,older=fixture()
        with self.assertRaises(ValueError):carry(newer,older,source_commit="0"*40)
        newer,older=fixture()
        newer["cases"][1],newer["cases"][2]=newer["cases"][2],newer["cases"][1]
        with self.assertRaises(ValueError):carry(newer,older)
        newer,older=fixture()
        receipt=carry(newer,older,source_commit=PIN)["ledger_pages"][1]["receipt"]
        fake=deepcopy(receipt)
        fake["final"]["objects"]["conditional-fourth-response-model"][
            "post_limit_motion_permitted"]=True
        with self.assertRaises(ValueError):verify_receipt(fake)
        fake=deepcopy(receipt)
        fake["events"][-1]["effect"]={"fifth_impulse":"selected"}
        with self.assertRaises(ValueError):verify_receipt(fake)


if __name__=="__main__":
    unittest.main()
