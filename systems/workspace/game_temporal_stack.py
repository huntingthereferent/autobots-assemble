"""Continue existing Complete Stack with actual native game-to-temporal execution.

Existing 6 source-owned jobs first. Seventh native BUILD writes the interactive
bridge; Chromium WITNESS calls the real emitted prototype on game turns.
Formal NIH-P2-TEST is intentionally NOT claimed ahead of GAME-WORKER-READY.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .coordinator_window import CoordinatorIndex
from .controls import run_job,reverify_job
from .game_temporal_bridge import (
    WORKER_ID,JOB_ID,LiveJoinBridge,copy_join_source)
from .nih_temporal_game_stack import join as original_join,WINDOW, _slot
from .cp_motion import workstation_cp_view,one_cp_handoff
from .coordinator_window import freshly_reverify_linked_jobs

VERSION="live-v1"
ROOT=Path(__file__).resolve().parents[2]
REQUEST=ROOT/"network/tests/fixtures/game_temporal_live_example.json"

def continue_stack(*,data_dir:Path,output_dir:Path,real_browser=True):
    data,output=Path(data_dir),Path(output_dir)
    state_file = data / "runtime.jsonl"
    if state_file.exists() and JOB_ID in HandoffRuntime(
            event_store=RuntimeJournal(state_file)).snapshot():
        # A continuation must not re-create the old six-job seed over the
        # seventh real native job. Reverify every original source-owned parent
        # and reuse its frozen report; do NOT invent new events.
        for original_id in (
                "nih-scope-001", "ontology-job", "nih-reasoning-001",
                "nih-packet-001", "nih-prototype-001", "build-game-room-v1"):
            verified=reverify_job(data_dir=data,job_id=original_id)
            if verified["status"]!="COMPLETE":
                raise ValueError("original complete-stack parent no longer verified")
        original=json.loads((output/"complete-stack-temporal-game.json").read_text(encoding="utf8"))
        if (original.get("phase_2_prototype")!="WITNESSED"
                or original.get("prototype_native_witness")!="PASS"):
            raise ValueError("original stack checkpoint report no longer trusted")
    else:
        original=original_join(data_dir=data,output_dir=output,
                               browser_witness=real_browser,
                               packet_build=True,prototype_build=True)
    request=json.loads(REQUEST.read_text(encoding="utf8"))
    desk=ProcessWorkstation(data/"workstation")
    try:desk.inspect(worker_id=WORKER_ID,version_id=VERSION)
    except KeyError:copy_join_source(data,version_id=VERSION,allow_copy=True)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    bridge=LiveJoinBridge(runtime=runtime,workstation=desk)
    if JOB_ID not in runtime.snapshot():
        bridge.admit(version_id=VERSION,inputs=request,
                     from_actor="complete-stack-game-temporal-world",job_id=JOB_ID)
    else:
        h=runtime.get(JOB_ID)
        if h.metadata.get("worker_id")!=WORKER_ID or h.inputs.get("request")!=request:
            raise ValueError("original live relation was changed")
    index=CoordinatorIndex(data/"coordinator-windows.jsonl")
    slot="game-temporal-live-join"
    existing=_slot(index,"game",slot)
    if existing is None:
        index.link_runtime(WINDOW,"game",slot=slot,job_id=JOB_ID,
                           worker_id=WORKER_ID,version_id=VERSION)
    elif (existing.get("source_kind"),existing.get("job_id"),
          existing.get("worker_id"),existing.get("version_id"))!=(
          "runtime-job",JOB_ID,WORKER_ID,VERSION):
        raise ValueError("game-temporal link belongs to another worker")
    move=run_job(data_dir=data,job_id=JOB_ID,confirm_execute=JOB_ID)
    if move["status"]!="COMPLETE" or reverify_job(data_dir=data,job_id=JOB_ID)["status"]!="COMPLETE":
        raise ValueError("live game source-owned BUILD unverified")
    from .game_temporal_browser import witness
    if real_browser:
        browser=witness(data_dir=data,output_dir=output)
        if not browser["game_solved"]:
            raise ValueError("real game did not complete with prototype queries")
    else:
        browser=None
        bundle=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).state(JOB_ID).output["bundle"]
        for name,content in (
            ("temporal-game.html",bundle["html"]),
            ("temporal_bridge_server.py",bundle["server_source"]),
            ("temporal_query.py",bundle["temporal_source"]),
            ("temporal_dataset.json",bundle["temporal_dataset"]),
            ("game-temporal-config.json",json.dumps(bundle["config"],sort_keys=True,indent=2)+"\n"),
        ):
            (output/name).write_text(content,encoding="utf8")
    cpview=workstation_cp_view(data)
    checked=freshly_reverify_linked_jobs(
        index,WINDOW,cpview,lambda job_id:reverify_job(data_dir=data,job_id=job_id))
    graph=one_cp_handoff(index,WINDOW,checked,reverified=True)["cp_automation"]
    gate=next(x for x in graph["checkpoints"] if x["checkpoint"]=="NIH-P2-TEST")
    if gate["state"]!="BLOCKED" or "GAME-WORKER-READY" not in gate["blocked_by"]:
        raise ValueError("live join incorrectly claimed unverified game CP")
    if "NIH-P2-PROTOTYPE" not in graph["witnessed"]:
        raise ValueError("live game lost source-owned temporal prototype")
    if len(HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl")).snapshot())!=7:
        raise ValueError("not same original seven source-owned jobs")
    result={"schema":"complete-stack-live-temporal-game/v1",
            "original_temporary_stack":original["schema"],
            "source_owned_jobs":7,
            "new_native_build":JOB_ID,
            "game_temporal_browser":"PASS" if browser else "NOT_RUN",
            "game_to_real_python_queries":browser["live_queries"] if browser else 0,
            "formally_witnessed_nih_p2_test":False,
            "formal_cp_status":gate["state"],
            "formal_cp_blocked_by":gate["blocked_by"],
            "source_owned_witness":True,
            "no_ai_helper_assumed":True,
            "synthetic_only":True}
    (output/"game-temporal-complete-stack.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    (output/"game-temporal-cp-frontier.json").write_text(json.dumps(graph,sort_keys=True,indent=2)+"\n")
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--no-browser",action="store_true")
    x=p.parse_args(argv)
    print(json.dumps(continue_stack(data_dir=x.data_dir,output_dir=x.output_dir,
                                    real_browser=not x.no_browser),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
