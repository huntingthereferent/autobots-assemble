"""Transport a proven finite A/B relation without repeating full transition audit.

Only native, source-owned finite-field laws can produce a positive proof packet.
A caller-supplied black-box is not certified by the source theorem or by anchors.
This is a bounded test of proof reuse, NOT an unrestricted A/B/chatbot engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_structural_witness import (
    CovariantSource, State, add, is_state, reconstruct_known_a,
)

F3 = range(3)
ZERO: State = (0, 0, 0)
E0: State = (1, 0, 0)
E2: State = (0, 0, 1)
E01: State = (1, 1, 0)


@dataclass(frozen=True)
class Shear:
    """Canonical, invertible H_c(i,j,k)=(i,j,k+c*i*j) over F3."""
    c: int

    def __post_init__(self) -> None:
        if type(self.c) is not int or self.c not in F3:
            raise ValueError("shear parameter must be in F3")

    def forward(self, x: State) -> State:
        if not is_state(x):
            raise ValueError("invalid F3^3 point")
        i, j, k = x
        return (i, j, (k + self.c * i * j) % 3)

    def inverse(self, y: State) -> State:
        if not is_state(y):
            raise ValueError("invalid F3^3 point")
        i, j, k = y
        return (i, j, (k - self.c * i * j) % 3)

    def then(self, next_change: "Shear") -> "Shear":
        if not isinstance(next_change, Shear):
            raise TypeError("only native shears can be transported")
        return Shear((self.c + next_change.c) % 3)


@dataclass(frozen=True)
class SourceWitness:
    """Native construction witness, NOT a claimed external-oracle witness."""
    source: CovariantSource
    phi: tuple[int, int, int]
    anchor_record: tuple[tuple[State, str, State], ...]

    @classmethod
    def establish(cls, source: CovariantSource) -> "SourceWitness":
        if type(source) is not CovariantSource:
            raise TypeError("source must be a native CovariantSource")
        result = reconstruct_known_a(source.step, source=source)
        if result.status != "VERIFIED_SOURCE_CONSTRUCTION":
            raise ValueError("source does not meet fixed-A and anchor requirements")
        assert result.phi is not None
        return cls(source, result.phi, result.queries)

    def verify(self) -> None:
        # These checks and the source representation establish the theorem.
        # No claim is made about a separate, arbitrary transition oracle.
        result = reconstruct_known_a(self.source.step, source=self.source)
        if (result.status != "VERIFIED_SOURCE_CONSTRUCTION" or
                result.phi != self.phi or result.queries != self.anchor_record):
            raise ValueError("source proof changed or lost its native witness")


@dataclass(frozen=True)
class ReachedWitness:
    """Same source theorem, carried across a sequence of native correspondences."""
    root: SourceWitness
    changes: tuple[Shear, ...] = ()

    def verify(self) -> None:
        self.root.verify()
        if any(type(change) is not Shear for change in self.changes):
            raise ValueError("a correspondence was not a verified native shear")

    @property
    def shear(self) -> Shear:
        self.verify()
        c = 0
        for change in self.changes:
            c = (c + change.c) % 3
        return Shear(c)

    @property
    def phi(self) -> tuple[int, int, int]:
        self.verify()
        return self.root.phi

    def transport(self, change: Shear) -> "ReachedWitness":
        if type(change) is not Shear:
            raise TypeError("unwitnessed arbitrary coordinate changes are not admitted")
        self.verify()
        return ReachedWitness(self.root, (*self.changes, change))

    def step(self, y: State, action: str) -> State:
        """Source law pushed forward through H; not a sampled external law."""
        h = self.shear
        return h.forward(self.root.source.step(h.inverse(y), action))

    def shift(self, y: State, t: State) -> State:
        """Transported translation H T_t H^-1, not ordinary y -> y+t."""
        h = self.shear
        return h.forward(add(h.inverse(y), t))

    def anchors(self) -> tuple[tuple[State, State], ...]:
        """Push original witnessed B-anchors through the correspondence."""
        h = self.shear
        return tuple((h.forward(point), h.forward(output))
                     for point, action, output in self.root.anchor_record if action == "B")

    def packet(self) -> dict:
        """Recoverable research packet; replay proves only a native model claim."""
        self.verify()
        return {
            "schema": "a-b-native-transport-v1",
            "source_phi": list(self.root.phi),
            "anchor_record": [
                {"state": list(s), "action": a, "result": list(out)}
                for s, a, out in self.root.anchor_record
            ],
            "shear_history": [change.c for change in self.changes],
            "current_shear": self.shear.c,
            "scope": "native-construction-only",
        }

    @classmethod
    def reenter(cls, payload: dict) -> "ReachedWitness":
        """Replay native construction; never authorize an external law by JSON."""
        if type(payload) is not dict or set(payload) != {
                "schema", "source_phi", "anchor_record", "shear_history",
                "current_shear", "scope"}:
            raise ValueError("invalid proof packet fields")
        if (payload["schema"] != "a-b-native-transport-v1" or
                payload["scope"] != "native-construction-only"):
            raise ValueError("unsupported proof packet / source scope")
        raw_phi = payload["source_phi"]
        if (type(raw_phi) is not list or len(raw_phi) != 3 or
                any(type(v) is not int or v not in F3 for v in raw_phi)):
            raise ValueError("invalid source parameter")
        source = CovariantSource.for_law(tuple(raw_phi))
        root = SourceWitness.establish(source)
        if payload["anchor_record"] != [
                {"state": list(s), "action": a, "result": list(out)}
                for s, a, out in root.anchor_record]:
            raise ValueError("source observation history does not replay")
        raw_history = payload["shear_history"]
        if type(raw_history) is not list:
            raise ValueError("invalid shear history")
        changes = tuple(Shear(c) for c in raw_history)
        reached = cls(root, changes)
        if type(payload["current_shear"]) is not int or reached.shear.c != payload["current_shear"]:
            raise ValueError("current correspondence does not replay")
        return reached


@dataclass(frozen=True)
class ExternalCheck:
    status: str  # VERIFIED_AGAINST_NATIVE_TABLE / COUNTEREXAMPLE / UNKNOWN_BUDGET
    calls: int
    witness: tuple[State, str, object, State] | None = None


def check_external(
    reached: ReachedWitness,
    oracle: Callable[[State, str], State],
    *, max_calls: int = 54,
) -> ExternalCheck:
    """No theorem laundering: inspect all 54 transitions of unknown black box."""
    reached.verify()
    if max_calls < 0:
        raise ValueError("negative observation budget")
    calls = 0
    for y in product(F3, repeat=3):
        for action in "AB":
            if calls == max_calls:
                return ExternalCheck("UNKNOWN_BUDGET", calls)
            observed = oracle(y, action)
            calls += 1
            expected = reached.step(y, action)
            if observed != expected:
                return ExternalCheck("COUNTEREXAMPLE", calls, (y, action, observed, expected))
    return ExternalCheck("VERIFIED_AGAINST_NATIVE_TABLE", calls)


def main() -> None:
    source = SourceWitness.establish(CovariantSource.for_law((0, 1, 2)))
    start = ReachedWitness(source)
    first = start.transport(Shear(1))
    second = first.transport(Shear(1))
    third = second.transport(Shear(1))
    for depth, current in enumerate((start, first, second, third)):
        reread = ReachedWitness.reenter(current.packet())
        assert reread.shear.c == depth % 3
        print(f"depth={depth} transported_shear={current.shear.c} "
              f"source_anchors={len(current.root.anchor_record)} "
              f"native_model_replay=VERIFIED")
    y = ZERO
    print("nonlinear coordinates:", first.step((1, 0, 0), "B"),
          "versus ordinary shift of B(0,0,0):", add(first.step(y, "B"), E01))
    print("A/B witnessed under transported translations; "
          "arbitrary external oracle remains UNKNOWN until independently checked")


if __name__ == "__main__":
    main()
