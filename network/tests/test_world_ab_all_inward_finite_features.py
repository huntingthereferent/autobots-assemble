"""Independent WORLD23 finite-face root witness (numerical, not formal).

Rebuild the original WORLD21 third impulse, independently check Trial22, then
find *every* inward crossing by a numerical scan of signed normal velocity,
root-bisect derivative transitions, and root-bisect monotonic gap segments.
The source generator instead uses analytic trigonometric stationary formulas.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin
import unittest

from systems.workspace.world_ab_all_inward_finite_features import (
    attempt, run, inward_roots, ANGLES, DURATION, SCHEMA
)
from systems.workspace.world_ab_first_post_third_candidate import (
    attempt as source22, ROOT_TOL
)
from systems.workspace.world_ab_third_contact import attempt as source21
from network.tests.test_world_ab_first_post_third_candidate import independent_check as check22
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER

VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
WORLD=(24.,6.)
ACCURACY=2e-5


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def pose(h,corner,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    x,y=corner
    return (h["contact_center"][0]+h["outgoing_velocity"][0]*t+
            x*cos(theta)-y*sin(theta),
            h["contact_center"][1]+h["outgoing_velocity"][1]*t+
            x*sin(theta)+y*cos(theta))


def rate(h,corner,normal,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    x,y=corner
    rx=x*cos(theta)-y*sin(theta)
    ry=x*sin(theta)+y*cos(theta)
    w=h["outgoing_spin"]
    return dot((h["outgoing_velocity"][0]-w*ry,
                h["outgoing_velocity"][1]+w*rx),normal)


def all_surface_defs(previous,angle):
    original=source18(angle)["source_first_contact"]
    return [
        ("original_finite_face",tuple(original["normal"]),tuple(WALL_CENTER),1.),
        ("motion_derived_receiver",tuple(previous["source_receiver"]["normal"]),
         tuple(previous["source_receiver"]["anchor"]),1.),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(WORLD[0],0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,WORLD[1]),None),
    ]


def independently_bisected_roots(h,corner,normal,anchor):
    def gap(t):
        p=pose(h,corner,t)
        return dot((p[0]-anchor[0],p[1]-anchor[1]),normal)
    def derivative(t):
        return rate(h,corner,normal,t)
    # Independent dense derivative scan, not WORLD23's analytic stationary.
    steps=2048
    limits=[0.,DURATION]
    before=0.
    prior=derivative(0.)
    for i in range(1,steps+1):
        after=DURATION*i/steps
        current=derivative(after)
        if prior*current<0:
            lo,hi=before,after
            sign=prior
            for _ in range(47):
                middle=(lo+hi)/2
                if derivative(middle)*sign>0:
                    lo=middle
                else:
                    hi=middle
            limits.append((lo+hi)/2)
        prior=current
        before=after
    limits.sort()
    roots=[]
    for a,b in zip(limits,limits[1:]):
        if gap(a)<=1e-9 or gap(b)>=-1e-9:
            continue
        lo,hi=a,b
        for _ in range(53):
            mid=(lo+hi)/2
            if gap(mid)>0:
                lo=mid
            else:
                hi=mid
        t=(lo+hi)/2
        if t>1e-9 and derivative(t)<-1e-7:
            roots.append(t)
    return roots


def verify(record):
    if record.get("schema")!=SCHEMA or record.get("angle") not in ANGLES:
        raise ValueError("source identity altered")
    angle=record["angle"]
    old22=source22(angle)
    check22(old22)
    old21=source21(angle)
    required={
        "source_trial22_schema":old22["schema"],
        "source_trial22_status":old22["status"],
        "source_trial22_first_crossing":old22["first_crossing"],
        "source_trial22_all_first_per_line":old22["all_source_line_crossings"],
        "source_third_impulse":old21["third_impulse"],
        "source_receiver":old21["source_receiver"],
        "projection_horizon":DURATION,
        "nominal_ballistic_assumption_only":True,
        "continuous_measured_motion":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "collision_after_candidate_solved":False,
        "formally_certified_root_isolation":False,
    }
    if any(record.get(key)!=value for key,value in required.items()):
        raise ValueError("original conditional source or claim changed")
    if old21["third_impulse"] is None:
        if (record["status"]!="NO_ADMITTED_THIRD_IMPULSE" or
            any(record.get(k) for k in (
                "all_inward_roots","eligible_geometry_roots",
                "coearliest_eligible","outside_finite_face_roots",
                "endpoint_uncertainties","near_tangent_uncertainties")) or
            record.get("first_eligible_geometry") is not None or
            record.get("monotonic_segments_checked")!=0):
            raise ValueError("absent impulse received later movement")
        return True
    h=old21["third_impulse"]
    expected=[]
    for name,normal,anchor,span in all_surface_defs(old21,angle):
        for index,corner in enumerate(VERTICES):
            ts=independently_bisected_roots(h,corner,normal,anchor)
            for t in ts:
                p=pose(h,corner,t)
                tangent=(-normal[1],normal[0])
                u=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
                if span is None:
                    kind="WORLD_PERIMETER_CANDIDATE"
                    coord=None
                elif abs(u)>span/2+ROOT_TOL:
                    kind="SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED"
                    coord=u
                elif abs(u)>=span/2-ROOT_TOL:
                    kind="ENDPOINT_FEATURE_UNRESOLVED"
                    coord=u
                else:
                    kind="FINITE_FACE_INTERIOR_CANDIDATE"
                    coord=u
                expected.append((t,name,index,p,coord,rate(h,corner,normal,t),kind))
    expected.sort(key=lambda x:(x[0],x[1],x[2]))
    original=record.get("all_inward_roots")
    if type(original) is not list or len(original)!=len(expected):
        raise ValueError("all-root source missed or fabricated inward crossings")
    for reported,e in zip(original,expected):
        t,name,index,p,coord,v,kind=e
        if (reported.get("surface")!=name
            or reported.get("vertex_index")!=index
            or abs(reported.get("dt_after_third_impulse",-99)-t)>ACCURACY
            or abs(reported.get("absolute_virtual_time",-99)-
                   (h["contact_absolute_virtual_time"]+t))>ACCURACY
            or any(abs(a-b)>ACCURACY for a,b in zip(
                reported["vertex_position"],p))
            or reported.get("feature_classification")!=kind
            or abs(reported.get("incoming_normal_vertex_rate",99)-v)>ACCURACY
            or abs(reported.get("signed_line_gap_residual",99))>ACCURACY
            or reported.get("physical_contact_measured") is not False
            or reported.get("conditional_source_geometry_only") is not True
            or ((reported.get("source_face_tangent_coordinate") is None)
                !=(coord is None))
            or (coord is not None and
                abs(reported["source_face_tangent_coordinate"]-coord)>ACCURACY)):
            raise ValueError("independent geometric event witness differs")
    accepted=[x for x in original if x["feature_classification"] in (
        "FINITE_FACE_INTERIOR_CANDIDATE","WORLD_PERIMETER_CANDIDATE")]
    rejected=[x for x in original if x["feature_classification"] ==
              "SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED"]
    endpoints=[x for x in original if x["feature_classification"] ==
               "ENDPOINT_FEATURE_UNRESOLVED"]
    if (record.get("eligible_geometry_roots")!=accepted or
        record.get("outside_finite_face_roots")!=rejected or
        record.get("endpoint_uncertainties")!=endpoints):
        raise ValueError("finite-face membership changed")
    first=accepted[0] if accepted else None
    tied=[x for x in accepted if
          abs(x["dt_after_third_impulse"]-first["dt_after_third_impulse"])<=1e-7
          ] if first else []
    if record.get("first_eligible_geometry")!=first or record.get("coearliest_eligible")!=tied:
        raise ValueError("earliest finite candidate / alternatives changed")
    label=("NO_ELIGIBLE_INWARD_ROOT_IN_WINDOW_UNDER_ASSUMPTIONS" if first is None else
           "COEARLIEST_GEOMETRIC_FEATURES_UNRESOLVED" if len(tied)>1 else
           "FIRST_FINITE_OR_BOUNDARY_GEOMETRY_CANDIDATE")
    if record.get("status")!=label:
        raise ValueError("unsupported next contact status")
    for item in record.get("near_tangent_uncertainties",[]):
        name=item["surface"]
        vertex=item["vertex_index"]
        if name not in [a[0] for a in all_surface_defs(old21,angle)] or vertex not in range(4):
            raise ValueError("unknown near-tangent feature")
        n,anchor=next((n,a) for label,n,a,span in
                      all_surface_defs(old21,angle) if label==name)
        t=item["time"]
        if not (0<t<DURATION):
            raise ValueError("near tangent outside window")
        p=pose(h,VERTICES[vertex],t)
        dist=dot((p[0]-anchor[0],p[1]-anchor[1]),n)
        if abs(dist)>1e-6 or abs(rate(h,VERTICES[vertex],n,t))>1e-4:
            raise ValueError("falsified near-zero stationary feature")
    if record.get("monotonic_segments_checked",0)<24:
        raise ValueError("source did not examine all 24 corner/line pairs")
    return True


class OriginalWorld23Tests(unittest.TestCase):
    def test_multi_crossing_counterexample_discriminates_from_first_only(self):
        q=(0.,0.,.1,0.,40.)
        roots,near,intervals=inward_roots(q)
        self.assertEqual(len(roots),2)
        self.assertAlmostEqual(roots[0],3.141592653589793/80,places=6)
        self.assertAlmostEqual(roots[1],5*3.141592653589793/80,places=6)
        self.assertGreater(intervals,2)

    def test_all_eight_original_source_cases_checked_independently(self):
        native=run()
        self.assertEqual(native["schema"],SCHEMA)
        self.assertEqual(native["angles"],list(ANGLES))
        self.assertEqual(native["conditional_third_impulse_inputs"],6)
        self.assertEqual(native["without_third_impulse"],2)
        self.assertEqual(native["total_inward_root_candidates"],
                         native["trial22_first_per_pair_candidates"] +
                         native["additional_inward_roots_beyond_trial22_first"])
        self.assertGreaterEqual(native["additional_inward_roots_beyond_trial22_first"],0)
        self.assertLessEqual(native["cases_with_new_later_root"],6)
        self.assertEqual(native["first_eligible_cases"]+
                         native["root_free_eligible_windows"],6)
        for key in ("physical_measurements","fourth_impulses_selected",
                    "physical_receivers_built"):
            self.assertEqual(native[key],0)
        for case in native["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_no_third_impulse_does_not_make_first_candidate(self):
        for angle in (0.,20.):
            case=attempt(angle)
            self.assertEqual(case["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertEqual(case["all_inward_roots"],[])
            self.assertIsNone(case["first_eligible_geometry"])

    def test_forged_later_impact_or_truncated_roots_rejected(self):
        test=attempt(7.5)
        for key,value in (
            ("fourth_impulse_selected",True),
            ("new_receiver_constructed",True),
            ("projection_horizon",1.),
            ("continuous_measured_motion",True),
        ):
            forged=deepcopy(test)
            forged[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(forged)
        if test["all_inward_roots"]:
            forged=deepcopy(test)
            forged["all_inward_roots"].pop()
            with self.assertRaises(ValueError):verify(forged)
        forged=deepcopy(test)
        forged["source_trial22_status"]="HARDWARE_HIT"
        with self.assertRaises(ValueError):verify(forged)


if __name__=="__main__":
    unittest.main()
