"""Independent WORLD33 source-plane interval witness.

Reconstruct square corners in the world frame instead of using the WORLD33
projection function, independently check every declared covered subinterval,
and reject any interval after the first unsupported prefix. No fifth contact
or material behavior is inferred.
"""
from __future__ import annotations

from copy import deepcopy
from math import sin,cos,pi,hypot
import unittest

from systems.workspace.world_ab_local_plane_prefix import (
    attempt,run,SCHEMA,HORIZON,MAX_NEW_WINDOW,BASE_INTERVALS,
    REFINEMENT_DEPTH,GUARD
)
from systems.workspace.world_ab_geometry_at_first_envelope_limit import attempt as prior32
from network.tests.test_world_ab_geometry_at_first_envelope_limit import (
    verify as verify32,original_planes
)
from systems.workspace.world_ab_first_finite_response_qualification import attempt as prior29
from systems.workspace.world_ab_third_contact import attempt as prior21,ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
EPS=5e-8


def points(h,t):
    theta=h["theta"]+h["spin"]*t
    center=(h["center"][0]+h["velocity"][0]*t,
            h["center"][1]+h["velocity"][1]*t)
    return [(center[0]+x*cos(theta)-y*sin(theta),
             center[1]+x*sin(theta)+y*cos(theta)) for x,y in CCW]


def original_bounds(h,planes,a,b):
    first,last=points(h,a),points(h,b)
    output=[]
    for name,n,anchor,span in planes:
        g1=min((p[0]-anchor[0])*n[0]+(p[1]-anchor[1])*n[1] for p in first)
        g2=min((p[0]-anchor[0])*n[0]+(p[1]-anchor[1])*n[1] for p in last)
        speed=abs(h["velocity"][0]*n[0]+h["velocity"][1]*n[1])+abs(h["spin"])*hypot(HALF,HALF)
        surplus=g1+g2-speed*(b-a)-2*GUARD
        output.append((name,span is not None,g1,g2,speed,surplus,
                       g1>GUARD and g2>GUARD and surplus>0))
    return output


def check_interval(record,h,planes,a,b,should_pass):
    if (abs(record.get("start",-1)-a)>EPS or abs(record.get("end",-1)-b)>EPS
        or record.get("original_constraints_checked")!=6
        or record.get("floating_point_not_formal_certificate") is not True):
        raise ValueError("original source interval/time altered")
    expected=original_bounds(h,planes,a,b)
    rows=record.get("source_plane_bounds")
    if type(rows) is not list or len(rows)!=6:
        raise ValueError("all six original source planes required")
    for got,(name,finite,g1,g2,speed,surplus,passed) in zip(rows,expected):
        for key,val in (("source_plane",name),
                        ("original_plane_is_finite_segment",finite),
                        ("interval_supported",passed)):
            if got.get(key)!=val:raise ValueError("source plane or sufficiency classification changed")
        for key,val in (("start_min_signed_gap",g1),("end_min_signed_gap",g2),
                        ("fixed_axis_speed_upper_bound",speed),
                        ("endpoint_neighborhood_surplus",surplus)):
            if not isinstance(got.get(key),(float,int)) or abs(got[key]-val)>EPS:
                raise ValueError("independent rotating-corner geometry disagrees: "+key)
    passed=all(row[-1] for row in expected)
    if record.get("nominally_clear_through_interval") is not passed or passed is not should_pass:
        raise ValueError("original nominal clearance decision was promoted")
    if passed:
        midpoint=points(h,(a+b)/2)
        if any(min((p[0]-anchor[0])*n[0]+(p[1]-anchor[1])*n[1]
                   for p in midpoint)<-EPS for _,n,anchor,_ in planes):
            raise ValueError("midpoint falsifies supposedly clear original plane")
    return passed


