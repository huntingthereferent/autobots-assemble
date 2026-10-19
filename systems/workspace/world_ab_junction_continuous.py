"""WORLD Trial 06: continuous motion in two measured finite source segments.

Source geometry is generated from the original Trial 04B receivers in Trial
05. Every line segment is treated as a finite two-sided capsule contact:
straight interior plus real endpoint caps. Impacts occur at swept continuous
times within a sampled observation grid. Ambiguous simultaneous contacts
STOP rather than inventing a two-contact impulse. This is virtual rigid-disc
mechanics, not complete material or Earth physics.
"""
from __future__ import annotations
from math import sqrt,hypot
from systems.workspace.world_ab_connected_routing import assemble,PROBE_Y

SCHEMA="world-ab-connected-continuous-junction/v1"
R=.25
I=.03125
STEP=.05
HORIZON=1.5
EPS=1e-9
CLEARANCE=2e-7
MAX_EVENTS=12
ADVERSARIAL_Y=(1.3,1.322386,1.4)

def dot(x,y):return x[0]*y[0]+x[1]*y[1]
def sub(x,y):return (x[0]-y[0],x[1]-y[1])
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def mul(c,x):return (c*x[0],c*x[1])
def rounded(x):return round(float(x),9)

def nearest(p,seg):
    a,b=seg["endpoints"]
    ab=sub(b,a)
    fraction=max(0.,min(1.,dot(sub(p,a),ab)/dot(ab,ab)))
    point=add(a,mul(fraction,ab))
    return hypot(*sub(p,point)),point,fraction

def candidates(p,v,segments,remaining):
    """Continuous swept disc vs finite segment interior AND circular endpoints."""
    result=[]
    speed2=dot(v,v)
    if speed2<=1e-10:return result
    for seg in segments:
        a,b=seg["endpoints"]
        tangent=sub(b,a)
        length=hypot(*tangent)
        tangent=mul(1/length,tangent)
        normal=(-tangent[1],tangent[0])
        signed=dot(sub(p,a),normal)
        rate=dot(v,normal)
        if abs(rate)>EPS:
            for side in (-1,1):
                contact_normal=mul(side,normal)
                if dot(v,contact_normal)>=-EPS:continue
                t=(side*R-signed)/rate
                if not (-EPS<=t<=remaining+EPS):continue
                t=max(0.,t)
                center=add(p,mul(t,v))
                along=dot(sub(center,a),tangent)
                if EPS<along<length-EPS:
                    result.append((t,seg["id"],"interior",contact_normal,center))
        for i,endpoint in enumerate((a,b)):
            relative=sub(p,endpoint)
            linear=dot(relative,v)
            constant=dot(relative,relative)-R*R
            discriminant=linear*linear-speed2*constant
            if discriminant<0:continue
            t=(-linear-sqrt(max(discriminant,0.)))/speed2
            if not (-EPS<=t<=remaining+EPS):continue
            t=max(0.,t)
            center=add(p,mul(t,v))
            delta=sub(center,endpoint)
            distance=hypot(*delta)
            if distance<=1e-12:continue
            normal=mul(1/distance,delta)
            if dot(v,normal)<-EPS:
                result.append((t,seg["id"],f"endpoint-{i}",normal,center))
    return sorted(result,key=lambda x:(x[0],x[1],x[2]))

def physical_impulse(v,spin,normal,friction=.4):
    length=hypot(*normal)
    if abs(length-1)>1e-7:raise ValueError("contact normal not unit")
    normal=mul(1/length,normal)
    tangent=(-normal[1],normal[0])
    approach=dot(v,normal)
    if approach>=-EPS:raise ValueError("nonincoming contact")
    jn=-2*approach
    slip=dot(v,tangent)-spin*R
    jt=max(-friction*jn,min(friction*jn,-slip/(1+R*R/I)))
    outgoing=add(v,add(mul(jn,normal),mul(jt,tangent)))
    after_spin=spin-R*jt/I
    energy=lambda velocity,omega:.5*dot(velocity,velocity)+.5*I*omega*omega
    before=energy(v,spin)
    after=energy(outgoing,after_spin)
    if after>before+1e-8:raise ValueError("contact generated kinetic energy")
    receipt={"normal_impulse":rounded(jn),"tangential_impulse":rounded(jt),
             "energy_before":rounded(before),"energy_after":rounded(after)}
    return outgoing,after_spin,receipt

