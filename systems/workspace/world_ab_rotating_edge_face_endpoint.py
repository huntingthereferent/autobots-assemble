"""WORLD24 — finite face endpoint meeting a rotating square edge.

The original WORLD21 conditional third impulse and existing WORLD22 projection
are the sole source of virtual motion. This lane checks a different finite
geometry: either endpoint of either *existing* finite source face against any
of the four moving square edge interiors. A vertex crossing a face's infinite
supporting line is not sufficient for this relationship, and an endpoint
meeting an extension of a square edge is not an edge contact.

Numerical sign changes and bisection only, bounded to [.008, .25] virtual
time after the third hypothetical impulse. Record all alternatives and
unsupported tangencies; do not select a fourth impulse or actual material hit.
"""
from __future__ import annotations

from math import hypot, isfinite
from systems.workspace.world_ab_first_post_third_candidate import (
    ANGLES, DURATION, VERTICES, surfaces, pose, attempt as trial22, rd
)
from systems.workspace.world_ab_third_contact import attempt as trial21

SCHEMA = "world-ab-finite-face-endpoint-rotating-square-edge/v1"
START = .008
SAMPLES = 4096
TOL = 3e-7
EDGE_ORDER = (0, 2, 3, 1)
KINDS = (
    "FACE_ENDPOINT_TO_SQUARE_EDGE_INTERIOR_CANDIDATE",
    "SQUARE_VERTEX_FACE_ENDPOINT_UNRESOLVED",
    "SQUARE_EDGE_SUPPORT_LINE_OUTSIDE_EDGE_UNRESOLVED",
)


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def endpoints(source,angle):
    result=[]
    for name,n,anchor,span in surfaces(source,angle):
        if span is None:
            continue
        tangent=(-n[1],n[0])
        for end,sign in enumerate((-1.,1.)):
            result.append((name,end,
                (anchor[0]+sign*.5*span*tangent[0],
                 anchor[1]+sign*.5*span*tangent[1])))
    return result


def edge_vertices(h,edge,t):
    i=EDGE_ORDER[edge]
    j=EDGE_ORDER[(edge+1)%4]
    return pose(h,VERTICES[i],t),pose(h,VERTICES[j],t)


def edge_signed_and_param(h,endpoint,edge,t):
    a,b=edge_vertices(h,edge,t)
    vec=(b[0]-a[0],b[1]-a[1])
    length=hypot(*vec)
    if length<=0:
        raise ValueError("source square edge degenerated")
    to=(endpoint[0]-a[0],endpoint[1]-a[1])
    # CCW square: a stationary point starts outside this moving edge
    # when signed cross(edge, point-from-edge) is negative.
    return cross(vec,to)/length, dot(vec,to)/(length*length)


def inward_endpoint_edge_roots(h,p,edge,start=START,stop=DURATION,samples=SAMPLES):
    """Numerical roots of outside-to-inside crossing of a moving square edge."""
    if not 0<=start<stop<=DURATION or samples<16:
        raise ValueError("invalid bounded projection")
    candidates=[]
    watch=[]
    left=start
    previous=edge_signed_and_param(h,p,edge,left)[0]
    for k in range(1,samples+1):
        right=start+(stop-start)*k/samples
        current=edge_signed_and_param(h,p,edge,right)[0]
        if previous < -1e-9 and current > 1e-9:
            lo,hi=left,right
            for _ in range(51):
                middle=(lo+hi)/2
                if edge_signed_and_param(h,p,edge,middle)[0]<0:
                    lo=middle
                else:
                    hi=middle
            t=(lo+hi)/2
            if not candidates or t-candidates[-1]>1e-8:
                candidates.append(t)
        elif abs(current)<1e-7:
            watch.append(rd(right))
        left,previous=right,current
    return candidates,watch


def classify(u):
    if u < -TOL or u > 1.+TOL:
        return KINDS[2]
    if u<=TOL or u>=1.-TOL:
        return KINDS[1]
    return KINDS[0]


