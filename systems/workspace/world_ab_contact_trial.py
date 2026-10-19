"""WORLD / A-B physical trial 01: one rigid translating block approaches a wall.

A transparent, deliberately SIMPLE two-dimensional mechanical model: virtual
grid distance units, one translational rigid square, no spin, gravity, drag or
surface friction, and specular restitution at one source-owned wall face.
Source wall geometry is read from the existing 24x6 physical construction.
The generator NEVER receives the visual blueprint's guide/funnel/spiral labels.
A/B contrasts the exact same initial motion with and without the wall.
"""
from __future__ import annotations
from math import isfinite, hypot
from systems.workspace.world_physical_construction import BLOCKS,WIDTH_PER_LANE,LANES,HEIGHT_PER_STAGE,STAGES

SCHEMA="world-ab-physical-contact-trial/v1"
HALF=0.25
DT=0.25
STEPS=16
WALL=next(x for x in BLOCKS if x["id"]=="boundary-wall")
WORLD_WIDTH=WIDTH_PER_LANE*len(LANES)
WORLD_HEIGHT=HEIGHT_PER_STAGE*len(STAGES)

def initial(*,x=3.0,y=1.35,vx=3.0,vy=0.12,restitution=1.0):
    raw=dict(x=x,y=y,vx=vx,vy=vy,restitution=restitution)
    if any(type(v) not in (float,int) or not isfinite(v) for v in raw.values()):
        raise ValueError("physical controls must be bounded finite scalars")
    if not (0.5<=x<=8 and 0.5<=y<=5.5 and 0.2<=vx<=4.0
            and -0.5<=vy<=0.5 and 0.0<=restitution<=1.0):
        raise ValueError("unsupported initial physical trial parameters")
    if x+HALF>=WALL["x"]:
        raise ValueError("block started within or beyond source wall")
    if not (0<=y-HALF and y+HALF<WORLD_HEIGHT):
        raise ValueError("block starts outside declared virtual floor")
    if not (0<=x+vx*DT<=WORLD_WIDTH):
        raise ValueError("block starts outside declared virtual floor")
    return {k:float(v) for k,v in raw.items()}

def _round(value):
    return round(float(value),9)

def integrate(start,*,wall_present):
    if type(wall_present) is not bool:raise ValueError("A/B wall branch must be explicit")
    s=initial(**start)
    x,y,vx,vy=(s[k] for k in ("x","y","vx","vy"))
    e=s["restitution"]
    if not (0<=x+vx*DT*STEPS<=WORLD_WIDTH
            and 0<=y+vy*DT*STEPS<=WORLD_HEIGHT):
        raise ValueError("free flight leaves this bounded physical experiment")
    frames=[{"turn":0,"time":0.0,"x":_round(x),"y":_round(y),
             "vx":_round(vx),"vy":_round(vy)}]
    contacts=[]
    for turn in range(1,STEPS+1):
        remaining=DT
        # Single west-face collision only; no hidden world-size wrap.
        if wall_present and not contacts and vx>0 and x+HALF<WALL["x"]+1e-8:
            distance=WALL["x"]-HALF-x
            hit_time=distance/vx if distance>=0 else float("inf")
            hit_y=y+vy*hit_time
            if (0<=hit_time<=remaining+1e-10 and
                WALL["y"]-HALF<=hit_y<=WALL["y"]+1+HALF):
                hit_time=min(hit_time,remaining)
                incoming=(vx,vy)
                incoming_energy=0.5*(vx*vx+vy*vy)
                x+=vx*hit_time;y+=vy*hit_time
                remaining-=hit_time
                vx=-e*vx
                contacts.append({
                  "time":_round((turn-1)*DT+hit_time),
                  "x":_round(x),"y":_round(y),
                  "incoming_velocity":[_round(z) for z in incoming],
                  "outgoing_velocity":[_round(vx),_round(vy)],
                  "normal":[-1.0,0.0],
                  "normal_impulse":_round((1+e)*incoming[0]),
                  "energy_before":_round(incoming_energy),
                  "energy_after":_round(0.5*(vx*vx+vy*vy)),
                  "wall_id":WALL["id"],
                })
        x+=vx*remaining;y+=vy*remaining
        frames.append({"turn":turn,"time":_round(turn*DT),
                       "x":_round(x),"y":_round(y),
                       "vx":_round(vx),"vy":_round(vy)})
    if any(not (0<=f["x"]<=WORLD_WIDTH and 0<=f["y"]<=WORLD_HEIGHT)
           for f in frames):
        raise ValueError("physical model path exits grid")
    # Relations discovered from actual before/contact/after states. These are
    # computed, not copied from the original A/B sketch or target list.
    relations=[]
    if start["vx"]>0 and start["x"]+HALF<WALL["x"]:
        relations.append("approaching-boundary")
    if contacts:
        relations.extend(["contact","normal-motion-reversed"])
        if contacts[0]["outgoing_velocity"]!=contacts[0]["incoming_velocity"]:
            relations.append("movement-redirected")
    elif frames[-1]["x"]+HALF>WALL["x"]:
        relations.append("passed-boundary-coordinate")
    else:
        relations.append("no-contact-observed")
    if hypot(frames[-1]["vx"],frames[-1]["vy"])>0:
        relations.append("continued-motion")
    return {"frames":frames,"contacts":contacts,"relations":relations,
            "final":frames[-1],
            "wall_present":wall_present}

def trial(start):
    s=initial(**start)
    absent=integrate(s,wall_present=False)
    solid=integrate(s,wall_present=True)
    if solid["contacts"]:
        c=solid["contacts"][0]
        if not (c["x"]==WALL["x"]-HALF and
                c["incoming_velocity"][0]>0 and
                c["outgoing_velocity"][0]<=0 and
                c["energy_after"]<=c["energy_before"]+1e-8):
            raise ValueError("unsupported collision dynamics")
    return {"schema":SCHEMA,
            "model":"2D-translational-square/specular-single-face/no-gravity-no-friction",
            "physical_world_dimensions":[WORLD_WIDTH,WORLD_HEIGHT],
            "source_boundary":{"id":WALL["id"],"face_x":WALL["x"],
                               "y_min":WALL["y"],"y_max":WALL["y"]+1},
            "half_extent":HALF,"duration":DT*STEPS,"time_step":DT,
            "initial":s,"A_without_wall":absent,"B_with_wall":solid,
            "observed_relation_difference":{
                "A":absent["relations"],"B":solid["relations"]},
            "literal_Earth_physics_equivalence":False,
            "source_blueprint_structure_generated":False,
            "clinical_evidence":False,
           }
