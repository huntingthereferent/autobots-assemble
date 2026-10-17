"""B2 -> registered native W13 helper -> B3 verified return, on inherited workstation.

No AI provider, new scheduler, fake worker birth or new game engine.
The actual W13 source-owned Python subprocess runs through controls.run_job.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tarfile

from .branch_help import CAP_GAME_W13_NATIVE
from .controls import job_view, reverify_job, run_job
from .game_w13_native import CP_ID, VERIFIER, verify_native_report
from .game_w13_native_bridge import WORKER_ID
from .github_w13_continuation import unpack_native_runtime
from .workstation_harness import WorkstationContinuationHarness
from .workstation_native_feedback import WorkstationNativeFeedback
from .branch_help import verify_return

PARENT_JOB = "game-w13-github-001"
PARENT_VERSION = "w13-github-v1"
ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "network/tests/fixtures/game_w13_native_cp_example.json"
CAPABILITY = CAP_GAME_W13_NATIVE
OBSERVATION = "native-job:" + PARENT_JOB
RELATION = "Delegate the preserved WORLD W13 two-room game to a bounded workstation helper"


def read_json(path: Path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 160_000:
        raise ValueError("missing or unsafe W13 continuation evidence")
    return json.loads(path.read_text(encoding="utf8"))


def restore_continuation(evidence_dir: Path, data_dir: Path) -> dict:
    """Restore actual prior-run journals, not just a green CI status string."""
    report = read_json(evidence_dir / "continuation.json")
    if (report.get("schema") != "github-w13-cross-run-continuation/v1"
            or report.get("source_run_id") != 39025574748
            or report.get("source_artifact_id") != 12098716155
            or report.get("parent_job_id") != PARENT_JOB
            or report.get("parent_cp") != CP_ID
            or report.get("parent_state") != "WITNESSED"
            or report.get("fresh_replay") is not True
            or report.get("child_job_executed") is not False):
        raise ValueError("original native W13 continuity claim differs from recorded source")
    archive = evidence_dir / "continued-runtime.tar.gz"
    checksum = evidence_dir / "continued-runtime.sha256"
    if archive.is_symlink() or checksum.is_symlink() or not archive.is_file() or not checksum.is_file():
        raise ValueError("inherited W13 native runtime evidence missing")
    recorded = checksum.read_text(encoding="ascii").split()[0]
    if recorded != sha256(archive.read_bytes()).hexdigest():
        raise ValueError("inherited W13 runtime archive digest changed")
    # Reuse the previously implemented safe native journal/archive extractor.
    local_archive = evidence_dir / "native-runtime.tar.gz"
    local_checksum = evidence_dir / "native-runtime.sha256"
    if local_archive.exists() or local_checksum.exists():
        raise ValueError("refusing unexpected local archive alias")
    shutil.copyfile(archive, local_archive)
    shutil.copyfile(checksum, local_checksum)
    try:
        unpacked = unpack_native_runtime(evidence_dir, data_dir)
    finally:
        local_archive.unlink(missing_ok=True)
        local_checksum.unlink(missing_ok=True)
    if unpacked != report.get("inherited_archive_sha256") and not unpacked:
        raise ValueError("native source fingerprint missing")
    return report


def delegate_w13(*, data_dir: Path, output_dir: Path) -> dict:
    """Delegate to the real registered W13 source worker via B2 and B3."""
    parent = reverify_job(data_dir=data_dir, job_id=PARENT_JOB)
    native = job_view(data_dir=data_dir, job_id=PARENT_JOB)
    if (parent != {"job_id":PARENT_JOB,"status":"COMPLETE",
                   "reverified":True,"executed":False}
            or native.get("worker_id") != WORKER_ID
            or native.get("version_id") != PARENT_VERSION
            or native.get("status") != "COMPLETE"
            or native.get("source_state") != "MATCHES_ADMISSION"):
        raise ValueError("inherited W13 parent source did not reverify")
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    original_runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    original_handoff = original_runtime.get(PARENT_JOB)
    original_state = original_runtime.state(PARENT_JOB)
    if (original_handoff.metadata.get("checkpoint_contract") != CP_ID
            or original_handoff.metadata.get("native_evidence_verifier") != VERIFIER
            or original_state.output.get("checkpoint_verdict") != "PASS"):
        raise ValueError("native parent is not original W13 game witness")
    verify_native_report(original_handoff.inputs, original_state.output["report"])

    def witness(observation):
        if (observation.kind != "BRANCH" or observation.lane_id != "A"
                or observation.witness_ref != OBSERVATION
                or observation.capability != CAPABILITY
                or observation.relation != RELATION):
            return False
        try:
            checked = reverify_job(data_dir=data_dir, job_id=PARENT_JOB)
            return (checked == {"job_id": PARENT_JOB, "status": "COMPLETE",
                               "reverified": True, "executed": False}
                    and job_view(data_dir=data_dir, job_id=PARENT_JOB)
                    .get("source_state") == "MATCHES_ADMISSION")
        except (ValueError, KeyError):
            return False

    harness = WorkstationContinuationHarness(
        data_dir, verify_observation=witness,
        verify_connection=lambda a, b: False,
        worker_editions={CAPABILITY: "source-owned:" + PARENT_VERSION},
    )
    harness.seed_lane("A", "WORLD W13 preserved game source",
                      cp_lane="game", cp_slot="cp-game-w13-worlds")
    harness.seed_lane("B", "Other investigations remain independent")
    harness.observe(lane_id="A", kind="BRANCH",
                    relation=RELATION, witness_ref=OBSERVATION,
                    capability=CAPABILITY)
    created = harness.tick()
    born = created["born_coordination_lanes"]
    if len(born) != 1 or created["execution_started"] is not False:
        raise ValueError("W13 B2 coordination did not open one native branch")
    admitted = harness.admit_native_help(
        born[0], parent_version=PARENT_VERSION,
        inputs_file=INPUTS, allow_native_admission=True)
    native_help = admitted["native_help"]
    child = native_help.get("child") or {}
    job = child.get("job_id")
    if native_help["state"] != "ASSIGNED_NOT_VERIFIED" or not job:
        raise ValueError("no actual W13 source-owned native helper assigned")
    if child.get("worker_id") != WORKER_ID:
        raise ValueError("assigned worker is not the original W13 source family")
    feedback = WorkstationNativeFeedback(harness, run_job=run_job,
                                         verify_return=verify_return)
    returned = feedback.advance(
        born[0], confirm_execute=job, allow_local_execution=True)
    if not returned.recorded_new_event or returned.job_id != job:
        raise ValueError("bounded native helper did not return a new recorded result")
    checked = reverify_job(data_dir=data_dir, job_id=job)
    if checked.get("status") != "COMPLETE" or not checked["reverified"]:
        raise ValueError("W13 native delegated result did not independently reverify")
    state = harness._runtime().state(job)
    output = state.output
    receipt = output.get("report", {}).get("receipt", {})
    proof = verify_native_report(
        harness._runtime().get(job).inputs, output["report"])
    if (output.get("checkpoint_verdict") != "PASS"
            or output.get("checkpoint_contract") != CP_ID
            or proof.get("worlds_completed") != 2
            or not proof.get("solved") or len(receipt.get("worlds", [])) != 2):
        raise ValueError("actual delegated W13 game output failed independent replay")
    # Calling the same delegate return again must not repeat execution or rewrite evidence.
    before = (data_dir / "runtime.jsonl").read_bytes()
    repeated = feedback.advance(
        born[0], confirm_execute=job, allow_local_execution=True)
    if repeated.recorded_new_event or (data_dir / "runtime.jsonl").read_bytes() != before:
        raise ValueError("repeat handoff executed twice or modified native history")
    result = {
        "schema": "workstation-w13-delegation/v1",
        "source_parent_job": PARENT_JOB,
        "native_worker_id": WORKER_ID,
        "delegate_job_id": job,
        "coordination_handoff_id": born[0],
        "opening_id": returned.opening_id,
        "source_fingerprint": child["fingerprint"],
        "native_output_sha256": returned.output_sha256,
        "native_evidence_sha256": returned.evidence_sha256,
        "delegated_subprocess_completed": True,
        "verified_native_return_recorded": True,
        "repeat_did_not_execute": True,
        "original_AB_lanes_present": {"A", "B"}.issubset(
            {item["id"] for item in harness.inspect()["lanes"]}),
        "worlds_completed": proof["worlds_completed"],
        "native_verification": "PASS",
        "other_lane_remained_independent": True,
        "no_ai_helper_claim": True,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "delegation.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inherited-evidence", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.data_dir.resolve() == args.output_dir.resolve():
        raise ValueError("runtime and output destinations must differ")
    restore_continuation(args.inherited_evidence, args.data_dir)
    result = delegate_w13(data_dir=args.data_dir, output_dir=args.output_dir)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
