"""WORLD Trial 15: same motion-derived construction with different body support.

A disc and an axis-aligned, fixed-orientation square move by the SAME
frictionless translational contact map inside the original finite WORLD.
Only their mathematical support against a face differs. The square has an
explicit orientation constraint; this is NOT free rigid-body square dynamics.

No engine, shape classification system, Earth material calibration, or
multicontact selection. A finite source miss makes no new object.
"""
from __future__ import annotations

from math import cos, sin, radians, hypot, isfinite

from systems.workspace.world_ab_oblique_rotation import (
    START, VELOCITY, SOURCE, R, SPAN, PROJECTION, FOOTPRINT,
)

SCHEMA = "world-ab-body-support-construction/v1"
BODIES = ("disc", "fixed-square")
ANGLES = (0., 7.5, 12.25, 20.)
POST_CONTACT = .1
EPS = 1e-8


def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]


def add(a, b):
    return (a[0]+b[0], a[1]+b[1])


def sub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def scale(x, a):
    return (x*a[0], x*a[1])


def rd(x):
    return round(float(x), 10)


def support(body, normal):
    """Support distance from body centre to its tangent plane."""
    if body not in BODIES:
        raise ValueError("only these two bounded test bodies are admitted")
    return R if body == "disc" else R*(abs(normal[0])+abs(normal[1]))


def contact_offset(body, n):
    if body == "disc":
        return scale(-R, n)
    if body != "fixed-square":
        raise ValueError("unknown bounded body")
    # One point on the square's support face. For zero components its
    # midpoint is selected, not a claim of a unique material contact point.
    return tuple(-R * (1 if z > EPS else -1 if z < -EPS else 0) for z in n)


def segment(identity, anchor, n):
    tangent = (-n[1], n[0])
    endpoints = [add(anchor, scale(k * SPAN/2, tangent)) for k in (-1, 1)]
    if any(not (0 <= point[0] <= FOOTPRINT[0] and
                0 <= point[1] <= FOOTPRINT[1]) for point in endpoints):
        raise ValueError("surface not inside original WORLD")
    return {
        "id": identity,
        "anchor": [rd(z) for z in anchor],
        "normal": [rd(z) for z in n],
        "endpoints": [[rd(z) for z in p] for p in endpoints],
    }


