"""WORLD43 independent finite source separation witness, not a line proxy.

CCW rigid-square ordering independently checks fixed SAT axes, both
unaltered ORIGINAL finite segments, four source perimeter planes, and
chronological first-unknown subdivision. It refuses to infer seventh contact
from a line crossing outside a finite segment.
"""
from __future__ import annotations
from copy import deepcopy
from functools import lru_cache
from math import cos,sin,hypot,isfinite
import unittest

from systems.workspace.world_ab_finite_post_sixth_source_separation import (
    attempt,run,SCHEMA,START,END,BASE_SLABS,MAX_REFINE,GUARD,
    face_witness
)
from systems.workspace.world_ab_first_post_sixth_guard_limit import attempt as prior42
from network.tests.test_world_ab_first_post_sixth_guard_limit import verify as verify42
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as prior40
from systems.workspace.world_ab_post_sixth_local_clearance import source_model
from systems.workspace.world_ab_post_fifth_contiguous_prefix import original_planes
from systems.workspace.world_ab_third_contact import ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
TOL=5e-8
RADIUS=hypot(HALF,HALF)


def dot(a,b):return a[0]*b[0]+a[1]*b[1]

def corners(h,t):
    theta=h["theta"]+h["spin"]*t
    co,si=cos(theta),sin(theta)
    center=(h["center"][0]+h["velocity"][0]*t,
            h["center"][1]+h["velocity"][1]*t)
    return [(center[0]+x*co-y*si,center[1]+x*si+y*co)
            for x,y in CCW]

def segments_world(planes):
    faces=[];world=[]
    for name,n,anchor,span in planes:
        if span is None:
            world.append((name,n,anchor));continue
        tangent=(-n[1],n[0])
        faces.append((name,n,(
            (anchor[0]-span*tangent[0]/2,anchor[1]-span*tangent[1]/2),
            (anchor[0]+span*tangent[0]/2,anchor[1]+span*tangent[1]/2))))
    return faces,world

def phase_axes(model,n,a,b):
    output=[("finite_segment_normal",n)]
    for label,t in (("square_at_start",a),("square_at_end",b)):
        phi=model["theta"]+model["spin"]*t
        c,s=cos(phi),sin(phi)
        output.extend(((label+"_first",(c,s)),(label+"_second",(-s,c))))
    return output

def sat_gap(q,segment,axis,reverse):
    proj_box=[dot(point,axis) for point in q]
    proj_seg=[dot(point,axis) for point in segment]
    return (min(proj_seg)-max(proj_box) if reverse
            else min(proj_box)-max(proj_seg))

def check_record(record,model,faces,world,a,b):
    if not isinstance(record,dict) or any(
        abs(record.get(k,-999)-value)>TOL for k,value in
        (("start",a),("end",b))):
        raise ValueError("original chronological interval changed")
    v=hypot(*model["velocity"])+abs(model["spin"])*RADIUS
    if (record.get("original_finite_face_count")!=2
        or record.get("original_world_perimeter_count")!=4
        or record.get("original_square_corner_count")!=4
        or record.get("uncertified_means_contact") is not False
        or record.get("formal_outward_rounded_certificate") is not False
        or abs(record.get("finite_rigid_vertex_speed_bound",-999)-v)>TOL):
        raise ValueError("original model speed/geometry or material refusal changed")
    qa,qb=corners(model,a),corners(model,b)
    recfaces=record.get("original_finite_face_certificates")
    recperims=record.get("original_world_perimeter_certificates")
    if not isinstance(recfaces,list) or len(recfaces)!=2 or not isinstance(
        recperims,list) or len(recperims)!=4:
        raise ValueError("finite two faces / world four perimeter records absent")
    all_clear=True
    for rec,(name,n,segment) in zip(recfaces,faces):
        options=[]
        for label,axis in phase_axes(model,n,a,b):
            for reverse in (False,True):
                ga=sat_gap(qa,segment,axis,reverse)
                gb=sat_gap(qb,segment,axis,reverse)
                lower=ga+gb-v*(b-a)-2*GUARD
                valid=ga>GUARD and gb>GUARD and lower>0
                options.append((label,axis,reverse,ga,gb,lower,valid))
        winning=next((x for x in options if
            x[0]==rec.get("axis_source") and
            x[2] is rec.get("reverse_segment_square_order") and
            isinstance(rec.get("fixed_axis"),list) and
            len(rec["fixed_axis"])==2 and all(abs(rec["fixed_axis"][i]-x[1][i])<TOL
                for i in range(2))),None)
        if rec.get("original_face")!=name or winning is None:
            raise ValueError("original finite SAT axis/face source not reproducible")
        for key,value in (
            ("start_projection_gap",winning[3]),
            ("end_projection_gap",winning[4]),
            ("endpoint_lipschitz_surplus",winning[5])):
            if not isinstance(rec.get(key),(float,int)) or abs(rec[key]-value)>TOL:
                raise ValueError("finite source positive-gap certificate tampered")
        if rec.get("separates_entire_subinterval") is not winning[6]:
            raise ValueError("finite source SAT accepted invalid bound")
        any_valid=any(x[6] for x in options)
        if rec["separates_entire_subinterval"] is not any_valid:
            raise ValueError("source hid a separating finite SAT axis")
        all_clear&=any_valid
    for rec,(name,n,anchor) in zip(recperims,world):
        gap0=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in qa)
        gap1=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in qb)
        lower=gap0+gap1-v*(b-a)-2*GUARD
        yes=gap0>GUARD and gap1>GUARD and lower>0
        if (rec.get("original_world_plane")!=name
            or rec.get("source_corner_count")!=4
            or rec.get("perimeter_clear_entire_subinterval") is not yes):
            raise ValueError("original world finite perimeter certification changed")
        for key,value in (
            ("start_minimum_corner_gap",gap0),
            ("end_minimum_corner_gap",gap1),
            ("endpoint_lipschitz_surplus",lower)):
            if not isinstance(rec.get(key),(int,float)) or abs(rec[key]-value)>TOL:
                raise ValueError("original world corner/perimeter gap changed")
        all_clear&=yes
    if record.get("nominal_separation_supported") is not bool(all_clear):
        raise ValueError("unsupported original model separation declared")
    return bool(all_clear)


