"""Neutral A/B WORLD30 transport negative and receipt tests.

Synthetic fixtures check evidence flow only. The original pinned source's
independent numerical verifier owns correctness of actual corner bounds.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial30_handoff import (
    carry,PIN,SCHEMA,SOURCE,PRIOR,ANGLES,ACCEPTED,NO_RESPONSE,BOUND_LABELS
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    latest=[];older=[]
    for i,angle in enumerate(ANGLES):
        accepted=i in (1,2,3)
        source_impulse=({
            "source_face":"original_finite_face",
            "source_vertex_index":2,
            "normal_impulse":1.,
            "materially_witnessed":False,
            "response_selected_as_actual":False
        } if accepted else None)
        original_third={"outgoing_spin":.2,"materially_witnessed":False} if i not in (0,7) else None
        feature=({"source_face":"original_finite_face",
                  "source_vertex_index":2} if accepted else None)
        before={
            "schema":PRIOR,"angle":angle,
            "status":"CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE" if accepted
                     else "NO_ORIGINAL_FIRST_FINITE_ONSET" if i not in (0,7)
                     else "NO_ADMITTED_THIRD_IMPULSE",
            "qualifying_source_feature":deepcopy(feature),
            "conditional_fourth_response":deepcopy(source_impulse),
            "source_original_third_response":deepcopy(original_third),
        }
        bounds=[]
        if accepted:
            for plane in BOUND_LABELS:
                for corner in range(4):
                    bounds.append({
                        "surface":plane,"corner_index":corner,
                        "accepted":True,
                        "starts_at_qualified_contact":plane=="original_finite_face" and corner==2,
                        "gap_at_candidate":0. if plane=="original_finite_face" and corner==2 else .3,
                        "outgoing_normal_rate":.7,
                        "curvature_upper_bound":.01,
                        "end_gap_lower_bound":.3,
                        "normal_rate_lower_bound":.69,
                        "conservative_bound":.69,
                        "classification":"TOUCHING_VERTEX_DEPARTURE_LOWER_RATE"
                        if plane=="original_finite_face" and corner==2
                        else "OTHER_VERTEX_POSITIVE_GAP_BOUND",
                        "original_finite_source_not_real_hardware":True,
                    })
        newest={
            "schema":SOURCE,"angle":angle,
            "source_trial29_schema":PRIOR,
            "source_trial29_status":before["status"],
            "source_original_third_impulse":deepcopy(original_third),
            "source_candidate_contact":deepcopy(feature),
            "source_candidate_response":deepcopy(source_impulse),
            "original_world":[24.,6.],
            "original_finite_source_faces":2,
            "four_original_world_boundaries":4,
            "post_candidate_horizon":.008,
            "nominal_free_flight_model_only":True,
            "actual_contact_selected":False,
            "real_material_response_witnessed":False,
            "post_candidate_continuous_motion_authenticated":False,
            "formally_outward_rounded_numeric_certificate":False,
            "new_receiver_built":False,
            "fifth_impulse_computed":False,
            "status":ACCEPTED if accepted else NO_RESPONSE,
            "clearance_bounds":bounds,
            "accepted_bounds":len(bounds),
            "unresolved_bounds":0,
            "nominal_local_clearance_admitted":accepted,
        }
        older.append(before);latest.append(newest)
    return {
        "schema":SOURCE,"angles":list(ANGLES),"cases":latest,
        "real_material_impacts_witnessed":0,
        "selected_actual_fourth_impulses":0,
        "fifth_impulses_computed":0,
        "new_receivers_constructed":0,
        "new_physics_engine":False,
        "locally_separated_conditional_candidates":3,
        "post_candidate_geometry_unresolved":0,
        "no_qualified_source_response":5,
        "source_qualified_fourth_candidates":3,
    },{
        "schema":PRIOR,"angles":list(ANGLES),"cases":older,
        "material_impacts_witnessed":0,
        "actual_fourth_impulses_selected":0,
        "post_response_trajectories_solved":0,
    }


class Trial30TransportTests(unittest.TestCase):
    def test_three_source_clearances_and_five_nonresponses_preserved(self):
        source,prior=fixture()
        frozen=deepcopy((source,prior))
        report=carry(source,prior)
        self.assertEqual((source,prior),frozen)
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["qualified_local_clearances"],3)
        self.assertEqual(report["source_unresolved_local_cases"],0)
        self.assertEqual(report["without_original_fourth_candidate"],5)
        self.assertEqual(report["ledger_witness"]["pages_verified"],8)
        self.assertEqual(report["ledger_witness"]["steps_verified"],56)
        self.assertEqual(report["ledger_witness"]["observations_recorded"],24)
        self.assertTrue(report["ledger_witness"]["valid"])
        for key in ("physical_fourth_impacts_selected","fifth_impulses_computed",
                    "actual_post_contact_motion_authenticated","receivers_created"):
            self.assertEqual(report[key],0)
        for page in report["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            observed=page["receipt"]["final"]["comparisons"][
                "bounded-separation-versus-no-response"]["result"]
            self.assertEqual(observed,"DIFFERENT" if page["nominal_local_clearance"] else "MATCH")

    def test_source_response_is_observed_before_clearance_without_state_mutation(self):
        source,prior=fixture()
        receipt=carry(source,prior)["ledger_pages"][1]["receipt"]
        steps=[e["operation"] for e in receipt["events"]]
        earlier=next(i for i,x in enumerate(steps) if x["id"]=="prior-source-response")
        later=next(i for i,x in enumerate(steps) if x["id"]=="source-local-clearance-bounds")
        self.assertLess(earlier,later)
        self.assertFalse(any(x["op"]=="revise" for x in steps))
        self.assertEqual(receipt["final"]["observations"]
                         ["source-local-clearance-bounds"]["reading"]
                         ["original_plane_bounds"],source["cases"][1]["clearance_bounds"])

    def test_absent_source_response_cannot_become_new_motion(self):
        source,prior=fixture()
        source["cases"][0]["nominal_local_clearance_admitted"]=True
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        source["cases"][4]["source_candidate_response"]={"made_up":"impact"}
        with self.assertRaises(ValueError):carry(source,prior)

    def test_real_impulse_or_fabricated_clearance_refused(self):
        for name,value in (
            ("actual_contact_selected",True),
            ("real_material_response_witnessed",True),
            ("new_receiver_built",True),
            ("post_candidate_horizon",1.),
            ("formally_outward_rounded_numeric_certificate",True),
        ):
            source,prior=fixture()
            source["cases"][1][name]=value
            with self.subTest(key=name),self.assertRaises(ValueError):
                carry(source,prior)
        source,prior=fixture()
        source["cases"][1]["clearance_bounds"][5]["accepted"]=False
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        source["cases"][1]["clearance_bounds"][3]["surface"]="made-up receiver"
        with self.assertRaises(ValueError):carry(source,prior)

    def test_source_pin_case_swap_and_ledger_tampering_refused(self):
        source,prior=fixture()
        with self.assertRaises(ValueError):carry(source,prior,source_commit="0"*40)
        source,prior=fixture()
        source["cases"][1],source["cases"][2]=source["cases"][2],source["cases"][1]
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        receipt=carry(source,prior,source_commit=PIN)["ledger_pages"][1]["receipt"]
        forged=deepcopy(receipt)
        forged["final"]["objects"]["hypothetical-square"][
            "physical_fourth_impulse_selected"]=True
        with self.assertRaises(ValueError):verify_receipt(forged)
        forged=deepcopy(receipt)
        forged["events"][-1]["effect"]={"physical":True}
        with self.assertRaises(ValueError):verify_receipt(forged)


if __name__=="__main__":
    unittest.main()
