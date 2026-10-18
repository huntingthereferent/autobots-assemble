"""Real GAME-NATIVE-VERIFIER CP follows witnessed W13 in same temporal stack.

The ninth bounded job belongs to the ORIGINAL ProcessWorkstation/runtime journal.
WITNESS's executable independently replays the native W13 receipt, while the
host separately invokes the original pinned-W12 W13 replay checker.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import prepare,run_job,reverify_job
from .game_w13_temporal_join import join as original_eight,JOB as W13_JOB,WINDOW
from .game_native_verifier_bridge import (
    WORKER_ID,VERSION,JOB_ID,copy_verifier_source,NativeGameVerifierBridge)
from .coordinator_window import (CoordinatorIndex,from_existing_workstation,
                                 run_exact_linked_job,freshly_reverify_linked_jobs)
from .cp_motion import workstation_cp_view,one_cp_handoff

SLOT="cp-game-native-verifier"
ORIGINAL_EIGHT=(
    "nih-scope-001","ontology-job","nih-reasoning-001",
    "nih-packet-001","nih-prototype-001","build-game-room-v1",
    "live-game-temporal-001",W13_JOB
)

def join(*,data_dir:Path,output_dir:Path,with_browser=True):
    data,output=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    output.mkdir(parents=True,exist_ok=True)
    existing=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot()
    if JOB_ID not in existing:
        game=original_eight(data_dir=data,output_dir=output,with_browser=with_browser)
    else:
        for parent in ORIGINAL_EIGHT:
            if reverify_job(data_dir=data,job_id=parent)["status"]!="COMPLETE":
                raise ValueError("one of original eight source-owned jobs changed")
        game=json.loads((output/"game-w13-real-native-joined.json").read_text())
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_verifier_source(data,version_id=VERSION,allow_copy=True)
    spec=output/"game-native-verifier-request.json"
    expected='{"w13_job_id": "game-w13-cp-joined-001"}\n'
    if spec.exists() and spec.read_text()!=expected:
        raise ValueError("W13 game verifier owner request changed")
    spec.write_text(expected)
    prepare(data_dir=data,worker_id=WORKER_ID,version_id=VERSION,inputs_file=spec)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if JOB_ID not in runtime.snapshot():
        NativeGameVerifierBridge(runtime=runtime,workstation=desk).admit(
            version_id=VERSION,inputs={"w13_job_id":W13_JOB},
            from_actor="complete-stack-independent-game-witness",job_id=JOB_ID)
    else:
        h=runtime.get(JOB_ID)
        if h.metadata.get("worker_id")!=WORKER_ID or h.inputs["parent_job_id"]!=W13_JOB:
            raise ValueError("native game witness parent is different")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    _,lanes=index.definition(WINDOW)
    slot=next((x for x in lanes["game"] if x["slot"]==SLOT),None)
    if slot is None:
        raise ValueError("original Complete Stack missing game native witness checkpoint")
    if slot["source_kind"]=="planned":
        index.bind_planned(WINDOW,"game",slot=SLOT,
                           job_id=JOB_ID,worker_id=WORKER_ID,version_id=VERSION)
    elif (slot.get("source_kind"),slot.get("job_id"),
          slot.get("worker_id"),slot.get("version_id"))!=(
          "runtime-job",JOB_ID,WORKER_ID,VERSION):
        raise ValueError("another worker owns the independent game witness CP")
    status=run_exact_linked_job(
        index,WINDOW,"game",SLOT,JOB_ID,from_existing_workstation(data),
        lambda jid,confirm:run_job(data_dir=data,job_id=jid,confirm_execute=confirm))
    if status["status"]!="COMPLETE" or reverify_job(data_dir=data,job_id=JOB_ID)["status"]!="COMPLETE":
        raise ValueError("game native verifier source was not independently witnessed")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    cpview=workstation_cp_view(data)
    certified=freshly_reverify_linked_jobs(
        index,WINDOW,cpview,lambda j:reverify_job(data_dir=data,job_id=j))
    graph=one_cp_handoff(index,WINDOW,certified,reverified=True)["cp_automation"]
    required={"GAME-W13-WORLDS","GAME-NATIVE-VERIFIER","NIH-P2-PROTOTYPE"}
    if not required.issubset(set(graph["witnessed"])):
        raise ValueError("existing native CP lineage did not reverify")
    ready=next(x for x in graph["checkpoints"] if x["checkpoint"]=="GAME-WORKER-READY")
    if ready["state"]!="ADMISSIBLE":
        raise ValueError("source-pinned game worker readiness CP not the next admissible game work")
    phase2=next(x for x in graph["checkpoints"] if x["checkpoint"]=="NIH-P2-TEST")
    if phase2["state"]!="BLOCKED" or phase2["blocked_by"]!=["GAME-WORKER-READY"]:
        raise ValueError("independent W13 witness illegally bypassed source worker readiness")
    if len(runtime.snapshot())!=9:
        raise ValueError("not original native nine-job Complete Stack")
    result={"schema":"game-native-independent-verifier-complete-stack/v1",
            "original_live_game_browser":game["live_game_browser"],
            "native_jobs":9,"source_owned_game_verifier":JOB_ID,
            "w13_worlds_witnessed":True,
            "game_native_verifier_witnessed":True,
            "next_admissible_game_cp":"GAME-WORKER-READY",
            "phase_2_test":phase2["state"],
            "phase_2_blocked_by":phase2["blocked_by"],
            "synthetic_only":True,"official_NIH_submission":False}
    (output/"game-independent-verifier-complete-stack.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    (output/"game-independent-verifier-native-receipt.json").write_text(
        json.dumps(runtime.state(JOB_ID).output["report"],sort_keys=True,indent=2)+"\n")
    (output/"game-temporal-cp-frontier.json").write_text(
        json.dumps(graph,sort_keys=True,indent=2)+"\n")
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    parser.add_argument("--no-browser",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(join(data_dir=args.data_dir,output_dir=args.output_dir,
                          with_browser=not args.no_browser),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
