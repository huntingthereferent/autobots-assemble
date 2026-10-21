"""Independent WORLD27 uncertainty partition and sub-grid negative controls.

Recalculate source grid intersection directly using world-coordinate SAT;
recalculate fixed-axis margins with an independently rotated square and
reconstruct envelope classifications without calling WORLD27's classifier.
Original WORLD25/26 numerical witnesses remain independent.
"""
from __future__ import annotations

from copy import deepcopy
from math import hypot
import unittest

from systems.workspace.world_ab_interval_uncertainty_audit import (
    attempt,run,SCHEMA,HIT,UNKNOWN,COVERED,classified_intervals,
)
from systems.workspace.world_ab_between_sample_clearance import (
    attempt as source26, START,DURATION,SAMPLE_COUNT,GUARD,face_windows,
)
from systems.workspace.world_ab_finite_segment_square_overlap import (
    attempt as source25,grid_for_face,finite_clip,
)
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_first_post_third_candidate import ANGLES
from systems.workspace.world_ab_oblique_impact import HALF
from network.tests.test_world_ab_finite_segment_square_overlap import sat_segment_square
from network.tests.test_world_ab_between_sample_clearance import (
    separately_reconstructed_sat_margin,verify as verify26,
)


def independently_reconstructed_face(prior25,prior26,h):
    segment=prior25["segment"]
    n=SAMPLE_COUNT
    dt=(DURATION-START)/n
    times=[START+i*dt for i in range(n+1)]
    hits=[sat_segment_square(h,segment,t) for t in times]
    if sum(hits)!=prior25["intersecting_grid_samples"]:
        raise ValueError("original WORLD25 sampled intersection roster differed")
    margins=[separately_reconstructed_sat_margin(h,segment,t) for t in times]
    speed=hypot(*h["outgoing_velocity"])+abs(h["outgoing_spin"])*hypot(HALF,HALF)
    classes=[]
    for i in range(n):
        a,b=margins[i],margins[i+1]
        covered=a>GUARD and b>GUARD and a+b-speed*dt>2*GUARD
        if (hits[i] or hits[i+1]) and covered:
            raise ValueError("sampled source overlap was falsely separated")
        classes.append(HIT if (hits[i] or hits[i+1]) else
                       COVERED if covered else UNKNOWN)
    spans=[]
    for i,label in enumerate(classes):
        if not spans or spans[-1]["classification"]!=label:
            spans.append({"first_interval_index":i,
                          "last_interval_index":i,
                          "classification":label})
        else:
            spans[-1]["last_interval_index"]=i
    counts={key:classes.count(key) for key in (HIT,UNKNOWN,COVERED)}
    if counts[HIT]+counts[UNKNOWN]!=prior26["uncovered_interval_count"]:
        raise ValueError("prior WORLD26 uncovered records differ from independent classification")
    return {
        "face":prior25["face"],
        "source_sampled_overlap_count":prior25["intersecting_grid_samples"],
        "source_uncovered_interval_count":prior26["uncovered_interval_count"],
        "classified_interval_counts":counts,
        "ordered_classification_spans":spans,
        "uncovered_both_samples_separated_intervals":[
            i for i,label in enumerate(classes) if label==UNKNOWN],
        "physical_contact_measurements":0,
        "formal_intervals_certified":0,
    }


