"""Discover and certify finite labeled A/B conjugacy from transition observations.

The target interface is ONLY step(state, action). Neither a relabeling H nor a
parameter describing it is passed to the discovery algorithm. This algorithm
recovers a rooted orbit mapping and, if requested, tries full-state extension.

A completed full-state proof is an explicit checked bijection across both
labeled generators on a fixed declared 27-element domain. Incompletely queried
edges must never be reported as proven full-state correspondence.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem

State = tuple[int, int, int]
ZERO: State = (0, 0, 0)
DOMAIN: tuple[State, ...] = tuple(product(range(3), repeat=3))
DOMAIN_SET = frozenset(DOMAIN)
Action = str
Step = Callable[[State, Action], State]


@dataclass(frozen=True)
class Observation:
    state: State
    action: Action
    output: State


@dataclass(frozen=True)
class Discovery:
    status: str
    rooted_pairs: tuple[tuple[State, State], ...]
    full_pairs: tuple[tuple[State, State], ...]
    observed: tuple[Observation, ...]
    attempts: int
    detail: str = ""

    @property
    def calls(self) -> int:
        return len(self.observed)

    @property
    def rooted_count(self) -> int:
        return len(self.rooted_pairs)


class _OutOfQueries(Exception):
    pass


class _InvalidTransition(Exception):
    def __init__(self, state: State, action: Action, value: object):
        self.state, self.action, self.value = state, action, value


class _OutOfSearch(Exception):
    pass


class Observations:
    def __init__(self, observe: Step, limit: int):
        self.observe = observe
        self.limit = limit
        self.table: dict[tuple[State, Action], State] = {}

    def get(self, s: State, act: Action) -> State:
        key = (s, act)
        if key not in self.table:
            if len(self.table) >= self.limit:
                raise _OutOfQueries()
            value = self.observe(s, act)
            if type(value) is not tuple or len(value) != 3 or any(
                    type(x) is not int or x not in (0, 1, 2) for x in value):
                raise _InvalidTransition(s, act, value)
            self.table[key] = value
        return self.table[key]

    def record(self) -> tuple[Observation, ...]:
        return tuple(Observation(s, action, val)
                     for (s, action), val in self.table.items())


def _grow(
    source: FiniteSystem,
    target: Callable[[State, Action], State],
    forward: dict[State, State],
    reverse: dict[State, State],
    source_anchor: State,
    target_anchor: State,
) -> bool:
    """Synchronize labeled transitions, extending a partial bijection.

    Use staging copies supplied by caller so unsuccessful branches are reversible.
    """
    queue = deque([(source_anchor, target_anchor)])
    while queue:
        s, t = queue.popleft()
        if s in forward:
            if forward[s] != t:
                return False
            if reverse[t] != s:
                return False
            continue
        if t in reverse:
            return False
        forward[s], reverse[t] = t, s
        for act in "AB":
            queue.append((source.step(s, act), target(t, act)))
    return True


def _orbit_sizes(table_step: Step) -> tuple[int, ...]:
    """Partition invariant state components under both labeled generators."""
    left = set(DOMAIN)
    sizes = []
    while left:
        seed = min(left)
        reached = {seed}
        queue = deque([seed])
        while queue:
            here = queue.popleft()
            for a in "AB":
                nxt = table_step(here, a)
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)
        left.difference_update(reached)
        sizes.append(len(reached))
    return tuple(sorted(sizes))


def discover(
    source: FiniteSystem,
    observe_target: Step,
    *,
    source_root: State = ZERO,
    target_root: State = ZERO,
    full: bool = True,
    max_queries: int = 54,
    max_extension_attempts: int = 10000,
) -> Discovery:
    """Derive pointed H from movement; optionally extend over disconnected parts.

    Positive ROOTED_REACHABLE only certifies the orbits of the provided roots.
    FULL_CONJUGACY requires all 54 target transitions and verifies both A and B
    at all 27 states. An exhausted budget is UNKNOWN, not negative evidence.
    """
    if type(source) is not FiniteSystem:
        raise TypeError("source must be the finite three-coordinate source law")
    if source_root not in DOMAIN_SET or target_root not in DOMAIN_SET:
        raise ValueError("roots must be in F3^3")
    if (type(max_queries) is not int or type(max_extension_attempts) is not int or
            max_queries < 0 or max_extension_attempts < 0):
        raise ValueError("budgets must be nonnegative integers")
    observed = Observations(observe_target, max_queries)
    anchored: dict[State, State] = {}
    inverse: dict[State, State] = {}
    attempts = 0

    def reply(status: str, *, final: dict[State, State] | None = None,
              detail: str = "") -> Discovery:
        return Discovery(status, tuple(sorted(anchored.items())),
                         tuple(sorted(final.items())) if final is not None else (),
                         observed.record(), attempts, detail)

    try:
        # A direct version of rooted action-graph discovery, on observed target edges.
        if not _grow(source, observed.get, anchored, inverse, source_root, target_root):
            return reply("ROOTED_OBSTRUCTED", detail="contradictory images of A/B words")
        if not full:
            return reply("ROOTED_REACHABLE", detail="no claim about states off the rooted orbit")

        # The source may not be root-transitive. Observe the remaining target
        # domain before seeking a full-state witness (no invisible evidence).
        for t in DOMAIN:
            for act in "AB":
                observed.get(t, act)

        table_step = lambda x, a: observed.table[(x, a)]
        # Conjugates of bijective source generators must be bijective, too.
        for a in "AB":
            outputs = [table_step(s, a) for s in DOMAIN]
            if len(set(outputs)) != len(DOMAIN):
                return reply("FULL_OBSTRUCTED", detail=f"target {a} is not bijective")
        src_orbits = _orbit_sizes(source.step)
        tgt_orbits = _orbit_sizes(table_step)
        if src_orbits != tgt_orbits:
            return reply("FULL_OBSTRUCTED", detail=f"orbit sizes {src_orbits} != {tgt_orbits}")

        # Unlike a pre-supplied H, we must choose a valid pairing of every
        # as-yet-unmapped source component and target component. The rooted
        # mapping remains fixed throughout this finite exact-cover search.
        def extend(fwd: dict[State, State], rev: dict[State, State]):
            nonlocal attempts
            if len(fwd) == len(DOMAIN):
                return fwd
            seed = next(s for s in DOMAIN if s not in fwd)
            for anchor in DOMAIN:
                if anchor in rev:
                    continue
                if attempts >= max_extension_attempts:
                    raise _OutOfSearch()
                attempts += 1
                candidate_fwd = dict(fwd)
                candidate_rev = dict(rev)
                if _grow(source, table_step, candidate_fwd, candidate_rev, seed, anchor):
                    found = extend(candidate_fwd, candidate_rev)
                    if found is not None:
                        return found
            return None

        found = extend(anchored, inverse)
        if found is None:
            return reply("FULL_OBSTRUCTED", detail="exhaustive pointed A/B mapping search failed")
        # Direct final witness check; includes states not originally reachable.
        if (len(found) != 27 or set(found.values()) != DOMAIN_SET or
                any(found[source.step(s, a)] != table_step(found[s], a)
                    for s in DOMAIN for a in "AB") or
                found[source_root] != target_root):
            raise AssertionError("proposed H failed full-state generator squares")
        return reply("FULL_CONJUGACY", final=found,
                     detail="explicit bijection verified on both generators and every state")
    except _OutOfQueries:
        return reply("UNKNOWN_QUERY_BUDGET", detail="required target transitions unobserved")
    except _OutOfSearch:
        return reply("UNKNOWN_SEARCH_BUDGET", detail="finite extension search not exhausted")
    except _InvalidTransition as err:
        return reply("WALL_INVALID_OBSERVATION", detail=f"{err.state} {err.action}: {err.value!r}")


def verify_recorded_full(source: FiniteSystem, result: Discovery,
                         *, source_root: State = ZERO, target_root: State = ZERO) -> bool:
    """Independently replay an apparent full witness from recorded transitions.

    No outside oracle is silently consulted: all 54 target edges must exist
    in the actual record. Neither the record nor this check authenticates an
    external source; an externally supplied log can be fabricated.
    """
    if result.status != "FULL_CONJUGACY" or len(result.full_pairs) != 27:
        return False
    table = {(o.state, o.action): o.output for o in result.observed}
    mapping = dict(result.full_pairs)
    if len(table) != 54 or len(mapping) != 27 or set(mapping) != DOMAIN_SET or set(mapping.values()) != DOMAIN_SET:
        return False
    return (mapping.get(source_root) == target_root and
            all(mapping[source.step(s, a)] == table[(mapping[s], a)]
                for s in DOMAIN for a in "AB"))


def main() -> None:
    from ab_chatbot_witness_transport import Shear, ReachedWitness, SourceWitness
    from ab_chatbot_structural_witness import CovariantSource
    phi = (0, 0, 0)
    source = FiniteSystem(phi)
    target = ReachedWitness(SourceWitness.establish(CovariantSource.for_law(phi))).transport(Shear(1))
    partial = discover(source, target.step, full=False)
    exact = discover(source, target.step, full=True)
    print("rooted:", partial.status, partial.rooted_count, "target queries:", partial.calls)
    print("complete:", exact.status, len(exact.full_pairs), "target queries:", exact.calls,
          "extension trials:", exact.attempts, "replay:", verify_recorded_full(source, exact))
    print("Note: no H or shear parameter passed to discover().")


if __name__ == "__main__":
    main()
