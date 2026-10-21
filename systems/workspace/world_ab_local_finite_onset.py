"""WORLD28: locally refine FIRST detected finite overlap, not later motion.

Trial25 supplies the original first grid transition for each existing finite
source face. Trial26 supplies sufficient nominal separation for intervals before
that transition. Refine *only* the first local onset using a signed SAT margin
and compare source-owned Trial23 vertex times on the SAME finite face.

The refinement is an ordinary-float numerical bracket under a HYPOTHETICAL
third-impulse ballistic projection. It neither certifies exact first contact
nor selects a fourth impulse, receiver, post-contact path or material outcome.
"""
from __future__ import annotations

from math import isfinite
from systems.workspace.world_ab_finite_segment_square_overlap import attempt as source25
from systems.workspace.world_ab_between_sample_clearance import (
    attempt as source26, nominal_margin, START, DURATION, SAMPLE_COUNT
)
from systems.workspace.world_ab_all_inward_finite_features import attempt as source23
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES

SCHEMA = "world-ab-local-first-finite-onset-refinement/v1"
TOL = 3e-7


def refine(h,face,bracket):
    low=bracket["last_grid_separated_at"]
    high=bracket["first_grid_intersection_at"]
    if not (START <= low < high <= DURATION):
        raise ValueError("invalid original WORLD25 finite onset bracket")
    a=nominal_margin(h,face,low)
    b=nominal_margin(h,face,high)
    if not isfinite(a) or not isfinite(b) or a<=-1e-7 or b>1e-7:
        raise ValueError("original nominal SAT signs do not bracket onset")
    for _ in range(58):
        m=(low+high)/2
        if nominal_margin(h,face,m)>0:
            low=m
        else:
            high=m
    return {"last_nominally_separated_time":round(low,12),
            "first_nominally_intersecting_time":round(high,12),
            "signed_sat_margin_at_left":round(nominal_margin(h,face,low),12),
            "signed_sat_margin_at_right":round(nominal_margin(h,face,high),12),
            "numeric_bracket_only":True,
            "physically_witnessed":False}


def attempt(angle):
    old25=source25(angle)
    old26=source26(angle)
    old23=source23(angle)
    original=source21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial25_schema":old25["schema"],
        "source_trial25_status":old25["status"],
        "source_trial26_schema":old26["schema"],
        "source_trial26_status":old26["status"],
        "source_trial23_schema":old23["schema"],
        "source_original_third_impulse":original["third_impulse"],
        "original_window":[START,DURATION],
        "original_sample_intervals":SAMPLE_COUNT,
        "finite_source_faces_unchanged":True,
        "nominal_conditional_motion_only":True,
        "certified_exact_root":False,
        "material_measurements":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "post_candidate_motion_solved":False,
    }
    if original["third_impulse"] is None:
        if old25["face_results"] or old26["face_clearance_bounds"]:
            raise ValueError("original control acquired an unsupported face")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "face_first_onsets":[],"first_eligible_finite_onset":None,
                "cases_with_earlier_unknown_clear_sample_gaps":0}
    if not (len(old25["face_results"])==
            len(old26["face_clearance_bounds"])==2):
        raise ValueError("original finite source face count changed")
    results=[]
    unresolved_earlier=0
    for prior,limits in zip(old25["face_results"],old26["face_clearance_bounds"]):
        if prior["face"]!=limits["face"] or prior["segment"]!=limits["segment"]:
            raise ValueError("original source geometry changed")
        first=prior["first_transition_bracket"]
        if first is None:
            continue
        onset_index=prior["sampled_intersection_windows"][0]["first_sample_index"]
        if onset_index<=0:
            results.append({"face":prior["face"],"status":"FIRST_FRAME_ALREADY_INTERSECTING",
                            "original_grid_bracket":None,"refined_sat_bracket":None,
                            "same_face_first_vertex_candidate_time":None,
                            "local_vertex_time_consistent":False,
                            "uncleared_intervals_before_onset":None})
            continue
        unknown={x["interval_index"] for x in limits["uncovered_intervals"]}
        earlier=sorted(i for i in unknown if i<onset_index-1)
        unresolved_earlier+=int(bool(earlier))
        root=refine(original["third_impulse"],prior["segment"],first)
        vertex=[
            x["dt_after_third_impulse"] for x in old23["eligible_geometry_roots"]
            if x["surface"]==prior["face"] and
               x["feature_classification"]=="FINITE_FACE_INTERIOR_CANDIDATE"
        ]
        source_first=min(vertex) if vertex else None
        near=(source_first is not None and
              abs(source_first-root["first_nominally_intersecting_time"])<=TOL)
        status=("EARLIER_CLEAR_ENDPOINT_GAP_NOT_CERTIFIED" if earlier else
                "NUMERIC_FINITE_ONSET_ALIGNS_WITH_VERTEX_SOURCE" if near else
                "NUMERIC_FINITE_ONSET_FEATURE_UNRESOLVED")
        results.append({
            "face":prior["face"],"status":status,
            "original_grid_bracket":first,
            "refined_sat_bracket":root,
            "same_face_first_vertex_candidate_time":source_first,
            "local_vertex_time_consistent":near,
            "uncleared_intervals_before_onset":earlier,
            "source_after_first_contact_counterfactual":True,
        })
    eligible=[x for x in results if x["refined_sat_bracket"] is not None]
    eligible.sort(key=lambda x:(
        x["refined_sat_bracket"]["first_nominally_intersecting_time"],x["face"]))
    first=eligible[0] if eligible else None
    if not results:
        state="NO_SAMPLED_FINITE_ONSET_IN_ORIGINAL_WINDOW"
    elif unresolved_earlier:
        state="SOURCE_EARLIER_INTERVALS_REMAIN_UNRESOLVED"
    elif first and first["local_vertex_time_consistent"]:
        state="FIRST_NUMERICAL_FINITE_ONSET_CORROBORATED_BY_VERTEX"
    else:
        state="FIRST_NUMERICAL_FINITE_ONSET_FEATURE_UNRESOLVED"
    return {**base,"status":state,"face_first_onsets":results,
            "first_eligible_finite_onset":first,
            "cases_with_earlier_unknown_clear_sample_gaps":unresolved_earlier}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "admitted_third_impulse_cases":sum(
                x["source_original_third_impulse"] is not None for x in cases),
            "no_source_impulse_controls":sum(
                x["status"]=="NO_ADMITTED_THIRD_IMPULSE" for x in cases),
            "cases_with_numeric_first_finite_onset":sum(
                x["first_eligible_finite_onset"] is not None for x in cases),
            "cases_with_vertex_corrobated_onset":sum(
                x["status"]=="FIRST_NUMERICAL_FINITE_ONSET_CORROBORATED_BY_VERTEX"
                for x in cases),
            "earlier_clear_endpoint_uncertainty_cases":sum(
                x["cases_with_earlier_unknown_clear_sample_gaps"]>0 for x in cases),
            "actual_material_contacts_measured":0,"fourth_impulses_solved":0,
            "real_receivers_built":0,"new_world_or_engine":False}
