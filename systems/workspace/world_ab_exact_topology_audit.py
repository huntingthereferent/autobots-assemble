"""Exact topological predicates for *recorded finite binary coordinates*.

Independent audit prompted by kika's separation of geometric predicates from
coordinate construction. This is original A/B code; neither kika nor
Shewchuk's expansion arithmetic is copied. Python Fraction provides exact
rational arithmetic over the finite input floats as actually recorded.

Only a read-only classification: NO new intersection point, impulse, contact
removal, solver alteration, or claim about the unrounded physical source.
"""
from __future__ import annotations

from fractions import Fraction
from math import isfinite

_MAX_COORD = 10_000


def _coordinate(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError("coordinate must be a finite real number")
    if not isfinite(v) or abs(v) > _MAX_COORD:
        raise ValueError("coordinate outside finite WORLD audit bound")
    # Integers retain exact values; floats retain their exact binary value,
    # not an imagined infinitely precise decimal measurement.
    return Fraction(v)


def _point(p):
    if not isinstance(p, (tuple, list)) or len(p) != 2:
        raise ValueError("two-coordinate point required")
    return tuple(_coordinate(x) for x in p)


def _segment(s):
    if not isinstance(s, (tuple, list)) or len(s) != 2:
        raise ValueError("two finite segment endpoints required")
    p, q = _point(s[0]), _point(s[1])
    if p == q:
        raise ValueError("zero-length segment is not admitted in WORLD audit")
    return p, q


def _signed(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


def orientation(a, b, c):
    """Exact -1 / 0 / +1 sign of the *supplied binary* point orientation."""
    det = _signed(_point(a), _point(b), _point(c))
    return (det > 0) - (det < 0)


def _inside(point, a, b):
    return (min(a[0], b[0]) <= point[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= point[1] <= max(a[1], b[1]))


def segment_kind(first, second):
    """Exact classification without constructing an intersection coordinate.

    The returned kind distinguishes proper interior crossing, shared endpoint,
    endpoint touching another interior, collinear touch / overlap, and disjoint.
    It never infers a contact response or a valid chain from proximity alone.
    """
    a, b = _segment(first)
    c, d = _segment(second)
    o1, o2 = _signed(a, b, c), _signed(a, b, d)
    o3, o4 = _signed(c, d, a), _signed(c, d, b)

    if o1 == o2 == o3 == o4 == 0:
        # Project along an axis on which both collinear segments have an extent.
        axis = 0 if a[0] != b[0] else 1
        left = max(min(a[axis], b[axis]), min(c[axis], d[axis]))
        right = min(max(a[axis], b[axis]), max(c[axis], d[axis]))
        if left > right:
            return "disjoint"
        return "collinear-touch" if left == right else "collinear-overlap"

    touching = {
        p for p, s, t in ((a, c, d), (b, c, d),
                          (c, a, b), (d, a, b))
        if _signed(s, t, p) == 0 and _inside(p, s, t)
    }
    if touching:
        endpoints = (a, b, c, d)
        if any(p in (a, b) and p in (c, d) for p in touching):
            return "shared-endpoint"
        return "endpoint-interior"
    if ((o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)
            and o1 and o2 and o3 and o4):
        return "interior-crossing"
    return "disjoint"


def audit_classification(first, second):
    """Compare exact recorded-coordinate topology with existing float audit.

    A disagreement is reported, not silently 'fixed' by mutating native
    experiment geometry or declaring a physics collision.
    """
    from .world_ab_segment_topology import classify_pair
    accurate = segment_kind(first, second)
    existing = classify_pair(first, second)["topology"]
    paired = {
        "interior-crossing": {"interior-crossing"},
        "shared-endpoint": {"shared-endpoint"},
        "endpoint-interior": {"endpoint-interior"},
        "collinear-touch": {"parallel-or-unresolved"},
        "collinear-overlap": {"parallel-or-unresolved"},
        "disjoint": {"disjoint", "parallel-or-unresolved"},
    }
    return {
        "exact_recorded_coordinate_kind": accurate,
        "existing_approximate_kind": existing,
        "agrees_with_approximation": existing in paired[accurate],
        "execution_started": False,
        "world_source_changed": False,
        "contact_resolution_claimed": False,
    }
