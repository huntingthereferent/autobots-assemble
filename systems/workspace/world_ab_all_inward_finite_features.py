"""WORLD23: all inward roots and finite-feature filtering after source Trial22.

Same original WORLD21 conditional third impulse, original two finite faces,
and 24 x 6 bounded world. Trial22 retained only the *first* inward root for
each vertex / supporting line, including roots outside finite face endpoints.

Enumerate every positive-to-negative root within the SAME 0.25 nominal
projection. Classify all, separate interior finite-face / world-boundary
candidates from crossings outside a finite face, and retain endpoint or
near-tangent uncertainty. No fourth impulse, new receiver, material event,
collision response, or continuation beyond an actual source-certified impact.
"""
from __future__ import annotations

from math import isfinite
from systems.workspace.world_ab_first_post_third_candidate import (
    attempt as source22, ANGLES, DURATION, ROOT_TOL, TIE_TOL, VERTICES,
    surfaces, gap_terms, gap_value, gap_rate, stationary, pose, classify, rd
)
from systems.workspace.world_ab_third_contact import attempt as source21

SCHEMA = "world-ab-all-inward-roots-finite-feature-audit/v1"
SOURCE22 = "world-ab-first-candidate-after-conditional-third/v1"
SELECTABLE_GEOMETRY = ("FINITE_FACE_INTERIOR_CANDIDATE",
                       "WORLD_PERIMETER_CANDIDATE")
OUTSIDE = "SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED"
ENDPOINT = "ENDPOINT_FEATURE_UNRESOLVED"
ROOT_EPS = 1e-9
EDGE_TOL = 1e-7


def inward_roots(q):
    """All interior positive-to-negative roots of each monotonic gap segment."""
    times = stationary(q)
    crossings = []
    for left, right in zip(times, times[1:]):
        gl, gr = gap_value(q, left), gap_value(q, right)
        if gl <= ROOT_EPS or gr >= -ROOT_EPS:
            continue
        a,b = left,right
        for _ in range(58):
            middle=(a+b)/2
            if gap_value(q,middle)>0:
                a=middle
            else:
                b=middle
        t=(a+b)/2
        if t>ROOT_EPS and t<=DURATION and gap_rate(q,t)<-1e-7:
            if not crossings or abs(t-crossings[-1])>ROOT_EPS:
                crossings.append(t)
    unresolved_tangencies = [
        {"time":rd(t),"signed_gap":rd(gap_value(q,t))}
        for t in times[1:-1]
        if abs(gap_value(q,t))<=EDGE_TOL
    ]
    return crossings, unresolved_tangencies, len(times)-1


def candidate(name, normal, anchor, span, corner, t, h):
    p=pose(h,VERTICES[corner],t)
    kind,along=classify(name,anchor,normal,span,p)
    return {
        "surface":name,"vertex_index":corner,
        "dt_after_third_impulse":rd(t),
        "absolute_virtual_time":rd(h["contact_absolute_virtual_time"]+t),
        "vertex_position":[rd(z) for z in p],
        "source_face_tangent_coordinate":along,
        "incoming_normal_vertex_rate":rd(gap_rate(
            gap_terms(h,VERTICES[corner],normal,anchor),t)),
        "signed_line_gap_residual":rd(gap_value(
            gap_terms(h,VERTICES[corner],normal,anchor),t)),
        "feature_classification":kind,
        "conditional_source_geometry_only":True,
        "physical_contact_measured":False,
    }


