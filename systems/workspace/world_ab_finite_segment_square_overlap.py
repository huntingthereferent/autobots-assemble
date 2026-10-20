"""WORLD25 — actual finite-segment vs rotating-square model overlap checks.

Stay in the original WORLD 24x6 space with the already source-owned two finite
faces, conditional Trial21 outgoing rigid-square motion, and [.008, .25]
nominal-time window. This checks finite shape intersection directly rather
than treating an infinite supporting-line crossing as a finite contact.

Clip each static finite source segment in the moving square's *local* frame.
The independent witness uses convex separating-axis projection instead.
Numerical grid/bisection gives *detected* brackets, not certified completeness,
contact forces, actual material outcomes, or a fourth impulse.
"""
from __future__ import annotations

from math import cos, sin, isfinite
from systems.workspace.world_ab_first_post_third_candidate import (
    ANGLES, DURATION, attempt as source22, surfaces, rd
)
from systems.workspace.world_ab_all_inward_finite_features import attempt as source23
from systems.workspace.world_ab_rotating_edge_face_endpoint import attempt as source24
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA = "world-ab-finite-segment-rotating-square-intersection/v1"
START = .008
SAMPLE_COUNT = 2048
TOL = 1e-9
KIND = "FINITE_SOURCE_SEGMENT_SQUARE_INTERSECTION_CANDIDATE"


def static_faces(ancestor, angle):
    result=[]
    for name,n,anchor,span in surfaces(ancestor,angle):
        if span is not None:
            tangent=(-n[1],n[0])
            result.append((name, [
                [anchor[0]-span*tangent[0]/2,anchor[1]-span*tangent[1]/2],
                [anchor[0]+span*tangent[0]/2,anchor[1]+span*tangent[1]/2]]))
    return result


