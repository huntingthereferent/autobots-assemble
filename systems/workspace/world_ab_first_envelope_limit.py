"""WORLD31 — locate the first limit of existing original WORLD30 plane bounds.

Only source-owned WORLD29 hypothetical fourth response / WORLD30 original
24 signed-gap and outgoing-velocity envelopes. Calculate the largest initial
time prefix [0,t] for which EACH SAME ORIGINAL constraint retains its
conservative positive nominal separation. Keep the first limiting constraints
and exact original ancestry. Bound failure != geometric hit or fifth impulse.

No trajectory after a limit, no adaptive new receiver, no formal outward-
rounded root certificate, no real physical movement. The original two finite
face supporting lines and four world boundary planes remain unchanged.
"""
from __future__ import annotations

from math import isfinite

from systems.workspace.world_ab_post_fourth_local_clearance import (
    attempt as source30, SCHEMA as SOURCE30, WINDOW, MARGIN
)
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import ANGLES

SCHEMA="world-ab-source-first-conservative-envelope-limit/v1"
HORIZON=.25
BISECTION_ITERATIONS=54
TIME_TOLERANCE=4e-7
LIMIT_MARGIN=MARGIN


def sufficient(r,t):
    """The source30 Taylor inequality, with variable t, not a new contact law."""
    g=r["gap_at_candidate"]
    rate=r["outgoing_normal_rate"]
    curve=r["curvature_upper_bound"]
    if r["starts_at_qualified_contact"]:
        return abs(g)<=3e-6 and rate-curve*t > LIMIT_MARGIN
    return min(g,g+rate*t-curve*t*t/2)>LIMIT_MARGIN


def constraint_limit(r):
    if not sufficient(r,WINDOW):
        raise ValueError("original WORLD30 source did not verify its short window")
    if sufficient(r,HORIZON):
        return {
            "max_supported_prefix":HORIZON,
            "constraint_restricts_declared_horizon":False,
            "at_short_window":True,
            "at_declared_horizon":True,
        }
    left,right=WINDOW,HORIZON
    for _ in range(BISECTION_ITERATIONS):
        middle=(left+right)/2
        if sufficient(r,middle):
            left=middle
        else:
            right=middle
    return {
        "max_supported_prefix":float(left),
        "constraint_restricts_declared_horizon":True,
        "at_short_window":True,
        "at_declared_horizon":False,
    }


def attempt(angle):
    source=source30(angle)
    earlier=source29(angle)
    result={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial30_schema":SOURCE30,
        "source_trial30_status":source["status"],
        "original_source30_case":source,
        "source_trial29_schema":earlier["schema"],
        "source_trial29_status":earlier["status"],
        "source_qualified_fourth_response":earlier["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "source_original_minimum_horizon":WINDOW,
        "declared_followup_horizon":HORIZON,
        "positive_separation_margin":LIMIT_MARGIN,
        "original_24_halfplane_constraints":24,
        "same_original_two_finite_source_faces":True,
        "original_model_response_only":True,
        "physical_fourth_impulse_selected":False,
        "fifth_impulse_solved":False,
        "fifth_contact_feature_observed":False,
        "physical_trajectory_recorded":False,
        "exact_interval_arithmetic_certificate":False,
        "post_limit_continuation_admitted":False,
    }
    if earlier["conditional_fourth_response"] is None:
        if source["clearance_bounds"] or source["nominal_local_clearance_admitted"]:
            raise ValueError("unqualified prior response acquired motion")
        return {**result,
                "status":"NO_QUALIFIED_FOURTH_RESPONSE",
                "per_original_constraint_limits":[],
                "max_common_nominal_clearance_prefix":None,
                "first_limiting_constraints":[],
                "original_constraints_checked":0}
    if source["status"]!="CONDITIONAL_LOCAL_OUTGOING_SEPARATION":
        return {**result,
                "status":"ORIGINAL_SHORT_LOCAL_GEOMETRY_UNRESOLVED",
                "per_original_constraint_limits":[],
                "max_common_nominal_clearance_prefix":None,
                "first_limiting_constraints":[],
                "original_constraints_checked":0}
    records=source["clearance_bounds"]
    if len(records)!=24 or not all(r["accepted"] for r in records):
        raise ValueError("original WORLD30 qualification lost")
    entries=[]
    for r in records:
        lim=constraint_limit(r)
        entries.append({
            "source_plane":r["surface"],
            "source_corner_index":r["corner_index"],
            "source_starts_at_qualified_contact":r["starts_at_qualified_contact"],
            "original_gap_at_contact":r["gap_at_candidate"],
            "original_outgoing_normal_rate":r["outgoing_normal_rate"],
            "original_curvature_bound":r["curvature_upper_bound"],
            **lim,
        })
    minimum=min(r["max_supported_prefix"] for r in entries)
    limits=[r for r in entries if r["max_supported_prefix"]<=minimum+TIME_TOLERANCE
            and r["constraint_restricts_declared_horizon"]]
    status=("NOMINAL_CLEARANCE_THROUGH_DECLARED_HORIZON" if minimum==HORIZON
            else "FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT")
    if not isfinite(minimum) or minimum<WINDOW or minimum>HORIZON:
        raise ValueError("invalid original bounded nominal clearance prefix")
    return {**result,
            "status":status,"per_original_constraint_limits":entries,
            "max_common_nominal_clearance_prefix":float(minimum),
            "first_limiting_constraints":limits,
            "original_constraints_checked":len(entries)}


def run():
    records=[attempt(angle) for angle in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":records,
        "qualified_original_responses":sum(
            c["source_qualified_fourth_response"] is not None for c in records),
        "cases_clear_through_horizon":sum(
            c["status"]=="NOMINAL_CLEARANCE_THROUGH_DECLARED_HORIZON" for c in records),
        "cases_with_prior_envelope_limit":sum(
            c["status"]=="FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT" for c in records),
        "without_qualified_response":sum(
            c["status"]=="NO_QUALIFIED_FOURTH_RESPONSE" for c in records),
        "contact_features_solved":0,
        "fifth_impulses_computed":0,
        "real_material_measurements":0,
        "new_receivers_built":0,
        "new_engine_or_world":False,
    }
