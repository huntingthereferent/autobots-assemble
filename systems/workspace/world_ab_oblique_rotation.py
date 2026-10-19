"""WORLD A/B Trial 04: oblique rigid-disc collision, tangential impulse and spin.

Four controlled branches vary the angle of an EXPERIMENTAL source face (0/20
degrees) and Coulomb friction (0/.4). The ORIGINAL 24x6 WORLD wall and
Trial-03 native source are NOT rewritten: the angled source is a separate,
explicitly marked comparison perturbation anchored at the original wall.
A measured outgoing velocity generates a NEW receiver's normal and location;
the source target diagram is not imported by this physics generator.

Two physical collisions are solved at continuous event times; a unit-mass
disc with I=1/2*m*r*r responds to normal restitution e=1 and capped
tangential impulse. Circular body orientation is observable via a painted
material marker. No gravity, drag, deformability or scale calibration.
"""
from __future__ import annotations
from math import cos,sin,radians,hypot,atan2,degrees,isfinite
SCHEMA="world-ab-oblique-rotational-contact/v1"
R=.25
M=1.
I=.5*M*R*R
SOURCE=(12.,1.5)
START=(3.,1.35)
VELOCITY=(3.,.12)
SPAN=1.
RESTITUTION=1.
HORIZON=3.3
LOOK_STEP=.1
PROJECTION=.25
FOOTPRINT=(24.,6.)
ANGLE_VALUES=(0,20)
FRICTION_VALUES=(0.,.4)
EPS=1e-9

def f(v):
    return round(float(v),10)

def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]

def add(a,b):
    return (a[0]+b[0],a[1]+b[1])

def mul(k,a):
    return (k*a[0],k*a[1])

def sub(a,b):
    return (a[0]-b[0],a[1]-b[1])

def norm(a):
    q=hypot(*a)
    if not q>EPS:raise ValueError("receiver cannot be constructed from zero motion")
    return (a[0]/q,a[1]/q)

def scalar_energy(v,w):
    return .5*M*dot(v,v)+.5*I*w*w

def impact(v,omega,n,mu):
    if abs(hypot(*n)-1)>1e-10:raise ValueError("contact normal not unit")
    t=(-n[1],n[0])
    incoming_n=dot(v,n)
    if not incoming_n < -EPS:raise ValueError("no incoming motion at surface")
    jn=-(1+RESTITUTION)*incoming_n*M
    slip=dot(v,t)-omega*R
    raw=-slip/(1/M+R*R/I)
    jt=max(-mu*jn,min(mu*jn,raw))
    out=add(v,add(mul(jn/M,n),mul(jt/M,t)))
    spin=omega-R*jt/I
    before=scalar_energy(v,omega)
    after=scalar_energy(out,spin)
    if after>before+1e-9:raise ValueError("rigid-body contact created energy")
    return out,spin,{
       "incoming_velocity":[f(z) for z in v],
       "outgoing_velocity":[f(z) for z in out],
       "incoming_spin":f(omega),"outgoing_spin":f(spin),
       "normal":[f(z) for z in n],
       "normal_impulse":f(jn),"tangential_impulse":f(jt),
       "tangential_slip_before":f(slip),
       "kinetic_energy_before":f(before),"kinetic_energy_after":f(after)}

