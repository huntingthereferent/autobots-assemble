"""WORLD Trial 08: an explicitly *candidate* frictionless two-contact impulse.

Experiment only: preserve the original Trial 04B source surfaces, Trial 06
single-contact friction=0.4, Trial 07 contact-time discontinuity, and native W13.
At the independently located exact arrival tie, evaluate a simultaneous,
frictionless e=1 two-normal impulse for a unit-mass disc. The two-contact
law is a new falsifiable model, not a solution for arbitrary joint contacts.
"""
from __future__ import annotations
from math import hypot,isfinite
from systems.workspace.world_ab_junction_threshold import run as threshold_run,arrival_pair
from systems.workspace.world_ab_junction_continuous import (
    trace,nearest,dot,add,mul,sub,R,HORIZON,STEP,I)

SCHEMA="world-ab-two-contact-frictionless-candidate/v1"
FRICTION=0.
RESTITUTION=1.
START_V=(-2.,0.)
EPS=1e-9

def f(x):return round(float(x),9)

def solve_two_normals(v,normals):
    if len(normals)!=2:raise ValueError("exactly two normals are required")
    n0,n1=normals
    lengths=[hypot(*n) for n in normals]
    if any(abs(z-1.)>1e-7 for z in lengths):raise ValueError("non-unit measured normal")
    g00=dot(n0,n0);g01=dot(n0,n1);g11=dot(n1,n1)
    determinant=g00*g11-g01*g01
    if determinant<=1e-7:raise ValueError("dependent normals require a different solver")
    incoming=[dot(v,n) for n in normals]
    if any(z>=-EPS for z in incoming):raise ValueError("not a simultaneous incoming pair")
    # Equal restitution normal constraints and nonnegative unilateral impulses:
    # n_i · (v + sum_j lambda_j n_j) = -n_i · v  (e=1).
    rhs=[-2*z for z in incoming]
    impulses=((rhs[0]*g11-rhs[1]*g01)/determinant,
              (rhs[1]*g00-rhs[0]*g01)/determinant)
    if any(z<=EPS for z in impulses):
        raise ValueError("contact requires negative or inactive normal impulse")
    outgoing=add(v,add(mul(impulses[0],n0),mul(impulses[1],n1)))
    speed_before=dot(v,v)
    speed_after=dot(outgoing,outgoing)
    if not all(isfinite(z) for z in (*outgoing,*impulses)):
        raise ValueError("non-finite candidate")
    if any(abs(dot(outgoing,n)+vin)>3e-8 for n,vin in zip(normals,incoming)):
        raise ValueError("simultaneous normal restitution unsatisfied")
    if speed_after>speed_before+3e-8 or abs(speed_after-speed_before)>3e-8:
        raise ValueError("frictionless restitution generated/lost energy")
    if any(dot(outgoing,n)<=0 for n in normals):
        raise ValueError("candidate exits into a contact")
    return {"normal_impulses":[f(q) for q in impulses],
            "incoming_normal_speeds":[f(q) for q in incoming],
            "outgoing_normal_speeds":[f(dot(outgoing,n)) for n in normals],
            "incoming_velocity":[f(q) for q in v],
            "outgoing_velocity":[f(q) for q in outgoing],
            "incoming_spin":0.,"outgoing_spin":0.,
            "kinetic_energy_before":f(.5*speed_before),
            "kinetic_energy_after":f(.5*speed_after),
            "friction":FRICTION,"normal_restitution":RESTITUTION,
            "normal_matrix_determinant":f(determinant)}

def run():
    prior=threshold_run()
    faces=prior["source_geometry"]["surfaces"]
    y=prior["junction_contact"]["entry_y"]
    paired=arrival_pair(y,faces)
    t=(paired[0]["time"]+paired[1]["time"])/2
    point=tuple(paired[0]["center"])
    if abs(paired[0]["time"]-paired[1]["time"])>1e-9 or hypot(*sub(point,paired[1]["center"]))>1e-8:
        raise ValueError("original independent source pair no longer coincides")
    original=trace(y,faces)
    if original["status"]!="unresolved-multiple-contacts" or original["contacts"]:
        raise ValueError("Trial 06 no longer stops at the true tie")
    trial=solve_two_normals(START_V,[q["normal"] for q in paired])
    outgoing=tuple(trial["outgoing_velocity"])
    # Construct a finite, separately marked counterfactual continuation.
    # Do NOT replace any existing single-contact trace() event.
    frames=[]
    min_clearance=float("inf")
    for i in range(round(HORIZON/STEP)+1):
        clock=i*STEP
        if clock<=t:
            center=add((12.,y),mul(clock,START_V))
        else:
            center=add(point,mul(clock-t,outgoing))
        for seg in faces:
            distance,_,_=nearest(center,seg)
            min_clearance=min(min_clearance,distance)
            if distance<R-3e-7:raise ValueError("candidate penetrated a source surface")
        if not (R<=center[0]<=24.-R and R<=center[1]<=6.-R):
            raise ValueError("candidate escaped original WORLD perimeter")
        frames.append({"time":f(clock),"position":[f(q) for q in center],
                       "velocity":[f(q) for q in (START_V if clock<t else outgoing)],
                       "spin":0.,"orientation":0.})
    if any(dot(outgoing,q["normal"])<=EPS for q in paired):
        raise ValueError("outgoing candidate would reenter the same crossing")
    receipt={
        "entry_y":round(y,12),"collision_time":round(t,12),
        "collision_center":[f(q) for q in point],
        "source_ids":[q["surface_id"] for q in paired],
        "normals":[[f(z) for z in q["normal"]] for q in paired],
        **trial,"frames":frames,
        "minimum_sampled_clearance":f(min_clearance),
        "candidate_full_horizon_observed":True,
        "original_stop":original["status"]}
    return {
        "schema":SCHEMA,"geometry":prior["source_geometry"],
        "candidate":receipt,
        "baseline_trial06_status":original["status"],
        "nearby_trial07_statuses":[{"offset":z["offset"],"status":z["status"],
                                    "first_contact":z["first_contact"]}
                                   for z in prior["probes"]],
        "original_trial06_friction":.4,
        "candidate_friction":FRICTION,
        "candidate_is_a_new_comparison_not_original_friction_physics":True,
        "simultaneous_frictional_manifold_solved":False,
        "arbitrary_junctions_solved":False,
        "real_material_behavior_verified":False,
        "original_blueprint_generated":False}