def trial(body, *, angle=0., anchor=SOURCE):
    if body not in BODIES:
        raise ValueError("unsupported object; no implicit body solver")
    if type(angle) not in (int, float) or not isfinite(angle) or abs(angle) > 40:
        raise ValueError("angle outside bounded original test region")
    if not isinstance(anchor, (tuple, list)) or len(anchor) != 2 or any(
        type(v) not in (int,float) or not isfinite(v) for v in anchor
    ):
        raise ValueError("finite source anchor pair required")
    anchor = (float(anchor[0]), float(anchor[1]))
    if not (7 <= anchor[0] <= 16 and .75 <= anchor[1] <= 5.25):
        raise ValueError("source anchor outside bounded WORLD trial")

    n = (-cos(radians(angle)), -sin(radians(angle)))
    source = segment("original-test-source", anchor, n)
    initial = tuple(START)
    vin = tuple(VELOCITY)
    width = support(body, n)
    rate = dot(vin, n)
    if rate >= -EPS:
        raise ValueError("source is not approached")
    t1 = (width - dot(sub(initial, anchor), n)) / rate

    baseline = {
        "schema": SCHEMA,
        "body": body,
        "body_support": "disc radius" if body=="disc" else
                        "axis-aligned square support, orientation fixed by constraint",
        "half_extent": R,
        "source_angle": rd(angle),
        "source_anchor": [rd(z) for z in anchor],
        "initial_center": list(initial),
        "initial_velocity": list(vin),
        "source": source,
        "selected_physical_outcome": False,
        "measured_earth_material": False,
        "target_receiver_shape_provided": False,
    }
    if t1 <= EPS:
        return {**baseline, "status": "NO_FUTURE_CONTACT", "receiver": None,
                "contacts": [], "frames": []}

    p1 = add(initial, scale(t1, vin))
    representative = add(p1, contact_offset(body, n))
    tangent = (-n[1], n[0])
    along = dot(sub(representative, anchor), tangent)
    if abs(along) >= SPAN/2-EPS:
        return {**baseline, "status": "MISSED_FINITE_SOURCE",
                "receiver": None, "contacts": [], "frames": []}
    if any(not (R <= p1[i] <= FOOTPRINT[i]-R) for i in range(2)):
        return {**baseline, "status": "SOURCE_OUTSIDE_WORLD",
                "receiver": None, "contacts": [], "frames": []}

    # One identical point-contact translational law for both CONSTRAINED
    # bodies; no unsupported free-square torque or spin is inferred.
    v1 = sub(vin, scale(2*rate, n))
    length = hypot(*v1)
    if length <= EPS:
        raise ValueError("zero outgoing direction")
    n2 = scale(-1/length, v1)
    p2 = add(p1, scale(PROJECTION, v1))
    a2 = sub(p2, scale(support(body,n2), n2))
    receiver = segment("movement-derived-receiver", a2, n2)
    second_point = add(p2, contact_offset(body,n2))
    t2 = (-n2[1], n2[0])
    if abs(dot(sub(second_point,a2),t2)) >= SPAN/2-EPS:
        return {**baseline, "status": "MISSED_DERIVED_FINITE_FACE",
                "receiver": None, "contacts": [], "frames": []}
    if any(not (R <= p2[i] <= FOOTPRINT[i]-R) for i in range(2)):
        return {**baseline, "status": "RECEIVER_OUTSIDE_WORLD",
                "receiver": None, "contacts": [], "frames": []}
    rate2 = dot(v1,n2)
    if rate2 >= -EPS:
        raise ValueError("receiver does not face incoming motion")
    v2 = sub(v1, scale(2*rate2,n2))

    receiver["activated_at"] = rd(t1)
    receiver["caused_by_contact_index"] = 0
    receiver["constructed_from"] = "recorded-model-outgoing-velocity"
    contacts = [
        {"time": rd(t1), "source_id": source["id"],
         "center": [rd(z) for z in p1],
         "before": [rd(z) for z in vin], "after": [rd(z) for z in v1]},
        {"time": rd(t1+PROJECTION), "source_id": receiver["id"],
         "center": [rd(z) for z in p2],
         "before": [rd(z) for z in v1], "after": [rd(z) for z in v2]},
    ]
    times = sorted(set([0.,t1,t1+PROJECTION,t1+PROJECTION+POST_CONTACT]+[
        (t1+PROJECTION+POST_CONTACT)*i/16 for i in range(17)]))
    frames = []
    for clock in times:
        if clock < t1:
            p = add(initial,scale(clock,vin))
            v = vin
        elif clock < t1+PROJECTION:
            p = add(p1,scale(clock-t1,v1))
            v = v1
        else:
            p = add(p2,scale(clock-t1-PROJECTION,v2))
            v = v2
        if any(not (R-EPS<=p[i]<=FOOTPRINT[i]-R+EPS)
               for i in range(2)):
            raise ValueError("object left finite WORLD")
        # Conservative full-plane clearance. Does not pretend to solve
        # endpoint contacts or allow passage through finite face extensions.
        if dot(sub(p,anchor),n) < support(body,n)-EPS:
            raise ValueError("body penetrated source face plane")
        if clock >= t1 and dot(sub(p,a2),n2) < support(body,n2)-EPS:
            raise ValueError("body penetrated derived face plane")
        frames.append({
            "time": rd(clock), "center": [rd(z) for z in p],
            "velocity": [rd(z) for z in v],
        })
    return {
        **baseline,
        "status": "TWO_MODELED_CONTACTS",
        "receiver": receiver,
        "contacts": contacts,
        "frames": frames,
        "square_rotation_prevented_by_constraint": body=="fixed-square",
        "finite_face_endpoints_matter": True,
        "actual_hardware_contact_witnessed": False,
        "new_physical_law_inferred": False,
    }


def run():
    cases = [trial(body,angle=angle) for body in BODIES for angle in ANGLES]
    return {
        "schema": SCHEMA, "source_trial14": "world-ab-relation-derived-free-orientation/v1",
        "source_trial04b_reused": True, "body_types": list(BODIES),
        "angles": list(ANGLES), "cases": cases,
        "shape_independent_contact_law": "frictionless translational normal reflection",
        "no_new_world_or_renderer": True,
        "real_material_behavior_observed": False,
    }
