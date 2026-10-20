"""WORLD15: independently recompute geometry and reject invented body relations."""
from copy import deepcopy
from math import cos, sin, radians, hypot
import unittest

from systems.workspace.world_ab_body_support import run, trial, SCHEMA, BODIES
from systems.workspace.world_ab_relation_morph import trial as earlier_disc
from systems.workspace.world_ab_oblique_rotation import R, PROJECTION, START, VELOCITY


def d(a,b):
    return a[0]*b[0]+a[1]*b[1]


def diff(a,b):
    return (a[0]-b[0],a[1]-b[1])


def plus(a,b):
    return (a[0]+b[0],a[1]+b[1])


def mul(k,a):
    return (k*a[0],k*a[1])


def near(a,b,eps=4e-7):
    if isinstance(a,(tuple,list)):
        return isinstance(b,(tuple,list)) and len(a)==len(b) and all(
            abs(x-y)<eps for x,y in zip(a,b))
    return abs(a-b)<eps


def width(body,n):
    return R if body=="disc" else R*(abs(n[0])+abs(n[1]))


def corner(body,n):
    if body=="disc":return mul(-R,n)
    return tuple(-R if a>1e-8 else R if a< -1e-8 else 0 for a in n)


def independent_witness(record):
    if record["schema"]!=SCHEMA or record["status"]!="TWO_MODELED_CONTACTS":
        raise ValueError("not completed bounded source")
    if record["body"] not in BODIES or record["measured_earth_material"] is not False:
        raise ValueError("unobserved source claim")
    if record["selected_physical_outcome"] is not False or record["target_receiver_shape_provided"] is not False:
        raise ValueError("material outcome or target shape invented")
    body=record["body"]
    a=record["source_anchor"]
    v=tuple(VELOCITY)
    start=tuple(START)
    theta=radians(record["source_angle"])
    n=(-cos(theta),-sin(theta))
    if not near(record["source"]["normal"],n):
        raise ValueError("source normal changed")
    tangent=(-n[1],n[0])
    for pt,k in zip(record["source"]["endpoints"],(-.5,.5)):
        if not near(pt,plus(a,mul(k,tangent))):
            raise ValueError("source finite segment modified")
    time1=(width(body,n)-d(diff(start,a),n))/d(v,n)
    p1=plus(start,mul(time1,v))
    point=plus(p1,corner(body,n))
    if not abs(d(diff(point,a),tangent)) < .5:
        raise ValueError("source support point not on admitted segment interior")
    v1=diff(v,mul(2*d(v,n),n))
    n2=mul(-1/hypot(*v1),v1)
    p2=plus(p1,mul(PROJECTION,v1))
    a2=diff(p2,mul(width(body,n2),n2))
    receiver=record["receiver"]
    if not near(receiver["normal"],n2) or not near(receiver["anchor"],a2):
        raise ValueError("constructed receiver was not derived from movement")
    tangent2=(-n2[1],n2[0])
    for pt,k in zip(receiver["endpoints"],(-.5,.5)):
        if not near(pt,plus(a2,mul(k,tangent2))):
            raise ValueError("receiver finite endpoints changed")
    if not abs(d(diff(plus(p2,corner(body,n2)),a2),tangent2))<.5:
        raise ValueError("receiver support point outside admitted finite interior")
    if receiver["caused_by_contact_index"]!=0 or receiver["constructed_from"]!="recorded-model-outgoing-velocity":
        raise ValueError("fabricated construction ancestry")
    if not near(receiver["activated_at"],time1):
        raise ValueError("source-derived receiver backdated")
    v2=diff(v1,mul(2*d(v1,n2),n2))
    for event,time,center,before,after in (
            (record["contacts"][0],time1,p1,v,v1),
            (record["contacts"][1],time1+PROJECTION,p2,v1,v2)):
        if not (near(event["time"],time) and near(event["center"],center)
                and near(event["before"],before) and near(event["after"],after)):
            raise ValueError("changed contact or movement")
    if len(record["frames"])<12:raise ValueError("incomplete movement witness")
    for frame in record["frames"]:
        time=frame["time"]
        if time<time1-1e-9:
            p=plus(start,mul(time,v));vel=v
        elif time<time1+PROJECTION-1e-9:
            p=plus(p1,mul(time-time1,v1));vel=v1
        else:
            p=plus(p2,mul(time-time1-PROJECTION,v2));vel=v2
        if not near(frame["center"],p) or not near(frame["velocity"],vel):
            raise ValueError("invented trajectory")
        if d(diff(p,a),n)<width(body,n)-5e-7:
            raise ValueError("source separating-plane penetration")
        if time>=time1 and d(diff(p,a2),n2)<width(body,n2)-5e-7:
            raise ValueError("derived separating-plane penetration")
    if body=="fixed-square" and record["square_rotation_prevented_by_constraint"] is not True:
        raise ValueError("free square spin was not solved")
    if record["actual_hardware_contact_witnessed"] is not False or record["new_physical_law_inferred"] is not False:
        raise ValueError("model trajectory elevated to physical observation")
    return True


