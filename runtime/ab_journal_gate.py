"""A/B journal boundary: A checks admission, B checks emitted state.

These checks concern journal integrity, not mathematical or source truth.
"""
from __future__ import annotations
from dataclasses import dataclass
from .handoff import Handoff, HandoffEvent

@dataclass(frozen=True)
class GateDecision:
    side: str
    admitted: bool
    reason: str

def entry_gate(handoffs: dict[str, Handoff], events: tuple[HandoffEvent, ...], event: HandoffEvent, handoff: Handoff | None = None) -> GateDecision:
    if handoff is not None and (event.event_type != 'CREATED' or event.handoff_id != handoff.handoff_id or handoff.handoff_id in handoffs):
        return GateDecision('A/ENTRY', False, 'invalid submission identity')
    if handoff is None and event.handoff_id not in handoffs:
        return GateDecision('A/ENTRY', False, 'unknown handoff')
    if not event.event_id or not event.actor_id or not event.occurred_at or any(e.event_id == event.event_id for e in events):
        return GateDecision('A/ENTRY', False, 'invalid event identity')
    return GateDecision('A/ENTRY', True, 'admitted structurally; not source authenticated')

def output_gate(handoffs: dict[str, Handoff], events: tuple[HandoffEvent, ...], event: HandoffEvent) -> GateDecision:
    if event.handoff_id not in handoffs or not events or events[-1] != event:
        return GateDecision('B/OUTPUT', False, 'missing terminal event')
    if len({e.event_id for e in events}) != len(events):
        return GateDecision('B/OUTPUT', False, 'duplicate event')
    chain = [e for e in events if e.handoff_id == event.handoff_id]
    if not chain or chain[0].event_type != 'CREATED':
        return GateDecision('B/OUTPUT', False, 'missing origin')
    return GateDecision('B/OUTPUT', True, 'recorded; not semantic proof')