@lru_cache(maxsize=16)
def original_independent_ancestry(angle):
    old=prior42(angle)
    if not verify42(old):
        raise ValueError("WORLD42 independent original guard witness failed")
    return old,prior40(angle)


def verify(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("WORLD43 source angle/schema invalid")
    prior,before=original_independent_ancestry(angle)
    fixed={
        "source_trial42_schema":prior["schema"],
        "source_trial42_status":prior["status"],
        "source_trial42_horizon":prior["supported_horizon_endpoint"],
        "original_world":[24.,6.],
        "original_finite_face_count":2,
        "original_world_perimeter_count":4,
        "original_corner_count":4,
        "source_window_start":START,
        "source_window_end":END,
        "base_interval_count":BASE_SLABS,
        "max_bisection_depth":MAX_REFINE,
        "positive_finite_separation_guard":GUARD,
        "conditional_sixth_response_only":True,
        "physical_sixth_impact_observed":False,
        "physical_seventh_impact_observed":False,
        "seventh_impulse_computed":False,
        "source_continuation_after_first_unknown":False,
        "new_receiver_constructed":False,
        "outward_rounded_interval_certification":False,
    }
    if any(row.get(k)!=v for k,v in fixed.items()):
        raise ValueError("source finite WORLD original geometry/refusal changed")
    if (before["conditional_sixth_response"] is None or
        prior["status"]!="POST_SIXTH_ORIGINAL_GUARDS_CLEAR_THROUGH_HORIZON"):
        status=("NO_SOURCE_SIXTH_RESPONSE" if before["conditional_sixth_response"] is None
                else "SOURCE_T42_FIRST_HORIZON_NOT_SUPPORTED")
        if (row.get("status")!=status
            or row.get("original_conditional_model_at_sixth") is not None
            or row.get("original_finite_source_segments")!=[]
            or row.get("original_accepted_intervals")!=[]
            or row.get("first_finite_original_unknown") is not None
            or row.get("nominally_supported_prefix_end") is not None):
            raise ValueError("ineligible original source given future motion")
        return True
    model,ancestor=source_model(angle,before)
    planes=original_planes(ancestor,angle)
    faces,world=segments_world(planes)
    if len(faces)!=2 or len(world)!=4:
        raise ValueError("original two finite faces/four world planes missing")
    expected_pose={
        "center":model["center"],"theta":model["theta"],
        "outgoing_velocity":model["velocity"],"outgoing_spin":model["spin"]}
    got=row.get("original_conditional_model_at_sixth")
    if not isinstance(got,dict):raise ValueError("source sixth pose absent")
    for key,want in expected_pose.items():
        observed=got.get(key)
        if isinstance(want,list):
            if not isinstance(observed,list) or len(observed)!=len(want) or any(
                abs(observed[i]-want[i])>TOL for i in range(len(want))):
                raise ValueError("source original conditional six pose drift")
        elif not isinstance(observed,(float,int)) or abs(observed-want)>TOL:
            raise ValueError("original conditional sixth spin/orientation changed")
    expect_faces=[{"name":n,"endpoints":[[round(z,12) for z in p] for p in seg]}
                  for n,_,seg in faces]
    if row.get("original_finite_source_segments")!=expect_faces or row.get(
        "source_original_perimeter_planes")!=[n for n,_,_ in world]:
        raise ValueError("source finite segments replaced")
    accepted=row.get("original_accepted_intervals")
    if not isinstance(accepted,list):raise ValueError("accepted intervals not a list")
    count=[0]
    def replay(a,b,depth):
        # Independent CCW full-time finite SAT and world perimeter test.
        q0,q1=corners(model,a),corners(model,b)
        v=hypot(*model["velocity"])+abs(model["spin"])*RADIUS
        admissible=True
        for name,n,seg in faces:
            qualifies=False
            for _,axis in phase_axes(model,n,a,b):
                for reverse in (False,True):
                    ga=sat_gap(q0,seg,axis,reverse)
                    gb=sat_gap(q1,seg,axis,reverse)
                    if ga>GUARD and gb>GUARD and ga+gb-v*(b-a)>2*GUARD:
                        qualifies=True
            admissible&=qualifies
        for _,n,anchor in world:
            ga=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in q0)
            gb=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in q1)
            admissible&=(ga>GUARD and gb>GUARD and
                          ga+gb-v*(b-a)>2*GUARD)
        if admissible:
            if count[0]>=len(accepted):
                raise ValueError("original accepted finite clearance slab omitted")
            if not check_record(accepted[count[0]],model,faces,world,a,b):
                raise ValueError("invalid accepted finite original slab")
            count[0]+=1
            return None
        if depth==MAX_REFINE:return a,b
        mid=(a+b)/2
        return replay(a,mid,depth+1) or replay(mid,b,depth+1)
    unknown=None
    for i in range(BASE_SLABS):
        a=START+(END-START)*i/BASE_SLABS
        b=START+(END-START)*(i+1)/BASE_SLABS
        unknown=replay(a,b,0)
        if unknown:break
    if count[0]!=len(accepted):
        raise ValueError("accepted source intervals skip chronology")
    first=accepted[-1]["end"] if accepted else START
    full=unknown is None
    if (row.get("entire_finite_declared_window_supported") is not full
        or not isinstance(row.get("nominally_supported_prefix_end"),(int,float))
        or abs(row["nominally_supported_prefix_end"]-first)>TOL):
        raise ValueError("first finite unsupported bound ignored")
    if full:
        if row.get("first_finite_original_unknown") is not None:
            raise ValueError("source invented first unknown")
    else:
        failed=row.get("first_finite_original_unknown")
        if (not isinstance(failed,dict)
            or failed.get("status")!="FIRST_FINITE_ORIGINAL_SEPARATION_UNRESOLVED"
            or failed.get("seventh_collision_measured") is not False
            or check_record(failed,model,faces,world,*unknown)):
            raise ValueError("unresolved finite interval not preserved")
        if abs(first-unknown[0])>TOL:
            raise ValueError("model moved beyond first unknown finite interval")
    status=("FINITE_ORIGINAL_SEGMENTS_NOMINALLY_SEPARATED_THROUGH_HORIZON"
            if full else "FIRST_FINITE_ORIGINAL_SEPARATION_UNRESOLVED")
    if row.get("status")!=status:
        raise ValueError("finite original source output mislabels unknown")
    return True


