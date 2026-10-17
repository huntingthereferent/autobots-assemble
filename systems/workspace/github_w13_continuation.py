"""Replay a GitHub W13 native journal on a later runner and open its next CP.

Consumes the ORIGINAL worker edition and journal from an authenticated GitHub
artifact. Uses the existing source-native verifier and coordinator; no second
worker runtime, regenerated W13 proof, or implicit job execution.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

from .branch_help import open_help
from .coordinator_window import CoordinatorIndex, freshly_reverify_linked_jobs
from .cp_motion import one_cp_handoff, workstation_cp_view
from .controls import reverify_job

RUN_ID = 39025574748
ARTIFACT_ID = 12098716155
ORIGINAL_HEAD = "1c28c44f655c3794fd64eb0b2ab822bebc9db2b2"
ORIGINAL_DIGEST = "sha256:543c08f9f9f5cb1eee47b0ab21535e759495c6e7318dc5e06f3519f27f4dfcfa"
JOB_ID = "game-w13-github-001"
CHECKPOINT = "GAME-W13-WORLDS"
NEXT = "GAME-NATIVE-VERIFIER"
SOURCE = "systems/workspace/game_w13_worker_source/game_worlds_worker.py"
FIXTURE = "network/tests/fixtures/game_w13_native_cp_example.json"
AUTHORIZATION = "systems/workspace/native_job_requests/w13/game-w13-github-001.json"
MAX_ARCHIVE = 2_000_000
MAX_UNPACKED = 4_000_000


def _object(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 150_000:
        raise ValueError(f"missing or unsafe evidence file: {path.name}")
    parsed = json.loads(path.read_text(encoding="utf8"))
    if type(parsed) is not dict:
        raise ValueError(f"wrong evidence shape: {path.name}")
    return parsed


def _git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def validate_archive_metadata(artifact: Path, origin: dict, *, repo_root: Path) -> dict:
    """Reject a green badge or arbitrary artifact without its concrete source."""
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", str(origin.get("repository", ""))):
        raise ValueError("missing source repository identity")
    if (origin.get("workflow") != "workstation-w13-owner-merged-one-shot"
            or origin.get("event") != "push" or origin.get("branch") != "main"
            or origin.get("actor") != origin["repository"].split("/")[0]
            or origin.get("conclusion") != "success"
            or origin.get("artifact_expired") is not False
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", str(origin.get("digest", "")))
            or type(origin.get("run_id")) is not int or type(origin.get("artifact_id")) is not int
            or type(origin.get("attempt")) is not int or origin["attempt"] < 1):
        raise ValueError("GitHub source run and artifact ownership are unproved")
    if origin["run_id"] == RUN_ID and (origin["artifact_id"] != ARTIFACT_ID
            or origin.get("head_sha") != ORIGINAL_HEAD
            or origin["digest"] != ORIGINAL_DIGEST):
        raise ValueError("original witnessed W13 archive differs from recorded identity")
    if not re.fullmatch(r"[0-9a-f]{40}", str(origin.get("head_sha", ""))):
        raise ValueError("invalid original source commit")
    provenance = _object(artifact / "provenance.json")
    request = _object(artifact / "authorization.json")
    expected_request = _object(repo_root / AUTHORIZATION)
    if request != expected_request:
        raise ValueError("W13 authorization was replaced")
    if (str(provenance.get("run_id")) != str(origin["run_id"])
            or str(provenance.get("run_attempt")) != str(origin["attempt"])
            or provenance.get("repository") != origin["repository"]
            or provenance.get("head_sha") != origin["head_sha"]
            or provenance.get("event") != "push"
            or provenance.get("owner_actor") != origin["actor"]
            or provenance.get("job_id") != JOB_ID
            or provenance.get("worker_git_blob") != request["worker_git_blob"]
            or provenance.get("fixture_git_blob") != request["fixture_git_blob"]
            or _git_blob(repo_root / SOURCE) != request["worker_git_blob"]
            or _git_blob(repo_root / FIXTURE) != request["fixture_git_blob"]):
        raise ValueError("journal source identity or provenance drifted")
    output = _object(artifact / "execution.json")
    verified = _object(artifact / "native-reverify.json")
    verdict = _object(artifact / "verdict.json")
    if (output.get("job_id") != JOB_ID or output.get("status") != "COMPLETE"
            or verified.get("job_id") != JOB_ID
            or verified.get("status") != "COMPLETE"
            or verified.get("reverified") is not True or verified.get("executed") is not False
            or verdict.get("native_job_id") != JOB_ID
            or verdict.get("cp") != CHECKPOINT
            or verdict.get("cp_state") != "WITNESSED"
            or verdict.get("next") != NEXT):
        raise ValueError("previous native job evidence is missing or contradictory")
    return {"source": provenance, "authorization": request, "source_run": origin}


def unpack_native_runtime(artifact: Path, destination: Path) -> str:
    """Only original journal/source edition paths, regular files and bounded sizes."""
    archive = artifact / "native-runtime.tar.gz"
    checksum = artifact / "native-runtime.sha256"
    if (archive.is_symlink() or not archive.is_file()
            or archive.stat().st_size > MAX_ARCHIVE or checksum.is_symlink()
            or not checksum.is_file() or checksum.stat().st_size > 256):
        raise ValueError("missing or oversized native journal archive")
    actual = sha256(archive.read_bytes()).hexdigest()
    recorded = checksum.read_text(encoding="ascii").split()[0]
    if not re.fullmatch("[0-9a-f]{64}", recorded) or actual != recorded:
        raise ValueError("native archive SHA-256 mismatch")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("refusing to overlay an existing workstation")
    destination.mkdir(parents=True, exist_ok=True)
    total = 0
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) > 100:
            raise ValueError("native runtime archive member count exceeds bound")
        for member in members:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or
                    not path.parts or path.parts[0] not in
                    {"workstation", "runtime.jsonl", "coordinator-windows.jsonl"} or
                    (path.parts[0] != "workstation" and len(path.parts) != 1) or
                    not (member.isdir() or member.isfile()) or
                    member.size < 0):
                raise ValueError("unsafe archived workstation entry")
            total += member.size
            if total > MAX_UNPACKED:
                raise ValueError("native journal extraction budget exceeded")
        tar.extractall(path=destination, members=members, filter="data")
    for name in ("runtime.jsonl", "coordinator-windows.jsonl"):
        if not (destination / name).is_file():
            raise ValueError("archived native journals incomplete")
    return actual


def continue_from_artifact(*, artifact_dir: Path, data_dir: Path, output_dir: Path,
                           origin: dict, repo_root: Path) -> dict:
    """One inherited native journal -> fresh replay -> one durable help opening."""
    archive_binding = validate_archive_metadata(artifact_dir, origin, repo_root=repo_root)
    archived_hash = unpack_native_runtime(artifact_dir, data_dir)
    index = CoordinatorIndex(data_dir / "coordinator-windows.jsonl")
    native = workstation_cp_view(data_dir)
    checked = freshly_reverify_linked_jobs(
        index, "complete-stack", native,
        lambda job_id: reverify_job(data_dir=data_dir, job_id=job_id))
    packet = one_cp_handoff(index, "complete-stack", checked, reverified=True)
    cp = packet["cp_automation"]
    states = {r["checkpoint"]: r["state"] for r in cp["checkpoints"]}
    if (states.get(CHECKPOINT) != "WITNESSED"
            or states.get(NEXT) != "ADMISSIBLE"
            or CHECKPOINT not in cp["witnessed"] or NEXT not in cp["frontier"]):
        raise ValueError("cross-run original journal failed fresh native replay")
    opening = open_help(
        data_dir=data_dir, lane="game", slot="cp-game-native-verifier",
        capability="game-native-archive-consumer",
        opening_key=f"w13-{origin['run_id']}-{origin['attempt']}",
        reason="Consume the verified W13 native journal in the next source-owned checkpoint",
    )
    if opening["state"] != "OPEN_UNSTAFFED":
        raise ValueError("a native verifier worker was claimed without admission")
    # Reopen inherited append-only journals: branch opening survives process exit.
    from .branch_help import help_summary
    seen = [r for r in help_summary(data_dir) if r["opening_id"] == opening["opening_id"]]
    if len(seen) != 1:
        raise ValueError("new branch opening was not durably replayed")
    result = {
        "schema": "github-w13-cross-run-continuation/v1",
        "source_run_id": origin["run_id"],
        "source_artifact_id": origin["artifact_id"],
        "source_artifact_digest": origin["digest"],
        "source_head_sha": origin["head_sha"],
        "inherited_archive_sha256": archived_hash,
        "parent_job_id": JOB_ID,
        "parent_cp": CHECKPOINT, "parent_state": "WITNESSED",
        "next_cp": NEXT, "next_state": "ADMISSIBLE",
        "branch_opening_id": opening["opening_id"],
        "branch_state": opening["state"],
        "child_job_admitted": False, "child_job_executed": False,
        "fresh_replay": True,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "continuation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-binding", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.data_dir.resolve() == args.output_dir.resolve():
        raise ValueError("runtime and output paths must be distinct")
    root = Path(__file__).resolve().parents[2]
    result = continue_from_artifact(
        artifact_dir=args.artifact_dir, data_dir=args.data_dir,
        output_dir=args.output_dir, origin=_object(args.source_binding),
        repo_root=root)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