def trace(y,segments):
    if not 0<=y<=6:raise ValueError("probe outside original WORLD")
    pos=(12.,float(y))
    vel=(-2.,0.)
    spin=0.
    orientation=0.
    clock=0.
    contacts=[]
    frames=[{"time":0.,"position":[12.,rounded(y)],"velocity":[-2.,0.],
             "spin":0.,"orientation":0.}]
    lowest=float("inf")
    status="completed"
    unresolved=None
    for tick in range(1,round(HORIZON/STEP)+1):
        budget=tick*STEP-clock
        while budget>EPS:
            possible=candidates(pos,vel,segments,budget)
            if not possible:
                orientation+=spin*budget
                pos=add(pos,mul(budget,vel))
                clock+=budget
                budget=0.
                break
            dt,surface,feature,normal,center=possible[0]
            touching=[seg["id"] for seg in segments if nearest(center,seg)[0]<=R+CLEARANCE]
            ambiguity=(len(set(touching))>1 or
                       any(abs(other[0]-dt)<1e-7 and other[1]!=surface for other in possible[1:]))
            orientation+=spin*dt
            pos=center
            clock+=dt
            budget-=dt
            if ambiguity:
                status="unresolved-multiple-contacts"
                unresolved={"time":rounded(clock),"surfaces":sorted(set(touching)),
                            "center":[rounded(z) for z in pos]}
                break
            old_vel=vel
            old_spin=spin
            vel,spin,impulse=physical_impulse(vel,spin,normal)
            contacts.append({"time":rounded(clock),"surface_id":surface,"feature":feature,
                             "center":[rounded(z) for z in pos],
                             "normal":[rounded(z) for z in normal],
                             "incoming_velocity":[rounded(z) for z in old_vel],
                             "outgoing_velocity":[rounded(z) for z in vel],
                             "incoming_spin":rounded(old_spin),"outgoing_spin":rounded(spin),**impulse})
            if len(contacts)>=MAX_EVENTS:
                status="unresolved-event-budget"
                unresolved={"time":rounded(clock)}
                break
        for seg in segments:
            distance,_,_=nearest(pos,seg)
            lowest=min(lowest,distance)
            if distance<R-CLEARANCE:
                status="penetration"
                unresolved={"time":rounded(clock),"surface_id":seg["id"],
                            "distance":rounded(distance)}
                break
        if not (R-1e-7<=pos[0]<=24-R+1e-7 and R-1e-7<=pos[1]<=6-R+1e-7):
            status="outside-world"
            unresolved={"time":rounded(clock)}
        frames.append({"time":rounded(clock),"position":[rounded(z) for z in pos],
                       "velocity":[rounded(z) for z in vel],
                       "spin":rounded(spin),"orientation":rounded(orientation)})
        if status!="completed":break
    return {"entry_y":rounded(y),"status":status,"frames":frames,
            "contacts":contacts,"first_contact":contacts[0]["surface_id"] if contacts else None,
            "exit":frames[-1],"minimum_frame_clearance":rounded(lowest),
            "unresolved":unresolved}

def run(geometry=None,probe_levels=None):
    geometry=assemble() if geometry is None else geometry
    levels=tuple(PROBE_Y)+ADVERSARIAL_Y if probe_levels is None else tuple(probe_levels)
    solo=[trace(y,geometry["surfaces"][:1]) for y in levels]
    connected=[trace(y,geometry["surfaces"]) for y in levels]
    return {"schema":SCHEMA,"geometry":geometry,
            "probe_levels":list(levels),"baseline_finite_capsule":solo,
            "connected_finite_capsule":connected,
            "completed_cases":sum(z["status"]=="completed" for z in connected),
            "unresolved_cases":[{"entry_y":z["entry_y"],"status":z["status"]}
                               for z in connected if z["status"]!="completed"],
            "finite_segment_endpoints_enabled":True,
            "restitution":1.,"friction":.4,"virtual_disc_radius":R,
            "physical_world_dimensions":[24,6],
            "multi_contact_manifold_solver":False,
            "source_04B_branches_simultaneously_generated":False,
            "full_original_blueprint_generated":False}
