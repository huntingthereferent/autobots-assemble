"""Verify one exact research MOVE source declaration against a native workstation result.

Read-only and explicitly local. A Git-committed research source MUST name the
native job, RESULT event, verifier and pinned edition fingerprint. A true join
requires independent fresh native re-verification. This checks source identity,
NOT whether the scientific interpretation or research causal claim is correct.
"""
from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess

from .native_receipt_projection import reverify_local

SCHEMA = "native-research-source-join/v1"
DECLARATION_SCHEMA = "research-native-receipt-relation/v1"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
PART = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
MAX_SOURCE_BYTES = 64_000
EXPECTED = frozenset((
    "schema", "job_id", "result_event_id", "worker_id", "worker_version",
    "native_verifier_id", "source_fingerprint",
))


def _research_path(path: str) -> str:
    """Restrict to structured source-record paths the public index understands."""
    if not isinstance(path, str) or len(path) > 280:
        raise ValueError("exact structured research path required")
    parts = path.split("/")
    if (len(parts) == 3 and parts[:2] == ["state", "pins"]
            and parts[2].endswith(".json")
            and PART.fullmatch(parts[2]) and parts[2] not in (".", "..")):
        return path
    if (len(parts) == 4 and parts[:2] == ["research", "dives"]
            and PART.fullmatch(parts[2]) and parts[2] not in (".", "..")
            and parts[3] == "dive.json"):
        return path
    raise ValueError("path is not a structured MOVE research record")


def _committed_record(repo_root: str | Path, commit: str,
                      rel: str) -> tuple[dict, str]:
    if not isinstance(commit, str) or HEX40.fullmatch(commit) is None:
        raise ValueError("exact forty-character Git commit required")
    rel = _research_path(rel)
    repo = Path(repo_root).resolve()
    path = repo / rel
    if not repo.is_dir() or not (repo / ".git").exists():
        raise ValueError("local source checkout with Git history required")
    if (not path.is_file() or path.is_symlink()
            or any(p.is_symlink() for p in path.parents if p != repo and repo in p.parents)
            or path.stat().st_size > MAX_SOURCE_BYTES):
        raise ValueError("research source missing, unsafe or too large")
    raw = path.read_bytes()
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{rel}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("pinned Git source unavailable") from exc
    if completed.returncode != 0 or len(completed.stdout) > MAX_SOURCE_BYTES:
        raise ValueError("source absent from exact Git revision")
    if raw != completed.stdout:
        raise ValueError("working source differs from pinned Git revision")
    try:
        record = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("invalid exact research source JSON") from exc
    if (type(record) is not dict or record.get("schema_version") != 1
            or record.get("result_state") not in ("MOVE", "MOVE_WITH_WALL")):
        raise ValueError("not a structured original MOVE record")
    return record, sha256(raw).hexdigest()


def verify_local_relation(*, data_dir: str | Path, job_id: str,
                          repo_root: str | Path, research_commit: str,
                          research_path: str) -> dict:
    """Check a dual source identity; no journal writes, worker execution or publish.

    If a source has no native declaration, the relationship remains OPEN without
    running the verifier. An explicit false declaration is a hard failure.
    """
    path = _research_path(research_path)
    record, source_digest = _committed_record(repo_root, research_commit, path)
    base = {
        "schema": SCHEMA,
        "movement_id": "structured:" + path,
        "research_commit": research_commit,
        "research_source_sha256": source_digest,
        "native_job_id": job_id,
        "publicly_published": False,
        "research_causality": "NOT_ESTABLISHED",
        "independent_research_owner_attestation": False,
    }
    decl = record.get("native_workstation_receipt")
    if decl is None:
        return {**base, "relation": "OPEN_NO_EXACT_SOURCE_DECLARATION",
                "native_verified": False, "result_event_id": None}
    if (type(decl) is not dict or set(decl) != EXPECTED
            or decl.get("schema") != DECLARATION_SCHEMA
            or decl.get("job_id") != job_id):
        raise ValueError("declared relation has wrong schema or native job")
    if (not isinstance(decl.get("source_fingerprint"), str)
            or HEX64.fullmatch(decl["source_fingerprint"]) is None):
        raise ValueError("invalid declared native edition SHA-256")
    for k in ("result_event_id", "worker_id", "worker_version", "native_verifier_id"):
        if not isinstance(decl.get(k), str) or not 1 <= len(decl[k]) <= 128:
            raise ValueError("invalid declared exact field: " + k)

    native = reverify_local(data_dir, job_id)
    if (native.get("verification") != "FRESH_NATIVE_REVERIFICATION_LOCAL"
            or native.get("recorded_status") != "COMPLETE"
            or native.get("job_id") != decl["job_id"]
            or native.get("worker_id") != decl["worker_id"]
            or native.get("worker_version") != decl["worker_version"]
            or native.get("native_verifier_id") != decl["native_verifier_id"]
            or native.get("source_fingerprint") != decl["source_fingerprint"]):
        raise ValueError("native source identity differs from committed relation")
    events = native["events"]
    if (not events or not any(
            e.get("event_id") == decl["result_event_id"]
            and e.get("type") == "RESULT"
            and e.get("result_status") == "COMPLETE"
            for e in events)):
        raise ValueError("committed research record does not name exact native RESULT")
    # Detect a concurrent source edit/revision switch while verifying a job.
    _, fresh_digest = _committed_record(repo_root, research_commit, path)
    if fresh_digest != source_digest:
        raise ValueError("research source changed during native re-verification")
    return {
        **base,
        "relation": "EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH",
        "native_verified": True,
        "result_event_id": decl["result_event_id"],
        "native_source_fingerprint": native["source_fingerprint"],
        "verification_scope": "local native computation and explicit Git source identity only",
    }


def main(argv=None) -> int:
    parser = ArgumentParser(description="Read-only exact native/research source relation")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--research-commit", required=True)
    parser.add_argument("--research-path", required=True)
    args = parser.parse_args(argv)
    result = verify_local_relation(
        data_dir=args.data_dir, job_id=args.job_id,
        repo_root=args.repo_root, research_commit=args.research_commit,
        research_path=args.research_path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
