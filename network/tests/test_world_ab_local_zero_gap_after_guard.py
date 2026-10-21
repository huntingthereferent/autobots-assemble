"""WORLD39 independent finite-feature probe witness for the original WORLD.

Reconstruct selected source corner from CCW vertices (not generator order),
recover every original source plane, solve the first zero-gap from a separate
sampled bracket with high precision and check every competing original
corner/plane lower bound. This verifies a *numerical mathematical candidate*
only, not a material sixth impulse or an authorized sixth trajectory.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from math import cos,sin,hypot,isfinite
import unittest

from systems.workspace.world_ab_local_zero_gap_after_guard import (
    attempt,run,SCHEMA,PROBE_WIDTH,GUARD,ROOT_TOL,OTHER_GAP_GUARD,
    INWARD_GUARD,HORIZON
)
from systems.workspace.world_ab_first_post_fifth_guard_limit import attempt as source38
from systems.workspace.world_ab_post_fifth_contiguous_prefix import model_at_conditional_fifth
from systems.workspace.world_ab_whole_contact_configuration import attempt as source35
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
SOURCE_ORDER=(0,3,1,2)
NUMERICAL_TOL=2e-9


def dot(a,b):return a[0]*b[0]+a[1]*b[1]

def corner(model,index,t):
    x,y=CCW[SOURCE_ORDER[index]]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    r=(x*c-y*s,x*s+y*c)
    p=(model["center"][0]+model["velocity"][0]*t+r[0],
       model["center"][1]+model["velocity"][1]*t+r[1])
    rate=(model["velocity"][0]-model["spin"]*r[1],
          model["velocity"][1]+model["spin"]*r[0])
    return p,rate


@lru_cache(maxsize=8)
def ancestry(angle):
    before=source38(angle)
    fifth=source35(angle)
    world=source21(angle)
    return before,fifth,world


def check(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("WORLD39 original source identity unavailable")
    old,fifth,world=ancestry(angle)
    baseline={
        "source_trial38_schema":old["schema"],
        "source_trial38_status":old["status"],
        "source_original_guard_feature":old["first_source_guard_limit"],
        "source_original_24_by_6_world":[24.,6.],
        "source_original_finite_faces":2,
        "source_original_perimeter_planes":4,
        "maximum_local_probe_width":PROBE_WIDTH,
        "source_guard_threshold":GUARD,
        "other_original_gap_guard":OTHER_GAP_GUARD,
        "source_model_counterfactual_only":True,
        "source_clearance_proven_only_to_guard":True,
        "new_interval_not_admitted_continuation":True,
        "real_sixth_contact_observed":False,
        "physical_sixth_impulse_selected":False,
        "hypothetical_sixth_impulse_calculated":False,
        "post_sixth_model_motion_solved":False,
        "new_receiver_constructed":False,
        "formal_interval_arithmetic_proof":False
    }
    if any(row.get(k)!=v for k,v in baseline.items()):
        raise ValueError("first original guard or real-event boundary tampered")
    if fifth["conditional_fifth_response"] is None:
        if (row.get("status")!="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE"
            or row.get("source_24_plane_corner_probe_records")!=[]
            or row.get("bracketed_first_zero_time") is not None
            or row.get("source_contact_geometry_qualified") is not False):
            raise ValueError("inactive original source invented sixth contact")
        return True
    first=old["first_source_guard_limit"]
    if first is None:
        if row.get("status")!="NO_ADMITTED_FIRST_SOURCE_GUARD_BOUNDARY":
            raise ValueError("missing source first guard falsely advanced")
        return True
    if (old["status"]!="FIRST_ORIGINAL_CLEARANCE_GUARD_BOUNDARY"
        or len(old["coearliest_source_guard_features"])!=1
        or first["source_plane_is_finite"] is not True
        or first["finite_face_intersecting_span_at_limit"] is not True
        or first["normal_rate_at_limit"]>=-INWARD_GUARD):
        if row.get("status")!="GUARD_SOURCE_FEATURE_UNRESOLVED":
            raise ValueError("unqualified source feature promoted to contact")
        return True
    h=model_at_conditional_fifth(fifth,world)
    planes=original_planes(world,angle)
    t0=first["guard_limit_time"]
    index=first["source_corner_index"]
    name=first["source_plane"]
    choice=next((x for x in planes if x[0]==name and x[3] is not None),None)
    if choice is None or len(planes)!=6 or not (0.058<t0<HORIZON):
        raise ValueError("original contact face replaced")
    _,n,anchor,span=choice
    g=lambda t: dot((corner(h,index,t)[0][0]-anchor[0],
                     corner(h,index,t)[0][1]-anchor[1]),n)
    endpoint=min(HORIZON,t0+PROBE_WIDTH)
    p0,v0=corner(h,index,t0)
    curvature=h["spin"]**2*hypot(HALF,HALF)
    upper=dot(v0,n)+curvature*(endpoint-t0)
    if not (abs(g(t0)-GUARD)<ROOT_TOL and g(t0)>0
            and upper < -INWARD_GUARD and g(endpoint)<0):
        if row.get("status")!="LOCAL_ZERO_GAP_NOT_BRACKETED_OR_INWARD":
            raise ValueError("unbracketed original first mathematical zero")
        return True
    low,high=t0,endpoint
    for _ in range(70):
        mid=(low+high)/2
        if g(mid)>0:low=mid
        else:high=mid
    zero=(low+high)/2
    p,velocity=corner(h,index,zero)
    tangent=(-n[1],n[0])
    along=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
    inside=abs(along)<span/2-1e-6
    for key,value in (
        ("selected_source_face",name),("selected_corner",index),
        ("tangent_inside_finite_face",inside)):
        if row.get(key)!=value:
            raise ValueError("original source finite feature replaced: "+key)
    for key,value in (
        ("guard_time",t0),("local_probe_endpoint",endpoint),
        ("bracketed_first_zero_time",zero),
        ("source_normal_rate_at_zero",dot(velocity,n)),
        ("selected_inward_rate_upper_bound",upper)):
        if not isinstance(row.get(key),(int,float)) or abs(row[key]-value)>NUMERICAL_TOL:
            raise ValueError("independent candidate timing or rate mismatch: "+key)
    if not isinstance(row.get("first_zero_contact_model_position"),list) or len(
            row["first_zero_contact_model_position"])!=2 or any(
            abs(a-b)>NUMERICAL_TOL for a,b in zip(
                row["first_zero_contact_model_position"],p)):
        raise ValueError("world-coordinate source feature location changed")
    original=row.get("source_24_plane_corner_probe_records")
    if type(original) is not list or len(original)!=24:
        raise ValueError("must retain all original 24 plane-corner records")
    good=0
    selected=0
    for plane_index,(plane,normal,anchor_point,span_) in enumerate(planes):
        speed=abs(dot(h["velocity"],normal))+abs(h["spin"])*hypot(HALF,HALF)
        for source_index in range(4):
            rec=original[plane_index*4+source_index]
            a=corner(h,source_index,t0)[0]
            b=corner(h,source_index,zero)[0]
            g0=dot((a[0]-anchor_point[0],a[1]-anchor_point[1]),normal)
            gz=dot((b[0]-anchor_point[0],b[1]-anchor_point[1]),normal)
            floor=g0-speed*(zero-t0)
            target=plane==name and source_index==index
            selected+=int(target)
            accepted=None if target else floor>OTHER_GAP_GUARD
            good+=int(accepted is True)
            fields={
                "source_plane":plane,"source_corner_index":source_index,
                "source_plane_finite":span_ is not None,
                "selected_guard_feature":target,
                "other_original_relation_separated_through_probe":accepted,
            }
            if any(rec.get(k)!=value for k,value in fields.items()):
                raise ValueError("source competing plane identity or clearance falsified")
            for key,value in (
                ("source_guard_start_gap",g0),
                ("source_zero_time_gap",gz),
                ("original_normal_speed_upper_bound",speed),
                ("conservative_other_gap_lower_bound",floor)):
                if not isinstance(rec.get(key),(int,float)) or not isfinite(
                        rec[key]) or abs(rec[key]-value)>NUMERICAL_TOL:
                    raise ValueError("independent original source gap differs: "+key)
    if selected!=1:raise ValueError("source first original feature not unique")
    qualified=inside and good==23 and abs(g(zero))<=ROOT_TOL
    if (row.get("all_23_other_original_constraints_strictly_separated") is not (good==23)
        or row.get("source_contact_geometry_qualified") is not qualified):
        raise ValueError("original competing source clearance inflated")
    expected=("LOCAL_ORIGINAL_ZERO_GAP_NUMERICAL_FEATURE_QUALIFIED" if qualified
              else "LOCAL_FIRST_SOURCE_ZERO_GAP_GEOMETRY_UNRESOLVED")
    if row.get("status")!=expected:
        raise ValueError("mathematical sixth contact promoted beyond its evidence")
    return True


class WORLD39Tests(unittest.TestCase):
    def test_original_numerical_zero_probe_replays_by_independent_world_coordinates(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["inactive_source_controls"],7)
        self.assertEqual(data["measured_sixth_contacts"],0)
        self.assertEqual(data["selected_sixth_impulses"],0)
        self.assertEqual(data["qualified_numerical_zero_gap_features"]+
                         data["unresolved_local_zero_gap_features"],1)
        for row in data["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(check(row))

    def test_guard_is_not_zero_gap_or_material_impact(self):
        original=attempt(10.)
        self.assertNotEqual(original["guard_time"],original["bracketed_first_zero_time"])
        self.assertLess(original["bracketed_first_zero_time"]-
                        original["guard_time"],PROBE_WIDTH)
        self.assertFalse(original["real_sixth_contact_observed"])
        self.assertFalse(original["hypothetical_sixth_impulse_calculated"])

    def test_false_material_claims_and_competing_gap_tampering_fail(self):
        example=attempt(10.)
        for key,value in (
            ("real_sixth_contact_observed",True),
            ("physical_sixth_impulse_selected",True),
            ("hypothetical_sixth_impulse_calculated",True),
            ("post_sixth_model_motion_solved",True),
            ("new_receiver_constructed",True),
            ("formal_interval_arithmetic_proof",True),
            ("source_original_24_by_6_world",[6.,24.])):
            trial=deepcopy(example)
            trial[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                check(trial)
        forged=deepcopy(example)
        forged["source_24_plane_corner_probe_records"][1]["source_zero_time_gap"]+=.02
        with self.assertRaises(ValueError):
            check(forged)


if __name__=="__main__":
    unittest.main()
