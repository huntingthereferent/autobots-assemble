"""WORLD Trial 14: change finite source geometry; construct from its actual motion.

A narrow mathematical continuation of original WORLD Trial 04B on the Trial13
branch. No new engine, renderer, arbitrary laws, automatic material growth, or
assumption of a solved simultaneous contact. A single finite source segment
can be given any *admitted* angle/anchor in a bounded region. Its first
modeled contact yields the next receiver's position AND orientation, and the
same moving disc reaches that receiver at a separately verified later time.

These are virtual, declared contact-model observations, not measurements of
hardware. A contact miss constructs nothing. No desired output shape is input.
"""
from __future__ import annotations

from math import cos, hypot, isfinite, radians, sin

from systems.workspace.world_ab_oblique_rotation import (
    R, I, M, START, VELOCITY, SPAN, PROJECTION,
    FOOTPRINT, impact, scalar_energy, dot, add, mul, sub, norm,
)
from systems.workspace.world_ab_junction_continuous import nearest

SCHEMA = "world-ab-relation-derived-free-orientation/v1"
ANGLE_BOUND = 40.0
EPS = 1e-9
CLEARANCE = 2e-7
AFTER_SECOND = 0.10
OBSERVATIONS = 16


def rounded(x):
    return round(float(x), 10)


def finite_pair(v, name):
    if not isinstance(v, (tuple, list)) or len(v) != 2:
        raise ValueError(name + " must be a pair")
    if any(type(z) not in (int, float) or not isfinite(z) for z in v):
        raise ValueError(name + " requires finite numeric coordinates")
    return tuple(float(z) for z in v)


def segment(identifier, anchor, normal):
    tangent = (-normal[1], normal[0])
    a = add(anchor, mul(-SPAN / 2, tangent))
    b = add(anchor, mul(SPAN / 2, tangent))
    if any(not (0. <= p[0] <= FOOTPRINT[0] and
                0. <= p[1] <= FOOTPRINT[1]) for p in (a, b)):
        raise ValueError("source or derived segment exits declared WORLD")
    return {
        "id": identifier,
        "anchor": [rounded(z) for z in anchor],
        "normal": [rounded(z) for z in normal],
        "endpoints": [[rounded(z) for z in p] for p in (a, b)],
        "span": SPAN,
    }


