"""WORLD A/B Trial 05: functional routing through connected source-derived faces.

Cross-run assembly: combine the TWO receiver segments from Trial 04B's
separately executed (0°, .4) and (20°, .4) source experiments. Their actual
segment-line intersection establishes geometrical connectedness. This is a
declared counterfactual assembly (not observed spontaneous co-generation).
No target guide/funnel/diverter/spiral labels feed any construction routine.

Fresh disc probes approach from the RIGHT. A first-contact continuous-time
finite-segment solver decides which one-sided face is hit first, and computes
a rigid-disc angular impulse. Compare against the same probes facing only the
0° receiver. Claims are limited to FIRST-contact branching and outgoing motion:
the acute crossing junction is not yet a fully resolved multi-contact rigid
contact manifold or a buildable material object.
"""
from __future__ import annotations
from math import hypot
from systems.workspace.world_ab_oblique_rotation import run as prior_run,impact,R,I,RESTITUTION
SCHEMA="world-ab-connected-receiver-routing/v1"
SOURCE_BRANCHES=((0,.4),(20,.4))
PROBE_Y=(.9,1.05,1.2,1.6,1.8,2.0,2.25)
PROBE_X=12.
PROBE_V=(-2.,0.)
PROBE_LOOK=.20
SPAN=1.
EPS=1e-9

def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def mul(k,a):return (k*a[0],k*a[1])
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def f(v):return round(float(v),9)

def assemble():
    source=prior_run()
    candidates=[]
    for angle,friction in SOURCE_BRANCHES:
        matches=[c for c in source["branches"]
            if c["source_angle_degrees"]==angle and c["friction"]==friction]
        if len(matches)!=1:raise ValueError("source experiment is not a unique original branch")
        original=matches[0]["constructed_receiver"]
        anchor=tuple(original["anchor"])
        normal=tuple(original["normal"])
        scale=hypot(*normal)
        if abs(scale-1)>1e-8:raise ValueError("measured receiver normal not unit")
        tangent=(-normal[1],normal[0])
        first=add(anchor,mul(-SPAN/2,tangent))
        last=add(anchor,mul(SPAN/2,tangent))
        candidates.append({
            "id":f"source-derived-{angle}-friction-{friction}",
            "source_original_angle":angle,"source_friction":friction,
            "anchor":[f(x) for x in anchor],
            "normal":[f(x) for x in normal],
            "endpoints":[[f(z) for z in first],[f(z) for z in last]],
            "origin_04B_branch_first_contact":matches[0]["events"][0]["at"],
            "origin_04B_branch_receiver_contact":matches[0]["events"][1]["at"],
            "source_receipt_id":original["id"],
        })
    a,b=candidates
    aa=tuple(a["anchor"]);bb=tuple(b["anchor"])
    ta=tuple(sub(a["endpoints"][1],a["endpoints"][0]))
    tb=tuple(sub(b["endpoints"][1],b["endpoints"][0]))
    determinant=cross(ta,tb)
    if abs(determinant)<1e-5:raise ValueError("no novel orientation / parallel faces")
    delta=sub(bb,aa)
    u=cross(delta,tb)/determinant
    v=cross(delta,ta)/determinant
    if not (-.5<=u<=.5 and -.5<=v<=.5):
        raise ValueError("measured finite source-generated segments do not connect")
    vertex=add(aa,mul(u,ta))
    if not (R<vertex[0]<24-R and R<vertex[1]<6-R):
        raise ValueError("source-derived junction outside physical WORLD")
    return {"schema":SCHEMA,"assembly_policy":"combine independent observed 04B receivers without moving or relabeling",
        "source_experiment_is_separate_cross_run_branches":True,
        "surfaces":candidates,
        "junction":[f(z) for z in vertex],
        "junction_local_coordinates":[f(u),f(v)],
        "finite_intersection_verified":True,
        "topology":{"segments":2,"intersections":1,"connected_components":1,
                    "curved_segments":0},
        "original_geometry_24x6_preserved":True,
        "simultaneous_disc_multicontact_resolved":False}

def _hit(start,face):
    n=face["normal"];origin=face["anchor"]
    approach=dot(PROBE_V,n)
    if approach>=-EPS:return None
    t=(R-dot(sub(start,origin),n))/approach
    if t<=EPS:return None
    center=add(start,mul(t,PROBE_V))
    point=sub(center,mul(R,n))
    tangent=(-n[1],n[0])
    along=dot(sub(point,origin),tangent)
    if abs(along)>SPAN/2+EPS:return None
    # At a geometrical crossing simultaneous impacts can be ambiguous;
    # witness tests explicitly reject near-ties rather than pick a label.
    return t,center,along

def probe(y,faces,*,mu=.4):
    if y not in PROBE_Y:raise ValueError("only predeclared probe levels supported")
    if len(faces) not in (1,2):raise ValueError("invalid assembled source extent")
    start=(PROBE_X,y)
    candidates=[]
    for face in faces:
        h=_hit(start,face)
        if h is not None:candidates.append((h[0],face["id"],face,h))
    candidates.sort(key=lambda item:(item[0],item[1]))
    if len(candidates)>=2 and abs(candidates[0][0]-candidates[1][0])<.01:
        raise ValueError("unresolved simultaneous receiver contacts")
    if not candidates:
        return {"initial":[f(z) for z in start],"source_first_contact":None,
            "hit_time":None,"contact_center":None,
            "outgoing_velocity":[f(z) for z in PROBE_V],
            "angular_velocity":0.,"look_after":None,
            "contact_impulse":None}
    t,id,face,( _,p,within)=candidates[0]
    velocity,spin,event=impact(PROBE_V,0.,tuple(face["normal"]),mu)
    look=add(p,mul(PROBE_LOOK,velocity))
    return {"initial":[f(z) for z in start],"source_first_contact":id,
        "hit_time":f(t),"contact_center":[f(z) for z in p],
        "contact_tangent_coordinate":f(within),
        "outgoing_velocity":[f(z) for z in velocity],
        "angular_velocity":f(spin),"look_after":[f(z) for z in look],
        "contact_impulse":event}

def run():
    geo=assemble()
    base=[probe(y,geo["surfaces"][:1]) for y in PROBE_Y]
    connected=[probe(y,geo["surfaces"]) for y in PROBE_Y]
    changed=[]
    first={}
    for y,a,b in zip(PROBE_Y,base,connected):
        if a["source_first_contact"]!=b["source_first_contact"] or a["outgoing_velocity"]!=b["outgoing_velocity"]:
            changed.append(y)
        first[str(y)]=b["source_first_contact"]
    return {"schema":SCHEMA,"geometry":geo,"probe_y_levels":list(PROBE_Y),
        "baseline_first_face_only":base,"assembled_two_faces":connected,
        "source_first_surface_by_level":first,
        "route_changed_probe_levels":changed,
        "distinct_first_contacts":sorted(set(x["source_first_contact"] for x in connected if x["source_first_contact"])),
        "functional_first_contact_splitting_verified":len(set(x["source_first_contact"] for x in connected if x["source_first_contact"]))>=2 and bool(changed),
        "simultaneous_source_generation_proven":False,
        "continuous_multicontact_navigation_verified":False,
        "target_original_blueprint_shapes_generated":False,
        "material_earth_physics_verified":False}
