"""CP movement across one EXISTING Process Workstation, not an executor.

Selecting a research referent opens a declared dependency graph immediately.
Subsequent status calls re-evaluate its frontier from exact native results.
Nothing here admits, starts or fabricates jobs or independently authenticates
external competition decisions. Each domain retains its own verifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
import argparse
import json

from .coordinator_window import (CoordinatorIndex, one_window_status,
                                  from_existing_workstation,
                                  freshly_reverify_linked_jobs)


@dataclass(frozen=True)
class Checkpoint:
    id: str
    lane: str
    label: str
    requires: tuple[str, ...]
    worker_role: str
    external: bool = False


# Research dependency policy deliberately distinguished from NIH rules.
# GAME-WORKER-READY is OUR desired prerequisite for exercising Phase-2 tests,
# not an official NIH prerequisite for Phase-2 research or eligibility.
GRAPH = (
    Checkpoint('NIH-P1-SCOPE', 'nih', 'Scope biomedical question and evidence', (), 'research-scoper'),
    Checkpoint('NIH-P1-ONTOLOGY', 'nih', 'OWL-Time PROV-O and Biolink mapping', ('NIH-P1-SCOPE',), 'ontology-builder'),
    Checkpoint('NIH-P1-REASONING', 'nih', 'Temporal axioms and negative controls', ('NIH-P1-ONTOLOGY',), 'temporal-witness'),
    Checkpoint('NIH-P1-PACKET', 'nih', 'Phase 1 design packet and independent review', ('NIH-P1-REASONING',), 'artifact-builder'),
    Checkpoint('NIH-P1-SUBMISSION', 'nih', 'Official phase 1 submission receipt', ('NIH-P1-PACKET',), 'external-nih-portal', True),
    Checkpoint('NIH-P1-AWARD', 'nih', 'Official eligibility decision from NIH', ('NIH-P1-SUBMISSION',), 'external-nih-decision', True),
    Checkpoint('GAME-W13-WORLDS', 'game', 'Construct multi-world game from W12 rules', (), 'game-build'),
    Checkpoint('GAME-NATIVE-VERIFIER', 'game', 'Witness full multi-world replay and negative controls', ('GAME-W13-WORLDS',), 'game-witness'),
    Checkpoint('GAME-WORKER-READY', 'game', 'Verify source-pinned game workstation adapter', ('GAME-NATIVE-VERIFIER',), 'game-adapter'),
    Checkpoint('NIH-P2-PROTOTYPE', 'nih', 'Develop prototype independent of submission status', ('NIH-P1-REASONING',), 'temporal-build'),
    Checkpoint('NIH-P2-TEST', 'nih', 'Exercise prototype via finished game-backed test infrastructure',
               ('NIH-P1-PACKET', 'GAME-WORKER-READY', 'NIH-P2-PROTOTYPE'), 'temporal-test'),
    Checkpoint('NIH-P2-BENCHMARK', 'nih', 'Replay temporal and static-graph benchmarks', ('NIH-P2-TEST',), 'temporal-benchmark'),
    Checkpoint('NIH-P2-SUBMISSION', 'nih', 'Official phase 2 submission',
               ('NIH-P1-AWARD', 'NIH-P2-BENCHMARK'), 'external-nih-portal', True),
)


def validate_graph(graph=GRAPH):
    lookup = {node.id: node for node in graph}
    if len(lookup) != len(graph):
        raise ValueError('duplicate checkpoint')
    if not all(set(node.requires) <= set(lookup) and node.id not in node.requires for node in graph):
        raise ValueError('unknown/self dependency')
    visited, active = set(), set()
    def visit(name):
        if name in active: raise ValueError('checkpoint cycle')
        if name in visited: return
        active.add(name)
        for item in lookup[name].requires: visit(item)
        active.remove(name); visited.add(name)
    for name in lookup: visit(name)
    return lookup


validate_graph()


def admit_research(index: CoordinatorIndex, window: str = 'complete-stack', *, source_zip: str | Path | None = None, game_w12_zip: str | Path | None = None, correspondence_index: str | Path | None = None) -> int:
    """Idempotently add *planned* CPs to the existing coordinator index.

    This is the requested onset of CP automation: source selection registers
    dependency structure, not native jobs or autonomous process activation.
    """
    try:
        _, links = index.definition(window)
    except KeyError:
        index.create_window(window, lanes=('game', 'correspondence', 'nih'))
        _, links = index.definition(window)
    existing = {(lane, item['slot']) for lane, entries in links.items() for item in entries}
    count = 0
    for lane, slot, source_path, description in (
        ('nih', 'nih-intake', source_zip, 'Original NIH phase contract and W01 source; integrity only'),
        ('game', 'game-w12-baseline', game_w12_zip, 'Original independently reported W12 candidate; historical only'),
        ('correspondence', 'cp30-source-index', correspondence_index, 'Recovered CP30 source index; not live worker'),
    ):
        if source_path is None: continue
        source = Path(source_path)
        if not source.is_file() or source.is_symlink():
            raise ValueError(f'{lane} source archive unavailable or unsafe')
        if (lane, slot) not in existing:
            index.link_artifact(window, lane, slot=slot, locator=source.name,
                sha256_hex=sha256(source.read_bytes()).hexdigest(),
                historical_note=description)
            count += 1
    for cp in GRAPH:
        slot = 'cp-' + cp.id.lower()
        if (cp.lane, slot) not in existing:
            index.link_planned(window, cp.lane, slot=slot,
                 next_movement=f'{cp.id}: {cp.label}; requires {", ".join(cp.requires) or "research intake"}')
            count += 1
    return count


def _freshly_witnessed(workstation_view: dict, graph=GRAPH):
    """Do not accept mere COMPLETE, source hashes, or archived CP30 evidence.

    A native adapter must explicitly return the exact declared CP contract and
    PASS verdict, and independently reverify that exact local computation.
    External official decisions are never derived from local workstation jobs.
    """
    mapping = validate_graph(graph)
    verified = set()
    refused = []
    for job in workstation_view.get('jobs', ()):
        result = job.get('result') or {}
        if not isinstance(result, dict): continue
        cp_id = result.get('checkpoint_contract')
        if cp_id not in mapping: continue
        node = mapping[cp_id]
        valid = (
            not node.external
            and job.get('status') == 'COMPLETE'
            and job.get('source_state') == 'MATCHES_ADMISSION'
            and job.get('verification') == 'natively-reverified'
            and not job.get('missing_witnesses')
            and not job.get('blocked_by')
            and result.get('checkpoint_verdict') == 'PASS'
            and result.get('checkpoint_worker_role') == node.worker_role
            and job.get('checkpoint_contract') == cp_id
            and job.get('native_verifier') == f'cp-checker:{cp_id}'
            and result.get('native_verifier') == f'cp-checker:{cp_id}'
            and job.get('worker_id') is not None
            and job.get('version_id') is not None
        )
        if valid: verified.add(cp_id)
        else: refused.append({'checkpoint': cp_id, 'job_id': job.get('job_id'),
                              'reason': 'native contract, verifier, or freshness unproved'})
    return verified, refused


def checkpoint_frontier(workstation_view: dict, *, graph=GRAPH, official_proofs=()):
    """Evaluate frontier without starting workers. official_proofs must be supplied
    by a separate official-result authenticator; untrusted user input doesn't
    become an NIH award. Normal CLI intentionally passes none.
    """
    mapping = validate_graph(graph)
    native_proven, refused = _freshly_witnessed(workstation_view, graph)
    proven = set()
    # A local PASS cannot skip its checkpoint ancestry; do not accept a
    # forged 'future' result just because it names a higher checkpoint.
    pending = set(native_proven)
    changed = True
    while changed:
        changed = False
        for cp_id in list(pending):
            if set(mapping[cp_id].requires) <= proven:
                proven.add(cp_id)
                pending.remove(cp_id)
                changed = True
    refused.extend({'checkpoint':cp, 'reason':'missing certified checkpoint ancestry'}
                   for cp in sorted(pending))
    # External official proofs are NOT accepted here; a future external
    # verification adapter will need a separate explicit admission contract.
    if official_proofs:
        raise ValueError('external official proofs require an independent authority adapter')
    rows = []
    for cp in graph:
        missing = [name for name in cp.requires if name not in proven]
        if cp.id in proven:
            state = 'WITNESSED'
        elif missing:
            state = 'BLOCKED'
        elif cp.external:
            state = 'EXTERNAL_GATE'
        else:
            state = 'ADMISSIBLE'  # eligible to formulate/admit a worker, NOT auto-executed
        rows.append({'checkpoint': cp.id, 'lane': cp.lane, 'state': state,
                     'worker_role': cp.worker_role, 'label': cp.label,
                     'requires': list(cp.requires), 'blocked_by': missing,
                     'native_witness_required': not cp.external})
    return {'schema_version': 2, 'mode': 'checkpoint-automation-not-autonomous-scheduling',
            'witnessed': sorted(proven), 'frontier': [r['checkpoint'] for r in rows if r['state']=='ADMISSIBLE'],
            'checkpoints': rows, 'refused_claims': refused, 'started_workers': 0,
            'note': 'ADMISSIBLE means a CP can receive a source-owned native task; it is not admitted, executed, or passed.'}


def attach_native_cp_contracts(view: dict, handoffs) -> dict:
    """Read source-pinned *submitted* handoff specs; do not trust result fields
    to declare their own authority. Does not start or modify native jobs.
    """
    ids = {h.handoff_id: h for h in handoffs}
    copied = {**view, 'jobs': [dict(job) for job in view.get('jobs', ())]}
    for job in copied['jobs']:
        h = ids.get(job.get('job_id'))
        if h is None: continue
        if (h.metadata.get('worker_id'), h.metadata.get('worker_version')) != (job.get('worker_id'), job.get('version_id')):
            continue
        job['checkpoint_contract'] = h.metadata.get('checkpoint_contract')
        job['native_verifier'] = h.metadata.get('native_evidence_verifier')
    return copied


def workstation_cp_view(directory: Path) -> dict:
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    runtime = HandoffRuntime(event_store=RuntimeJournal(directory/'runtime.jsonl'))
    return attach_native_cp_contracts(from_existing_workstation(directory), runtime._handoffs.values())


def one_cp_handoff(index: CoordinatorIndex, window: str, native: dict, *, reverified=False, artifact_dir=None):
    workers = one_window_status(index, window, native, artifact_dir=artifact_dir)
    _, links = index.definition(window)
    bound_ids = {row['job_id'] for entries in links.values() for row in entries
                 if row['source_kind'] == 'runtime-job'}
    # A CP is part of THIS coordinator only after an explicit exact-ID link.
    scoped_native = {**native, 'jobs': [job for job in native.get('jobs', ())
                                      if job.get('job_id') in bound_ids]}
    plan = checkpoint_frontier(scoped_native)
    return {'coordinator_window': window, 'workers': workers['workers'],
            'workstation_unresolved_lanes': workers['unresolved_lanes'],
            'cp_automation': plan, 'native_reverification_requested': reverified,
            'execution_triggered': False}


def handoff_markdown(packet: dict) -> str:
    automation = packet['cp_automation']
    rows = [f"# CP COORDINATOR — {packet['coordinator_window']}", '',
            '**Motion:** research entered stack → dependencies exposed → witness-driven frontier.',
            '', '## Next admissible checkpoints', '']
    if automation['frontier']:
        for cp in automation['frontier']:
            node=next(r for r in automation['checkpoints'] if r['checkpoint']==cp)
            rows.append(f"- **{cp}** — {node['label']} ({node['worker_role']}); not yet admitted")
    else: rows.append('No next CP is currently admissible.')
    rows.extend(['', '## All CPs', '', '| CP | State | Missing dependencies |', '|---|---|---|'])
    for row in automation['checkpoints']:
        rows.append(f"| {row['checkpoint']} | {row['state']} | {', '.join(row['blocked_by']) or '—'} |")
    rows.extend(['','## Existing workstation workers','','| Lane | Slot | Native status | Verification |', '|---|---|---|---|'])
    for row in packet['workers']:
        rows.append(f"| {row['lane']} | {row['slot']} | {row['status']} | {row['verification']} |")
    rows.extend(['', '## Preserved boundaries', '',
        '- Phase 1 scope/design can advance using suitable workers; it does not require the game engine.',
        '- Phase 2 **testing through our chosen game-engine path** is blocked until the game adapter has native witnesses.',
        '- Phase 2 prototype research can begin after NIH-P1-REASONING, without official award.',
        '- NIH Phase 2 submission separately requires the official NIH Phase 1 winner gate.',
        '- An archived checkpoint or generic worker COMPLETE never proves a new biomedical checkpoint.',
        '- This CP planner does not automatically admit/execute jobs, run between chat turns, or command other conversation tabs.', ''])
    return '\n'.join(rows)


def main(argv=None):
    ap=argparse.ArgumentParser(description='CP motion on top of the existing Process Workstation')
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--window', default='complete-stack')
    sub=ap.add_subparsers(dest='operation',required=True)
    adm=sub.add_parser('admit-research')
    adm.add_argument('--nih-contract-zip', help='pin existing NIH source archive by SHA-256')
    adm.add_argument('--game-w12-zip', help='pin W12 game archive as historical evidence')
    adm.add_argument('--correspondence-index', help='pin CP30 source index as historical evidence')
    status=sub.add_parser('handoff')
    status.add_argument('--markdown',action='store_true')
    status.add_argument('--artifact-dir')
    status.add_argument('--reverify',action='store_true')
    args=ap.parse_args(argv)
    root=Path(args.data_dir)
    index=CoordinatorIndex(root/'coordinator-windows.jsonl')
    if args.operation=='admit-research':
        n=admit_research(index,args.window,source_zip=args.nih_contract_zip,
            game_w12_zip=args.game_w12_zip,correspondence_index=args.correspondence_index)
        print(json.dumps({'planned_cp_added':n,'window':args.window,'workers_executed':0}))
        return 0
    native=workstation_cp_view(root)
    if args.reverify:
        from systems.workspace.controls import reverify_job
        native=freshly_reverify_linked_jobs(index,args.window,native,
                    lambda job_id: reverify_job(data_dir=root,job_id=job_id))
    packet=one_cp_handoff(index,args.window,native,reverified=args.reverify,artifact_dir=args.artifact_dir)
    # Helper openings live in the SAME native journal; the coordinator only views them.
    from .branch_help import help_summary
    packet['help_openings']=help_summary(root)
    rendered=handoff_markdown(packet)
    if packet['help_openings']:
        rendered+='\n## Unfinished-branch help openings\n\n'
        for opening in packet['help_openings']:
            rendered+=(f"- **{opening['parent_lane']}/{opening['parent_slot']}**: "
                      f"{opening['capability']} — {opening['state']} "
                      f"({opening['opening_id']})\n")
    print(rendered if args.markdown else json.dumps(packet,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())