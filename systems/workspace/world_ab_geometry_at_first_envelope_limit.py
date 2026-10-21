"""WORLD32: examine finite geometry ONLY at WORLD31 first sufficiency-limit time.

Source WORLD31 located three first conservative inequality limits following
unselected hypothetical fourth responses. Those times are limits of evidence,
NOT contacts. Reuse the unchanged original source faces, square and 24x6 WORLD
to inspect each limiting model pose. Do not extrapolate to a fifth event.

Finite face vs square uses original source25 local-frame segment clipping and
source26 signed SAT geometry. Independent WORLD32 witness uses world-coordinate
SAT and separate corner reconstruction. Neither is a material observation.
"""
from __future__ import annotations

from math import cos,sin,isfinite

from systems.workspace.world_ab_first_envelope_limit import (
    attempt as source31,SCHEMA as SOURCE31,HORIZON
)
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_finite_segment_square_overlap import static_faces,finite_clip
from systems.workspace.world_ab_between_sample_clearance import nominal_margin
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-finite-geometry-at-conservative-first-limit/v1"
EPS=1e-7
SQUARE=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):
    return round(float(x),10)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def state_after_hypothesis(f,response):
    return {
        "contact_center":list(f["contact_center"]),
        "contact_orientation":f["contact_angle"],
        "outgoing_velocity":list(response["outgoing_velocity"]),
        "outgoing_spin":response["outgoing_spin"],
    }


def rotating_corner(h,index,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    x,y=SQUARE[index]
    c,s=cos(theta),sin(theta)
    center=(h["contact_center"][0]+h["outgoing_velocity"][0]*t,
            h["contact_center"][1]+h["outgoing_velocity"][1]*t)
    return (center[0]+c*x-s*y,center[1]+s*x+c*y)


def attempt(angle):
    prior=source31(angle)
    parent=source29(angle)
    ancestor=source21(angle)
    baseline={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial31_schema":SOURCE31,
        "source_trial31_status":prior["status"],
        "source_first_nominal_limit":prior["max_common_nominal_clearance_prefix"],
        "source_limiting_constraints":prior["first_limiting_constraints"],
        "source_conditional_fourth_response":parent["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_source_faces":2,
        "source_declared_max_horizon":HORIZON,
        "conditional_mathematical_pose_only":True,
        "actual_material_fifth_contact_measured":False,
        "fifth_impulse_calculated":False,
        "new_receiver_constructed":False,
        "post_limit_ballistic_movement_admitted":False,
        "certified_exact_first_contact":False,
    }
    if parent["conditional_fourth_response"] is None:
        if prior["max_common_nominal_clearance_prefix"] is not None:
            raise ValueError("unqualified original source gained later movement")
        return {**baseline,"status":"NO_QUALIFIED_FOURTH_RESPONSE",
                "finite_face_model_states":[],
                "limiting_corner_model_states":[],
                "original_boundary_min_gaps":[],
                "model_finite_overlap_at_limit":False}
    if prior["status"]!="FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT":
        return {**baseline,"status":"NO_FIRST_LIMIT_WITHIN_DECLARED_HORIZON",
                "finite_face_model_states":[],
                "limiting_corner_model_states":[],
                "original_boundary_min_gaps":[],
                "model_finite_overlap_at_limit":False}
    t=prior["max_common_nominal_clearance_prefix"]
    h=state_after_hypothesis(parent["qualifying_source_feature"],
                             parent["conditional_fourth_response"])
    if not (isfinite(t) and .008<=t<HORIZON):
        raise ValueError("original first limiting time unsupported")
    faces=static_faces(ancestor,angle)
    if len(faces)!=2:
        raise ValueError("original source finite faces changed")
    face_states=[]
    for name,segment in faces:
        clip=finite_clip(h,segment,t)
        signed=nominal_margin(h,segment,t)
        face_states.append({
            "source_face":name,
            "source_original_segment":segment,
            "source_finite_clip_overlap_at_limit":bool(clip["overlap"]),
            "source_clip_entry_fraction":clip["entry"],
            "source_clip_exit_fraction":clip["exit"],
            "signed_sat_separation_at_limit":rd(signed),
            "model_only_not_material_measurement":True,
        })
    boundary=[]
    original_planes=list(surfaces(ancestor,angle))
    for name,n,anchor,span in original_planes:
        if span is not None:
            continue
        gaps=[]
        for index in range(4):
            p=rotating_corner(h,index,t)
            gaps.append(rd(dot((p[0]-anchor[0],p[1]-anchor[1]),n)))
        boundary.append({"plane":name,"four_vertex_gaps":gaps,
                         "minimum_model_gap":min(gaps),
                         "world_boundary_measured":False})
    limiting=[]
    for limit in prior["first_limiting_constraints"]:
        name=limit["source_plane"]
        corner=limit["source_corner_index"]
        found=[(tuple(n),tuple(anchor),span) for label,n,anchor,span in original_planes
               if label==name]
        if len(found)!=1:
            raise ValueError("original limiting plane missing from same source")
        normal,anchor,span=found[0]
        point=rotating_corner(h,corner,t)
        diff=(point[0]-anchor[0],point[1]-anchor[1])
        tangent=(-normal[1],normal[0])
        u=dot(diff,tangent) if span is not None else None
        limiting.append({
            "source_plane":name,"source_corner_index":corner,
            "model_corner_position":[rd(x) for x in point],
            "actual_signed_gap_in_conditional_model":rd(dot(diff,normal)),
            "finite_face_tangent_coordinate":rd(u) if u is not None else None,
            "within_finite_source_face_tangent_span":
                abs(u)<span/2 if u is not None else None,
            "no_material_sensor":True,
        })
    face_overlap=any(x["source_finite_clip_overlap_at_limit"] for x in face_states)
    world_candidate=any(x["minimum_model_gap"]<=EPS for x in boundary)
    near=any(abs(x["signed_sat_separation_at_limit"])<=EPS for x in face_states)
    if face_overlap:
        status="SAMPLED_CONDITIONAL_FINITE_INTERSECTION_AT_EVIDENCE_LIMIT"
    elif world_candidate or near:
        status="CONDITIONAL_WORLD_BOUNDARY_OR_GRAZING_GEOMETRY_UNRESOLVED"
    else:
        status="CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT"
    return {**baseline,"status":status,
            "finite_face_model_states":face_states,
            "limiting_corner_model_states":limiting,
            "original_boundary_min_gaps":boundary,
            "model_finite_overlap_at_limit":face_overlap}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "source_limit_model_cases":sum(c["source_first_nominal_limit"] is not None
                                           and c["status"]!="NO_FIRST_LIMIT_WITHIN_DECLARED_HORIZON"
                                           for c in cases),
            "finite_intersection_at_evidence_limit_cases":sum(
                c["status"]=="SAMPLED_CONDITIONAL_FINITE_INTERSECTION_AT_EVIDENCE_LIMIT"
                for c in cases),
            "finite_shapes_separated_at_limit_cases":sum(
                c["status"]=="CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT"
                for c in cases),
            "ambiguous_or_grazing_limit_cases":sum(
                c["status"]=="CONDITIONAL_WORLD_BOUNDARY_OR_GRAZING_GEOMETRY_UNRESOLVED"
                for c in cases),
            "without_qualified_fourth_response":sum(
                c["status"]=="NO_QUALIFIED_FOURTH_RESPONSE" for c in cases),
            "actual_material_impacts_measured":0,
            "fifth_impulses_solved":0,
            "real_receivers_built":0,
            "new_world_or_engine":False}
