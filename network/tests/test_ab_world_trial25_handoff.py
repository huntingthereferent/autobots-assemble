"""WORLD25 A/B controls: finite segments and source-ancestry are not impacts.

Synthetic fixtures exercise transport and refusal only. Source-owned clipping
and the independent separating-axis numerical oracle run in dedicated CI.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial25_handoff import (
    carry, ANGLES, FACES, SOURCE, SRC23, SRC24, NO_SOURCE,
    BRACKET, INTERVALS, grid_time, PIN,
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    data23, data24, data25 = [], [], []
    impulse = {"materially_witnessed": False,
               "contact_absolute_virtual_time": 3.0,
               "outgoing_velocity": [2.,0.], "outgoing_spin": 0.4}
    receiver = {"normal":[1.,0.],"anchor":[11.,1.5],"span":1.}
    for i,angle in enumerate(ANGLES):
        admissible = i not in (0,7)
        source_impulse = deepcopy(impulse) if admissible else None
        old_receiver = deepcopy(receiver) if admissible else None
        prior_status = ("CONDITIONAL_SOURCE_THIRD" if admissible else NO_SOURCE)
        root = {"surface":FACES[0],
                "feature_classification":"FINITE_FACE_INTERIOR_CANDIDATE",
                "dt_after_third_impulse":(grid_time(9)+grid_time(10))/2}
        first23 = deepcopy(root) if admissible else None
        first24 = None
        data23.append({
            "schema":SRC23,"angle":angle,"source_trial22_status":prior_status,
            "source_third_impulse":deepcopy(source_impulse),
            "source_receiver":deepcopy(old_receiver),
            "first_eligible_geometry":deepcopy(first23),
            "eligible_geometry_roots":[deepcopy(root)] if admissible else [],
        })
        data24.append({
            "schema":SRC24,"angle":angle,"source_trial22_status":prior_status,
            "source_third_impulse":deepcopy(source_impulse),
            "source_receiver":deepcopy(old_receiver),
            "first_eligible_edge":deepcopy(first24),
        })
        records=[]
        candidates=[]
        if admissible:
            for face_idx,face in enumerate(FACES):
                is_first=face_idx==0
                window={
                    "first_sample_index":10,"last_sample_index":20,
                    "first_sample_time":grid_time(10),
                    "last_sample_time":grid_time(20),
                }
                bracket={
                    "last_grid_separated_at":grid_time(9),
                    "first_grid_intersection_at":grid_time(10),
                    "bisected_transition_time":(grid_time(9)+grid_time(10))/2,
                    "source_finite_clip_entry_fraction":.30,
                    "source_finite_clip_exit_fraction":.56,
                    "numerical_transition_not_exact_certified":True,
                }
                records.append({
                    "face":face,
                    "segment":[[12.-face_idx,1.],[12.-face_idx,2.]],
                    "samples_checked":INTERVALS+1,
                    "intersecting_grid_samples":11 if is_first else 0,
                    "first_grid_intersection_at":grid_time(10) if is_first else None,
                    "sampled_intersection_windows":[window] if is_first else [],
                    "first_transition_bracket":deepcopy(bracket) if is_first else None,
                    "start_intersected":False,
                    "continuous_absence_certified":False,
                })
                if is_first:
                    candidates.append({"face":face,"bracket":deepcopy(bracket),
                                       "kind":"FINITE_SOURCE_SEGMENT_SQUARE_INTERSECTION_CANDIDATE",
                                       "hardware_measured":False})
            comparison={
                "face":FACES[0],
                "source_first_finite_vertex_time":
                    (grid_time(9)+grid_time(10))/2,
                "first_grid_clear_time":grid_time(9),
                "first_grid_overlap_time":grid_time(10),
                "relationship":"SOURCE_VERTEX_TIME_INSIDE_FIRST_GRID_BRACKET",
                "same_face_only":True,
                "numerical_grid_not_certified_first_contact":True,
            }
        else:
            comparison=None
        data25.append({
            "schema":SOURCE,"angle":angle,
            "source_trial22_status":prior_status,
            "source_trial23_schema":SRC23,
            "source_trial23_first_geometry":deepcopy(first23),
            "source_trial24_schema":SRC24,
            "source_trial24_first_edge":deepcopy(first24),
            "source_third_impulse":deepcopy(source_impulse),
            "source_receiver":deepcopy(old_receiver),
            "window_start":.008,"window_end":.25,
            "sample_intervals_per_face":INTERVALS,
            "original_24_by_6_world_preserved":True,
            "conditional_model_only":True,
            "model_positions_not_hardware":True,
            "physical_contact_witnessed":False,
            "fourth_impulse_solved":False,
            "new_receiver_created":False,
            "formally_certified_continuous_collision_detection":False,
            "status":BRACKET if admissible else NO_SOURCE,
            "onset_vs_original_vertex_candidate":comparison,
            "face_results":records,
            "first_detected_bracket":deepcopy(candidates[0]) if candidates else None,
            "faces_with_sampled_intersection":1 if admissible else 0,
            "finite_intersection_candidates":deepcopy(candidates),
        })
    return (
        {"schema":SOURCE,"angles":list(ANGLES),"cases":data25,
         "source_third_impulse_cases":6,
         "no_source_third_impulse_controls":2,
         "finite_intersection_grid_cases":6,
         "finite_grid_no_intersection_cases":0,
         "total_intersecting_grid_samples":66,
         "fourth_impulses_solved":0,"material_observations":0,
         "physical_receivers_constructed":0,"new_engine_or_world":False},
        {"schema":SRC23,"angles":list(ANGLES),"cases":data23,
         "fourth_impulses_selected":0,"physical_measurements":0},
        {"schema":SRC24,"angles":list(ANGLES),"cases":data24,
         "fourth_impulses_selected":0,"physical_measurements":0},
    )


class Trial25FiniteIntersectionHandoffTests(unittest.TestCase):
    def test_01_all_eight_cases_and_finite_evidence_kept_without_fourth_impact(self):
        source23, ancestry23, ancestry24 = fixture()
        immutable = deepcopy((source23,ancestry23,ancestry24))
        result = carry(source23,ancestry23,ancestry24)
        self.assertEqual((source23,ancestry23,ancestry24),immutable)
        self.assertEqual(result["original_cases"],8)
        self.assertEqual(result["conditionally_admitted"],6)
        self.assertEqual(result["source_refusals"],2)
        self.assertEqual(result["finite_grid_overlap_cases"],6)
        self.assertEqual(result["source_intersecting_grid_samples"],66)
        self.assertEqual(result["ledger_witness"]["pages_verified"],8)
        self.assertEqual(result["ledger_witness"]["observations_recorded"],36)
        self.assertEqual(result["ledger_witness"]["steps_verified"],92)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["material_impacts_observed"],0)
        self.assertEqual(result["fourth_impulses_selected"],0)
        self.assertFalse(result["finite_intersection_completeness_proven"])
        for page in result["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            self.assertIsNone(page["receipt"]["final"]["objects"]
                              ["original-conditional-square"]["fourth_impulse"])
        self.assertEqual(result["ledger_pages"][1]["receipt"]["final"]
                         ["comparisons"]["no-finite-grid-intersection-hypothesis"]
                         ["result"],"DIFFERENT")
        self.assertEqual(result["ledger_pages"][0]["receipt"]["final"]
                         ["comparisons"]["no-finite-grid-intersection-hypothesis"]
                         ["result"],"MATCH")

    def test_02_original_no_third_impulse_cannot_generate_a_finite_hit(self):
        source,p23,p24=fixture()
        source["cases"][0]["finite_intersection_candidates"]=[
            {"face":FACES[0],"bracket":{"bisected_transition_time":.02}}]
        with self.assertRaisesRegex(ValueError,"invented finite overlap"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["cases"][0]["fourth_impulse_solved"]=True
        with self.assertRaisesRegex(ValueError,"physical scope"):
            carry(source,p23,p24)

    def test_03_sampled_counts_and_brackets_cannot_be_invented(self):
        source,p23,p24=fixture()
        source["cases"][1]["face_results"][0]["sampled_intersection_windows"][0][
            "last_sample_index"]=21
        with self.assertRaisesRegex(ValueError,"overlap windows"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["cases"][1]["face_results"][0]["first_transition_bracket"][
            "bisected_transition_time"]=.2
        with self.assertRaisesRegex(ValueError,"transition bracket"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["total_intersecting_grid_samples"]=0
        with self.assertRaisesRegex(ValueError,"aggregate counts"):
            carry(source,p23,p24)

    def test_04_wrong_face_and_original_vertex_lineage_rejected(self):
        source,p23,p24=fixture()
        source["cases"][1]["face_results"][0]["face"]="unbounded-world"
        with self.assertRaisesRegex(ValueError,"finite source face"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        p23["cases"][1]["first_eligible_geometry"]={"invented":True}
        with self.assertRaisesRegex(ValueError,"23/24 feature"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        p24["cases"][1]["source_receiver"]={"invented":True}
        with self.assertRaisesRegex(ValueError,"23/24 feature"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["cases"][1]["onset_vs_original_vertex_candidate"]["same_face_only"]=False
        with self.assertRaisesRegex(ValueError,"same-finite-face"):
            carry(source,p23,p24)

    def test_05_no_material_impact_or_exact_numerical_certificate(self):
        source,p23,p24=fixture()
        source["cases"][1]["physical_contact_witnessed"]=True
        with self.assertRaisesRegex(ValueError,"physical scope"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["cases"][1]["formally_certified_continuous_collision_detection"]=True
        with self.assertRaisesRegex(ValueError,"physical scope"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        source["cases"][1]["face_results"][0]["continuous_absence_certified"]=True
        with self.assertRaisesRegex(ValueError,"finite source face"):
            carry(source,p23,p24)
        source,p23,p24=fixture()
        with self.assertRaisesRegex(ValueError,"commit changed"):
            carry(source,p23,p24,"unversioned-ref")

    def test_06_independent_a_b_witness_detects_tampering(self):
        source,p23,p24=fixture()
        receipt=carry(source,p23,p24)["ledger_pages"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["final"]["objects"]["original-conditional-square"]["fourth_impulse"]={"j":7}
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        bad=deepcopy(receipt)
        bad["events"][-1]["effect"]={"status":"hardware-collision-observed"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__=="__main__":
    unittest.main()
