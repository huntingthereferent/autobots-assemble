"""Advance real GAME-WORKER-READY in the original temporal/game workstation.

Ten exact source-owned jobs; this is an adapter readiness WITNESS. It makes
NIH-P2-TEST admissible for *future* source-owned construction and independent
testing. It does not award NIH-P2-TEST based on game readiness alone.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import prepare,run_job,reverify_job
from .game_native_verifier_temporal_join import join as previous_nine,JOB_ID as NATIVE_WITNESS
from .game_worker_ready_bridge import (
    WORKER_ID,VERSION,JOB_ID,copy_ready_source,GameReadyBridge)
from .coordinator_window import (
    CoordinatorIndex,from_existing_workstation,
    run_exact_linked_job,freshly_reverify_linked_jobs)
from .cp_motion import workstation_cp_view,one_cp_handoff

WINDOW="complete-stack"
SLOT="cp-game-worker-ready"
ORIGINAL_NINE=(
    "nih-scope-001","ontology-job","nih-reasoning-001",
    "nih-packet-001","nih-prototype-001","build-game-room-v1",
    "live-game-temporal-001","game-w13-cp-joined-001",NATIVE_WITNESS
)

def join(*,data_dir:Path,output_dir:Path,with_browser=True):
    data,output=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    output.mkdir(parents=True,exist_ok=True)
    existing=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot()
    if JOB_ID not in existing:
        nine=previous_nine(data_dir=data,output_dir=output,with_browser=with_browser)
    else:
        for parent in ORIGINAL_NINE:
            if reverify_job(data_dir=data,job_id=parent)["status"]!="COMPLETE":
                raise ValueError("one of original source-owned game workers changed")
        nine=json.loads((output/"game-independent-verifier-complete-stack.json").read_text())
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_ready_source(data,version_id=VERSION,allow_copy=True)
    spec=output/"game-adapter-ready-request.json"
    request='{"verify_game_adapter": true}\n'
    if spec.exists() and spec.read_text()!=request:
        raise ValueError("source owner game readiness request changed")
    spec.write_text(request)
    prepare(data_dir=data,worker_id=WORKER_ID,version_id=VERSION,inputs_file=spec)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if JOB_ID not in runtime.snapshot():
        GameReadyBridge(runtime=runtime,workstation=desk).admit(
            version_id=VERSION,inputs={"verify_game_adapter":True},
            from_actor="original-complete-stack-game-adapter",job_id=JOB_ID)
    else:
        h=runtime.get(JOB_ID)
        if h.metadata.get("worker_id")!=WORKER_ID or h.dependencies!=(
            "game-w13-cp-joined-001",NATIVE_WITNESS,"live-game-temporal-001"):
            raise ValueError("game ready child does not own source-bound parents")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    _,lanes=index.definition(WINDOW)
    slot=next((x for x in lanes["game"] if x["slot"]==SLOT),None)
    if slot is None:
        raise ValueError("original game readiness CP slot absent")
    if slot["source_kind"]=="planned":
        index.bind_planned(WINDOW,"game",slot=SLOT,
                           job_id=JOB_ID,worker_id=WORKER_ID,version_id=VERSION)
    elif (slot.get("source_kind"),slot.get("job_id"),
          slot.get("worker_id"),slot.get("version_id"))!=(
          "runtime-job",JOB_ID,WORKER_ID,VERSION):
        raise ValueError("game ready CP slot belongs to a different worker")
    state=run_exact_linked_job(
        index,WINDOW,"game",SLOT,JOB_ID,from_existing_workstation(data),
        lambda jid,confirm:run_job(data_dir=data,job_id=jid,confirm_execute=confirm))
    if state["status"]!="COMPLETE" or reverify_job(data_dir=data,job_id=JOB_ID)["status"]!="COMPLETE":
        raise ValueError("game native adapter readiness didn't receive source-owned WITNESS")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    checked=freshly_reverify_linked_jobs(
        index,WINDOW,workstation_cp_view(data),
        lambda jid:reverify_job(data_dir=data,job_id=jid))
    graph=one_cp_handoff(index,WINDOW,checked,reverified=True)["cp_automation"]
    required={"GAME-W13-WORLDS","GAME-NATIVE-VERIFIER","GAME-WORKER-READY",
              "NIH-P1-PACKET","NIH-P2-PROTOTYPE"}
    if not required.issubset(set(graph["witnessed"])):
        raise ValueError("native source-owned game readiness did not advance true graph")
    phase2=next(x for x in graph["checkpoints"] if x["checkpoint"]=="NIH-P2-TEST")
    if phase2["state"]!="ADMISSIBLE" or phase2["blocked_by"]:
        raise ValueError("Phase 2 temporal game test should be admissible after readiness")
    if "NIH-P2-TEST" in graph["witnessed"]:
        raise ValueError("mere game readiness cannot fabricate NIH Phase 2 experiment")
    if len(runtime.snapshot())!=10:
        raise ValueError("original Complete Stack should contain ten real native jobs")
    result={
        "schema":"game-worker-ready-original-complete-stack/v1",
        "original_game_browser":nine["original_live_game_browser"],
        "native_jobs":10,"game_worker_ready_job":JOB_ID,
        "game_worker_ready_witnessed":True,
        "independent_game_verifier_witnessed":True,
        "next_admissible_NIH_checkpoint":"NIH-P2-TEST",
        "nih_p2_test_state":phase2["state"],
        "nih_p2_test_witnessed":False,
        "official_NIH_submission":False,"synthetic_only":True}
    (output/"game-worker-ready-complete-stack.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    (output/"game-worker-ready-native-receipt.json").write_text(
        json.dumps(runtime.state(JOB_ID).output["report"],sort_keys=True,indent=2)+"\n")
    (output/"game-temporal-cp-frontier.json").write_text(
        json.dumps(graph,sort_keys=True,indent=2)+"\n")
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
