"""WORLD35: independently test whole original contact configuration at WORLD34 finite onset.

Only the 10-degree case with a WORLD34 first-unknown finite overlap bracket can
enter. Reuse the same 24x6 world, two finite source segments, four perimeter
planes and the unselected WORLD29 fourth-response hypothesis. A finite model
corner at one instant is not, by itself, the next physical impact.

Bound all other original corner/plane gaps continuously from the WORLD33
supported prefix up to the candidate with a rigid-vertex speed envelope.
Check the selected vertex is inward throughout that tiny interval and that
the other finite face is not intersecting at the candidate. Then, and only
then, evaluate the ORIGINAL ideal frictionless elastic normal-response law as
a conditional mathematical fifth response. Never select it as physical.
"""
from __future__ import annotations

from math import cos, sin, hypot, isfinite
from systems.workspace.world_ab_first_unknown_finite_feature import attempt as source34
from systems.workspace.world_ab_local_plane_prefix import attempt as source33
from systems.workspace.world_ab_first_finite_response_qualification import (
    attempt as source29, ideal_response,
)
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_finite_segment_square_overlap import static_faces, finite_clip
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA = "world-ab-whole-original-finite-contact-configuration/v1"
GAP_GUARD = 1e-8
ROOT_TOLERANCE = 3e-6
INWARD_RATE_GUARD = 1e-5
ENERGY_TOLERANCE = 3e-7
RADIUS = hypot(HALF, HALF)
VERTICES = ((-HALF, -HALF), (-HALF, HALF), (HALF, -HALF), (HALF, HALF))


def rd(x):
    return round(float(x), 12)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def rigid_vertex(h, index, t):
    a, b = VERTICES[index]
    theta = h["theta"] + h["spin"] * t
    co, si = cos(theta), sin(theta)
    lever = (co * a - si * b, si * a + co * b)
    p = (h["center"][0] + h["velocity"][0] * t + lever[0],
         h["center"][1] + h["velocity"][1] * t + lever[1])
    v = (h["velocity"][0] - h["spin"] * lever[1],
         h["velocity"][1] + h["spin"] * lever[0])
    return p, lever, v


def original_model(previous, response):
    return {
        "center": list(previous["contact_center"]),
        "theta": previous["contact_angle"],
        "velocity": list(response["outgoing_velocity"]),
        "spin": response["outgoing_spin"],
    }


