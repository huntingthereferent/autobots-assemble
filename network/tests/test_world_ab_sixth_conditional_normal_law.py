"""Independent WORLD40 whole-contact finite SAT and original elastic law witness.

Reconstruct zero-gap source corner using CCW square order, test both original
finite segments using separating axes (not source finite_clip), re-use the
WORLD39 independent all-24 competing-gap witness, then reconstruct the normal
impulse without calling source ideal_response. Preserve seven inactive cases
and material/sixth-continuation refusal.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,isfinite
import unittest

from systems.workspace.world_ab_sixth_conditional_normal_law import (
    attempt,run,SCHEMA,GAP_TOL,SPEED_GUARD,SEGMENT_GUARD,
    OTHER_GAP_GUARD,CONSERVATION_TOL
)
from systems.workspace.world_ab_local_zero_gap_after_guard import attempt as prior39
from network.tests.test_world_ab_local_zero_gap_after_guard import check as verify39
from systems.workspace.world_ab_whole_contact_configuration import attempt as prior35
from systems.workspace.world_ab_post_fifth_contiguous_prefix import model_at_conditional_fifth
from systems.workspace.world_ab_third_contact import attempt as prior21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from network.tests.test_world_ab_finite_segment_square_overlap import sat_segment_square
from systems.workspace.world_ab_oblique_impact import HALF,INERTIA

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
SOURCE_MAP=(0,3,1,2)
TOL=8e-7

def dot(a,b):return a[0]*b[0]+a[1]*b[1]

def independent_corner(h,index,t):
    x,y=CCW[SOURCE_MAP[index]]
    theta=h["theta"]+h["spin"]*t
    c,s=cos(theta),sin(theta)
    lever=(x*c-y*s,x*s+y*c)
    p=(h["center"][0]+h["velocity"][0]*t+lever[0],
       h["center"][1]+h["velocity"][1]*t+lever[1])
    v=(h["velocity"][0]-h["spin"]*lever[1],
       h["velocity"][1]+h["spin"]*lever[0])
    return p,lever,v


def independent_finite_segments(planes):
    segments=[]
    for name,n,anchor,span in planes:
        if span is None:continue
        tangent=(-n[1],n[0])
        segments.append((name,
            [[anchor[0]-span*tangent[0]/2,anchor[1]-span*tangent[1]/2],
             [anchor[0]+span*tangent[0]/2,anchor[1]+span*tangent[1]/2]]))
    return segments


def verify(row):
    angle=row.get("angle")
    if angle not in ANGLES or row.get("schema")!=SCHEMA:
        raise ValueError("WORLD40 source identity missing")
    old=prior39(angle)
    if not verify39(old):
        raise ValueError("WORLD39 independent source geometry failed")
    fixed={
        "source_trial39_schema":old["schema"],
        "source_trial39_status":old["status"],
        "source_first_original_zero_gap_time":old["bracketed_first_zero_time"],
        "original_24_by_6_world":[24.,6.],
        "source_original_two_finite_faces":True,
        "source_original_four_perimeter_planes":True,
        "original_mass":1.0,"original_inertia":INERTIA,
        "unchanged_law":"unit-mass frictionless normal restitution=1",
        "fifth_response_unselected":True,
        "measured_sixth_impact":False,
        "sixth_response_selected_as_physical":False,
        "post_sixth_continuation_admitted":False,
        "new_receiver_constructed":False,
        "outward_rounded_exact_contact_proof":False,
    }
    if any(row.get(k)!=v for k,v in fixed.items()):
        raise ValueError("original source law, geometry, or physical boundary altered")
    if old["status"]!="LOCAL_ORIGINAL_ZERO_GAP_NUMERICAL_FEATURE_QUALIFIED":
        expected=("NO_SOURCE_SIXTH_CANDIDATE" if
                  old["status"]=="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE"
                  else "UNQUALIFIED_ORIGINAL_ZERO_GAP_PROBE")
        if (row.get("status")!=expected
            or row.get("conditional_sixth_response") is not None
            or row.get("source_face") is not None
            or row.get("source_contact_geometry_independently_consistent") is not False):
            raise ValueError("unqualified source manufactured sixth response")
        return True
    fifth=prior35(angle)
    world=prior21(angle)
    h=model_at_conditional_fifth(fifth,world)
    planes=original_planes(world,angle)
    if len(planes)!=6:
        raise ValueError("original six planes changed")
    face=old["selected_source_face"]
    index=old["selected_corner"]
    t=old["bracketed_first_zero_time"]
    selected=next((x for x in planes if x[0]==face and x[3] is not None),None)
    if selected is None:
        raise ValueError("original finite face absent")
    _,n,anchor,span=selected
    p,r,v=independent_corner(h,index,t)
    offset=(p[0]-anchor[0],p[1]-anchor[1])
    tangent=(-n[1],n[0])
    gap=dot(offset,n)
    along=dot(offset,tangent)
    arrival=dot(v,n)
    inside=abs(along)<span/2-SEGMENT_GUARD
    geometry=(abs(gap)<=GAP_TOL and inside and arrival<-SPEED_GUARD
              and abs(arrival-old["source_normal_rate_at_zero"])<=SPEED_GUARD
              and all(abs(p[i]-old["first_zero_contact_model_position"][i])<=GAP_TOL
                      for i in (0,1)))
    rows=old["source_24_plane_corner_probe_records"]
    competitors=(len(rows)==24 and
                 sum(rec["selected_guard_feature"] for rec in rows)==1 and
                 all(rec["other_original_relation_separated_through_probe"] is True
                     and rec["conservative_other_gap_lower_bound"]>OTHER_GAP_GUARD
                     for rec in rows if not rec["selected_guard_feature"]))
    model={"contact_center":h["center"],"contact_orientation":h["theta"],
           "outgoing_velocity":h["velocity"],"outgoing_spin":h["spin"]}
    segment_results={name:sat_segment_square(model,segment,t)
                     for name,segment in independent_finite_segments(planes)}
    if len(segment_results)!=2:
        raise ValueError("original two source segments lost")
    selected_overlap=segment_results[face]
    other_overlap=any(v for key,v in segment_results.items() if key!=face)
    fixed_state={
        "source_face":face,"source_corner":index,
        "selected_corner_approaches_inside_finite_face":inside,
        "all_original_23_competing_clearances_retained":competitors,
        "original_selected_face_finite_clip_intersects":selected_overlap,
        "original_other_face_finite_clip_intersects":other_overlap,
        "source_contact_geometry_independently_consistent":geometry,
    }
    if any(row.get(k)!=v for k,v in fixed_state.items()):
        raise ValueError("independent source finite SAT/geometry contradicts source")
    for name,value in (("source_zero_gap",gap),
                       ("source_face_tangent",along),
                       ("incoming_source_normal_rate",arrival)):
        if not isinstance(row.get(name),(int,float)) or abs(row[name]-value)>TOL:
            raise ValueError("source zero-gap coordinate/normal rate changed")
    qualified=geometry and competitors and selected_overlap and not other_overlap
    response=row.get("conditional_sixth_response")
    expected=("CONDITIONAL_SIXTH_ELASTIC_RESPONSE_MATHEMATICALLY_QUALIFIED"
              if qualified else "ORIGINAL_SIXTH_CONFIGURATION_UNRESOLVED")
    if row.get("status")!=expected:
        raise ValueError("false original sixth candidate qualification")
    if not qualified:
        if response is not None:raise ValueError("unqualified source generated impulse")
        return True
    if (not isinstance(response,dict)
        or response.get("hypothetical_mathematics_only") is not True
        or response.get("selected_as_physical") is not False
        or response.get("post_sixth_motion_solved") is not False
        or response.get("original_source_face")!=face
        or response.get("original_source_corner")!=index):
        raise ValueError("source sixth result presented as physical motion")
    lever=r[0]*n[1]-r[1]*n[0]
    impulse=-2*arrival/(1+lever*lever/INERTIA)
    nextv=(h["velocity"][0]+impulse*n[0],
           h["velocity"][1]+impulse*n[1])
    nextw=h["spin"]+impulse*lever/INERTIA
    leaving=dot((nextv[0]-nextw*r[1],nextv[1]+nextw*r[0]),n)
    energy_before=.5*dot(h["velocity"],h["velocity"])+.5*INERTIA*h["spin"]**2
    energy_after=.5*dot(nextv,nextv)+.5*INERTIA*nextw**2
    if (not isfinite(impulse) or impulse<=0
        or abs(arrival+leaving)>CONSERVATION_TOL
        or abs(energy_before-energy_after)>CONSERVATION_TOL):
        raise ValueError("original frictionless normal law failed conservation")
    for name,value in (
        ("normal_impulse",impulse),
        ("incoming_contact_normal_rate",arrival),
        ("outgoing_contact_normal_rate",leaving),
        ("lever_cross_normal",lever),
        ("incoming_spin",h["spin"]),
        ("outgoing_spin",nextw),
        ("kinetic_energy_before",energy_before),
        ("kinetic_energy_after",energy_after)):
        if not isinstance(response.get(name),(float,int)) or abs(response[name]-value)>TOL:
            raise ValueError("independent sixth normal law differs: "+name)
    for key,want in (("incoming_velocity",h["velocity"]),("outgoing_velocity",nextv)):
        given=response.get(key)
        if not isinstance(given,list) or len(given)!=2 or any(
                abs(given[i]-want[i])>TOL for i in (0,1)):
            raise ValueError("original sixth vector mismatch: "+key)
    return True


class WORLD40Tests(unittest.TestCase):
    def test_all_source_cases_independently_satisfy_original_normal_law_or_refuse(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["original_sixth_model_candidates"],1)
        self.assertEqual(data["inactive_original_controls"],7)
        self.assertEqual(data["conditionally_qualified_sixth_responses"]+
                         data["unresolved_original_sixth_configurations"],1)
        self.assertEqual(data["real_sixth_impacts"],0)
        self.assertEqual(data["selected_sixth_impulses"],0)
        for item in data["cases"]:
            with self.subTest(angle=item["angle"]):
                self.assertTrue(verify(item))

    def test_unchanged_original_absent_sources_do_not_acquire_impulses(self):
        for angle in (0.,5.,12.25,20.):
            item=attempt(angle)
            self.assertIsNone(item["conditional_sixth_response"])

    def test_mutated_original_impulse_or_material_claim_fails_independent_witness(self):
        row=attempt(10.)
        for key,value in (
            ("measured_sixth_impact",True),
            ("sixth_response_selected_as_physical",True),
            ("post_sixth_continuation_admitted",True),
            ("new_receiver_constructed",True),
            ("outward_rounded_exact_contact_proof",True),
            ("original_24_by_6_world",[24.,24.])):
            fake=deepcopy(row);fake[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(fake)
        if row["conditional_sixth_response"] is not None:
            fake=deepcopy(row)
            fake["conditional_sixth_response"]["normal_impulse"]+=.2
            with self.assertRaises(ValueError):
                verify(fake)


if __name__=="__main__":
    unittest.main()
