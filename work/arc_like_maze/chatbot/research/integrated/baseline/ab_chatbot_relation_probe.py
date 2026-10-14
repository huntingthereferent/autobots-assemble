"""Standalone experiment: mathematical relationship-guided continuation.

Reimplements the finite 3-coordinate A/B example in
https://github.com/huntingthereferent/language-network/blob/main/work/arc_like_maze/math.py
and the rooted-reachable correspondence logic of alignment.py.

This is a bounded *relation probe*, not a chatbot, unrestricted A/B solver,
or evidence of physical/world-level claims. A model is queried only through
'equal outputs after two action words?', a relabeling-invariant observation.
Candidate filtering and choice of next probe occur without an LLM.
"""

from collections import deque
from dataclasses import dataclass
from itertools import product, combinations
from time import perf_counter


@dataclass(frozen=True)
class FiniteSystem:
    phi: tuple[int, int, int]

    def step(self, state: tuple[int, int, int], action: str) -> tuple[int, int, int]:
        x0, x1, x2 = state
        if action == "A":
            return ((x0 + 1) % 3, x1, x2)
        if action == "B":
            return (x0, (x1 + x0 + 1) % 3, (x2 + self.phi[x1]) % 3)
        raise ValueError(action)

    def follow(self, word: str) -> tuple[int, int, int]:
        state = (0, 0, 0)
        for action in word:
            state = self.step(state, action)
        return state

    def equal_ends(self, pair: tuple[str, str]) -> bool:
        return self.follow(pair[0]) == self.follow(pair[1])


def compare_systems(left: FiniteSystem, right: FiniteSystem) -> tuple[str, str] | None:
    """Exact origin-reachable A/B correspondence or two conflicting words.

    If a source state maps inconsistently, or two distinct source states
    collapse under the target map, there is an equality-of-endpoints query
    separating the two systems. No fixed state labels are required by the query.
    """
    origin = (0, 0, 0)
    forward = {origin: origin}
    reverse = {origin: origin}
    word_for = {origin: ""}
    queue = deque([origin])
    while queue:
        source = queue.popleft()
        target = forward[source]
        for a in "AB":
            s_next = left.step(source, a)
            t_next = right.step(target, a)
            new_word = word_for[source] + a
            if s_next in forward:
                if forward[s_next] != t_next:
                    return word_for[s_next], new_word
            elif t_next in reverse:
                return word_for[reverse[t_next]], new_word
            else:
                forward[s_next] = t_next
                reverse[t_next] = s_next
                word_for[s_next] = new_word
                queue.append(s_next)
    return None


def build_probes(systems: tuple[FiniteSystem, ...]) -> tuple[tuple[str, str], ...]:
    probes = set()
    for i, j in combinations(range(len(systems)), 2):
        pair = compare_systems(systems[i], systems[j])
        if pair is not None:
            assert systems[i].equal_ends(pair) != systems[j].equal_ends(pair)
            probes.add(tuple(sorted(pair)))
    return tuple(sorted(probes, key=lambda p: (len(p[0]) + len(p[1]), max(map(len, p)), p)))


def identify(systems: tuple[FiniteSystem, ...], hidden: FiniteSystem, probes: tuple[tuple[str, str], ...]):
    """No target parameter/law is exposed. Only observational equality is returned."""
    remaining = tuple(range(len(systems)))
    observations = []
    while True:
        options = []
        for pair in probes:
            yes = tuple(i for i in remaining if systems[i].equal_ends(pair))
            no = tuple(i for i in remaining if not systems[i].equal_ends(pair))
            if yes and no:
                # Most discriminating worst case, then cheaper action words.
                options.append((max(len(yes), len(no)), abs(len(yes) - len(no)),
                                sum(map(len, pair)), pair))
        if not options:
            return remaining, observations
        *_, pair = min(options)
        observed = hidden.equal_ends(pair)
        remaining = tuple(i for i in remaining if systems[i].equal_ends(pair) == observed)
        observations.append((pair, observed, remaining))


def main():
    t0 = perf_counter()
    systems = tuple(FiniteSystem((0, a, b)) for a, b in product(range(3), repeat=2))
    probes = build_probes(systems)
    groups = []
    unseen = set(range(9))
    while unseen:
        first = min(unseen)
        aligned = {i for i in unseen if compare_systems(systems[first], systems[i]) is None}
        groups.append(sorted(aligned))
        unseen -= aligned
    assert sorted(map(len, groups)) == [1, 2, 2, 2, 2], groups

    results = []
    for hidden_idx, hidden in enumerate(systems):
        remaining, observations = identify(systems, hidden, probes)
        expected = next(g for g in groups if hidden_idx in g)
        assert list(remaining) == expected, (hidden_idx, remaining, expected)
        results.append((hidden_idx, len(observations), remaining))

    print("Scope: 9 finite 3-coordinate candidate systems; origin-reachable labeled A/B")
    print("Exact equivalence classes:", [[systems[i].phi for i in g] for g in groups])
    print("Distinct observational probe pairs:", len(probes))
    print("Queries needed by target:", [(systems[i].phi, n) for i, n, _ in results])
    print("Maximum queries:", max(n for _, n, _ in results))
    demo_idx = 5
    remaining, observations = identify(systems, systems[demo_idx], probes)
    print("Example target:", systems[demo_idx].phi)
    for k, (pair, outcome, candidates) in enumerate(observations, 1):
        print(f"  {k}: compare ends of {pair!r} -> {'SAME' if outcome else 'DIFFERENT'}; ",
              f"remaining={[systems[i].phi for i in candidates]}")
    print("Stop: class resolved CONDITIONALLY on membership in the nine-system grammar")
    outsider = FiniteSystem((1, 0, 0))
    apparent, outsider_observations = identify(systems, outsider, probes)
    print("Negative control (outside grammar):", outsider.phi,
          "has the same measured answers as", [systems[i].phi for i in apparent])
    print("Therefore observed probe answers do NOT establish that an unknown target belongs to the admitted family")
    print(f"Elapsed seconds: {perf_counter() - t0:.4f}")


if __name__ == "__main__":
    main()