def trial(*, angle=0.0, anchor=(12., 1.5), friction=0.4):
    """One input geometry, two causal contact events, independently checkable.

    A continuous angle is *input*, not a category of object. It doesn't imply
    that this bounded contact model works for any angle or physical material.
    """
    if type(angle) not in (int, float) or not isfinite(angle) or abs(angle) > ANGLE_BOUND:
        raise ValueError("source angle must be finite and within admitted range")
    if type(friction) not in (int, float) or not isfinite(friction) or not 0 <= friction <= .4:
        raise ValueError("friction outside bounded contact model")
    anchor = finite_pair(anchor, "source anchor")
    if not (7 <= anchor[0] <= 16 and .75 <= anchor[1] <= 5.25):
        raise ValueError("source anchor outside experiment")
    n = (-cos(radians(angle)), -sin(radians(angle)))
    face = segment("finite-input-source", anchor, n)
    start = tuple(START)
    incoming = tuple(VELOCITY)
    approach = dot(incoming, n)
    if approach >= -EPS:
        raise ValueError("input geometry is not approached by the source disc")
    t1 = (R - dot(sub(start, anchor), n)) / approach
    miss = {
        "schema": SCHEMA,
        "input_source_angle_degrees": rounded(angle),
        "input_source_anchor": [rounded(z) for z in anchor],
        "friction": rounded(friction),
        "source": face,
        "disc_radius": R,
        "disc_inertia": I,
        "input_origin": list(start),
        "input_velocity": list(incoming),
        "measured_physical_material": False,
        "source_collision_is_a_declared_model": True,
        "target_shape_supplied": False,
    }
    if t1 <= EPS:
        return {**miss, "status": "NO_FUTURE_SOURCE_CONTACT",
                "receiver": None, "contacts": [], "frames": []}
    first_position = add(start, mul(t1, incoming))
    foot = sub(first_position, mul(R, n))
    tangent = (-n[1], n[0])
    offset = dot(sub(foot, anchor), tangent)
    if abs(offset) >= SPAN / 2 - EPS:
        return {**miss, "status": "NO_FINITE_SEGMENT_CONTACT",
                "receiver": None, "contacts": [], "frames": []}
    if any(not (R <= z <= high - R) for z, high in zip(first_position, FOOTPRINT)):
        return {**miss, "status": "SOURCE_CONTACT_OUTSIDE_WORLD",
                "receiver": None, "contacts": [], "frames": []}

    outgoing1, spin1, impulse1 = impact(incoming, 0., n, float(friction))
    if dot(outgoing1, n) <= EPS:
        raise ValueError("first outgoing motion did not separate from source")
    # No planned receiver direction or label: normal is opposite this ACTUAL
    # computed outgoing velocity, and contact is projected along that motion.
    n2 = mul(-1., norm(outgoing1))
    second_position = add(first_position, mul(PROJECTION, outgoing1))
    second_anchor = sub(second_position, mul(R, n2))
    try:
        receiver = segment("movement-derived-receiver", second_anchor, n2)
    except ValueError:
        return {**miss, "status": "DERIVED_RECEIVER_OUTSIDE_WORLD",
                "receiver": None, "contacts": [], "frames": []}
    # The source starts existing at time 0; receiver starts existing only at
    # first contact. Both must be genuinely reachable at a finite segment.
    gap1, _, fraction1 = nearest(first_position, face)
    gap2, _, fraction2 = nearest(second_position, receiver)
    if abs(gap1 - R) > CLEARANCE or not EPS < fraction1 < 1-EPS:
        raise ValueError("source contact fails finite-segment witness")
    if abs(gap2 - R) > CLEARANCE or not EPS < fraction2 < 1-EPS:
        raise ValueError("generated receiver contact fails finite-segment witness")
    if any(not (R <= z <= high-R) for z, high in zip(second_position, FOOTPRINT)):
        return {**miss, "status": "DERIVED_CONTACT_OUTSIDE_WORLD",
                "receiver": None, "contacts": [], "frames": []}
    if dot(outgoing1, n2) >= -EPS:
        raise ValueError("constructed receiver cannot be struck from outgoing motion")
    t2 = t1 + PROJECTION
    outgoing2, spin2, impulse2 = impact(outgoing1, spin1, n2, float(friction))
    if scalar_energy(outgoing2, spin2) > scalar_energy(incoming, 0.) + EPS:
        raise ValueError("contact composition created kinetic energy")
    if dot(outgoing2, n2) <= EPS:
        raise ValueError("second outgoing motion did not separate from receiver")

    times = sorted(set([0., t1, t2, t2+AFTER_SECOND] +
                       [(t2+AFTER_SECOND)*i/OBSERVATIONS
                        for i in range(OBSERVATIONS+1)]))
    frames = []
    for t in times:
        if t < t1:
            p = add(start, mul(t, incoming))
            v, spin, phase = incoming, 0., "before-source-contact"
        elif t < t2:
            p = add(first_position, mul(t-t1, outgoing1))
            v, spin, phase = outgoing1, spin1, "source-contact-to-receiver"
        else:
            p = add(second_position, mul(t-t2, outgoing2))
            v, spin, phase = outgoing2, spin2, "after-derived-contact"
        if any(not (R-CLEARANCE <= z <= bound-R+CLEARANCE)
               for z, bound in zip(p, FOOTPRINT)):
            raise ValueError("admitted frame escapes virtual WORLD")
        source_gap, _, _ = nearest(p, face)
        if source_gap < R-CLEARANCE:
            raise ValueError("movement penetrates the original source")
        # The receiver does not exist before the first contact.
        receiver_gap, _, _ = nearest(p, receiver)
        if t >= t1 and receiver_gap < R-CLEARANCE:
            raise ValueError("movement penetrates generated receiver")
        frames.append({
            "time": rounded(t),
            "position": [rounded(z) for z in p],
            "velocity": [rounded(z) for z in v],
            "spin": rounded(spin),
            "phase": phase,
        })
    contacts = [
        {"time": rounded(t1),
         "source_id": face["id"],
         "center": [rounded(z) for z in first_position],
         "incoming_velocity": [rounded(z) for z in incoming],
         "outgoing_velocity": [rounded(z) for z in outgoing1],
         "outgoing_spin": rounded(spin1),
         "impulse": impulse1},
        {"time": rounded(t2),
         "source_id": receiver["id"],
         "center": [rounded(z) for z in second_position],
         "incoming_velocity": [rounded(z) for z in outgoing1],
         "outgoing_velocity": [rounded(z) for z in outgoing2],
         "outgoing_spin": rounded(spin2),
         "impulse": impulse2},
    ]
    receiver["activated_at"] = rounded(t1)
    receiver["source_contact_index"] = 0
    receiver["constructed_from"] = "first-outgoing-velocity"
    return {
        **miss, "status": "TWO_CONTACTS_IN_DECLARED_MODEL",
        "receiver": receiver, "contacts": contacts, "frames": frames,
        "source_model_04B_unchanged": True,
        "world48_and_nih_unmodified": True,
        "all_physical_interactions_solved": False,
    }


def run():
    # Reproduce 04B's controls and genuinely new fractional source angles.
    angles = (0., 7.5, 12.25, 20.)
    friction = (0., .4)
    cases = [trial(angle=a, friction=mu) for a in angles for mu in friction]
    if len(cases) != 8:
        raise ValueError("control grid changed")
    return {
        "schema": SCHEMA,
        "source_angle_grid": list(angles),
        "friction_grid": list(friction),
        "cases": cases,
        "new_receiver_shape_is_source_derived": True,
        "real_earth_physics_verified": False,
        "physical_motor_or_nih_blueprint_tested": False,
    }
