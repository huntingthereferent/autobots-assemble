"""Trial26 neutral transport controls: uncovered intervals are not collisions.

Fixtures are synthetic. The pinned native source and its independently
reconstructed separating-axis and velocity-envelope witness run separately.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial26_handoff import (
    carry, ANGLES, FACES, SRC25, SRC26, PIN, START, END, INTERVALS, time_at,
    NO_SOURCE, COVERED, SAMPLED, UNKNOWN,
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    old=[]
    news=[]
    impulse={"materially_witnessed":False,"outgoing_velocity":[2.,0.],
             "outgoing_spin":.4}
    receiver={"normal":[1.,0.],"anchor":[11.,1.5]}
    for i,angle in enumerate(ANGLES):
        admitted = i not in (0,7)
        overlap = i in (1,2,3)
        unknown = i in (1,2,3,4,5)
        source_impulse=deepcopy(impulse) if admitted else None
        source_receiver=deepcopy(receiver) if admitted else None
        status=(
            "FINITE_MODEL_INTERSECTION_TRANSITION_BRACKET_DETECTED"
            if overlap else
            "NO_FINITE_INTERSECTION_DETECTED_ON_GRID_ONLY"
            if admitted else NO_SOURCE
        )
        faces=[]
        if admitted:
            for j,face in enumerate(FACES):
                faces.append({"face":face,
                    "segment":[[12.-j,1.],[12.-j,2.]],
                    "intersecting_grid_samples":2 if overlap and j==0 else 0})
        old.append({"schema":SRC25,"angle":angle,"status":status,
                    "source_third_impulse":deepcopy(source_impulse),
                    "source_receiver":deepcopy(source_receiver),
                    "face_results":faces,"faces_with_sampled_intersection":
                         1 if overlap else 0})
        bounds=[]
        if admitted:
            for j,face in enumerate(FACES):
                has_unknown=unknown and j==0
                intervals=([{"interval_index":10,
                             "start":time_at(10),"end":time_at(11),
                             "sample_start_separating_margin":-.01,
                             "sample_end_separating_margin":.02,
                             "velocity_envelope_surplus":-.03,
                             "classification":"NOT_CERTIFIED_BY_ENDPOINT_MARGIN"}]
                           if has_unknown else [])
                bounds.append({
                    "face":face,"segment":deepcopy(faces[j]["segment"]),
                    "velocity_norm_upper_bound":3.,
                    "sampled_margins_count":INTERVALS+1,
                    "grid_intervals_checked":INTERVALS,
                    "endpoint_margin_covered_intervals":INTERVALS-len(intervals),
                    "uncovered_intervals":intervals,
                    "uncovered_interval_count":len(intervals),
                    "minimum_covered_margin_surplus":.01,
                    "all_intervals_nominally_covered":len(intervals)==0,
                    "formal_outward_rounded_certificate":False,
                })
        n=sum(len(x["uncovered_intervals"]) for x in bounds)
        covered=sum(x["all_intervals_nominally_covered"] for x in bounds)
        next_status=(NO_SOURCE if not admitted else COVERED if covered==2
                     else SAMPLED if overlap else UNKNOWN)
        news.append({
            "schema":SRC26,"angle":angle,
            "source_trial25_schema":SRC25,
            "source_trial25_status":status,
            "source_trial25_intersecting_grid_samples":2 if overlap else 0,
            "source_third_impulse":deepcopy(source_impulse),
            "source_receiver":deepcopy(source_receiver),
            "observation_start":START,"observation_end":END,
            "sample_intervals":INTERVALS,"nominal_velocity_margin_guard":1e-7,
            "unchanged_existing_two_finite_faces":True,
            "model_free_flight_hypothesis_only":True,
            "physical_motion_witnessed":False,
            "selected_fourth_impulse":False,
            "new_receiver_constructed":False,
            "certified_floating_point_interval_arithmetic":False,
            "counterfactual_after_any_earlier_contact":True,
            "status":next_status,
            "face_clearance_bounds":bounds,
            "fully_nominally_covered_faces":covered,
            "uncovered_total_intervals":n,
        })
    return ({
        "schema":SRC26,"angles":list(ANGLES),"cases":news,
        "conditional_third_impulse_cases":6,
        "no_source_third_impulse_controls":2,
        "cases_with_both_faces_nominally_covered":1,
        "cases_with_unresolved_intervals":5,
        "total_uncovered_face_intervals":5,
        "actual_hardware_measurements":0,
        "fourth_impulses_selected":0,
        "new_physical_receivers_constructed":0,
        "new_physics_engine":False,
    },{
        "schema":SRC25,"angles":list(ANGLES),"cases":old,
        "fourth_impulses_solved":0,
    })


class World26NeutralUncertaintyTests(unittest.TestCase):
    def test_01_nominal_coverage_and_uncertainty_are_distinct(self):
        src,prior=fixture()
        snap=deepcopy((src,prior))
        out=carry(src,prior)
        self.assertEqual((src,prior),snap)
        self.assertEqual(out["source_conditional_cases"],6)
        self.assertEqual(out["source_absent_controls"],2)
        self.assertEqual(out["nominally_covered_both_faces_cases"],1)
        self.assertEqual(out["cases_with_unknown_intervals"],5)
        self.assertEqual(out["uncovered_source_intervals"],5)
        self.assertEqual(out["uncertainty_chunks"],5)
        self.assertEqual(out["ledger_witness"]["pages_verified"],13)
        self.assertEqual(out["ledger_witness"]["steps_verified"],102)
        self.assertEqual(out["ledger_witness"]["observations_recorded"],41)
        self.assertTrue(out["ledger_witness"]["valid"])
        self.assertFalse(out["continuous_material_clearance_proven"])
        self.assertFalse(out["formal_outward_interval_proof"])
        for page in out["ledger_summaries"]+out["ledger_uncertainty_chunks"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
        self.assertEqual(out["ledger_summaries"][1]["receipt"]["final"]
                         ["comparisons"]["no-source-uncovered-interval-hypothesis"]
                         ["result"],"DIFFERENT")
        self.assertEqual(out["ledger_summaries"][6]["receipt"]["final"]
                         ["comparisons"]["no-source-uncovered-interval-hypothesis"]
                         ["result"],"MATCH")

    def test_02_without_original_third_impulse_no_uncertainty_can_be_fabricated(self):
        src,prior=fixture()
        src["cases"][0]["face_clearance_bounds"]=[{"face":"forged"}]
        with self.assertRaisesRegex(ValueError,"fake between-frame"):
            carry(src,prior)
        src,prior=fixture()
        src["cases"][0]["uncovered_total_intervals"]=7
        with self.assertRaisesRegex(ValueError,"fake between-frame"):
            carry(src,prior)

    def test_03_nominal_bounds_do_not_imply_material_certification(self):
        for field,value in (("physical_motion_witnessed",True),
                            ("selected_fourth_impulse",True),
                            ("certified_floating_point_interval_arithmetic",True),
                            ("counterfactual_after_any_earlier_contact",False)):
            src,prior=fixture()
            src["cases"][1][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"physical boundary"):
                carry(src,prior)
        src,prior=fixture()
        src["cases"][1]["face_clearance_bounds"][0][
            "formal_outward_rounded_certificate"]=True
        with self.assertRaisesRegex(ValueError,"floating certificate"):
            carry(src,prior)

    def test_04_source25_face_lineage_and_covered_totals_cannot_drift(self):
        src,prior=fixture()
        src["cases"][1]["source_trial25_intersecting_grid_samples"]=0
        with self.assertRaisesRegex(ValueError,"Trial25 source ancestry"):
            carry(src,prior)
        src,prior=fixture()
        src["cases"][1]["face_clearance_bounds"][0]["segment"]=[[0.,0.],[1.,1.]]
        with self.assertRaisesRegex(ValueError,"finite source segment"):
            carry(src,prior)
        src,prior=fixture()
        src["cases"][1]["face_clearance_bounds"][0]["endpoint_margin_covered_intervals"]=2048
        with self.assertRaisesRegex(ValueError,"interval count"):
            carry(src,prior)
        src,prior=fixture()
        src["cases"][1]["fully_nominally_covered_faces"]=2
        with self.assertRaisesRegex(ValueError,"whole-face certainty"):
            carry(src,prior)

    def test_05_unknown_window_is_not_a_collision_and_keeps_exact_source_clock(self):
        src,prior=fixture()
        src["cases"][1]["face_clearance_bounds"][0]["uncovered_intervals"][0][
            "classification"]="COLLISION_OCCURRED"
        with self.assertRaisesRegex(ValueError,"promoted to collisions"):
            carry(src,prior)
        src,prior=fixture()
        src["cases"][1]["face_clearance_bounds"][0]["uncovered_intervals"][0][
            "start"]=.04
        with self.assertRaisesRegex(ValueError,"reordered"):
            carry(src,prior)
        src,prior=fixture()
        src["total_uncovered_face_intervals"]=0
        with self.assertRaisesRegex(ValueError,"aggregate"):
            carry(src,prior)
        with self.assertRaisesRegex(ValueError,"pin changed"):
            src,prior=fixture()
            carry(src,prior,"moving-branch")

    def test_06_independent_neutral_replay_catches_claims_of_real_collision(self):
        src,prior=fixture()
        output=carry(src,prior)
        receipt=output["ledger_summaries"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["final"]["objects"]["conditional-square"]["actual_fourth_impulse"]={"j":1.}
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        chunk=output["ledger_uncertainty_chunks"][0]["receipt"]
        bad=deepcopy(chunk)
        bad["final"]["observations"]["native-unknown-intervals"]["reading"][
            "not_certified_not_a_collision"]=False
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
