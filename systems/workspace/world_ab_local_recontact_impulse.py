"""WORLD Trial18: a *candidate* second impact at Trial17's first finite recontact.

One added mathematical move, no engine and no new WORLD. Keep the independently
verified original Trial04 impulse and Trial17 first renewed corner/face contact.
Try the SAME ideal frictionless, perfectly elastic rigid-square impulse law
at that measured-within-the-model corner. Independently inspect the resulting
very short, sampled motion. The contact assumption is a CONTROL, not observed
material behavior, a uniquely selected physics law or sustained contact proof.

Refuse nonincoming contact, source/feature mismatch, energy creation or local
sampled overlap. Never build a new receiver or claim hardware equivalence.
"""
from __future__ import annotations

from math import cos, hypot, isfinite, sin
from systems.workspace.world_ab_square_first_recontact import trial as prior_trial
from systems.workspace.world_ab_oblique_impact import (
    HALF, INERTIA, WALL_CENTER, SPAN,
)

SCHEMA="world-ab-local-corner-recontact-impulse/v1"
ANGLES=(0.,2.5,5.,7.5,10.,12.25,15.,20.)
MASS=1.
POST_HORIZON=.016
STEP=.0005
EPS=1e-8
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def rd(x):
    return round(float(x),10)


def vertex(center,theta,corner):
    cc,ss=cos(theta),sin(theta)
    x,y=corner
    return (center[0]+cc*x-ss*y,center[1]+ss*x+cc*y)


def local_gap(center,theta,n):
    tangent=(-n[1],n[0])
    checked=[]
    for i,p in enumerate(vertex(center,theta,c) for c in VERTICES):
        d=(p[0]-WALL_CENTER[0],p[1]-WALL_CENTER[1])
        along=dot(d,tangent)
        if abs(along)<=SPAN/2+EPS:
            checked.append((dot(d,n),i,along))
    return min(checked) if checked else None


