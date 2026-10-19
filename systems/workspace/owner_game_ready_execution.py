"""One owner-merged readiness job, existing runtime, encrypted continuation."""
from __future__ import annotations
import base64
from hashlib import sha1
import json
import os
from pathlib import Path
import shutil
import subprocess

from .owner_game_ready_bridge import JOB_ID, WORKER_ID, VERSION, SOURCE, FILE, LOCATOR
from .owner_temporal_handoff import SOURCES, CHILD_EVENT

REQUEST = "systems/workspace/native_readiness_requests/w13/game-worker-ready-owner-001.json"


def blob(path):
    raw = Path(path).read_bytes()
    return sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def expected_request():
    return {"contract":"owner-W13-adapter-readiness-one-shot/v1", "job_id":JOB_ID,
        "worker_id":WORKER_ID,"version":VERSION,"sources":SOURCES,
        "owner_child_event":CHILD_EVENT,
        "worker_git_blob":blob(SOURCE/FILE),
        "bridge_git_blob":blob(Path(__file__).with_name("owner_game_ready_bridge.py")),
        "authorizes_source_copy":True,"authorizes_admission":True,"authorizes_execution":True,
        "authorizes_encrypted_ready_retention":True,"retention_days":1,
        "authorizes_raw_journal_export":False,"authorizes_NIH_P2_TEST":False,
        "temporal_history":"authenticated-external-input-not-native-parent"}


def authenticate(root, merge):
    root = Path(root)
    def git(*args):
        return subprocess.run(["git","-C",str(root),*args],capture_output=True,
            text=True,check=True,timeout=10).stdout.strip()
    if (os.environ.get("GITHUB_EVENT_NAME") != "push"
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_REPOSITORY") != "huntingthereferent/autobots-assemble"
            or os.environ.get("GITHUB_ACTOR") != "huntingthereferent"
            or os.environ.get("GITHUB_RUN_ATTEMPT") != "1"
            or os.environ.get("GITHUB_SHA") != merge or git("rev-parse","HEAD") != merge):
        raise ValueError("exact first-attempt owner push on main required")
    parents = git("rev-list","--parents","-n","1",merge).split()
    if len(parents) != 3 or git("diff","--name-status",parents[1],merge,"--",str(Path(REQUEST).parent)) != "A\t"+REQUEST:
        raise ValueError("owner merge must add exactly one new readiness request")
    path = root/REQUEST
    if (not path.is_file() or path.is_symlink() or path.stat().st_size>8192
            or blob(path) != git("rev-parse",merge+":"+REQUEST)
            or json.loads(path.read_text()) != expected_request()):
        raise ValueError("exact owner readiness scope or source pins differ")


def execute(*, root, owner_commit, output):
    authenticate(root, owner_commit)
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from .owner_temporal_handoff import authenticated_sources
    from .owner_game_ready_bridge import OwnerGameReadyBridge
    from .workstation import ProcessWorkstation
    from .controls import run_job, reverify_job
    from .native_receipt_projection import reverify_local
    from .coordinator_window import (CoordinatorIndex,run_exact_linked_job,
        from_existing_workstation,freshly_reverify_linked_jobs)
    from .cp_motion import workstation_cp_view,one_cp_handoff
    from .owner_native_evidence_vault import seal_verified,restore_verified
    output = Path(output)
    if output.exists() or output.is_symlink() or not output.parent.is_dir() or output.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("new encrypted continuation destination outside repo required")
    private = base64.b64decode(os.environ["PRIVATE_KEY_B64"],validate=True)
    from .owner_temporal_handoff import PUBLIC_KEY
    with authenticated_sources(token=os.environ["GH_TOKEN"],private=private) as source:
        data = source/"owner-native"
        shutil.copyfile(source/"temporal.zip",data/"external-temporal.zip")
        (data/"external-temporal.zip").chmod(0o600)
        runtime = HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
        original_jobs = set(runtime.snapshot())
        if JOB_ID in original_jobs:
            raise ValueError("readiness is already admitted")
        index = CoordinatorIndex(data/"coordinator-windows.jsonl")
        _, lanes = index.definition("complete-stack")
        slots = [x for x in lanes["game"] if x["slot"] == "cp-game-worker-ready"]
        if len(slots) != 1 or slots[0]["source_kind"] != "planned":
            raise ValueError("original owner readiness slot is not available")
        desk = ProcessWorkstation(data/"workstation")
        desk.copy_source(SOURCE,worker_id=WORKER_ID,version_id=VERSION,source_locator=LOCATOR)
        OwnerGameReadyBridge(runtime=runtime,workstation=desk).admit(from_actor="owner-merged-readiness-request")
        index.bind_planned("complete-stack","game",slot="cp-game-worker-ready",
            job_id=JOB_ID,worker_id=WORKER_ID,version_id=VERSION)
        run_exact_linked_job(index,"complete-stack","game","cp-game-worker-ready",JOB_ID,
            from_existing_workstation(data),
            lambda job,confirmation:run_job(data_dir=data,job_id=job,confirm_execute=confirmation))
        ready = reverify_local(data,JOB_ID)
        events = [x for x in ready["events"] if x["type"] == "RESULT" and x["result_status"] == "COMPLETE"]
        if len(events)!=1 or ready["verification"]!="FRESH_NATIVE_REVERIFICATION_LOCAL":
            raise ValueError("one source-verified readiness RESULT required")
        now = HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
        if set(now.snapshot()) != original_jobs|{JOB_ID}:
            raise ValueError("readiness execution changed the native job scope")
        checked = freshly_reverify_linked_jobs(index,"complete-stack",workstation_cp_view(data),
            lambda job:reverify_job(data_dir=data,job_id=job))
        frontier = one_cp_handoff(index,"complete-stack",checked,reverified=True)["cp_automation"]
        if "GAME-WORKER-READY" not in frontier["witnessed"] or "NIH-P2-TEST" in frontier["witnessed"]:
            raise ValueError("readiness did not advance its exact checkpoint frontier")
        sealed = seal_verified(data_dir=data,public_key_b64=PUBLIC_KEY,
            owner_execution_commit=owner_commit,output=output)
        restore_verified(encrypted=output,private_key_raw=private,destination=source/"restored-ready",
            expected_owner_execution_commit=owner_commit,expected_child_event=CHILD_EVENT)
        restored = reverify_local(source/"restored-ready",JOB_ID)
        if restored != ready:
            raise ValueError("encrypted readiness restoration changed its exact native evidence")
        return {"schema":"owner-W13-native-ready-result/v1","owner_merge":owner_commit,
            "job_id":JOB_ID,"ready_result_event":events[0]["event_id"],
            "ready_source_fingerprint":ready["source_fingerprint"],
            "game_worker_ready_witnessed":True,"external_temporal_input_reverified":True,
            "temporal_history_imported":False,"native_job_count_added":1,
            "encrypted_retention":sealed,"encrypted_ready_restore_reverified":True,
            "separate_run_ready_restore_witnessed":False,"nih_p2_test_witnessed":False,
            "private_journal_published":False,"retention_days":1}


if __name__ == "__main__":
    print(json.dumps(execute(root=Path.cwd(),owner_commit=os.environ["GITHUB_SHA"],
        output=Path(os.environ["RUNNER_TEMP"])/"owner-ready-sealed"/"continuation.enc"),sort_keys=True))
