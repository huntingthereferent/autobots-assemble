"""WORLD42 independent source world-coordinate post-sixth guard-limit witness.

Different construction: CCW square index map and sine-phase stationary
equation, not generator's cosine-phase roots. Reconstruct source sixth model,
all six original planes and 24 signed normal gaps and each earliest guard.
A guard exhaustion is a sufficient-boundary event, not a seventh contact.
"""
from __future__ import annotations

from copy import deepcopy
from math import asin,atan2,ceil,cos,sin,hypot,isfinite,pi
import unittest

from systems.workspace.world_ab_first_post_sixth_guard_limit import (
    attempt,run,SCHEMA,START,END,GUARD,TIME_TIE,first_guard
)
from systems.workspace.world_ab_post_sixth_local_clearance import attempt as prior41
from network.tests.test_world_ab_post_sixth_local_clearance import verify as verify41
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as prior40
from systems.workspace.world_ab_local_zero_gap_after_guard import attempt as prior39
from systems.workspace.world_ab_whole_contact_configuration import attempt as prior35
from systems.workspace.world_ab_post_fifth_contiguous_prefix import model_at_conditional_fifth
from systems.workspace.world_ab_third_contact import attempt as prior21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
ORIGINAL_ORDER=(0,3,1,2)
TOL=2e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def source_state(h,index,t):
    x,y=CCW[ORIGINAL_ORDER[index]]
    angle=h["theta"]+h["spin"]*t
    c,s=cos(angle),sin(angle)
    r=(x*c-y*s,x*s+y*c)
    p=(h["center"][0]+h["velocity"][0]*t+r[0],
       h["center"][1]+h["velocity"][1]*t+r[1])
    v=(h["velocity"][0]-h["spin"]*r[1],
       h["velocity"][1]+h["spin"]*r[0])
    return p,v


def source_gap(h,index,n,anchor,t):
    p,_=source_state(h,index,t)
    return dot((p[0]-anchor[0],p[1]-anchor[1]),n)


def stationary_sine_phase(h,index,n):
    x,y=CCW[ORIGINAL_ORDER[index]]
    c,s=cos(h["theta"]),sin(h["theta"])
    px=x*c-y*s
    py=x*s+y*c
    a=dot((px,py),n)
    b=dot((-py,px),n)
    rate=dot(h["velocity"],n)
    spin=h["spin"]
    r=hypot(a,b)
    critical=[START,END]
    if abs(spin)>1e-12 and r>1e-12:
        z=rate/(spin*r)
        if abs(z)<=1.:
            phi=atan2(b,a)
            alpha=asin(max(-1.,min(1.,z)))
            limit=ceil(abs(spin)*END/(2*pi))+8
            for k in range(-limit,limit+1):
                for choice in (alpha,pi-alpha):
                    time=(phi+choice+2*pi*k)/spin
                    if START+1e-13<time<END-1e-13:
                        critical.append(time)
    return sorted(set(critical))


def independent_first(h,index,n,anchor):
    marks=stationary_sine_phase(h,index,n)
    g=lambda t:source_gap(h,index,n,anchor,t)
    if g(START)<=GUARD:
        raise ValueError("WORLD41 claimed positive end but original corner gap absent")
    root=None
    for a,b in zip(marks,marks[1:]):
        if g(a)<=GUARD:
            root=a;break
        if g(b)>GUARD:continue
        lo,hi=a,b
        for _ in range(72):
            m=(lo+hi)/2
            if g(m)>GUARD:lo=m
            else:hi=m
        root=(lo+hi)/2
        break
    return root,len(marks)-2,min(g(t) for t in marks)


def original_sixth_world(angle):
    sixth=prior40(angle)
    fifth=prior35(angle)
    t=prior39(angle)["bracketed_first_zero_time"]
    old=model_at_conditional_fifth(fifth,prior21(angle))
    return {
        "center":[old["center"][i]+old["velocity"][i]*t for i in (0,1)],
        "theta":old["theta"]+old["spin"]*t,
        "velocity":list(sixth["conditional_sixth_response"]["outgoing_velocity"]),
        "spin":sixth["conditional_sixth_response"]["outgoing_spin"],
    }


