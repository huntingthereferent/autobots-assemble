"""CP help openings over the EXISTING coordinator/workstation/runtime journal.

An unfinished checkpoint may request assistance without a completed-parent
spawn, which is unsuitable for blocked parents. The known finite-prefilter
adapter demonstrates branching/admitting a child; it is NOT a game-builder.
No second scheduler, new unverified capability, or automatic execution.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from .coordinator_window import CoordinatorIndex, _id
from .workstation import ProcessWorkstation

CAP_FINITE = 'finite-required-edge-prefilter'
CAP_GAME = 'game-engine-build'
_SUPPORTED = {CAP_FINITE}
_OPENING_TYPE = 'cp-worker-help-opening'


def _load(data_dir: str | Path):
    root = Path(data_dir)
    return (CoordinatorIndex(root / 'coordinator-windows.jsonl'),
            HandoffRuntime(event_store=RuntimeJournal(root / 'runtime.jsonl')),
            ProcessWorkstation(root / 'workstation'))


def _opening_id(window: str, lane: str, slot: str, key: str) -> str:
    content = '|'.join((window, lane, slot, key)).encode('utf8')
    return 'cp-help-' + sha256(content).hexdigest()[:32]


def _original(runtime: HandoffRuntime, opening_id: str) -> Handoff:
    h = runtime.get(opening_id)
    if h.metadata.get('source_system') != _OPENING_TYPE:
        raise ValueError('not a CP help opening')
    return h


def _assignment(runtime: HandoffRuntime, opening_id: str) -> dict | None:
    items = [e for e in runtime.event_store.for_handoff(opening_id)
             if e.event_type == 'HELP_ASSIGNED']
    if len(items) > 1:
        raise ValueError('repeated helper assignment')
    return dict(items[0].data) if items else None


def open_help(*, data_dir: str | Path, lane: str, slot: str, capability: str,
              opening_key: str, reason: str, window: str = 'complete-stack') -> dict:
    """An explicit native need opens durable help; it does not birth an agent."""
    lane, slot, window, opening_key = map(_id, (lane, slot, window, opening_key))
    if not isinstance(capability, str) or not capability or len(capability) > 96:
        raise ValueError('named exact capability required')
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
        raise ValueError('specific bounded reason required')
    index, runtime, _ = _load(data_dir)
    _, links = index.definition(window)
    parent = [e for e in links.get(lane, ()) if e['slot'] == slot]
    if len(parent) != 1:
        raise ValueError('help requires an existing exact checkpoint/worker slot')
    # A completed verified CP needs a new opening/branch, not retroactive help.
    oid = _opening_id(window, lane, slot, opening_key)
    values = {'window': window, 'lane': lane, 'slot': slot,
              'capability': capability, 'opening_key': opening_key, 'reason': reason.strip()}
    if oid in runtime.snapshot():
        old = _original(runtime, oid)
        if old.inputs != values:
            raise ValueError('help opening ID already reserved for a different request')
        return help_status(runtime, oid)
    runtime.submit(Handoff(
        handoff_id=oid, referent=f'{window}/{lane}/{slot}: {reason.strip()}',
        from_actor='cp-coordinator', to_actor='capability-router',
        required_relation='match a bounded helper to an unfinished CP',
        inputs=values,
        expected_output={'worker_assigned': 'native source-pinned job, if supported'},
        boundaries=('Opening does not prove a worker exists.',
                    'Unfinished parent never becomes complete due to helper birth.',
                    'No worker executes without exact source-owned controls.'),
        provenance=(f'coordinator-window:{window}', f'parent-slot:{lane}:{slot}'),
        metadata={'source_system': _OPENING_TYPE, **values},
    ))
    return help_status(runtime, oid)


def staff_finite(*, data_dir: str | Path, opening_id: str,
                 parent_version: str, inputs_file: str | Path) -> dict:
    """Branch a real finite edition and admit exactly one bounded worker job.

    Does not execute. Source copy/admission are recoverable across interruptions.
    Only one *registered* capability is allowed by this initial adapter.
    """
    from .process_handoff import WORKER_ID as FINITE_ID
    from .controls import admit_finite
    _, runtime, desk = _load(data_dir)
    h = _original(runtime, opening_id)
    if h.inputs['capability'] != CAP_FINITE:
        raise ValueError('no source-owned adapter registered for this capability')
    already = _assignment(runtime, opening_id)
    if already:
        return help_status(runtime, opening_id)
    parent_version = _id(parent_version)
    info = desk.inspect(worker_id=FINITE_ID, version_id=parent_version)
    # The existing edition is the provenance anchor, never a new invented worker.
    child_version = 'help-' + opening_id[-20:]
    child_job = 'help-job-' + opening_id[-20:]
    try:
        child = desk.branch(worker_id=FINITE_ID, parent_version=parent_version,
                            version_id=child_version)
    except FileExistsError:
        folder, provenance = desk._read(FINITE_ID, child_version)
        if provenance.get('parent_version') != parent_version or provenance.get('source_locator') != desk._read(FINITE_ID,parent_version)[1]['source_locator']:
            raise ValueError('helper edition version collision')
        child = desk.inspect(worker_id=FINITE_ID, version_id=child_version)
    if child.get('source_fingerprint', child.get('current_fingerprint')) != info['current_fingerprint']:
        raise ValueError('helper edition differs from parent source at birth')
    if child_job in runtime.snapshot():
        admitted = runtime.get(child_job)
        if (admitted.metadata.get('worker_id') != FINITE_ID or
            admitted.metadata.get('worker_version') != child_version or
            admitted.metadata.get('edition_fingerprint') != info['current_fingerprint']):
            raise ValueError('conflicting existing helper job')
    else:
        admit_finite(data_dir=data_dir, version_id=child_version,
                     inputs_file=inputs_file, job_id=child_job,
                     confirm_admit=child_job, from_actor='cp-help-coordinator',
                     lane_id=h.inputs['lane'])
    # Durable append-only reference to the genuine native job; never an invented proof.
    runtime = HandoffRuntime(event_store=RuntimeJournal(Path(data_dir) / 'runtime.jsonl'))
    runtime.event_store.append(HandoffEvent.create(
        handoff_id=opening_id, event_type='HELP_ASSIGNED', actor_id='cp-help-coordinator',
        data={'job_id': child_job, 'worker_id': FINITE_ID,
              'version_id': child_version, 'fingerprint': info['current_fingerprint'],
              'parent_version': parent_version},
        parents=(runtime.state(opening_id).last_event_id,)))
    return help_status(runtime, opening_id)


def verify_return(*, data_dir: str | Path, opening_id: str) -> dict:
    """Returns verified finite worker computation, never promotes parent CP."""
    from .controls import reverify_job, job_view
    _, runtime, _ = _load(data_dir)
    _original(runtime, opening_id)
    assigned = _assignment(runtime, opening_id)
    if assigned is None:
        raise ValueError('no native helper to return')
    native = job_view(data_dir=data_dir, job_id=assigned['job_id'])
    if (native['status'] != 'COMPLETE' or native['source_state'] != 'MATCHES_ADMISSION'
        or native['worker_id'] != assigned['worker_id']
        or native['version_id'] != assigned['version_id']
        or native['edition_fingerprint'] != assigned['fingerprint']):
        raise ValueError('helper source or native completion is not current')
    outcome = reverify_job(data_dir=data_dir,job_id=assigned['job_id'])
    if outcome != {'job_id':assigned['job_id'],'status':'COMPLETE',
                   'reverified':True,'executed':False}:
        raise ValueError('native verifier did not confirm source-bound result')
    events = runtime.event_store.for_handoff(opening_id)
    returns = [e for e in events if e.event_type == 'HELP_RETURNED']
    if not returns:
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=opening_id,event_type='HELP_RETURNED',actor_id='cp-help-coordinator',
            data={'job_id':assigned['job_id'], 'native_verifier_confirmed':True,
                  'claim_scope':'finite prefilter computation only'},
            parents=(runtime.state(opening_id).last_event_id,)))
    return help_status(HandoffRuntime(event_store=RuntimeJournal(Path(data_dir)/'runtime.jsonl')),
                       opening_id)


def help_status(runtime: HandoffRuntime, opening_id: str) -> dict:
    h = _original(runtime, opening_id)
    a = _assignment(runtime, opening_id)
    returned = any(e.event_type == 'HELP_RETURNED'
                   for e in runtime.event_store.for_handoff(opening_id))
    return {'opening_id':opening_id,'parent_lane':h.inputs['lane'],
            'parent_slot':h.inputs['slot'],'capability':h.inputs['capability'],
            'reason':h.inputs['reason'],
            'state':'RETURN_RECORDED_REVERIFY_BEFORE_USE' if returned
                   else 'ASSIGNED_NOT_VERIFIED' if a
                   else 'OPEN_UNSTAFFED',
            'registered_capability':h.inputs['capability'] in _SUPPORTED,
            'child':a, 'parent_cp_witnessed':False,
            'note':'Returned finite computation is not a parent-domain proof.'}


def help_summary(data_dir: str | Path) -> list[dict]:
    """Read the same runtime journal; no new persistence or network calls."""
    _, runtime, _ = _load(data_dir)
    return [help_status(runtime, h.handoff_id)
            for h in runtime._handoffs.values()
            if h.metadata.get('source_system') == _OPENING_TYPE]


def main(argv=None):
    ap = argparse.ArgumentParser(description='CP helper birth in existing workstation')
    ap.add_argument('--data-dir', required=True)
    sub = ap.add_subparsers(dest='command', required=True)
    p=sub.add_parser('open')
    p.add_argument('--lane',required=True);p.add_argument('--slot',required=True)
    p.add_argument('--capability',required=True);p.add_argument('--key',required=True)
    p.add_argument('--reason',required=True)
    p=sub.add_parser('staff-finite')
    p.add_argument('--opening-id',required=True);p.add_argument('--parent-version',required=True)
    p.add_argument('--inputs-file',required=True)
    p=sub.add_parser('return')
    p.add_argument('--opening-id',required=True)
    sub.add_parser('status')
    args=ap.parse_args(argv)
    if args.command=='open':
        row=open_help(data_dir=args.data_dir,lane=args.lane,slot=args.slot,
                      capability=args.capability,opening_key=args.key,reason=args.reason)
    elif args.command=='staff-finite':
        row=staff_finite(data_dir=args.data_dir,opening_id=args.opening_id,
                         parent_version=args.parent_version,inputs_file=args.inputs_file)
    elif args.command=='return':
        row=verify_return(data_dir=args.data_dir,opening_id=args.opening_id)
    else:row=help_summary(args.data_dir)
    print(json.dumps(row,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())