def verify(row):
    angle=row.get("angle")
    old=prior32(angle)
    before=prior29(angle)
    ancestor=prior21(angle)
    if row.get("schema")!=SCHEMA or angle not in ANGLES or not verify32(old):
        raise ValueError("source WORLD32 parent lacks independent witness")
    immutable={
        "source_trial32_schema":old["schema"],
        "source_trial32_status":old["status"],
        "source_first_limit_time":old["source_first_nominal_limit"],
        "original_first_limit_geometry":old,
        "source_qualified_fourth_response":before["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_two_static_finite_segments":True,
        "world_perimeter_plane_count":4,
        "declared_original_horizon":HORIZON,
        "maximum_new_window":MAX_NEW_WINDOW,
        "base_intervals":BASE_INTERVALS,
        "max_subdivision_depth":REFINEMENT_DEPTH,
        "positive_clearance_guard":GUARD,
        "conditional_ballistic_pose_only":True,
        "numerical_non_outward_rounded":True,
        "fifth_contact_witnessed":False,
        "fifth_impulse_computed":False,
        "physical_motion_authenticated":False,
        "post_unknown_continuation_permitted":False,
        "new_receiver_created":False,
    }
    if any(row.get(k)!=v for k,v in immutable.items()):
        raise ValueError("source ancestry, original finite world or physics claim changed")
    empty=("source_recomputed_plane_names","certified_subintervals")
    if before["conditional_fourth_response"] is None or old["status"]!="CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT":
        label=("NO_QUALIFIED_FOURTH_RESPONSE" if before["conditional_fourth_response"] is None
               else "FIRST_LIMIT_GEOMETRY_NOT_CONFIRMED_SEPARATED")
        if (row.get("status")!=label or any(row.get(k)!=[] for k in empty)
            or row.get("attempted_end_time") is not None
            or row.get("supported_prefix_end_time") is not None
            or row.get("first_unknown_subinterval") is not None
            or row.get("new_window_fully_nominally_supported") is not False):
            raise ValueError("unsupported original fourth response gained movement")
        return True
    t0=old["source_first_nominal_limit"]
    t1=min(HORIZON,t0+MAX_NEW_WINDOW)
    h={"center":before["qualifying_source_feature"]["contact_center"],
       "theta":before["qualifying_source_feature"]["contact_angle"],
       "velocity":before["conditional_fourth_response"]["outgoing_velocity"],
       "spin":before["conditional_fourth_response"]["outgoing_spin"]}
    planes=original_planes(ancestor,angle)
    if row.get("source_recomputed_plane_names")!=[x[0] for x in planes] or abs(
        row.get("attempted_end_time",-1)-t1)>EPS:
        raise ValueError("source original planes or declared bound changed")
    certified=row.get("certified_subintervals")
    if type(certified) is not list:raise ValueError("missing source covered prefix")
    cursor=[0]
    def rewalk(a,b,depth):
        enough=all(x[-1] for x in original_bounds(h,planes,a,b))
        if enough:
            if cursor[0]>=len(certified):raise ValueError("source omitted verified prefix")
            check_interval(certified[cursor[0]],h,planes,a,b,True)
            cursor[0]+=1
            return None
        if depth==REFINEMENT_DEPTH:return a,b
        mid=(a+b)/2
        left=rewalk(a,mid,depth+1)
        return left if left is not None else rewalk(mid,b,depth+1)
    unknown=None
    for i in range(BASE_INTERVALS):
        a=t0+(t1-t0)*i/BASE_INTERVALS
        b=t0+(t1-t0)*(i+1)/BASE_INTERVALS
        unknown=rewalk(a,b,0)
        if unknown is not None:break
    if cursor[0]!=len(certified):raise ValueError("source accepted motion after the first unknown")
    full=unknown is None
    endpoint=certified[-1]["end"] if certified else round(t0,12)
    if (row.get("new_window_fully_nominally_supported") is not full or
        abs(row.get("supported_prefix_end_time",-1)-endpoint)>EPS):
        raise ValueError("supported source movement prefix changed")
    if full:
        if row.get("first_unknown_subinterval") is not None:raise ValueError("invented unknown")
    else:
        unknown_record=row.get("first_unknown_subinterval")
        if (not isinstance(unknown_record,dict)
            or unknown_record.get("status")!="FIRST_UNRESOLVED_LOCAL_SUBINTERVAL"
            or unknown_record.get("failure_not_a_collision") is not True):
            raise ValueError("first unknown source interval lost")
        check_interval(unknown_record,h,planes,*unknown,False)
        if certified and abs(certified[-1]["end"]-unknown[0])>EPS:
            raise ValueError("source skipped unverified time")
    if row.get("status")!=("FULL_NEW_WINDOW_NOMINALLY_SEPARATED" if full else
                            "FIRST_LOCAL_HALFPLANE_BOUND_UNRESOLVED"):
        raise ValueError("source physical extrapolation asserted")
    return True


class World33Tests(unittest.TestCase):
    def test_rotation_can_hide_mid_interval_contact_between_clear_ends(self):
        h={"center":[.31,0.],"theta":0.,"velocity":[0.,0.],"spin":pi/.02}
        plane=[("synthetic",(1.,0.),(0.,0.),None)]
        b=original_bounds(h,plane,0.,.01)[0]
        self.assertGreater(b[2],0)
        self.assertGreater(b[3],0)
        self.assertLess(min(x[0] for x in points(h,.005)),0)
        self.assertFalse(b[-1])

    def test_every_source_case_independently_replayed(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["original_first_limit_cases"],3)
        self.assertEqual(report["without_original_response"],5)
        self.assertEqual(report["full_new_window_supported_cases"]+
                         report["locally_unresolved_cases"],3)
        self.assertEqual(report["fifth_impulses_selected"],0)
        for row in report["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_original_absent_response_cannot_move(self):
        for angle in (0.,20.):
            self.assertEqual(attempt(angle)["certified_subintervals"],[])

    def test_tampered_limits_and_real_fifth_impulses_fail_closed(self):
        row=attempt(5.)
        for k,v in (("fifth_contact_witnessed",True),("fifth_impulse_computed",True),
                    ("physical_motion_authenticated",True),
                    ("post_unknown_continuation_permitted",True),
                    ("declared_original_horizon",1.)):
            fake=deepcopy(row);fake[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):verify(fake)
        if row["certified_subintervals"]:
            fake=deepcopy(row);fake["certified_subintervals"].pop(0)
            with self.assertRaises(ValueError):verify(fake)


if __name__=="__main__":
    unittest.main()
