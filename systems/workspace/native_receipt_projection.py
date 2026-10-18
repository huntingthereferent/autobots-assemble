"""Read-only exact native journal receipts for an explicitly selected local job.

No GitHub publication, agent execution, job admission or inferred research links.
Recorded journal events are NOT native proof. Native-reverified status is only
returned after invoking the existing source-specific read-only verifier.
"""
from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import re

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal

SCHEMA = "workstation-native-receipt-local/v1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_JOURNAL_BYTES = 32 * 1024 * 1024
MAX_EVENTS_PER_JOB = 2048


def _open_runtime(data_dir: str | Path) -> tuple[Path, HandoffRuntime]:
    root = Path(data_dir).resolve()
    journal = root / "runtime.jsonl"
    if not journal.is_file() or journal.is_symlink():
        raise ValueError("explicit private runtime journal missing or unsafe")
    if journal.stat().st_size > MAX_JOURNAL_BYTES:
        raise ValueError("native receipt journal exceeds inspection bound")
    return journal, HandoffRuntime(event_store=RuntimeJournal(journal))


def recorded_receipt(runtime: HandoffRuntime, job_id: str) -> dict:
    """Inspect one exact source-owned handoff and its *local* parent event edges.

    Does not return inputs, outputs, raw evidence, actors, user-defined titles,
    arbitrary metadata, paths, timestamps, or external source contents.
    """
    if not isinstance(job_id, str) or not 1 <= len(job_id) <= 128:
        raise ValueError("exact bounded job id required")
    h = runtime.get(job_id)
    md = h.metadata
    if md.get("source_system") != "process-workstation":
        raise ValueError("not an exact process-workstation source")
    worker = md.get("worker_id")
    edition = md.get("worker_version")
    fingerprint = md.get("edition_fingerprint")
    verifier = md.get("native_evidence_verifier")
    if any(not isinstance(v, str) or not 1 <= len(v) <= 128
           for v in (worker, edition, verifier)):
        raise ValueError("incomplete native source identity")
    if not isinstance(fingerprint, str) or SHA256.fullmatch(fingerprint) is None:
        raise ValueError("missing exact source fingerprint")
    events = runtime.event_store.for_handoff(job_id)
    if not events or len(events) > MAX_EVENTS_PER_JOB or events[0].event_type != "CREATED":
        raise ValueError("missing or excessive native event chain")
    seen = set()
    compact = []
    result_status = None
    for n, event in enumerate(events):
        eid = event.event_id
        if not isinstance(eid, str) or not 1 <= len(eid) <= 128 or eid in seen:
            raise ValueError("duplicate or invalid native event id")
        if event.handoff_id != job_id:
            raise ValueError("native event owned by a different job")
        parents = tuple(event.parents)
        if n == 0 and parents:
            raise ValueError("creation event cannot cite an earlier native parent")
        if len(parents) != len(set(parents)) or any(p not in seen for p in parents):
            raise ValueError("unresolved or forward native event parent")
        if event.event_type == "RESULT":
            result_status = event.data.get("status")
            if result_status not in ("COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"):
                raise ValueError("invalid native result status")
        if n > 0 and event.event_type == "CREATED":
            raise ValueError("duplicate native creation")
        compact.append({
            "event_id": eid,
            "type": event.event_type,
            "parents": list(parents),
            "result_status": result_status if event.event_type == "RESULT" else None,
        })
        seen.add(eid)
    state = runtime.state(job_id)
    if state.last_event_id != compact[-1]["event_id"]:
        raise ValueError("native state and event chain disagree")
    if state.status == "COMPLETE" and result_status != "COMPLETE":
        raise ValueError("complete state without exact native result")
    return {
        "schema": SCHEMA,
        "scope": "local-private-journal-only",
        "job_id": job_id,
        "worker_id": worker,
        "worker_version": edition,
        "source_fingerprint": fingerprint,
        "native_verifier_id": verifier,
        "recorded_status": state.status,
        "verification": "RECORDED_NOT_REVERIFIED",
        "events": compact,
        "publicly_published": False,
        "causal_research_link": None,
    }


def inspect_local(data_dir: str | Path, job_id: str) -> dict:
    """Read one exact private job without touching execution or a publication."""
    _, runtime = _open_runtime(data_dir)
    return recorded_receipt(runtime, job_id)


def reverify_local(data_dir: str | Path, job_id: str) -> dict:
    """Freshly recheck original native source; detect journal changes and fail closed.

    The existing controls.reverify_job dispatches to the original worker's
    independently implemented native verifier. This function never executes
    jobs or creates/publishes a new receipt.
    """
    journal, runtime = _open_runtime(data_dir)
    before = recorded_receipt(runtime, job_id)
    if before["recorded_status"] != "COMPLETE":
        raise ValueError("noncomplete native job cannot be promoted")
    digest_before = sha256(journal.read_bytes()).digest()
    from .controls import reverify_job
    result = reverify_job(data_dir=Path(data_dir).resolve(), job_id=job_id)
    if (result.get("job_id") != job_id or result.get("status") != "COMPLETE"
            or result.get("reverified") is not True or result.get("executed") is not False):
        raise ValueError("native verifier did not return exact read-only pass")
    if sha256(journal.read_bytes()).digest() != digest_before:
        raise ValueError("runtime journal changed during native re-verification")
    _, fresh = _open_runtime(data_dir)
    after = recorded_receipt(fresh, job_id)
    if before != after:
        raise ValueError("native receipt changed during verification")
    after["verification"] = "FRESH_NATIVE_REVERIFICATION_LOCAL"
    return after


def main(argv=None) -> int:
    parser = ArgumentParser(description="Read one exact local workstation receipt (never publish)")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--reverify", action="store_true",
                        help="invoke original source-native read-only re-verifier")
    args = parser.parse_args(argv)
    fn = reverify_local if args.reverify else inspect_local
    print(json.dumps(fn(args.data_dir, args.job_id), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