def independent_check(case):
    angle=case.get("angle")
    if case.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("bad original trial identity")
    prev25=source25(angle)
    prev26=source26(angle)
    ancestor=source21(angle)
    if not verify26(prev26):
        raise ValueError("independent WORLD26 witness failed")
    required={
        "source_trial25_schema":prev25["schema"],
        "source_trial25_status":prev25["status"],
        "source_trial26_schema":prev26["schema"],
        "source_trial26_status":prev26["status"],
        "original_source_third_impulse":ancestor["third_impulse"],
        "source_original_window":[START,DURATION],
        "source_intervals_per_face":SAMPLE_COUNT,
        "unchanged_original_24_by_6_world":True,
        "conditional_ballistic_model_only":True,
        "physical_event_witnessed":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "formal_root_or_interval_certificate":False,
    }
    if any(case.get(k)!=v for k,v in required.items()):
        raise ValueError("source ancestry or physical scope changed")
    if ancestor["third_impulse"] is None:
        if (case.get("status")!="NO_ADMITTED_THIRD_IMPULSE" or
            case.get("face_partitions")!=[] or
            case.get("totals")!={HIT:0,UNKNOWN:0,COVERED:0}):
            raise ValueError("no source impulse fabricated interval evidence")
        return True
    if len(prev25["face_results"])!=2 or len(prev26["face_clearance_bounds"])!=2:
        raise ValueError("missing original finite sources")
    expected=[independently_reconstructed_face(f,g,ancestor["third_impulse"])
              for f,g in zip(prev25["face_results"],prev26["face_clearance_bounds"])]
    if case.get("face_partitions")!=expected:
        raise ValueError("source classification or run spans changed")
    total={key:sum(r["classified_interval_counts"][key] for r in expected)
           for key in (HIT,UNKNOWN,COVERED)}
    if case.get("totals")!=total:
        raise ValueError("source unknown/overlap totals changed")
    label=("SAMPLED_FINITE_OVERLAP_WITH_SEPARATE_UNKNOWN_TAILS" if total[HIT] else
           "CLEAR_GRID_ENDPOINTS_WITH_UNRESOLVED_GAPS" if total[UNKNOWN] else
           "ALL_FACE_INTERVALS_NOMINALLY_SEPARATED")
    if case.get("status")!=label:
        raise ValueError("an unproved interval was promoted")
    return True


class World27Tests(unittest.TestCase):
    def test_all_source_controls_reconstruct_three_way_partition(self):
        source=run()
        self.assertEqual(source["schema"],SCHEMA)
        self.assertEqual(source["source_conditional_impulse_cases"],6)
        self.assertEqual(source["no_impulse_controls"],2)
        self.assertEqual(source["physical_measurements"],0)
        self.assertEqual(source["selected_fourth_impulses"],0)
        self.assertEqual(sum(source["classified_face_intervals"].values()),
                         6*2*SAMPLE_COUNT)
        for row in source["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(independent_check(row))

    def test_fast_hidden_between_frame_intersection_is_classified_unknown(self):
        h={"contact_center":[-8000.3,0.],
           "contact_orientation":0.,
           "outgoing_velocity":[1000000.,0.],
           "outgoing_spin":0.}
        segment=[[.4,-.1],[.4,.1]]
        dt=(DURATION-START)/SAMPLE_COUNT
        self.assertFalse(finite_clip(h,segment,START)["overlap"])
        self.assertFalse(finite_clip(h,segment,START+dt)["overlap"])
        self.assertTrue(finite_clip(h,segment,START+.0000006)["overlap"])
        one=grid_for_face(h,"synthetic-between-samples",segment)
        two=face_windows(h,"synthetic-between-samples",segment)
        audit=classified_intervals(one,two)
        self.assertIn(0,audit["uncovered_both_samples_separated_intervals"])
        self.assertEqual(audit["ordered_classification_spans"][0]["classification"],UNKNOWN)

    def test_absent_original_impact_stays_absent(self):
        for angle in (0.,20.):
            row=attempt(angle)
            self.assertEqual(row["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertEqual(row["face_partitions"],[])

    def test_forged_clearance_material_and_source_unknowns_rejected(self):
        row=attempt(7.5)
        for key,value in (
            ("physical_event_witnessed",True),
            ("fourth_impulse_selected",True),
            ("source_original_window",[0.,1.]),
            ("formal_root_or_interval_certificate",True),
        ):
            tampered=deepcopy(row)
            tampered[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                independent_check(tampered)
        tampered=deepcopy(row)
        part=tampered["face_partitions"][0]
        part["classified_interval_counts"][UNKNOWN]+=1
        with self.assertRaises(ValueError):independent_check(tampered)
        tampered=deepcopy(row)
        part=tampered["face_partitions"][0]
        part["ordered_classification_spans"][0]["classification"]="ALL_MATERIAL_SAFE"
        with self.assertRaises(ValueError):independent_check(tampered)


if __name__=="__main__":
    unittest.main()
