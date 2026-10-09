"""Exhaust all affine constructions of the two phi coordinates over F_3.

The accepted reversible maps preserve the previously discovered exact
rooted A/B equivalence (the zero class plus four nonzero +/- pairs).
Closure is mathematically scoped to the 3D finite affine-bijection family.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .alignment import equivalent_classes
from .math import inverse_candidates
from .operators import Operator


@dataclass(frozen=True)
class AffineScan:
    status: str
    all_affine_maps: int
    bijections: int
    quotient_compatible_maps: int
    compatible_bijections: int
    translated_compatible_bijections: int
    induced_quotient_permutations: int
    quotient_classes: int
    accepted: tuple[Operator, ...]
    quotient_actions: tuple[tuple[int, ...], ...]
    failure: str | None = None


def affine_maps() -> tuple[Operator, ...]:
    return tuple(Operator(
        name=f"affine_{p}{q}{r}{s}_{c}{d}",
        matrix=((p, q), (r, s)), offset=(c, d),
    ) for p, q, r, s, c, d in product(range(3), repeat=6))


def compose(left: Operator, right: Operator) -> Operator:
    """Apply right, then left; preserve exact F_3 affine composition."""
    (a, b), (c, d) = left.matrix
    (e, f), (g, h) = right.matrix
    x, y = right.offset
    u, v = left.offset
    return Operator(
        name=f"({left.name} ∘ {right.name})",
        matrix=(((a*e+b*g) % 3, (a*f+b*h) % 3),
                ((c*e+d*g) % 3, (c*f+d*h) % 3)),
        offset=((a*x+b*y+u) % 3, (c*x+d*y+v) % 3),
    )


def scan_affine() -> AffineScan:
    worlds = inverse_candidates()
    groups = equivalent_classes(worlds)
    class_index = {w: i for i, block in enumerate(groups) for w in block}
    candidate_maps = affine_maps()
    all_compatible = 0
    bijections = 0
    accepted = []
    induced = set()
    translated = 0
    for operator in candidate_maps:
        outputs = {w: operator(w) for w in worlds}
        bijective = len(set(outputs.values())) == len(worlds)
        compatible = all(len({class_index[outputs[w]] for w in block}) == 1
                         for block in groups)
        bijections += bool(bijective)
        all_compatible += bool(compatible)
        if bijective and compatible:
            accepted.append(operator)
            translated += operator.offset != (0, 0)
            induced.add(tuple(class_index[outputs[block[0]]] for block in groups))
    # Prove group closure by exhaustive composition, not merely finite cycles.
    keys = {(o.matrix, o.offset) for o in accepted}
    if any((c.matrix, c.offset) not in keys
           for a in accepted for b in accepted for c in (compose(a, b),)):
        return AffineScan("OPEN", len(candidate_maps), bijections, all_compatible,
                          len(accepted), translated, len(induced), len(groups),
                          tuple(accepted), tuple(sorted(induced)),
                          "accepted operators are not composition-closed")
    if any(action[0] != 0 or set(action) != set(range(len(groups))) for action in induced):
        return AffineScan("OPEN", len(candidate_maps), bijections, all_compatible,
                          len(accepted), translated, len(induced), len(groups),
                          tuple(accepted), tuple(sorted(induced)),
                          "induced action is not a permutation fixing the zero class")
    return AffineScan(
        "CLOSED_FOR_INVERTIBLE_AFFINE_AB_QUOTIENT",
        len(candidate_maps), bijections, all_compatible, len(accepted),
        translated, len(induced), len(groups), tuple(accepted), tuple(sorted(induced)),
    )
