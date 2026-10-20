"""Independent WORLD22 first post-third candidate geometry witness.

Numerically find stationary times using derivative sign sweeps and bisection,
not the generator's trigonometric closed-form stationary partition. Independently
replay original WORLD21 third-impulse source and validate source geometry/limits.
Only nominal-model candidate crossings are witnessed; no fourth impulse.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin
import unittest

from systems.workspace.world_ab_first_post_third_candidate import (
    attempt, run, ANGLES, SCHEMA, DURATION, ROOT_TOL, WORLD
)
from systems.workspace.world_ab_third_contact import attempt as previous
from network.tests.test_world_ab_third_contact import independent_check as verify21
from systems.workspace.world_ab_local_recontact_impulse import attempt as before
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER

VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
EPS=2e-5


def dot(x,y):
    return x[0]*y[0]+x[1]*y[1]


def transform(h,corner,t):
    angle=h["contact_orientation"]+h["outgoing_spin"]*t
    c,s=cos(angle),sin(angle)
    x,y=corner
    return (h["contact_center"][0]+h["outgoing_velocity"][0]*t+c*x-s*y,
            h["contact_center"][1]+h["outgoing_velocity"][1]*t+s*x+c*y)


def current_rate(h,corner,n,t):
    angle=h["contact_orientation"]+h["outgoing_spin"]*t
    c,s=cos(angle),sin(angle)
    x,y=corner
    r=(c*x-s*y,s*x+c*y)
    w=h["outgoing_spin"]
    return dot((h["outgoing_velocity"][0]-w*r[1],
                h["outgoing_velocity"][1]+w*r[0]),n)


def independent_surfaces(source,angle):
    n=source["source_receiver"]["normal"]
    original=before(angle)["source_first_contact"]["normal"]
    return [
        ("original_finite_face",tuple(original),tuple(WALL_CENTER),1.),
        ("motion_derived_receiver",tuple(n),tuple(source["source_receiver"]["anchor"]),1.),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(WORLD[0],0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,WORLD[1]),None),
    ]


def numerical_first_inward(h,corner,n,anchor):
    """Independent dense derivative partition, then monotonic gap bisection."""
    def gap(t):
        pt=transform(h,corner,t)
        return dot((pt[0]-anchor[0],pt[1]-anchor[1]),n)
    def dg(t):
        return current_rate(h,corner,n,t)
    partitions=[0.,DURATION]
    last=0.
    ylast=dg(0.)
    for step in range(1,1025):
        now=DURATION*step/1024
        y=dg(now)
        if ylast*y<0:
            lo,hi=last,now
            initial_sign=ylast
            for _ in range(46):
                mid=(lo+hi)/2
                if dg(mid)*initial_sign>0:
                    lo=mid
                else:
                    hi=mid
            partitions.append((lo+hi)/2)
        last,ylast=now,y
    partitions.sort()
    for a,b in zip(partitions,partitions[1:]):
        if gap(a)<=1e-9 or gap(b)>=-1e-9:
            continue
        lo,hi=a,b
        for _ in range(53):
            mid=(lo+hi)/2
            if gap(mid)>0:lo=mid
            else:hi=mid
        candidate=(lo+hi)/2
        if candidate>1e-9 and dg(candidate)<-1e-7:
            return candidate
    return None


def independent_check(record):
    if record["schema"]!=SCHEMA or record["angle"] not in ANGLES:
        raise ValueError("trial source identity or angle")
    old=previous(record["angle"])
    verify21(old)
    declarations={
        "source_trial21_schema":old["schema"],
        "source_trial21_status":old["status"],
        "source_third_impulse":old["third_impulse"],
        "source_receiver":old["source_receiver"],
        "projection_horizon":DURATION,
        "source_trial21_local_window":old["local_window"],
        "source_original_world":[24.,6.],
        "unselected_conditional_model_only":True,
        "model_motion_not_material_measurement":True,
        "fourth_impulse_solved":False,
        "new_receiver_constructed":False,
        "continuous_real_world_motion_verified":False,
        "formally_outward_rounded_certificate":False,
        "later_forces_and_impacts_assumed_absent":True,
    }
    if any(record.get(k)!=v for k,v in declarations.items()):
        raise ValueError("prior source or virtual model scope changed")
    if old["third_impulse"] is None:
        if (record["status"]!="NO_ADMITTED_THIRD_IMPULSE" or
            record["first_crossing"] is not None or
            record["coearliest_crossings"] or
            record["all_source_line_crossings"] or
            record["monotonic_intervals_checked"]!=0):
            raise ValueError("no source impulse produced invented event")
        return True
    if old["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        if record["status"]!="SOURCE_LOCAL_GEOMETRY_UNRESOLVED":
            raise ValueError("unresolved source became solved")
        return True
    h=old["third_impulse"]
    allfound=[]
    for name,n,anchor,span in independent_surfaces(old,record["angle"]):
        for i,vertex in enumerate(VERTICES):
            t=numerical_first_inward(h,vertex,n,anchor)
            if t is not None:
                p=transform(h,vertex,t)
                tangent=(-n[1],n[0])
                along=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
                if span is None:
                    feature="WORLD_PERIMETER_CANDIDATE"
                    tc=None
                elif abs(along)>span/2+ROOT_TOL:
                    feature="SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED"
                    tc=along
                elif abs(along)>=span/2-ROOT_TOL:
                    feature="ENDPOINT_FEATURE_UNRESOLVED"
                    tc=along
                else:
                    feature="FINITE_FACE_INTERIOR_CANDIDATE"
                    tc=along
                allfound.append((t,name,i,p,tc,current_rate(h,vertex,n,t),feature))
    expected=sorted(allfound,key=lambda v:(v[0],v[1],v[2]))
    reported=record["all_source_line_crossings"]
    if len(reported)!=len(expected):
        raise ValueError("missing/extra modeled line-crossing record")
    for entry,w in zip(reported,expected):
        t,name,i,point,along,rate,feature=w
        if (entry["surface"]!=name or entry["vertex_index"]!=i
            or abs(entry["dt_after_third_impulse"]-t)>EPS
            or abs(entry["absolute_virtual_time"]-
                   (h["contact_absolute_virtual_time"]+t))>EPS
            or any(abs(a-b)>EPS for a,b in zip(entry["vertex_position"],point))
            or entry["feature_classification"]!=feature
            or entry["physical_contact_measured"] is not False
            or abs(entry["incoming_normal_vertex_rate"]-rate)>EPS
            or abs(entry["signed_line_gap_residual"])>EPS
            or ((entry["source_face_tangent_coordinate"] is None)!=(along is None))
            or (along is not None and
                abs(entry["source_face_tangent_coordinate"]-along)>EPS)):
            raise ValueError("independent first-crossing witness disagreed")
    if not expected:
        if (record["status"]!="NO_INWARD_SOURCE_LINE_CROSSING_IN_BOUNDED_PROJECTION"
            or record["first_crossing"] is not None or
            record["coearliest_crossings"]):
            raise ValueError("fabricated or omitted empty result")
    else:
        first=expected[0]
        same=[w for w in expected if abs(w[0]-first[0])<=1e-7]
        if record["first_crossing"] != reported[0]:
            raise ValueError("first source event changed")
        if len(record["coearliest_crossings"]) != len(same):
            raise ValueError("simultaneous source alternatives lost")
        if record["coearliest_crossings"] != reported[:len(same)]:
            raise ValueError("candidate chronology changed")
        status=("MULTIPLE_FIRST_FEATURES_UNRESOLVED" if len(same)>1 else
                "FIRST_MODEL_CONTACT_GEOMETRY_CANDIDATE" if
                first[6] in ("WORLD_PERIMETER_CANDIDATE",
                             "FINITE_FACE_INTERIOR_CANDIDATE")
                else first[6])
        if record["status"] != status:
            raise ValueError("outside-face or ambiguous event promoted")
    if record["monotonic_intervals_checked"]<=0:
        raise ValueError("monotonic source investigation missing")
    return True


class World22Tests(unittest.TestCase):
    def test_all_original_conditional_controls_independently_replayed(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["angles"],list(ANGLES))
        self.assertEqual(report["conditional_third_impulse_inputs"],6)
        self.assertEqual(report["no_third_impulse_controls"],2)
        self.assertEqual(report["physical_contact_measurements"],0)
        self.assertEqual(report["selected_fourth_impulses"],0)
        self.assertEqual(report["real_receivers_constructed"],0)
        self.assertFalse(report["new_world_or_engine"])
        self.assertEqual(report["source_line_crossing_cases"]+
                         report["source_line_no_crossing_cases"],6)
        for case in report["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(independent_check(case))

    def test_no_source_third_impulse_cannot_gain_future_contact(self):
        for angle in (0.,20.):
            a=attempt(angle)
            self.assertIsNone(a["first_crossing"])
            self.assertEqual(a["status"],"NO_ADMITTED_THIRD_IMPULSE")

    def test_false_hardware_fourth_impulse_or_unbounded_claim_refused(self):
        base=attempt(10.)
        for key,value in (("new_receiver_constructed",True),
                          ("fourth_impulse_solved",True),
                          ("model_motion_not_material_measurement",False),
                          ("projection_horizon",2.0),
                          ("formally_outward_rounded_certificate",True)):
            altered=deepcopy(base)
            altered[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                independent_check(altered)

    def test_candidate_time_feature_and_lineage_tampering_refused(self):
        a=attempt(12.25)
        if a["all_source_line_crossings"]:
            for key,value in (
                ("dt_after_third_impulse",.24),
                ("absolute_virtual_time",0.),
                ("incoming_normal_vertex_rate",100.),
                ("feature_classification","REAL_HARDWARE_CONTACT"),
                ("vertex_index",9),
            ):
                altered=deepcopy(a)
                altered["all_source_line_crossings"][0][key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):
                    independent_check(altered)
        a=attempt(7.5)
        a["source_third_impulse"]["outgoing_spin"]+=1.
        with self.assertRaises(ValueError):independent_check(a)


if __name__=="__main__":
    unittest.main()
