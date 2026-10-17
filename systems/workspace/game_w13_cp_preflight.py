"""COORDINATOR W13: read-only source-pinned browser evidence preflight.

This is deliberately *not* a Process Workstation admission, native worker,
source-owner signature, or CP WITNESSED status. It consumes two distinct
real browser-run artifact directories after CI verifies their GitHub identities
and checks every receipt with the separately authored W13 WITNESS oracle.
A positive observation cannot grant permission to execute a source edition.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
from typing import Any

from network.witness_w13_independent import (
    W12_SOURCE_SHA256, independent_w13_replay, strict_json,
)
from systems.workspace.cp_motion import checkpoint_frontier

CP = "GAME-W13-WORLDS"

# Immutable Git blob source identities from the exact merged WORLD / BUILD /
# WITNESS commits. These are source pins, NOT owner-signed authorizations.
SOURCE_BLOBS = {
    "systems/workspace/game_construction.py": "5fd78ef193d32f6b8369b17c402ae6f06e377d39",
    "systems/workspace/WORLD_W13_MOVEMENT_01.md": "9449c62eb9928662752fe89fadaedd9dc9ea7623",
    "docs/game_w13_preview.html": "eeb5e383fa093ff941c9880fb88acd62485ce3f2",
    "systems/workspace/game_w13_engine.py": "f8bee610b59553ffbb37cbf175371c86e4deb64b",
    "systems/workspace/game_w13_receipt.py": "39b9454e3fcf49c30469487fa0d9fc572d37cf85",
    "network/witness_w13_independent.py": "ed04a0feccb179b29dcadf9074993b6e14d694ca",
    "systems/workspace/WITNESS_W13_INDEPENDENT_VERDICT.md": "1fcf82e31d4d2a8569e0646f7c21050898855d0a",
    "network/tests/fixtures/world_w13_movement_01.json": "715a49ba7313ca94093a59a5082e59e5fbbbdf5f",
}
ARTIFACTS = {
    "build": {
        "run": 38999614131, "head": "49a82fc09428ef413561edf3b9c1f612bab0232c",
        "id": 12088487637, "name": "w13-build-chromium-evidence",
        "digest": "sha256:bf94bd3420000fa1767f026ec03a8adf7a4e5c93647624d30032bd165a5242dc",
    },
    "witness": {
        "run": 39001126918, "head": "1b067e05e37f5629556defca5b406da6ecd3cbfb",
        "id": 12088694155, "name": "w13-independent-witness-chromium-evidence",
        "digest": "sha256:7b98c96ef0d8d9be5b63233bf65aec44d59278f4a667d5ad2818ba9e12a625b0",
    },
}
BUILD_NEGATIVES = ("boundary", "final", "first-room", "second-room")
WITNESS_NEGATIVES = ("global", "world-before", "world-after",
                     "world-final", "crossing", "session-final")
SUCCESS_ACTIONS = ["right", "interact", "advance", "right", "interact"]


def _git_blob_digest(source: bytes) -> str:
    return sha1(b"blob " + str(len(source)).encode("ascii") + b"\0" + source).hexdigest()


def verify_source_identity(repo_root: Path) -> dict[str, dict[str, str]]:
    """Fail closed on any source, WORLD contract, BUILD or WITNESS drift."""
    report = {}
    for relative, expected in SOURCE_BLOBS.items():
        file = repo_root / relative
        if not file.is_file() or file.is_symlink():
            raise ValueError(f"source file missing/unsafe: {relative}")
        raw = file.read_bytes()
        if _git_blob_digest(raw) != expected:
            raise ValueError(f"source changed from pinned WORLD/BUILD/WITNESS edition: {relative}")
        report[relative] = {
            "git_blob": expected,
            "sha256": sha256(raw).hexdigest(),
        }
    if report["systems/workspace/game_construction.py"]["sha256"] != W12_SOURCE_SHA256:
        raise ValueError("original W12 source hash does not match WITNESS authority")
    return report


def _read_data(directory: Path, filename: str) -> tuple[dict, str]:
    if directory.is_symlink():
        raise ValueError("artifact directory must not be a symlink")
    path = directory / filename
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or unsafe recorded browser artifact: {filename}")
    raw = path.read_bytes()
    if len(raw) > 250_000:
        raise ValueError(f"unexpectedly large browser receipt: {filename}")
    value = strict_json(raw.decode("utf8"))
    if type(value) is not dict:
        raise ValueError(f"browser receipt is not an object: {filename}")
    return value, sha256(raw).hexdigest()


def _positive(directory: Path, name: str) -> tuple[dict, dict, str]:
    receipt, digest = _read_data(directory, name)
    proof = independent_w13_replay(receipt)
    if not proof["solved"] or proof["worlds_completed"] != 2 or proof["boundaries_checked"] != 1:
        raise ValueError(f"browser observation is not a witnessed completed two-world session: {name}")
    if receipt["actions"] != SUCCESS_ACTIONS:
        raise ValueError(f"browser action path differs from WORLD W13 Movement 01: {name}")
    return receipt, proof, digest


def assess_game_evidence(
    repo_root: str | Path, build_dir: str | Path, witness_dir: str | Path,
) -> dict[str, Any]:
    """Read only. Never write/admit/execute a job or promote a checkpoint."""
    root, build, witness = Path(repo_root), Path(build_dir), Path(witness_dir)
    source_report = verify_source_identity(root)
    if build.resolve() == witness.resolve():
        raise ValueError("BUILD and WITNESS evidence must come from separate archive directories")
    build_receipt, build_proof, build_sha = _positive(build, "w13_browser_positive.json")
    witness_receipt, witness_proof, witness_sha = _positive(witness, "witness_real_browser_success.json")

    # Distinct actual Chromium receipts must agree on the whole WORLD relation
    # and W12 native head hashes. Merely agreeing on 'solved=true' is insufficient.
    if build_receipt != witness_receipt or build_proof["per_world"] != witness_proof["per_world"]:
        raise ValueError("BUILD and independent WITNESS browser histories disagree")

    bad_checks = {}
    for source, directory, labels, prefix in (
        ("build", build, BUILD_NEGATIVES, "w13_rejected_"),
        ("witness", witness, WITNESS_NEGATIVES, "witness_reject_"),
    ):
        for label in labels:
            name = prefix + label + ".json"
            damaged, sha = _read_data(directory, name)
            try:
                independent_w13_replay(damaged)
            except ValueError:
                bad_checks[source + ":" + label] = sha
            else:
                raise ValueError(f"independent oracle ACCEPTED a false browser claim: {name}")

    # This check is the *real* CP graph. A browser witness, however strong,
    # is not an admitted and freshly reverified native workstation job.
    frontier = checkpoint_frontier({"jobs": []})
    row = next(x for x in frontier["checkpoints"] if x["checkpoint"] == CP)
    if row["state"] != "ADMISSIBLE" or CP in frontier["witnessed"]:
        raise ValueError("unexpected native checkpoint movement without admitted job")

    return {
        "schema": "coordinator-w13-evidence-preflight-v1",
        "cp": CP,
        "verdict": "SOURCE_BOUND_BROWSER_EVIDENCE_ACCEPTED_FOR_OPERATOR_REVIEW",
        "cp_state": row["state"],
        "cp_witnessed": False,
        "execution_triggered": False,
        "job_admitted": False,
        "checkpoint_promoted": False,
        "source_pins": source_report,
        "github_artifact_identity_expected": ARTIFACTS,
        "github_artifact_metadata_verified": "required separately by GitHub Actions read-only API step",
        "browser_positive_sha256": {"build": build_sha, "witness": witness_sha},
        "independent_w12_replay": {
            "per_world": build_proof["per_world"],
            "boundaries_checked": build_proof["boundaries_checked"],
            "solved": build_proof["solved"],
        },
        "mutated_browser_receipts_rejected": bad_checks,
        "next_requirement": (
            "Explicit source-pinned native GAME-W13-WORLDS workstation admission, "
            "completed exact job, cp-checker verifier PASS, independent fresh "
            "native re-verification, and exact coordinator slot binding"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--build-evidence", type=Path, required=True)
    parser.add_argument("--witness-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = assess_game_evidence(args.repo_root, args.build_evidence, args.witness_evidence)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
