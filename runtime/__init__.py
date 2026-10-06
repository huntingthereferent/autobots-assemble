"""Cross-layer handoff runtime.

The runtime executes the repository's existing core.handoff contract.
It is an implementation layer, not A/B itself.
"""

from .handoff import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffEvent,
    HandoffState,
    SimulatedActor,
)
from .engine import EventStore, HandoffRuntime
from .activation import (
    ActivationRegistry,
    ActivationResult,
    ActivationRoute,
    run_activation,
)

__all__ = [
    "EvidenceRecord",
    "ExecutionResult",
    "Handoff",
    "HandoffEvent",
    "HandoffState",
    "SimulatedActor",
    "EventStore",
    "HandoffRuntime",
    "ActivationRegistry",
    "ActivationResult",
    "ActivationRoute",
    "run_activation",
    "SystemEmission",
    "SystemBinding",
    "OrchestrationStep",
    "Orchestrator",
]

from .orchestrator import OrchestrationStep, Orchestrator, SystemBinding, SystemEmission
