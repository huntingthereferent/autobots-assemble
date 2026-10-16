"""Opt-in event-driven continuation through the existing append-only RuntimeJournal.

A verified LOCAL_PASS event (not the assistant's decision to call a selector)
triggers bounded, explicitly authorized source adapters. Actual observation,
not the event label or the planned path, determines supported relations.

This is an in-process *event hook*, not an always-on agent or GitHub adapter.
Recovery deliberately stops at an unobserved started attempt: external actions
may not be safe to retry. The source owner must reconcile that effect first.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.main_referent_selector import Capability, Witness, continue_referent

LOCAL_PASS = 'LOCAL_PASS'
START = 'CONTINUATION_ATTEMPT_STARTED'
OBSERVED = 'CONTINUATION_ATTEMPT_OBSERVED'
OPEN = 'CONTINUATION_BOUNDARY_OPEN'
STOP = 'CONTINUATION_RECOVERY_REQUIRED'


@dataclass(frozen=True)
class SourceAdapter:
    capability: Capability
    execute: Callable[[Capability], object]
    observe_native: Callable[[Capability, object], Witness]


class ObservedEventJournal(RuntimeJournal):
    """Journal with an opt-in callback on LOCAL_PASS, not an external scheduler.

    A normal HandoffRuntime(... event_store=this_journal) need not invoke
    continue_referent explicitly. It emits LOCAL_PASS through the usual append
    surface; this journal performs the next authorized attempt on that call.
    """

    def __init__(self, path: str | Path, *, adapters: tuple[SourceAdapter, ...],
                 verify_local_pass: Callable[[Handoff, HandoffEvent], bool],
                 max_attempts: int = 8):
        if not callable(verify_local_pass):
            raise TypeError('independent local-result event verifier is required')
        if type(max_attempts) is not int or not 1 <= max_attempts <= 64:
            raise ValueError('max_attempts must be 1..64')
        if any(not isinstance(x, SourceAdapter) for x in adapters):
            raise TypeError('source adapters required')
        if len({(x.capability.name, x.capability.edition) for x in adapters}) != len(adapters):
            raise ValueError('duplicate native capability source edition')
        self.adapters = tuple(adapters)
        self.verify_local_pass = verify_local_pass
        self.max_attempts = max_attempts
        self._processing = False
        super().__init__(path)
        # Only replay LOCAL_PASS events for which no reaction was journaled.
        # The source adapter remains separately authorized, and any START
        # without OBSERVED remains blocked rather than running twice.
        self.recover_pending()

    def recover_pending(self) -> tuple[str, ...]:
        """Resume durable local results interrupted *before* native attempt start.

        This is single-writer recovery. An unfinished START is intentionally not
        replayed: it may have caused a real external effect before crashing.
        """
        recovered: list[str] = []
        for trigger in tuple(self._events):
            if trigger.event_type != LOCAL_PASS:
                continue
            # Completion is local to the claimed relation, not to the assistant's
            # decision or a copied success label.
            relation = self._handoffs[trigger.handoff_id].required_relation
            prior = self.for_handoff(trigger.handoff_id)
            if any(e.event_type == OBSERVED and
                   relation in e.data.get('relations_admitted', ()) for e in prior):
                continue
            if any(e.event_type in (START, OBSERVED, OPEN, STOP) and
                   e.data.get('trigger_id') == trigger.event_id for e in prior):
                continue
            self._react(trigger)
            recovered.append(trigger.event_id)
        return tuple(recovered)

    def append(self, event: HandoffEvent) -> HandoffEvent:
        if event.event_type in (START, OBSERVED, OPEN, STOP):
            raise ValueError('continuation records must be emitted by the reactor')
        if any(e.event_id == event.event_id for e in self._events):
            raise ValueError('duplicate journal event identity')
        persisted = super().append(event)
        if event.event_type == LOCAL_PASS and not self._processing:
            self._react(persisted)
        return persisted

    def _emit(self, subject: str, kind: str, data: dict) -> HandoffEvent:
        event = HandoffEvent.create(handoff_id=subject, event_type=kind,
                                    actor_id='observed-continuation', data=data)
        if any(e.event_id == event.event_id for e in self._events):
            raise ValueError('duplicate journal event identity')
        return super().append(event)

    def _react(self, trigger: HandoffEvent) -> None:
        handoff = self._handoffs[trigger.handoff_id]
        # The local PASS is evidence only of a local result, not source-native proof.
        try:
            accepted = self.verify_local_pass(handoff, trigger) is True
        except Exception:
            accepted = False
        if not accepted:
            self._emit(trigger.handoff_id, OPEN, {'cause': 'unverified local-result event',
                                                  'trigger_id': trigger.event_id})
            return
        if self._processing:
            return
        self._processing = True
        try:
            self._advance(handoff, trigger)
        finally:
            self._processing = False

    def _advance(self, handoff: Handoff, trigger: HandoffEvent) -> None:
        # One relation belongs to one native boundary. Composed/independent
        # source joins require their own independently observed handoff.
        subject = handoff.handoff_id
        relation = handoff.required_relation
        # B9 bridge requests pin ONE source edition. An authorized source with
        # the same claimed relation but a different identity is NOT interchangeable.
        # Ordinary, non-B9 handoffs preserve their prior multi-source behavior.
        binding = handoff.metadata.get('continuation_source_binding')
        if binding is not None and (
                not isinstance(binding, dict) or set(binding) != {'name', 'edition'}
                or any(not isinstance(binding[k], str) or not binding[k]
                       for k in ('name', 'edition'))):
            self._emit(subject, OPEN, {'cause': 'invalid source edition binding',
                                       'trigger_id': trigger.event_id})
            return
        existing = self.for_handoff(subject)
        begun = {(e.data['name'], e.data['edition']) for e in existing if e.event_type == START}
        resolved = {(e.data['name'], e.data['edition']) for e in existing if e.event_type == OBSERVED}
        if begun - resolved:
            self._emit(subject, STOP, {'reason': 'native effect uncertain after interrupted attempt',
                                       'unresolved_attempts': sorted([list(i) for i in begun - resolved])})
            return
        supported = any(e.event_type == OBSERVED and relation in e.data.get('relations_admitted', ())
                        for e in existing)
        if supported:
            return
        for _ in range(self.max_attempts):
            existing = self.for_handoff(subject)
            begun = {(e.data['name'], e.data['edition']) for e in existing if e.event_type == START}
            eligible = [a for a in self.adapters if a.capability.authorized
                        and relation in a.capability.claims
                        and (binding is None or
                             (a.capability.name == binding['name']
                              and a.capability.edition == binding['edition']))
                        and (a.capability.name, a.capability.edition) not in begun]
            if not eligible:
                self._emit(subject, OPEN, {'cause': 'no further authorized source editions',
                                           'relation': relation, 'trigger_id': trigger.event_id})
                return
            bindings = {(a.capability.name, a.capability.edition): a for a in eligible}

            def execute(cap: Capability) -> object:
                self._emit(subject, START, {'name': cap.name, 'edition': cap.edition,
                                            'trigger_id': trigger.event_id, 'relation': relation})
                return bindings[(cap.name, cap.edition)].execute(cap)

            def observe(cap: Capability, raw: object) -> Witness:
                return bindings[(cap.name, cap.edition)].observe_native(cap, raw)

            result = continue_referent((relation,), (a.capability for a in eligible),
                                       attempt=execute, observe=observe,
                                       local_passed=True, max_attempts=1)
            movement = result.movements[0]
            self._emit(subject, OBSERVED, {'name': movement.capability,
                        'edition': movement.edition, 'observed': movement.observed,
                        'evidence_ref': movement.evidence_ref,
                        'relations_admitted': list(movement.relations_admitted),
                        'error': movement.error, 'trigger_id': trigger.event_id})
            if result.status == 'CROSSED':
                return
        self._emit(subject, OPEN, {'cause': 'attempt budget exhausted',
                                   'relation': relation, 'trigger_id': trigger.event_id})

    def projection(self, handoff_id: str) -> dict:
        if handoff_id not in self._handoffs:
            raise KeyError(handoff_id)
        relation = self._handoffs[handoff_id].required_relation
        events = self.for_handoff(handoff_id)
        successes = [e for e in events if e.event_type == OBSERVED
                     and relation in e.data.get('relations_admitted', ())]
        starts = {(e.data['name'], e.data['edition']) for e in events if e.event_type == START}
        results = {(e.data['name'], e.data['edition']) for e in events if e.event_type == OBSERVED}
        return {'relation': relation,
                'state': 'CROSSED' if successes else 'RECOVERY_REQUIRED' if starts - results else 'OPEN',
                'attempts_started': len(starts), 'observations': len(results),
                'source_evidence': [e.data['evidence_ref'] for e in successes],
                'handoff_complete': False}
