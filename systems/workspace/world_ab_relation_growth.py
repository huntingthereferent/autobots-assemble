"""WORLD / A-B physical composition trial 02.

Construct ONE previously nonexistent collision face from the measured rebound
relationship of Trial 01; then replay the SAME moving object with it present.
No reference to desired guide/funnel/diverter/spiral categories is imported.
Construction is a declared *digital assembly rule*, NOT spontaneous material
self-assembly or evidence about actual Earth materials.

The original source-owned wall at x=12 is unchanged. As a bounded extension of
the original simple translational-square model, both obstacles are vertical
one-sided line faces with square half-width 0.25; no torque, gravity or friction.
"""
from __future__ import annotations
from math import isfinite
from systems.workspace.world_ab_contact_trial import (
    HALF,DT,STEPS,WALL,WORLD_WIDTH,WORLD_HEIGHT,initial,trial)

SCHEMA="world-ab-relation-derived-second-surface/v1"
PROJECTION_DURATION=0.75
SOURCE_SPAN=1.0
EPS=1e-9

def clean(v):
    return round(float(v),9)

def construct(observation):
    """Inputs only original SOURCE wall contact and returned velocity.

    A receiver is placed one fixed temporal observation span along the
    measured outgoing direction. Its x-face is perpendicular to the dominant
    outgoing horizontal movement. Width/height are inherited from the source
    boundary; its position is NOT set to match an external target picture.
    """
    if not isinstance(observation,dict) or observation.get("schema")!="world-ab-physical-contact-trial/v1":
        raise ValueError("not an admitted original physical observation")
    if observation.get("source_boundary",{}).get("face_x")!=WALL["x"] or observation.get("half_extent")!=HALF:
        raise ValueError("original physical calibration changed")
    c=observation.get("B_with_wall",{}).get("contacts")
    if type(c) is not list or len(c)!=1:
        return {"constructed":False,"reason":"NO_SINGLE_SOURCE_CONTACT",
                "surface":None,"source_contact":None}
    hit=c[0]
    vy=hit["outgoing_velocity"][1]
    vx=hit["outgoing_velocity"][0]
    if not all(type(x) in (int,float) and isfinite(x) for x in (vx,vy,hit["time"],hit["x"],hit["y"])):
        raise ValueError("contact result invalid")
    if abs(vx)<=EPS:
        return {"constructed":False,"reason":"NO_OUTGOING_REBOUND",
                "surface":None,"source_contact":hit}
    if not (vx<0 and hit["normal"]==[-1.0,0.0] and
            abs(hit["x"]-(WALL["x"]-HALF))<EPS and
            hit["wall_id"]==WALL["id"]):
        raise ValueError("source rebound was not independently admitted")
    face=hit["x"]+vx*PROJECTION_DURATION
    center=hit["y"]+vy*PROJECTION_DURATION
    if not (HALF<face<WALL["x"]-2*HALF and
            SOURCE_SPAN/2+HALF<center<WORLD_HEIGHT-SOURCE_SPAN/2-HALF):
        return {"constructed":False,"reason":"PROJECTED_RECEIVER_OUTSIDE_WORLD",
                "surface":None,"source_contact":hit}
    return {"constructed":True,"reason":"PROJECTED_FROM_OBSERVED_REBOUND",
        "surface":{
            "id":"relation-surface-1",
            "face_x":clean(face),
            "y_min":clean(center-SOURCE_SPAN/2),
            "y_max":clean(center+SOURCE_SPAN/2),
            "normal":[1.0,0.0],
            "basis_contact_time":hit["time"],
            "basis_contact_xy":[hit["x"],hit["y"]],
            "basis_outgoing_velocity":list(hit["outgoing_velocity"]),
            "projection_duration":PROJECTION_DURATION,
            "source_boundary_id":WALL["id"],
        },
        "source_contact":hit}

