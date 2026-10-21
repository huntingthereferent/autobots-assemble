"""Independent WORLD30 short-time source clearance witness.

Reconstruct finite source and WORLD plane identities separately from the
generator, rederive rotated corners / normal velocities and Taylor error
bounds, test all 24 decisions per candidate, plus sampled falsification
checks. All conclusions remain conditional on the source's unrealized
frictionless elastic fourth-response hypothesis.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,hypot
import unittest

from systems.workspace.world_ab_post_fourth_local_clearance import (
    attempt,run,WINDOW,MARGIN,TOL,SCHEMA
)
from systems.workspace.world_ab_first_finite_response_qualification import (
    attempt as source29
)
from network.tests.test_world_ab_first_finite_response_qualification import verify as verify29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER

SQUARE=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
DELTA=4e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def planes_from_original_source(original,angle):
    old=source18(angle)
    n1=tuple(old["source_first_contact"]["normal"])
    receiver=original["source_receiver"]
    n2=tuple(receiver["normal"])
    return [
        ("original_finite_face",n1,tuple(WALL_CENTER)),
        ("motion_derived_receiver",n2,tuple(receiver["anchor"])),
        ("world_left",(1.,0.),(0.,0.)),
        ("world_right",(-1.,0.),(24.,0.)),
        ("world_bottom",(0.,1.),(0.,0.)),
        ("world_top",(0.,-1.),(0.,6.)),
    ]


def state(h,i,dt):
    theta=h["theta"]+dt*h["spin"]
    x,y=SQUARE[i]
    c,s=cos(theta),sin(theta)
    r=(x*c-y*s,x*s+y*c)
    cx=h["center"][0]+dt*h["velocity"][0]
    cy=h["center"][1]+dt*h["velocity"][1]
    return (cx+r[0],cy+r[1]),r


def independently_compute(h,index,n,anchor,touch):
    pt,r=state(h,index,0.)
    gap=dot((pt[0]-anchor[0],pt[1]-anchor[1]),n)
    vel=(h["velocity"][0]-h["spin"]*r[1],
         h["velocity"][1]+h["spin"]*r[0])
    rate=dot(vel,n)
    curvature=h["spin"]*h["spin"]*hypot(HALF,HALF)
    floor_at_end=gap+rate*WINDOW-.5*curvature*WINDOW*WINDOW
    minimum_rate=rate-curvature*WINDOW
    bound=minimum_rate if touch else min(gap,floor_at_end)
    accepted=(abs(gap)<=TOL and minimum_rate>MARGIN) if touch else (bound>MARGIN)
    reason=("TOUCHING_VERTEX_DEPARTURE_LOWER_RATE" if accepted else
            "TOUCHING_VERTEX_OUTGOING_SEPARATION_UNRESOLVED") if touch else (
            "OTHER_VERTEX_POSITIVE_GAP_BOUND" if accepted else
            "NONTOUCHING_CORNER_CLEARANCE_UNRESOLVED")
    return gap,rate,curvature,floor_at_end,minimum_rate,bound,accepted,reason


def verify(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("wrong source identity or angle")
    prior=source29(angle)
    native=source21(angle)
    if not verify29(prior):
        raise ValueError("earlier independent source response witness failed")
    required={
        "source_trial29_schema":prior["schema"],
        "source_trial29_status":prior["status"],
        "source_original_third_impulse":native["third_impulse"],
        "source_candidate_contact":prior["qualifying_source_feature"],
        "source_candidate_response":prior["conditional_fourth_response"],
        "original_world":[24.,6.],
        "original_finite_source_faces":2,
        "four_original_world_boundaries":4,
        "post_candidate_horizon":WINDOW,
        "nominal_free_flight_model_only":True,
        "actual_contact_selected":False,
        "real_material_response_witnessed":False,
        "post_candidate_continuous_motion_authenticated":False,
        "formally_outward_rounded_numeric_certificate":False,
        "new_receiver_built":False,
        "fifth_impulse_computed":False,
    }
    if any(row.get(k)!=value for k,value in required.items()):
        raise ValueError("original source/candidate/material boundary changed")
    if prior["conditional_fourth_response"] is None:
        if (row.get("status")!="NO_QUALIFIED_SOURCE_FOURTH_RESPONSE" or
            row.get("clearance_bounds")!=[] or
            row.get("accepted_bounds")!=0 or
            row.get("unresolved_bounds")!=0 or
            row.get("nominal_local_clearance_admitted") is not False):
            raise ValueError("unqualified source response acquired later movement")
        return True
    f=prior["qualifying_source_feature"]
    response=prior["conditional_fourth_response"]
    h={"center":f["contact_center"],"theta":f["contact_angle"],
       "velocity":response["outgoing_velocity"],"spin":response["outgoing_spin"]}
    face=f["source_face"]
    corner=f["source_vertex_index"]
    bounds=row.get("clearance_bounds")
    if type(bounds) is not list or len(bounds)!=24:
        raise ValueError("all 24 original normal constraints required")
    passed=0
    touched=0
    for (name,n,anchor),j in zip(planes_from_original_source(native,angle),
                                  range(6)):
        for i in range(4):
            rec=bounds[j*4+i]
            touch=(name==face and i==corner)
            gap,rate,curvature,end,ratefloor,bound,accepted,reason=(
                independently_compute(h,i,n,anchor,touch))
            numbers={
                "gap_at_candidate":gap,
                "outgoing_normal_rate":rate,
                "curvature_upper_bound":curvature,
                "end_gap_lower_bound":end,
                "normal_rate_lower_bound":ratefloor,
                "conservative_bound":bound,
            }
            if (rec.get("surface")!=name or rec.get("corner_index")!=i
                or rec.get("starts_at_qualified_contact") is not touch
                or rec.get("accepted") is not accepted
                or rec.get("classification")!=reason
                or rec.get("original_finite_source_not_real_hardware") is not True
                or any(abs(rec.get(k,float("inf"))-v)>DELTA for k,v in numbers.items())):
                raise ValueError("independent source corner bound or refusal disagreed")
            passed+=int(accepted)
            touched+=int(touch)
            if accepted:
                for tau in (WINDOW/4,WINDOW/2,WINDOW):
                    pt,_=state(h,i,tau)
                    g=dot((pt[0]-anchor[0],pt[1]-anchor[1]),n)
                    if g < -DELTA:
                        raise ValueError("supposed covered interval has sampled interpenetration")
    if touched!=1 or row.get("accepted_bounds")!=passed or row.get("unresolved_bounds")!=24-passed:
        raise ValueError("source qualification count or unique contact changed")
    if row.get("nominal_local_clearance_admitted") is not (passed==24):
        raise ValueError("unresolved source planes falsely cleared")
    expected=("CONDITIONAL_LOCAL_OUTGOING_SEPARATION" if passed==24 else
              "POST_CANDIDATE_LOCAL_GEOMETRY_UNRESOLVED")
    if row.get("status")!=expected:
        raise ValueError("post-response local status changed")
    return True


class World30Tests(unittest.TestCase):
    def test_synthetic_outgoing_central_contact_separates_over_short_window(self):
        h={"center":[0.,0.],"theta":0.,
           "velocity":[1.,0.],"spin":0.}
        n=(1.,0.)
        anchor=(.25,0.)
        out=independently_compute(h,2,n,anchor,True)
        self.assertGreater(out[4],0)
        self.assertTrue(out[6])

    def test_all_eight_original_source_statuses_verified_independently(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["source_qualified_fourth_candidates"],3)
        self.assertEqual(report["no_qualified_source_response"],5)
        self.assertEqual(report["actual_material_impacts_witnessed"]
                         if "actual_material_impacts_witnessed" in report else
                         report["real_material_impacts_witnessed"],0)
        self.assertEqual(report["selected_actual_fourth_impulses"],0)
        self.assertEqual(report["fifth_impulses_computed"],0)
        self.assertEqual(report["locally_separated_conditional_candidates"]+
                         report["post_candidate_geometry_unresolved"],3)
        for case in report["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_no_original_source_response_makes_no_new_motion(self):
        for angle in (0.,20.):
            c=attempt(angle)
            self.assertEqual(c["status"],"NO_QUALIFIED_SOURCE_FOURTH_RESPONSE")
            self.assertEqual(c["clearance_bounds"],[])

    def test_forged_real_contact_and_false_bound_are_refused(self):
        source=attempt(7.5)
        for key,value in (
            ("actual_contact_selected",True),
            ("real_material_response_witnessed",True),
            ("fifth_impulse_computed",True),
            ("post_candidate_horizon",1.),
            ("formally_outward_rounded_numeric_certificate",True),
        ):
            changed=deepcopy(source);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(changed)
        if source["clearance_bounds"]:
            changed=deepcopy(source)
            changed["clearance_bounds"][0]["accepted"]=not changed["clearance_bounds"][0]["accepted"]
            with self.assertRaises(ValueError):
                verify(changed)


if __name__=="__main__":
    unittest.main()