class World43Tests(unittest.TestCase):
    def test_independent_original_finite_source_and_world_perimeter_prefix(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["inactive_original_controls"],7)
        self.assertEqual(data["admitted_post_sixth_finite_models"]+
                         data["prior_horizon_unresolved"],1)
        self.assertEqual(data["admitted_post_sixth_finite_models"],
                         data["complete_finite_windows"]+data["first_finite_unknown_models"])
        self.assertEqual(data["material_seventh_contacts"],0)
        for row in data["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_supporting_line_through_square_outside_finite_segment_is_separated(self):
        h={"center":[0.,0.],"theta":0.,"velocity":[0.,0.],"spin":0.}
        seg=((0.,2.),(0.,3.))
        q=corners(h,START)
        self.assertLess(min(p[0] for p in q),0.)
        self.assertGreater(max(p[0] for p in q),0.)
        winner=face_witness(h,("synthetic_finite_original",(1.,0.),seg),
                            q,q,START,START+.002,0.)
        self.assertTrue(winner["separates_entire_subinterval"])
        self.assertNotEqual(winner["axis_source"],"finite_segment_normal")

    def test_false_seventh_and_source_finite_gap_tampering_rejected(self):
        row=attempt(10.)
        for field,value in (
            ("physical_sixth_impact_observed",True),
            ("physical_seventh_impact_observed",True),
            ("seventh_impulse_computed",True),
            ("source_continuation_after_first_unknown",True),
            ("new_receiver_constructed",True),
            ("outward_rounded_interval_certification",True),
            ("original_world",[6.,24.])):
            fake=deepcopy(row);fake[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(fake)
        if row["original_accepted_intervals"]:
            fake=deepcopy(row)
            fake["original_accepted_intervals"][0][
                "original_finite_face_certificates"][0]["end_projection_gap"]+=.3
            with self.assertRaises(ValueError):verify(fake)
        elif row["first_finite_original_unknown"] is not None:
            fake=deepcopy(row)
            fake["first_finite_original_unknown"][
                "original_finite_face_certificates"][0]["end_projection_gap"]+=.3
            with self.assertRaises(ValueError):verify(fake)

if __name__=="__main__":
    unittest.main()
