"""Read-only bridge from *actual* native worker jobs into witnessed frontiers.

No new executor, score predictor or promotion mechanism is introduced. This
is an original A/B adapter informed by the strict source/effect separation in
microduck's safety authority, Dolt's merge conflict checks and Gitleaks'
baseline matching. None of their source code is copied.

Current supported scoring scope: finite required-edge prefilter **decision
coverage**, NOT mathematical correctness or task-level performance.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Sequence

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .controls import job_view, reverify_job
from .finite_verifier import validate_inputs, verdicts
from .process_handoff import WORKER_ID, VERIFIER
from .witnessed_frontier import Trial, witnessed_frontier, _id
from .workstation import ProcessWorkstation

_METRIC = "finite-decided-verdict-count-v1"
_MAX_CASES = 1024


@dataclass(frozen=True)
class NativeCase:
    candidate: str
    task_id: str
    job_id: str


def _digest(value) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()).hexdigest()


def _candidate_receipt(*, runtime: HandoffRuntime, desk: ProcessWorkstation,
                       root: Path, case: NativeCase) -> Trial:
    for x, field in ((case.candidate, "candidate"), (case.task_id, "task"),
                     (case.job_id, "native job")):
        _id(x, field)
    h = runtime.get(case.job_id)
    meta = h.metadata
    if (meta.get("source_system") != "process-workstation"
            or meta.get("worker_id") != WORKER_ID
            or meta.get("native_evidence_verifier") != VERIFIER):
        raise ValueError("only installed finite native workers are measurable")
    edition = meta.get("worker_version")
    pinned = meta.get("edition_fingerprint")
    _id(edition, "worker edition")
    view = job_view(data_dir=root, job_id=case.job_id)
    if (view["status"] != "COMPLETE"
            or view["source_state"] != "MATCHES_ADMISSION"
            or view["worker_id"] != WORKER_ID
            or view["version_id"] != edition
            or view["edition_fingerprint"] != pinned):
        raise ValueError("native job must be COMPLETE on its original source")
    source = desk.inspect(worker_id=WORKER_ID, version_id=edition)
    if source["current_fingerprint"] != pinned:
        raise ValueError("native source changed since execution")
    canonical = validate_inputs(h.inputs)
    output = view["result"]
    if (not isinstance(output, dict)
            or output.get("kind") != "finite-prefilter-v1"
            or output.get("worker_version") != edition
            or output.get("edition_fingerprint") != pinned
            or not isinstance(output.get("verdicts"), list)):
        raise ValueError("native result lacks exact domain/source shape")
    # Never construct an invented native score from metadata alone. Every
    # candidate's fixed metric is the number of actual decided verdicts;
    # independent validation occurs AGAIN in each callback below.
    score = sum(v in ("CONTRADICTED", "NOT_CONTRADICTED")
                for v in output["verdicts"])
    expected = verdicts(canonical)
    oracle_hash = _digest(expected)
    return Trial(
        candidate=case.candidate, worker_id=WORKER_ID,
        edition=edition, source_sha256=pinned,
        setup_sha256=_digest({"domain": VERIFIER, "inputs": canonical,
                              "metric": _METRIC}),
        task_id=case.task_id, native_job_id=case.job_id,
        result_sha256=_digest(output), metric_id=_METRIC,
        score=score, direction="maximize",
        result_witness="journal:" + case.job_id,
        score_witness="finite-oracle:" + case.job_id + ":" + oracle_hash,
    )


def native_decision_frontier(
    *, data_dir: str | Path, cases: Sequence[NativeCase],
    required_tasks: Sequence[str],
) -> dict:
    """Reverify already completed native jobs, then compare decision coverage.

    The only supported metric is a factual count of decided verdicts, *not*
    an advantage in science, truth, economics, agent ability or physics.
    Unknown/unrecorded outcomes cannot be converted to zero scores.

    No writes to the workstation or runtime and no agent / process launches.
    """
    if not cases or len(cases) > _MAX_CASES:
        raise ValueError("native case selection must be nonempty and bounded")
    root = Path(data_dir)
    runtime = HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl"))
    desk = ProcessWorkstation(root / "workstation")
    claims: dict[str, NativeCase] = {}
    trials = []
    for case in cases:
        if not isinstance(case, NativeCase):
            raise TypeError("expected exact NativeCase declarations")
        if case.job_id in claims:
            raise ValueError("native job cannot be counted more than once")
        claims[case.job_id] = case
        trials.append(_candidate_receipt(
            runtime=runtime, desk=desk, root=root, case=case))

    def _real_job(t: Trial) -> bool:
        case = claims[t.native_job_id]
        fresh = _candidate_receipt(
            runtime=runtime, desk=desk, root=root, case=case)
        if fresh != t:
            return False
        # Native, source-owned verifier must actually replay the retained
        # RESULT. This cannot launch another worker or accept a READY job.
        checked = reverify_job(data_dir=root, job_id=t.native_job_id)
        return (checked == {"job_id": t.native_job_id, "status": "COMPLETE",
                             "reverified": True, "executed": False}
                and _candidate_receipt(runtime=runtime, desk=desk,
                                       root=root, case=case) == t)

    def _score(t: Trial) -> bool:
        case = claims[t.native_job_id]
        h = runtime.get(case.job_id)
        expected = verdicts(validate_inputs(h.inputs))
        state = runtime.state(case.job_id)
        return (
            state.status == "COMPLETE"
            and state.output.get("verdicts") == expected
            and t.score == sum(x != "UNDECIDED" for x in expected)
            and t.score_witness == ("finite-oracle:" + case.job_id + ":"
                                    + _digest(expected))
            and t.setup_sha256 == _digest({
                "domain": VERIFIER, "inputs": validate_inputs(h.inputs),
                "metric": _METRIC})
        )

    result = witnessed_frontier(
        trials=trials, required_tasks=required_tasks,
        verify_native=_real_job, verify_score=_score)
    result["observed_native_jobs"] = [
        {"candidate": t.candidate, "task_id": t.task_id,
         "job_id": t.native_job_id, "edition": t.edition,
         "source_sha256": t.source_sha256,
         "result_sha256": t.result_sha256,
         "score": t.score, "metric_id": _METRIC}
        for t in sorted(trials, key=lambda x: (x.candidate, x.task_id))
    ]
    result["metric_meaning"] = (
        "number of finite prefilter verdicts that are not UNDECIDED; "
        "NOT_CONTRADICTED does not establish a true edge or general success")
    result["only_native_reverification"] = True
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Observe native finite worker edition outcomes without execution")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--manifest", required=True,
                        help="JSON object: required_tasks array, cases array")
    args = parser.parse_args(argv)
    p = Path(args.manifest)
    if not p.is_file() or p.stat().st_size > 131072:
        raise ValueError("bounded existing manifest required")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if (not isinstance(raw, dict) or set(raw) != {"required_tasks", "cases"}
            or not isinstance(raw["cases"], list)):
        raise ValueError("manifest must contain only required_tasks and cases")
    cases = []
    for c in raw["cases"]:
        if not isinstance(c, dict) or set(c) != {"candidate", "task_id", "job_id"}:
            raise ValueError("one exact candidate/task/job locator required per case")
        cases.append(NativeCase(**c))
    print(json.dumps(native_decision_frontier(
        data_dir=args.data_dir, cases=cases,
        required_tasks=raw["required_tasks"]), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
