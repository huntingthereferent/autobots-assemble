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

__all__ = [
    "EvidenceRecord",
    "ExecutionResult",
    "Handoff",
    "HandoffEvent",
    "HandoffState",
    "SimulatedActor",
    "EventStore",
    "HandoffRuntime",
]