def attempt(angle):
    parent=trial22(angle)
    previous=trial21(angle)
    report={
        "schema":SCHEMA,"angle":rd(angle),
        "source_trial22_schema":parent["schema"],
        "source_trial22_status":parent["status"],
        "source_trial22_first_crossing":parent["first_crossing"],
        "source_third_impulse":previous["third_impulse"],
        "source_receiver":previous["source_receiver"],
        "observation_start":START,"observation_end":DURATION,
        "square_edges_examined":4,"source_finite_faces_examined":2,
        "source_face_endpoints_per_face":2,
        "original_source_and_world_unchanged":True,
        "conditional_ballistic_model_only":True,
        "physical_contact_witnessed":False,
        "fourth_impulse_calculated":False,
        "new_receiver_constructed":False,
        "formal_root_completeness_certificate":False,
    }
    if previous["third_impulse"] is None:
        if parent["status"]!="NO_ADMITTED_THIRD_IMPULSE":
            raise ValueError("no source third impulse but Trial22 reports movement")
        return {**report,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "endpoint_edge_roots":[],"eligible_edge_candidates":[],
                "first_eligible_edge":None,"coearliest_edge_candidates":[],
                "edge_extension_roots":[],"vertex_endpoint_uncertainties":[],
                "near_zero_sample_watches":[],"first_geometric_source_candidate":None,
                "conditional_model_pairs_checked":0}
    if previous["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("original conditional third impulse is unresolved")
    h=previous["third_impulse"]
    roots,watches=[],[]
    count=0
    for face,endpoint_idx,p in endpoints(previous,angle):
        for edge in range(4):
            count+=1
            ts,near=inward_endpoint_edge_roots(h,p,edge)
            for t in ts:
                distance,u=edge_signed_and_param(h,p,edge,t)
                if not (isfinite(t) and isfinite(u) and abs(distance)<1e-6):
                    raise ValueError("nonfinite or noncontact numerical edge root")
                roots.append({
                    "face":face,"face_endpoint_index":endpoint_idx,
                    "square_edge_index":edge,
                    "dt_after_third_impulse":rd(t),
                    "absolute_virtual_time":rd(h["contact_absolute_virtual_time"]+t),
                    "edge_fraction":rd(u),
                    "edge_signed_gap_residual":rd(distance),
                    "feature_classification":classify(u),
                    "conditionally_modeled":True,
                    "material_contact_witnessed":False,
                })
            for t in near:
                watches.append({
                    "face":face,"face_endpoint_index":endpoint_idx,
                    "square_edge_index":edge,
                    "sample_time":t,
                    "geometry_unresolved":True,
                })
    key=lambda x:(x["dt_after_third_impulse"],x["face"],
                  x["face_endpoint_index"],x["square_edge_index"])
    roots.sort(key=key)
    eligible=[x for x in roots if x["feature_classification"]==KINDS[0]]
    extension=[x for x in roots if x["feature_classification"]==KINDS[2]]
    unresolved=[x for x in roots if x["feature_classification"]==KINDS[1]]
    first=eligible[0] if eligible else None
    coearliest=[x for x in eligible if abs(
        x["dt_after_third_impulse"]-first["dt_after_third_impulse"])<=1e-7
        ] if first else []
    v=parent["all_source_line_crossings"]
    eligible_vertex=[x for x in v if x["feature_classification"] in (
        "FINITE_FACE_INTERIOR_CANDIDATE","WORLD_PERIMETER_CANDIDATE")]
    earlier_vertex=eligible_vertex[0] if eligible_vertex else None
    if first is None:
        status="NO_ELIGIBLE_ENDPOINT_EDGE_ROOT_IN_BOUNDED_SAMPLES"
    elif len(coearliest)>1:
        status="COEARLIEST_ENDPOINT_EDGE_FEATURES_UNRESOLVED"
    elif earlier_vertex is None or first["dt_after_third_impulse"]+1e-7<earlier_vertex["dt_after_third_impulse"]:
        status="ENDPOINT_EDGE_CANDIDATE_BEFORE_VERTEX_LINE_CANDIDATE"
    else:
        status="ENDPOINT_EDGE_CANDIDATE_NOT_EARLIER_THAN_VERTEX_LINE"
    return {**report,"status":status,
            "endpoint_edge_roots":roots,"eligible_edge_candidates":eligible,
            "first_eligible_edge":first,"coearliest_edge_candidates":coearliest,
            "edge_extension_roots":extension,
            "vertex_endpoint_uncertainties":unresolved,
            "near_zero_sample_watches":watches,
            "first_geometric_source_candidate":earlier_vertex,
            "conditional_model_pairs_checked":count}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "conditional_source_inputs":sum(c["source_third_impulse"] is not None for c in cases),
        "without_source_impulse":sum(c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
        "cases_with_eligible_endpoint_edge":sum(c["first_eligible_edge"] is not None for c in cases),
        "cases_without_eligible_endpoint_edge":sum(
            c["source_third_impulse"] is not None and c["first_eligible_edge"] is None for c in cases),
        "edge_candidates_preceding_vertex_line":sum(
            c["status"]=="ENDPOINT_EDGE_CANDIDATE_BEFORE_VERTEX_LINE_CANDIDATE" for c in cases),
        "source_edge_pairs_checked":sum(c["conditional_model_pairs_checked"] for c in cases),
        "numerical_endpoint_edge_roots":sum(len(c["endpoint_edge_roots"]) for c in cases),
        "extension_only_roots":sum(len(c["edge_extension_roots"]) for c in cases),
        "vertex_endpoint_uncertainties":sum(len(c["vertex_endpoint_uncertainties"]) for c in cases),
        "physical_measurements":0,"fourth_impulses_selected":0,
        "new_receivers_built":0,"new_engine_or_world":False}
