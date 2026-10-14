"""Opt-in synthetic CP30 owner/pin route audit with exact tasks, not real owners."""
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.integrated_source import copy_integrated_source, WORKER_ID
from systems.workspace.integrated_route_bridge import IntegratedRouteBridge

REPO=Path(__file__).resolve().parents[2]
VERSION="cp30-route-fixture-001"
JOB_ID="cp30-synthetic-route-001"
INPUTS={"route":"left","scenario":"intact","tasks":[
    {"name":"required-a","state":[1,0,0],"action":"B"},
    {"name":"required-b","state":[1,1,2],"action":"A"},
    {"name":"unproved","state":[0,1,2],"action":"B"}]}


def main():
    ap=ArgumentParser(description="Explicit trusted local CP30 synthetic route fixture")
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    if not args.execute:
        ap.error("--execute is required to admit and run a synthetic CP30 route job")
    data=args.data_dir.resolve()
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:
        copy_integrated_source(repo_root=REPO,data_dir=data,stage=30,
                               version_id=VERSION,allow_copy=True)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    bridge=IntegratedRouteBridge(runtime=runtime,workstation=desk)
    if JOB_ID not in runtime.snapshot():
        bridge.admit(version_id=VERSION,inputs=INPUTS,from_actor="local-fixture-demo",job_id=JOB_ID)
    status=runtime.state(JOB_ID).status
    if status=="READY":bridge.execute(JOB_ID,allow_local_execution=True)
    bridge.reverify(JOB_ID)
    report=runtime.state(JOB_ID).output["report"]
    print("Job status:",runtime.state(JOB_ID).status)
    print("Receiver:",report["receive_status"])
    print("Fresh route replay calls:",report["replay_calls"])
    print("Exact task outcomes:",report["task_statuses"])
    print("Usable within synthetic fixture:",report["usable"])
    print("Real-world owner authenticated: False")


if __name__=="__main__":main()
