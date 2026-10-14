"""Bounded admission extension for the A/B relation probe.

Run beside ab_chatbot_relation_probe.py with:
    python ab_chatbot_admission_probe.py

All positive claims assume the explicitly declared state domain F_3^3.
Rooted endpoint equality alone cannot certify an unknown full-state law.
This is not a general chatbot or an unbounded A/B theorem.
"""

from collections import Counter
from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem, build_probes, compare_systems, identify

State = tuple[int, int, int]
STATES = tuple(product(range(3), repeat=3))


@dataclass(frozen=True)
class Admission:
    status: str  # VERIFIED_27_GRAMMAR / OUTSIDE_27_GRAMMAR / UNKNOWN_BUDGET
    inferred_phi: tuple[int, ...]
    calls: int
    mismatch: tuple | None = None


def check_full_state_law(
    observe_step: Callable[[State, str], State], *, max_calls: int = 54
) -> Admission:
    """Certify a supplied black-box transition oracle on ALL 27 named states.

    The promise is a total deterministic oracle F_3^3 x {A,B} -> F_3^3.
    Check its complete, labeled transition table before claiming membership.
    At most 54 distinct transitions are queried. A query-cap wall is UNKNOWN.
    """
    if max_calls < 0:
        raise ValueError("max_calls must be nonnegative")
    cache: dict[tuple[State, str], State] = {}

    def read(s: State, action: str):
        key = (s, action)
        if key not in cache:
            if len(cache) >= max_calls:
                return None
            actual = observe_step(s, action)
            cache[key] = actual
        return cache[key]

    phi = []
    for index in range(3):
        source = (0, index, 0)
        observed = read(source, "B")
        if observed is None:
            return Admission("UNKNOWN_BUDGET", tuple(phi), len(cache))
        if (not isinstance(observed, tuple) or len(observed) != 3 or
                any(type(v) is not int or v not in (0, 1, 2) for v in observed)):
            return Admission("OUTSIDE_27_GRAMMAR", tuple(phi), len(cache),
                             (source, "B", observed, "valid F_3^3 state"))
        if observed[:2] != (0, (index + 1) % 3):
            return Admission("OUTSIDE_27_GRAMMAR", tuple(phi), len(cache),
                             (source, "B", observed, (0, (index + 1) % 3, "phi")))
        phi.append(observed[2])

    candidate = FiniteSystem(tuple(phi))
    for s in STATES:
        for a in "AB":
            observed = read(s, a)
            if observed is None:
                return Admission("UNKNOWN_BUDGET", tuple(phi), len(cache))
            expected = candidate.step(s, a)
            if observed != expected:
                return Admission("OUTSIDE_27_GRAMMAR", tuple(phi), len(cache),
                                 (s, a, observed, expected))
    return Admission("VERIFIED_27_GRAMMAR", tuple(phi), len(cache))


def membership_query(target: FiniteSystem) -> bool:
    """Exact 9-of-27 gate ONLY assuming the input already follows this grammar."""
    return target.equal_ends(("AA", "AAB"))


class OffOrbitAlteration:
    """Agrees with phi=(0,0,0) on every origin-reachable state.

    On x2=1 or 2, B swaps the third coordinate. This is a permutation and
    cannot be expressed as B of any fixed phi(x1) in the declared grammar.
    """
    base = FiniteSystem((0, 0, 0))

    def step(self, state: State, action: str) -> State:
        output = self.base.step(state, action)
        if action == "B" and output[2] in (1, 2):
            return (output[0], output[1], 3 - output[2])
        return output

    def follow(self, word: str) -> State:
        state = (0, 0, 0)
        for action in word:
            state = self.step(state, action)
        return state

    def equal_ends(self, words: tuple[str, str]) -> bool:
        return self.follow(words[0]) == self.follow(words[1])


def main() -> None:
    candidates = tuple(FiniteSystem(p) for p in product(range(3), repeat=3))
    probes = build_probes(candidates)
    classes: list[tuple[FiniteSystem, ...]] = []
    for system in candidates:
        if not any(compare_systems(group[0], system) is None for group in classes):
            classes.append(tuple(other for other in candidates
                                 if compare_systems(system, other) is None))
    assert len(classes) == 14 and sorted(map(len, classes)) == [1] + [2] * 13
    assert len(probes) == 6

    lengths = []
    for system in candidates:
        remaining, questions = identify(candidates, system, probes)
        expected = next(group for group in classes if system in group)
        assert tuple(candidates[i] for i in remaining) == expected
        lengths.append(len(questions))
    assert min(lengths) == 3 and max(lengths) == 5

    gate = Counter((p[0] == 0, membership_query(FiniteSystem(p))) for p in product(range(3), repeat=3))
    assert gate == {(True, True): 9, (False, False): 18}

    for system in candidates:
        result = check_full_state_law(system.step)
        assert result.status == "VERIFIED_27_GRAMMAR"
        assert result.inferred_phi == system.phi
        assert result.calls == 54

    changed = OffOrbitAlteration()
    assert all(changed.follow(w) == changed.base.follow(w)
               for n in range(9) for tup in product("AB", repeat=n) for w in ("".join(tup),))
    rejection = check_full_state_law(changed.step)
    assert rejection.status == "OUTSIDE_27_GRAMMAR"
    assert rejection.mismatch[0] == (0, 0, 1)
    assert check_full_state_law(candidates[0].step, max_calls=53).status == "UNKNOWN_BUDGET"

    print("27 explicit finite-field transformation laws, 14 exact rooted classes")
    print("6 separating probe pairs; autonomous questions per member:", dict(sorted(Counter(lengths).items())))
    print("AA vs AAB gate: 9/9 admitted and 18/18 excluded under the 27-law premise")
    print("Full-state validation: all 27 laws verified after 54 distinct transition queries")
    print("Off-orbit altered law: rooted equality cannot expose it; full-state rejection:", rejection.mismatch)
    print("Budget 53: UNKNOWN_BUDGET (not an inferred proof)")


if __name__ == "__main__":
    main()
