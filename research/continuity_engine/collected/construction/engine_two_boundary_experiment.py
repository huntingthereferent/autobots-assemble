"""Engine 2 mathematical research experiment (not a repository patch).

Implements a bounded independent-coupling family from the existing finite-field
A/B research and a WATCH-limited boundary reader modeled after Boundary Math 0.5.
No claim of unrestricted inverse A/B, autonomous research, or universal closure.
"""
from __future__ import annotations
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from itertools import product
from typing import Literal

Rule = tuple[int, int, int]
State = tuple[int, ...]
RULES: tuple[Rule, ...] = tuple((0, a, b) for a, b in product(range(3), repeat=2))
ZERO: Rule = (0, 0, 0)
IDENTITY: Rule = (0, 1, 2)


@dataclass(frozen=True)
class CouplingLaw:
    """Declared finite-field triangular transformation system."""
    rules: tuple[Rule, ...]

    def __post_init__(self):
        if not self.rules or any(rule not in RULES for rule in self.rules):
            raise ValueError("nonempty sequence of (0,a,b) in F3 required")

    @property
    def depth(self) -> int:
        return len(self.rules) + 2

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, x: State, label: str) -> State:
        if len(x) != self.depth or any(v not in (0, 1, 2) for v in x):
            raise ValueError("state must have the declared F3 depth")
        y = list(x)
        if label == "A":
            y[0] = (x[0] + 1) % 3
        elif label == "B":
            y[1] = (x[1] + x[0] + 1) % 3
            for i, rule in enumerate(self.rules, start=2):
                y[i] = (x[i] + rule[x[i-1]]) % 3
        else:
            raise ValueError("only A and B are declared")
        return tuple(y)

    def inverse(self, x: State, label: str) -> State:
        y = list(x)
        if len(x) != self.depth or any(v not in (0, 1, 2) for v in x):
            raise ValueError("state must have the declared F3 depth")
        if label == "A":
            y[0] = (x[0] - 1) % 3
        elif label == "B":
            y[1] = (x[1] - x[0] - 1) % 3
            for i, rule in enumerate(self.rules, start=2):
                y[i] = (x[i] - rule[y[i-1]]) % 3
        else:
            raise ValueError("only A and B are declared")
        return tuple(y)

    def count_fixed_B(self) -> int:
        return 3 * __import__('math').prod(sum(v == 0 for v in r) for r in self.rules)

    def fixed_B(self) -> frozenset[State]:
        return frozenset(x for x in product(range(3), repeat=self.depth)
                         if self.step(x, "B") == x)

    def rooted_signature(self, max_states: int = 2500) -> tuple[int, ...]:
        """Exact canonical rooted action graph, not fixed-point proxy."""
        indexes = {self.origin: 0}
        queue = [self.origin]
        edges = []
        for state in queue:
            for label in ("A", "B"):
                target = self.step(state, label)
                if target not in indexes:
                    if len(queue) >= max_states:
                        raise RuntimeError("UNKNOWN: graph state budget exhausted")
                    indexes[target] = len(queue)
                    queue.append(target)
                edges.append(indexes[target])
        return tuple(edges)


@dataclass(frozen=True)
class SpaceResult:
    width: int
    descriptions: int
    rooted_classes: int
    distribution: tuple[tuple[int, int], ...]
    fixed_B_counts: tuple[tuple[int, int], ...]
    certificate: str


@dataclass(frozen=True)
class BoundaryWitness:
    """WATCH reading of a native B-fixed-continuation property.

    Both worlds share the EXACT SAME state carrier F3^d. The earned
    correspondence is identity on states, NOT a claimed A/B conjugacy.
    Source/target fixed-state sets are exhaustively compared under this map.
    """
    source_rules: tuple[Rule, ...]
    target_rules: tuple[Rule, ...]
    watch: str
    comparison_rule: str
    lost: tuple[State, ...]
    gained: tuple[State, ...]
    surviving: tuple[State, ...]
    correspondence: tuple[tuple[State, State], ...]
    before_count: int
    after_count: int
    unresolved_before: tuple[State, ...] = ()
    unresolved_after: tuple[State, ...] = ()
    delta_s: int | None = None
    status: str = "UNKNOWN"
    omissions: tuple[str, ...] = (
        "only complete-space B-fixed membership is watched",
        "state-coordinate identity does not establish A/B conjugacy",
    )
    parent_witness: int | None = None

    def summary(self) -> dict:
        return {
            "status": self.status,
            "width": len(self.source_rules),
            "before_fixed_B": self.before_count,
            "after_fixed_B": self.after_count,
            "lost": len(self.lost), "gained": len(self.gained),
            "surviving": len(self.surviving),
            "survival_relation_pairs": len(self.correspondence),
            "omissions": self.omissions,
            "unresolved": (len(self.unresolved_before), len(self.unresolved_after)),
            "delta_s": self.delta_s,
            "parent_witness": self.parent_witness,
            "watch": self.watch,
        }


