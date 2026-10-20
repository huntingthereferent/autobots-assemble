"""Independent numerical witness for Trial14 source-conditioned world morph.

Do not call the generator's impact or geometry helpers in the oracle.
All source positions, orientations and impulses are independently recomputed.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, hypot, radians, sin
import unittest

from systems.workspace.world_ab_relation_morph import trial, run, SCHEMA
from systems.workspace.world_ab_oblique_rotation import (
    single as old_single, R, I, START, VELOCITY, PROJECTION
)

TOL = 4e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def near(a,b,eps=TOL):
    if isinstance(a,(tuple,list)):
        return len(a)==len(b) and all(abs(x-y)<eps for x,y in zip(a,b))
    return abs(a-b)<eps


def independent_contact(v,spin,n,mu):
    tang=(-n[1],n[0])
    normal_impulse=-2*dot(v,n)
    if not normal_impulse>0:raise ValueError("nonincoming")
    tangent_impulse=max(-mu*normal_impulse,
                        min(mu*normal_impulse,
                            -(dot(v,tang)-R*spin)/(1+R*R/I)))
    output=(v[0]+normal_impulse*n[0]+tangent_impulse*tang[0],
            v[1]+normal_impulse*n[1]+tangent_impulse*tang[1])
    out_spin=spin-R*tangent_impulse/I
    return output,out_spin,normal_impulse,tangent_impulse


def distance(point,endpoints):
    a,b=endpoints
    ab=(b[0]-a[0],b[1]-a[1])
    f=max(0.,min(1.,dot((point[0]-a[0],point[1]-a[1]),ab)/dot(ab,ab)))
    return hypot(point[0]-a[0]-f*ab[0],point[1]-a[1]-f*ab[1])


def audit(case):
    if case["schema"]!=SCHEMA or case["status"]!="TWO_CONTACTS_IN_DECLARED_MODEL":
        raise ValueError("not completed finite WORLD Trial14")
    if case["measured_physical_material"] is not False or case["target_shape_supplied"] is not False:
        raise ValueError("unmeasured behavior promoted")
    if case["source_model_04B_unchanged"] is not True or case["world48_and_nih_unmodified"] is not True:
        raise ValueError("source lineage switched")
    angle=case["input_source_angle_degrees"]
    mu=case["friction"]
    anchor=case["input_source_anchor"]
    n=(-cos(radians(angle)),-sin(radians(angle)))
    source=case["source"]
    if not near(source["normal"],n):
        raise ValueError("source normal fabricated")
    tangent=(-n[1],n[0])
    for point,sign in zip(source["endpoints"],(-.5,.5)):
        if not near(point,(anchor[0]+sign*tangent[0],anchor[1]+sign*tangent[1])):
            raise ValueError("source finite segment fabricated")
    v=tuple(VELOCITY)
    origin=tuple(START)
    t1=(R-dot((origin[0]-anchor[0],origin[1]-anchor[1]),n))/dot(v,n)
    p1=(origin[0]+t1*v[0],origin[1]+t1*v[1])
    v1,w1,jn1,jt1=independent_contact(v,0.,n,mu)
    n2=(-v1[0]/hypot(*v1),-v1[1]/hypot(*v1))
    p2=(p1[0]+PROJECTION*v1[0],p1[1]+PROJECTION*v1[1])
    anchor2=(p2[0]-R*n2[0],p2[1]-R*n2[1])
    segment=case["receiver"]
    if segment["constructed_from"]!="first-outgoing-velocity" or segment["source_contact_index"]!=0:
        raise ValueError("invented construction ancestry")
    if not near(segment["normal"],n2) or not near(segment["anchor"],anchor2):
        raise ValueError("receiver orientation or position not source-derived")
    tangent2=(-n2[1],n2[0])
    for point,sign in zip(segment["endpoints"],(-.5,.5)):
        if not near(point,(anchor2[0]+sign*tangent2[0],
                           anchor2[1]+sign*tangent2[1])):
            raise ValueError("receiver extent invented")
    v2,w2,jn2,jt2=independent_contact(v1,w1,n2,mu)
    e1,e2=case["contacts"]
    for event,t,p,vin,vout,spin,jn,jt in (
        (e1,t1,p1,v,v1,w1,jn1,jt1),
        (e2,t1+PROJECTION,p2,v1,v2,w2,jn2,jt2)):
        if not near(event["time"],t) or not near(event["center"],p):
            raise ValueError("incorrect contact time/position")
        if not near(event["incoming_velocity"],vin) or not near(event["outgoing_velocity"],vout):
            raise ValueError("false contact velocities")
        if not near(event["outgoing_spin"],spin):
            raise ValueError("false contact rotation")
        if not near(event["impulse"]["normal_impulse"],jn) or not near(event["impulse"]["tangential_impulse"],jt):
            raise ValueError("false impulse")
    if not near(segment["activated_at"],t1):
        raise ValueError("receiver existed before causal source contact")
    if not near(distance(p1,source["endpoints"]),R) or not near(distance(p2,segment["endpoints"]),R):
        raise ValueError("not real finite segment contact")
    if len(case["frames"])<5:
        raise ValueError("missing finite motion record")
    for frame in case["frames"]:
        t=frame["time"]
        if t<t1-1e-9:
            expected=(origin[0]+t*v[0],origin[1]+t*v[1])
            velocity=v;spin=0.
        elif t<t1+PROJECTION-1e-9:
            expected=(p1[0]+(t-t1)*v1[0],p1[1]+(t-t1)*v1[1])
            velocity=v1;spin=w1
        else:
            expected=(p2[0]+(t-t1-PROJECTION)*v2[0],
                      p2[1]+(t-t1-PROJECTION)*v2[1])
            velocity=v2;spin=w2
        if not near(frame["position"],expected) or not near(frame["velocity"],velocity) or not near(frame["spin"],spin):
            raise ValueError("false source-derived finite motion frame")
        if distance(expected,source["endpoints"]) < R-TOL:
            raise ValueError("source geometry penetrated")
        if t>=t1 and distance(expected,segment["endpoints"]) < R-TOL:
            raise ValueError("receiver geometry penetrated")
        if not (R-TOL<=expected[0]<=24-R+TOL and R-TOL<=expected[1]<=6-R+TOL):
            raise ValueError("frame escaped WORLD perimeter")
    return True


class WorldRelationMorphTests(unittest.TestCase):
    def test_all_eight_cases_replay_against_independent_physics(self):
        out=run()
        self.assertEqual(out["schema"],SCHEMA)
        self.assertEqual(len(out["cases"]),8)
        self.assertTrue(out["new_receiver_shape_is_source_derived"])
        self.assertFalse(out["real_earth_physics_verified"])
        self.assertFalse(out["physical_motor_or_nih_blueprint_tested"])
        for case in out["cases"]:
            with self.subTest(angle=case["input_source_angle_degrees"],
                              mu=case["friction"]):
                self.assertEqual(case["status"],"TWO_CONTACTS_IN_DECLARED_MODEL")
                self.assertTrue(audit(case))

    def test_original_04b_two_contacts_preserved_under_same_inputs(self):
        for angle in (0,20):
            for mu in (0.,.4):
                with self.subTest(angle=angle,friction=mu):
                    old=old_single(angle=angle,friction=mu)
                    new=trial(angle=angle,friction=mu)
                    for a,b in zip(old["events"],new["contacts"]):
                        self.assertTrue(near(a["at"],b["time"]))
                        self.assertTrue(near(a["center"],b["center"]))
                        self.assertTrue(near(a["outgoing_velocity"],b["outgoing_velocity"]))
                        self.assertTrue(near(a["outgoing_spin"],b["outgoing_spin"]))
                    self.assertTrue(near(old["constructed_receiver"]["normal"],
                                         new["receiver"]["normal"]))
                    self.assertTrue(near(old["constructed_receiver"]["anchor"],
                                         new["receiver"]["anchor"]))

    def test_fractional_angles_morph_generated_orientation(self):
        first=trial(angle=7.5)
        second=trial(angle=12.25)
        self.assertNotEqual(first["receiver"]["normal"],second["receiver"]["normal"])
        self.assertNotEqual(first["contacts"][0]["time"],second["contacts"][0]["time"])
        self.assertTrue(audit(first))
        self.assertTrue(audit(second))

    def test_other_source_anchor_moves_the_reconstructed_contact(self):
        original=trial(angle=12.25)
        shifted=trial(angle=12.25,anchor=(10.,1.5))
        self.assertEqual(shifted["status"],"TWO_CONTACTS_IN_DECLARED_MODEL")
        self.assertNotEqual(shifted["receiver"]["anchor"],original["receiver"]["anchor"])
        self.assertTrue(audit(shifted))

    def test_finite_segment_miss_constructs_nothing(self):
        missed=trial(angle=0.,anchor=(12.,4.))
        self.assertEqual(missed["status"],"NO_FINITE_SEGMENT_CONTACT")
        self.assertIsNone(missed["receiver"])
        self.assertEqual(missed["contacts"],[])
        self.assertEqual(missed["frames"],[])

    def test_invalid_unbounded_or_nonfinite_inputs_refused(self):
        for kwargs in (
            {"angle":41}, {"angle":float("nan")}, {"angle":True},
            {"friction":-0.1}, {"friction":float("inf")}, {"friction":True},
            {"anchor":(12,float("nan"))}, {"anchor":(40,1.5)},
        ):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                trial(**kwargs)

    def test_modified_receiver_position_or_angle_rejected(self):
        for name in ("anchor","normal","endpoints"):
            damaged=deepcopy(trial(angle=12.25))
            if name=="endpoints":
                damaged["receiver"][name][0][0]+=.07
            else:
                damaged["receiver"][name][0]+=.07
            with self.subTest(field=name),self.assertRaises(ValueError):
                audit(damaged)

    def test_modified_history_and_pretend_hardware_result_rejected(self):
        original=trial(angle=7.5)
        for field in ("outgoing_velocity","center"):
            damaged=deepcopy(original)
            damaged["contacts"][1][field][0]+=.25
            with self.subTest(field=field),self.assertRaises(ValueError):
                audit(damaged)
        claimed=deepcopy(original)
        claimed["measured_physical_material"]=True
        with self.assertRaises(ValueError):
            audit(claimed)
        future=deepcopy(original)
        future["receiver"]["activated_at"]=0.
        with self.assertRaises(ValueError):
            audit(future)


if __name__=="__main__":
    unittest.main()