def model_pose(h,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    x=h["contact_center"][0]+h["outgoing_velocity"][0]*t
    y=h["contact_center"][1]+h["outgoing_velocity"][1]*t
    return (x,y,theta)


def local_point(p,pose):
    cx,cy,theta=pose
    c,s=cos(theta),sin(theta)
    dx,dy=p[0]-cx,p[1]-cy
    return (dx*c+dy*s,-dx*s+dy*c)


def finite_clip(h,segment,t):
    """Liang–Barsky clip of *finite* segment against oriented finite square."""
    pose=model_pose(h,t)
    a=local_point(segment[0],pose)
    b=local_point(segment[1],pose)
    low,high=0.,1.
    for i in (0,1):
        va,vb=a[i],b[i]
        step=vb-va
        if abs(step)<1e-14:
            if va < -HALF-TOL or va > HALF+TOL:
                return {"overlap":False,"entry":None,"exit":None}
            continue
        enter=(-HALF-va)/step
        leave=(HALF-va)/step
        if enter>leave:
            enter,leave=leave,enter
        low=max(low,enter)
        high=min(high,leave)
        if high < low-TOL:
            return {"overlap":False,"entry":None,"exit":None}
    if high < -TOL or low > 1+TOL:
        return {"overlap":False,"entry":None,"exit":None}
    return {"overlap":True,"entry":rd(max(0.,low)),
            "exit":rd(min(1.,high))}


def grid_for_face(h,name,segment):
    """Finite detection grid, plus first transition bracketing, no free-flight proof."""
    times=[START+(DURATION-START)*i/SAMPLE_COUNT
           for i in range(SAMPLE_COUNT+1)]
    flags=[finite_clip(h,segment,t)["overlap"] for t in times]
    clusters=[]
    start=None
    for i,present in enumerate(flags):
        if present and start is None:
            start=i
        if start is not None and (not present or i==SAMPLE_COUNT):
            end=i-1 if not present else i
            clusters.append({
                "first_sample_index":start,
                "last_sample_index":end,
                "first_sample_time":rd(times[start]),
                "last_sample_time":rd(times[end]),
            })
            start=None
    bracket=None
    if clusters:
        first=clusters[0]["first_sample_index"]
        if first>0:
            lo,hi=times[first-1],times[first]
            for _ in range(48):
                mid=(lo+hi)/2
                if finite_clip(h,segment,mid)["overlap"]:
                    hi=mid
                else:
                    lo=mid
            clip=finite_clip(h,segment,hi)
            bracket={
                "last_grid_separated_at":rd(times[first-1]),
                "first_grid_intersection_at":rd(times[first]),
                "bisected_transition_time":rd(hi),
                "source_finite_clip_entry_fraction":clip["entry"],
                "source_finite_clip_exit_fraction":clip["exit"],
                "numerical_transition_not_exact_certified":True,
            }
    return {
        "face":name,"segment":segment,
        "samples_checked":SAMPLE_COUNT+1,
        "intersecting_grid_samples":sum(flags),
        "first_grid_intersection_at":rd(times[clusters[0]["first_sample_index"]])
                                     if clusters else None,
        "sampled_intersection_windows":clusters,
        "first_transition_bracket":bracket,
        "start_intersected":bool(flags[0]),
        "continuous_absence_certified":False,
    }


def attempt(angle):
    parent=source21(angle)
    before22=source22(angle)
    before23=source23(angle)
    before24=source24(angle)
    base={
        "schema":SCHEMA,"angle":rd(angle),
        "source_trial22_schema":before22["schema"],
        "source_trial22_status":before22["status"],
        "source_trial23_schema":before23["schema"],
        "source_trial23_first_geometry":before23["first_eligible_geometry"],
        "source_trial24_schema":before24["schema"],
        "source_trial24_first_edge":before24["first_eligible_edge"],
        "source_third_impulse":parent["third_impulse"],
        "source_receiver":parent["source_receiver"],
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
    if parent["third_impulse"] is None:
        if before22["status"]!="NO_ADMITTED_THIRD_IMPULSE":
            raise ValueError("original third impulse absent but later candidate present")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "face_results":[],"first_detected_bracket":None,
                "faces_with_sampled_intersection":0,
                "finite_intersection_candidates":[]}
    if parent["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("unresolved conditional third impulse cannot move")
    h=parent["third_impulse"]
    records=[grid_for_face(h,name,segment)
             for name,segment in static_faces(parent,angle)]
    if len(records)!=2:
        raise ValueError("original finite faces missing")
    candidates=[
        {"face":r["face"],"bracket":r["first_transition_bracket"],
         "kind":KIND,"hardware_measured":False}
        for r in records if r["first_transition_bracket"] is not None
    ]
    candidates.sort(key=lambda x:(x["bracket"]["bisected_transition_time"],
                                  x["face"]))
    if any(r["start_intersected"] for r in records):
        status="PREEXISTING_FINITE_INTERSECTION_AT_WINDOW_START_UNRESOLVED"
    elif candidates:
        status="FINITE_MODEL_INTERSECTION_TRANSITION_BRACKET_DETECTED"
    else:
        status="NO_FINITE_INTERSECTION_DETECTED_ON_GRID_ONLY"
    return {**base,"status":status,
            "face_results":records,
            "first_detected_bracket":candidates[0] if candidates else None,
            "faces_with_sampled_intersection":sum(
                r["intersecting_grid_samples"]>0 for r in records),
            "finite_intersection_candidates":candidates}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "source_third_impulse_cases":sum(
                c["source_third_impulse"] is not None for c in cases),
            "no_source_third_impulse_controls":sum(
                c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
            "finite_intersection_grid_cases":sum(
                c["faces_with_sampled_intersection"]>0 for c in cases),
            "finite_grid_no_intersection_cases":sum(
                c["source_third_impulse"] is not None and
                c["faces_with_sampled_intersection"]==0 for c in cases),
            "total_intersecting_grid_samples":sum(
                sum(r["intersecting_grid_samples"] for r in c["face_results"])
                for c in cases),
            "fourth_impulses_solved":0,"material_observations":0,
            "physical_receivers_constructed":0,"new_engine_or_world":False}
