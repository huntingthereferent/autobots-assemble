"""Independent WORLD41 CCW square original post-sixth clearance witness.

Reconstruct all 24 original signed gaps directly from CCW rigid-square
coordinates and independently supplied original six planes. Verify each
source-accepted chronological subinterval against two endpoint neighborhoods
and independently bound outgoing selected-source normal rate over the entire
prefix. Refuse skipped time, fabricated seventh impulses, or physical sixth.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,hypot,isfinite
import unittest

from systems.workspace.world_ab_post_sixth_local_clearance import (
    attempt,run,SCHEMA,WINDOW,BASE_SLABS,REFINE_DEPTH,
    POSITIVE_GUARD,START_ZERO_TOL,DEPART_RATE_GUARD
)
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as original40
from network.tests.test_world_ab_sixth_conditional_normal_law import verify as verify40
from systems.workspace.world_ab_local_zero_gap_after_guard import attempt as original39
from systems.workspace.world_ab_whole_contact_configuration import attempt as original35
from systems.workspace.world_ab_post_fifth_contiguous_prefix import model_at_conditional_fifth
from systems.workspace.world_ab_third_contact import attempt as original21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
ORIGINAL_INDEX=(0,3,1,2)
NUM_TOL=5e-8


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def square_corner(model,index,t):
    x,y=CCW[ORIGINAL_INDEX[index]]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    r=(x*c-y*s,x*s+y*c)
    p=(model["center"][0]+model["velocity"][0]*t+r[0],
       model["center"][1]+model["velocity"][1]*t+r[1])
    velocity=(model["velocity"][0]-model["spin"]*r[1],
              model["velocity"][1]+model["spin"]*r[0])
    return p,velocity


def world_at_sixth(angle,source):
    fifth=original35(angle)
    root=original39(angle)["bracketed_first_zero_time"]
    h=model_at_conditional_fifth(fifth,original21(angle))
    return {"center":[h["center"][i]+h["velocity"][i]*root for i in (0,1)],
            "theta":h["theta"]+h["spin"]*root,
            "velocity":list(source["conditional_sixth_response"]["outgoing_velocity"]),
            "spin":source["conditional_sixth_response"]["outgoing_spin"]}


def analytic_original_slab(model,planes,face,index,a,b):
    selected=next(z for z in planes if z[0]==face)
    _,n,anchor,length=selected
    if length is None:raise ValueError("source selected face not original finite face")
    p0,v0=square_corner(model,index,0.)
    initial_gap=dot((p0[0]-anchor[0],p0[1]-anchor[1]),n)
    initial_rate=dot(v0,n)
    global_rate_floor=initial_rate-model["spin"]**2*hypot(HALF,HALF)*b
    selected_ok=abs(initial_gap)<=START_ZERO_TOL and global_rate_floor>DEPART_RATE_GUARD
    rows=[]
    for name,normal,anchor_point,span in planes:
        speed=abs(dot(model["velocity"],normal))+abs(model["spin"])*hypot(HALF,HALF)
        for corner_id in range(4):
            p_left,_=square_corner(model,corner_id,a)
            p_right,_=square_corner(model,corner_id,b)
            gl=dot((p_left[0]-anchor_point[0],p_left[1]-anchor_point[1]),normal)
            gr=dot((p_right[0]-anchor_point[0],p_right[1]-anchor_point[1]),normal)
            surplus=gl+gr-speed*(b-a)-2*POSITIVE_GUARD
            same=name==face and corner_id==index
            yes=(selected_ok if same else
                 gl>POSITIVE_GUARD and gr>POSITIVE_GUARD and surplus>0)
            rows.append((name,corner_id,span is not None,same,gl,gr,speed,
                         surplus,global_rate_floor if same else None,yes))
    return (initial_gap,initial_rate,global_rate_floor,rows,
            all(x[-1] for x in rows))


def verify_interval(source_record,model,planes,face,index,a,b,sufficient):
    witness=analytic_original_slab(model,planes,face,index,a,b)
    initial_gap,initial_rate,floor,rows,can_certify=witness
    if (source_record.get("all_original_constraints_checked")!=24
        or source_record.get("floating_point_not_formal_proof") is not True
        or not isinstance(source_record.get("bounds"),list)
        or len(source_record["bounds"])!=24
        or abs(source_record.get("start",-999)-a)>NUM_TOL
        or abs(source_record.get("end",-999)-b)>NUM_TOL):
        raise ValueError("wrong source nominal interval or original constraint count")
    for key,value in (
        ("selected_corner_initial_gap",initial_gap),
        ("selected_corner_initial_outgoing_normal_rate",initial_rate),
        ("selected_corner_global_outgoing_rate_lower",floor)):
        got=source_record.get(key)
        if not isinstance(got,(int,float)) or abs(got-value)>NUM_TOL:
            raise ValueError("original selected source departure mismatch")
    for record,independent in zip(source_record["bounds"],rows):
        name,idx,finite,selected,gl,gr,speed,surplus,rate,good=independent
        exact={
            "source_plane":name,"source_corner_index":idx,
            "original_plane_finite":finite,
            "selected_original_sixth_contact":selected,
            "nominal_interval_supported":good,
        }
        if any(record.get(k)!=v for k,v in exact.items()):
            raise ValueError("source original plane identity or separation faked")
        for key,value in (
            ("starting_signed_normal_gap",gl),
            ("ending_signed_normal_gap",gr),
            ("normal_speed_lipschitz_limit",speed),
            ("endpoint_neighborhood_surplus",surplus)):
            x=record.get(key)
            if not isinstance(x,(int,float)) or not isfinite(x) or abs(x-value)>NUM_TOL:
                raise ValueError("independent original corner endpoint/Lipschitz mismatch")
        if rate is None:
            if record.get("selected_contact_global_outward_rate_lower") is not None:
                raise ValueError("competitor assigned selected corner rate")
        else:
            x=record.get("selected_contact_global_outward_rate_lower")
            if not isinstance(x,(int,float)) or abs(x-rate)>NUM_TOL:
                raise ValueError("selected original departure rate altered")
    if source_record.get("interval_nominally_supported") is not can_certify or (
        can_certify is not sufficient):
        raise ValueError("unverified source interval promoted to certified continuation")
    return True


def verify(row):
    angle=row.get("angle")
    if angle not in ANGLES or row.get("schema")!=SCHEMA:
        raise ValueError("WORLD41 original source identity invalid")
    old=original40(angle)
    if not verify40(old):
        raise ValueError("original WORLD40 independent finite contact invalid")
    fixed={
        "source_trial40_schema":old["schema"],
        "source_trial40_status":old["status"],
        "source_original_sixth_response":old["conditional_sixth_response"],
        "original_24_by_6_world":[24.,6.],
        "source_original_finite_faces":2,
        "source_original_world_perimeter_planes":4,
        "declared_post_sixth_window":WINDOW,
        "base_slab_count":BASE_SLABS,
        "maximum_refinement_depth":REFINE_DEPTH,
        "positive_clearance_guard":POSITIVE_GUARD,
        "selected_zero_gap_tolerance":START_ZERO_TOL,
        "departure_rate_guard":DEPART_RATE_GUARD,
        "model_source_only":True,
        "material_sixth_impact_observed":False,
        "sixth_response_selected_as_physical":False,
        "material_seventh_impact_observed":False,
        "seventh_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_admitted":False,
        "outward_rounded_interval_proof":False,
    }
    if any(row.get(k)!=v for k,v in fixed.items()):
        raise ValueError("original source sixth geometry or physical refusal altered")
    if old["conditional_sixth_response"] is None:
        if (row.get("status")!="NO_SOURCE_SIXTH_RESPONSE"
            or row.get("original_conditional_sixth_pose") is not None
            or row.get("source_planes")!=[]
            or row.get("accepted_original_subintervals")!=[]
            or row.get("first_unknown_original_subinterval") is not None
            or row.get("supported_contiguous_prefix_end") is not None):
            raise ValueError("inactive original source case acquired seventh movement")
        return True
    model=world_at_sixth(angle,old)
    planes=original_planes(original21(angle),angle)
    chosen=(old["source_face"],old["source_corner"])
    pose=row.get("original_conditional_sixth_pose")
    if not isinstance(pose,dict):
        raise ValueError("sixth model pose omitted")
    for key,expected in (
        ("center",model["center"]),("theta",model["theta"]),
        ("velocity",model["velocity"]),("spin",model["spin"])):
        field="outgoing_velocity" if key=="velocity" else (
            "outgoing_spin" if key=="spin" else key)
        value=pose.get(field)
        if isinstance(expected,list):
            if not isinstance(value,list) or len(value)!=len(expected) or any(
                abs(value[i]-expected[i])>NUM_TOL for i in range(len(value))):
                raise ValueError("source sixth model vector drift")
        elif not isinstance(value,(int,float)) or abs(value-expected)>NUM_TOL:
            raise ValueError("source sixth model angular value drift")
    if (row.get("original_source_selected_face")!=chosen[0]
        or row.get("original_source_selected_corner")!=chosen[1]
        or row.get("source_planes")!=[z[0] for z in planes]):
        raise ValueError("original selected corner or six planes changed")
    accepted=row.get("accepted_original_subintervals")
    if not isinstance(accepted,list):raise ValueError("source accepted prefix not a list")
    count=[0]
    def visit(a,b,depth):
        bound=analytic_original_slab(model,planes,*chosen,a,b)
        sufficient=bound[-1]
        if sufficient:
            if count[0]>=len(accepted):
                raise ValueError("source omitted an original certified interval")
            verify_interval(accepted[count[0]],model,planes,*chosen,a,b,True)
            count[0]+=1
            return None
        if depth==REFINE_DEPTH:return a,b
        mid=(a+b)/2
        return visit(a,mid,depth+1) or visit(mid,b,depth+1)
    unknown=None
    for i in range(BASE_SLABS):
        a=WINDOW*i/BASE_SLABS
        b=WINDOW*(i+1)/BASE_SLABS
        unknown=visit(a,b,0)
        if unknown is not None:break
    if count[0]!=len(accepted):
        raise ValueError("source moved after first unknown original interval")
    full=unknown is None
    bound_time=accepted[-1]["end"] if accepted else 0.
    if (row.get("full_declared_window_supported") is not full
        or not isinstance(row.get("supported_contiguous_prefix_end"),(float,int))
        or abs(row["supported_contiguous_prefix_end"]-bound_time)>NUM_TOL):
        raise ValueError("source original certified prefix endpoint changed")
    if full:
        if row.get("first_unknown_original_subinterval") is not None:
            raise ValueError("invented source clearance failure")
    else:
        failed=row.get("first_unknown_original_subinterval")
        if (not isinstance(failed,dict)
            or failed.get("status")!="FIRST_POST_SIXTH_ORIGINAL_BOUND_UNRESOLVED"
            or failed.get("failed_bound_is_not_seventh_contact") is not True):
            raise ValueError("missing source first unresolved interval")
        verify_interval(failed,model,planes,*chosen,*unknown,False)
        if abs(bound_time-unknown[0])>NUM_TOL:
            raise ValueError("chronological source unknown skipped")
    status=("CONDITIONAL_SIXTH_FIRST_WINDOW_NOMINALLY_SEPARATED" if full
            else "FIRST_POST_SIXTH_CLEARANCE_BOUND_UNRESOLVED")
    if row.get("status")!=status:
        raise ValueError("unsupported original source trajectory declared clear")
    return True


class WORLD41Tests(unittest.TestCase):
    def test_all_original_source_cases_replay_independent_contiguous_prefix(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["eligible_conditional_sixth_models"],1)
        self.assertEqual(report["no_source_sixth_response_controls"],7)
        self.assertEqual(report["supported_full_windows"]+
                         report["first_unresolved_windows"],1)
        self.assertEqual(report["material_seventh_impacts"],0)
        for case in report["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_unqualified_source_controls_stop_before_any_new_time(self):
        for angle in (0.,5.,12.25,20.):
            case=attempt(angle)
            self.assertEqual(case["status"],"NO_SOURCE_SIXTH_RESPONSE")
            self.assertEqual(case["accepted_original_subintervals"],[])

    def test_original_selected_departure_bound_refuses_wrong_direction(self):
        from systems.workspace.world_ab_post_sixth_local_clearance import slab
        # Preserve the same six original planes and all 24 plane/corner
        # relationships even in the negative-direction test. The previous
        # one-plane fixture tested the topology guard, not outward motion.
        ancestor=original21(10.)
        planes=original_planes(ancestor,10.)
        face,n,anchor,span=next(z for z in planes if z[3] is not None)
        self.assertEqual(len(planes),6)
        self.assertEqual(sum(z[3] is not None for z in planes),2)
        # Corner zero starts on this original plane but moves *inward*.
        h={"center":[anchor[0]+HALF,anchor[1]+HALF],
           "theta":0.,"velocity":[-2.*n[0],-2.*n[1]],"spin":0.}
        candidate=slab(h,planes,(face,0),0.,.002)
        self.assertEqual(candidate["all_original_constraints_checked"],24)
        self.assertEqual(len(candidate["bounds"]),24)
        self.assertLess(candidate["selected_corner_initial_outgoing_normal_rate"],0)
        self.assertFalse(candidate["interval_nominally_supported"])

    def test_physical_seventh_and_tampered_original_gap_refused(self):
        case=attempt(10.)
        for name,value in (
            ("material_sixth_impact_observed",True),
            ("sixth_response_selected_as_physical",True),
            ("material_seventh_impact_observed",True),
            ("seventh_impulse_computed",True),
            ("new_receiver_constructed",True),
            ("post_first_unknown_motion_admitted",True),
            ("outward_rounded_interval_proof",True),
            ("original_24_by_6_world",[24.,24.])):
            altered=deepcopy(case);altered[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError):
                verify(altered)
        if case["accepted_original_subintervals"]:
            altered=deepcopy(case)
            altered["accepted_original_subintervals"][0]["bounds"][0][
                "ending_signed_normal_gap"]+=.05
            with self.assertRaises(ValueError):verify(altered)
        elif case["first_unknown_original_subinterval"] is not None:
            altered=deepcopy(case)
            altered["first_unknown_original_subinterval"]["bounds"][0][
                "ending_signed_normal_gap"]+=.05
            with self.assertRaises(ValueError):verify(altered)


if __name__=="__main__":
    unittest.main()
