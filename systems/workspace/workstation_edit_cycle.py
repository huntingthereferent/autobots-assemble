"""One explicitly invoked, source-backed edit-and-verify pass on ProcessWorkstation.

A registered bounded *subprocess* proposes a real source edit in response to a
native verifier failure. The host applies it only to a private source edition,
independently executes the verifier, and branches a successor only on PASS.

No AI generator, unattended scheduler, GitHub push, or sandbox is implied.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Any

from .workstation import ProcessWorkstation, _safe_id

SOURCE_NAME = "factory_machine_worker.py"
WORKER = "factory-machine-validated-edits"
REGISTERED_PROPOSER = Path(__file__).with_name("factory_edit_proposer.py")
INDEPENDENT_VERIFIER = Path(__file__).with_name("factory_edit_verifier.py")
CANONICAL_SOURCE = Path(__file__).with_name(SOURCE_NAME)
MAX_BYTES = 25000


def _child(script: Path, source: Path, *, observed: dict | None = None) -> subprocess.CompletedProcess:
    if script.is_symlink() or not script.is_file():
        raise ValueError("registered native subprocess missing or unsafe")
    return subprocess.run([sys.executable, "-I", str(script), str(source)],
                          input=json.dumps(observed) if observed is not None else None,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=10, check=False)


def _run_verifier(source: Path) -> dict:
    result = _child(INDEPENDENT_VERIFIER, source)
    if len(result.stdout) > 3000 or len(result.stderr) > 3000:
        raise ValueError("verifier output exceeds bound")
    return {"returncode": result.returncode,
            "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def _bounded_proposal(source: Path, observed: dict) -> dict:
    worker = _child(REGISTERED_PROPOSER, source,
                    observed={"exit_code": observed["returncode"],
                              "stderr": observed["stderr"]})
    if worker.returncode or len(worker.stdout) > 4096:
        raise ValueError("registered worker did not propose an admissible edit")
    try:
        proposal = json.loads(worker.stdout)
    except (ValueError, TypeError) as exc:
        raise ValueError("malformed native worker proposal") from exc
    if (type(proposal) is not dict
            or set(proposal) != {"worker", "pid", "target", "before", "after",
                                 "source_sha256", "failure"}
            or proposal["worker"] != "factory-blank-product-proposer/v1"
            or type(proposal["pid"]) is not int or proposal["pid"] <= 0
            or proposal["target"] != SOURCE_NAME
            or proposal["failure"] != "BLANK_PRODUCT_ACCEPTED"
            or type(proposal["before"]) is not str
            or type(proposal["after"]) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", proposal["source_sha256"])):
        raise ValueError("invalid worker source/patch identity")
    if (proposal["before"] != "not inputs['product']"
            or proposal["after"] != "not inputs['product'].strip()"):
        raise ValueError("worker attempted an edit outside registered correction")
    raw = source.read_bytes()
    if len(raw) > MAX_BYTES or sha256(raw).hexdigest() != proposal["source_sha256"]:
        raise ValueError("source changed since worker proposal")
    if raw.decode("utf8").count(proposal["before"]) != 1:
        raise ValueError("ambiguous source edit")
    return proposal


def edit_pass(*, desk: ProcessWorkstation, worker_id: str,
              parent_version: str, candidate_version: str,
              accepted_version: str, execute: bool = False) -> dict[str, Any]:
    """Only observed native PASS creates a successor source edition.

    Child processes execute Python from an explicitly trusted local source;
    '-I' limits Python imports, but does NOT sandbox hostile code.
    """
    if not execute:
        raise PermissionError("explicit --execute required for native source check/edit")
    worker_id = _safe_id(worker_id)
    parent_version, candidate_version, accepted_version = (
        _safe_id(v) for v in (parent_version, candidate_version, accepted_version))
    if len({parent_version, candidate_version, accepted_version}) != 3:
        raise ValueError("edition IDs must be distinct")
    parent, _ = desk._read(worker_id, parent_version)
    original = parent / SOURCE_NAME
    if original.is_symlink() or not original.is_file():
        raise ValueError("exact registered worker source absent")
    if desk.inspect(worker_id=worker_id, version_id=parent_version)["modified"]:
        raise ValueError("input edition has unreviewed modifications")
    if desk._edition(worker_id, candidate_version).exists() or desk._edition(worker_id, accepted_version).exists():
        raise FileExistsError("candidate/successor already exists; never rerun blindly")
    before = _run_verifier(original)
    if before["returncode"] != 4 or "BLANK_PRODUCT_ACCEPTED" not in before["stderr"]:
        raise ValueError("required native defect not observed; do not guess an edit")
    proposal = _bounded_proposal(original, before)
    # Existing ProcessWorkstation owns the edition fork and fingerprints.
    candidate = desk.branch(worker_id=worker_id, parent_version=parent_version,
                            version_id=candidate_version)
    target = Path(candidate["path"]) / SOURCE_NAME
    raw = target.read_bytes()
    if sha256(raw).hexdigest() != proposal["source_sha256"]:
        raise ValueError("candidate source does not match checked parent")
    result = raw.decode("utf8").replace(proposal["before"], proposal["after"], 1)
    target.write_text(result, encoding="utf8")
    inspected = desk.inspect(worker_id=worker_id, version_id=candidate_version)
    if inspected["modified"] != [SOURCE_NAME] or inspected["added"] or inspected["deleted"]:
        raise ValueError("candidate modification exceeded registered target")
    after = _run_verifier(target)
    passed = after["returncode"] == 0 and after["stdout"] == "FACTORY_NATIVE_BEHAVIOR_PASS"
    successor = None
    if passed:
        # Branch only after an independent native test. This creates a new
        # source *edition*, NOT an already-running worker or code promotion.
        successor = desk.branch(worker_id=worker_id, parent_version=candidate_version,
                                version_id=accepted_version)
        if (Path(successor["path"]) / SOURCE_NAME).read_bytes() != target.read_bytes():
            raise ValueError("accepted successor changed after verified copy")
    return {
        "schema": "workstation-native-edit-cycle/v1",
        "source": str(CANONICAL_SOURCE.relative_to(Path(__file__).resolve().parents[2])),
        "worker_id": worker_id,
        "parent_version": parent_version,
        "candidate_version": candidate_version,
        "accepted_version": accepted_version if passed else None,
        "proposal_worker_pid": proposal["pid"],
        "source_sha256": proposal["source_sha256"],
        "candidate_sha256": sha256(target.read_bytes()).hexdigest(),
        "initial_observation": before,
        "independent_recheck": after,
        "outcome": "ACCEPTED_EDITION" if passed else "REJECTED_CANDIDATE",
        "candidate_edited": True,
        "successor_created": passed,
        "native_execution": True,
        "ai_model": False,
        "not_proven": "No general-purpose coding agent or autonomous scheduler; edit is confined to one registered repair.",
    }


def run_once(*, data_dir: str | Path, run_id: str,
             execute: bool = False) -> dict[str, Any]:
    if not execute:
        raise PermissionError("use --execute to allow the bounded native repair run")
    run_id = _safe_id(run_id)
    root = Path(data_dir).resolve()
    repo_root = Path(__file__).resolve().parents[2]
    if root == repo_root or repo_root.is_relative_to(root) or root.is_relative_to(repo_root):
        raise ValueError("workstation data must be outside repository source tree")
    if CANONICAL_SOURCE.is_symlink() or not CANONICAL_SOURCE.is_file():
        raise ValueError("original source unavailable")
    desk = ProcessWorkstation(root / "workstation")
    base, candidate, accepted = ("factory-" + run_id + "-" + s
                                 for s in ("base", "candidate", "accepted"))
    for v in (base, candidate, accepted):
        if desk._edition(WORKER, v).exists():
            raise FileExistsError("already attempted this exact workstation edit run")
    # Copy ORIGINAL real worker bytes into a private seed, not an invented
    # demonstration implementation. The original file is never modified.
    with TemporaryDirectory(prefix="factory-source-", dir=root if root.exists() else None) as scratch:
        source = Path(scratch)
        shutil.copyfile(CANONICAL_SOURCE, source / SOURCE_NAME)
        desk.copy_source(source, worker_id=WORKER, version_id=base,
                         source_locator=f"repository:{CANONICAL_SOURCE.relative_to(repo_root)}#sha256={sha256(CANONICAL_SOURCE.read_bytes()).hexdigest()}")
    report = edit_pass(desk=desk, worker_id=WORKER,
                       parent_version=base, candidate_version=candidate,
                       accepted_version=accepted, execute=True)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--run-id", default="first")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = run_once(data_dir=args.data_dir, run_id=args.run_id, execute=args.execute)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        # Never write into the source repository or silently publish private evidence.
        destination = args.output.resolve()
        if Path(__file__).resolve().parents[2] in destination.parents:
            raise ValueError("refusing to publish private candidate receipt into repository")
        if destination.exists():
            raise FileExistsError("do not overwrite a previous edit receipt")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(encoded)
    print(encoded, end="")
    return 0 if result["successor_created"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