class BodySupportWorldTests(unittest.TestCase):
    def test_both_body_types_advance_without_changing_world(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(len(data["cases"]),8)
        self.assertEqual(data["body_types"],list(BODIES))
        self.assertTrue(data["no_new_world_or_renderer"])
        self.assertFalse(data["real_material_behavior_observed"])
        for case in data["cases"]:
            with self.subTest(body=case["body"],angle=case["source_angle"]):
                self.assertEqual(case["status"],"TWO_MODELED_CONTACTS")
                self.assertTrue(independent_witness(case))

    def test_disc_regression_matches_existing_trial14_frictionless(self):
        for angle in (0.,7.5,12.25,20.):
            with self.subTest(angle=angle):
                former=earlier_disc(angle=angle,friction=0.)
                current=trial("disc",angle=angle)
                self.assertEqual(former["status"],"TWO_CONTACTS_IN_DECLARED_MODEL")
                for old,new in zip(former["contacts"],current["contacts"]):
                    self.assertTrue(near(old["time"],new["time"]))
                    self.assertTrue(near(old["center"],new["center"]))
                    self.assertTrue(near(old["outgoing_velocity"],new["after"]))
                self.assertTrue(near(former["receiver"]["anchor"],current["receiver"]["anchor"]))
                self.assertTrue(near(former["receiver"]["normal"],current["receiver"]["normal"]))

    def test_square_contact_support_changes_actual_face_location(self):
        disc=trial("disc",angle=20.)
        square=trial("fixed-square",angle=20.)
        self.assertNotEqual(disc["contacts"][0]["time"],square["contacts"][0]["time"])
        self.assertNotEqual(disc["receiver"]["anchor"],square["receiver"]["anchor"])
        self.assertEqual(disc["source"]["endpoints"],square["source"]["endpoints"])
        self.assertTrue(independent_witness(square))

    def test_unsupported_endpoint_case_is_not_called_physical_miss(self):
        disc=trial("disc",angle=30.)
        square=trial("fixed-square",angle=30.)
        self.assertEqual(disc["status"],"TWO_MODELED_CONTACTS")
        self.assertEqual(square["status"],"NO_ADMITTED_INTERIOR_CONTACT")
        self.assertIsNone(square["receiver"])
        self.assertEqual(square["frames"],[])
        self.assertEqual(square["contacts"],[])

    def test_wrong_body_anchor_and_angle_are_refused(self):
        for name,options in (
            ("triangle",{}),
            ("disc",{"angle":float("nan")}),
            ("disc",{"angle":41}),
            ("fixed-square",{"anchor":(float("inf"),1.5)}),
            ("disc",{"anchor":(22,1.5)}),
        ):
            with self.subTest(body=name,options=options),self.assertRaises(ValueError):
                trial(name,**options)

    def test_change_to_source_receiver_or_event_fails(self):
        good=trial("fixed-square",angle=12.25)
        for key in ("source","receiver"):
            for part in ("anchor","normal","endpoints"):
                damaged=deepcopy(good)
                if part=="endpoints":damaged[key][part][0][0]+=.07
                else:damaged[key][part][0]+=.07
                with self.subTest(key=key,part=part),self.assertRaises(ValueError):
                    independent_witness(damaged)
        for key in ("time","center","after"):
            damaged=deepcopy(good)
            if key=="time":damaged["contacts"][1][key]+=.2
            else:damaged["contacts"][1][key][0]+=.2
            with self.subTest(contact=key),self.assertRaises(ValueError):
                independent_witness(damaged)

    def test_fake_hardware_measurement_and_premature_construction_refused(self):
        case=trial("disc",angle=7.5)
        for key,value in (("actual_hardware_contact_witnessed",True),
                          ("new_physical_law_inferred",True),
                          ("measured_earth_material",True)):
            bad=deepcopy(case);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                independent_witness(bad)
        bad=deepcopy(case);bad["receiver"]["activated_at"]=0.
        with self.assertRaises(ValueError):
            independent_witness(bad)


if __name__=="__main__":
    unittest.main()
