"""WORLD A/B trial 04: source-wall angle and rigid-square angular impulse.

Both branches use the SAME incoming rigid 2-D square and the SAME finite
source-wall length. The A branch retains the original vertical source wall;
B rotates its face by a controlled angle about the original wall center.
Event-time first contact is solved for the rigid polygon's earliest support.
The collision impulse includes moment of inertia and contact lever arm.

Only the FIRST collision is independently adjudicated; the short after-look
is an explicitly UNCONSTRAINED ballistic projection, not a continuous
contact/penetration-free simulation. The receiver is a proposal derived from
actual outgoing velocity, NOT an empirically verified next collision.
No guide/funnel/diverter/spiral category enters the generator.
"""
from __future__ import annotations
from math import cos,sin,radians,hypot,isfinite
from systems.workspace.world_ab_contact_trial import HALF,WALL,WORLD_HEIGHT,WORLD_WIDTH,initial

SCHEMA="world-ab-oblique-normal-angular-impact/v1"
MASS=1.0
INERTIA=MASS*(2*HALF)**2/6
WALL_CENTER=(float(WALL["x"]),float(WALL["y"])+.5)
SPAN=1.0
AFTER_LOOK=.025
RECEIVER_LOOK=.6

def round9(x):return round(float(x),9)

def dot(x,y):return x[0]*y[0]+x[1]*y[1]
def cross(x,y):return x[0]*y[1]-x[1]*y[0]
def vertices():
    return [(-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF)]

def angle_normal(angle):
    if type(angle) not in (int,float) or not isfinite(angle) or not 0<=angle<=20:
        raise ValueError("angle outside bounded original WALL trial (0–20 degrees)")
    a=radians(angle)
    return [-cos(a),-sin(a)]

def strike(start,angle):
    start=initial(**start)
    n=angle_normal(angle)
    tangent=[-n[1],n[0]]
    p=[start["x"],start["y"]]
    v=[start["vx"],start["vy"]]
    # earliest incoming *rotationally still* square support relative to wall.
    distances=[dot(c,n) for c in vertices()]
    minimum=min(distances)
    support=[c for c,d in zip(vertices(),distances) if abs(d-minimum)<1e-10]
    lever=[sum(c[i] for c in support)/len(support) for i in (0,1)]
    separation=dot([p[0]-WALL_CENTER[0],p[1]-WALL_CENTER[1]],n)+minimum
    approach=dot(v,n)
    if not separation>0 or not approach<0:
        raise ValueError("block must approach original source wall from outside")
    hit_time=-separation/approach
    hit_center=[p[i]+hit_time*v[i] for i in (0,1)]
    contact_point=[hit_center[i]+lever[i] for i in (0,1)]
    span_parameter=dot([contact_point[i]-WALL_CENTER[i] for i in (0,1)],tangent)
    # This finite segment condition applies to the actual support point,
    # not merely to the square centre.
    if not (0<hit_time<4.0 and abs(span_parameter)<=SPAN/2+1e-9):
        return {"hit":False,"reason":"CONTACT_OUTSIDE_FINITE_SOURCE_FACE",
            "angle_degrees":float(angle),"normal":[round9(k) for k in n],
            "source_wall_center":list(WALL_CENTER),
            "source_wall_span":SPAN,"incoming":start,
            "candidate_receiver":None}
    r_cross_n=cross(lever,n)
    impulse=-(1+start["restitution"])*approach/(1/MASS+r_cross_n**2/INERTIA)
    vout=[v[i]+impulse*n[i]/MASS for i in (0,1)]
    spin=impulse*r_cross_n/INERTIA
    after_center=[hit_center[i]+vout[i]*AFTER_LOOK for i in (0,1)]
    after_theta=spin*AFTER_LOOK
    speed=hypot(*vout)
    proposal=None
    if speed>1e-10:
        outward=[vout[0]/speed,vout[1]/speed]
        proposed_center=[contact_point[i]+vout[i]*RECEIVER_LOOK for i in (0,1)]
        # Candidate contact receiver is oriented against observed motion.
        proposed_normal=[-outward[i] for i in (0,1)]
        proposal={"center":[round9(z) for z in proposed_center],
            "normal":[round9(z) for z in proposed_normal],
            "tangent":[round9(-proposed_normal[1]),round9(proposed_normal[0])],
            "source_rule":"outgoing_velocity_times_fixed_observation_duration",
            "projection_duration":RECEIVER_LOOK,
            "surface_built":False,"second_contact_witnessed":False}
    return {"hit":True,"reason":"FIRST_CONTACT_SOLVED",
        "angle_degrees":float(angle),
        "normal":[round9(z) for z in n],
        "tangent":[round9(z) for z in tangent],
        "source_wall_center":list(WALL_CENTER),"source_wall_span":SPAN,
        "incoming":start,"first_contact_time":round9(hit_time),
        "first_contact_center":[round9(z) for z in hit_center],
        "contact_point":[round9(z) for z in contact_point],
        "support_lever":[round9(z) for z in lever],
        "support_count":len(support),
        "finite_wall_parameter":round9(span_parameter),
        "normal_impulse":round9(impulse),
        "velocity_before":[round9(z) for z in v],
        "velocity_after":[round9(z) for z in vout],
        "angular_velocity_before":0.0,"angular_velocity_after":round9(spin),
        "moment_of_inertia":round9(INERTIA),
        "kinetic_energy_before":round9(.5*MASS*dot(v,v)),
        "kinetic_energy_after":round9(.5*MASS*dot(vout,vout)+.5*INERTIA*spin*spin),
        "after_look":{"duration":AFTER_LOOK,
             "predicted_center":[round9(z) for z in after_center],
             "predicted_orientation_radians":round9(after_theta),
             "continuous_contact_retested":False,
             "unconstrained_ballistic_projection_only":True},
        "candidate_receiver":proposal}

def experiment(start=None,*,angle=20):
    s=initial(**(start or {}))
    a=strike(s,0.0)
    b=strike(s,angle)
    if not a["hit"]:
        raise ValueError("original vertical wall first impact not witnessed")
    return {"schema":SCHEMA,"world_dimensions":[WORLD_WIDTH,WORLD_HEIGHT],
        "source_wall":{"center":list(WALL_CENTER),"span":SPAN,"x":WALL["x"],
                       "original_orientation":"vertical"},
        "body":{"shape":"rigid-square","half_size":HALF,"mass":MASS,
                "moment_of_inertia":round9(INERTIA)},
        "A_original_vertical":a,
        "B_oblique":b,
        "angled_wall_is_counterfactual_change":True,
        "baseline_iterated_wall_source_preserved":True,
        "generated_shapes_from_original_blueprint":[],
        "material_properties_measured":False,
        "continuous_physics_after_first_impact_verified":False,
        "exact_original_blueprint_generated":False,
        "literal_all_Earth_physics":False}
