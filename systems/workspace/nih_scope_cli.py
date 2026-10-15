"""Explicit copy/prepare/admit commands for the existing workstation scope worker."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_scope_bridge import NIHScopeBridge, WORKER_ID, copy_scope_source
from .nih_scope_native import validate_scope
from .workstation import ProcessWorkstation


def input_file(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > 16384:
        raise ValueError('synthetic scope inputs require bounded JSON <=16 KiB')
    return validate_scope(json.loads(path.read_text(encoding='utf-8')))


def main(argv=None):
    p=argparse.ArgumentParser(description='Explicit NIH scope worker admission; no automatic execution')
    p.add_argument('--data-dir',type=Path,required=True)
    sub=p.add_subparsers(dest='action',required=True)
    c=sub.add_parser('copy');c.add_argument('--version',required=True);c.add_argument('--confirm-copy',action='store_true')
    c=sub.add_parser('prepare');c.add_argument('--version',required=True);c.add_argument('--inputs-file',type=Path,required=True)
    c=sub.add_parser('admit');c.add_argument('--version',required=True);c.add_argument('--inputs-file',type=Path,required=True)
    c.add_argument('--job-id',required=True);c.add_argument('--confirm-admit',required=True);c.add_argument('--from-actor',required=True)
    a=p.parse_args(argv)
    directory=a.data_dir.resolve()
    repo=Path(__file__).resolve().parents[2]
    if directory==repo or repo.is_relative_to(directory):
        raise ValueError('private data dir must not contain repo')
    if a.action=='copy':
        report=copy_scope_source(directory,version_id=a.version,allow_copy=a.confirm_copy)
    else:
        payload=input_file(a.inputs_file)
        desk=ProcessWorkstation(directory/'workstation')
        edition=desk.inspect(worker_id=WORKER_ID,version_id=a.version)
        if a.action=='prepare':
            report={'prepared':True,'admitted':False,'executed':False,
                    'worker_id':WORKER_ID,'edition_fingerprint':edition['current_fingerprint'],
                    'inputs':payload}
        else:
            if a.confirm_admit != a.job_id:
                raise PermissionError('confirm-admit must match exact job ID')
            runtime=HandoffRuntime(event_store=RuntimeJournal(directory/'runtime.jsonl'))
            bridge=NIHScopeBridge(runtime=runtime,workstation=desk)
            handoff=bridge.admit(version_id=a.version,inputs=payload,from_actor=a.from_actor,job_id=a.job_id)
            report={'job_id':handoff.handoff_id,'status':runtime.state(handoff.handoff_id).status,
                    'executed':False,'worker_id':WORKER_ID,'edition_fingerprint':edition['current_fingerprint']}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())