def replay(start,structure):
    """Continuous event-time contact within each fixed output step.

    Source wall (vx>0) and newly assembled west-facing receiver (vx<0)
    are competing event candidates. Next event is selected by physically
    nearest admissible time, not a predetermined structure name.
    """
    s=initial(**start)
    x,y,vx,vy=[s[k] for k in ("x","y","vx","vy")]
    shape=structure.get("surface")
    if structure.get("constructed") is not True or type(shape) is not dict:
        raise ValueError("there is no physically assembled receiver")
    if shape.get("id")!="relation-surface-1" or shape.get("normal")!=[1.0,0.0]:
        raise ValueError("receiver identity or collision normal drifted")
    frames=[{"turn":0,"time":0.0,"x":clean(x),"y":clean(y),"vx":clean(vx),"vy":clean(vy)}]
    contacts=[]
    for turn in range(1,STEPS+1):
        remaining=DT
        within=0.
        for _ in range(3):
            if remaining<=EPS:break
            candidate=[]
            # First source wall is a west-face. The original block must
            # approach from the left.
            if vx>EPS:
                t=(WALL["x"]-HALF-x)/vx
                if t>=-EPS and t<=remaining+EPS:
                    cy=y+vy*t
                    if WALL["y"]-HALF<=cy<=WALL["y"]+SOURCE_SPAN+HALF:
                        candidate.append((max(t,0.),"source-wall"))
            if vx< -EPS:
                t=(shape["face_x"]+HALF-x)/vx
                if t>=-EPS and t<=remaining+EPS:
                    cy=y+vy*t
                    if shape["y_min"]-HALF<=cy<=shape["y_max"]+HALF:
                        candidate.append((max(t,0.),shape["id"]))
            if not candidate:
                x+=vx*remaining;y+=vy*remaining
                within+=remaining;remaining=0.
                break
            elapsed,kind=min(candidate,key=lambda e:e[0])
            x+=vx*elapsed;y+=vy*elapsed
            within+=elapsed;remaining-=elapsed
            incoming=[vx,vy]
            old_energy=0.5*(vx*vx+vy*vy)
            vx=-s["restitution"]*vx
            contacts.append({
               "time":clean((turn-1)*DT+within),
               "surface":kind,
               "x":clean(x),"y":clean(y),
               "incoming_velocity":[clean(z) for z in incoming],
               "outgoing_velocity":[clean(vx),clean(vy)],
               "normal":[-1.0,0.0] if kind=="source-wall" else [1.0,0.0],
               "normal_impulse":clean((1+s["restitution"])*abs(incoming[0])),
               "energy_before":clean(old_energy),
               "energy_after":clean(0.5*(vx*vx+vy*vy)),
             })
            if len(contacts)>3:
                raise ValueError("unexpected repeated impacts beyond bounded trial")
        else:
            raise ValueError("event iteration guard exceeded")
        if remaining>EPS:
            raise ValueError("event resolution did not consume entire time step")
        frames.append({"turn":turn,"time":clean(turn*DT),
            "x":clean(x),"y":clean(y),"vx":clean(vx),"vy":clean(vy)})
    if any(not (0<=f["x"]<=WORLD_WIDTH and 0<=f["y"]<=WORLD_HEIGHT) for f in frames):
        raise ValueError("assembled collision path escaped WORLD")
    return {"frames":frames,"contacts":contacts,"final":frames[-1]}

def experiment(start=None):
    s=initial(**(start or {}))
    original=trial(s)
    derived=construct(original)
    if not derived["constructed"]:
        return {"schema":SCHEMA,"input":s,"original":original,
            "assembly":derived,"second_motion":None,"new_surface_reused":False,
            "automatically_assembled_without_declared_rule":False,
            "full_visual_blueprint_generated":False}
    restored=replay(s,derived)
    source_hits=[c for c in restored["contacts"] if c["surface"]=="source-wall"]
    receiver_hits=[c for c in restored["contacts"] if c["surface"]=="relation-surface-1"]
    successful=bool(receiver_hits)
    if source_hits and (source_hits[0]["time"]!=original["B_with_wall"]["contacts"][0]["time"] or
        source_hits[0]["x"]!=original["B_with_wall"]["contacts"][0]["x"]):
        raise ValueError("original W13 source-wall interaction changed after assembly")
    return {"schema":SCHEMA,"input":s,
        "original":original,
        "assembly":derived,
        "second_motion":restored,
        "new_surface_reused":successful,
        "observed_contacts":[c["surface"] for c in restored["contacts"]],
        "automatically_assembled_without_declared_rule":False,
        "full_visual_blueprint_generated":False,
        "physics_scope":"one rigid translating square, one original wall, one relation-assembled collision face"}
