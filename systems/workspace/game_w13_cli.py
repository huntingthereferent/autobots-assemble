"""Exact copy, prepare and admit controls for W13 in the existing workstation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .game_w13_native import validate_request,expected_report
from .game_w13_bridge import GameW13Bridge,WORKER_ID,copy_game_source
from .workstation import ProcessWorkstation


def main(argv=None):
    p=argparse.ArgumentParser(description='GAME W13 native worker, explicit controls only')
    p.add_argument('--data-dir',type=Path,required=True)
    subs=p.add_subparsers(dest='mode',required=True)
    s=subs.add_parser('copy');s.add_argument('--version',required=True);s.add_argument('--confirm-copy',action='store_true')
    s=subs.add_parser('prepare');s.add_argument('--version',required=True);s.add_argument('--inputs-file',type=Path,required=True)
    s=subs.add_parser('admit');s.add_argument('--version',required=True);s.add_argument('--inputs-file',type=Path,required=True)
    s.add_argument('--job-id',required=True);s.add_argument('--confirm-admit',required=True);s.add_argument('--from-actor',required=True)
    args=p.parse_args(argv)
    root=args.data_dir.resolve();repo=Path(__file__).resolve().parents[2]
    if root==repo or repo.is_relative_to(root):
        raise ValueError('private runtime cannot contain repository')
    if args.mode=='copy':
        report=copy_game_source(root,version_id=args.version,allow_copy=args.confirm_copy)
    else:
        if not args.inputs_file.is_file() or args.inputs_file.stat().st_size>16384:
            raise ValueError('W13 input file missing or exceeds 16 KiB')
        data=validate_request(json.loads(args.inputs_file.read_text(encoding='utf8')))
        expected_report(data)
        desk=ProcessWorkstation(root/'workstation')
        info=desk.inspect(worker_id=WORKER_ID,version_id=args.version)
        if args.mode=='prepare':
            report={'prepared':True,'admitted':False,'executed':False,
                    'worker_id':WORKER_ID,'edition_fingerprint':info['current_fingerprint']}
        else:
            if args.confirm_admit!=args.job_id:
                raise PermissionError('exact W13 job confirmation required')
            runtime=HandoffRuntime(event_store=RuntimeJournal(root/'runtime.jsonl'))
            h=GameW13Bridge(runtime=runtime,workstation=desk).admit(
                version_id=args.version,inputs=data,job_id=args.job_id,from_actor=args.from_actor)
            report={'job_id':h.handoff_id,'status':runtime.state(h.handoff_id).status,
                    'worker_id':WORKER_ID,'executed':False}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':raise SystemExit(main())