def attempt(angle):
    source=prior_trial(angle)
    parent=source["source_original_first_contact"]
    base={
        "schema":SCHEMA,
        "source_trial17":source["schema"],
        "source_original_trial04":parent["schema"] if "schema" in parent else
            "world-ab-oblique-normal-angular-impact/v1",
        "angle":rd(angle),
        "source_first_contact":parent,
        "source_trial17_first_return":source["first_return"],
        "local_time_horizon":POST_HORIZON,
        "observation_step":STEP,
        "second_impulse_is_a_model_hypothesis":True,
        "physical_second_impact_observed":False,
        "receiver_constructed":False,
        "continuous_clearance_certified":False,
        "further_impacts_solved":False,
    }
    candidate=source["first_return"]
    if candidate is None:
        return {**base,"status":"NO_ADMITTED_RENEWED_CONTACT",
                "candidate_impulse":None,"post_contact_samples":[]}
    if source["status"]!="FIRST_RENEWED_FINITE_FACE_CONTACT_CANDIDATE":
        return {**base,"status":"UNRESOLVED_RECONTACT_FEATURE",
                "candidate_impulse":None,"post_contact_samples":[]}
    t=candidate["dt_after_initial_contact"]
    idx=candidate["corner_index"]
    if type(idx) is not int or idx<0 or idx>=4 or not (0<t<=.06):
        raise ValueError("invalid admitted source time or vertex identity")
    normal=tuple(parent["normal"])
    tangent=(-normal[1],normal[0])
    spin_before=parent["angular_velocity_after"]
    v_before=tuple(parent["velocity_after"])
    theta=spin_before*t
    start=tuple(parent["first_contact_center"])
    center=(start[0]+t*v_before[0],start[1]+t*v_before[1])
    cp=vertex(center,theta,VERTICES[idx])
    r=(cp[0]-center[0],cp[1]-center[1])
    relative=(cp[0]-WALL_CENTER[0],cp[1]-WALL_CENTER[1])
    normal_gap=dot(relative,normal)
    along=dot(relative,tangent)
    if (abs(normal_gap)>2e-7 or
            abs(along-candidate["source_face_tangent_coordinate"])>2e-7 or
            not (-SPAN/2+EPS<along<SPAN/2-EPS) or
            max(abs(a-b) for a,b in zip(cp,candidate["corner_position"]))>2e-7):
        raise ValueError("first source recontact feature moved")
    prior=local_gap(center,theta,normal)
    if prior is not None and prior[0]<-2e-7:
        return {**base,"status":"UNRESOLVED_PREEXISTING_INTERPENETRATION",
                "candidate_impulse":None,"post_contact_samples":[]}
    v_at_corner=(v_before[0]-spin_before*r[1],
                 v_before[1]+spin_before*r[0])
    inward=dot(v_at_corner,normal)
    if inward>=-EPS:
        return {**base,"status":"NO_INCOMING_VERTEX_MOTION",
                "candidate_impulse":None,"post_contact_samples":[]}
    lever=cross(r,normal)
    effective_inverse_mass=1/MASS+(lever**2)/INERTIA
    j=-(1+1.)*inward/effective_inverse_mass
    if not (isfinite(j) and j>EPS):
        raise ValueError("invalid finite candidate normal impulse")
    v_after=(v_before[0]+j*normal[0]/MASS,
             v_before[1]+j*normal[1]/MASS)
    spin_after=spin_before+j*lever/INERTIA
    out_corner=(v_after[0]-spin_after*r[1],
                v_after[1]+spin_after*r[0])
    if abs(dot(out_corner,normal)+inward)>1e-7:
        raise ValueError("proposed contact does not restore normal relative speed")
    eb=.5*MASS*dot(v_before,v_before)+.5*INERTIA*spin_before**2
    ea=.5*MASS*dot(v_after,v_after)+.5*INERTIA*spin_after**2
    if ea>eb+1e-8 or ea<eb-1e-8:
        raise ValueError("ideal normal impulse violates original elastic energy control")
    impulse={
        "normal_impulse":rd(j),
        "incoming_vertex_normal_rate":rd(inward),
        "outgoing_vertex_normal_rate":rd(dot(out_corner,normal)),
        "lever_cross_normal":rd(lever),
        "angular_velocity_before":rd(spin_before),
        "angular_velocity_after":rd(spin_after),
        "velocity_before":[rd(z) for z in v_before],
        "velocity_after":[rd(z) for z in v_after],
        "kinetic_energy_before":rd(eb),
        "kinetic_energy_after":rd(ea),
        "contact_vertex_index":idx,
        "contact_time_relative":rd(t),
        "contact_center":[rd(z) for z in center],
        "contact_point":[rd(z) for z in cp],
        "contact_angle":rd(theta),
        "source_face_normal":[rd(z) for z in normal],
        "constitutive_hypothesis":"single frictionless normal, e=1, rotating rigid square",
        "selected_as_actual_material_response":False,
    }
    samples=[]
    first_overlap=None
    for k in range(round(POST_HORIZON/STEP)+1):
        dt=k*STEP
        p=(center[0]+dt*v_after[0],center[1]+dt*v_after[1])
        th=theta+dt*spin_after
        sampled=local_gap(p,th,normal)
        if sampled is None:
            gap=None;vertex_id=None;along_pos=None
        else:
            gap,vertex_id,along_pos=sampled
            if gap<-EPS and first_overlap is None:
                first_overlap=dt
        samples.append({
            "dt_after_candidate":rd(dt),
            "center":[rd(z) for z in p],
            "orientation":rd(th),
            "minimum_sampled_signed_face_gap":None if gap is None else rd(gap),
            "worst_finite_face_corner":vertex_id,
            "worst_finite_face_tangent":None if along_pos is None else rd(along_pos),
        })
    return {**base,
            "status":("LOCAL_OVERLAP_UNRESOLVED" if first_overlap is not None
                      else "NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES"),
            "candidate_impulse":impulse,
            "post_contact_samples":samples,
            "first_sampled_post_contact_overlap":None if first_overlap is None else rd(first_overlap),
            "next_movement_admitted_as_verified":False}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "cases_with_candidate_impulse":sum(c["candidate_impulse"] is not None for c in cases),
        "cases_without_recontact":sum(c["status"]=="NO_ADMITTED_RENEWED_CONTACT" for c in cases),
        "cases_with_sampled_post_overlap":sum(c["status"]=="LOCAL_OVERLAP_UNRESOLVED" for c in cases),
        "material_contact_response_proven":False,
        "created_any_new_receiver":False,
        "general_rotating_contact_solver":False,
    }
