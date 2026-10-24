"""AnchorMove: keep continuation inside the current finite referent world.

Pure decision function. No execution, worker admission, or fabricated presence.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Kind = Literal["inside", "outside", "blocked"]

@dataclass(frozen=True)
class Move:
    operation: str
    kind: Kind
    evidence: str = ""
    required_for: str = ""

@dataclass(frozen=True)
class World:
    referent: str
    operations: tuple[str, ...]
    retained: tuple[str, ...] = ()
    walls: tuple[str, ...] = ()

def anchor_move(world: World, proposals: tuple[Move, ...]) -> dict:
    """Select an admissible internal move before any external move.

    External movement is admitted only when it is explicitly required for a
    currently registered operation AND no internal candidate is available.
    A blocked operation remains a wall, not a global stop.
    """
    if not world.referent or not world.operations:
        raise ValueError("finite world needs a referent and operations")
    inside = [m for m in proposals if m.kind == "inside" and m.operation in world.operations
              and m.operation not in world.walls]
    if inside:
        m = inside[0]
        return {"decision": "continue_inside", "referent": world.referent,
                "operation": m.operation, "evidence": m.evidence}
    outside = [m for m in proposals if m.kind == "outside"
               and m.required_for in world.operations and m.required_for not in world.walls]
    if outside:
        m = outside[0]
        return {"decision": "external_dependency", "referent": world.referent,
                "operation": m.operation, "required_for": m.required_for}
    return {"decision": "retain_wall", "referent": world.referent,
            "walls": list(world.walls), "retained": list(world.retained)}


def anchored_dispatch(world: World, proposals: tuple[Move, ...], *,
                      internal_handlers: dict[str, object],
                      external_handler=None) -> dict:
    """Invoke an authorized handler only after the finite-world anchor_move decision.

    An external operation is never invoked without an explicit handler.
    The handler owns native authorization, execution, and evidence validation.
    """
    decision = anchor_move(world, proposals)
    if decision["decision"] == "continue_inside":
        handler = internal_handlers.get(decision["operation"])
        if not callable(handler):
            return {**decision, "state": "UNSTAFFED", "executed": False}
        return {**decision, "state": "DISPATCHED", "result": handler(),
                "executed": True}
    if decision["decision"] == "external_dependency":
        if not callable(external_handler):
            return {**decision, "state": "UNSTAFFED", "executed": False}
        return {**decision, "state": "DISPATCHED", "result": external_handler(decision),
                "executed": True}
    return {**decision, "state": "RETAINED", "executed": False}