def single(*,angle=0,friction=0.):
    if type(angle) is not int or angle not in ANGLE_VALUES:
        raise ValueError("angle belongs to the declared independent variable grid")
    if type(friction) not in (int,float) or friction not in FRICTION_VALUES:
        raise ValueError("friction belongs to declared independent variable grid")
    a=radians(angle)
    n=(-cos(a),-sin(a))
    tangent=(-n[1],n[0])
    incoming=VELOCITY
    vn=dot(incoming,n)
    signed=dot(sub(START,SOURCE),n)
    t1=(R-signed)/vn
    if not (0<t1<HORIZON):
        raise ValueError("original experimental face inaccessible")
    p1=add(START,mul(t1,incoming))
    offset=dot(sub(p1,SOURCE),tangent)
    if abs(offset)>SPAN/2+R:
        raise ValueError("disc passed outside experimental source segment")
    after1,w1,e1=impact(incoming,0.,n,float(friction))
    # The generated receiver's face normal is exactly opposite the
    # measured *outgoing translational* velocity, without blueprint labels.
    n2=mul(-1.,norm(after1))
    p2_target=add(p1,mul(PROJECTION,after1))
    anchor= sub(p2_target,mul(R,n2))
    denominator=dot(after1,n2)
    t2_rel=(R-dot(sub(p1,anchor),n2))/denominator
    t2=t1+t2_rel
    if not (abs(t2_rel-PROJECTION)<1e-9 and t2<HORIZON):
        raise ValueError("second generated receiver would not be reached")
    p2=add(p1,mul(t2_rel,after1))
    if any(not(R<=p[0]<=FOOTPRINT[0]-R and R<=p[1]<=FOOTPRINT[1]-R)
           for p in (p1,p2)):
        raise ValueError("collision exited virtual WORLD bounds")
    after2,w2,e2=impact(after1,w1,n2,float(friction))
    if not scalar_energy(after2,w2)<=scalar_energy(incoming,0.)+1e-8:
        raise ValueError("unphysical energy growth across source and receiver")
    first={"id":"original-source-face-experimental",
        "at":f(t1),"center":[f(x) for x in p1],
        "face_normal":[f(z) for z in n],
        "source_tangent_coordinate":f(offset),**e1}
    second={"id":"derived-receiver-face",
        "at":f(t2),"center":[f(x) for x in p2],
        "face_normal":[f(z) for z in n2],**e2}
    receiver={"id":"contact-derived-face-1",
        "anchor":[f(v) for v in anchor],
        "normal":[f(v) for v in n2],
        "normal_angle_degrees":f(degrees(atan2(n2[1],n2[0]))),
        "span":SPAN,
        "activated_at":f(t1),
        "observed_source_event":"original-source-face-experimental",
        "constructed_from":"observed-outgoing-center-velocity",
        "projection_duration":PROJECTION}
    frames=[]
    for i in range(34):
        t=min(HORIZON,i*LOOK_STEP)
        if t<t1:
            pos=add(START,mul(t,incoming));v=incoming;omega=0.;theta=0.;phase="before-source-contact"
        elif t<t2:
            pos=add(p1,mul(t-t1,after1));v=after1;omega=w1
            theta=w1*(t-t1);phase="between-collisions"
        else:
            pos=add(p2,mul(t-t2,after2));v=after2;omega=w2
            theta=w1*(t2-t1)+w2*(t-t2);phase="after-receiver-contact"
        if not(R-1e-8<=pos[0]<=FOOTPRINT[0]-R+1e-8 and R-1e-8<=pos[1]<=FOOTPRINT[1]-R+1e-8):
            raise ValueError("temporal path does not fit bounded physical WORLD")
        frames.append({"t":f(t),"position":[f(z) for z in pos],
            "velocity":[f(z) for z in v],"angular_velocity":f(omega),
            "orientation":f(theta),"phase":phase})
    return {"source_angle_degrees":angle,"friction":float(friction),
        "source_face":{"anchor":list(SOURCE),"normal":[f(z) for z in n],
            "span":SPAN,"source_world_wall_unchanged":True,
            "mode":"isolated angled perturbation; original wall is separately retained"},
        "constructed_receiver":receiver,"events":[first,second],
        "frames":frames,"last":frames[-1],
        "generated_surface_count":1,
        "nonzero_spin_generated":any(abs(e["outgoing_spin"])>1e-7 for e in (first,second)),
        "receiver_nonvertical":abs(n2[1])>1e-5,
        "shape_topology":"two straight line segments, not curved guide/funnel/diverter/spiral"}

def run():
    cases=[single(angle=angle,friction=mu)
            for angle in ANGLE_VALUES for mu in FRICTION_VALUES]
    if len(cases)!=4:raise ValueError("factorial experiment grid not filled")
    return {"schema":SCHEMA,"model":"2D unit-mass disc/I=0.5*m*r^2/normal restitution 1/capped Coulomb friction",
        "units":"original WORLD virtual movement cells, unitless normalized mass",
        "geometry":[24,6],"disc_radius":R,"disc_mass":M,"moment_of_inertia":I,
        "initial_position":list(START),"initial_velocity":list(VELOCITY),
        "source_anchor":list(SOURCE),"projection_duration":PROJECTION,
        "horizon":HORIZON,"branches":cases,
        "original_W13_world_rewritten":False,
        "original_Trial03_collision_source_rewritten":False,
        "original_sketch_shape_labels_given_to_generator":False,
        "full_original_physical_blueprint_generated":False,
        "real_Earth_material_behavior_verified":False}