def attempt(angle):
    parent=source22(angle)
    ancestor=source21(angle)
    common={
        "schema":SCHEMA,"angle":rd(angle),
        "source_trial22_schema":SOURCE22,
        "source_trial22_status":parent["status"],
        "source_trial22_first_crossing":parent["first_crossing"],
        "source_trial22_all_first_per_line":parent["all_source_line_crossings"],
        "source_third_impulse":ancestor["third_impulse"],
        "source_receiver":ancestor["source_receiver"],
        "projection_horizon":DURATION,
        "nominal_ballistic_assumption_only":True,
        "continuous_measured_motion":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "collision_after_candidate_solved":False,
        "formally_certified_root_isolation":False,
    }
    if ancestor["third_impulse"] is None:
        if parent["status"]!="NO_ADMITTED_THIRD_IMPULSE":
            raise ValueError("no-source control has conflicting Trial22 source")
        return {**common,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "all_inward_roots":[],"eligible_geometry_roots":[],
                "first_eligible_geometry":None,"coearliest_eligible":[],
                "outside_finite_face_roots":[],"endpoint_uncertainties":[],
                "near_tangent_uncertainties":[],"monotonic_segments_checked":0}
    if ancestor["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("original third impulse did not support bounded continuation")
    h=ancestor["third_impulse"]
    all_roots, outside, endpoints, tangencies=[],[],[],[]
    segments=0
    for name, normal, anchor, span in surfaces(ancestor,angle):
        for index,corner in enumerate(VERTICES):
            q=gap_terms(h,corner,normal,anchor)
            if not all(isfinite(z) for z in q):
                raise ValueError("nonfinite nominal root coefficients")
            ts, touches, checked = inward_roots(q)
            segments+=checked
            for watch in touches:
                tangencies.append({"surface":name,"vertex_index":index,
                                   **watch, "actual_contact_unresolved":True})
            for t in ts:
                item=candidate(name,normal,anchor,span,index,t,h)
                all_roots.append(item)
                if item["feature_classification"]==OUTSIDE:
                    outside.append(item)
                elif item["feature_classification"]==ENDPOINT:
                    endpoints.append(item)
    key=lambda x:(x["dt_after_third_impulse"],x["surface"],x["vertex_index"])
    all_roots.sort(key=key)
    outside.sort(key=key)
    endpoints.sort(key=key)
    eligible=[c for c in all_roots if c["feature_classification"] in
              SELECTABLE_GEOMETRY]
    first=eligible[0] if eligible else None
    tied=[c for c in eligible if
          abs(c["dt_after_third_impulse"]-first["dt_after_third_impulse"])<=TIE_TOL
          ] if first else []
    if first is None:
        status="NO_ELIGIBLE_INWARD_ROOT_IN_WINDOW_UNDER_ASSUMPTIONS"
    elif len(tied)>1:
        status="COEARLIEST_GEOMETRIC_FEATURES_UNRESOLVED"
    else:
        status="FIRST_FINITE_OR_BOUNDARY_GEOMETRY_CANDIDATE"
    # Retain source22's per-surface first crossings as original ancestry.
    source_first={(r["surface"],r["vertex_index"]):r
                  for r in parent["all_source_line_crossings"]}
    for pair,r in source_first.items():
        found=[q for q in all_roots if (q["surface"],q["vertex_index"])==pair]
        if not found or abs(found[0]["dt_after_third_impulse"]-
                            r["dt_after_third_impulse"])>3e-7:
            raise ValueError("Trial22's original first root lost on this source lane")
    if len(source_first)!=len({
        (x["surface"],x["vertex_index"]) for x in all_roots
    }):
        raise ValueError("changed original supporting-line search coverage")
    return {**common,"status":status,
            "all_inward_roots":all_roots,
            "eligible_geometry_roots":eligible,
            "first_eligible_geometry":first,
            "coearliest_eligible":tied,
            "outside_finite_face_roots":outside,
            "endpoint_uncertainties":endpoints,
            "near_tangent_uncertainties":tangencies,
            "monotonic_segments_checked":segments}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "conditional_third_impulse_inputs":sum(
                c["source_third_impulse"] is not None for c in cases),
            "without_third_impulse":sum(
                c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
            "first_eligible_cases":sum(
                c["first_eligible_geometry"] is not None for c in cases),
            "root_free_eligible_windows":sum(
                c["source_third_impulse"] is not None and
                c["first_eligible_geometry"] is None for c in cases),
            "total_inward_root_candidates":sum(
                len(c["all_inward_roots"]) for c in cases),
            "outside_finite_face_candidates":sum(
                len(c["outside_finite_face_roots"]) for c in cases),
            "endpoint_uncertainties":sum(
                len(c["endpoint_uncertainties"]) for c in cases),
            "near_tangent_uncertainties":sum(
                len(c["near_tangent_uncertainties"]) for c in cases),
            "physical_measurements":0,"fourth_impulses_selected":0,
            "physical_receivers_built":0,"new_world_or_engine":False}
