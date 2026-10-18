"""Read-only readiness gate for the real archived W13 -> native verifier CP.

Uses the actual source-owned GitHub W13 archive and native journal, not a
synthetic same-named job. Re-verifies original native computation via existing
Workstation controls and checks coordinator source pins. No copying worker
source, admission, execution, helper birth, or journal publication.
"""
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re

from .github_w13_continuation import (
    RUN_ID, ARTIFACT_ID, ORIGINAL_DIGEST, ORIGINAL_HEAD, JOB_ID,
    _object, _git_blob, validate_archive_metadata, unpack_native_runtime,
)
from .w13_original_research_witness import RESEARCH_PATH
from .native_research_join import verify_local_relation
from .game_native_verifier_bridge import (
    OWNER_JOB_ID, OWNER_VERSION, OWNER_W13_JOB,
    OWNER_W13_FINGERPRINT, OWNER_W13_RESULT_EVENT, WORKER_ID, VERIFIER,
    SOURCE_DIRECTORY, SOURCE_FILE,
)
from .cp_motion import workstation_cp_view, one_cp_handoff
from .coordinator_window import CoordinatorIndex, freshly_reverify_linked_jobs
from .controls import reverify_job
from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal

SCHEMA = "owner-w13-game-native-verifier-source-preflight/v1"
EXPECTED_WITNESS_BLOB = "39fbb7178fccd9c37bd33f6b670b560fdbac4d30"
EXPECTED_PARENT_BLOB = "f8fbf981c75ccf53a8a72006053f8b02a31343dc"
EXPECTED_WINDOW = "complete-stack"
EXPECTED_PARENT_SLOT = "cp-game-w13-worlds"
EXPECTED_CHILD_SLOT = "cp-game-native-verifier"
OWNER_REQUEST = "systems/workspace/native_job_requests/w13/game-native-verifier-github-001.json"


def examine_original(*, artifact_dir: Path, source_binding: Path,
                     repo_root: Path, research_commit: str) -> dict:
    """An independently replayed predecessor may open a CP, not staff it."""
    if (not isinstance(research_commit,str) or
            re.fullmatch("[0-9a-f]{40}", research_commit) is None):
        raise ValueError("exact committed research revision required")
    root = Path(repo_root).resolve()
    origin = _object(Path(source_binding))
    if (origin.get("repository")!="huntingthereferent/autobots-assemble"
            or origin.get("workflow")!="workstation-w13-owner-merged-one-shot"
            or origin.get("run_id")!=RUN_ID
            or origin.get("artifact_id")!=ARTIFACT_ID
            or origin.get("attempt")!=1
            or origin.get("head_sha")!=ORIGINAL_HEAD
            or origin.get("digest")!=ORIGINAL_DIGEST):
        raise ValueError("original owner W13 provenance mismatched")

    witness_source = SOURCE_DIRECTORY / SOURCE_FILE
    if (not witness_source.is_file() or witness_source.is_symlink()
            or not witness_source.resolve().is_relative_to(root)
            or _git_blob(witness_source)!=EXPECTED_WITNESS_BLOB):
        raise ValueError("independent native verifier source differs from pinned edition")
    record_path = root / RESEARCH_PATH
    if (not record_path.is_file() or record_path.is_symlink()
            or _git_blob(record_path)!=EXPECTED_PARENT_BLOB):
        raise ValueError("original admitted W13 research source changed")
    if (root / OWNER_REQUEST).exists():
        raise ValueError("owner-child authorization requires separate source review")

    validate_archive_metadata(Path(artifact_dir), origin, repo_root=root)
    with TemporaryDirectory(prefix="owner-w13-next-cp-") as scratch:
        data = Path(scratch)/"private"
        unpack_native_runtime(Path(artifact_dir),data)
        exact = verify_local_relation(
            data_dir=data, job_id=JOB_ID, repo_root=root,
            research_commit=research_commit, research_path=RESEARCH_PATH)
        if (exact["relation"]!="EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH"
                or exact["native_verified"] is not True
                or exact["result_event_id"]!=OWNER_W13_RESULT_EVENT
                or exact["native_source_fingerprint"]!=OWNER_W13_FINGERPRINT):
            raise ValueError("original W13 source-native RESULT cannot be reverified")

        runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
        if OWNER_W13_JOB!=JOB_ID or OWNER_JOB_ID in runtime.snapshot():
            raise ValueError("owner child already admitted or original parent missing")
        index=CoordinatorIndex(data/"coordinator-windows.jsonl")
        _, links=index.definition(EXPECTED_WINDOW)
        game=links.get("game",())
        parent=[row for row in game if row.get("slot")==EXPECTED_PARENT_SLOT]
        child=[row for row in game if row.get("slot")==EXPECTED_CHILD_SLOT]
        if (len(parent)!=1 or len(child)!=1
                or parent[0].get("source_kind")!="runtime-job"
                or parent[0].get("job_id")!=JOB_ID
                or child[0].get("source_kind")!="planned"):
            raise ValueError("owner coordinator parent or unstaffed verifier slot changed")

        # Recheck coordinator linkage through original controls: no new job.
        cpview=workstation_cp_view(data)
        independently_checked=freshly_reverify_linked_jobs(
            index,EXPECTED_WINDOW,cpview,
            lambda job_id:reverify_job(data_dir=data,job_id=job_id))
        frontier=one_cp_handoff(
            index,EXPECTED_WINDOW,independently_checked,reverified=True)["cp_automation"]
        states={r["checkpoint"]:r["state"] for r in frontier["checkpoints"]}
        if (states.get("GAME-W13-WORLDS")!="WITNESSED"
                or states.get("GAME-NATIVE-VERIFIER")!="ADMISSIBLE"
                or states.get("GAME-WORKER-READY")!="BLOCKED"
                or "GAME-NATIVE-VERIFIER" not in frontier["frontier"]):
            raise ValueError("real W13 original CP is not admissible for separate owner work")

        return {
            "schema":SCHEMA,
            "status":"SOURCE_VERIFIED_ADMISSIBLE_NOT_ADMITTED",
            "original_run_id":RUN_ID,
            "original_artifact_id":ARTIFACT_ID,
            "original_archive_digest":ORIGINAL_DIGEST,
            "original_w13_job":OWNER_W13_JOB,
            "original_result_event":OWNER_W13_RESULT_EVENT,
            "original_native_reverified":True,
            "game_w13_cp":"WITNESSED",
            "game_native_verifier_cp":"ADMISSIBLE",
            "game_worker_ready_cp":"BLOCKED",
            "registered_verifier_worker":WORKER_ID,
            "registered_verifier_edition":OWNER_VERSION,
            "registered_verifier_source_blob":EXPECTED_WITNESS_BLOB,
            "candidate_child_job_id":OWNER_JOB_ID,
            "owner_child_authorized":False,
            "child_job_admitted":False,
            "child_job_executed":False,
            "raw_journal_published":False,
            "external_scientific_claim":False,
        }


def main(argv=None):
    p=ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir",type=Path,required=True)
    p.add_argument("--source-binding",type=Path,required=True)
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--research-commit",required=True)
    a=p.parse_args(argv)
    print(json.dumps(examine_original(
        artifact_dir=a.artifact_dir, source_binding=a.source_binding,
        repo_root=a.repo_root,research_commit=a.research_commit),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
