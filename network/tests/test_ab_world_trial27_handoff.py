"""A/B WORLD27 interval type: overlap samples, unknown gaps, nominal margin."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial27_handoff import (
    carry, ANGLES, FACES, SOURCE, SOURCE25, SOURCE26,
    PIN, N, HIT, UNKNOWN, COVERED, CLASSES,
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    native25,native26,native27=[],[],[]
    model={"materially_witnessed":False,"outgoing_velocity":[2.,0.]}
    for i,angle in enumerate(ANGLES):
        admitted=i not in (0,7)
        has_hit=i in (1,2,3)
        impulse=deepcopy(model) if admitted else None
        old_status="FINITE_MODEL_INTERSECTION_TRANSITION_BRACKET_DETECTED" if has_hit else (
            "NO_FINITE_INTERSECTION_DETECTED_ON_GRID_ONLY" if admitted else
            "NO_ADMITTED_THIRD_IMPULSE")
        previous25=[]
        previous26=[]
        parts=[]
        totals={k:0 for k in CLASSES}
        if admitted:
            for j,face in enumerate(FACES):
                hit=has_hit and j==0
                windows=[{"first_sample_index":10,"last_sample_index":12,
                          "first_sample_time":.0,
                          "last_sample_time":.0}] if hit else []
                previous25.append({
                    "face":face,"segment":[[12.-j,1.],[12.-j,2.]],
                    "samples_checked":N+1,
                    "intersecting_grid_samples":3 if hit else 0,
                    "sampled_intersection_windows":windows,
                    "start_intersected":False,
                })
                missed=[{
                    "interval_index":k,
                    "classification":"NOT_CERTIFIED_BY_ENDPOINT_MARGIN"
                } for k in (9,10,11,12)] if hit else []
                previous26.append({
                    "face":face,"segment":deepcopy(previous25[-1]["segment"]),
                    "grid_intervals_checked":N,
                    "formal_outward_rounded_certificate":False,
                    "uncovered_intervals":missed,
                    "uncovered_interval_count":len(missed),
                })
                labels=[HIT if hit and k in (9,10,11,12) else COVERED
                        for k in range(N)]
                counts={key:labels.count(key) for key in CLASSES}
                for key in CLASSES:
                    totals[key]+=counts[key]
                spans=[]
                for k,label in enumerate(labels):
                    if not spans or spans[-1]["classification"]!=label:
                        spans.append({"first_interval_index":k,
                                      "last_interval_index":k,
                                      "classification":label})
                    else:
                        spans[-1]["last_interval_index"]=k
                parts.append({
                    "face":face,
                    "source_sampled_overlap_count":3 if hit else 0,
                    "source_uncovered_interval_count":4 if hit else 0,
                    "classified_interval_counts":counts,
                    "ordered_classification_spans":spans,
                    "uncovered_both_samples_separated_intervals":[],
                    "physical_contact_measurements":0,
                    "formal_intervals_certified":0,
                })
        native25.append({
            "schema":SOURCE25,"angle":angle,"status":old_status,
            "source_third_impulse":deepcopy(impulse),
            "face_results":previous25,
        })
        status26="SAMPLED_FINITE_INTERSECTION_WITH_UNRESOLVED_BETWEEN_FRAMES" if has_hit else (
            "ALL_FINITE_FACE_INTERVALS_NOMINALLY_SEPARATED" if admitted else
            "NO_ADMITTED_THIRD_IMPULSE")
        native26.append({
            "schema":SOURCE26,"angle":angle,"status":status26,
            "source_third_impulse":deepcopy(impulse),
            "source_trial25_intersecting_grid_samples":3 if has_hit else 0,
            "uncovered_total_intervals":4 if has_hit else 0,
            "face_clearance_bounds":previous26,
        })
        status27="SAMPLED_FINITE_OVERLAP_WITH_SEPARATE_UNKNOWN_TAILS" if has_hit else (
            "ALL_FACE_INTERVALS_NOMINALLY_SEPARATED" if admitted else
            "NO_ADMITTED_THIRD_IMPULSE")
        native27.append({
            "schema":SOURCE,"angle":angle,
            "source_trial25_schema":SOURCE25,
            "source_trial26_schema":SOURCE26,
            "source_trial25_status":old_status,
            "source_trial26_status":status26,
            "original_source_third_impulse":deepcopy(impulse),
            "source_original_window":[.008,.25],
            "source_intervals_per_face":N,
            "unchanged_original_24_by_6_world":True,
            "conditional_ballistic_model_only":True,
            "physical_event_witnessed":False,
            "fourth_impulse_selected":False,
            "new_receiver_constructed":False,
            "formal_root_or_interval_certificate":False,
            "status":status27,"face_partitions":parts,
            "totals":totals,
        })
    tally={k:sum(c["totals"][k] for c in native27) for k in CLASSES}
    return (
        {"schema":SOURCE,"angles":list(ANGLES),"cases":native27,
         "source_conditional_impulse_cases":6,
         "no_impulse_controls":2,
         "cases_with_unobserved_only_uncertainty":0,
         "classified_face_intervals":tally,
         "physical_measurements":0,"selected_fourth_impulses":0,
         "new_engine_or_world":False},
        {"schema":SOURCE25,"angles":list(ANGLES),"cases":native25,
         "fourth_impulses_solved":0},
        {"schema":SOURCE26,"angles":list(ANGLES),"cases":native26,
         "fourth_impulses_selected":0},
    )


class Source27ThreeWayCarrierTests(unittest.TestCase):
    def test_01_six_virtual_cases_two_controls_eight_receipts(self):
        a,b,c=fixture()
        before=deepcopy((a,b,c))
        record=carry(a,b,c)
        self.assertEqual((a,b,c),before)
        self.assertEqual(record["original_angle_controls"],8)
        self.assertEqual(record["conditional_third_impulse_cases"],6)
        self.assertEqual(record["no_original_impulse_controls"],2)
        self.assertEqual(record["sampled_overlap_cases"],3)
        self.assertEqual(record["sampled_overlap_adjacent_intervals"],12)
        self.assertEqual(record["clear_endpoint_unknown_intervals"],0)
        self.assertEqual(record["nominal_covered_intervals"],6*2*N-12)
        self.assertEqual(record["ledger_witness"]["pages_verified"],8)
        self.assertEqual(record["ledger_witness"]["steps_verified"],100)
        self.assertEqual(record["ledger_witness"]["observations_recorded"],36)
        self.assertTrue(record["ledger_witness"]["valid"])
        for row in record["ledger_pages"]:
            self.assertTrue(verify_receipt(row["receipt"])["valid"])
        self.assertFalse(record["actual_continuous_contact_response_solved"])
        self.assertEqual(record["material_impacts_measured"],0)
        self.assertNotIn("original-finite-face-0",
                         record["ledger_pages"][0]["receipt"]["final"]["objects"])
        self.assertEqual(record["ledger_pages"][1]["receipt"]["final"]["comparisons"][
            "no-sampled-finite-overlap-hypothesis"]["result"],"DIFFERENT")
        self.assertEqual(record["ledger_pages"][4]["receipt"]["final"]["comparisons"][
            "no-sampled-finite-overlap-hypothesis"]["result"],"MATCH")

    def test_02_observed_overlap_endpoint_cannot_be_falsely_covered(self):
        a,b,c=fixture()
        c["cases"][1]["face_clearance_bounds"][0]["uncovered_intervals"].pop()
        c["cases"][1]["face_clearance_bounds"][0]["uncovered_interval_count"]=3
        with self.assertRaisesRegex(ValueError,"overlap falsely declared"):
            carry(a,b,c)
        a,b,c=fixture()
        a["cases"][1]["face_partitions"][0]["classified_interval_counts"][HIT]=0
        with self.assertRaisesRegex(ValueError,"three-way interval partition"):
            carry(a,b,c)

    def test_03_original_face_and_sampled_grid_must_agree(self):
        a,b,c=fixture()
        b["cases"][1]["face_results"][0]["face"]="infinite-face-extension"
        with self.assertRaisesRegex(ValueError,"finite source face"):
            carry(a,b,c)
        a,b,c=fixture()
        b["cases"][1]["face_results"][0]["sampled_intersection_windows"][0][
            "last_sample_index"]=N+1
        with self.assertRaisesRegex(ValueError,"out of bounds"):
            carry(a,b,c)
        a,b,c=fixture()
        c["cases"][1]["source_trial25_intersecting_grid_samples"]=99
        with self.assertRaisesRegex(ValueError,"source25 sampled-overlap counts"):
            carry(a,b,c)

    def test_04_controls_without_model_impulse_acquire_no_face_or_collision(self):
        a,b,c=fixture()
        a["cases"][0]["face_partitions"]=[{"face":"invented"}]
        with self.assertRaisesRegex(ValueError,"absent source third"):
            carry(a,b,c)
        a,b,c=fixture()
        a["cases"][7]["totals"][HIT]=1
        with self.assertRaisesRegex(ValueError,"absent source third"):
            carry(a,b,c)

    def test_05_invalid_material_claims_and_fake_clear_endpoint_unknown_rejected(self):
        a,b,c=fixture()
        a["cases"][1]["physical_event_witnessed"]=True
        with self.assertRaisesRegex(ValueError,"material claim"):
            carry(a,b,c)
        a,b,c=fixture()
        a["selected_fourth_impulses"]=1
        with self.assertRaisesRegex(ValueError,"physical boundaries"):
            carry(a,b,c)
        a,b,c=fixture()
        part=a["cases"][1]["face_partitions"][0]
        part["uncovered_both_samples_separated_intervals"]=[20]
        with self.assertRaisesRegex(ValueError,"three-way interval partition"):
            carry(a,b,c)
        with self.assertRaisesRegex(ValueError,"immutable commit"):
            a,b,c=fixture()
            carry(a,b,c,"unversioned-original")

    def test_06_independent_ledger_replay_catches_physical_replacement(self):
        a,b,c=fixture()
        receipt=carry(a,b,c)["ledger_pages"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["final"]["objects"]["original-conditional-square"]["fourth_impulse"]={"j":1}
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        bad=deepcopy(receipt)
        bad["events"][-1]["effect"]={"claim":"experimentally measured impact"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__=="__main__":
    unittest.main()
