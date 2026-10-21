"""WORLD29 — qualify the existing first finite model contact before proposing a response.

Original WORLD28 source locates three conditional finite segment/square onsets.
Original WORLD23 source supplies individual rotating-vertex feature candidates.
This lane NEVER infers a contact from overlap alone: it requires a unique
incoming corner, source-consistent finite-face normal and tangent coordinate,
the earliest eligible known feature, and no other finite-face simultaneity.

Only an accepted candidate receives the ORIGINAL frictionless, restitution-1
rigid-square normal response equation. This is a *hypothetical mathematics*
record; no fourth physical impact, continued post-response path, or receiver.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_local_finite_onset import attempt as earlier28,TOL
from systems.workspace.world_ab_all_inward_finite_features import attempt as earlier23
from systems.workspace.world_ab_third_contact import attempt as earlier21,ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF,INERTIA

SCHEMA="world-ab-first-finite-feature-conditional-response/v1"
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
MASS=1.
EPS=3e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def point_at(t,original,i):
    theta=original["contact_orientation"]+original["outgoing_spin"]*t
    c,s=cos(theta),sin(theta)
    x,y=VERTICES[i]
    offset=(c*x-s*y,s*x+c*y)
    center=(original["contact_center"][0]+original["outgoing_velocity"][0]*t,
            original["contact_center"][1]+original["outgoing_velocity"][1]*t)
    return center,theta,offset,(center[0]+offset[0],center[1]+offset[1])


def rd(x):
    return round(float(x),10)


def ideal_response(v,w,r,n):
    """Original Trial18/21 elastic frictionless unit-mass rigid-square law."""
    incoming=dot((v[0]-w*r[1],v[1]+w*r[0]),n)
    lever=cross(r,n)
    normal_impulse=-2*incoming/(1/MASS+lever*lever/INERTIA)
    after=(v[0]+normal_impulse*n[0]/MASS,
           v[1]+normal_impulse*n[1]/MASS)
    spin=w+normal_impulse*lever/INERTIA
    leaving=dot((after[0]-spin*r[1],after[1]+spin*r[0]),n)
    before_energy=.5*MASS*dot(v,v)+.5*INERTIA*w*w
    after_energy=.5*MASS*dot(after,after)+.5*INERTIA*spin*spin
    return {"incoming_contact_normal_rate":rd(incoming),
            "outgoing_contact_normal_rate":rd(leaving),
            "normal_impulse":rd(normal_impulse),
            "lever_cross_normal":rd(lever),
            "incoming_velocity":[rd(z) for z in v],
            "outgoing_velocity":[rd(z) for z in after],
            "incoming_spin":rd(w),"outgoing_spin":rd(spin),
            "kinetic_energy_before":rd(before_energy),
            "kinetic_energy_after":rd(after_energy)}


def attempt(angle):
    native28=earlier28(angle)
    native23=earlier23(angle)
    native21=earlier21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial28_schema":native28["schema"],
        "source_trial28_status":native28["status"],
        "source_trial23_schema":native23["schema"],
        "source_trial23_first_eligible":native23["first_eligible_geometry"],
        "source_original_third_response":native21["third_impulse"],
        "original_world_dimensions":[24.,6.],
        "original_mass":MASS,"original_inertia":INERTIA,
        "source_conditional_free_flight_only":True,
        "assumed_law":"single frictionless normal, restitution 1, unit-mass rotating square",
        "physical_fourth_impact_witnessed":False,
        "physical_response_selected":False,
        "post_response_trajectory_solved":False,
        "another_receiver_constructed":False,
        "exact_root_or_material_certification":False,
    }
    first=native28["first_eligible_finite_onset"]
    if native21["third_impulse"] is None:
        if first is not None:
            raise ValueError("no original third impulse could give fourth candidate")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "qualifying_source_feature":None,
                "source_contact_rejection":None,
                "conditional_fourth_response":None}
    if first is None:
        return {**base,"status":"NO_ORIGINAL_FIRST_FINITE_ONSET",
                "qualifying_source_feature":None,
                "source_contact_rejection":None,
                "conditional_fourth_response":None}
    if (native28["cases_with_earlier_unknown_clear_sample_gaps"]!=0 or
        native28["status"]!="FIRST_NUMERICAL_FINITE_ONSET_CORROBORATED_BY_VERTEX"):
        return {**base,"status":"UNRESOLVED_FIRST_ONSET_ANCESTRY",
                "qualifying_source_feature":None,
                "source_contact_rejection":"original first finite onset lacks independent corroboration",
                "conditional_fourth_response":None}
    face=first["face"]
    t=first["refined_sat_bracket"]["first_nominally_intersecting_time"]
    defs=[(n,anchor,span) for name,n,anchor,span in surfaces(native21,angle)
          if name==face and span is not None]
    if len(defs)!=1:
        raise ValueError("finite source face missing from source-defined geometry")
    normal,anchor,span=defs[0]
    normal=tuple(normal)
    tangent=(-normal[1],normal[0])
    matches=[x for x in native23["eligible_geometry_roots"]
             if x["surface"]==face
             and x["feature_classification"]=="FINITE_FACE_INTERIOR_CANDIDATE"
             and abs(x["dt_after_third_impulse"]-t)<=TOL]
    earliest=native23["first_eligible_geometry"]
    reason=None
    if len(matches)!=1:
        reason="contact feature not a unique qualified rotating-square vertex"
    elif earliest is not None and earliest["dt_after_third_impulse"]<t-TOL:
        reason="original source reported earlier competing boundary feature"
    elif any(x["face"]!=face and x["refined_sat_bracket"] is not None and
             x["refined_sat_bracket"]["first_nominally_intersecting_time"]<=t+TOL
             for x in native28["face_first_onsets"]):
        reason="other original finite face is coearliest"
    if reason is not None:
        return {**base,"status":"UNRESOLVED_OR_COMPETING_FINITE_CONTACT",
                "qualifying_source_feature":None,
                "source_contact_rejection":reason,
                "conditional_fourth_response":None}
    corner=matches[0]
    idx=corner["vertex_index"]
    center,theta,r,cp=point_at(corner["dt_after_third_impulse"],
                                native21["third_impulse"],idx)
    d=(cp[0]-anchor[0],cp[1]-anchor[1])
    along=dot(d,tangent)
    gap=dot(d,normal)
    prev=native21["third_impulse"]
    before=tuple(prev["outgoing_velocity"])
    spin=prev["outgoing_spin"]
    incoming=dot((before[0]-spin*r[1],before[1]+spin*r[0]),normal)
    competing=[]
    for j in range(4):
        if j==idx:continue
        _,_,_,other=point_at(corner["dt_after_third_impulse"],prev,j)
        dv=(other[0]-anchor[0],other[1]-anchor[1])
        if abs(dot(dv,tangent))<=span/2+EPS and dot(dv,normal)<=EPS:
            competing.append(j)
    if (abs(hypot(*normal)-1)>EPS or abs(gap)>2e-6
        or not -span/2+EPS<along<span/2-EPS
        or abs(along-corner["source_face_tangent_coordinate"])>2e-6
        or abs(incoming-corner["incoming_normal_vertex_rate"])>2e-6
        or incoming>=-EPS or competing):
        return {**base,"status":"UNRESOLVED_OR_COMPETING_FINITE_CONTACT",
                "qualifying_source_feature":None,
                "source_contact_rejection":{
                    "normal_gap":rd(gap),
                    "finite_face_along":rd(along),
                    "incoming_rate":rd(incoming),
                    "other_nonseparated_face_vertices":competing,
                    "reason":"nonincoming, nonunique, or inconsistent finite corner feature"},
                "conditional_fourth_response":None}
    response=ideal_response(before,spin,r,normal)
    if (not all(isfinite(x) for x in (
        response["normal_impulse"],*response["outgoing_velocity"],
        response["outgoing_spin"]))
        or response["normal_impulse"]<=EPS
        or abs(response["incoming_contact_normal_rate"]+
               response["outgoing_contact_normal_rate"])>EPS
        or abs(response["kinetic_energy_before"]-
               response["kinetic_energy_after"])>EPS):
        raise ValueError("original elastic contact rule failed conditional controls")
    feature={
        "source_face":face,"source_vertex_index":idx,
        "dt_after_original_third_impulse":rd(corner["dt_after_third_impulse"]),
        "absolute_virtual_time":rd(prev["contact_absolute_virtual_time"]+
                                   corner["dt_after_third_impulse"]),
        "source_onset_refined_at":rd(t),
        "source_vertex_witness":corner,
        "contact_center":[rd(x) for x in center],
        "contact_point":[rd(x) for x in cp],
        "contact_angle":rd(theta),
        "contact_normal":[rd(x) for x in normal],
        "finite_face_tangent_coordinate":rd(along),
        "contact_lever":[rd(x) for x in r],
        "independent_finite_geometry_not_material_contact":True,
    }
    return {**base,"status":"CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE",
            "qualifying_source_feature":feature,
            "source_contact_rejection":None,
            "conditional_fourth_response":{
                **response,
                "source_face":face,
                "source_vertex_index":idx,
                "materially_witnessed":False,
                "response_selected_as_actual":False,
                "further_contacts_resolved":False}}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "original_finite_first_onset_cases":sum(
                earlier28(c["angle"])["first_eligible_finite_onset"] is not None
                for c in cases),
            "conditionally_qualifying_responses":sum(
                c["conditional_fourth_response"] is not None for c in cases),
            "unresolved_finite_feature_cases":sum(
                c["status"]=="UNRESOLVED_OR_COMPETING_FINITE_CONTACT" for c in cases),
            "absent_source_impulse_controls":sum(
                c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
            "material_impacts_witnessed":0,
            "actual_fourth_impulses_selected":0,
            "post_response_trajectories_solved":0,
            "receivers_constructed":0,"new_engine_or_world":False}