def verify(row):
    angle=row.get("angle")
    if angle not in ANGLES or row.get("schema")!=SCHEMA:
        raise ValueError("original WORLD42 schema/angle changed")
    earlier=prior41(angle)
    if not verify41(earlier):
        raise ValueError("original WORLD41 independent source ancestry failed")
    sixth=prior40(angle)
    unchanged={
        "original_trial41_schema":earlier["schema"],
        "original_trial41_status":earlier["status"],
        "source_trial41_end":earlier["supported_contiguous_prefix_end"],
        "original_world":[24.,6.],
        "source_finite_faces":2,
        "source_perimeter_planes":4,
        "first_supported_post_sixth_window":START,
        "declared_max_post_sixth_horizon":END,
        "original_positive_guard":GUARD,
        "source_original_plane_corner_count":24,
        "counterfactual_sixth_response_only":True,
        "material_sixth_impact_observed":False,
        "material_seventh_contact_observed":False,
        "seventh_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_admitted":False,
        "exact_outward_rounded_interval_proof":False,
    }
    if any(row.get(k)!=v for k,v in unchanged.items()):
        raise ValueError("source world geometry or physical refusal altered")
    if (sixth["conditional_sixth_response"] is None
        or earlier["status"]!="CONDITIONAL_SIXTH_FIRST_WINDOW_NOMINALLY_SEPARATED"):
        expected=("NO_ADMITTED_SIXTH_SOURCE" if
                  sixth["conditional_sixth_response"] is None else
                  "FIRST_POST_SIXTH_SOURCE_WINDOW_UNRESOLVED")
        if (row.get("status")!=expected
            or row.get("original_24_guard_searches")!=[]
            or row.get("first_original_guard_limit") is not None
            or row.get("coearliest_original_features")!=[]
            or row.get("supported_horizon_endpoint") is not None
            or row.get("all_original_guards_clear_through_horizon") is not False):
            raise ValueError("unsupported source continuation falsely admitted")
        return True
    model=original_sixth_world(angle)
    planes=original_planes(prior21(angle),angle)
    rows=row.get("original_24_guard_searches")
    if type(rows) is not list or len(rows)!=24 or len(planes)!=6:
        raise ValueError("all 24 original source constraints required")
    found=[]
    for j,(name,n,anchor,span) in enumerate(planes):
        tangent=(-n[1],n[0])
        for i in range(4):
            got=rows[j*4+i]
            root,parts,minimum=independent_first(model,i,n,anchor)
            expected={
                "source_plane":name,
                "source_corner_index":i,
                "original_face_finite":span is not None,
                "analytic_stationary_partition_count":parts,
                "not_an_observed_material_contact":True,
            }
            if any(got.get(k)!=v for k,v in expected.items()):
                raise ValueError("original independent stationary-partition identity mismatch")
            for key,value in (
                ("start_signed_normal_gap",source_gap(model,i,n,anchor,START)),
                ("horizon_signed_normal_gap",source_gap(model,i,n,anchor,END)),
                ("analytic_interval_minimum_gap",minimum)):
                if not isinstance(got.get(key),(int,float)) or not isfinite(
                        got[key]) or abs(got[key]-value)>TOL:
                    raise ValueError("original analytic gap differs: "+key)
            feature=got.get("first_original_guard_feature")
            if root is None:
                if feature is not None:
                    raise ValueError("invented guard exhaustion on source corner")
                continue
            p,velocity=source_state(model,i,root)
            along=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
            if not isinstance(feature,dict):
                raise ValueError("source original guard root omitted")
            fixed={
                "source_plane":name,
                "source_corner_index":i,
                "original_face_finite":span is not None,
                "within_original_finite_span":(
                    abs(along)<=span/2+1e-8 if span is not None else None),
                "material_seventh_contact":False
            }
            if any(feature.get(k)!=v for k,v in fixed.items()):
                raise ValueError("original finite guard feature modified")
            numbers={
                "guard_limit_time":root,
                "signed_gap_at_guard_limit":source_gap(model,i,n,anchor,root),
                "incoming_normal_rate":dot(velocity,n),
                "finite_face_tangent_coordinate":along if span is not None else None,
            }
            for key,value in numbers.items():
                if value is None:
                    if feature.get(key) is not None:
                        raise ValueError("perimeter plane falsely finite")
                elif not isinstance(feature.get(key),(int,float)) or abs(
                        feature[key]-value)>TOL:
                    raise ValueError("independent original guard feature value changed: "+key)
            point=feature.get("model_corner_location")
            if (not isinstance(point,list) or len(point)!=2 or any(
                    abs(point[k]-p[k])>TOL for k in range(2))):
                raise ValueError("source corner point not original CCW geometry")
            found.append((root,feature))
    found.sort(key=lambda x:(x[0],x[1]["source_plane"],x[1]["source_corner_index"]))
    first=found[0][1] if found else None
    equally=[x[1] for x in found if abs(x[0]-found[0][0])<=TIME_TIE] if found else []
    if (row.get("first_original_guard_limit")!=first or
        row.get("coearliest_original_features")!=equally):
        raise ValueError("first original source guard chronology changed")
    good=first is None
    status=("POST_SIXTH_ORIGINAL_GUARDS_CLEAR_THROUGH_HORIZON" if good
            else "FIRST_POST_SIXTH_ORIGINAL_GUARD_LIMIT")
    if (row.get("status")!=status or
        row.get("all_original_guards_clear_through_horizon") is not good or
        not isinstance(row.get("supported_horizon_endpoint"),(int,float)) or
        abs(row["supported_horizon_endpoint"]-(
            END if good else first["guard_limit_time"]))>TOL):
        raise ValueError("source retained movement past its first source guard")
    return True


