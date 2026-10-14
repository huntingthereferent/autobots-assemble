"""Prefer a source-pinned worker edition for one explicitly confirmed NEW job.

The preferred record is a source selection, NOT permission to run, a witness
for future work, or an implicit job admission. Native source replay is required.
This local-file protocol is not a concurrent multi-user transaction boundary.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.factory.system import FactorySystem
from .workstation import ProcessWorkstation, _safe_id
from .promotion import PreferredEditions
from .finite_verifier import validate_inputs
from .process_handoff import (CorrespondenceWorkBridge, WORKER_ID as FINITE,
                              VERIFIER as FINITE_VERIFIER, RELATION as FINITE_RELATION)
from .factory_machine_bridge import (FactoryMachineSimulationBridge, WORKER_ID as FACTORY,
                                     VERIFIER as FACTORY_VERIFIER)

SUPPORTED = frozenset((FINITE, FACTORY))


def checked_selection(*, data_dir: str | Path, worker_id: str,
                      confirm_selection: str | None = None) -> dict[str, Any]:
    """Recheck selected edition AND its native supporting result, without execution."""
    if worker_id not in SUPPORTED:
        raise ValueError('unsupported preferred worker')
    root = Path(data_dir).resolve()
    ledger = PreferredEditions(root / 'preferred_editions.jsonl')
    selected = ledger.current().get(worker_id)
    if selected is None:
        raise ValueError('no preferred edition selected for this worker')
    if confirm_selection is not None and confirm_selection != selected['event_id']:
        raise PermissionError('preferred selection changed: confirm exact event ID')
    desk = ProcessWorkstation(root / 'workstation')
    info = desk.inspect(worker_id=worker_id, version_id=selected['version_id'])
    if info['current_fingerprint'] != selected['source_fingerprint']:
        raise ValueError('preferred edition source changed: selection is stale')
    runtime = HandoffRuntime(event_store=RuntimeJournal(root / 'runtime.jsonl'))
    job_id = selected['supporting_job_id']
    handoff = runtime.get(job_id)
    metadata = handoff.metadata
    native_verifier = FINITE_VERIFIER if worker_id == FINITE else FACTORY_VERIFIER
    if (runtime.state(job_id).status != 'COMPLETE'
            or selected['native_verifier'] != native_verifier
            or metadata.get('native_evidence_verifier') != native_verifier
            or metadata.get('worker_id') != worker_id
            or metadata.get('worker_version') != selected['version_id']
            or metadata.get('edition_fingerprint') != selected['source_fingerprint']
            or handoff.required_relation != selected['required_relation']
            or (metadata.get('source_system') != 'process-workstation'
                if worker_id == FINITE else
                not (metadata.get('source_system') == 'factory' and
                     metadata.get('workstation_worker') is True))):
        raise ValueError('selection supporting job or native capability does not match')
    if worker_id == FINITE:
        if handoff.required_relation != FINITE_RELATION:
            raise ValueError('unsupported finite preference capability')
        bridge = CorrespondenceWorkBridge(runtime=runtime, workstation=desk)
    else:
        if metadata.get('stage') != 'machine':
            raise ValueError('unsupported Factory preference stage')
        bridge = FactoryMachineSimulationBridge(runtime=runtime, workstation=desk)
    bridge.reverify(job_id)
    # Catch preference replacement and source mutation across native replay.
    if ledger.current().get(worker_id, {}).get('event_id') != selected['event_id']:
        raise ValueError('preferred selection changed during revalidation')
    if desk.inspect(worker_id=worker_id, version_id=selected['version_id'])['current_fingerprint'] != selected['source_fingerprint']:
        raise ValueError('preferred source changed during revalidation')
    return {'worker_id':worker_id, 'version_id':selected['version_id'],
            'selection_event_id':selected['event_id'],
            'source_fingerprint':selected['source_fingerprint'],
            'supporting_job_id':job_id, 'native_verifier':native_verifier,
            'supporting_job_reverified':True, 'admitted':False, 'executed':False}


def admit_preferred_finite(*, data_dir: str | Path, inputs: dict,
                           job_id: str, confirm_admit: str, confirm_selection: str,
                           from_actor: str, lane_id: str = '') -> dict:
    """A NEW finite job, never an inherited result. Requires exact confirmations."""
    _safe_id(job_id)
    if confirm_admit != job_id:
        raise PermissionError('confirm-admit must match new job ID')
    if not from_actor or not from_actor.strip():
        raise ValueError('from-actor required')
    canonical = validate_inputs(inputs)
    root = Path(data_dir).resolve()
    preference = checked_selection(data_dir=root, worker_id=FINITE,
                                   confirm_selection=confirm_selection)
    runtime = HandoffRuntime(event_store=RuntimeJournal(root / 'runtime.jsonl'))
    if job_id in runtime.snapshot():
        raise ValueError('new job ID already exists')
    if job_id == preference['supporting_job_id']:
        raise ValueError('new job cannot reuse the supporting job')
    bridge = CorrespondenceWorkBridge(runtime=runtime,
                                     workstation=ProcessWorkstation(root / 'workstation'))
    # A copy and preference are never an authority to execute. Admit READY only.
    handoff = bridge.admit(version_id=preference['version_id'], inputs=canonical,
                          from_actor=from_actor, lane_id=lane_id, job_id=job_id,
                          selection_event_id=preference['selection_event_id'])
    if handoff.metadata['edition_fingerprint'] != preference['source_fingerprint']:
        raise ValueError('admitted edition fingerprint differs from selected source')
    return {'job_id':job_id, 'worker_id':FINITE, 'version_id':preference['version_id'],
            'selection_event_id':preference['selection_event_id'],
            'source_fingerprint':preference['source_fingerprint'],
            'status':runtime.state(job_id).status, 'executed':False,
            'supporting_job_id':preference['supporting_job_id']}


def admit_preferred_factory(*, data_dir: str | Path, order_id: str,
                            confirm_handoff: str, confirm_selection: str) -> dict:
    """Bind an existing source-owned pending machine stage; no invented orders."""
    root = Path(data_dir).resolve()
    preference = checked_selection(data_dir=root, worker_id=FACTORY,
                                   confirm_selection=confirm_selection)
    factory_path = root / 'factory_orders.jsonl'
    if not factory_path.is_file():
        raise ValueError('Factory order journal is unavailable')
    factory = FactorySystem(factory_path)
    order = factory.order(order_id)
    handoff = factory.pending_handoff(order_id)
    if order.stage_index != 1 or handoff is None or handoff.metadata.get('stage') != 'machine':
        raise ValueError('Factory has no source-owned pending machine stage')
    if handoff.handoff_id != confirm_handoff:
        raise PermissionError('confirm-handoff must match Factory pending job ID')
    runtime = HandoffRuntime(event_store=RuntimeJournal(root / 'runtime.jsonl'))
    if handoff.handoff_id in runtime.snapshot():
        raise ValueError('Factory machine handoff already admitted')
    bridge = FactoryMachineSimulationBridge(runtime=runtime,
                                            workstation=ProcessWorkstation(root / 'workstation'))
    supply_id = f'factory-{order_id}-01-supply'
    if supply_id not in runtime.snapshot() or runtime.state(supply_id).status != 'COMPLETE':
        raise ValueError('native Factory supply must already be recorded complete')
    bridge.native.reverify(supply_id)
    marked = bridge.admit(handoff, version_id=preference['version_id'],
                          selection_event_id=preference['selection_event_id'])
    if marked.metadata['edition_fingerprint'] != preference['source_fingerprint']:
        raise ValueError('admitted factory edition fingerprint differs from selected source')
    return {'job_id':handoff.handoff_id, 'worker_id':FACTORY,
            'version_id':preference['version_id'],
            'selection_event_id':preference['selection_event_id'],
            'source_fingerprint':preference['source_fingerprint'],
            'status':runtime.state(handoff.handoff_id).status, 'executed':False,
            'supporting_job_id':preference['supporting_job_id']}