def attempt(angle):
    old = source34(angle)
    earlier = source33(angle)
    prior = source29(angle)
    ancestor = source21(angle)
    base = {
        "schema": SCHEMA,
        "angle": float(angle),
        "source_trial34_status": old["status"],
        "original_first_unknown": old["source_first_unknown_subinterval"],
        "original_source_feature": old["unique_incoming_source_feature"],
        "original_24_by_6_world": [24., 6.],
        "original_static_finite_faces": 2,
        "original_world_perimeter_planes": 4,
        "conditional_fourth_response_unselected": True,
        "actual_material_fifth_contact_measured": False,
        "fifth_response_selected_as_physical": False,
        "post_fifth_continuation_admitted": False,
        "new_receiver_constructed": False,
        "formal_outward_rounded_contact_proof": False,
    }
    empty = {
        "candidate_virtual_time": None,
        "source_face": None,
        "candidate_corner": None,
        "same_original_plane_corner_bounds": [],
        "other_finite_face_intersects_at_candidate": None,
        "selected_corner_inward_rate_upper_bound": None,
        "source_feature_geometry_consistent": False,
        "all_competing_original_constraints_clear": False,
        "conditional_fifth_response": None,
    }
    if old["status"] != "FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED":
        return {**base, **empty, "status": "NO_QUALIFIED_LOCAL_SOURCE_FEATURE"}
    feature = old["unique_incoming_source_feature"]
    first = old["earliest_local_model_candidate"]
    if feature is None or first is None or earlier["first_unknown_subinterval"] is None:
        raise ValueError("qualified original WORLD34 feature ancestry missing")
    if prior["conditional_fourth_response"] is None or prior["qualifying_source_feature"] is None:
        raise ValueError("no original fourth response hypothesis")
    lo = earlier["first_unknown_subinterval"]["start"]
    hi = earlier["first_unknown_subinterval"]["end"]
    t = first["refined_model_transition_time"]
    if not (isfinite(t) and 0 <= lo < t < hi <= .25):
        raise ValueError("unbounded or changed original first unknown interval")
    h = original_model(prior["qualifying_source_feature"],
                       prior["conditional_fourth_response"])
    face, corner = feature["source_face"], feature["source_corner_index"]
    definitions = list(surfaces(ancestor, angle))
    matches = [(n, anchor, span) for label, n, anchor, span in definitions
               if label == face and span is not None]
    if len(definitions) != 6 or len(matches) != 1 or corner not in range(4):
        raise ValueError("original six planes or finite candidate source changed")
    n, anchor, span = matches[0]
    n = tuple(n)
    anchor = tuple(anchor)
    tangent = (-n[1], n[0])
    selected_position, lever, velocity = rigid_vertex(h, corner, t)
    d = (selected_position[0] - anchor[0], selected_position[1] - anchor[1])
    gap = dot(d, n)
    along = dot(d, tangent)
    incoming = dot(velocity, n)
    p0, _, v0 = rigid_vertex(h, corner, lo)
    starting_gap = dot((p0[0] - anchor[0], p0[1] - anchor[1]), n)
    outgoing_curvature_upper = h["spin"] ** 2 * RADIUS
    upper_inward_rate = dot(v0, n) + outgoing_curvature_upper * (t - lo)
    accurate = (
        abs(gap) <= ROOT_TOLERANCE
        and abs(along) < span / 2 - ROOT_TOLERANCE
        and abs(along - feature["finite_face_tangent_coordinate"]) <= ROOT_TOLERANCE
        and abs(incoming - feature["incoming_normal_rate"]) <= ROOT_TOLERANCE
        and all(abs(x-y) <= ROOT_TOLERANCE for x,y in
                zip(selected_position, feature["contact_model_position"]))
        and starting_gap > GAP_GUARD
        and upper_inward_rate < -INWARD_RATE_GUARD
        and incoming < -INWARD_RATE_GUARD
    )
    records = []
    for label, normal, plane_anchor, plane_span in definitions:
        nn = tuple(normal)
        aa = tuple(plane_anchor)
        # Bound a fixed plane's normal gap for each original vertex on [lo,t].
        max_rate = abs(dot(h["velocity"], nn)) + abs(h["spin"]) * RADIUS
        for index in range(4):
            start, _, _ = rigid_vertex(h, index, lo)
            end, _, _ = rigid_vertex(h, index, t)
            g0 = dot((start[0]-aa[0], start[1]-aa[1]), nn)
            gt = dot((end[0]-aa[0], end[1]-aa[1]), nn)
            chosen = label == face and index == corner
            surplus = g0 - max_rate * (t-lo) - GAP_GUARD
            records.append({
                "source_plane": label,
                "source_corner_index": index,
                "selected_candidate_corner": chosen,
                "original_plane_finite": plane_span is not None,
                "gap_at_last_supported_time": rd(g0),
                "gap_at_candidate_pose": rd(gt),
                "fixed_normal_speed_upper_bound": rd(max_rate),
                "whole_precontact_interval_lower_surplus": rd(surplus),
                "separation_sufficient_before_candidate": (None if chosen else surplus > 0),
            })
    if len(records) != 24 or sum(x["selected_candidate_corner"] for x in records) != 1:
        raise ValueError("original world plane/corner coverage changed")
    no_competing_planes = all(
        x["separation_sufficient_before_candidate"] is True
        for x in records if not x["selected_candidate_corner"]
    )
    original_faces = static_faces(ancestor, angle)
    if len(original_faces) != 2 or set(x[0] for x in original_faces) !=             {x[0] for x in definitions if x[3] is not None}:
        raise ValueError("original finite source segments were substituted")
    other_face_intersection = any(
        finite_clip({
            "contact_center": h["center"],
            "contact_orientation": h["theta"],
            "outgoing_velocity": h["velocity"],
            "outgoing_spin": h["spin"],
        }, segment, t)["overlap"]
        for name, segment in original_faces if name != face
    )
    qualified = accurate and no_competing_planes and not other_face_intersection
    response = None
    if qualified:
        response = ideal_response(h["velocity"], h["spin"], lever, n)
        if not (all(isfinite(x) for x in (
                response["normal_impulse"], *response["outgoing_velocity"],
                response["outgoing_spin"]))
                and response["normal_impulse"] > 0
                and abs(response["incoming_contact_normal_rate"] + response[
                    "outgoing_contact_normal_rate"]) <= ENERGY_TOLERANCE
                and abs(response["kinetic_energy_before"] -
                        response["kinetic_energy_after"]) <= ENERGY_TOLERANCE):
            raise ValueError("original elastic normal-response controls failed")
        response = {**response, "mathematical_counterfactual_only": True,
                    "selected_as_physical": False, "post_response_motion_solved": False}
    return {
        **base, "status": (
            "CONDITIONAL_FIFTH_RESPONSE_MATHEMATICALLY_QUALIFIED" if qualified
            else "ORIGINAL_CONTACT_CONFIGURATION_UNRESOLVED"),
        "candidate_virtual_time": t, "source_face": face, "candidate_corner": corner,
        "same_original_plane_corner_bounds": records,
        "other_finite_face_intersects_at_candidate": other_face_intersection,
        "selected_corner_inward_rate_upper_bound": rd(upper_inward_rate),
        "source_feature_geometry_consistent": accurate,
        "all_competing_original_constraints_clear": no_competing_planes,
        "conditional_fifth_response": response,
    }


def run():
    cases = [attempt(a) for a in ANGLES]
    return {
        "schema": SCHEMA, "angles": list(ANGLES), "cases": cases,
        "original_local_candidate_cases": sum(x["candidate_virtual_time"] is not None for x in cases),
        "conditionally_qualified_fifth_responses": sum(x["conditional_fifth_response"] is not None for x in cases),
        "original_configuration_unresolved_cases": sum(x["status"] == "ORIGINAL_CONTACT_CONFIGURATION_UNRESOLVED" for x in cases),
        "inactive_source_controls": sum(x["status"] == "NO_QUALIFIED_LOCAL_SOURCE_FEATURE" for x in cases),
        "actual_fifth_contacts_measured": 0,
        "physical_fifth_responses_selected": 0,
        "new_receivers_created": 0,
        "general_world_engine_built": False,
    }
