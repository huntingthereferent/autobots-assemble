"""Opt-in, witness-gated agent lineage over the existing handoff runtime.

This is orchestration, NOT an implementation of A/B. ``evaluate`` and
``admit_closure`` are supplied by a real comparator or a marked simulation.
The original activation registry remains a read-only projection for its
existing routes. Routes intended to start a lineage must explicitly opt in
with projection='agent_lineage'.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable
from uuid import NAMESPACE_URL, uuid5

from .activation import ActivationRegistry
from .engine import HandoffRuntime
from .handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffEvent, HandoffState, SimulatedActor
from .swallow_first import SwallowFirstBoundary


@dataclass(frozen=True)
class AgentMove:
    """Caller-supplied comparison result; none of these strings prove A/B."""

    result: ExecutionResult
    next_referent: str = ""
    closes: tuple[str, ...] = ()
    closure_evidence: tuple[EvidenceRecord, ...] = ()
    closure_birth_referent: str = ""


@dataclass(frozen=True)
class LineageStep:
    executed: tuple[str, ...] = ()
    born: tuple[str, ...] = ()
    closed: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


Evaluator = Callable[[Handoff, HandoffState], AgentMove]
ClosureAdmitter = Callable[[Handoff, Handoff, tuple[EvidenceRecord, ...]], bool]


class AgentLineage:
    """Sequential bounded scheduler; supports overlapping OPEN lineage states.

    Agents have independent execution and loop closure. COMPLETE means this
    agent returned an admitted result, not that its loop is closed. A later
    descendant may close an ancestor when a caller-supplied closure admission
    accepts the evidence. Closure may admit another distinct work referent.
    """

    _CONTROL = "_agent_lineage"

    def __init__(
        self,
        runtime: HandoffRuntime,
        registry: ActivationRegistry,
        *,
        evaluate: Evaluator | None = None,
        admit_closure: ClosureAdmitter | None = None,
        boundary: SwallowFirstBoundary | None = None,
        max_births: int = 16,
        allow_simulation: bool = True,
    ) -> None:
        if max_births < 1:
            raise ValueError("max_births must be positive")
        if boundary is not None and boundary.runtime is not runtime:
            raise ValueError("swallow boundary must share the lineage runtime")
        self.runtime = runtime
        self.registry = registry
        self.evaluate = evaluate
        self.admit_closure = admit_closure
        self.boundary = boundary
        self.max_births = max_births
        self.allow_simulation = allow_simulation

    @staticmethod
    def _id(*parts: str) -> str:
        return "agent_" + uuid5(NAMESPACE_URL, "|".join(parts)).hex

    def _members(self, root: str) -> tuple[Handoff, ...]:
        return tuple(
            self.runtime.get(hid) for hid in self.runtime.snapshot()
            if self.runtime.get(hid).metadata.get("lineage_root") == root
            and self.runtime.get(hid).metadata.get("agent_lineage") is True
        )

    def activate(self, surface: str, *, actor_id: str, instance_id: str,
                 referent: str | None = None) -> str | None:
        """Exactly one agent per explicit activation instance; never mutate ohayo."""
        route = self.registry.resolve(surface, actor_id=actor_id)
        if route is None or route.projection != "agent_lineage":
            return None
        if not instance_id.strip():
            raise ValueError("instance_id is required for replay-safe activation")
        if referent is not None and not referent.strip():
            raise ValueError("referent cannot be blank")
        chosen_referent = referent.strip() if referent is not None else route.referent
        root = self._id("activation", route.activation_id, actor_id.strip().casefold(), instance_id)
        if root in self.runtime.snapshot():
            existing = self.runtime.get(root)
            if existing.referent != chosen_referent:
                raise ValueError("activation instance already bound to another referent")
        else:
            self.runtime.submit(Handoff(
                handoff_id=root, referent=chosen_referent,
                from_actor=actor_id, to_actor="agent-ab",
                required_relation="A/B compare admitted referent",
                required_witnesses=("movement witness",),
                admissible_evidence={"movement witness": (
                    ("simulation", "measurement", "source") if self.allow_simulation
                    else ("measurement", "source")
                )},
                boundaries=route.boundaries,
                provenance=route.provenance,
                metadata={"agent_lineage": True, "lineage_root": root,
                          "birth_parent": "", "generation": 1, "birth_reason": "activation",
                          "activation_id": route.activation_id},
            ))
        return root

    def _ancestors(self, child: Handoff) -> tuple[Handoff, ...]:
        ancestors: list[Handoff] = []
        parent_id = str(child.metadata.get("birth_parent") or "")
        seen: set[str] = set()
        while parent_id:
            if parent_id in seen:
                raise ValueError("cycle detected in agent ancestry")
            seen.add(parent_id)
            parent = self.runtime.get(parent_id)
            ancestors.append(parent)
            parent_id = str(parent.metadata.get("birth_parent") or "")
        return tuple(ancestors)

    def _closed(self, target_id: str) -> bool:
        return any(e.event_type == "AGENT_LOOP_CLOSED"
                   for e in self.runtime.event_store.for_handoff(target_id))

    def loop_status(self, agent_id: str) -> str:
        self.runtime.get(agent_id)
        return "CLOSED" if self._closed(agent_id) else "OPEN"

    def _apply(self, agent: Handoff) -> LineageStep:
        state = self.runtime.state(agent.handoff_id)
        data = state.output.get(self._CONTROL)
        if state.status != "COMPLETE" or not isinstance(data, dict):
            return LineageStep(unresolved=(agent.handoff_id,) if state.status in ("UNKNOWN", "BLOCKED", "PARTIAL", "FAILED") else ())

        closed: list[str] = []
        approved_closures: list[str] = []
        ancestors = {h.handoff_id: h for h in self._ancestors(agent)}
        closure_evidence = tuple(EvidenceRecord(**item)
                                 for item in data.get("closure_evidence", ()))
        for target_id in data.get("closes", ()):
            target = ancestors.get(target_id)
            if target is None:
                continue  # No cross-lineage or self-closure.
            events = self.runtime.event_store.for_handoff(target_id)
            prior = next((e for e in events if e.event_type == "AGENT_LOOP_CLOSED"), None)
            if prior is not None:
                # A durable admission survives restart even if the verifier is offline.
                # Only the original closing agent and identical evidence may resume.
                if prior.data.get("closed_by") == agent.handoff_id and prior.evidence == closure_evidence:
                    approved_closures.append(target_id)
                continue
            if self.admit_closure is None or not closure_evidence:
                continue  # Evidence syntax alone never admits closure.
            if not self.admit_closure(agent, target, closure_evidence):
                continue
            parent = events[-1].event_id if events else ""
            self.runtime.event_store.append(HandoffEvent.create(
                handoff_id=target_id,
                event_type="AGENT_LOOP_CLOSED",
                actor_id=agent.handoff_id,
                data={"closed_by": agent.handoff_id, "reason": "admitted descendant comparison"},
                evidence=closure_evidence,
                parents=(parent, state.last_event_id) if parent else (state.last_event_id,),
            ))
            closed.append(target_id)
            approved_closures.append(target_id)

        births: list[str] = []
        candidates = []
        if data.get("next_referent"):
            candidates.append(("result", data["next_referent"]))
        if approved_closures and data.get("closure_birth_referent"):
            candidates.append(("closure", data["closure_birth_referent"]))
        for reason, next_ref in candidates:
            ref = str(next_ref).strip()
            if not ref:
                continue
            child_id = self._id("child", agent.handoff_id, reason, ref)
            if child_id in self.runtime.snapshot():
                continue
            if len(self._members(agent.metadata["lineage_root"])) >= self.max_births:
                break
            # Identical referent+identical received payload is not fresh work.
            if any(
                older.referent == ref and older.inputs.get("parent_output") == state.output
                for older in (*self._ancestors(agent), agent)
            ):
                continue
            child = Handoff(
                handoff_id=child_id, referent=ref,
                from_actor=agent.handoff_id, to_actor="agent-ab",
                required_relation=agent.required_relation,
                inputs={"parent_output": state.output, "parent_evidence": [
                    {"source": e.source, "ref": e.ref, "kind": e.kind, "depth": e.depth}
                    for e in state.evidence
                ]},
                expected_output=agent.expected_output,
                required_witnesses=agent.required_witnesses,
                admissible_evidence=agent.admissible_evidence,
                provenance=tuple(dict.fromkeys((*agent.provenance, agent.handoff_id))),
                boundaries=agent.boundaries,
                metadata={"agent_lineage": True,
                          "lineage_root": agent.metadata["lineage_root"],
                          "birth_parent": agent.handoff_id,
                          "generation": int(agent.metadata["generation"]) + 1,
                          "birth_reason": reason,
                          "activation_id": agent.metadata["activation_id"]},
            )
            # COMPLETE parent uses runtime.spawn, other statuses cannot birth.
            self.runtime.spawn(agent.handoff_id, child)
            births.append(child_id)
        return LineageStep(born=tuple(births), closed=tuple(closed))

    def step(self, root: str) -> LineageStep:
        """Process one eligible agent; safe to call again after a restart."""
        members = self._members(root)
        if not members:
            raise KeyError(f"no agent lineage: {root}")
        for agent in members:
            state = self.runtime.state(agent.handoff_id)
            executed: tuple[str, ...] = ()
            if state.status == "READY" and self.evaluate is not None:
                decision = self.evaluate(agent, state)
                if not isinstance(decision, AgentMove):
                    raise TypeError("agent evaluator must return AgentMove")
                if self._CONTROL in decision.result.output:
                    raise ValueError("reserved output key: _agent_lineage")
                # Fail before STARTED so invalid COMPLETE cannot strand ACTIVE.
                if decision.result.status == "COMPLETE":
                    self.runtime._validate_complete_evidence(agent, decision.result.evidence)
                control = {
                    "next_referent": decision.next_referent,
                    "closes": list(dict.fromkeys(decision.closes)),
                    "closure_evidence": [asdict(e) for e in decision.closure_evidence],
                    "closure_birth_referent": decision.closure_birth_referent,
                }
                result = ExecutionResult(
                    status=decision.result.status,
                    output={**decision.result.output, self._CONTROL: control},
                    evidence=decision.result.evidence,
                    note=decision.result.note,
                )
                self.runtime.run(agent.handoff_id, SimulatedActor(
                    actor_id="agent-ab", capabilities=(agent.required_relation,),
                    handler=lambda _h, r=result: r,
                ))
                executed = (agent.handoff_id,)
                if self.boundary is not None and result.status in {"BLOCKED", "UNKNOWN"}:
                    self.boundary.resolve(agent.handoff_id)
            applied = self._apply(agent)
            if executed or applied.born or applied.closed:
                return LineageStep(
                    executed=executed, born=applied.born, closed=applied.closed,
                    unresolved=applied.unresolved,
                )
        return LineageStep()

    def submit_move(self, agent_id: str, move: AgentMove, *, actor_id: str) -> LineageStep:
        """Accept an externally produced A/B result through the durable handoff.

        Neither a JSON result nor a source locator proves an A/B conclusion;
        descendant loop closure still needs an independent admission callback.
        """
        agent = self.runtime.get(agent_id)
        if agent.metadata.get("agent_lineage") is not True:
            raise ValueError("target is not an agent-lineage handoff")
        if not actor_id.strip():
            raise ValueError("result actor is required")
        if not isinstance(move, AgentMove):
            raise TypeError("result must be AgentMove")
        if self._CONTROL in move.result.output:
            raise ValueError("reserved lineage output key")
        state = self.runtime.state(agent_id)
        if state.status != "READY":
            raise ValueError(f"agent result already recorded or not ready: {state.status}")
        if move.result.status == "COMPLETE":
            self.runtime._validate_complete_evidence(agent, move.result.evidence)
            witnesses = [e for e in move.result.evidence if e.condition == "movement witness"]
            if not all(e.ref.strip() and e.source.strip() and
                       e.depth != "simulated" and e.kind != "simulation" for e in witnesses):
                raise ValueError("live movement requires non-simulated witness with native ref")
        control = {
            "next_referent": move.next_referent,
            "closes": list(dict.fromkeys(move.closes)),
            "closure_evidence": [asdict(e) for e in move.closure_evidence],
            "closure_birth_referent": move.closure_birth_referent,
        }
        result = ExecutionResult(
            status=move.result.status,
            output={**move.result.output, self._CONTROL: control},
            evidence=move.result.evidence,
            note=move.result.note,
        )
        # Fail evidence validation before STARTED, so invalid results remain READY.
        self.runtime.event_store.append(HandoffEvent.create(
            handoff_id=agent_id, event_type="STARTED", actor_id=actor_id,
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        self.runtime.return_result(agent_id, actor_id=actor_id, result=result)
        if self.boundary is not None and result.status in {"BLOCKED", "UNKNOWN"}:
            self.boundary.resolve(agent_id)
        applied = self._apply(agent)
        return LineageStep(executed=(agent_id,), born=applied.born,
                           closed=applied.closed, unresolved=applied.unresolved)

    def reconcile_completed(self) -> None:
        """Resume saved closure/birth transitions; never rerun the evaluator."""
        roots = set(h.metadata.get("lineage_root") for h in self.runtime._handoffs.values()
                    if h.metadata.get("agent_lineage") is True)
        for root in roots:
            for _ in range(self.max_births + 1):
                births = 0
                for agent in self._members(root):
                    if self.runtime.state(agent.handoff_id).status == "COMPLETE":
                        births += len(self._apply(agent).born)
                if births == 0:
                    break

    def run_until_idle(self, root: str, *, max_steps: int = 64) -> tuple[LineageStep, ...]:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        steps: list[LineageStep] = []
        for _ in range(max_steps):
            step = self.step(root)
            if not (step.executed or step.born or step.closed):
                return tuple(steps)
            steps.append(step)
        raise RuntimeError("agent lineage exceeded max_steps; remaining work preserved")
