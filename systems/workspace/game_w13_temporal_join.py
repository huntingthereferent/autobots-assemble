"""Move the REAL original W13 CP worker into the live temporal-game workstation.

A successful browser play does not impersonate W13 admission or GAME-WORKER-READY.
This reuses the exact existing W13 source-owned worker, original W12 native oracle,
coordinator CP slots, and original journal—no new W13 game rules or worker runtime.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import run_job,reverify_job,prepare
from .game_temporal_stack import continue_stack,JOB_ID as LIVE_JOB
from .game_w13_native_bridge import copy_game_source,GameW13NativeBridge,WORKER_ID
from .game_w13_native import verify_native_report
from .coordinator_window import (
    CoordinatorIndex,from_existing_workstation,
    freshly_reverify_linked_jobs,run_exact_linked_job)
from .cp_motion import one_cp_handoff,workstation_cp_view

WINDOW="complete-stack"
JOB="game-w13-cp-joined-001"
VERSION="world-v1"
SLOT="cp-game-w13-worlds"
FIXTURE=Path(__file__).resolve().parents[2]/"network/tests/fixtures/game_w13_native_cp_example.json"
ORIGINAL_JOBS=(
    "nih-scope-001","ontology-job","nih-reasoning-001",
    "nih-packet-001","nih-prototype-001","build-game-room-v1",LIVE_JOB,
)

def join(*,data_dir:Path,output_dir:Path,with_browser=True):
    data,output=Path(data_dir),Path(output_dir)
    existing=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot()
    if JOB not in existing:
        # This is the existing seven-job game+temporal construction, not a new
        # harness or second source owner.
        live=continue_stack(data_dir=data,output_dir=output,real_browser=with_browser)
    else:
        # When continuing, reverify the seven original jobs, do NOT reseed the
        # original exact-count assertions over their own successor.
        for old in ORIGINAL_JOBS:
            if reverify_job(data_dir=data,job_id=old)["status"]!="COMPLETE":
                raise ValueError("original temporal/game source was changed")
        live=json.loads((output/"game-temporal-complete-stack.json").read_text())
        if with_browser:
            from .game_temporal_browser import witness
            browser=witness(data_dir=data,output_dir=output)
            if not browser["game_solved"]:
                raise ValueError("original live game WITNESS unavailable")
    fixture=json.loads(FIXTURE.read_text(encoding="utf8"))
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_game_source(data,version_id=VERSION,allow_copy=True)
    checked=prepare(data_dir=data,worker_id=WORKER_ID,version_id=VERSION,inputs_file=FIXTURE)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if JOB not in runtime.snapshot():
        GameW13NativeBridge(runtime=runtime,workstation=desk).admit(
            version_id=VERSION,inputs=fixture,from_actor="complete-stack-game-world",
            job_id=JOB,lane_id="game")
    else:
        h=runtime.get(JOB)
        if h.metadata.get("worker_id")!=WORKER_ID or h.inputs!=fixture:
            raise ValueError("existing W13 game CP differs from owner source")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    _,slots=index.definition(WINDOW)
    x=next((q for q in slots["game"] if q["slot"]==SLOT),None)
    if x is None:
        raise ValueError("original research CP graph lost its game slot")
    if x["source_kind"]=="planned":
        index.bind_planned(WINDOW,"game",slot=SLOT,
                           job_id=JOB,worker_id=WORKER_ID,version_id=VERSION)
    elif (x.get("source_kind"),x.get("job_id"),x.get("worker_id"),x.get("version_id"))!=(
          "runtime-job",JOB,WORKER_ID,VERSION):
        raise ValueError("W13 CP linked to another source job")
    status=run_exact_linked_job(
        index,WINDOW,"game",SLOT,JOB,from_existing_workstation(data),
        lambda job_id,confirm:run_job(data_dir=data,job_id=job_id,confirm_execute=confirm))
    if status["status"]!="COMPLETE":
        raise ValueError("W13 native worker not completed")
    if reverify_job(data_dir=data,job_id=JOB)["status"]!="COMPLETE":
        raise ValueError("native W13 worker not independently verified")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    report=runtime.state(JOB).output["report"]
    verified=verify_native_report(fixture,report)
    view=workstation_cp_view(data)
    fresh=freshly_reverify_linked_jobs(
        index,WINDOW,view,lambda job_id:reverify_job(data_dir=data,job_id=job_id))
    graph=one_cp_handoff(index,WINDOW,fresh,reverified=True)["cp_automation"]
    if "GAME-W13-WORLDS" not in graph["witnessed"]:
        raise ValueError("game WORLD/W13 proof wasn't witnessed by original CP graph")
    next_gate=next(x for x in graph["checkpoints"] if x["checkpoint"]=="GAME-NATIVE-VERIFIER")
    if next_gate["state"]!="ADMISSIBLE":
        raise ValueError("independent game-verifier CP should be next real game movement")
    gate=next(x for x in graph["checkpoints"] if x["checkpoint"]=="NIH-P2-TEST")
    if gate["state"]!="BLOCKED" or "GAME-WORKER-READY" not in gate["blocked_by"]:
        raise ValueError("W13 finite computation incorrectly promoted entire NIH test")
    if len(runtime.snapshot())!=8:
        raise ValueError("not original eight source-owned jobs")
    result={"schema":"temporal-game-w13-native-join/v1",
            "real_original_native_jobs":8,
            "source_owned_w13_job":JOB,
            "native_w12_independent_replay":"PASS",
            "w13_worlds_witnessed":True,
            "w13_worlds_completed":verified["worlds_completed"],
            "next_game_checkpoint":"GAME-NATIVE-VERIFIER",
            "formal_nih_p2_test":gate["state"],
            "formal_blocked_by":gate["blocked_by"],
            "live_game_browser":live["game_temporal_browser"],
            "synthetic_only":True,
            "official_NIH_submission":False}
    output.mkdir(parents=True,exist_ok=True)
    (output/"game-w13-real-native-joined.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    (output/"game-w13-native-receipt.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    (output/"game-temporal-cp-frontier.json").write_text(
        json.dumps(graph,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--no-browser",action="store_true")
    a=p.parse_args(argv)
    print(json.dumps(join(data_dir=a.data_dir,output_dir=a.output_dir,
                          with_browser=not a.no_browser),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
