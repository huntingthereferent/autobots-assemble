"""Trial04 independent rigid-body geometry and impulse oracle.

The oracle re-solves exact plane intersections, impulse+torque and piecewise
trajectories without invoking the dynamics generator. It checks source
activation, energy, nonretroactivity, missing curved geometry and 2x2 contrasts.
"""
from __future__ import annotations
from copy import deepcopy
from math import cos,sin,pi,hypot,isclose,atan2,degrees
import json
from pathlib import Path
import unittest
from systems.workspace.world_ab_oblique_rotation import run,single,SCHEMA

TOL=4e-8
def near(a,b,location):
    if not isclose(a,b,rel_tol=0,abs_tol=TOL):
        raise ValueError(f"{location}: {a} != {b}")
def vector_eq(a,b,where):
    if len(a)!=len(b):raise ValueError(where+" length")
    for i,(u,v) in enumerate(zip(a,b)):near(u,v,where+f"[{i}]")
def div(a,b):return (a[0]-b[0],a[1]-b[1])
def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def scaled(c,a):return (c*a[0],c*a[1])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def independently_verify_case(c):
    radius=.25;mass=1.;inertia=.03125;P=(3.,1.35);v=(3.,.12)
    degree=c["source_angle_degrees"];friction=c["friction"]
    if degree not in (0,20) or friction not in (0.,.4):
        raise ValueError("comparison axes outside predeclared grid")
    ang=degree*pi/180
    n=(-cos(ang),-sin(ang))
    anchor=(12.,1.5)
    t1=(radius-dot(div(P,anchor),n))/dot(v,n)
    p1=plus(P,scaled(t1,v))
    e1,e2=c["events"]
    near(e1["at"],t1,"source time")
    vector_eq(e1["center"],p1,"source position")
    vector_eq(e1["normal"],n,"source normal")
    near(c["source_face"]["span"],1.,"source span")
    if c["source_face"]["mode"]!="isolated angled perturbation; original wall is separately retained":
        raise ValueError("original native wall claim changed")
    def bounce(in_v,in_w,normal,observed):
        t=(-normal[1],normal[0])
        vn=dot(in_v,normal)
        if vn>=0:raise ValueError("contact not incoming")
        normal_impulse=-2*vn
        before_slip=dot(in_v,t)-radius*in_w
        requested=-before_slip/(1+radius**2/inertia)
        tangent_impulse=min(friction*normal_impulse,max(-friction*normal_impulse,requested))
        outgoing=plus(in_v,plus(scaled(normal_impulse,normal),scaled(tangent_impulse,t)))
        spin=in_w-(radius/inertia)*tangent_impulse
        kinetic_before=.5*dot(in_v,in_v)+.5*inertia*in_w**2
        kinetic_after=.5*dot(outgoing,outgoing)+.5*inertia*spin**2
        if kinetic_after>kinetic_before+TOL:raise ValueError("energy increased")
        vector_eq(observed["incoming_velocity"],in_v,"incoming")
        vector_eq(observed["outgoing_velocity"],outgoing,"outgoing")
        near(observed["incoming_spin"],in_w,"input spin")
        near(observed["outgoing_spin"],spin,"output spin")
        vector_eq(observed["normal"],normal,"impulse normal")
        near(observed["normal_impulse"],normal_impulse,"normal impulse")
        near(observed["tangential_impulse"],tangent_impulse,"tangential impulse")
        near(observed["tangential_slip_before"],before_slip,"friction pre-contact slip")
        near(observed["kinetic_energy_before"],kinetic_before,"energy before")
        near(observed["kinetic_energy_after"],kinetic_after,"energy after")
        return outgoing,spin
    v1,w1=bounce(v,0.,n,e1)
    unit=hypot(*v1)
    if unit<=0:raise ValueError("no outgoing receiver")
    n2=(-v1[0]/unit,-v1[1]/unit)
    p2=plus(p1,scaled(.25,v1))
    next_anchor=div(p2,scaled(radius,n2))
    vector_eq(c["constructed_receiver"]["anchor"],next_anchor,"receiver assembled placement")
    vector_eq(c["constructed_receiver"]["normal"],n2,"new face normal")
    near(c["constructed_receiver"]["normal_angle_degrees"],degrees(atan2(n2[1],n2[0])),"orientation")
    if (c["constructed_receiver"]["constructed_from"]!="observed-outgoing-center-velocity" or
        c["constructed_receiver"]["observed_source_event"]!=e1["id"] or
        c["constructed_receiver"]["id"]!="contact-derived-face-1"):
        raise ValueError("receiver obtained from incorrect source")
    near(c["constructed_receiver"]["activated_at"],t1,"causal activation")
    t2=t1+(radius-dot(div(p1,next_anchor),n2))/dot(v1,n2)
    near(t2,t1+.25,"receiver contact lag")
    near(e2["at"],t2,"receiver event time")
    vector_eq(e2["center"],p2,"receiver impact position")
    vector_eq(e2["face_normal"],n2,"receiver normal")
    if not t1<t2<3.3:raise ValueError("receiver absent within observation horizon")
    v2,w2=bounce(v1,w1,n2,e2)
    if len(c["frames"])!=34:raise ValueError("missing observed physical frames")
    for i,frame in enumerate(c["frames"]):
        t=i*.1
        near(frame["t"],t,f"frame[{i}].t")
        if t<t1:
            loc=plus(P,scaled(t,v));now_v=v;omega=0.;theta=0.;phase="before-source-contact"
        elif t<t2:
            loc=plus(p1,scaled(t-t1,v1));now_v=v1;omega=w1;theta=w1*(t-t1);phase="between-collisions"
        else:
            loc=plus(p2,scaled(t-t2,v2));now_v=v2;omega=w2
            theta=w1*(t2-t1)+w2*(t-t2);phase="after-receiver-contact"
        vector_eq(frame["position"],loc,f"frame[{i}].position")
        vector_eq(frame["velocity"],now_v,f"frame[{i}].velocity")
        near(frame["angular_velocity"],omega,f"frame[{i}].angular velocity")
        near(frame["orientation"],theta,f"frame[{i}].orientation")
        if frame["phase"]!=phase:raise ValueError("future contact frame substituted")
    if c["last"]!=c["frames"][-1] or c["generated_surface_count"]!=1:
        raise ValueError("unsupported last frame or geometry count")
    if c["shape_topology"]!="two straight line segments, not curved guide/funnel/diverter/spiral":
        raise ValueError("original blueprint structure promoted without evidence")
    return {"first_time":t1,"second_time":t2,
        "angle_generated":degrees(atan2(n2[1],n2[0])),
        "spin_generated":abs(w1)>TOL or abs(w2)>TOL}