@dataclass
class Engine2Embryo:
    """Engine 2 owns its research space and witness history; Engine 1 is absent."""
    maximum_full_space: int = 6561
    studies: list[SpaceResult] = field(default_factory=list)
    witnesses: list[BoundaryWitness] = field(default_factory=list)

    def construct_and_classify(self, width: int) -> SpaceResult:
        if not 1 <= width <= 4:
            raise ValueError("exhaustive declared-space research currently width 1..4")
        descriptions = 9 ** width
        if descriptions > self.maximum_full_space:
            raise ValueError("UNKNOWN: declared research budget exceeded")
        class_counts: Counter[tuple[int, ...]] = Counter()
        full_fixed_counts = Counter()
        for rs in product(RULES, repeat=width):
            law = CouplingLaw(tuple(rs))
            class_counts[law.rooted_signature()] += 1
            full_fixed_counts[law.count_fixed_B()] += 1
        sizes = Counter(class_counts.values())
        result = SpaceResult(
            width=width, descriptions=descriptions,
            rooted_classes=len(class_counts),
            distribution=tuple(sorted(sizes.items())),
            fixed_B_counts=tuple(sorted(full_fixed_counts.items())),
            certificate="EXHAUSTIVE_ROOTED_GRAPH_FOR_DECLARED_FAMILY",
        )
        self.studies.append(result)
        return result

    def watch_rule_change(self, prefix: tuple[Rule, ...],
                          before_rule: Rule = ZERO, after_rule: Rule = IDENTITY,
                          *, parent_witness: int | None = None) -> BoundaryWitness:
        if before_rule not in RULES or after_rule not in RULES:
            raise ValueError("only declared F3 coupling rule edits")
        if parent_witness is not None and not (0 <= parent_witness < len(self.witnesses)):
            raise ValueError("no such retained parent witness")
        if len(prefix) > 4 or any(r not in RULES for r in prefix):
            raise ValueError("this WATCH has an explicit bounded-depth contract")
        before = CouplingLaw(prefix + (before_rule,))
        after = CouplingLaw(prefix + (after_rule,))
        fixed_before, fixed_after = before.fixed_B(), after.fixed_B()
        # Native formula and independent complete-state enumeration agree.
        assert len(fixed_before) == before.count_fixed_B()
        assert len(fixed_after) == after.count_fixed_B()
        # Native coordinate identity is earned because every coordinate value
        # has exactly the same meaning in the two explicitly constructed laws.
        survive = fixed_before & fixed_after
        lost = fixed_before - fixed_after
        gain = fixed_after - fixed_before
        status = "BOUNDARY" if lost or gain else "EARNED_ZERO_FOR_FIXED_B_WATCH"
        result = BoundaryWitness(
            source_rules=before.rules, target_rules=after.rules,
            watch="B-fixed-state membership in complete F3 state carrier",
            comparison_rule="native exact B transition and state-set membership",
            lost=tuple(sorted(lost)), gained=tuple(sorted(gain)),
            surviving=tuple(sorted(survive)),
            correspondence=tuple((x, x) for x in sorted(survive)),
            before_count=len(fixed_before), after_count=len(fixed_after),
            delta_s=len(fixed_after) - len(fixed_before), status=status,
            parent_witness=parent_witness,
        )
        self.witnesses.append(result)
        return result

    def follow_witness_into_next_space(self, witness_index: int,
                                       before_rule: Rule = ZERO,
                                       after_rule: Rule = IDENTITY) -> BoundaryWitness:
        """Admit another bounded space ONLY by extending prior constructed law.

        The previous target rules are preserved as an exact prefix. Check
        complete-state A/B projection commuting squares, not conjugacy.
        """
        if not (0 <= witness_index < len(self.witnesses)):
            raise ValueError("witness does not exist")
        prior = self.witnesses[witness_index]
        current = CouplingLaw(prior.target_rules)
        ext = CouplingLaw(prior.target_rules + (before_rule,))
        if len(current.rules) > 4:
            raise ValueError("UNKNOWN: outside admitted experiment depth")
        for x in product(range(3), repeat=ext.depth):
            for a in ("A", "B"):
                if ext.step(x, a)[:-1] != current.step(x[:-1], a):
                    raise AssertionError("witnessed next-space projection broke")
                if ext.inverse(x, a)[:-1] != current.inverse(x[:-1], a):
                    raise AssertionError("inverse projection broke")
        return self.watch_rule_change(prior.target_rules, before_rule, after_rule,
                                      parent_witness=witness_index)


def run_experiment() -> dict:
    engine = Engine2Embryo()
    spaces = [engine.construct_and_classify(n) for n in range(1, 5)]
    first = engine.watch_rule_change((IDENTITY,))
    second = engine.follow_witness_into_next_space(0)
    third = engine.follow_witness_into_next_space(1)
    fourth = engine.follow_witness_into_next_space(2)
    # Distinct coupling laws can earn ZERO for this particular WATCH.
    # They may differ under a different watched property.
    earned_zero = engine.watch_rule_change((IDENTITY,), IDENTITY, (0, 2, 1))
    assert [s.rooted_classes for s in spaces] == [5, 21, 85, 341]
    assert [s.descriptions for s in spaces] == [9, 81, 729, 6561]
    assert [w.status for w in [first, second, third, fourth]] == ["BOUNDARY"] * 4
    assert earned_zero.status == "EARNED_ZERO_FOR_FIXED_B_WATCH"
    return {
        "spaces": [vars(x) for x in spaces],
        "witnesses": [x.summary() for x in engine.witnesses],
        "engine_one_calls": 0,
        "scope": "Finite F3 triangular coupling families; rooted-class and full-space fixed-B WATCH remain distinct",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment(), indent=2))