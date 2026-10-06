from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .engine import HandoffRuntime
from .handoff import ExecutionResult, Handoff, HandoffState, SimulatedActor


@dataclass(frozen=True)
class SystemEmission:
    system_id: str
    local_ref: str
    handoff: Handoff


@dataclass(frozen=True)
class SystemBinding:
    """Boundary between one system's local state and the shared runtime."""

    system_id: str
    emit_ready: Callable[[], Iterable[SystemEmission]]
    reconcile: Callable[[SystemEmission, HandoffState], None]


@dataclass(frozen=True)
class OrchestrationStep:
    submitted: tuple[str, ...] = ()
    executed: tuple[str, ...] = ()
    reconciled: tuple[str, ...] = ()
    waiting_for_actor: tuple[str, ...] = ()


class Orchestrator:
    """Route handoffs without owning system-local state."""

    def __init__(self, runtime: HandoffRuntime | None = None) -> None:
        self.runtime = runtime or HandoffRuntime()
        self._systems: dict[str, SystemBinding] = {}
        self._actors: dict[str, SimulatedActor] = {}
        self._origins: dict[str, tuple[SystemBinding, SystemEmission]] = {}

    def register_system(self, binding: SystemBinding) -> None:
        if binding.system_id in self._systems:
            raise ValueError(f"system already registered: {binding.system_id}")
        self._systems[binding.system_id] = binding

    def register_actor(self, actor: SimulatedActor) -> None:
        if actor.actor_id in self._actors:
            raise ValueError(f"actor already registered: {actor.actor_id}")
        self._actors[actor.actor_id] = actor

    def _runtime_has(self, handoff_id: str) -> bool:
        try:
            self.runtime.get(handoff_id)
            return True
        except KeyError:
            return False

    def step(self) -> OrchestrationStep:
        submitted: list[str] = []
        executed: list[str] = []
        reconciled: list[str] = []
        waiting: list[str] = []

        for binding in self._systems.values():
            for emission in binding.emit_ready():
                if emission.system_id != binding.system_id:
                    raise ValueError(
                        f"emission system {emission.system_id!r} does not match "
                        f"binding {binding.system_id!r}"
                    )

                handoff = emission.handoff
                already_known = self._runtime_has(handoff.handoff_id)
                if not already_known:
                    self.runtime.submit(handoff)
                    submitted.append(handoff.handoff_id)

                # Rebuild origin routing even when the handoff came from a
                # recovered durable runtime rather than this process.
                self._origins.setdefault(
                    handoff.handoff_id,
                    (binding, emission),
                )

                state = self.runtime.state(handoff.handoff_id)

                # A crash may occur after the runtime accepted a result but
                # before the originating system reconciled it. If that system
                # re-emits the same pending handoff on restart, apply the
                # already-recorded result instead of executing again.
                if already_known and state.status in {
                    "COMPLETE",
                    "PARTIAL",
                    "BLOCKED",
                    "FAILED",
                    "UNKNOWN",
                }:
                    binding.reconcile(emission, state)
                    reconciled.append(handoff.handoff_id)
                    continue

                if state.status != "READY":
                    continue

                actor = self._actors.get(handoff.to_actor)
                if actor is None:
                    waiting.append(handoff.handoff_id)
                    continue

                state = self.runtime.run(handoff.handoff_id, actor)
                executed.append(handoff.handoff_id)
                binding.reconcile(emission, state)

        return OrchestrationStep(
            submitted=tuple(submitted),
            executed=tuple(executed),
            reconciled=tuple(reconciled),
            waiting_for_actor=tuple(waiting),
        )

    def return_result(
        self,
        handoff_id: str,
        *,
        actor_id: str,
        result: ExecutionResult,
    ) -> HandoffState:
        state = self.runtime.return_result(
            handoff_id,
            actor_id=actor_id,
            result=result,
        )
        try:
            binding, emission = self._origins[handoff_id]
        except KeyError as exc:
            raise KeyError(
                f"no system origin registered for handoff {handoff_id}"
            ) from exc

        binding.reconcile(emission, state)
        return state

    def run_until_idle(self, *, max_steps: int = 100) -> tuple[OrchestrationStep, ...]:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")

        steps: list[OrchestrationStep] = []
        for _ in range(max_steps):
            step = self.step()
            steps.append(step)
            if not step.submitted and not step.executed and not step.reconciled:
                return tuple(steps)

        raise RuntimeError(
            f"orchestrator did not become idle within {max_steps} steps"
        )
