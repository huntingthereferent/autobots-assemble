"""Shared observe/move interface over the existing finite A/B modules.

The harness normalizes the shape of observations, not their mathematical
meaning. Native family classifiers remain authoritative. Cross-family
comparisons are UNKNOWN unless a dedicated bridge supplies a witness.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine_one import (
    ConstructedEngine, InverseConstructionEngine, RelationWitness, Requirements,
    _tower_witness, _window_witness,
)
from .third_coupling import CouplingTower, count_fixed_B_formula, rooted_graph
from .window_combined import CombinedWorld, classify_pair

WORDS = ("B", "BBB", "AABAB", "ABABAB")


@dataclass(frozen=True)
class Observation:
    family: str
    version: int
    law: str
    scope: str
    fixed_word_counts: tuple[tuple[str, int], ...] = ()
    fixed_B_count: int | None = None
    rooted_state_count: int | None = None
    root: tuple[int, ...] | None = None


@dataclass(frozen=True)
class Comparison:
    status: str
    source_family: str
    target_family: str
    witness_kind: str | None
    evidence: tuple[str, ...]
    witness: RelationWitness | None = None


@dataclass(frozen=True)
class Movement:
    status: str
    previous_version: int
    next_version: int | None
    witness_kinds: tuple[str, ...]
    wall: str | None
    result: Any


class ObserveMoveHarness:
    """Common observation and movement entry point; no cross-family guessing."""

    def __init__(self, constructor: InverseConstructionEngine | None = None):
        self.constructor = constructor or InverseConstructionEngine()

    @staticmethod
    def _family(law: object) -> str:
        if isinstance(law, CombinedWorld):
            return "window48"
        if isinstance(law, CouplingTower):
            return "coupling_tower"
        return "unsupported"

    def observe(self, engine: ConstructedEngine) -> Observation:
        law = engine.law
        family = self._family(law)
        if isinstance(law, CombinedWorld):
            counts = tuple((word, law.fixed_word(word, depth=3)) for word in WORDS)
            return Observation(
                family, engine.version, repr(law),
                "complete F3^3 state space; fixed-word counts at depth 3",
                fixed_word_counts=counts, root=(0, 0, 0),
            )
        if isinstance(law, CouplingTower):
            graph = rooted_graph(law)
            return Observation(
                family, engine.version, repr(law),
                f"complete state space F3^{law.depth}; fixed-B formula and exact root-reachable graph",
                fixed_B_count=count_fixed_B_formula(law),
                rooted_state_count=graph.states, root=law.origin,
            )
        raise TypeError("harness has no observation adapter for this law type")

    def compare(self, source: ConstructedEngine, target: ConstructedEngine) -> Comparison:
        """Use native witnesses; never infer equivalence from matching summaries."""
        left, right = self._family(source.law), self._family(target.law)
        if left == "unsupported" or right == "unsupported":
            return Comparison("UNKNOWN", left, right, None,
                              ("no native adapter for one or both law types",))
        if left != right:
            return Comparison(
                "UNKNOWN", left, right, None,
                ("cross-family bridge not admitted",
                 "different observation schemas do not imply equivalence or inequivalence",
                 "a bridge must supply its own independently checked witness"),
            )
        if isinstance(source.law, CombinedWorld) and isinstance(target.law, CombinedWorld):
            native = classify_pair(source.law, target.law)
            witness = _window_witness(source.law, target.law)
            if native.kind is None:
                return Comparison("OBSTRUCTED_FULL_STATE", left, right,
                                  witness.kind, witness.evidence, witness)
            status = "EQUIVALENT_ROOTED" if native.root_preserving else "EQUIVALENT_UNROOTED"
            return Comparison(status, left, right, witness.kind, witness.evidence, witness)
        if isinstance(source.law, CouplingTower) and isinstance(target.law, CouplingTower):
            witness = _tower_witness(source.law, target.law)
            if witness is None:
                return Comparison(
                    "UNKNOWN", left, right, None,
                    ("no admitted one-step relation witness for this pair",
                     "absence of a witness is not an inequivalence proof"),
                )
            statuses = {
                "ROOTED_FULL": "EQUIVALENT_ROOTED",
                "FULL_UNROOTED": "EQUIVALENT_UNROOTED",
                "ROOTED_REACHABLE": "EQUIVALENT_ROOTED_REACHABLE_ONLY",
                "FULL_OBSTRUCTED": "OBSTRUCTED_FULL_STATE",
                "ROOTED_OBSTRUCTED": "DIFFERENT_ROOTED_FULL_UNKNOWN",
                "PROJECTION": "PROJECTION_ONLY",
            }
            return Comparison(statuses.get(witness.kind, "UNKNOWN"), left, right,
                              witness.kind, witness.evidence, witness)
        return Comparison("UNKNOWN", left, right, None,
                          ("family type did not match its native adapter",))

    def move(self, engine: ConstructedEngine, requirements: Requirements) -> Movement:
        """Attempt one native movement and preserve its exact witnesses."""
        result = engine.evolve(self.constructor, requirements)
        if result.status != "CONSTRUCTED" or result.engine is None:
            return Movement("WALL", engine.version, None, (), result.wall, result)
        new = result.engine
        added = new.history[len(engine.history):]
        return Movement("MOVED", engine.version, new.version,
                        tuple(w.kind for w in added), None, result)
