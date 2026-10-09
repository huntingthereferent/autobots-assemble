"""Inverse A/B: independently constructed finite-field coupling towers.

Each rule r_i: F_3 -> F_3 has r_i(0)=0. Canonical signatures classify
ONLY the deterministic A/B action graph reachable from the zero origin.
No claim about full-state or unrestricted inverse-limit conjugacy follows.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from math import lcm

Rule = tuple[int, int, int]
State = tuple[int, ...]
RULES: tuple[Rule, ...] = tuple((0, a, b) for a, b in product(range(3), repeat=2))


def validate(rules: tuple[Rule, ...]) -> None:
    if not rules or any(len(rule) != 3 or rule[0] != 0 or
                        any(type(x) is not int or x not in range(3) for x in rule)
                        for rule in rules):
        raise ValueError("nonempty F_3 rules with r_i(0)=0 required")


@dataclass(frozen=True)
class CouplingTower:
    rules: tuple[Rule, ...]
    depth: int

    def __post_init__(self):
        validate(self.rules)
        if self.depth < len(self.rules) + 2:
            raise ValueError("depth must expose all admitted coupling rules")

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, state: State, action: str) -> State:
        if (len(state) != self.depth or any(type(v) is not int or v not in range(3) for v in state)):
            raise ValueError("state must lie in F_3^depth")
        moved = list(state)
        if action == "A":
            moved[0] = (state[0] + 1) % 3
        elif action == "B":
            moved[1] = (state[1] + state[0] + 1) % 3
            for i in range(2, self.depth):
                increment = (self.rules[i-2][state[i-1]] if i-2 < len(self.rules)
                             else state[i-1])
                moved[i] = (state[i] + increment) % 3
        else:
            raise ValueError("only A/B")
        return tuple(moved)

    def inverse(self, state: State, action: str) -> State:
        if len(state) != self.depth or any(type(v) is not int or v not in range(3) for v in state):
            raise ValueError("invalid state")
        before = list(state)
        if action == "A":
            before[0] = (state[0] - 1) % 3
        elif action == "B":
            before[1] = (state[1] - state[0] - 1) % 3
            for i in range(2, self.depth):
                increment = (self.rules[i-2][before[i-1]] if i-2 < len(self.rules)
                             else before[i-1])
                before[i] = (state[i] - increment) % 3
        else:
            raise ValueError("only A/B")
        return tuple(before)


def construct_family(couplings: int = 3, *, depth: int | None = None) -> tuple[CouplingTower, ...]:
    if not 1 <= couplings <= 4:
        raise ValueError("bounded enumeration supports 1 to 4 independent couplings")
    depth = depth or couplings + 2
    return tuple(CouplingTower(tuple(sequence), depth)
                 for sequence in product(RULES, repeat=couplings))


@dataclass(frozen=True)
class CanonicalGraph:
    transitions: tuple[int, ...]
    states: int


def rooted_graph(world: CouplingTower, *, state_budget: int = 2500) -> CanonicalGraph:
    """Canonical BFS graph: deterministic AB-word order is rooted-isomorphism invariant.

    A rooted, action-labeled bijection exists iff BOTH breadth-first
    enumerations create identical transition-index sequences. No graph
    hashing, state-name comparison, or arbitrary alignment is assumed.
    """
    if state_budget < 1:
        raise ValueError("positive state budget required")
    labels = {world.origin: 0}
    queue = [world.origin]
    edges = []
    for state in queue:
        for action in 'AB':
            next_state = world.step(state, action)
            if next_state not in labels:
                if len(queue) >= state_budget:
                    raise ValueError("UNKNOWN: reachable-state budget exceeded")
                labels[next_state] = len(queue)
                queue.append(next_state)
            edges.append(labels[next_state])
    return CanonicalGraph(tuple(edges), len(queue))


def classify_rooted(worlds: tuple[CouplingTower, ...], *, state_budget: int = 2500):
    groups: dict[CanonicalGraph, list[CouplingTower]] = defaultdict(list)
    for world in worlds:
        groups[rooted_graph(world, state_budget=state_budget)].append(world)
    return tuple(tuple(group) for group in groups.values())


def first_dormant(world: CouplingTower) -> int:
    return next((i for i, rule in enumerate(world.rules) if rule == (0,0,0)), len(world.rules))


def projective_scaling(source: CouplingTower, target: CouplingTower) -> tuple[int, ...] | None:
    """Find explicit all-depth *full-state* diagonal conjugacy, if this family provides it."""
    if len(source.rules) != len(target.rules):
        return None
    for scales in product((1,2), repeat=len(source.rules)):
        previous = 1
        for rule, other, scale in zip(source.rules, target.rules, scales):
            if any(other[(previous * digit) % 3] != (scale * rule[digit]) % 3
                   for digit in range(3)):
                break
            previous = scale
        else:
            return tuple(scales)
    return None


def scale_state(state: State, scales: tuple[int,...]) -> State:
    if len(state) < len(scales)+2 or any(k not in (1,2) for k in scales):
        raise ValueError("invalid scaling")
    if any(type(d) is not int or d not in range(3) for d in state):
        raise ValueError("invalid coordinate")
    return state[:2] + tuple((scales[i-2] if i-2 < len(scales) else scales[-1])*state[i] % 3
                             for i in range(2,len(state)))


@dataclass(frozen=True)
class ThirdCouplingCertificate:
    status: str
    constructed_worlds: int
    rooted_classes: int
    class_distribution: tuple[tuple[int,int], ...]
    reachable_distribution: tuple[tuple[int,int], ...]
    first_dormant_classes: tuple[tuple[int,int], ...]
    all_depth_diagonal_classes: int
    rooted_only_classes: int
    stable_next_depth: bool
    rotation_order: int
    failure: str | None = None


def certify_three_couplings() -> ThirdCouplingCertificate:
    """Exhaust all 729 five-dimensional graphs and their six-dimensional extensions.

    Exact checks establish the finite partitions. For the active classes,
    explicit diagonal conjugacies establish equivalence at ALL dimensions.
    Dormant prefixes stay zero on the origin orbit, but do NOT imply
    isomorphism of the complete finite-coordinate state spaces.
    """
    worlds = construct_family(3)
    groups = classify_rooted(worlds)
    distribution = Counter(len(group) for group in groups)
    reachable = Counter(rooted_graph(w).states for w in worlds)
    dormants = Counter(first_dormant(group[0]) for group in groups)
    active_classes = 0
    for group in groups:
        dormant = first_dormant(group[0])
        if any(first_dormant(world) != dormant for world in group):
            return ThirdCouplingCertificate("OPEN",len(worlds),len(groups),(),(),(),0,0,False,0,
                                            "rooted class mixes incompatible active coupling lengths")
        if dormant >= 2:
            for world in group:
                if projective_scaling(group[0],world) is None:
                    return ThirdCouplingCertificate("OPEN",len(worlds),len(groups),(),(),(),0,0,False,0,
                                                    "active class lacks full-space diagonal witness")
            active_classes += 1
    higher = tuple(CouplingTower(w.rules,6) for w in worlds)
    elevated = classify_rooted(higher)
    signature4 = {world.rules:i for i, group in enumerate(groups) for world in group}
    signature5 = {world.rules:i for i, group in enumerate(elevated) for world in group}
    stable = all((signature4[a.rules] == signature4[b.rules]) ==
                 (signature5[a.rules] == signature5[b.rules])
                 for a in worlds for b in worlds)
    status = "CLOSED_ROOTED_FAMILY_AT_DEPTH_5_AND_6" if stable else "OPEN_DEPTH_REFINEMENT"
    return ThirdCouplingCertificate(status,len(worlds),len(groups),
                                    tuple(sorted(distribution.items())),
                                    tuple(sorted(reachable.items())),
                                    tuple(sorted(dormants.items())), active_classes,
                                    len(groups)-active_classes, stable,
                                    lcm(*distribution))


def rotation(groups: tuple[tuple[CouplingTower, ...], ...]) -> dict[CouplingTower,CouplingTower]:
    """Chosen finite rooted-class permutation; NEVER an automatic closure of new rules."""
    return {world: group[(i+1)%len(group)]
            for group in groups for i,world in enumerate(group)}


@dataclass(frozen=True)
class ExtensionObstruction:
    """Two permitted one-coordinate constructions with distinct B invariants."""
    base_depth: int
    base_fixed: int
    zero_extension_fixed: int
    identity_extension_fixed: int
    status: str


def count_fixed_B_formula(world: CouplingTower) -> int:
    """ALL full-space B fixed points without iterating over 3^depth states.

    B(x)=x requires x_0=2, and for coordinate i>=2 the preceding
    coordinate x_(i-1) lies in the zeros of its associated coupling rule.
    The final coordinate x_(d-1) is unconstrained. Each input condition
    involves a different coordinate, so their zero-set sizes multiply.
    """
    choices = 3  # last coordinate is free
    for i in range(2,world.depth):
        rule = world.rules[i-2] if i-2 < len(world.rules) else (0,1,2)
        choices *= sum(rule[value] == 0 for value in range(3))
    return choices


def extension_obstruction(rules: tuple[Rule, ...]) -> ExtensionObstruction:
    """Prove no finite depth closes unrestricted independent couplings.

    The new coordinate may use the zero or identity input function;
    these give different B-fixed state counts on the whole space.
    This is a model-specific impossibility theorem for finite terminal
    depth, not a proof about universal A/B mathematics.
    """
    validate(rules)
    base_depth = len(rules) + 2
    base = CouplingTower(rules, base_depth)
    zero = CouplingTower(rules + ((0,0,0),), base_depth+1)
    identity = CouplingTower(rules + ((0,1,2),), base_depth+1)
    b, z, one = (count_fixed_B_formula(w) for w in (base,zero,identity))
    return ExtensionObstruction(base_depth,b,z,one,
                                'OPEN_UNRESTRICTED_EXTENSION' if (z == 3*b and one == b and b>0)
                                else 'UNKNOWN')
