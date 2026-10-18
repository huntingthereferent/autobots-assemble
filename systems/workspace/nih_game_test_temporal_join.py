"""Source-owned NIH-P2-TEST from actual playable game -> real temporal Python.

Eleventh native job, same ProcessWorkstation/RuntimeJournal/Complete Stack CP
index. WITNESS independently executes ORIGINAL temporal_query.py on the actual
browser event log. No official NIH submission or patient-data experiment.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import prepare,run_job,reverify_job
from .game_worker_ready_temporal_join import join as original_ten
from .nih_game_test_bridge import (
    WORKER_ID,VERSION,JOB_ID,copy_test_source,NIHGameTestBridge)
from .coordinator_window import (
    CoordinatorIndex,from_existing_workstation,
    run_exact_linked_job,freshly_reverify_linked_jobs)
from .cp_motion import workstation_cp_view,one_cp_handoff

WINDOW="complete-stack"
SLOT="cp-nih-p2-test"
PARENTS=(
    "nih-scope-001","ontology-job","nih-reasoning-001","nih-packet-001",
    "nih-prototype-001","build-game-room-v1","live-game-temporal-001",
    "game-w13-cp-joined-001","game-native-verifier-joined-001",
    "game-worker-ready-joined-001",
)
REQUEST={"kind":"native-game-backed-temporal-test/v1","synthetic":True}

def _read_actual_events(folder):
    path=folder/"game-temporal-query-events.jsonl"
    if not path.is_file() or path.is_symlink() or path.stat().st_size>120000:
        raise ValueError("actual independent Chromium temporal query log is required")
    events=[json.loads(line) for line in path.read_text(encoding="utf8").splitlines()]
    if not 4<=len(events)<=60:
        raise ValueError("actual browser query history has wrong bounds")
    return events

def join(*,data_dir:Path,output_dir:Path):
    data,out=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    existing=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot()
    if JOB_ID not in existing:
        ready=original_ten(data_dir=data,output_dir=out,with_browser=True)
    else:
        for j in PARENTS:
            if reverify_job(data_dir=data,job_id=j)["status"]!="COMPLETE":
                raise ValueError("original ten source-owned native jobs changed")
        ready=json.loads((out/"game-worker-ready-complete-stack.json").read_text())
    if ready["nih_p2_test_state"]!="ADMISSIBLE":
        raise ValueError("original game-ready CP has not opened temporal test")
    events=_read_actual_events(out)
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_test_source(data,version_id=VERSION,allow_copy=True)
    req_file=out/"nih-game-test-request.json"
    req=json.dumps(REQUEST,sort_keys=True)+"\n"
    if req_file.exists() and req_file.read_text()!=req:
        raise ValueError("original source-owned temporal game test request changed")
    req_file.write_text(req,encoding="utf8")
    prepare(data_dir=data,worker_id=WORKER_ID,version_id=VERSION,inputs_file=req_file)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if JOB_ID not in runtime.snapshot():
        NIHGameTestBridge(runtime=runtime,workstation=desk).admit(
            version_id=VERSION,inputs={"request":REQUEST,"events":events},
            from_actor="complete-stack-temporal-game-experiment",job_id=JOB_ID)
    else:
        h=runtime.get(JOB_ID)
        if (h.metadata.get("worker_id")!=WORKER_ID or
                h.inputs["events"]!=events):
            raise ValueError("source-owned query history changed after admission")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    _,lanes=index.definition(WINDOW)
    original=next((x for x in lanes["nih"] if x["slot"]==SLOT),None)
    if original is None:
        raise ValueError("original NIH P2 CP slot missing")
    if original["source_kind"]=="planned":
        index.bind_planned(WINDOW,"nih",slot=SLOT,
                           job_id=JOB_ID,worker_id=WORKER_ID,version_id=VERSION)
    elif (original.get("source_kind"),original.get("job_id"),
          original.get("worker_id"),original.get("version_id"))!=(
          "runtime-job",JOB_ID,WORKER_ID,VERSION):
        raise ValueError("original NIH P2 test CP belongs to another source job")
    state=run_exact_linked_job(
        index,WINDOW,"nih",SLOT,JOB_ID,from_existing_workstation(data),
        lambda jid,confirm:run_job(data_dir=data,job_id=jid,confirm_execute=confirm))
    if state["status"]!="COMPLETE" or reverify_job(data_dir=data,job_id=JOB_ID)["status"]!="COMPLETE":
        raise ValueError("source-owned Phase2 temporal browser test failed independent host replay")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    checked=freshly_reverify_linked_jobs(
        index,WINDOW,workstation_cp_view(data),
        lambda jid:reverify_job(data_dir=data,job_id=jid))
    graph=one_cp_handoff(index,WINDOW,checked,reverified=True)["cp_automation"]
    required={"NIH-P1-PACKET","NIH-P2-PROTOTYPE","GAME-WORKER-READY","NIH-P2-TEST"}
    if not required.issubset(set(graph["witnessed"])):
        raise ValueError("real synthetic Phase2 test wasn't witnessed in original CP graph")
    benchmark=next(x for x in graph["checkpoints"] if x["checkpoint"]=="NIH-P2-BENCHMARK")
    if benchmark["state"]!="ADMISSIBLE":
        raise ValueError("benchmark should be next independent bounded movement")
    if "NIH-P2-BENCHMARK" in graph["witnessed"] or len(runtime.snapshot())!=11:
        raise ValueError("source-owned Phase2 test invented a benchmark or jobs")
    report=runtime.state(JOB_ID).output["report"]
    result={
        "schema":"nih-phase2-original-live-game-temporal-test/v1",
        "native_jobs":11,"niH_P2_test_job":JOB_ID,
        "game_worker_ready_witnessed":True,
        "actual_game_query_count":report["query_count"],
        "original_browser_queries_independently_replayed":True,
        "static_future_leakage_observed":True,
        "NIH_P2_TEST":"WITNESSED",
        "next_admissible_checkpoint":"NIH-P2-BENCHMARK",
        "benchmark_witnessed":False,
        "official_NIH_submission":False,"synthetic_only":True,
    }
    (out/"nih-phase2-game-test-complete-stack.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    (out/"nih-phase2-game-test-native-receipt.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    (out/"game-temporal-cp-frontier.json").write_text(
        json.dumps(graph,sort_keys=True,indent=2)+"\n")
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    a=parser.parse_args(argv)
    print(json.dumps(join(data_dir=a.data_dir,output_dir=a.output_dir),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
