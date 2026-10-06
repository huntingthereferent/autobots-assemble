from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from network import EvidenceRef, Protocol, ProtocolResult, Relation, Witness, apply_protocol


EXTERNAL_JOB_PROTOCOL = Protocol(
    "work.external-bounded-problem",
    "Admit and continue a bounded external job without inventing hidden requirements.",
    ("specification", "acceptance", "required_inputs"),
)


@dataclass(frozen=True)
class JobState:
    job_id: str
    referent: str
    result: ProtocolResult


def load_job(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def job_to_relations(job: dict) -> tuple[Relation, ...]:
    job_id = str(job.get("id", "job:unknown"))
    source = str(job.get("source_url") or job.get("source_platform") or "job record")
    evidence = (EvidenceRef(f"{job_id}:record", source, "canonical job.json"),)

    fields = {
        "title": job.get("title"),
        "preferred_referent": job.get("preferred_referent"),
        "boundary": job.get("boundary"),
        "acceptance": job.get("acceptance"),
        "status": job.get("status"),
        "submission_status": job.get("submission_status"),
        "payment_status": job.get("payment_status"),
        "next_movement": job.get("next_movement"),
        "result": job.get("result"),
        "reward_observed": job.get("reward_observed"),
    }

    out: list[Relation] = []
    for predicate, value in fields.items():
        if value not in (None, "", []):
            out.append(Relation(job_id, predicate, value, source, evidence=evidence))

    for blocker in job.get("blockers") or ():
        out.append(Relation(job_id, "wall", blocker, source, evidence=evidence))
    for item in job.get("evidence") or ():
        out.append(Relation(job_id, "evidence_path", item, source, evidence=evidence))
    return tuple(out)


def evaluate_job(job: dict) -> JobState:
    job_id = str(job.get("id", "job:unknown"))
    referent = str(job.get("preferred_referent") or job.get("title") or job_id)
    src = str(job.get("source_url") or "job record")
    record = EvidenceRef(f"{job_id}:record", src, "canonical job record")

    blockers = tuple(job.get("blockers") or ())
    status = str(job.get("status") or "").lower()

    spec_state = "SUPPORTED" if job.get("boundary") else "UNKNOWN"
    acceptance_state = "SUPPORTED" if job.get("acceptance") else "UNKNOWN"
    if blockers:
        inputs_state = "MISSING"
    elif status in {"queued", "discovered"}:
        inputs_state = "PARTIAL"
    else:
        inputs_state = "SUPPORTED"

    witnesses = (
        Witness("specification", spec_state, (record,)),
        Witness("acceptance", acceptance_state, (record,)),
        Witness("required_inputs", inputs_state, (record,), "; ".join(blockers)),
    )

    result = apply_protocol(
        EXTERNAL_JOB_PROTOCOL,
        referent=referent,
        witnesses=witnesses,
        outputs=job_to_relations(job),
        next_referent=str(job.get("next_movement") or referent),
        note=str(job.get("result") or ""),
    )
    return JobState(job_id, referent, result)


def load_all_jobs(root: str | Path) -> tuple[dict, ...]:
    root = Path(root)
    return tuple(load_job(path) for path in sorted(root.glob("JOB-*/job.json")))
