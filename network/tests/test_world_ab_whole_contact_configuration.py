"""WORLD35 independent world-coordinate reconstruction and conditional-law witness.

Recalculate all 24 original plane/corner normal gaps, the selected incoming
corner, competing finite-face SAT, and the original unit-mass elastic response.
This is not an independent proof that a numerical root is exact or material.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin, hypot, isfinite
import unittest

from systems.workspace.world_ab_whole_contact_configuration import (
    attempt, run, SCHEMA, GAP_GUARD, ROOT_TOLERANCE, INWARD_RATE_GUARD,
    ENERGY_TOLERANCE,
)
from systems.workspace.world_ab_first_unknown_finite_feature import attempt as prior34
from network.tests.test_world_ab_first_unknown_finite_feature import verify as verify34
from systems.workspace.world_ab_first_finite_response_qualification import attempt as prior29
from systems.workspace.world_ab_third_contact import attempt as prior21, ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from network.tests.test_world_ab_finite_segment_square_overlap import sat_segment_square
from systems.workspace.world_ab_oblique_impact import HALF, INERTIA

CCW = ((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
SOURCE_CORNER_MAP=(0,3,1,2)
TOL=5e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def state(h,i,t):
    a,b=CCW[SOURCE_CORNER_MAP[i]]
    theta=h["theta"]+h["spin"]*t
    co,si=cos(theta),sin(theta)
    lever=(a*co-b*si,a*si+b*co)
    p=(h["center"][0]+h["velocity"][0]*t+lever[0],
       h["center"][1]+h["velocity"][1]*t+lever[1])
    velocity=(h["velocity"][0]-h["spin"]*lever[1],
              h["velocity"][1]+h["spin"]*lever[0])
    return p,lever,velocity


def reconstruct(row):
    angle=row.get("angle")
    if angle not in ANGLES or row.get("schema")!=SCHEMA:
        raise ValueError("source identity is missing")
    old=prior34(angle)
    if not verify34(old):
        raise ValueError("WORLD34 independent finite source witness invalid")
    unchanged={
        "source_trial34_status": old["status"],
        "original_first_unknown": old["source_first_unknown_subinterval"],
        "original_source_feature": old["unique_incoming_source_feature"],
        "original_24_by_6_world": [24.,6.],
        "original_static_finite_faces":2,
        "original_world_perimeter_planes":4,
        "conditional_fourth_response_unselected":True,
        "actual_material_fifth_contact_measured":False,
        "fifth_response_selected_as_physical":False,
        "post_fifth_continuation_admitted":False,
        "new_receiver_constructed":False,
        "formal_outward_rounded_contact_proof":False,
    }
    if any(row.get(k)!=v for k,v in unchanged.items()):
        raise ValueError("original source ancestry or physical refusal altered")
    if old["status"]!="FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED":
        if (row.get("status")!="NO_QUALIFIED_LOCAL_SOURCE_FEATURE"
            or row.get("candidate_virtual_time") is not None
            or row.get("same_original_plane_corner_bounds")!=[]
            or row.get("conditional_fifth_response") is not None
            or row.get("all_competing_original_constraints_clear") is not False):
            raise ValueError("unqualified source invented later movement")
        return True
    earlier=prior29(angle)
    source=prior21(angle)
    prev=earlier["qualifying_source_feature"]
    oldresponse=earlier["conditional_fourth_response"]
    if prev is None or oldresponse is None:
        raise ValueError("previous hypothetical response absent")
    h={"center":prev["contact_center"],"theta":prev["contact_angle"],
       "velocity":oldresponse["outgoing_velocity"],
       "spin":oldresponse["outgoing_spin"]}
    candidate=old["unique_incoming_source_feature"]
    chosen_face=candidate["source_face"]
    chosen_index=candidate["source_corner_index"]
    a=old["source_first_unknown_subinterval"]["start"]
    b=old["source_first_unknown_subinterval"]["end"]
    t=old["earliest_local_model_candidate"]["refined_model_transition_time"]
    if (row.get("candidate_virtual_time")!=t or not a<t<b<=.25
        or row.get("source_face")!=chosen_face
        or row.get("candidate_corner")!=chosen_index):
        raise ValueError("source first finite feature changed")
    planes=original_planes(source,angle)
    if len(planes)!=6:raise ValueError("original planes missing")
    rows=row.get("same_original_plane_corner_bounds")
    if not isinstance(rows,list) or len(rows)!=24:
        raise ValueError("all original 24 plane-corner records required")
    expected=[]
    for name,n,anchor,span in planes:
        ratebound=abs(dot(h["velocity"],n))+abs(h["spin"])*hypot(HALF,HALF)
        for i in range(4):
            before,_,_=state(h,i,a)
            after,_,_=state(h,i,t)
            g0=dot((before[0]-anchor[0],before[1]-anchor[1]),n)
            gt=dot((after[0]-anchor[0],after[1]-anchor[1]),n)
            selected=name==chosen_face and i==chosen_index
            surplus=g0-ratebound*(t-a)-GAP_GUARD
            expected.append((name,i,selected,span is not None,g0,gt,ratebound,
                             surplus,None if selected else surplus>0))
    for got,want in zip(rows,expected):
        name,i,selected,finite,g0,gt,bound,surplus,sufficient=want
        if (got.get("source_plane")!=name
            or got.get("source_corner_index")!=i
            or got.get("selected_candidate_corner") is not selected
            or got.get("original_plane_finite") is not finite
            or got.get("separation_sufficient_before_candidate") is not sufficient):
            raise ValueError("original competing halfplane constraints changed")
        for key,value in (("gap_at_last_supported_time",g0),
                          ("gap_at_candidate_pose",gt),
                          ("fixed_normal_speed_upper_bound",bound),
                          ("whole_precontact_interval_lower_surplus",surplus)):
            if not isinstance(got.get(key),(float,int)) or abs(got[key]-value)>TOL:
                raise ValueError("world-coordinate independent corner mismatch "+key)
    no_competition=all(w[-1] is True for w in expected if not w[2])
    if row.get("all_competing_original_constraints_clear") is not no_competition:
        raise ValueError("unverified competing source constraint suppressed")
    selected=next((x for x in planes if x[0]==chosen_face and x[3] is not None),None)
    if selected is None:raise ValueError("source finite original face replaced")
    _,n,anchor,span=selected
    p,r,v=state(h,chosen_index,t)
    p0,_,v0=state(h,chosen_index,a)
    tangent=(-n[1],n[0])
    gap=dot((p[0]-anchor[0],p[1]-anchor[1]),n)
    along=dot((p[0]-anchor[0],p[1]-anchor[1]),tangent)
    inward=dot(v,n)
    upper=dot(v0,n)+h["spin"]**2*hypot(HALF,HALF)*(t-a)
    if (row.get("selected_corner_inward_rate_upper_bound") is None or
        abs(row["selected_corner_inward_rate_upper_bound"]-upper)>TOL):
        raise ValueError("source inbound entire-prefix rate unsupported")
    consistent=(abs(gap)<=ROOT_TOLERANCE
                and abs(along)<span/2-ROOT_TOLERANCE
                and abs(along-candidate["finite_face_tangent_coordinate"])<=ROOT_TOLERANCE
                and abs(inward-candidate["incoming_normal_rate"])<=ROOT_TOLERANCE
                and all(abs(x-y)<=ROOT_TOLERANCE for x,y in zip(p,candidate["contact_model_position"]))
                and dot((p0[0]-anchor[0],p0[1]-anchor[1]),n)>GAP_GUARD
                and inward<-INWARD_RATE_GUARD
                and upper<-INWARD_RATE_GUARD)
    if row.get("source_feature_geometry_consistent") is not consistent:
        raise ValueError("source first incoming finite corner unsupported")
    competitors=[]
    for other_name,other_n,other_anchor,other_span in planes:
        if other_name==chosen_face or other_span is None:continue
        tangent=(-other_n[1],other_n[0])
        segment=[[other_anchor[0]-other_span*tangent[0]/2,other_anchor[1]-other_span*tangent[1]/2],
                 [other_anchor[0]+other_span*tangent[0]/2,other_anchor[1]+other_span*tangent[1]/2]]
        model={"contact_center":h["center"],"contact_orientation":h["theta"],
               "outgoing_velocity":h["velocity"],"outgoing_spin":h["spin"]}
        competitors.append(sat_segment_square(model,segment,t))
    other_overlap=any(competitors)
    if row.get("other_finite_face_intersects_at_candidate") is not other_overlap:
        raise ValueError("independent finite SAT found different competing face")
    qualified=consistent and no_competition and not other_overlap
    status=("CONDITIONAL_FIFTH_RESPONSE_MATHEMATICALLY_QUALIFIED" if qualified
            else "ORIGINAL_CONTACT_CONFIGURATION_UNRESOLVED")
    if row.get("status")!=status:raise ValueError("physical/mathematical status inflated")
    response=row.get("conditional_fifth_response")
    if not qualified:
        if response is not None:raise ValueError("unqualified source invented fifth impulse")
        return True
    if response is None or response.get("mathematical_counterfactual_only") is not True or (
        response.get("selected_as_physical") is not False
        or response.get("post_response_motion_solved") is not False):
        raise ValueError("conditional result falsely represented as physical")
    # Independently reconstruct original unit mass, restitution 1, frictionless law.
    lever=r[0]*n[1]-r[1]*n[0]
    impulse=-2*inward/(1+lever**2/INERTIA)
    vnext=(h["velocity"][0]+impulse*n[0],h["velocity"][1]+impulse*n[1])
    wnext=h["spin"]+impulse*lever/INERTIA
    departing=dot((vnext[0]-wnext*r[1],vnext[1]+wnext*r[0]),n)
    initialenergy=.5*dot(h["velocity"],h["velocity"])+.5*INERTIA*h["spin"]**2
    finalenergy=.5*dot(vnext,vnext)+.5*INERTIA*wnext**2
    if (not isfinite(impulse) or impulse<=0
        or abs(inward+departing)>ENERGY_TOLERANCE
        or abs(initialenergy-finalenergy)>ENERGY_TOLERANCE):
        raise ValueError("original energy/contact equation invalid")
    for k,want in (("normal_impulse",impulse),("outgoing_spin",wnext),
                   ("incoming_contact_normal_rate",inward),
                   ("outgoing_contact_normal_rate",departing),
                   ("kinetic_energy_before",initialenergy),
                   ("kinetic_energy_after",finalenergy)):
        if not isinstance(response.get(k),(float,int)) or abs(response[k]-want)>TOL:
            raise ValueError("original ideal response mismatches independent formula: "+k)
    for got,want in zip(response["outgoing_velocity"],vnext):
        if abs(got-want)>TOL:raise ValueError("independent fifth outgoing vector disagrees")
    return True


class World35Tests(unittest.TestCase):
    def test_full_source_cases_have_independent_geometry_and_law_witness(self):
        result=run()
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["original_local_candidate_cases"],1)
        self.assertEqual(result["inactive_source_controls"],7)
        self.assertEqual(result["actual_fifth_contacts_measured"],0)
        self.assertEqual(result["physical_fifth_responses_selected"],0)
        self.assertEqual(result["conditionally_qualified_fifth_responses"]+
                         result["original_configuration_unresolved_cases"],1)
        for row in result["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(reconstruct(row))

    def test_inactive_original_controls_cannot_gain_fifth_response(self):
        for angle in (0.,5.,12.25,20.):
            self.assertIsNone(attempt(angle)["conditional_fifth_response"])

    def test_false_material_claim_and_synthetic_competitor_refused(self):
        row=attempt(10.)
        for key,value in (("actual_material_fifth_contact_measured",True),
                          ("fifth_response_selected_as_physical",True),
                          ("post_fifth_continuation_admitted",True),
                          ("new_receiver_constructed",True),
                          ("formal_outward_rounded_contact_proof",True),
                          ("original_24_by_6_world",[24.,24.])):
            forged=deepcopy(row);forged[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                reconstruct(forged)
        fake=deepcopy(row)
        fake["same_original_plane_corner_bounds"][0]["gap_at_candidate_pose"]+=.1
        with self.assertRaises(ValueError):reconstruct(fake)
        if row["conditional_fifth_response"] is not None:
            fake=deepcopy(row);fake["conditional_fifth_response"]["normal_impulse"]+=.2
            with self.assertRaises(ValueError):reconstruct(fake)


if __name__=="__main__":
    unittest.main()
