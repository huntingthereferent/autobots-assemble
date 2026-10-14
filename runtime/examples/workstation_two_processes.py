"""Opt-in persistent demonstration of two different source-pinned workstation jobs.

Run once with --execute; running again replays/reverifies without duplicate
jobs. No physical device, general autonomous agent or external service is run.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.store import WorkspaceStore
from systems.workspace.monitor import workstation_snapshot
from systems.workspace.process_handoff import (CorrespondenceWorkBridge,
                                                WORKER_ID as FCP_ID)
from systems.workspace.factory_machine_bridge import (FactoryMachineSimulationBridge,
                                                       WORKER_ID as FACTORY_ID)
from systems.factory import FactorySystem, default_simulated_actors
from systems.factory.simulated import FactorySimulationAdmission

REPO = Path(__file__).resolve().parents[2]
FCP_SOURCE = REPO / 'work' / 'arc_like_maze' / 'chatbot'
FACTORY_WORKER_SOURCE = REPO / 'systems' / 'workspace' / 'factory_machine_worker.py'
FCP_INPUTS = {'old_phi': [0, 0, 1], 'new_phi': [0, 0, 0],
              'candidate_words': [['ABAA', 'ABBABA'], ['ABAA', 'AAABB', 'BAAAB']],
              'required_state': [0, 0, 0], 'required_action': 'B'}
FCP_JOB = 'workstation-demo-finite-001'
ORDER_ID = 'WORKSTATION-DEMO-001'
FCP_VERSION = 'baseline-001'
FACTORY_VERSION = 'machine-001'


def _copy_once(desk: ProcessWorkstation, selected: Path, *, worker_id: str,
               version_id: str):
    """Never overwrite or silently rebase an existing private edition."""
    try:
        existing = desk.inspect(worker_id=worker_id, version_id=version_id)
    except KeyError:
        desk.copy_source(selected, worker_id=worker_id, version_id=version_id)
    else:
        if existing['current_fingerprint'] != existing['baseline_fingerprint']:
            raise ValueError('persistent demo edition changed: use a new version, not overwrite')


def _seed_lanes(journal: Path):
    ws = WorkspaceStore(journal)
    present = {x.lane_id for x in ws.lanes()}
    if 'finite-correspondence' not in present:
        ws.open_lane('finite-correspondence', label='Finite Correspondence Process',
                     actor_id='james', referent='finite required-edge prefilter',
                     sources=('work/arc_like_maze/chatbot/PROCESS.md',))
    if 'factory-simulation' not in present:
        ws.open_lane('factory-simulation', label='Factory machine simulation',
                     actor_id='james', referent='simulated machine stage',
                     sources=('systems/factory/simulated.py',))
    if ws.focused_lane() is None:
        ws.set_focus('finite-correspondence')
    return ws


def populate(data_dir: str | Path, *, execute: bool = False) -> dict:
    if not execute:
        raise PermissionError('populating and executing workers requires --execute')
    data = Path(data_dir).resolve()
    # Guard against editing the source repository as a data directory.
    if data == REPO or REPO.is_relative_to(data):
        raise ValueError('data_dir must not contain the source repository')
    data.mkdir(parents=True, exist_ok=True)
    desk = ProcessWorkstation(data / 'workstation')
    source = data / 'demo-selected-sources'
    finite = source / 'finite'
    machine = source / 'factory-machine'
    finite.mkdir(parents=True, exist_ok=True)
    machine.mkdir(parents=True, exist_ok=True)
    for name in ('finite_goal_priority.py', 'finite_required_edge_guard.py'):
        src = FCP_SOURCE / name
        target = finite / name
        if not target.exists():
            shutil.copyfile(src, target)
        elif target.read_bytes() != src.read_bytes():
            raise ValueError('selected finite source has changed; refusing silent recopy')
    target = machine / 'factory_machine_worker.py'
    if not target.exists():
        shutil.copyfile(FACTORY_WORKER_SOURCE, target)
    elif target.read_bytes() != FACTORY_WORKER_SOURCE.read_bytes():
        raise ValueError('selected Factory source has changed; refusing silent recopy')
    _copy_once(desk, finite, worker_id=FCP_ID, version_id=FCP_VERSION)
    _copy_once(desk, machine, worker_id=FACTORY_ID, version_id=FACTORY_VERSION)
    try:
        desk.inspect(worker_id=FCP_ID, version_id='experiment-001')
    except KeyError:
        desk.branch(worker_id=FCP_ID, parent_version=FCP_VERSION,
                    version_id='experiment-001')
    workspace = _seed_lanes(data / 'workspace.jsonl')
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / 'runtime.jsonl'))
    fcp = CorrespondenceWorkBridge(runtime=runtime, workstation=desk)
    factory_bridge = FactoryMachineSimulationBridge(runtime=runtime, workstation=desk)

    if FCP_JOB not in runtime.snapshot():
        fcp.admit(version_id=FCP_VERSION, inputs=FCP_INPUTS,
                  from_actor='workstation-demo', lane_id='finite-correspondence',
                  job_id=FCP_JOB)
    if runtime.state(FCP_JOB).status == 'READY':
        fcp.execute(FCP_JOB, allow_local_execution=True)
    if not fcp.reverify(FCP_JOB):
        raise ValueError('finite computation did not reverify')

    factory = FactorySystem(data / 'factory_orders.jsonl')
    if ORDER_ID not in {item.order_id for item in factory.orders()}:
        factory.create_order(order_id=ORDER_ID, product='demo-part',
                             material='demo-stock', quantity=3)
    order = factory.order(ORDER_ID)
    if order.stage_index == 0:
        supply = factory.pending_handoff(ORDER_ID) or factory.next_handoff(ORDER_ID)
        if supply.handoff_id not in runtime.snapshot():
            native = factory_bridge.native.admit(supply)
            runtime.submit(native)
        elif runtime.get(supply.handoff_id).metadata.get('native_evidence_verifier') is None:
            raise ValueError('unverified pre-existing supply stage')
        if runtime.state(supply.handoff_id).status == 'READY':
            runtime.run(supply.handoff_id, default_simulated_actors()[supply.to_actor])
        factory_bridge.native.reverify(supply.handoff_id)
        factory.reconcile(ORDER_ID, handoff=supply, state=runtime.state(supply.handoff_id))
    order = factory.order(ORDER_ID)
    if order.stage_index == 1:
        machine_handoff = factory.pending_handoff(ORDER_ID) or factory.next_handoff(ORDER_ID)
        if machine_handoff.handoff_id not in runtime.snapshot():
            factory_bridge.admit(machine_handoff, version_id=FACTORY_VERSION)
        if runtime.state(machine_handoff.handoff_id).status == 'READY':
            factory_bridge.execute(machine_handoff.handoff_id, allow_local_execution=True)
        factory_bridge.reverify(machine_handoff.handoff_id)
        factory.reconcile(ORDER_ID, handoff=machine_handoff,
                          state=runtime.state(machine_handoff.handoff_id))
    # Native revalidation is required on every restart, not just first execution.
    factory_bridge.native.reverify(f'factory-{ORDER_ID}-01-supply')
    machine_id = f'factory-{ORDER_ID}-02-machine'
    factory_bridge.reverify(machine_id)
    # Bind each real result to its own return point exactly once.
    current_fcp = workspace.get_lane('finite-correspondence')
    if not any(f'handoff:{FCP_JOB}' in e.get('data', {}).get('evidence_refs', [])
               for e in workspace.history('finite-correspondence')):
        workspace.record_movement('finite-correspondence',
                                  changes='finite prefilter job recorded and reverified',
                                  preserved='finite research sources and CP history unchanged',
                                  next_movement='inspect bounded verdicts or branch a new edition',
                                  evidence_refs=(f'handoff:{FCP_JOB}',))
    current_factory = workspace.get_lane('factory-simulation')
    if not any(f'handoff:{machine_id}' in e.get('data', {}).get('evidence_refs', [])
               for e in workspace.history('factory-simulation')):
        workspace.record_movement('factory-simulation',
                                  changes='machine stage simulated and natively reverified',
                                  preserved='factory source owns order; physical machining remains unproved',
                                  next_movement='inspect simulated output; no physical stages admitted',
                                  evidence_refs=(f'handoff:{machine_id}',))
    if factory.order(ORDER_ID).stage_index != 2:
        raise ValueError('demo expected only supply + machine stages, no physical operation')
    # Snapshot read is side effect free; no speculative event on every resume.
    view = workstation_snapshot(root=desk.root, runtime=runtime,
                                workspace_journal=data / 'workspace.jsonl')
    ids = {x['worker_id'] for x in view['editions']}
    assert {FCP_ID, FACTORY_ID} <= ids
    assert len(view['jobs']) == 2
    assert all(job['status'] == 'COMPLETE' for job in view['jobs'])
    assert all(job['source_state'] == 'MATCHES_ADMISSION' for job in view['jobs'])
    return view


def main():
    parser = argparse.ArgumentParser(description='Explicit two-process local workstation witness')
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='Authorize both trusted local demo processes')
    args = parser.parse_args()
    snapshot = populate(args.data_dir, execute=args.execute)
    print('Worker kinds:', snapshot['counts']['workers'])
    print('Admitted workstation jobs:', snapshot['counts']['jobs'])
    for job in snapshot['jobs']:
        print(job['worker_id'], job['status'], job['realization'], job['source_state'])
    print('Read-only viewer: python -m systems.workspace.view_server --data-dir', args.data_dir)


if __name__ == '__main__':
    main()
