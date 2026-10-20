"""Independent WORLD25 finite segment / rotating convex square witness.

Source implementation clips the finite segment to the square's moving local
axes. Independent verifier instead applies the separating-axis theorem to a
world-coordinate rotating polygon and a world-coordinate finite segment.
Both agree on every declared sample; neither certifies missed microintervals.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin, hypot
import unittest

from systems.workspace.world_ab_finite_segment_square_overlap import (
    attempt,run,finite_clip,grid_for_face,START,DURATION,SAMPLE_COUNT,SCHEMA,
)
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_first_post_third_candidate import attempt as source22
from network.tests.test_world_ab_first_post_third_candidate import independent_check as verify22
from systems.workspace.world_ab_all_inward_finite_features import attempt as source23
from systems.workspace.world_ab_rotating_edge_face_endpoint import attempt as source24
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER
from systems.workspace.world_ab_first_post_third_candidate import ANGLES

VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
EPS=1e-9


def square_world(h,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    co,si=cos(theta),sin(theta)
    center=(h["contact_center"][0]+h["outgoing_velocity"][0]*t,
            h["contact_center"][1]+h["outgoing_velocity"][1]*t)
    return [(center[0]+co*x-si*y,center[1]+si*x+co*y)
            for x,y in VERTICES]


def independent_segments(parent,angle):
    first=source18(angle)["source_first_contact"]
    receiver=parent["source_receiver"]
    result=[]
    for name,n,anchor in (
        ("original_finite_face",first["normal"],WALL_CENTER),
        ("motion_derived_receiver",receiver["normal"],receiver["anchor"])
    ):
        tangent=(-n[1],n[0])
        result.append((name,[
            [anchor[0]-tangent[0]/2,anchor[1]-tangent[1]/2],
            [anchor[0]+tangent[0]/2,anchor[1]+tangent[1]/2],
        ]))
    return result


def sat_segment_square(h,segment,t):
    corners=square_world(h,t)
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    co,si=cos(theta),sin(theta)
    line=(segment[1][0]-segment[0][0],
          segment[1][1]-segment[0][1])
    size=hypot(*line)
    if size<1e-15:
        raise ValueError("original segment degenerated")
    axes=((co,si),(-si,co),(-line[1]/size,line[0]/size))
    for n in axes:
        p=[a*n[0]+b*n[1] for a,b in corners]
        q=[a*n[0]+b*n[1] for a,b in segment]
        if max(p)<min(q)-EPS or max(q)<min(p)-EPS:
            return False
    return True


def verify(case):
    angle=case.get("angle")
    if case.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("source trial or angle changed")
    old=source21(angle)
    parent22=source22(angle)
    verify22(parent22)
    parent23=source23(angle)
    parent24=source24(angle)
    declarations={
        "source_trial22_schema":parent22["schema"],
        "source_trial22_status":parent22["status"],
        "source_trial23_schema":parent23["schema"],
        "source_trial23_first_geometry":parent23["first_eligible_geometry"],
        "source_trial24_schema":parent24["schema"],
        "source_trial24_first_edge":parent24["first_eligible_edge"],
        "source_third_impulse":old["third_impulse"],
        "source_receiver":old["source_receiver"],
        "window_start":START,"window_end":DURATION,
        "sample_intervals_per_face":SAMPLE_COUNT,
        "original_24_by_6_world_preserved":True,
        "conditional_model_only":True,
        "model_positions_not_hardware":True,
        "physical_contact_witnessed":False,
        "fourth_impulse_solved":False,
        "new_receiver_created":False,
        "formally_certified_continuous_collision_detection":False,
    }
    if any(case.get(k)!=v for k,v in declarations.items()):
        raise ValueError("source relationship, finite controls or physical scope changed")
    if old["third_impulse"] is None:
        if (case.get("status")!="NO_ADMITTED_THIRD_IMPULSE" or
            case.get("face_results")!=[] or
            case.get("first_detected_bracket") is not None or
            case.get("finite_intersection_candidates")!=[] or
            case.get("onset_vs_original_vertex_candidate") is not None):
            raise ValueError("absent source impulse produced imaginary motion")
        return True
    if old["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("unwitnessed original third impulse")
    records=case.get("face_results")
    if type(records) is not list or len(records)!=2:
        raise ValueError("original two finite faces not preserved")
    first_candidates=[]
    for record,(label,segment) in zip(records,independent_segments(old,angle)):
        if record.get("face")!=label or record.get("segment")!=segment or (
            record.get("samples_checked")!=SAMPLE_COUNT+1):
            raise ValueError("original finite segment placement or grid changed")
        times=[START+(DURATION-START)*i/SAMPLE_COUNT
               for i in range(SAMPLE_COUNT+1)]
        marks=[sat_segment_square(old["third_impulse"],segment,t) for t in times]
        actual=sum(marks)
        if actual != record.get("intersecting_grid_samples"):
            raise ValueError("finite segment-square overlap counts differ from SAT")
        onset=next((i for i,flag in enumerate(marks) if flag),None)
        onset_time=round(times[onset],10) if onset is not None else None
        if onset_time != record.get("first_grid_intersection_at"):
            raise ValueError("first sampled overlap time altered")
        if record.get("start_intersected") is not marks[0]:
            raise ValueError("unresolved start overlap hidden")
        windows=[]
        started=None
        for i,flag in enumerate(marks):
            if flag and started is None:
                started=i
            if started is not None and (not flag or i==SAMPLE_COUNT):
                end=i-1 if not flag else i
                windows.append({
                    "first_sample_index":started,"last_sample_index":end,
                    "first_sample_time":round(times[started],10),
                    "last_sample_time":round(times[end],10),
                })
                started=None
        if record.get("sampled_intersection_windows")!=windows:
            raise ValueError("missing/extra finite contact grid interval")
        if record.get("continuous_absence_certified") is not False:
            raise ValueError("sampled gap misrepresented as continuous proof")
        bracket=record.get("first_transition_bracket")
        if onset is not None and onset>0:
            if type(bracket) is not dict:
                raise ValueError("detected onset missing transition bracket")
            lo,hi=times[onset-1],times[onset]
            root=bracket.get("bisected_transition_time")
            if (not isinstance(root,(int,float))
                or not lo-1e-8<=root<=hi+1e-8
                or abs(bracket.get("last_grid_separated_at",-99)-round(lo,10))>1e-8
                or abs(bracket.get("first_grid_intersection_at",-99)-round(hi,10))>1e-8
                or bracket.get("numerical_transition_not_exact_certified") is not True
                or not sat_segment_square(old["third_impulse"],segment,root+2e-8)):
                raise ValueError("inconsistent first finite-onset bracket")
            first_candidates.append({
                "face":label,"bracket":bracket,
                "kind":"FINITE_SOURCE_SEGMENT_SQUARE_INTERSECTION_CANDIDATE",
                "hardware_measured":False})
        elif bracket is not None:
            raise ValueError("invented bisection without detected crossing")
    first_candidates.sort(key=lambda r:(r["bracket"]["bisected_transition_time"],r["face"]))
    if case.get("finite_intersection_candidates")!=first_candidates:
        raise ValueError("source invented or removed a finite-intersection candidate")
    first=first_candidates[0] if first_candidates else None
    if case.get("first_detected_bracket")!=first:
        raise ValueError("first finite-intersection bracket changed")
    expected_comparison=None
    if first:
        b=first["bracket"]
        matching=[
            x["dt_after_third_impulse"]
            for x in parent23["eligible_geometry_roots"]
            if x["surface"]==first["face"] and
               x["feature_classification"]=="FINITE_FACE_INTERIOR_CANDIDATE"
        ]
        time=min(matching) if matching else None
        lo=b["last_grid_separated_at"]
        hi=b["first_grid_intersection_at"]
        relationship=("NO_PRIOR_VERTEX_CANDIDATE_ON_THIS_FINITE_FACE"
                      if time is None else
                      "SOURCE_VERTEX_TIME_INSIDE_FIRST_GRID_BRACKET"
                      if lo-3e-7<=time<=hi+3e-7 else
                      "SOURCE_VERTEX_TIME_BEFORE_FIRST_GRID_BRACKET"
                      if time<lo else
                      "SOURCE_VERTEX_TIME_AFTER_FIRST_GRID_BRACKET")
        expected_comparison={
            "face":first["face"],
            "source_first_finite_vertex_time":time,
            "first_grid_clear_time":lo,
            "first_grid_overlap_time":hi,
            "relationship":relationship,
            "same_face_only":True,
            "numerical_grid_not_certified_first_contact":True,
        }
    if case.get("onset_vs_original_vertex_candidate")!=expected_comparison:
        raise ValueError("same finite face timing comparison differs")
    count=sum(r["intersecting_grid_samples"]>0 for r in records)
    if case.get("faces_with_sampled_intersection")!=count:
        raise ValueError("observed finite-face count wrong")
    status=("PREEXISTING_FINITE_INTERSECTION_AT_WINDOW_START_UNRESOLVED"
            if any(r["start_intersected"] for r in records)
            else "FINITE_MODEL_INTERSECTION_TRANSITION_BRACKET_DETECTED"
            if first_candidates
            else "NO_FINITE_INTERSECTION_DETECTED_ON_GRID_ONLY")
    if case.get("status")!=status:
        raise ValueError("finite geometry status promoted")
    return True


class Trial25IndependentFiniteGeometry(unittest.TestCase):
    def test_static_segment_mid_square_intersection(self):
        h={"contact_center":[0.,0.],"contact_orientation":0.,
           "outgoing_velocity":[1.,0.],"outgoing_spin":0.}
        face=[[.4,-.1],[.4,.1]]
        self.assertFalse(finite_clip(h,face,.10)["overlap"])
        self.assertFalse(sat_segment_square(h,face,.10))
        self.assertTrue(finite_clip(h,face,.16)["overlap"])
        self.assertTrue(sat_segment_square(h,face,.16))
        grid=grid_for_face(h,"test-face",face)
        self.assertGreater(grid["intersecting_grid_samples"],0)
        self.assertIsNotNone(grid["first_transition_bracket"])

    def test_all_original_model_cases_agree_between_sat_and_clip(self):
        native=run()
        self.assertEqual(native["schema"],SCHEMA)
        self.assertEqual(native["source_third_impulse_cases"],6)
        self.assertEqual(native["no_source_third_impulse_controls"],2)
        self.assertEqual(native["finite_intersection_grid_cases"]+
                         native["finite_grid_no_intersection_cases"],6)
        self.assertEqual(native["material_observations"],0)
        self.assertEqual(native["fourth_impulses_solved"],0)
        for case in native["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_source_missing_impulse_cannot_create_new_overlap(self):
        for a in (0.,20.):
            result=attempt(a)
            self.assertEqual(result["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertEqual(result["face_results"],[])

    def test_false_hardware_and_forged_finite_overlap_rejected(self):
        base=attempt(7.5)
        for key,value in (
            ("physical_contact_witnessed",True),
            ("fourth_impulse_solved",True),
            ("window_end",1.),
            ("formally_certified_continuous_collision_detection",True),
            ("model_positions_not_hardware",False),
        ):
            x=deepcopy(base);x[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(x)
        x=deepcopy(base)
        if x["face_results"]:
            x["face_results"][0]["intersecting_grid_samples"]+=1
            with self.assertRaises(ValueError):verify(x)


if __name__=="__main__":
    unittest.main()
