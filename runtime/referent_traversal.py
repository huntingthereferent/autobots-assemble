"""Referent traversal implementation. Legacy `runtime.ab_loop` imports are aliases.

Names express evidence-preserving movement, not mathematical generators.
"""

from __future__ import annotations


from dataclasses import dataclass
from typing import Any, Callable, Literal
import json


ReferentResultState = Literal["MOVE", "WALL", "UNKNOWN", "PARTIAL"]


@dataclass(frozen=True)
class ReferentFrame:
    """One recoverable position in a recursive referent traversal traversal."""

    referent: str
    direction: str
    current: dict[str, Any]
    survives: tuple[str, ...]
    edge: str
    walls: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    depth: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("referent", self.referent),
            ("direction", self.direction),
            ("edge", self.edge),
        ):
            if not str(value).strip():
                raise ValueError(f"ReferentFrame {name} is required")
        if self.depth < 0:
            raise ValueError("ReferentFrame depth cannot be negative")


@dataclass(frozen=True)
class ReferentMove:
    """Result of one referent traversal pass."""

    state: ReferentResultState
    reached: dict[str, Any]
    survived: tuple[str, ...]
    changed: tuple[str, ...]
    edge: str
    evidence: tuple[str, ...] = ()
    direction: str | None = None
    referent: str | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.state not in {"MOVE", "WALL", "UNKNOWN", "PARTIAL"}:
            raise ValueError(f"unsupported referent traversal result state: {self.state}")
        if not str(self.edge).strip():
            raise ValueError("ReferentMove edge is required")


@dataclass(frozen=True)
class ReferentAgent:
    actor_id: str
    handler: Callable[[ReferentFrame], ReferentMove]

    def move(self, frame: ReferentFrame) -> ReferentMove:
        return self.handler(frame)


@dataclass(frozen=True)
class ReferentStep:
    actor_id: str
    frame: ReferentFrame
    move: ReferentMove
    reground: bool = False
    swallow: bool = False


@dataclass(frozen=True)
class ReferentTraversalResult:
    initial: ReferentFrame
    steps: tuple[ReferentStep, ...]
    final_frame: ReferentFrame
    stop_reason: str

    @property
    def move_count(self) -> int:
        return sum(1 for step in self.steps if step.move.state == "MOVE")

    @property
    def reground_count(self) -> int:
        return sum(1 for step in self.steps if step.reground)

    @property
    def swallow_count(self) -> int:
        return sum(1 for step in self.steps if step.swallow)


def next_frame(frame: ReferentFrame, move: ReferentMove, *, actor_id: str) -> ReferentFrame:
    """Project a MOVE back into the same referent traversal input shape."""

    if move.state != "MOVE":
        raise ValueError("only MOVE can become the next ordinary frame")
    next_direction = move.direction or (
        frame.current.get("prior_direction", frame.direction)
        if frame.current.get("reground")
        else frame.direction
    )
    return ReferentFrame(
        referent=move.referent or frame.referent,
        direction=next_direction,
        current=dict(move.reached),
        survives=tuple(move.survived),
        edge=move.edge,
        walls=frame.walls,
        provenance=(*frame.provenance, f"{actor_id}:MOVE:{frame.edge}"),
        depth=frame.depth + 1,
    )


def wall_frame(frame: ReferentFrame, move: ReferentMove, *, actor_id: str) -> ReferentFrame:
    """Make the stopped relation itself the next referent traversal referent."""

    if move.state == "MOVE":
        raise ValueError("MOVE is not a wall")
    return ReferentFrame(
        referent=frame.referent,
        direction=f"re-establish movement across: {move.edge}",
        current={
            "reground": True,
            "entered": dict(frame.current),
            "stopped_state": move.state,
            "observation": dict(move.reached),
            "changed": list(move.changed),
            "evidence": list(move.evidence),
            "prior_direction": frame.direction,
        },
        survives=tuple(move.survived or frame.survives),
        edge=move.edge,
        walls=frame.walls,
        provenance=(*frame.provenance, f"{actor_id}:{move.state}:{move.edge}"),
        depth=frame.depth,
    )


