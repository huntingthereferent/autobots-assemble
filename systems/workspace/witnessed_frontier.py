"""Verified multi-task frontier for already executed A/B worker editions.

Original finite A/B implementation informed by GEPA's per-example Pareto
frontiers and AFlow's bounded workflow search. No optimizing model, search
engine, grader or auto-promoter is imported.

The caller owns the metric, native result verifier, and declared task set.
Unknown evidence stays UNKNOWN; a relative score never becomes a fact.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
import re
from typing import Callable, Sequence


_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_MAX_CANDIDATES = 32
_MAX_TASKS = 32


@dataclass(frozen=True)
class Trial:
    """One native task result and its *separate* evaluated score receipt."""

    candidate: str
    worker_id: str
    edition: str
    source_sha256: str
    setup_sha256: str
    task_id: str
    native_job_id: str
    result_sha256: str
    metric_id: str
    score: float
    direction: str
    result_witness: str
    score_witness: str


def _id(value: str, what: str) -> None:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{what} must be a bounded identifier")


def _digest(value: str, what: str) -> None:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError(f"{what} must be a sha256 digest")


def _validate(t: Trial) -> None:
    if not isinstance(t, Trial):
        raise TypeError("trials must be Trial receipts")
    for attr in ("candidate", "worker_id", "edition", "task_id",
                 "native_job_id", "metric_id"):
        _id(getattr(t, attr), attr)
    for attr in ("source_sha256", "setup_sha256", "result_sha256"):
        _digest(getattr(t, attr), attr)
    if not isinstance(t.score, (int, float)) or isinstance(t.score, bool):
        raise ValueError("score must be an explicit finite numeric measurement")
    if not math.isfinite(t.score):
        raise ValueError("score is nonfinite")
    if t.direction not in ("maximize", "minimize"):
        raise ValueError("direction must be maximize or minimize")
    if not all(isinstance(x, str) and 1 <= len(x) <= 300
               and not any(ch in x for ch in "\r\n")
               for x in (t.result_witness, t.score_witness)):
        raise ValueError("two bounded evidence references are required")
    if t.result_witness == t.score_witness:
        raise ValueError("native and score witnesses must be separate")


def witnessed_frontier(
    *, trials: Sequence[Trial], required_tasks: Sequence[str],
    verify_native: Callable[[Trial], bool],
    verify_score: Callable[[Trial], bool],
) -> dict:
    """Observe a bounded Pareto frontier without trying or selecting workers.

    Compare ONLY identical named tasks and metrics under identical test setup.
    Each candidate needs one separately witnessed score per task. An incomplete
    candidate is UNKNOWN and not presumed worse. No implicit neutral score,
    fallback score, extrapolation, or self-reported winning branch.
    """
    if not callable(verify_native) or not callable(verify_score):
        raise ValueError("independent native and score verifier callbacks required")
    if not required_tasks or len(required_tasks) > _MAX_TASKS:
        raise ValueError("task set must be nonempty and bounded")
    tasks = tuple(required_tasks)
    for t in tasks:
        _id(t, "required task")
    if len(set(tasks)) != len(tasks):
        raise ValueError("duplicate required task")
    if not trials or len(trials) > _MAX_CANDIDATES * len(tasks):
        raise ValueError("trial receipts must be nonempty and bounded")

    by_candidate: dict[str, dict[str, Trial]] = {}
    jobs: set[str] = set()
    for t in trials:
        _validate(t)
        if t.task_id not in tasks:
            raise ValueError("undeclared task in trial")
        group = by_candidate.setdefault(t.candidate, {})
        if len(by_candidate) > _MAX_CANDIDATES:
            raise ValueError("too many candidates")
        if t.task_id in group or t.native_job_id in jobs:
            raise ValueError("repeated candidate/task or reused native job")
        group[t.task_id] = t
        jobs.add(t.native_job_id)

    # Even when two candidates used the same task, they are incomparable if
    # its scorer/metric, direction or test conditions changed.
    anchors: dict[str, tuple[str, str, str]] = {}
    for task in tasks:
        rows = [group[task] for group in by_candidate.values() if task in group]
        if not rows:
            raise ValueError("required task was not observed in any edition")
        anchor = (rows[0].metric_id, rows[0].direction, rows[0].setup_sha256)
        if any((r.metric_id, r.direction, r.setup_sha256) != anchor for r in rows):
            raise ValueError("test setup or scoring metric differs between candidates")
        anchors[task] = anchor

    validated: dict[str, dict[str, Trial]] = {}
    unknown: dict[str, list[str]] = {}
    # Callbacks MUST check actual source-owned native records, rather than
    # interpreting receipt labels as proof. Only a literal bool is accepted.
    for candidate, group in sorted(by_candidate.items()):
        required = tuple(sorted(set(tasks) - set(group)))
        valid: dict[str, Trial] = {}
        missing = list(required)
        fingerprints = {(t.worker_id, t.edition, t.source_sha256)
                        for t in group.values()}
        if len(fingerprints) != 1:
            raise ValueError("candidate edition/source changed between task receipts")
        for task, t in sorted(group.items()):
            native = verify_native(t)
            checked = verify_score(t) if native is True else False
            if type(native) is not bool or type(checked) is not bool:
                raise TypeError("verifier callbacks must return bool")
            if native and checked:
                valid[task] = t
            else:
                missing.append(task)
        if missing:
            unknown[candidate] = sorted(missing)
        else:
            validated[candidate] = valid

    def better(a: str, b: str) -> bool:
        strict = False
        for task in tasks:
            av, bv = validated[a][task].score, validated[b][task].score
            positive = anchors[task][1] == "maximize"
            if (av < bv if positive else av > bv):
                return False
            if av != bv:
                strict = True
        return strict

    complete = sorted(validated)
    dominated = {a: [b for b in complete if a != b and better(b, a)]
                 for a in complete}
    frontier = [a for a in complete if not dominated[a]]
    data = {
        "task_ids": list(tasks),
        "verified_frontier": frontier,
        "dominated_by": dominated,
        "unknown": unknown,
        "status": "PROVISIONAL" if unknown else "COMPLETE_FOR_DECLARED_TASKS",
        "scope": "only declared tasks, scores, current native/source witnesses",
        "auto_selected": False,
        "auto_executed": False,
        "candidate_count": len(by_candidate),
        "verified_count": len(validated),
    }
    # A reproducible report digest, NOT a cryptographic attestation of claims.
    data["report_sha256"] = sha256(json.dumps(
        {"report": data, "trials": [asdict(t) for t in sorted(
            trials, key=lambda r: (r.candidate, r.task_id))]},
        sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return data
