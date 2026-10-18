"""Run real NIH-P2-BENCHMARK as job twelve in the original temporal/game stack.

The predecessor is the actual browser-backed native NIH-P2-TEST, not a replayed
summary. New bitemporal boundary cases are independently verified by invoking
the original emitted temporal_query.py and a separate source-observation oracle.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import prepare,run_job,reverify_job
from .nih_game_test_temporal_join import join as original_eleven,PARENTS as ORIGINAL_TEN
from .nih_benchmark_bridge import (WORKER_ID,VERSION,JOB_ID,REQUEST,
                                   copy_benchmark_source,NIHBenchmarkBridge)
from .coordinator_window import (CoordinatorIndex,from_existing_workstation,
                                 run_exact_linked_job,freshly_reverify_linked_jobs)
from .cp_motion import workstation_cp_view,one_cp_handoff

WINDOW="complete-stack"
SLOT="cp-nih-p2-benchmark"
PREDECESSORS=(*ORIGINAL_TEN,"nih-p2-game-test-001")

def join(*,data_dir:Path,output_dir:Path):
    data,out=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    snapshot=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot()
    if JOB_ID not in snapshot:
        previous=original_eleven(data_dir=data,output_dir=out)
    else:
        for p in PREDECESSORS:
            if reverify_job(data_dir=data,job_id=p)["status"]!="COMPLETE":
                raise ValueError("original eleven exact source jobs changed")
        previous=json.loads((out/"nih-phase2-game-test-complete-stack.json").read_text())
    if (previous["NIH_P2_TEST"]!="WITNESSED" or
        previous["next_admissible_checkpoint"]!="NIH-P2-BENCHMARK"):
        raise ValueError("benchmark cannot precede source-owned Phase2 real-browser test")
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_benchmark_source(data,version_id=VERSION,allow_copy=True)
    request_file=out/"nih-benchmark-request.json"
    req=json.dumps(REQUEST,sort_keys=True)+"\n"
    if request_file.exists() and request_file.read_text()!=req:
        raise ValueError("source-owned benchmark request changed")
    request_file.write_text(req,encoding="utf8")
    prepare(data_dir=data,worker_id=WORKER_ID,version_id=VERSION,inputs_file=request_file)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if JOB_ID not in runtime.snapshot():
        NIHBenchmarkBridge(runtime=runtime,workstation=desk).admit(
            version_id=VERSION,inputs=REQUEST,
            from_actor="original-complete-stack-temporal-benchmark",job_id=JOB_ID)
    else:
        h=runtime.get(JOB_ID)
        if (h.metadata.get("worker_id")!=WORKER_ID or
            h.dependencies!=("nih-p2-game-test-001","nih-prototype-001")):
            raise ValueError("original benchmark worker ancestry differs")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    _,lanes=index.definition(WINDOW)
    entry=next((x for x in lanes["nih"] if x["slot"]==SLOT),None)
    if entry is None:
        raise ValueError("original temporal benchmark CP slot missing")
    if entry["source_kind"]=="planned":
        index.bind_planned(WINDOW,"nih",slot=SLOT,
                           job_id=JOB_ID,worker_id=WORKER_ID,version_id=VERSION)
    elif (entry.get("source_kind"),entry.get("job_id"),
          entry.get("worker_id"),entry.get("version_id"))!=(
          "runtime-job",JOB_ID,WORKER_ID,VERSION):
        raise ValueError("original temporal benchmark slot bound to another source")
    state=run_exact_linked_job(
        index,WINDOW,"nih",SLOT,JOB_ID,from_existing_workstation(data),
        lambda jid,confirm:run_job(data_dir=data,job_id=jid,confirm_execute=confirm))
    if state["status"]!="COMPLETE" or reverify_job(data_dir=data,job_id=JOB_ID)["status"]!="COMPLETE":
        raise ValueError("native synthetic temporal-static benchmark not independently checked")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    checked=freshly_reverify_linked_jobs(
        index,WINDOW,workstation_cp_view(data),
        lambda jid:reverify_job(data_dir=data,job_id=jid))
    graph=one_cp_handoff(index,WINDOW,checked,reverified=True)["cp_automation"]
    required={"NIH-P1-PACKET","NIH-P2-PROTOTYPE","GAME-WORKER-READY",
              "NIH-P2-TEST","NIH-P2-BENCHMARK"}
    if not required.issubset(set(graph["witnessed"])):
        raise ValueError("native twelfth benchmark was not witnessed in original CP graph")
    if (len(runtime.snapshot())!=12 or
        "NIH-P2-SUBMISSION" in graph["witnessed"] or
        "NIH-P1-AWARD" in graph["witnessed"]):
        raise ValueError("benchmark invented external award, submission, or jobs")
    report=runtime.state(JOB_ID).output["report"]
    result={
        "schema":"nih-phase2-original-synthetic-temporal-static-benchmark/v1",
        "native_jobs":12,"benchmark_job_id":JOB_ID,"NIH_P2_BENCHMARK":"WITNESSED",
        "NIH_P2_TEST":"WITNESSED",
        "source_browser_history_sha256":report["query_history_sha256"],
        "source_temporal_executable_sha256":report["prototype_sha256"],
        "new_boundary_queries_independently_executed":report["query_count"],
        "static_future_leakage_cases":report["static_future_leakage_cases"],
        "static_future_leakage_ids_total":report["static_future_leakage_ids_total"],
        "temporal_leakage_ids_total":report["temporal_leakage_ids_total"],
        "original_executable_and_source_oracle_checked":True,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "official_NIH_submission":False,"NIH_award":False,
    }
    (out/"nih-phase2-temporal-static-benchmark.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    (out/"nih-phase2-temporal-static-benchmark-cases.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    (out/"game-temporal-cp-frontier.json").write_text(
        json.dumps(graph,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    a=p.parse_args(argv)
    print(json.dumps(join(data_dir=a.data_dir,output_dir=a.output_dir),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