def failed_reground_frame(
    frame: ReferentFrame,
    move: ReferentMove,
    *,
    actor_id: str,
) -> ReferentFrame:
    """Record a failed reground attempt without changing the wall itself."""

    if not frame.current.get("reground"):
        raise ValueError("failed_reground_frame requires a reground frame")
    current = dict(frame.current)
    attempts = list(current.get("reground_attempts") or ())
    attempts.append(
        {
            "actor_id": actor_id,
            "state": move.state,
            "note": move.note,
            "evidence": list(move.evidence),
        }
    )
    current["reground_attempts"] = attempts
    return ReferentFrame(
        referent=frame.referent,
        direction=frame.direction,
        current=current,
        survives=frame.survives,
        edge=frame.edge,
        walls=frame.walls,
        provenance=(*frame.provenance, f"{actor_id}:{move.state}:reground-attempt"),
        depth=frame.depth,
    )


def swallow_frame(frame: ReferentFrame) -> ReferentFrame:
    """Turn an unresolved WALL/UNKNOWN into an outward-search referent traversal referent."""

    if not frame.current.get("reground"):
        raise ValueError("swallow_frame requires an unresolved reground frame")
    current = dict(frame.current)
    current["swallow"] = True
    current["swallow_goal"] = (
        "find a missing external/native source, system, reference, tool, "
        "workflow, or relation that can close this exact boundary"
    )
    return ReferentFrame(
        referent=frame.referent,
        direction=(
            "SWALLOW FIRST: search outward in native shapes and referent traversal whether "
            f"the reached thing closes this boundary: {frame.edge}"
        ),
        current=current,
        survives=frame.survives,
        edge=frame.edge,
        walls=tuple(
            dict.fromkeys(
                (
                    *frame.walls,
                    "swallow means traverse/connect, not copy external owned state",
                    "do not treat discovery as proof",
                    "do not change the unresolved wall merely to claim progress",
                )
            )
        ),
        provenance=(*frame.provenance, "boundary-route:swallow-first"),
        depth=frame.depth,
    )


def failed_swallow_frame(
    original: ReferentFrame,
    move: ReferentMove,
    *,
    actor_id: str,
) -> ReferentFrame:
    """Record a failed outward search while preserving the exact wall."""

    current = dict(original.current)
    attempts = list(current.get("swallow_attempts") or ())
    attempts.append(
        {
            "actor_id": actor_id,
            "state": move.state,
            "note": move.note,
            "evidence": list(move.evidence),
        }
    )
    current["swallow_attempts"] = attempts
    current["swallow_attempted"] = True
    return ReferentFrame(
        referent=original.referent,
        direction=original.direction,
        current=current,
        survives=original.survives,
        edge=original.edge,
        walls=original.walls,
        provenance=(
            *original.provenance,
            f"{actor_id}:{move.state}:swallow-attempt",
        ),
        depth=original.depth,
    )


def equivalence_signature(
    frame: ReferentFrame,
    *,
    history_sensitive: bool,
) -> str:
    """Return state identity relative to the operations allowed next.

    Forward-only callers may ignore provenance/depth when the future movement
    cannot inspect history. Undo/reopen/reground-style callers must request a
    history-sensitive identity. This is conditional equivalence, not a global
    claim that the states are identical.
    """

    payload: dict[str, Any] = {
        "referent": frame.referent,
        "direction": frame.direction,
        "current": frame.current,
        "survives": frame.survives,
        "edge": frame.edge,
        "walls": frame.walls,
    }
    if history_sensitive:
        payload["provenance"] = frame.provenance
        payload["depth"] = frame.depth
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def equivalent_for(
    left: ReferentFrame,
    right: ReferentFrame,
    *,
    history_sensitive: bool,
) -> bool:
    return equivalence_signature(
        left,
        history_sensitive=history_sensitive,
    ) == equivalence_signature(
        right,
        history_sensitive=history_sensitive,
    )


