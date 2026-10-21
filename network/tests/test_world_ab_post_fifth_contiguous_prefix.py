"""Independent WORLD37 original source plane/corner continuous-prefix replay.

A second construction orders square vertices CCW and reconstructs all six
planes through existing independent WORLD witness ancestry. It replays each
source accepted slab, must stop at the FIRST unsupported leaf, and never
turns failed source clearance into a sixth material collision.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,hypot,pi,isfinite
import unittest

from systems.workspace.world_ab_post_fifth_contiguous_prefix import (
    attempt,run,SCHEMA,START,HORIZON,NEW_WINDOW,BASE_INTERVALS,
    REFINEMENT_DEPTH,GUARD
)
from systems.workspace.world_ab_post_fifth_local_clearance import attempt as trial36
from network.tests.test_world_ab_post_fifth_local_clearance import check as verify36
from systems.workspace.world_ab_whole_contact_configuration import attempt as trial35
from systems.workspace.world_ab_first_finite_response_qualification import attempt as trial29
from systems.workspace.world_ab_third_contact import attempt as trial21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

ORDER=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
SOURCE_MAP=(0,3,1,2)
TOL=2e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def corners(model,t):
    theta=model["theta"]+model["spin"]*t
    x=model["center"][0]+model["velocity"][0]*t
    y=model["center"][1]+model["velocity"][1]*t
    c,s=cos(theta),sin(theta)
    return [(x+ax*c-ay*s,y+ax*s+ay*c) for ax,ay in ORDER]


def check_sliver(model,planes,left,right):
    start,end=corners(model,left),corners(model,right)
    results=[]
    for name,n,anchor,span in planes:
        speed=abs(dot(model["velocity"],n))+abs(model["spin"])*hypot(HALF,HALF)
        for source_i,ccw_i in enumerate(SOURCE_MAP):
            pa,pb=start[ccw_i],end[ccw_i]
            gl=dot((pa[0]-anchor[0],pa[1]-anchor[1]),n)
            gr=dot((pb[0]-anchor[0],pb[1]-anchor[1]),n)
            surplus=gl+gr-speed*(right-left)-2*GUARD
            ok=gl>GUARD and gr>GUARD and surplus>0
            results.append((name,source_i,span is not None,gl,gr,speed,surplus,ok))
    return results


def check_record(record,model,planes,left,right,expected_ok):
    if not isinstance(record,dict) or (abs(record.get("left",-1)-left)>TOL
        or abs(record.get("right",-1)-right)>TOL
        or record.get("original_plane_corner_constraints")!=24
        or record.get("floating_point_not_outward_rounded") is not True):
        raise ValueError("source interval identity or numerical boundary altered")
    rows=record.get("source_bounds")
    if type(rows) is not list or len(rows)!=24:
        raise ValueError("source failed to preserve 24 original plane-corner constraints")
    witness=check_sliver(model,planes,left,right)
    for rec,(name,index,finite,gl,gr,speed,surplus,pass_) in zip(rows,witness):
        if (rec.get("source_plane")!=name
            or rec.get("source_corner_index")!=index
            or rec.get("source_plane_is_finite") is not finite
            or rec.get("interval_supported") is not pass_):
            raise ValueError("original plane/corner identity or accepted bound forged")
        for key,w in (("left_gap",gl),("right_gap",gr),
                      ("normal_speed_upper_bound",speed),
                      ("two_endpoint_neighborhood_surplus",surplus)):
            if (not isinstance(rec.get(key),(float,int)) or not isfinite(rec[key])
                or abs(rec[key]-w)>TOL):
                raise ValueError("independent original WORLD corner disagrees: "+key)
    enough=all(x[-1] for x in witness)
    if (record.get("interval_nominally_separated") is not enough
        or enough is not expected_ok):
        raise ValueError("source interval classification violates original constraints")
    return enough


def verify(row):
    angle=row.get("angle")
    previous=trial36(angle)
    before=trial35(angle)
    ancestor=trial21(angle)
    if row.get("schema")!=SCHEMA or angle not in ANGLES or not verify36(previous):
        raise ValueError("original WORLD36 independent evidence missing")
    fixed={
        "original_trial36_schema":previous["schema"],
        "original_trial36_status":previous["status"],
        "original_trial36_case":previous,
        "original_trial35_status":before["status"],
        "original_source_fifth_response":before["conditional_fifth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_finite_source_faces":2,
        "original_perimeter_planes":4,
        "source_original_short_window":START,
        "attempted_additional_window":NEW_WINDOW,
        "declared_max_post_fifth_horizon":HORIZON,
        "base_interval_count":BASE_INTERVALS,
        "maximum_refinement_depth":REFINEMENT_DEPTH,
        "positive_gap_guard":GUARD,
        "source_model_only":True,
        "material_fifth_impact_witnessed":False,
        "physical_fifth_impulse_selected":False,
        "sixth_contact_observed":False,
        "sixth_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_approved":False,
        "exact_interval_arithmetic_certificate":False,
    }
    if any(row.get(k)!=v for k,v in fixed.items()):
        raise ValueError("original conditional source ancestry or refusal altered")
    if (before["conditional_fifth_response"] is None
        or previous["status"]!="CONDITIONAL_FIFTH_LOCAL_CLEARANCE_NOMINALLY_SUPPORTED"):
        status=("NO_QUALIFIED_SOURCE_FIFTH_RESPONSE"
                if before["conditional_fifth_response"] is None else
                "PREVIOUS_SHORT_CLEARANCE_NOT_SUPPORTED")
        if (row.get("status")!=status
            or row.get("source_plane_names")!=[]
            or row.get("initial_clearance_time") is not None
            or row.get("attempted_end_time") is not None
            or row.get("supported_prefix_end") is not None
            or row.get("supported_source_subintervals")!=[]
            or row.get("first_unsupported_subinterval") is not None
            or row.get("full_new_interval_supported") is not False):
            raise ValueError("inactive original WORLD case acquired later motion")
        return True
    fourth=trial29(angle)
    t=before["candidate_virtual_time"]
    original=fourth["qualifying_source_feature"]
    response=fourth["conditional_fourth_response"]
    final=before["conditional_fifth_response"]
    model={
        "center":[original["contact_center"][i]+response["outgoing_velocity"][i]*t
                  for i in (0,1)],
        "theta":original["contact_angle"]+response["outgoing_spin"]*t,
        "velocity":final["outgoing_velocity"],"spin":final["outgoing_spin"]
    }
    planes=original_planes(ancestor,angle)
    if (row.get("source_plane_names")!=[x[0] for x in planes]
        or row.get("initial_clearance_time")!=START
        or abs(row.get("attempted_end_time",0)-min(HORIZON,START+NEW_WINDOW))>TOL):
        raise ValueError("original plane/time horizon replaced")
    accepted=row.get("supported_source_subintervals")
    if type(accepted) is not list:
        raise ValueError("source accepted prefix missing")
    current=[0]
    def walk(a,b,depth):
        sufficient=all(z[-1] for z in check_sliver(model,planes,a,b))
        if sufficient:
            if current[0]>=len(accepted):
                raise ValueError("source omitted a supported original interval")
            check_record(accepted[current[0]],model,planes,a,b,True)
            current[0]+=1
            return None
        if depth==REFINEMENT_DEPTH:return a,b
        midpoint=(a+b)/2
        return walk(a,midpoint,depth+1) or walk(midpoint,b,depth+1)
    unknown=None
    end=min(HORIZON,START+NEW_WINDOW)
    for i in range(BASE_INTERVALS):
        a=START+(end-START)*i/BASE_INTERVALS
        b=START+(end-START)*(i+1)/BASE_INTERVALS
        unknown=walk(a,b,0)
        if unknown is not None:break
    if current[0]!=len(accepted):
        raise ValueError("source accepted extra intervals after its first unknown")
    full=unknown is None
    supported=accepted[-1]["right"] if accepted else START
    if (row.get("full_new_interval_supported") is not full
        or abs(row.get("supported_prefix_end",0)-supported)>TOL):
        raise ValueError("source verified prefix endpoint replaced")
    if full:
        if row.get("first_unsupported_subinterval") is not None:
            raise ValueError("invented original bound limit")
    else:
        limit=row.get("first_unsupported_subinterval")
        if (not isinstance(limit,dict)
            or limit.get("status")!="FIRST_SOURCE_CLEARANCE_BOUND_UNRESOLVED"
            or limit.get("bound_failure_is_not_collision") is not True):
            raise ValueError("missing first source unknown or false impact")
        check_record(limit,model,planes,*unknown,False)
        if abs(supported-unknown[0])>TOL:
            raise ValueError("skipped original unverified time")
    expected=("EXTENDED_CONDITIONAL_FIFTH_MODEL_CLEARANCE_SUPPORTED" if full
              else "FIRST_POST_FIFTH_LOCAL_BOUND_UNRESOLVED")
    if row.get("status")!=expected:
        raise ValueError("first source limit upgraded to real sixth impact")
    return True


class WORLD37Tests(unittest.TestCase):
    def test_all_eight_original_qualification_and_contiguous_prefixes(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["source_qualified_post_fifth_cases"],1)
        self.assertEqual(data["no_original_fifth_response_controls"],7)
        self.assertEqual(data["complete_new_window_cases"]+
                         data["first_unknown_window_cases"],1)
        self.assertEqual(data["material_sixth_contacts"],0)
        self.assertEqual(data["sixth_impulses"],0)
        for row in data["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_known_between_endpoint_rotation_not_falsely_separated(self):
        from systems.workspace.world_ab_post_fifth_contiguous_prefix import interval
        delta=.01
        spin=pi/(2*delta)
        m={"center":[1.25*HALF,0.],
           "theta":-spin*START,"velocity":[0.,0.],"spin":spin}
        # Positive at both endpoints, negative for the same vertex at midpoint.
        a,b=START,START+delta
        n=(1.,0.);anchor=(0.,0.)
        pts0=corners(m,a);ptsm=corners(m,(a+b)/2);pts1=corners(m,b)
        self.assertGreater(min(p[0] for p in pts0),0)
        self.assertGreater(min(p[0] for p in pts1),0)
        self.assertLess(min(p[0] for p in ptsm),0)
        slab=interval(m,[("synthetic",n,anchor,None)],a,b)
        self.assertFalse(slab["interval_nominally_separated"])

    def test_inactive_source_controls_remain_inactive(self):
        for angle in (0.,5.,12.25,20.):
            result=attempt(angle)
            self.assertEqual(result["status"],"NO_QUALIFIED_SOURCE_FIFTH_RESPONSE")
            self.assertEqual(result["supported_source_subintervals"],[])

    def test_forged_sixth_or_missing_original_bound_rejected(self):
        sample=attempt(10.)
        for k,v in (("material_fifth_impact_witnessed",True),
                    ("physical_fifth_impulse_selected",True),
                    ("sixth_contact_observed",True),
                    ("sixth_impulse_computed",True),
                    ("new_receiver_constructed",True),
                    ("post_first_unknown_motion_approved",True),
                    ("exact_interval_arithmetic_certificate",True),
                    ("original_24_by_6_world",[6.,24.])):
            tampered=deepcopy(sample);tampered[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):verify(tampered)
        if sample["supported_source_subintervals"]:
            tampered=deepcopy(sample)
            tampered["supported_source_subintervals"][0]["source_bounds"][0]["left_gap"]+=.05
            with self.assertRaises(ValueError):verify(tampered)


if __name__=="__main__":
    unittest.main()
