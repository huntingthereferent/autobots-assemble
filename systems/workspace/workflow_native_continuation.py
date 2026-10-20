"""Opt-in native actor entry point for the existing Workstation idea frontier.

Wrap one original repository-task HandoffRuntime actor handler. The worker
receives only its source-scoped current-position adapter; every observation
re-reads the live local frontier and addressed help proposals. The wrapper
does not schedule, execute, adopt, merge, backtrack or infer task outcomes.
The original runtime and native result verifier retain authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult, Handoff, SimulatedActor
from .workflow_idea_frontier import IdeaFrontier


@dataclass(frozen=True)
class NativePosition:
    handoff_id: str
    revision: str
    step_id: str


class BoundedWorkerContext:
    """Read and propose only from the one immutable native task handoff."""

    def __init__(self, frontier: IdeaFrontier, runtime: HandoffRuntime,
                 position: NativePosition) -> None:
        self._frontier = frontier
        self._runtime = runtime
        self._position = position

    def observe(self) -> dict:
        """Recheck the source and direct relations on EACH call during work."""
        return self._frontier.native_handoff_frontier(
            self._runtime, handoff_id=self._position.handoff_id,
            revision=self._position.revision, step_id=self._position.step_id)

    def observe_native_results(self) -> dict:
        """Reverify only native results attached to this visible current step
        and source-connected peer steps. This never ranks or executes branches.
        """
        from .workflow_native_frontier_evidence import NativeFrontierEvidence
        return NativeFrontierEvidence(self._frontier).observe(
            runtime=self._runtime, handoff_id=self._position.handoff_id,
            revision=self._position.revision, step_id=self._position.step_id)

    def propose(self, *, kind: str, target_revision: str, reason: str) -> dict:
        """Append a source-checked proposal, not a movement or result."""
        if kind not in {"BACKTRACK", "HELP"}:
            raise ValueError("only first-hop help/backtrack proposals are supported")
        return self._frontier.propose_from_native_handoff(
            self._runtime, handoff_id=self._position.handoff_id,
            revision=self._position.revision, step_id=self._position.step_id,
            target_revision=target_revision, kind=kind, reason=reason)


    def review_help(self, *, proposal_ref: str, decision: str,
                    reason: str) -> dict:
        """Record a decision on help addressed to THIS worker's native step.

        INSPECT means useful to investigate, not a claim that the other
        branch is better. No native reroute or source operation is invoked.
        """
        return self._frontier.review_help_from_native_handoff(
            self._runtime, handoff_id=self._position.handoff_id,
            revision=self._position.revision, step_id=self._position.step_id,
            proposal_ref=proposal_ref, decision=decision, reason=reason)


NativeWorkerHandler = Callable[[Handoff, BoundedWorkerContext], ExecutionResult]


class ScopedRepositoryWorker:
    """Install a capability on the EXISTING actor, not a new scheduler.

    The host owns the handler and must explicitly register/use the returned
    SimulatedActor with the existing runtime or orchestrator. There is no
    automatic worker activation and the label alone is not authentication.
    """

    def __init__(self, *, runtime: HandoffRuntime, frontier: IdeaFrontier,
                 position: NativePosition, handler: NativeWorkerHandler) -> None:
        if not callable(handler):
            raise TypeError("native owner handler is required")
        if not isinstance(position, NativePosition):
            raise TypeError("exact native position is required")
        self.runtime = runtime
        self.frontier = frontier
        self.position = position
        self._handler = handler
        # Check the current immutable task/actor owner AND the branch source
        # before manufacturing any actor capability.
        self.context = BoundedWorkerContext(frontier, runtime, position)
        view = self.context.observe()
        handoff = runtime.get(position.handoff_id)
        if view["native_handoff"]["to_actor"] != handoff.to_actor:
            raise ValueError("native handoff actor differs from current position")
        self.actor_id = handoff.to_actor
        self.required_relation = handoff.required_relation

    def as_actor(self) -> SimulatedActor:
        """A single-handoff actor for the unchanged HandoffRuntime.run API."""
        position = self.position
        context = self.context
        owner = self._handler

        def handle(native: Handoff) -> ExecutionResult:
            if native.handoff_id != position.handoff_id:
                raise ValueError("scoped actor cannot inspect or work on another task")
            view = context.observe()
            if (native.to_actor != view["position"]["worker"]
                    or native.handoff_id != view["native_handoff"]["id"]):
                raise ValueError("source-assigned worker changed")
            result = owner(native, context)
            if not isinstance(result, ExecutionResult):
                raise TypeError("native worker must return an original ExecutionResult")
            return result

        return SimulatedActor(
            actor_id=self.actor_id,
            capabilities=(self.required_relation,),
            handler=handle)

    def run(self, *, allow_native_execution: bool = False):
        """Explicit authorized invocation with a pre-STARTED source check.

        No caller opting into observation alone can start execution. Existing
        native completion witnesses remain checked by HandoffRuntime.
        """
        if allow_native_execution is not True:
            raise PermissionError("explicit native execution authorization required")
        self.context.observe()  # Fail before runtime's STARTED event.
        return self.runtime.run(self.position.handoff_id, self.as_actor())
