"""Engine 2 embryo: independently choose supported finite-field Boundary Math WATCHes.

Experimental local integration, not a general A/B theorem or autonomous research.
Combines the witnessed coupling-space construction in engine_two_boundary_experiment
with independent native tests of three different mathematical distinctions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Literal

from engine_two_boundary_experiment import (
    CouplingLaw, Engine2Embryo, BoundaryWitness, Rule, State, RULES, ZERO, IDENTITY,
)

Watch = Literal["AUTO", "ROOTED", "FIXED_B", "TRANSITIONS", "PROJECTION"]


def _word(law: CouplingLaw, actions: str) -> State:
    state = law.origin
    for letter in actions:
        state = law.step(state, letter)
    return state


@dataclass(frozen=True)
class RootCollision:
    """Two positive action words demonstrating failure of a rooted isomorphism."""
    old_word: str
    new_word: str
    source_old: State
    source_new: State
    target_old: State
    target_new: State
    collision_on: str  # source or target

    def verify(self, source: CouplingLaw, target: CouplingLaw) -> bool:
        if (self.source_old, self.source_new) != (_word(source, self.old_word), _word(source, self.new_word)):
            return False
        if (self.target_old, self.target_new) != (_word(target, self.old_word), _word(target, self.new_word)):
            return False
        if self.collision_on == "source":
            return self.source_old == self.source_new and self.target_old != self.target_new
        if self.collision_on == "target":
            return self.target_old == self.target_new and self.source_old != self.source_new
        return False


@dataclass(frozen=True)
class RootedReading:
    status: str
    watch: str
    native_rule: str
    before_rules: tuple[Rule, ...]
    after_rules: tuple[Rule, ...]
    before_reachable: int
    after_reachable: int
    state_correspondence: tuple[tuple[State, State], ...]
    obstruction: RootCollision | None
    unresolved: tuple[str, ...]
    omissions: tuple[str, ...]

    def summary(self) -> dict:
        d = {"watch": self.watch, "status": self.status,
             "before_reachable": self.before_reachable,
             "after_reachable": self.after_reachable,
             "correspondence_size": len(self.state_correspondence),
             "unresolved": list(self.unresolved), "omissions": list(self.omissions)}
        if self.obstruction is not None:
            d["obstruction"] = vars(self.obstruction)
        return d


def rooted_watch(before: CouplingLaw, after: CouplingLaw, *, max_reachable: int = 2500) -> RootedReading:
    """Exact rooted conjugacy or explicit collision; UNKNOWN on budget exhaustion.

    The BFS transports each pair of origin-generated states via the SAME A/B
    word. A repeated state must have the same partner in both directions.
    """
    if max_reachable < 1:
        raise ValueError("positive reachable-state budget required")
    if before.depth != after.depth:
        raise ValueError("ROOTED WATCH requires equal depths in this experiment")
    forward = {before.origin: (after.origin, "")}
    reverse = {after.origin: (before.origin, "")}
    queue = [(before.origin, after.origin, "")]
    for left, right, prefix in queue:
        for action in 'AB':
            a, b = before.step(left, action), after.step(right, action)
            word = prefix + action
            if a in forward and forward[a][0] != b:
                old_b, old_word = forward[a]
                collision = RootCollision(old_word, word, a, a, old_b, b, "source")
                assert collision.verify(before, after)
                return RootedReading("ROOTED_OBSTRUCTED", "rooted A/B continuation",
                    "action-word collision under proposed root transport",
                    before.rules, after.rules, len(forward), len(reverse),
                    tuple((x, v[0]) for x, v in forward.items()), collision, (),
                    ("rooted obstruction does not rule out unpointed full-state conjugacy",))
            if b in reverse and reverse[b][0] != a:
                old_a, old_word = reverse[b]
                collision = RootCollision(old_word, word, old_a, a, b, b, "target")
                assert collision.verify(before, after)
                return RootedReading("ROOTED_OBSTRUCTED", "rooted A/B continuation",
                    "action-word collision under proposed root transport",
                    before.rules, after.rules, len(forward), len(reverse),
                    tuple((x, v[0]) for x, v in forward.items()), collision, (),
                    ("rooted obstruction does not rule out unpointed full-state conjugacy",))
            if a not in forward and b not in reverse:
                if len(forward) >= max_reachable:
                    return RootedReading("UNKNOWN_BUDGET", "rooted A/B continuation",
                        "incomplete rooted generator graph comparison",
                        before.rules, after.rules, len(forward), len(reverse),
                        tuple((x, v[0]) for x, v in forward.items()), None,
                        ("reachable-state budget exhausted",),
                        ("no negative or positive conjugacy certificate",))
                forward[a] = (b, word)
                reverse[b] = (a, word)
                queue.append((a, b, word))
    # Every outgoing labeled edge of the complete paired reachable graphs was checked.
    for a, (b, _) in forward.items():
        for label in 'AB':
            assert forward[before.step(a, label)][0] == after.step(b, label)
    return RootedReading("ROOTED_EQUIVALENT", "rooted A/B continuation",
        "exhaustive mutual bijection and A/B generator squares on origin-reachable graphs",
        before.rules, after.rules, len(forward), len(reverse),
        tuple((x, v[0]) for x, v in forward.items()), None, (),
        ("root-reachable isomorphism is not full-state conjugacy",))


@dataclass(frozen=True)
class TransitionReading:
    status: str
    watch: str
    native_rule: str
    changed_A: int
    changed_B: int
    total_carrier_states: int
    sample_changes: tuple[tuple[State, str, State, State], ...]
    unresolved: tuple[str, ...]
    omissions: tuple[str, ...]

    def summary(self) -> dict:
        return {"watch": self.watch, "status": self.status,
                "changed_A": self.changed_A, "changed_B": self.changed_B,
                "total_carrier_states": self.total_carrier_states,
                "sample_changes": self.sample_changes,
                "unresolved": self.unresolved, "omissions": self.omissions}


def transition_watch(before: CouplingLaw, after: CouplingLaw,
                     *, max_carrier_states: int = 2200) -> TransitionReading:
    """WATCH exact labeled maps under identity coordinate correspondence.

    Different concrete arrows are *not* proof of abstract nonconjugacy.
    """
    if before.depth != after.depth:
        raise ValueError("TRANSITIONS WATCH requires equal state carriers")
    size = 3 ** before.depth
    if size > max_carrier_states:
        return TransitionReading("UNKNOWN_BUDGET", "labeled generator tables",
            "pointwise A/B transition comparison", 0, 0, size, (),
            ("full carrier exceeds declared enumeration budget",),
            ("no decision reached",))
    a_differ, b_differ, example = 0, 0, []
    for state in product(range(3), repeat=before.depth):
        for gen in 'AB':
            left, right = before.step(state, gen), after.step(state, gen)
            if left != right:
                if gen == 'A':
                    a_differ += 1
                else:
                    b_differ += 1
                if len(example) < 4:
                    example.append((state, gen, left, right))
    return TransitionReading(
        "LABELED_ARROWS_DIFFER" if a_differ or b_differ else "EARNED_ZERO_FOR_TRANSITIONS_WATCH",
        "labeled generator tables", "exhaustive pointwise labeled transition equality on identical carrier",
        a_differ, b_differ, size, tuple(example), (),
        ("changes in concrete generator tables do not disprove an abstract conjugacy",))


def fixed_B_watch(before: CouplingLaw, after: CouplingLaw,
                 *, max_carrier_states: int = 2200) -> BoundaryWitness:
    if before.depth != after.depth:
        raise ValueError("FIXED_B WATCH requires equal state carriers")
    if 3 ** before.depth > max_carrier_states:
        raise ValueError("UNKNOWN: FIXED_B full-state enumeration budget exceeded")
    old = before.fixed_B()
    new = after.fixed_B()
    if len(old) != before.count_fixed_B() or len(new) != after.count_fixed_B():
        raise AssertionError("independently enumerated B-fixed sets disagree with native formula")
    surviving, lost, gained = old & new, old-new, new-old
    return BoundaryWitness(
        source_rules=before.rules, target_rules=after.rules,
        watch="complete-space B-fixed membership",
        comparison_rule="native B generator fixed-point equation on identical F3 carrier",
        lost=tuple(sorted(lost)), gained=tuple(sorted(gained)),
        surviving=tuple(sorted(surviving)),
        correspondence=tuple((x, x) for x in sorted(surviving)),
        before_count=len(old), after_count=len(new), delta_s=len(new)-len(old),
        status="BOUNDARY" if lost or gained else "EARNED_ZERO_FOR_FIXED_B_WATCH",
        omissions=("identity correspondence is only for a B-fixed membership WATCH",
                   "does not establish complete labeled A/B conjugacy"),
    )


@dataclass(frozen=True)
class ProjectionReading:
    status: str
    watch: str
    native_rule: str
    source_depth: int
    target_depth: int
    new_coordinate_fiber: int | None
    checked_state_actions: int
    unresolved: tuple[str, ...]
    omissions: tuple[str, ...]

    def summary(self) -> dict:
        return vars(self)


def projection_watch(before: CouplingLaw, after: CouplingLaw,
                     *, max_carrier_states: int = 2200) -> ProjectionReading:
    if len(after.rules) != len(before.rules)+1 or after.rules[:-1] != before.rules:
        return ProjectionReading("WALL_UNADMITTED_EXTENSION", "dimension-dropping projection",
            "one independently appended rule with unchanged prefix required",
            before.depth, after.depth, None, 0,
            ("no proven constructor along this exact pair",),
            ("no claim about arbitrary cross-family projections",))
    count = 3 ** after.depth
    if count > max_carrier_states:
        return ProjectionReading("UNKNOWN_BUDGET", "dimension-dropping projection",
            "native triangular forward and inverse projection squares",
            before.depth, after.depth, None, 0,
            ("projection audit exceeds full carrier budget",),
            ("algebraic statement may be true; not verified by this execution",))
    for state in product(range(3), repeat=after.depth):
        for gen in 'AB':
            if after.step(state, gen)[:-1] != before.step(state[:-1], gen):
                raise AssertionError("forward projection square does not commute")
            if after.inverse(state, gen)[:-1] != before.inverse(state[:-1], gen):
                raise AssertionError("inverse projection square does not commute")
    return ProjectionReading("PROJECTION_PRESERVED", "dimension-dropping projection",
        "all A/B and inverse generator squares checked on complete target carrier",
        before.depth, after.depth, 3, 2*count, (),
        ("three-to-one state projection is NOT bijective conjugacy",
         "projection preserves transitions, not all higher-coordinate distinctions"))


@dataclass(frozen=True)
class DeferredReading:
    """A WATCH not performed because the native evidence budget was exceeded."""
    status: str
    watch: str
    native_rule: str
    unresolved: tuple[str, ...]
    omissions: tuple[str, ...]

    def summary(self) -> dict:
        return vars(self)


@dataclass(frozen=True)
class ResearchFinding:
    source_rules: tuple[Rule, ...]
    target_rules: tuple[Rule, ...]
    request: Watch
    selection_reason: str
    readings: tuple[object, ...]
    parent_id: int | None
    status: str
    unresolved: tuple[str, ...]
    remainder: tuple[str, ...]

    def summary(self) -> dict:
        return {"request": self.request, "selection_reason": self.selection_reason,
                "status": self.status, "source_rules": self.source_rules,
                "target_rules": self.target_rules, "parent_id": self.parent_id,
                "readings": [r.summary() for r in self.readings],
                "unresolved": self.unresolved, "remainder": self.remainder}


@dataclass
class Engine2ResearchKernel(Engine2Embryo):
    """Research WATCH selection and witnessed continuation are owned by Engine 2.

    AUTO is deterministic evidence-oriented scheduling, not AI/planning.
    The finite field F3 law grammar remains explicitly limited.
    """
    findings: list[ResearchFinding] = field(default_factory=list)
    maximum_state_carrier: int = 2200

    def investigate(self, before: CouplingLaw, after: CouplingLaw,
                    watch: Watch = "AUTO", *, parent_id: int | None = None,
                    rooted_budget: int = 2500) -> ResearchFinding:
        if watch not in ("AUTO", "ROOTED", "FIXED_B", "TRANSITIONS", "PROJECTION"):
            raise ValueError("only supported native WATCH types are admitted")
        if parent_id is not None:
            if not 0 <= parent_id < len(self.findings):
                raise ValueError("unknown parent finding")
            if self.findings[parent_id].target_rules != before.rules:
                raise ValueError("reentry must preserve its parent finding's target law")
        if watch == "PROJECTION" or (watch == "AUTO" and after.depth != before.depth):
            reading = projection_watch(before, after, max_carrier_states=self.maximum_state_carrier)
            readings = (reading,)
            selection = "dimension change: test admitted extension and full projection squares"
        elif before.depth != after.depth:
            raise ValueError("requested WATCH needs the same complete state carrier")
        elif watch == "ROOTED":
            readings = (rooted_watch(before, after, max_reachable=rooted_budget),)
            selection = "explicitly WATCH the origin-reachable labeled A/B relation"
        elif watch == "FIXED_B":
            readings = (fixed_B_watch(before, after, max_carrier_states=self.maximum_state_carrier),)
            selection = "explicitly WATCH complete-space fixed-B membership"
        elif watch == "TRANSITIONS":
            readings = (transition_watch(before, after, max_carrier_states=self.maximum_state_carrier),)
            selection = "explicitly WATCH exact generator arrows on identical coordinate carrier"
        else:
            # On equal carriers, rooted agreement alone does not detect dormant
            # higher-coordinate distinctions. Inspect both contracts, then
            # transition arrows to make representation-level differences visible.
            readings = (
                rooted_watch(before, after, max_reachable=rooted_budget),
                fixed_B_watch(before, after, max_carrier_states=self.maximum_state_carrier)
                if 3 ** before.depth <= self.maximum_state_carrier else
                DeferredReading("UNKNOWN_BUDGET", "complete-space B-fixed membership",
                    "native B generator fixed-point equation on identical F3 carrier",
                    ("full carrier exceeds stated membership enumeration budget",),
                    ("native count formula exists but complete state correspondence not enumerated",)),
                transition_watch(before, after, max_carrier_states=self.maximum_state_carrier),
            )
            selection = "AUTO: rooted relation + complete fixed-B when bounded + concrete labeled arrows"
        statuses = [r.status for r in readings]
        unresolved = tuple(msg for r in readings for msg in getattr(r, "unresolved", ()))
        remainder = []
        if "ROOTED_EQUIVALENT" in statuses and "BOUNDARY" in statuses:
            remainder.append("rooted continuation matches but complete-space B-fixed distinction differs")
        if "ROOTED_EQUIVALENT" in statuses and "LABELED_ARROWS_DIFFER" in statuses:
            remainder.append("pointwise arrows differ although rooted dynamics admit a bijective alignment")
        if any(s.startswith("UNKNOWN") for s in statuses):
            state = "PARTIAL_OR_UNKNOWN"
        elif any(s.startswith("WALL") for s in statuses):
            state = "WALL"
        elif any(s in ("BOUNDARY", "ROOTED_OBSTRUCTED", "LABELED_ARROWS_DIFFER") for s in statuses):
            state = "WATCHED_DIFFERENCE"
        else:
            state = "EARNED_LOCAL_PRESERVATION"
        result = ResearchFinding(before.rules, after.rules, watch,
                                 selection, readings, parent_id, state,
                                 unresolved, tuple(remainder))
        self.findings.append(result)
        return result

    def extend_from_finding(self, finding_id: int,
                            before_rule: Rule = ZERO, after_rule: Rule = IDENTITY,
                            *, watch: Watch = "AUTO") -> tuple[ResearchFinding, ResearchFinding]:
        """Use target law as prior space, check extension, then compare two branches.

        No Engine 1 import or call; no manufactured full-state conjugacy.
        """
        if not 0 <= finding_id < len(self.findings):
            raise ValueError("no such prior mathematical finding")
        if before_rule not in RULES or after_rule not in RULES:
            raise ValueError("invalid proposed extension rule")
        current = CouplingLaw(self.findings[finding_id].target_rules)
        candidate1 = CouplingLaw(current.rules + (before_rule,))
        candidate2 = CouplingLaw(current.rules + (after_rule,))
        projected = self.investigate(current, candidate1, "PROJECTION", parent_id=finding_id)
        if projected.status != "EARNED_LOCAL_PRESERVATION":
            raise ValueError("UNKNOWN: extension projection has not been earned")
        # The second extension has the same unchanged prefix; audit independently.
        other_projection = projection_watch(current, candidate2,
                                            max_carrier_states=self.maximum_state_carrier)
        if other_projection.status != "PROJECTION_PRESERVED":
            raise ValueError("UNKNOWN: competing branch projection not earned")
        compared = self.investigate(candidate1, candidate2, watch, parent_id=len(self.findings)-1)
        return projected, compared


def run_research() -> dict:
    kernel = Engine2ResearchKernel()
    # Watch one same-width pair from different vantage points.
    dormant = CouplingLaw((ZERO, ZERO))
    active = CouplingLaw((ZERO, IDENTITY))
    first = kernel.investigate(dormant, active)
    # Another pair: fixed B sets unchanged, concrete B arrow changes.
    second = kernel.investigate(CouplingLaw((IDENTITY, IDENTITY)),
                                CouplingLaw((IDENTITY, (0,2,1))))
    # Continue from the first result into two independently proven extensions.
    projected, third = kernel.extend_from_finding(0)
    return {"cases": [f.summary() for f in (first, second, projected, third)],
            "engine_one_calls": 0,
            "scope": "Finite F3 CouplingLaw; distinct native WATCHes and witnessed one-step extensions"}


if __name__ == "__main__":
    import json
    print(json.dumps(run_research(), indent=2))