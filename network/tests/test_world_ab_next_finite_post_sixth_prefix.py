"""WORLD44 independent CCW finite-geometry witness on [.50,.75].

Use a different CCW square vertex order and independently reconstruct BOTH
original finite segments from the original planes. For every source accepted
subinterval, independently replay all candidate fixed SAT projection axes,
world perimeter gaps and chronological bisections. No contact follows from a
failed positive-separation bound.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from math import cos,sin,hypot,isfinite
import unittest

from systems.workspace.world_ab_next_finite_post_sixth_prefix import (
    attempt,run,SCHEMA,START,END,BASE,REFINE,GUARD
)
from systems.workspace.world_ab_finite_post_sixth_source_separation import attempt as trial43
from network.tests.test_world_ab_finite_post_sixth_source_separation import verify as verify43
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as trial40
from systems.workspace.world_ab_post_sixth_local_clearance import source_model
from systems.workspace.world_ab_post_fifth_contiguous_prefix import original_planes
from systems.workspace.world_ab_third_contact import ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
TOL=6e-8


def dot(a,b):return a[0]*b[0]+a[1]*b[1]


def rotate_corners(h,t):
    theta=h["theta"]+h["spin"]*t
    c,s=cos(theta),sin(theta)
    centre=(h["center"][0]+h["velocity"][0]*t,
            h["center"][1]+h["velocity"][1]*t)
    return [(centre[0]+x*c-y*s,centre[1]+x*s+y*c)
            for x,y in CCW]


def source_faces(planes):
    faces=[];perimeters=[]
    for name,n,anchor,span in planes:
        if span is None:perimeters.append((name,n,anchor))
        else:
            tangent=(-n[1],n[0])
            ends=tuple((anchor[0]+s*span*tangent[0]/2,
                        anchor[1]+s*span*tangent[1]/2) for s in (-1,1))
            faces.append((name,n,ends))
    return faces,perimeters


def candidate_axes(h,n,a,b):
    output=[("finite_segment_normal",n)]
    for prefix,t in (("square_at_start",a),("square_at_end",b)):
        angle=h["theta"]+h["spin"]*t
        c,s=cos(angle),sin(angle)
        output.extend(((prefix+"_first",(c,s)),(prefix+"_second",(-s,c))))
    return output


def finite_gap(quad,ends,axis,reverse):
    x=[dot(point,axis) for point in quad]
    y=[dot(point,axis) for point in ends]
    return min(y)-max(x) if reverse else min(x)-max(y)


def independent_slab(h,faces,perimeters,a,b,record=None):
    qa=rotate_corners(h,a);qb=rotate_corners(h,b)
    L=hypot(*h["velocity"])+abs(h["spin"])*hypot(HALF,HALF)
    finite=[]
    for name,n,ends in faces:
        options=[]
        for source,axis in candidate_axes(h,n,a,b):
            for reverse in (False,True):
                ga=finite_gap(qa,ends,axis,reverse)
                gb=finite_gap(qb,ends,axis,reverse)
                extra=ga+gb-L*(b-a)-2*GUARD
                valid=ga>GUARD and gb>GUARD and extra>0
                options.append((source,axis,reverse,ga,gb,extra,valid))
        finite.append((name,options,any(o[-1] for o in options)))
    world=[]
    for name,n,anchor in perimeters:
        gl=min(dot((q[0]-anchor[0],q[1]-anchor[1]),n) for q in qa)
        gr=min(dot((q[0]-anchor[0],q[1]-anchor[1]),n) for q in qb)
        margin=gl+gr-L*(b-a)-2*GUARD
        world.append((name,gl,gr,margin,
                      gl>GUARD and gr>GUARD and margin>0))
    yes=all(x[2] for x in finite) and all(x[4] for x in world)
    if record is None:return yes
    if (not isinstance(record,dict)
        or abs(record.get("start",-10)-a)>TOL
        or abs(record.get("end",-10)-b)>TOL
        or record.get("original_square_vertex_count")!=4
        or record.get("original_finite_faces")!=[x[0] for x in faces]
        or record.get("original_world_perimeters")!=[x[0] for x in perimeters]
        or abs(record.get("vertex_speed_lipschitz_bound",-10)-L)>TOL
        or record.get("failed_bound_is_seventh_impact") is not False
        or record.get("numerical_not_outward_rounded") is not True
        or record.get("finite_interval_separation_supported") is not yes):
        raise ValueError("original finite WORLD44 separation record falsified")
    fs=record.get("source_finite_segment_SAT_witnesses")
    ps=record.get("source_world_perimeter_witnesses")
    if not isinstance(fs,list) or len(fs)!=2 or not isinstance(ps,list) or len(ps)!=4:
        raise ValueError("original six finite/perimeter witnesses missing")
    for witness,(name,options,has) in zip(fs,finite):
        if witness.get("original_face")!=name:
            raise ValueError("original source finite face replaced")
        match=next((x for x in options if
            x[0]==witness.get("axis_source") and
            x[2] is witness.get("reverse_segment_square_order") and
            isinstance(witness.get("fixed_axis"),list) and
            len(witness["fixed_axis"])==2 and all(abs(x[1][i]-witness["fixed_axis"][i])<TOL
                for i in range(2))),None)
        if match is None or match[-1] is not witness.get("separates_entire_subinterval"):
            raise ValueError("no independent fixed SAT witness on original segment")
        if match[-1]!=has:
            raise ValueError("source omitted viable finite separating SAT axis")
        for key,value in zip(("start_projection_gap","end_projection_gap",
                              "endpoint_lipschitz_surplus"),match[3:6]):
            got=witness.get(key)
            if not isinstance(got,(int,float)) or not isfinite(got) or abs(got-value)>TOL:
                raise ValueError("original SAT endpoint/margin changed")
    for witness,(name,gl,gr,margin,good) in zip(ps,world):
        if (witness.get("original_world_plane")!=name
            or witness.get("source_corner_count")!=4
            or witness.get("perimeter_clear_entire_subinterval") is not good):
            raise ValueError("original world perimeter coverage invalid")
        for field,value in (
            ("start_minimum_corner_gap",gl),
            ("end_minimum_corner_gap",gr),
            ("endpoint_lipschitz_surplus",margin)):
            got=witness.get(field)
            if not isinstance(got,(float,int)) or abs(got-value)>TOL:
                raise ValueError("original world source perimeter bound tampered")
    return yes


@lru_cache(maxsize=16)
def independently_verify_parent(angle):
    prior=trial43(angle)
    if not verify43(prior):
        raise ValueError("WORLD43 native independent finite-source ancestry invalid")
    return prior,trial40(angle)


def verify(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("original source schema or angle changed")
    prior,sixth=independently_verify_parent(angle)
    expected={
        "original_trial43_schema":prior["schema"],
        "original_trial43_status":prior["status"],
        "original_trial43_supported_endpoint":prior["nominally_supported_prefix_end"],
        "world_dimensions":[24.,6.],
        "original_static_finite_segment_count":2,
        "original_world_perimeter_count":4,
        "original_rotating_square_corner_count":4,
        "window_start":START,"window_end":END,
        "base_slab_count":BASE,"max_bisection_depth":REFINE,
        "positive_clearance_guard":GUARD,
        "sixth_impulse_unselected_model_only":True,
        "physical_sixth_contact_measured":False,
        "physical_seventh_contact_measured":False,
        "seventh_impulse_selected":False,
        "new_receiver_constructed":False,
        "source_motion_after_first_unknown_admitted":False,
        "formal_outward_rounded_interval_proof":False,
    }
    if any(row.get(k)!=value for k,value in expected.items()):
        raise ValueError("source world dimensions, dependency or physical refusal changed")
    eligible=(sixth["conditional_sixth_response"] is not None
              and prior["status"]=="FINITE_ORIGINAL_SEGMENTS_NOMINALLY_SEPARATED_THROUGH_HORIZON")
    if not eligible:
        status=("NO_ADMITTED_SIXTH_RESPONSE"
                if sixth["conditional_sixth_response"] is None
                else "SOURCE_T43_FINITE_WINDOW_UNRESOLVED")
        if (row.get("status")!=status
            or row.get("conditional_sixth_pose") is not None
            or row.get("accepted_original_intervals")!=[]
            or row.get("source_finite_segments")!=[]
            or row.get("first_unknown_original_interval") is not None
            or row.get("supported_finite_prefix_end") is not None):
            raise ValueError("inadmissible source granted further movement")
        return True
    h,old=source_model(angle,sixth)
    faces,world=source_faces(original_planes(old,angle))
    if len(faces)!=2 or len(world)!=4:
        raise ValueError("original finite/perimeter structures missing")
    pose=row.get("conditional_sixth_pose")
    if not isinstance(pose,dict):
        raise ValueError("source conditional sixth pose absent")
    for field,key in (("center","center"),("theta","theta"),
                      ("outgoing_velocity","velocity"),("outgoing_spin","spin")):
        got=pose.get(field)
        value=h[key]
        if isinstance(value,list):
            if not isinstance(got,list) or len(got)!=len(value) or any(
                abs(got[i]-value[i])>TOL for i in range(len(got))):
                raise ValueError("source original sixth model vector changed")
        elif not isinstance(got,(int,float)) or abs(got-value)>TOL:
            raise ValueError("original source model scalar drift")
    expected_faces=[{"name":name,"endpoints":[[round(x,12) for x in end] for end in ends]}
                    for name,_,ends in faces]
    if (row.get("source_finite_segments")!=expected_faces or
        row.get("source_world_perimeter_names")!=[name for name,_,_ in world]):
        raise ValueError("original finite material geometry changed")
    accepted=row.get("accepted_original_intervals")
    if not isinstance(accepted,list):
        raise ValueError("source original supported prefix missing")
    index=[0]
    def walk(a,b,depth):
        okay=independent_slab(h,faces,world,a,b)
        if okay:
            if index[0]>=len(accepted) or not independent_slab(
                h,faces,world,a,b,accepted[index[0]]):
                raise ValueError("source admitted gap not independently bounded")
            index[0]+=1
            return None
        if depth==REFINE:return a,b
        mid=(a+b)/2
        return walk(a,mid,depth+1) or walk(mid,b,depth+1)
    unknown=None
    for j in range(BASE):
        a=START+(END-START)*j/BASE
        b=START+(END-START)*(j+1)/BASE
        unknown=walk(a,b,0)
        if unknown is not None:break
    if index[0]!=len(accepted):
        raise ValueError("source includes movement past first unknown interval")
    last=accepted[-1]["end"] if accepted else START
    if (row.get("full_declared_finite_window_supported") is not (unknown is None)
        or not isinstance(row.get("supported_finite_prefix_end"),(int,float))
        or abs(row["supported_finite_prefix_end"]-last)>TOL):
        raise ValueError("source first original unknown chronology moved")
    if unknown is not None:
        u=row.get("first_unknown_original_interval")
        if (not isinstance(u,dict)
            or u.get("status")!="FIRST_ORIGINAL_FINITE_SEPARATION_BOUND_UNRESOLVED"
            or u.get("physical_seventh_contact_measured") is not False
            or independent_slab(h,faces,world,*unknown,u)
            or abs(last-unknown[0])>TOL):
            raise ValueError("first source unknown not retained exactly")
    elif row.get("first_unknown_original_interval") is not None:
        raise ValueError("source invented an unsupported interval")
    expected_status=("ORIGINAL_FINITE_SEPARATION_THROUGH_POST_SIXTH_0_75"
                     if unknown is None else
                     "FIRST_POST_SIXTH_FINITE_UNKNOWN_IN_0_5_TO_0_75")
    if row.get("status")!=expected_status:
        raise ValueError("source first finite unknown mislabeled")
    return True


class World44Tests(unittest.TestCase):
    def test_original_source_finite_prefix_independent_ccw_replay(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["inactive_source_controls"],7)
        self.assertEqual(data["admitted_original_finite_sources"]+
                         data["prior_original_source_unresolved"],1)
        self.assertEqual(data["admitted_original_finite_sources"],
                         data["fully_supported_0_75_horizons"]+
                         data["first_unknown_0_5_0_75_cases"])
        self.assertEqual(data["actual_seventh_impacts"],0)
        for row in data["cases"]:
            with self.subTest(angle=row["angle"]):self.assertTrue(verify(row))

    def test_original_finite_segment_outside_line_negative_control(self):
        # A short segment high above the square does not meet the square,
        # even though the infinite segment-support line x=0 cuts through it.
        model={"center":[0.,0.],"theta":0.,"velocity":[0.,0.],"spin":0.}
        faces=[("synthetic_finite",(1.,0.),((0.,2.),(0.,3.))),
               ("synthetic_second",(1.,0.),((3.,2.),(3.,3.)))]
        world=[("synthetic_world_left",(1.,0.),(-2.,0.)),
               ("synthetic_world_right",(-1.,0.),(2.,0.)),
               ("synthetic_world_bottom",(0.,1.),(0.,-2.)),
               ("synthetic_world_top",(0.,-1.),(0.,2.))]
        self.assertTrue(independent_slab(model,faces,world,.50,.501))

    def test_fake_seventh_and_original_finite_gap_tampering_rejected(self):
        source=attempt(10.)
        for field,value in (("physical_sixth_contact_measured",True),
                             ("physical_seventh_contact_measured",True),
                             ("seventh_impulse_selected",True),
                             ("new_receiver_constructed",True),
                             ("source_motion_after_first_unknown_admitted",True),
                             ("formal_outward_rounded_interval_proof",True),
                             ("world_dimensions",[6.,24.])):
            fake=deepcopy(source);fake[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):verify(fake)
        if source["accepted_original_intervals"]:
            fake=deepcopy(source)
            fake["accepted_original_intervals"][0][
                "source_finite_segment_SAT_witnesses"][0]["end_projection_gap"]+=.2
            with self.assertRaises(ValueError):verify(fake)
        elif source["first_unknown_original_interval"]:
            fake=deepcopy(source)
            fake["first_unknown_original_interval"][
                "source_finite_segment_SAT_witnesses"][0]["end_projection_gap"]+=.2
            with self.assertRaises(ValueError):verify(fake)


if __name__=="__main__":
    unittest.main()
