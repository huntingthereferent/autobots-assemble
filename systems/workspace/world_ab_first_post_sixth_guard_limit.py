"""WORLD42: first original post-sixth positive-gap guard limit.

Only if WORLD41 independently supported the entire first .025 conditional
post-sixth virtual window, enumerate all original 24 corner-plane signed
normal gaps to t=.25 under the SAME unselected sixth-response free-flight
model. Derive all stationary phases analytically; stop at the earliest gap
equal to the positive guard, or support the finite horizon if none.
A supporting-line guard is not a zero-gap or seventh material contact.
"""
from __future__ import annotations

from math import isfinite
from systems.workspace.world_ab_post_sixth_local_clearance import (
    attempt as source41, source_model, SCHEMA as SOURCE41, WINDOW as START)
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as source40
from systems.workspace.world_ab_post_fifth_contiguous_prefix import original_planes
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES
from systems.workspace.world_ab_first_post_fifth_guard_limit import (
    series, roots_of_derivative, gap, derivative, original_pose, VERTICES)
SCHEMA="world-ab-first-original-post-sixth-guard-limit/v1"
END=.25
GUARD=1e-7
TIME_TIE=2e-7


def rd(x):return round(float(x),12)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]


def first_guard(q):
    critical=roots_of_derivative(q,START,END)
    if gap(q,START)<=GUARD:
        raise ValueError("WORLD41 complete prefix did not retain positive gap")
    root=None
    for lo,hi in zip(critical,critical[1:]):
        if gap(q,lo)<=GUARD:
            root=lo;break
        if gap(q,hi)>GUARD:continue
        a,b=lo,hi
        for _ in range(72):
            m=(a+b)/2
            if gap(q,m)>GUARD:a=m
            else:b=m
        root=(a+b)/2;break
    return root,len(critical)-2,min(gap(q,t) for t in critical)


def attempt(angle):
    previous=source41(angle)
    before=source40(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "original_trial41_schema":SOURCE41,
        "original_trial41_status":previous["status"],
        "source_trial41_end":previous["supported_contiguous_prefix_end"],
        "original_world":[24.,6.],
        "source_finite_faces":2,"source_perimeter_planes":4,
        "first_supported_post_sixth_window":START,
        "declared_max_post_sixth_horizon":END,
        "original_positive_guard":GUARD,
        "source_original_plane_corner_count":24,
        "counterfactual_sixth_response_only":True,
        "material_sixth_impact_observed":False,
        "material_seventh_contact_observed":False,
        "seventh_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_admitted":False,
        "exact_outward_rounded_interval_proof":False,
    }
    empty={
        "original_24_guard_searches":[],
        "first_original_guard_limit":None,
        "coearliest_original_features":[],
        "supported_horizon_endpoint":None,
        "all_original_guards_clear_through_horizon":False,
    }
    if before["conditional_sixth_response"] is None:
        if previous["status"]!="NO_SOURCE_SIXTH_RESPONSE":
            raise ValueError("original sixth ancestry inconsistent")
        return {**base,**empty,"status":"NO_ADMITTED_SIXTH_SOURCE"}
    if (previous["status"]!="CONDITIONAL_SIXTH_FIRST_WINDOW_NOMINALLY_SEPARATED"
        or previous["full_declared_window_supported"] is not True
        or abs(previous["supported_contiguous_prefix_end"]-START)>1e-9):
        return {**base,**empty,"status":"FIRST_POST_SIXTH_SOURCE_WINDOW_UNRESOLVED"}
    model,world=source_model(angle,before)
    planes=original_planes(world,angle)
    if len(planes)!=6 or sum(p[3] is not None for p in planes)!=2:
        raise ValueError("original world faces/perimeter changed")
    rows=[]
    crossing=[]
    for name,n,anchor,span in planes:
        tangent=(-n[1],n[0])
        for idx,vertex in enumerate(VERTICES):
            q=series(model,vertex,n,anchor)
            if any(not isfinite(v) for v in q):
                raise ValueError("original guard model became nonfinite")
            t,partitions,min_gap=first_guard(q)
            feature=None
            if t is not None:
                point=original_pose(model,idx,t)
                along=dot((point[0]-anchor[0],point[1]-anchor[1]),tangent)
                feature={
                    "source_plane":name,"source_corner_index":idx,
                    "guard_limit_time":rd(t),
                    "signed_gap_at_guard_limit":rd(gap(q,t)),
                    "incoming_normal_rate":rd(derivative(q,t)),
                    "model_corner_location":[rd(x) for x in point],
                    "original_face_finite":span is not None,
                    "finite_face_tangent_coordinate":rd(along) if span is not None else None,
                    "within_original_finite_span":(
                        abs(along)<=span/2+1e-8 if span is not None else None),
                    "material_seventh_contact":False
                }
                crossing.append(feature)
            rows.append({
                "source_plane":name,"source_corner_index":idx,
                "original_face_finite":span is not None,
                "start_signed_normal_gap":rd(gap(q,START)),
                "horizon_signed_normal_gap":rd(gap(q,END)),
                "analytic_stationary_partition_count":partitions,
                "analytic_interval_minimum_gap":rd(min_gap),
                "first_original_guard_feature":feature,
                "not_an_observed_material_contact":True
            })
    if len(rows)!=24:raise ValueError("source plane/corner records missing")
    crossing.sort(key=lambda x:(x["guard_limit_time"],x["source_plane"],x["source_corner_index"]))
    first=crossing[0] if crossing else None
    tied=[z for z in crossing if abs(z["guard_limit_time"]-first["guard_limit_time"])<=TIME_TIE] if first else []
    return {
        **base,
        "status":("FIRST_POST_SIXTH_ORIGINAL_GUARD_LIMIT" if first else
                  "POST_SIXTH_ORIGINAL_GUARDS_CLEAR_THROUGH_HORIZON"),
        "original_24_guard_searches":rows,
        "first_original_guard_limit":first,
        "coearliest_original_features":tied,
        "supported_horizon_endpoint":first["guard_limit_time"] if first else END,
        "all_original_guards_clear_through_horizon":first is None,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "eligible_post_sixth_models":sum(z["supported_horizon_endpoint"] is not None for z in cases),
        "first_guard_limit_models":sum(z["first_original_guard_limit"] is not None for z in cases),
        "all_original_guard_full_horizon_models":sum(z["all_original_guards_clear_through_horizon"] for z in cases),
        "unresolved_previous_window_models":sum(z["status"]=="FIRST_POST_SIXTH_SOURCE_WINDOW_UNRESOLVED" for z in cases),
        "inactive_source_controls":sum(z["status"]=="NO_ADMITTED_SIXTH_SOURCE" for z in cases),
        "real_seventh_impacts":0,"seventh_impulses":0,
        "new_receivers":0,"new_world_engine":False
    }