class ReferentTraversal:
    """Keep applying referent traversal until no available actor can reground a wall."""

    def __init__(
        self,
        agents: tuple[ReferentAgent, ...],
        *,
        swallow_agent: ReferentAgent | None = None,
        max_steps: int = 100,
    ) -> None:
        if not agents:
            raise ValueError("at least one referent traversal agent is required")
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.agents = agents
        self.swallow_agent = swallow_agent
        self.max_steps = max_steps

    def run(self, initial: ReferentFrame) -> ReferentTraversalResult:
        frame = initial
        active_index = 0
        reground_tried: set[int] = set()
        steps: list[ReferentStep] = []

        for _ in range(self.max_steps):
            agent = self.agents[active_index]
            is_reground = bool(reground_tried)
            move = agent.move(frame)
            steps.append(
                ReferentStep(
                    actor_id=agent.actor_id,
                    frame=frame,
                    move=move,
                    reground=is_reground,
                )
            )

            if move.state == "MOVE":
                frame = next_frame(frame, move, actor_id=agent.actor_id)
                reground_tried.clear()
                continue

            if frame.current.get("reground"):
                frame = failed_reground_frame(
                    frame,
                    move,
                    actor_id=agent.actor_id,
                )
            else:
                frame = wall_frame(frame, move, actor_id=agent.actor_id)

                if (
                    move.state in {"WALL", "UNKNOWN"}
                    and self.swallow_agent is not None
                ):
                    outward = swallow_frame(frame)
                    swallow_move = self.swallow_agent.move(outward)
                    steps.append(
                        ReferentStep(
                            actor_id=self.swallow_agent.actor_id,
                            frame=outward,
                            move=swallow_move,
                            reground=True,
                            swallow=True,
                        )
                    )
                    if swallow_move.state == "MOVE":
                        frame = next_frame(
                            outward,
                            swallow_move,
                            actor_id=self.swallow_agent.actor_id,
                        )
                        reground_tried.clear()
                        continue
                    frame = failed_swallow_frame(
                        frame,
                        swallow_move,
                        actor_id=self.swallow_agent.actor_id,
                    )

            reground_tried.add(active_index)

            next_index = None
            for offset in range(1, len(self.agents) + 1):
                candidate = (active_index + offset) % len(self.agents)
                if candidate not in reground_tried:
                    next_index = candidate
                    break

            if next_index is None:
                return ReferentTraversalResult(
                    initial=initial,
                    steps=tuple(steps),
                    final_frame=frame,
                    stop_reason=(
                        "all available agents reached the same unresolved boundary"
                    ),
                )

            active_index = next_index

        return ReferentTraversalResult(
            initial=initial,
            steps=tuple(steps),
            final_frame=frame,
            stop_reason=f"max_steps={self.max_steps} reached",
        )


def frame_to_payload(frame: ReferentFrame) -> dict[str, Any]:
    """Serialize the recoverable referent traversal shape across another system boundary."""

    return {
        "referent": frame.referent,
        "direction": frame.direction,
        "current": dict(frame.current),
        "survives": list(frame.survives),
        "edge": frame.edge,
        "walls": list(frame.walls),
        "provenance": list(frame.provenance),
        "depth": frame.depth,
    }


def frame_from_payload(payload: dict[str, Any]) -> ReferentFrame:
    """Restore an referent traversal frame carried through a task/handoff boundary."""

    return ReferentFrame(
        referent=str(payload["referent"]),
        direction=str(payload["direction"]),
        current=dict(payload.get("current") or {}),
        survives=tuple(payload.get("survives") or ()),
        edge=str(payload["edge"]),
        walls=tuple(payload.get("walls") or ()),
        provenance=tuple(payload.get("provenance") or ()),
        depth=int(payload.get("depth") or 0),
    )


def move_to_payload(move: ReferentMove) -> dict[str, Any]:
    return {
        "state": move.state,
        "reached": dict(move.reached),
        "survived": list(move.survived),
        "changed": list(move.changed),
        "edge": move.edge,
        "evidence": list(move.evidence),
        "direction": move.direction,
        "referent": move.referent,
        "note": move.note,
    }


def move_from_payload(payload: dict[str, Any]) -> ReferentMove:
    return ReferentMove(
        state=str(payload["state"]),
        reached=dict(payload.get("reached") or {}),
        survived=tuple(payload.get("survived") or ()),
        changed=tuple(payload.get("changed") or ()),
        edge=str(payload["edge"]),
        evidence=tuple(payload.get("evidence") or ()),
        direction=payload.get("direction"),
        referent=payload.get("referent"),
        note=str(payload.get("note") or ""),
    )


def render_agent_prompt(frame: ReferentFrame) -> str:
    """Provider-neutral prompt projection for a model-backed worker."""

    lines = [
        "Continue the current referent traversal movement. Do not create a new project plan.",
        f"REFERENT: {frame.referent}",
        f"DIRECTION: {frame.direction}",
        f"CURRENT: {frame.current!r}",
        f"SURVIVES: {frame.survives!r}",
        f"EDGE: {frame.edge}",
    ]
    if frame.walls:
        lines.append(f"WALLS: {frame.walls!r}")
    if frame.provenance:
        lines.append(f"PROVENANCE: {frame.provenance!r}")
    lines.extend(
        (
            "Return one state: MOVE, WALL, UNKNOWN, or PARTIAL.",
            "On MOVE, reached state must be valid input to this same shape again.",
            "If a new relation is required, stop at WALL/UNKNOWN; the runtime will swallow outward first, then reground the same boundary if needed.",
        )
    )
    return "\n".join(lines)
