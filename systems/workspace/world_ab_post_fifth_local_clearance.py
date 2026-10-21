"""WORLD36 — short original-plane clearance after UNSELECTED fifth response.

The only eligible input is WORLD35's independent-model-qualified candidate.
Re-use its exact hypothetical fifth response and original 24x6 world. For each
original vertex and six original supporting planes, test a conservative
Taylor lower bound over [0, 0.008] virtual-time after the candidate. A failed
inequality is UNKNOWN, not sixth contact. No receiver or real motion.
"""
from __future__ import annotations

from math import cos, sin, hypot, isfinite

from systems.workspace.world_ab_whole_contact_configuration import (
    attempt as source35, SCHEMA as SOURCE35,
)
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA = "world-ab-fifth-hypothetical-response-local-clearance/v1"
WINDOW = .008
MARGIN = 1e-5
CONTACT_TOL = 3e-6
VERTICES = ((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):
    return round(float(x), 10)


def dot(a, b):
    return a[0]*b[0]+a[1]*b[1]


def rotate(p, theta):
    c,s=cos(theta),sin(theta)
    return (c*p[0]-s*p[1],s*p[0]+c*p[1])


def bound(center, theta, v, spin, index, normal, anchor, selected):
    offset=rotate(VERTICES[index],theta)
    point=(center[0]+offset[0],center[1]+offset[1])
    gap=dot((point[0]-anchor[0],point[1]-anchor[1]),normal)
    velocity=(v[0]-spin*offset[1],v[1]+spin*offset[0])
    rate=dot(velocity,normal)
    curvature=spin*spin*hypot(HALF,HALF)
    endpoint_lower=gap+rate*WINDOW-.5*curvature*WINDOW*WINDOW
    outgoing_rate_lower=rate-curvature*WINDOW
    if selected:
        supported=abs(gap)<=CONTACT_TOL and outgoing_rate_lower>MARGIN
        reason=("QUALIFIED_OUTGOING_CONTACT_NORMAL_RATE" if supported else
                "CONTACT_DEPARTURE_UNRESOLVED")
        lower=outgoing_rate_lower
    else:
        lower=min(gap,endpoint_lower)
        supported=lower>MARGIN
        reason=("OTHER_ORIGINAL_CORNER_POSITIVE_CLEARANCE" if supported else
                "OTHER_ORIGINAL_CORNER_CLEARANCE_UNRESOLVED")
    return {
        "source_corner_index":index,
        "selected_source_contact":bool(selected),
        "gap_at_hypothetical_fifth":rd(gap),
        "outgoing_normal_rate":rd(rate),
        "curvature_upper_bound":rd(curvature),
        "end_gap_taylor_lower_bound":rd(endpoint_lower),
        "outgoing_rate_lower_bound":rd(outgoing_rate_lower),
        "conservative_lower_bound":rd(lower),
        "interval_supported":bool(supported),
        "classification":reason,
        "material_contact_observed":False,
    }


def attempt(angle):
    prior=source35(angle)
    fourth=source29(angle)
    ancestor=source21(angle)
    base={
        "schema":SCHEMA, "angle":float(angle),
        "source_trial35_schema":SOURCE35,
        "source_trial35_status":prior["status"],
        "original_trial35_conditional_response":prior["conditional_fifth_response"],
        "original_source_candidate_time":prior["candidate_virtual_time"],
        "original_24_by_6_world":[24.,6.],
        "original_finite_faces":2,
        "original_world_boundaries":4,
        "declared_local_horizon":WINDOW,
        "positive_clearance_guard":MARGIN,
        "source_model_only":True,
        "physical_fifth_impact_selected":False,
        "sixth_impact_measured":False,
        "sixth_impulse_calculated":False,
        "post_window_continuation_admitted":False,
        "new_receiver_created":False,
        "outward_rounded_interval_certificate":False,
    }
    empty={
        "same_original_24_constraints":[],
        "supported_original_constraints":0,
        "unresolved_original_constraints":0,
        "nominal_clearance_covered":False,
        "conditional_fifth_contact_center":None,
        "conditional_fifth_contact_orientation":None,
        "source_selected_face":None,
        "source_selected_corner":None,
    }
    if prior["conditional_fifth_response"] is None:
        if prior["status"]!="NO_QUALIFIED_LOCAL_SOURCE_FEATURE" and prior["status"]!="ORIGINAL_CONTACT_CONFIGURATION_UNRESOLVED":
            raise ValueError("source fifth response/qualification mismatch")
        return {**base,**empty,"status":"NO_QUALIFIED_FIFTH_RESPONSE"}
    if prior["status"]!="CONDITIONAL_FIFTH_RESPONSE_MATHEMATICALLY_QUALIFIED":
        raise ValueError("conditional fifth response without qualified source")
    parent=fourth["qualifying_source_feature"]
    fourth_response=fourth["conditional_fourth_response"]
    t=prior["candidate_virtual_time"]
    fifth=prior["conditional_fifth_response"]
    if (parent is None or fourth_response is None or not isfinite(t)
        or t<=0 or t>=.25 or fifth["selected_as_physical"] is not False
        or fifth["mathematical_counterfactual_only"] is not True):
        raise ValueError("original hypothetical fifth source record invalid")
    center=(parent["contact_center"][0]+fourth_response["outgoing_velocity"][0]*t,
            parent["contact_center"][1]+fourth_response["outgoing_velocity"][1]*t)
    theta=parent["contact_angle"]+fourth_response["outgoing_spin"]*t
    v=tuple(fifth["outgoing_velocity"])
    spin=fifth["outgoing_spin"]
    if not all(isfinite(q) for q in (*center,theta,*v,spin)):
        raise ValueError("source fifth mathematical pose nonfinite")
    planes=list(surfaces(ancestor,angle))
    if len(planes)!=6 or sum(span is not None for _,_,_,span in planes)!=2:
        raise ValueError("original source world plane set missing")
    entries=[]
    for name,n,anchor,span in planes:
        for index in range(4):
            selected=name==prior["source_face"] and index==prior["candidate_corner"]
            result=bound(center,theta,v,spin,index,tuple(n),tuple(anchor),selected)
            entries.append({"source_plane":name, "original_plane_is_finite":span is not None,
                            **result})
    if len(entries)!=24 or sum(x["selected_source_contact"] for x in entries)!=1:
        raise ValueError("original selected finite source contact changed")
    good=sum(x["interval_supported"] for x in entries)
    status=("CONDITIONAL_FIFTH_LOCAL_CLEARANCE_NOMINALLY_SUPPORTED" if good==24
            else "POST_FIFTH_LOCAL_SEPARATION_INEQUALITIES_UNRESOLVED")
    return {
        **base, "status":status,
        "same_original_24_constraints":entries,
        "supported_original_constraints":good,
        "unresolved_original_constraints":24-good,
        "nominal_clearance_covered":good==24,
        "conditional_fifth_contact_center":[rd(x) for x in center],
        "conditional_fifth_contact_orientation":rd(theta),
        "source_selected_face":prior["source_face"],
        "source_selected_corner":prior["candidate_corner"],
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "original_conditional_fifth_responses":sum(
            x["original_trial35_conditional_response"] is not None for x in cases),
        "nominal_short_clearance_cases":sum(
            x["status"]=="CONDITIONAL_FIFTH_LOCAL_CLEARANCE_NOMINALLY_SUPPORTED" for x in cases),
        "locally_unresolved_cases":sum(
            x["status"]=="POST_FIFTH_LOCAL_SEPARATION_INEQUALITIES_UNRESOLVED" for x in cases),
        "without_qualified_fifth_response":sum(
            x["status"]=="NO_QUALIFIED_FIFTH_RESPONSE" for x in cases),
        "physical_fifth_impacts":0,"sixth_impulses":0,
        "new_receivers":0,"new_world_or_engine":False,
    }
