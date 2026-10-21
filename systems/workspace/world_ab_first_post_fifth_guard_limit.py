"""WORLD38 — first mathematically bounded original clearance-guard limit.

Do not lengthen WORLD37 by guesswork. Its one 10° conditional, unselected
fifth-response model has nominally cleared every original plane/corner to
post-fifth t=.058. Enumerate analytic stationary times for all 24 original
normal gaps on [.058,.25] and find the FIRST time any signed gap reaches the
original positive guard. An inward clearance-guard crossing is a *limit of a
sufficient separation condition*, not an observed sixth contact.

Both original finite segments remain finite; supporting-line crossings
outside their span cannot be relabeled finite material impacts. No new
receiver or response, no beyond-first-limit motion, no real measurement.
"""
from __future__ import annotations

from math import acos,atan2,ceil,cos,sin,hypot,isfinite,pi

from systems.workspace.world_ab_post_fifth_contiguous_prefix import (
    attempt as previous, SCHEMA as SOURCE37,
    model_at_conditional_fifth,original_planes,
    GUARD as SOURCE_GUARD
)
from systems.workspace.world_ab_whole_contact_configuration import attempt as fifth_source
from systems.workspace.world_ab_third_contact import attempt as trial21, ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-post-fifth-first-original-guard-limit/v1"
START=.058
END=.25
GUARD=SOURCE_GUARD
TIME_TIE=2e-7
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):return round(float(x),12)


def dot(a,b):return a[0]*b[0]+a[1]*b[1]


def series(model,corner,normal,anchor):
    x,y=corner
    a=model["theta"]
    px=x*cos(a)-y*sin(a)
    py=x*sin(a)+y*cos(a)
    return (
        dot((model["center"][0]-anchor[0],
             model["center"][1]-anchor[1]),normal),
        dot(model["velocity"],normal),
        px*normal[0]+py*normal[1],
        -py*normal[0]+px*normal[1],
        model["spin"],
    )


def gap(q,t):
    c,v,a,b,w=q
    return c+v*t+a*cos(w*t)+b*sin(w*t)


def derivative(q,t):
    _,v,a,b,w=q
    return v+w*(-a*sin(w*t)+b*cos(w*t))


def roots_of_derivative(q,start,end):
    _,v,a,b,w=q
    result=[start,end]
    amplitude=hypot(a,b)
    if abs(w)<1e-12 or amplitude<1e-12:
        return result
    ratio=-v/(w*amplitude)
    if abs(ratio)>1:return result
    theta=atan2(a,b)
    alpha=acos(max(-1.,min(1.,ratio)))
    count=ceil(abs(w)*end/(2*pi))+7
    for k in range(-count,count+1):
        for sign in (-1,1):
            t=(sign*alpha-theta+2*pi*k)/w
            if start+1e-13<t<end-1e-13:
                result.append(t)
    return sorted(set(result))


def first_guard_limit(q):
    marks=roots_of_derivative(q,START,END)
    if gap(q,START)<=GUARD:
        raise ValueError("WORLD37 source clear prefix did not reach positive initial gap")
    first=None
    for a,b in zip(marks,marks[1:]):
        ga,gb=gap(q,a),gap(q,b)
        if ga<=GUARD:
            first=a
            break
        if gb>GUARD:continue
        l,r=a,b
        for _ in range(65):
            m=(l+r)/2
            if gap(q,m)>GUARD:l=m
            else:r=m
        first=(l+r)/2
        break
    if first is None and gap(q,marks[-1])<=GUARD:
        first=marks[-1]
    return first,len(marks)-2,min(gap(q,x) for x in marks)


def original_pose(model,index,t):
    x,y=VERTICES[index]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    return (model["center"][0]+model["velocity"][0]*t+c*x-s*y,
            model["center"][1]+model["velocity"][1]*t+s*x+c*y)


