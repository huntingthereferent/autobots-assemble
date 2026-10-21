"""WORLD40: whole-original-configuration sixth conditional normal-response gate.

Re-use the only WORLD39 original numerical zero-gap candidate, not a material
sixth impact. Recheck the selected finite source face, all 23 competing
original corner-plane clearances, independent finite clipping of both original
segments at the candidate, incoming normal rate and conservation controls.
Only then apply WORLD29's unchanged ideal single-contact law as a *conditional*
mathematical sixth response. This never selects physical motion or authorizes
a post-sixth continuation.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_local_zero_gap_after_guard import (
    attempt as source39, SCHEMA as SOURCE39, PROBE_WIDTH
)
from systems.workspace.world_ab_whole_contact_configuration import attempt as source35
from systems.workspace.world_ab_post_fifth_contiguous_prefix import (
    model_at_conditional_fifth, original_planes
)
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES
from systems.workspace.world_ab_first_finite_response_qualification import ideal_response
from systems.workspace.world_ab_finite_segment_square_overlap import static_faces, finite_clip
from systems.workspace.world_ab_oblique_impact import HALF,INERTIA

SCHEMA="world-ab-sixth-whole-original-contact-conditional-normal-law/v1"
GAP_TOL=1e-8
SPEED_GUARD=1e-5
SEGMENT_GUARD=1e-6
OTHER_GAP_GUARD=1e-6
CONSERVATION_TOL=3e-7
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):return round(float(x),12)

def dot(a,b):return a[0]*b[0]+a[1]*b[1]

def cross(a,b):return a[0]*b[1]-a[1]*b[0]

def state(model,i,t):
    x,y=VERTICES[i]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    r=(x*c-y*s,x*s+y*c)
    p=(model["center"][0]+model["velocity"][0]*t+r[0],
       model["center"][1]+model["velocity"][1]*t+r[1])
    v=(model["velocity"][0]-model["spin"]*r[1],
       model["velocity"][1]+model["spin"]*r[0])
    return p,r,v

def attempt(angle):
    old=source39(angle)
    before=source35(angle)
    ancestor=source21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial39_schema":SOURCE39,
        "source_trial39_status":old["status"],
        "source_first_original_zero_gap_time":old["bracketed_first_zero_time"],
        "original_24_by_6_world":[24.,6.],
        "source_original_two_finite_faces":True,
        "source_original_four_perimeter_planes":True,
        "original_mass":1.0,"original_inertia":INERTIA,
        "unchanged_law":"unit-mass frictionless normal restitution=1",
        "fifth_response_unselected":True,
        "measured_sixth_impact":False,
        "sixth_response_selected_as_physical":False,
        "post_sixth_continuation_admitted":False,
        "new_receiver_constructed":False,
        "outward_rounded_exact_contact_proof":False,
    }
    empty={
        "source_face":None,"source_corner":None,
        "source_zero_gap":None,"source_face_tangent":None,
        "incoming_source_normal_rate":None,
        "selected_corner_approaches_inside_finite_face":False,
        "all_original_23_competing_clearances_retained":False,
        "original_selected_face_finite_clip_intersects":None,
        "original_other_face_finite_clip_intersects":None,
        "source_contact_geometry_independently_consistent":False,
        "conditional_sixth_response":None,
    }
    if old["status"]=="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE":
        return {**base,**empty,"status":"NO_SOURCE_SIXTH_CANDIDATE"}
    if old["status"]!="LOCAL_ORIGINAL_ZERO_GAP_NUMERICAL_FEATURE_QUALIFIED" or (
        old["source_contact_geometry_qualified"] is not True):
        return {**base,**empty,"status":"UNQUALIFIED_ORIGINAL_ZERO_GAP_PROBE"}
    if before["conditional_fifth_response"] is None:
        raise ValueError("original fifth-response ancestry missing")
    face,index,t=old["selected_source_face"],old["selected_corner"],old["bracketed_first_zero_time"]
    if (t is None or not isfinite(t) or not 0.058<t<.25
        or index not in range(4)
        or not old["guard_time"]<t<old["guard_time"]+PROBE_WIDTH
        or old["all_23_other_original_constraints_strictly_separated"] is not True):
        raise ValueError("WORLD39 original unique source configuration broken")
    recs=old["source_24_plane_corner_probe_records"]
    if (len(recs)!=24 or sum(r["selected_guard_feature"] for r in recs)!=1
        or any(r["other_original_relation_separated_through_probe"] is not True
               or r["conservative_other_gap_lower_bound"]<=OTHER_GAP_GUARD
               for r in recs if not r["selected_guard_feature"])):
        raise ValueError("whole original WORLD39 competitor clearance was lost")
    model=model_at_conditional_fifth(before,ancestor)
    planes=original_planes(ancestor,angle)
    match=[(n,anchor,span) for name,n,anchor,span in planes
           if name==face and span is not None]
    if len(match)!=1 or len(planes)!=6:
        raise ValueError("original finite face identity invalid")
    n,anchor,span=match[0]
    p,lever,velocity=state(model,index,t)
    tangent=(-n[1],n[0])
    offset=(p[0]-anchor[0],p[1]-anchor[1])
    gap=dot(offset,n)
    along=dot(offset,tangent)
    incoming=dot(velocity,n)
    inside=abs(along)<span/2-SEGMENT_GUARD
    consistent=(abs(gap)<=GAP_TOL
                and inside and incoming<-SPEED_GUARD
                and abs(incoming-old["source_normal_rate_at_zero"])<=SPEED_GUARD
                and all(abs(p[i]-old["first_zero_contact_model_position"][i])<=GAP_TOL
                        for i in (0,1)))
    original_model={
        "contact_center":model["center"],
        "contact_orientation":model["theta"],
        "outgoing_velocity":model["velocity"],
        "outgoing_spin":model["spin"],
    }
    faces=static_faces(ancestor,angle)
    if len(faces)!=2 or {x[0] for x in faces}!={z[0] for z in planes if z[3] is not None}:
        raise ValueError("source original finite faces substituted")
    results={name:finite_clip(original_model,segment,t)["overlap"]
             for name,segment in faces}
    selected=results[face]
    other=any(overlap for name,overlap in results.items() if name!=face)
    good=consistent and selected and not other
    response=None
    if good:
        response=ideal_response(model["velocity"],model["spin"],lever,n)
        if (not all(isfinite(x) for x in (
                response["normal_impulse"],*response["outgoing_velocity"],
                response["outgoing_spin"]))
            or response["normal_impulse"]<=0
            or abs(response["incoming_contact_normal_rate"]+
                   response["outgoing_contact_normal_rate"])>CONSERVATION_TOL
            or abs(response["kinetic_energy_before"]-
                   response["kinetic_energy_after"])>CONSERVATION_TOL):
            raise ValueError("original WORLD29 normal law fails sixth conditional checks")
        response={**response,
                  "original_source_face":face,
                  "original_source_corner":index,
                  "hypothetical_mathematics_only":True,
                  "selected_as_physical":False,
                  "post_sixth_motion_solved":False}
    return {
        **base,
        "status":("CONDITIONAL_SIXTH_ELASTIC_RESPONSE_MATHEMATICALLY_QUALIFIED"
                  if good else "ORIGINAL_SIXTH_CONFIGURATION_UNRESOLVED"),
        "source_face":face,"source_corner":index,
        "source_zero_gap":rd(gap),
        "source_face_tangent":rd(along),
        "incoming_source_normal_rate":rd(incoming),
        "selected_corner_approaches_inside_finite_face":inside,
        "all_original_23_competing_clearances_retained":True,
        "original_selected_face_finite_clip_intersects":selected,
        "original_other_face_finite_clip_intersects":other,
        "source_contact_geometry_independently_consistent":consistent,
        "conditional_sixth_response":response,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "original_sixth_model_candidates":sum(c["source_face"] is not None for c in cases),
            "conditionally_qualified_sixth_responses":sum(c["conditional_sixth_response"] is not None for c in cases),
            "unresolved_original_sixth_configurations":sum(c["status"]=="ORIGINAL_SIXTH_CONFIGURATION_UNRESOLVED" for c in cases),
            "inactive_original_controls":sum(c["status"]=="NO_SOURCE_SIXTH_CANDIDATE" for c in cases),
            "real_sixth_impacts":0,"selected_sixth_impulses":0,
            "post_sixth_trajectories_solved":0,"new_receivers":0,
            "new_general_world_engine":False}
