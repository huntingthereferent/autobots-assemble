"""All reversible nonlinear lifts of constructed A/B world relations.

Finite experiment: nine worlds W_phi over F_3^3, phi=(0,a,b).
A construction changes a WORLD PARAMETER, not an ARC player's state.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from math import factorial

from .alignment import discover_alignment, equivalent_classes
from .math import World, inverse_candidates
from .affine_scan import scan_affine

WorldIndexMap = tuple[int, ...]


@dataclass(frozen=True)
class ConstructionMap:
    """Total map over the nine parameter worlds; need not be invertible."""
    name: str
    images: WorldIndexMap

    def __post_init__(self) -> None:
        n = len(inverse_candidates())
        if not self.name or len(self.images) != n or any(
            type(value) is not int or not 0 <= value < n for value in self.images
        ):
            raise ValueError("invalid finite constructor")

    def __call__(self, world: World) -> World:
        worlds = inverse_candidates()
        if world.depth < 3 or world.phi[0] != 0:
            raise ValueError("world is outside this construction family")
        try:
            index = worlds.index(World(3, world.phi))
        except ValueError as exc:
            raise ValueError("world is outside this construction family") from exc
        return World(world.depth, worlds[self.images[index]].phi)

    @property
    def bijective(self) -> bool:
        return len(set(self.images)) == len(self.images)


def compose(left: ConstructionMap, right: ConstructionMap) -> ConstructionMap:
    """Apply right, then left."""
    return ConstructionMap(
        f"({left.name} composed with {right.name})",
        tuple(left.images[index] for index in right.images),
    )


def nonlinear_lifts() -> tuple[ConstructionMap, ...]:
    """Exhaust all nine-world bijections preserving the discovered A/B classes.

    One singleton is fixed. Four 2-point classes may be permuted (4!)
    and each pair independently oriented (2^4). This is exhaustive for
    the witnessed partition, NOT for arbitrary inverse A/B construction.
    """
    worlds = inverse_candidates()
    groups = equivalent_classes(worlds)
    if sorted(map(len, groups)) != [1, 2, 2, 2, 2] or groups[0] != (worlds[0],):
        raise ValueError("A/B partition changed; closure not admitted")
    indices = {world: i for i, world in enumerate(worlds)}
    results = []
    for destinations in permutations(range(4)):
        for flips in product(range(2), repeat=4):
            images = list(range(len(worlds)))
            for source_index, (destination_index, flip) in enumerate(zip(destinations, flips)):
                source = groups[source_index + 1]
                destination = groups[destination_index + 1]
                for orientation, origin in enumerate(source):
                    images[indices[origin]] = indices[destination[orientation ^ flip]]
            results.append(ConstructionMap(
                f"classes-{destinations}_flips-{flips}", tuple(images),
            ))
    return tuple(results)


def pair_flip() -> ConstructionMap:
    """Nonaffine involution swapping only one paired A/B class."""
    worlds = inverse_candidates()
    groups = equivalent_classes(worlds)
    indices = {world: i for i, world in enumerate(worlds)}
    images = list(range(len(worlds)))
    a, b = (indices[world] for world in groups[1])
    images[a], images[b] = images[b], images[a]
    return ConstructionMap("flip-one-equivalent-pair", tuple(images))


def collapse_to_zero() -> ConstructionMap:
    """Quotient-compatible but nonreversible: not a construction loop."""
    return ConstructionMap("collapse-to-zero", (0,) * len(inverse_candidates()))


def class_action(
    operation: ConstructionMap, groups: tuple[tuple[World, ...], ...],
) -> tuple[int, ...] | None:
    index = {world: i for i, group in enumerate(groups) for world in group}
    targets = []
    for group in groups:
        image_classes = {index[operation(world)] for world in group}
        if len(image_classes) != 1:
            return None
        targets.append(next(iter(image_classes)))
    return tuple(targets)


@dataclass(frozen=True)
class NonlinearCertificate:
    status: str
    world_count: int
    class_sizes: tuple[int, ...]
    reversible: int
    affine: int
    nonlinear: int
    quotient_actions: int
    lifts_per_action: int
    composition_checked: int
    sink_preserves_quotient: bool
    sink_is_loop: bool
    deeper_alignment: str
    failure: str | None = None


def certify_nonlinear_group() -> NonlinearCertificate:
    """Exhaustive maximal reversible group preserving this 3D A/B quotient.

    The bound is the nine-world parameter family. Higher-dimensional cross-
    depth alignment and arbitrary new inverse constructions are NOT certified.
    """
    worlds = inverse_candidates()
    groups = equivalent_classes(worlds)
    operators = nonlinear_lifts()
    affine = scan_affine().accepted
    affine_images = {
        tuple(worlds.index(operator(world)) for world in worlds)
        for operator in affine
    }
    keys = {operator.images for operator in operators}
    errors = []
    if len(operators) != factorial(4) * 2**4 or len(keys) != len(operators):
        errors.append("incomplete or repeated construction enumeration")
    if not all(operator.bijective and class_action(operator, groups) is not None
               for operator in operators):
        errors.append("invalid reversible quotient constructor")
    if not affine_images <= keys or len(affine_images) != 48:
        errors.append("affine witness mismatch")
    quotient_actions = {class_action(operator, groups) for operator in operators}
    if len(quotient_actions) != factorial(4):
        errors.append("quotient action count mismatch")
    for left in operators:
        for right in operators:
            if compose(left, right).images not in keys:
                errors.append("not closed under composition")
                break
        if errors:
            break
    sink = collapse_to_zero()
    deeper = discover_alignment(World(3), World(4)).status
    if deeper != "OPEN":
        errors.append("unexpected cross-depth equivalence")
    return NonlinearCertificate(
        "CLOSED_FOR_NINE_WORLD_NONLINEAR_BIJECTIONS" if not errors else "OPEN",
        len(worlds), tuple(len(group) for group in groups), len(operators),
        len(affine_images), len(keys - affine_images), len(quotient_actions),
        len(keys) // len(quotient_actions), len(operators)**2,
        class_action(sink, groups) is not None, sink.bijective, deeper,
        "; ".join(errors) or None,
    )