class ObliqueRotationTests(unittest.TestCase):
    def test_01_factorial_four_branches_analytical_replay(self):
        result=run()
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(len(result["branches"]),4)
        for case in result["branches"]:
            with self.subTest(deg=case["source_angle_degrees"],mu=case["friction"]):
                self.assertTrue(independently_verify_case(case))
                self.assertFalse(result["full_original_physical_blueprint_generated"])
    def test_02_tilt_and_friction_are_distinct_physical_controls(self):
        result=run()
        a,b,c,d=result["branches"]
        self.assertEqual([(r["source_angle_degrees"],r["friction"]) for r in (a,b,c,d)],
                         [(0,0.),(0,.4),(20,0.),(20,.4)])
        self.assertFalse(a["nonzero_spin_generated"])
        self.assertTrue(b["nonzero_spin_generated"])
        self.assertFalse(c["nonzero_spin_generated"])
        self.assertTrue(d["nonzero_spin_generated"])
        self.assertNotEqual(a["constructed_receiver"]["normal"],c["constructed_receiver"]["normal"])
        self.assertNotEqual(c["last"]["position"],d["last"]["position"])
        self.assertNotEqual(b["last"]["orientation"],d["last"]["orientation"])
    def test_03_energy_kinematic_and_torque_controls(self):
        result=run()
        for case in result["branches"]:
            for e in case["events"]:
                self.assertLessEqual(e["kinetic_energy_after"],e["kinetic_energy_before"]+1e-8)
                self.assertGreater(e["normal_impulse"],0)
        self.assertTrue(independently_verify_case(result["branches"][3])["spin_generated"])
    def test_04_unsupported_angles_and_friction_rejected(self):
        for kwargs in ({"angle":-20},{"angle":30},{"friction":-1},
                       {"friction":1},{"angle":True},{"friction":float("nan")}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                single(**kwargs)
    def test_05_analytic_mutants_rejected(self):
        r=run()["branches"][3]
        mutations=[
            lambda v:v["events"][0].update(outgoing_spin=0),
            lambda v:v["events"][0].update(normal_impulse=0),
            lambda v:v["events"][1].update(at=3.29),
            lambda v:v["events"][1].update(kinetic_energy_after=999),
            lambda v:v["constructed_receiver"].update(normal=[1.,0.]),
            lambda v:v["constructed_receiver"].update(activated_at=0),
            lambda v:v["frames"][20].update(orientation=1),
            lambda v:v["last"].update(position=[0,0]),
        ]
        for i,mutate in enumerate(mutations):
            v=deepcopy(r);mutate(v)
            with self.subTest(i=i),self.assertRaises(ValueError):
                independently_verify_case(v)
    def test_06_original_visual_blueprint_still_missing_complex_shapes(self):
        reference=json.loads((Path(__file__).parent/"fixtures/world_ab_original_visual_reference_v1.json").read_text())
        generated={"source-face","contact-derived-face-1"}
        self.assertEqual([x for x in reference["generated_geometries_required"] if x not in generated],
                         ["guide","funnel","diverter","spiral"])
        self.assertTrue(all(x["generated_surface_count"]==1 for x in run()["branches"]))
        self.assertTrue(all(x["shape_topology"].startswith("two straight") for x in run()["branches"]))
if __name__=="__main__":
    unittest.main()
