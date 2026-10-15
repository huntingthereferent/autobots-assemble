"""Explicit copy/prepare/admit for source-pinned synthetic RDF temporal reasoner."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_reasoning_bridge import NIHReasoningBridge,WORKER_ID,SOURCE_FILE,copy_reasoning_source
from .nih_reasoning_native import validate_request
from .workstation import ProcessWorkstation


def main(argv=None):
    ap=argparse.ArgumentParser(description='NIH Phase 1 synthetic temporal reasoning worker')
    ap.add_argument('--data-dir',required=True)
    sub=ap.add_subparsers(dest='action',required=True)
    s=sub.add_parser('copy');s.add_argument('--version',required=True);s.add_argument('--confirm-copy',action='store_true')
    for mode in ('prepare','admit'):
        s=sub.add_parser(mode);s.add_argument('--version',required=True);s.add_argument('--inputs-file',required=True)
        if mode=='admit':
            s.add_argument('--job-id',required=True);s.add_argument('--confirm-admit',required=True)
            s.add_argument('--from-actor',required=True)
    opts=ap.parse_args(argv)
    base=Path(opts.data_dir).resolve()
    if opts.action=='copy':
        print(json.dumps(copy_reasoning_source(base,version_id=opts.version,allow_copy=opts.confirm_copy),indent=2));return 0
    path=Path(opts.inputs_file)
    if not path.is_file() or path.stat().st_size>4096:
        raise ValueError('reasoning request file must be JSON <=4 KiB')
    req=validate_request(json.loads(path.read_text(encoding='utf-8')))
    desk=ProcessWorkstation(base/'workstation')
    folder,_=desk._read(WORKER_ID,opts.version)
    info=desk.inspect(worker_id=WORKER_ID,version_id=opts.version)
    if SOURCE_FILE not in desk._inventory_edition(folder):raise ValueError('worker source missing')
    if opts.action=='prepare':
        print(json.dumps({'admitted':False,'executed':False,'source_fingerprint':info['current_fingerprint'],
             'ontology_job_id':req['ontology_job_id'],'query_count':len(req['cases'])},indent=2));return 0
    if opts.job_id!=opts.confirm_admit:raise PermissionError('exact job-ID admission required')
    runtime=HandoffRuntime(event_store=RuntimeJournal(base/'runtime.jsonl'))
    bridge=NIHReasoningBridge(runtime=runtime,workstation=desk)
    handoff=bridge.admit(version_id=opts.version,inputs=req,from_actor=opts.from_actor,job_id=opts.job_id)
    print(json.dumps({'job_id':handoff.handoff_id,'worker_id':WORKER_ID,'status':runtime.state(handoff.handoff_id).status,
                      'source_fingerprint':handoff.metadata['edition_fingerprint'],'executed':False},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())