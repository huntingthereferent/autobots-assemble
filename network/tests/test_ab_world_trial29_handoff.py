"""A/B WORLD29 neutral transport and adversarial source-identity controls.

Synthetic source fixtures test *record* integrity only; source mathematical
correctness belongs to pinned original WORLD29 independent numerical tests.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial29_handoff import (
    carry,PIN,SOURCE,PRIOR,ANGLES,ACCEPTED
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    latest=[];previous=[]
    for i,angle in enumerate(ANGLES):
        accepted=i in (1,2,3)
        earlier_impulse=i not in (0,7)
        original_third={"outgoing_velocity":[2.,.5],
                        "materially_witnessed":False} if earlier_impulse else None
        onset=({
            "face":"original_finite_face",
            "refined_sat_bracket":{"first_nominally_intersecting_time":.1}
        } if accepted else None)
        p={
            "schema":PRIOR,"angle":angle,
            "status":"FIRST_NUMERICAL_FINITE_ONSET_CORROBORATED_BY_VERTEX"
            if accepted else "NO_SAMPLED_FINITE_ONSET_IN_ORIGINAL_WINDOW"
            if earlier_impulse else "NO_ADMITTED_THIRD_IMPULSE",
            "source_original_third_impulse":deepcopy(original_third),
            "first_eligible_finite_onset":deepcopy(onset),
        }
        feature=({
            "source_face":"original_finite_face",
            "source_vertex_index":2,
            "source_onset_refined_at":.1,
            "contact_point":[12.,2.],
            "contact_center":[11.7,2.],
            "contact_normal":[-1.,0.],
            "contact_lever":[.3,0.],
            "absolute_virtual_time":1.2,
            "finite_face_tangent_coordinate":.0,
            "dt_after_original_third_impulse":.1,
            "independent_finite_geometry_not_material_contact":True,
        } if accepted else None)
        response=({
            "source_face":"original_finite_face",
            "source_vertex_index":2,
            "normal_impulse":4.,
            "incoming_velocity":[2.,.5],
            "outgoing_velocity":[-2.,.5],
            "incoming_spin":0.,
            "outgoing_spin":0.,
            "incoming_contact_normal_rate":-2.,
            "outgoing_contact_normal_rate":2.,
            "kinetic_energy_before":2.125,
            "kinetic_energy_after":2.125,
            "materially_witnessed":False,
            "response_selected_as_actual":False,
            "further_contacts_resolved":False,
        } if accepted else None)
        c={
            "schema":SOURCE,"angle":angle,
            "source_trial28_schema":PRIOR,
            "source_trial28_status":p["status"],
            "source_trial23_schema":"world-ab-all-inward-roots-finite-feature-audit/v1",
            "source_original_third_response":deepcopy(original_third),
            "original_world_dimensions":[24.,6.],
            "original_mass":1.,
            "original_inertia":.04,
            "source_conditional_free_flight_only":True,
            "assumed_law":"single frictionless normal, restitution 1, unit-mass rotating square",
            "physical_fourth_impact_witnessed":False,
            "physical_response_selected":False,
            "post_response_trajectory_solved":False,
            "another_receiver_constructed":False,
            "exact_root_or_material_certification":False,
            "status":ACCEPTED if accepted else
                "NO_ORIGINAL_FIRST_FINITE_ONSET" if earlier_impulse
                else "NO_ADMITTED_THIRD_IMPULSE",
            "qualifying_source_feature":feature,
            "conditional_fourth_response":response,
            "source_contact_rejection":None,
        }
        previous.append(p);latest.append(c)
    return {
        "schema":SOURCE,"angles":list(ANGLES),"cases":latest,
        "material_impacts_witnessed":0,
        "actual_fourth_impulses_selected":0,
        "post_response_trajectories_solved":0,
        "receivers_constructed":0,
        "new_engine_or_world":False,
        "conditionally_qualifying_responses":3,
        "absent_source_impulse_controls":2,
        "original_finite_first_onset_cases":3,
        "unresolved_finite_feature_cases":0,
    },{
        "schema":PRIOR,"angles":list(ANGLES),"cases":previous,
        "actual_material_contacts_measured":0,
        "fourth_impulses_solved":0,
        "real_receivers_built":0,
    }


class Trial29LedgerTests(unittest.TestCase):
    def test_accepted_refusals_and_absent_source_controls_retained(self):
        source,prior=fixture()
        frozen=deepcopy((source,prior))
        report=carry(source,prior)
        self.assertEqual((source,prior),frozen)
        self.assertEqual(report["original_cases"],8)
        self.assertEqual(report["qualified_mathematical_candidates"],3)
        self.assertEqual(report["no_original_third_impulse_controls"],2)
        self.assertEqual(report["no_first_finite_onset_controls"],3)
        self.assertEqual(report["source_contact_refusals"],0)
        self.assertEqual(report["ledger_witness"]["pages_verified"],8)
        self.assertEqual(report["ledger_witness"]["steps_verified"],56)
        self.assertEqual(report["ledger_witness"]["observations_recorded"],24)
        self.assertTrue(report["ledger_witness"]["valid"])
        for key in ("physical_impacts_measured","actual_impulses_selected",
                    "verified_post_contact_motion","new_receivers_built"):
            self.assertEqual(report[key],0)
        for i,page in enumerate(report["ledger_pages"]):
            receipt=page["receipt"]
            self.assertTrue(verify_receipt(receipt)["valid"])
            self.assertEqual(len(receipt["final"]["objects"]),2)
            self.assertEqual(receipt["final"]["comparisons"]
                             ["source-response-versus-absent"]["result"],
                             "DIFFERENT" if i in (1,2,3) else "MATCH")

    def test_source_first_onset_observed_before_candidate_without_revision(self):
        source,prior=fixture()
        receipt=carry(source,prior)["ledger_pages"][1]["receipt"]
        events=[event["operation"] for event in receipt["events"]]
        earlier=next(i for i,v in enumerate(events)
                     if v["id"]=="earlier-first-finite-onset")
        qualification=next(i for i,v in enumerate(events)
                           if v["id"]=="source-qualification-reason")
        candidate=next(i for i,v in enumerate(events)
                       if v["id"]=="bounded-conditional-response")
        self.assertLess(earlier,qualification)
        self.assertLess(qualification,candidate)
        self.assertFalse(any(op["op"]=="revise" for op in events))
        recorded=receipt["final"]["observations"]
        self.assertEqual(
            recorded["bounded-conditional-response"]["reading"]["original_proposed_response"],
            source["cases"][1]["conditional_fourth_response"])

    def test_no_source_impulse_and_no_onset_cannot_forge_response(self):
        source,prior=fixture()
        source["cases"][0]["conditional_fourth_response"]=deepcopy(
            source["cases"][1]["conditional_fourth_response"])
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        source["cases"][4]["qualifying_source_feature"]=deepcopy(
            source["cases"][1]["qualifying_source_feature"])
        with self.assertRaises(ValueError):carry(source,prior)

    def test_forged_material_and_nonconservative_response_refused(self):
        for key,value in (
            ("physical_fourth_impact_witnessed",True),
            ("physical_response_selected",True),
            ("post_response_trajectory_solved",True),
            ("another_receiver_constructed",True),
            ("exact_root_or_material_certification",True),
        ):
            source,prior=fixture()
            source["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(source,prior)
        source,prior=fixture()
        source["cases"][1]["conditional_fourth_response"]["kinetic_energy_after"]+=1.
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        source["cases"][1]["qualifying_source_feature"]["source_onset_refined_at"]=.2
        with self.assertRaises(ValueError):carry(source,prior)

    def test_source_pin_angle_lineage_and_receipt_tampering_refused(self):
        source,prior=fixture()
        with self.assertRaises(ValueError):carry(source,prior,source_commit="0"*40)
        source,prior=fixture()
        source["cases"][1],source["cases"][2]=source["cases"][2],source["cases"][1]
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        source["cases"][1]["source_original_third_response"]={"fake":"material"}
        with self.assertRaises(ValueError):carry(source,prior)
        source,prior=fixture()
        receipt=carry(source,prior,source_commit=PIN)["ledger_pages"][1]["receipt"]
        forged=deepcopy(receipt)
        forged["final"]["objects"]["conditional-square-model"][
            "actual_fourth_impulse_selected"]=True
        with self.assertRaises(ValueError):verify_receipt(forged)
        forged=deepcopy(receipt)
        forged["events"][-1]["effect"]={"material":True}
        with self.assertRaises(ValueError):verify_receipt(forged)


if __name__=="__main__":
    unittest.main()
