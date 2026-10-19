"""WORLD Trial 07: locate a real two-face arrival tie; do NOT solve it.

Uses only the unchanged source-generated Trial 05 finite segments and Trial 06
full-motion engine. Interior contact-time crossing is a diagnostic, not a
simultaneous-contact impulse or a blueprint construction. The predeclared
bracket lies between the existing 1.35 and 1.40-height source probes.
"""
from __future__ import annotations
from math import hypot
from systems.workspace.world_ab_connected_routing import assemble
from systems.workspace.world_ab_junction_continuous import trace,R,dot,sub,add,mul

SCHEMA = "world-ab-junction-arrival-tie/v1"
BRACKET = (1.35,1.4)
OFFSETS = (-.01,-.0001,-.000001,-.00000001,0.,.00000001,.000001,.0001,.01)
INITIAL = (12.,-2.)
EPS = 1e-9

def interior_arrival(y, face):
    """First incoming finite-segment INTERIOR contact on the original ray."""
    a,b = face["endpoints"]
    tangent = sub(b,a)
    length = hypot(*tangent)
    if length <= EPS: raise ValueError("degenerate original segment")
    tangent = mul(1/length,tangent)
    normal = (-tangent[1],tangent[0])
    p,v = (INITIAL[0],y),(INITIAL[1],0.)
    signed = dot(sub(p,a),normal)
    rate = dot(v,normal)
    answers = []
    if abs(rate) <= EPS: raise ValueError("source probe is parallel")
    for side in (-1,1):
        n = mul(side,normal)
        if dot(v,n) >= -EPS: continue
        t = (side*R-signed)/rate
        if t <= EPS or t >= 1.5: continue
        center = add(p,mul(t,v))
        along = dot(sub(center,a),tangent)
        if EPS < along < length-EPS:
            answers.append((t,center,n))
    if len(answers)!=1: raise ValueError("interior contact not uniquely reached")
    t,center,n = answers[0]
    return {"surface_id":face["id"],"feature":"interior","time":t,
            "center":center,"normal":n}

def arrival_pair(y, faces):
    if not (BRACKET[0]-.02 <= y <= BRACKET[1]+.02):
        raise ValueError("outside predeclared local bracket")
    if len(faces)!=2 or faces[0]["id"]==faces[1]["id"]:
        raise ValueError("expected two distinct original source faces")
    return [interior_arrival(y,f) for f in faces]

def locate(faces):
    lo,hi = BRACKET
    def gap(y):
        a,b = arrival_pair(y,faces)
        return a["time"]-b["time"]
    gl,gh = gap(lo),gap(hi)
    if gl*gh >= 0: raise ValueError("source did not bracket an arrival switch")
    for _ in range(64):
        mid=(lo+hi)/2
        gm=gap(mid)
        if gm == 0: lo=hi=mid;break
        if gl*gm > 0: lo,gl = mid,gm
        else: hi,gh = mid,gm
    root=round((lo+hi)/2,12)
    a,b=arrival_pair(root,faces)
    if abs(a["time"]-b["time"])>1e-9:
        raise ValueError("arrival tie is not independently resolved by bracketing")
    if hypot(*sub(a["center"],b["center"]))>1e-8:
        raise ValueError("source contacts are not at the same real disc center")
    return root,[a,b]

def run():
    geometry=assemble()
    faces=geometry["surfaces"]
    height,contacts=locate(faces)
    contact={
        "entry_y":height,
        "candidate_gap":round(contacts[0]["time"]-contacts[1]["time"],12),
        "contact_time":round(sum(z["time"] for z in contacts)/2,12),
        "contact_center":[round(z,9) for z in contacts[0]["center"]],
        "source_ids":[z["surface_id"] for z in contacts],
        "features":[z["feature"] for z in contacts],
        "normals":[[round(z,9) for z in x["normal"]] for x in contacts],
    }
    probes=[]
    for offset in OFFSETS:
        y=height+offset
        result=trace(y,faces)
        reverse=trace(y,faces[::-1])
        probes.append({
            "offset":offset,"entry_y":round(y,12),
            "status":result["status"],
            "unresolved":result["unresolved"],
            "first_contact":result["first_contact"],
            "observed_contacts":len(result["contacts"]),
            "end_time":result["exit"]["time"],
            "surface_order_independent":result==reverse,
        })
    return {
        "schema":SCHEMA,"source_geometry":geometry,"bracket":list(BRACKET),
        "junction_contact":contact,"probes":probes,
        "simultaneous_contact_solver":False,
        "unresolved_contacts_remain_unresolved":True,
        "source_04B_branches_simultaneously_generated":False,
        "earth_material_equivalence":False,
        "full_original_blueprint_generated":False,
    }