class WORLD42Tests(unittest.TestCase):
    def test_original_24_analytic_guard_searches_and_inactive_controls(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["inactive_source_controls"],7)
        self.assertEqual(report["eligible_post_sixth_models"]+
                         report["unresolved_previous_window_models"],1)
        self.assertEqual(report["eligible_post_sixth_models"],
                         report["first_guard_limit_models"]+
                         report["all_original_guard_full_horizon_models"])
        self.assertEqual(report["real_seventh_impacts"],0)
        for row in report["cases"]:
            with self.subTest(angle=row["angle"]):self.assertTrue(verify(row))

    def test_synthetic_positive_endpoints_can_hide_interior_guard_loss(self):
        # This abstract signed-gap series has two positive endpoints,
        # but its first below-guard point occurs inside the finite interval.
        w=2*pi/(END-START)
        radius=.002
        q=(GUARD+.001,0.,radius*cos(w*START),
           radius*sin(w*START),w)
        self.assertGreater(q[0]+q[2]*cos(w*START)+q[3]*sin(w*START),GUARD)
        self.assertGreater(q[0]+q[2]*cos(w*END)+q[3]*sin(w*END),GUARD)
        t,_,_=first_guard(q)
        self.assertIsNotNone(t)
        self.assertLess(t,END)

    def test_material_seventh_and_original_gap_tampering_rejected(self):
        row=attempt(10.)
        for field,fake_value in (
            ("material_sixth_impact_observed",True),
            ("material_seventh_contact_observed",True),
            ("seventh_impulse_computed",True),
            ("new_receiver_constructed",True),
            ("post_first_unknown_motion_admitted",True),
            ("exact_outward_rounded_interval_proof",True),
            ("original_world",[6.,24.])):
            forged=deepcopy(row)
            forged[field]=fake_value
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(forged)
        if row["original_24_guard_searches"]:
            forged=deepcopy(row)
            forged["original_24_guard_searches"][0]["start_signed_normal_gap"]+=.2
            with self.assertRaises(ValueError):
                verify(forged)

if __name__=="__main__":
    unittest.main()
