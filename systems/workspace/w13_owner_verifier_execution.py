"""Execute ONE original-owner W13 native verifier only from a new exact owner request.

Predecessor: the original 39025574748 W13 journal and its pinned research MOVE.
Owner-child consent is a DIFFERENT newly merged source; the predecessor receipt
does not authorize a new job. Uses existing ProcessWorkstation, CoordinatorIndex,
RuntimeJournal, native GAME-NATIVE-VERIFIER bridge and controls.run_job.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from .github_w13_continuation import (
    _git_blob, _object, validate_archive_metadata, unpack_native_runtime,
    RUN_ID, ARTIFACT_ID, ORIGINAL_DIGEST, ORIGINAL_HEAD, JOB_ID)
from .game_native_verifier_bridge import (
    NativeGameVerifierBridge, copy_verifier_source, WORKER_ID,
    OWNER_JOB_ID, OWNER_VERSION, OWNER_W13_JOB,
    OWNER_W13_RESULT_EVENT, OWNER_W13_FINGERPRINT)
from .native_research_join import verify_local_relation
from .w13_original_research_witness import RESEARCH_PATH
from .controls import reverify_job, run_job
from .coordinator_window import (
    CoordinatorIndex, freshly_reverify_linked_jobs, run_exact_linked_job)
from .cp_motion import workstation_cp_view, one_cp_handoff
from .native_receipt_projection import reverify_local
from .workstation import ProcessWorkstation
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal

REQUEST = "systems/workspace/native_job_requests/w13/game-native-verifier-github-001.json"
PARENT_RESEARCH_BLOB = "f8fbf981c75ccf53a8a72006053f8b02a31343dc"
VERIFIER_WORKER_BLOB = "39fbb7178fccd9c37bd33f6b670b560fdbac4d30"
VERIFIER_BRIDGE_BLOB = "694580a5e4c68c37eafafe11172fcf3bf37faa9d"
WORKER_PATH = "systems/workspace/game_native_verifier_worker_source/native_verifier.py"
BRIDGE_PATH = "systems/workspace/game_native_verifier_bridge.py"
SLOT = "cp-game-native-verifier"
WINDOW = "complete-stack"

EXPECTED_REQUEST = {
    "contract": "owner-w13-independent-native-game-verifier-one-shot/v1",
    "source_run_id": RUN_ID,
    "source_artifact_id": ARTIFACT_ID,
    "source_artifact_digest": ORIGINAL_DIGEST,
    "source_head_sha": ORIGINAL_HEAD,
    "original_w13_job_id": OWNER_W13_JOB,
    "original_w13_result_event_id": OWNER_W13_RESULT_EVENT,
    "original_w13_source_fingerprint": OWNER_W13_FINGERPRINT,
    "checkpoint": "GAME-NATIVE-VERIFIER",
    "job_id": OWNER_JOB_ID,
    "worker_id": WORKER_ID,
    "source_version": OWNER_VERSION,
    "worker_git_blob": VERIFIER_WORKER_BLOB,
    "bridge_git_blob": VERIFIER_BRIDGE_BLOB,
    "parent_research_git_blob": PARENT_RESEARCH_BLOB,
    "authorizes_source_copy": True,
    "authorizes_admission": True,
    "authorizes_execution": True,
    "execution_scope": "one-exact-native-verifier-child-on-original-owner-W13",
    "activation": "new-exact-request-in-owner-merged-protected-main",
}


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True,
            text=True, timeout=10, check=True)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Git owner merge or original source revision unavailable") from exc
    return completed.stdout.strip()


def authenticate_owner_request(repo_root: Path, owner_merge_sha: str) -> dict:
    """Authorize a source-copied job only through an ADDED, exact owner request.

    GitHub Actions must additionally authenticate actor=repository_owner,
    event=push, branch=main, and event SHA equals owner_merge_sha.
    """
    root = Path(repo_root).resolve()
    if not isinstance(owner_merge_sha, str) or not re.fullmatch("[0-9a-f]{40}", owner_merge_sha):
        raise ValueError("exact owner-merge SHA required")
    if not (root / ".git").exists() or _git(root, "rev-parse", "HEAD")!=owner_merge_sha:
        raise ValueError("checkout does not equal trusted owner merge")
    parents = _git(root, "rev-list", "--parents", "-n", "1", owner_merge_sha).split()
    if len(parents)!=3:
        raise ValueError("native child requires a two-parent protected-main owner merge")
    diff=_git(root,"diff","--name-status",parents[1],owner_merge_sha,"--",
              "systems/workspace/native_job_requests/w13")
    if diff!="A\t"+REQUEST:
        raise ValueError("owner merge must add exactly one new authorized native child request")
    auth=root/REQUEST
    if (not auth.is_file() or auth.is_symlink()
            or auth.stat().st_size>4096
            or _git_blob(auth)!=_git(root,"rev-parse",owner_merge_sha+":"+REQUEST)):
        raise ValueError("original owner request missing, changed or unsafe")
    request=_object(auth)
    if request!=EXPECTED_REQUEST:
        raise ValueError("owner authorization disagrees with exact execution scope or source pins")
    for rel,expected in (
        (WORKER_PATH,VERIFIER_WORKER_BLOB),
        (BRIDGE_PATH,VERIFIER_BRIDGE_BLOB),
        (RESEARCH_PATH,PARENT_RESEARCH_BLOB),
    ):
        path=root/rel
        if not path.is_file() or path.is_symlink() or _git_blob(path)!=expected:
            raise ValueError("owner-request source edition changed: "+rel)
    return request


def execute_exact_authorized_child(*, artifact_dir: Path, source_binding: Path,
                                   repo_root: Path, owner_merge_sha: str) -> dict:
    """One temporary original journal, ONE new existing native worker, no raw export."""
    root=Path(repo_root).resolve()
    authenticate_owner_request(root,owner_merge_sha)
    origin=_object(Path(source_binding))
    if (origin.get("repository")!="huntingthereferent/autobots-assemble"
            or origin.get("workflow")!="workstation-w13-owner-merged-one-shot"
            or origin.get("run_id")!=RUN_ID
            or origin.get("artifact_id")!=ARTIFACT_ID
            or origin.get("attempt")!=1
            or origin.get("head_sha")!=ORIGINAL_HEAD
            or origin.get("digest")!=ORIGINAL_DIGEST):
        raise ValueError("original owner-run source binding differs from authorized parent")
    validate_archive_metadata(Path(artifact_dir),origin,repo_root=root)
    with TemporaryDirectory(prefix="owner-w13-native-child-") as tmp:
        data=Path(tmp)/"original-runtime"
        unpack_native_runtime(Path(artifact_dir),data)
        receipt=verify_local_relation(
            data_dir=data,job_id=JOB_ID,repo_root=root,
            research_commit=owner_merge_sha,research_path=RESEARCH_PATH)
        if (receipt.get("native_verified") is not True
                or receipt.get("relation")!="EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH"
                or receipt.get("result_event_id")!=OWNER_W13_RESULT_EVENT
                or receipt.get("native_source_fingerprint")!=OWNER_W13_FINGERPRINT):
            raise ValueError("original real W13 parent result not fresh and source-verified")

        runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
        if OWNER_JOB_ID in runtime.snapshot():
            raise ValueError("original owner journal already contains the requested child")
        index=CoordinatorIndex(data/"coordinator-windows.jsonl")
        _,links=index.definition(WINDOW)
        child=[x for x in links.get("game",[]) if x.get("slot")==SLOT]
        if len(child)!=1 or child[0].get("source_kind")!="planned":
            raise ValueError("original verifier slot already assigned or unavailable")
        before=freshly_reverify_linked_jobs(index,WINDOW,workstation_cp_view(data),
            lambda job:reverify_job(data_dir=data,job_id=job))
        states={x["checkpoint"]:x["state"] for x in
                one_cp_handoff(index,WINDOW,before,reverified=True)["cp_automation"]["checkpoints"]}
        if (states.get("GAME-W13-WORLDS")!="WITNESSED"
                or states.get("GAME-NATIVE-VERIFIER")!="ADMISSIBLE"):
            raise ValueError("original source-native checkpoint not admissible")

        # Original source-owned worker and exact explicit owner-merged request.
        copy_verifier_source(data,version_id=OWNER_VERSION,allow_copy=True)
        desk=ProcessWorkstation(data/"workstation")
        bridge=NativeGameVerifierBridge(runtime=runtime,workstation=desk)
        native=bridge.admit(version_id=OWNER_VERSION,
            inputs={"w13_job_id":OWNER_W13_JOB},
            from_actor="owner-protected-main-source-request",job_id=OWNER_JOB_ID)
        if (native.dependencies!=(OWNER_W13_JOB,)
                or runtime.state(OWNER_JOB_ID).status!="READY"):
            raise ValueError("original owner child did not admit as separate native work")
        index.bind_planned(WINDOW,"game",slot=SLOT,job_id=OWNER_JOB_ID,
                           worker_id=WORKER_ID,version_id=OWNER_VERSION)
        job=run_exact_linked_job(
            index,WINDOW,"game",SLOT,OWNER_JOB_ID,workstation_cp_view(data),
            lambda job_id,confirmation:run_job(
                data_dir=data,job_id=job_id,confirm_execute=confirmation))
        if job.get("status")!="COMPLETE":
            raise ValueError("owner-authorized native child did not complete")
        evidence=reverify_local(data,OWNER_JOB_ID)
        if evidence["recorded_status"]!="COMPLETE" or evidence["verification"]!="FRESH_NATIVE_REVERIFICATION_LOCAL":
            raise ValueError("owner child completion is not independently native-verified")
        checked=freshly_reverify_linked_jobs(index,WINDOW,workstation_cp_view(data),
            lambda job:reverify_job(data_dir=data,job_id=job))
        proof=one_cp_handoff(index,WINDOW,checked,reverified=True)["cp_automation"]
        state={x["checkpoint"]:x["state"] for x in proof["checkpoints"]}
        if (state.get("GAME-W13-WORLDS")!="WITNESSED"
                or state.get("GAME-NATIVE-VERIFIER")!="WITNESSED"
                or state.get("GAME-WORKER-READY")!="ADMISSIBLE"):
            raise ValueError("actual child did not advance original certified CP frontier")
        results=[x for x in evidence["events"] if x["type"]=="RESULT"]
        if len(results)!=1 or results[0]["result_status"]!="COMPLETE":
            raise ValueError("one exact completed child RESULT required")
        return {
            "schema":"original-w13-owner-child-native-result/v1",
            "original_run_id":RUN_ID,
            "owner_authorization_commit":owner_merge_sha,
            "parent_job_id":OWNER_W13_JOB,
            "parent_event_id":OWNER_W13_RESULT_EVENT,
            "child_job_id":OWNER_JOB_ID,
            "child_result_event_id":results[0]["event_id"],
            "child_worker_source_fingerprint":evidence["source_fingerprint"],
            "game_w13_cp":state["GAME-W13-WORLDS"],
            "game_native_verifier_cp":state["GAME-NATIVE-VERIFIER"],
            "game_worker_ready_cp":state["GAME-WORKER-READY"],
            "source_owner_authorized":True,
            "new_child_admitted":True,
            "one_native_child_executed":True,
            "fresh_native_child_reverified":True,
            "private_journal_uploaded":False,
            "official_game_or_scientific_claim":False,
        }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir",required=True,type=Path)
    p.add_argument("--source-binding",required=True,type=Path)
    p.add_argument("--repo-root",required=True,type=Path)
    p.add_argument("--owner-merge-sha",required=True)
    a=p.parse_args(argv)
    print(json.dumps(execute_exact_authorized_child(
        artifact_dir=a.artifact_dir,source_binding=a.source_binding,
        repo_root=a.repo_root,owner_merge_sha=a.owner_merge_sha),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
