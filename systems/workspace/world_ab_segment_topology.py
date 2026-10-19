"""Source-only finite segment topology before considering chain contact rules.

Inspired by Box2D's stated ghost-vertex *precondition*: contiguous chains meet
at endpoints. No Box2D source is included. In A/B's WORLD trial, the two
source-derived finite segments intersect in their interiors, not end-to-end.
An intersecting pair MUST NOT be silently made into a one-sided ghost chain.

Read-only geometry classification. It does not alter any contact, impulse,
friction, observed frame, source endpoint or game/world worker.
"""
from __future__ import annotations

from math import isfinite, hypot


def _point(p):
    if (not isinstance(p, (tuple, list)) or len(p) != 2 or
            any(not isinstance(x, (int, float)) or isinstance(x, bool)
                or not isfinite(x) for x in p)):
        raise ValueError("point needs two finite coordinates")
    return (float(p[0]), float(p[1]))


def classify_pair(a, b, *, tolerance=1e-7):
    """Classify only actual finite source-segment incidence.

    "shared-endpoint" means eligible for *further* one-sided chain-topology
    checks, NOT that ghost suppression can be applied or a contact removed.
    "interior-crossing" specifically forbids treating the junction as a
    contiguous endpoint chain; its independently witnessed contacts survive.
    """
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool):
        raise ValueError("finite tolerance required")
    if not isfinite(tolerance) or not 0 < tolerance < 0.001:
        raise ValueError("tolerance outside bounded range")
    for seg in (a, b):
        if not isinstance(seg, (tuple, list)) or len(seg) != 2:
            raise ValueError("finite segment endpoints required")
    a0, a1 = _point(a[0]), _point(a[1])
    b0, b1 = _point(b[0]), _point(b[1])
    ax, ay = a1[0]-a0[0], a1[1]-a0[1]
    bx, by = b1[0]-b0[0], b1[1]-b0[1]
    alen, blen = hypot(ax, ay), hypot(bx, by)
    if min(alen, blen) <= tolerance:
        raise ValueError("degenerate finite segment")
    cross = ax * by - ay * bx
    # No conclusion about coincident/overlapping segments from near-parallel
    # orientations; these need a separate predicate.
    if abs(cross) <= tolerance * alen * blen:
        return {"topology": "parallel-or-unresolved",
                "chain_ghost_rule_applicable": False,
                "conclusion": "unknown contact geometry"}
    dx, dy = b0[0]-a0[0], b0[1]-a0[1]
    ua = (dx * by - dy * bx) / cross
    ub = (dx * ay - dy * ax) / cross
    if not -tolerance <= ua <= 1+tolerance or not -tolerance <= ub <= 1+tolerance:
        topology = "disjoint"
    else:
        aend = ua <= tolerance or ua >= 1-tolerance
        bend = ub <= tolerance or ub >= 1-tolerance
        if aend and bend:
            topology = "shared-endpoint"
        elif not aend and not bend:
            topology = "interior-crossing"
        else:
            topology = "endpoint-interior"
    return {
        "topology": topology,
        "intersection_fractions": (round(ua, 9), round(ub, 9)),
        "chain_ghost_rule_applicable": topology == "shared-endpoint",
        "conclusion": (
            "endpoint adjacency requires further winding/neighbor checks"
            if topology == "shared-endpoint" else
            "do not suppress distinct finite-surface contacts"
            if topology in ("interior-crossing", "endpoint-interior") else
            "no established chain adjacency"),
    }
