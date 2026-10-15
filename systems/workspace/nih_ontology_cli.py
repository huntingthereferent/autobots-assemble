"""Explicit source-copy, validation and admission for Phase 1 RDF mapping."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_ontology_bridge import NIHOntologyBridge,WORKER_ID,SOURCE_FILE,copy_ontology_source
from .nih_ontology_native import validate_request
from .workstation import ProcessWorkstation


def main(argv=None):
    ap=argparse.ArgumentParser(description='Phase 1 synthetic ontology worker controls')
    ap.add_argument('--data-dir',required=True)
    sub=ap.add_subparsers(dest='action',required=True)
    a=sub.add_parser('copy');a.add_argument('--version',required=True);a.add_argument('--confirm-copy',action='store_true')
    for cmd in ('prepare','admit'):
        a=sub.add_parser(cmd);a.add_argument('--version',required=True);a.add_argument('--inputs-file',required=True)
        if cmd=='admit':
            a.add_argument('--job-id',required=True);a.add_argument('--confirm-admit',required=True)
            a.add_argument('--from-actor',required=True)
    args=ap.parse_args(argv)
    directory=Path(args.data_dir).resolve()
    if args.action=='copy':
        print(json.dumps(copy_ontology_source(directory,version_id=args.version,allow_copy=args.confirm_copy),indent=2));return 0
    path=Path(args.inputs_file)
    if not path.is_file() or path.stat().st_size>4096:raise ValueError('ontology request must be JSON <=4 KiB')
    req=validate_request(json.loads(path.read_text(encoding='utf-8')))
    desk=ProcessWorkstation(directory/'workstation')
    folder,record=desk._read(WORKER_ID,args.version)
    info=desk.inspect(worker_id=WORKER_ID,version_id=args.version)
    if SOURCE_FILE not in desk._inventory_edition(folder):raise ValueError('missing ontology source file')
    if args.action=='prepare':
        print(json.dumps({'admitted':False,'executed':False,'source_fingerprint':info['current_fingerprint'],
                          'mapping_id':req['mapping_id'],'scope_job_id':req['scope_job_id']},indent=2));return 0
    if args.confirm_admit!=args.job_id:raise PermissionError('explicit exact-ID admission confirmation required')
    runtime=HandoffRuntime(event_store=RuntimeJournal(directory/'runtime.jsonl'))
    bridge=NIHOntologyBridge(runtime=runtime,workstation=desk)
    handoff=bridge.admit(version_id=args.version,inputs=req,from_actor=args.from_actor,job_id=args.job_id)
    print(json.dumps({'job_id':handoff.handoff_id,'worker_id':WORKER_ID,'status':runtime.state(handoff.handoff_id).status,
                      'source_fingerprint':handoff.metadata['edition_fingerprint'],'executed':False},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())