def attempt(angle):
    prior=previous(angle)
    before=fifth_source(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial37_schema":SOURCE37,
        "source_trial37_status":prior["status"],
        "source_original_trial37_supported_prefix_end":prior["supported_prefix_end"],
        "original_world":[24.,6.],
        "source_finite_face_count":2,
        "source_perimeter_plane_count":4,
        "previous_nominally_supported_time":START,
        "declared_max_horizon_after_unselected_fifth":END,
        "positive_source_guard":GUARD,
        "corner_plane_count":24,
        "source_model_is_counterfactual":True,
        "material_fifth_impact_observed":False,
        "sixth_material_contact_observed":False,
        "sixth_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_guard_limit_motion_certified":False,
        "formal_outward_rounded_certificate":False,
    }
    empty={
        "original_24_analytic_gap_records":[],
        "first_source_guard_limit":None,
        "coearliest_source_guard_features":[],
        "nominally_supported_until":None,
        "all_original_supporting_lines_clear_through_horizon":False,
    }
    if before["conditional_fifth_response"] is None:
        if prior["status"]!="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE":
            raise ValueError("unqualified original source falsely progressed")
        return {**base,**empty,"status":"NO_SOURCE_FIFTH_RESPONSE"}
    if (prior["status"]!="EXTENDED_CONDITIONAL_FIFTH_MODEL_CLEARANCE_SUPPORTED"
        or not prior["full_new_interval_supported"]
        or abs(prior["supported_prefix_end"]-START)>1e-9):
        return {**base,**empty,"status":"SOURCE_PREFIX_NOT_FULLY_SUPPORTED"}
    model=model_at_conditional_fifth(before,trial21(angle))
    planes=original_planes(trial21(angle),angle)
    all_records=[]
    candidates=[]
    for name,n,anchor,span in planes:
        tangent=(-n[1],n[0])
        for index,corner in enumerate(VERTICES):
            q=series(model,corner,n,anchor)
            if not all(isfinite(v) for v in q):
                raise ValueError("original source nominal trajectory nonfinite")
            t,partitions,min_gap=first_guard_limit(q)
            feature=None
            if t is not None:
                p=original_pose(model,index,t)
                along=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
                feature={
                    "source_plane":name,
                    "source_corner_index":index,
                    "guard_limit_time":rd(t),
                    "gap_at_guard_limit":rd(gap(q,t)),
                    "normal_rate_at_limit":rd(derivative(q,t)),
                    "world_corner_at_limit":[rd(p[0]),rd(p[1])],
                    "source_plane_is_finite":span is not None,
                    "finite_face_tangent_coordinate":rd(along) if span is not None else None,
                    "finite_face_intersecting_span_at_limit":(
                        abs(along)<=span/2+1e-8 if span is not None else None),
                    "physical_contact":False,
                }
                candidates.append(feature)
            all_records.append({
                "source_plane":name,
                "source_corner_index":index,
                "source_plane_is_finite":span is not None,
                "at_start_signed_gap":rd(gap(q,START)),
                "at_horizon_signed_gap":rd(gap(q,END)),
                "stationary_partition_count":partitions,
                "minimum_analytic_stationary_gap":rd(min_gap),
                "first_guard_limit":feature,
                "never_assume_sixth_collision":True,
            })
    if len(all_records)!=24:
        raise ValueError("not all 24 original source constraints retained")
    candidates.sort(key=lambda x:(x["guard_limit_time"],x["source_plane"],x["source_corner_index"]))
    first=candidates[0] if candidates else None
    tied=([x for x in candidates if abs(x["guard_limit_time"]-first["guard_limit_time"])<=TIME_TIE]
          if first else [])
    end=first["guard_limit_time"] if first else END
    return {
        **base,
        "status":("FIRST_ORIGINAL_CLEARANCE_GUARD_BOUNDARY" if first else
                  "NO_ORIGINAL_PLANE_GUARD_LIMIT_THROUGH_DECLARED_HORIZON"),
        "original_24_analytic_gap_records":all_records,
        "first_source_guard_limit":first,
        "coearliest_source_guard_features":tied,
        "nominally_supported_until":end,
        "all_original_supporting_lines_clear_through_horizon":first is None,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "source_qualified_cases":sum(c["nominally_supported_until"] is not None for c in cases),
        "first_guard_limit_cases":sum(c["first_source_guard_limit"] is not None for c in cases),
        "complete_horizon_cases":sum(c["all_original_supporting_lines_clear_through_horizon"] for c in cases),
        "inactive_original_cases":sum(c["status"]=="NO_SOURCE_FIFTH_RESPONSE" for c in cases),
        "physical_sixth_contacts":0,"sixth_impulses":0,
        "new_receivers":0,"world_engine_built":False,
    }
