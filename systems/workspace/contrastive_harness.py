"""Bounded contrastive probes for source-owned workstation editions.

This is an original A/B adapter informed by the public Harness² research,
not a port of Google's executor, prompts, optimizers, or benchmark assets.
It never calls models, executes an edition, or assumes a probe's self-report
is proof. Existing native controls remain responsible for actual execution
and for any later preference/pin.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Callable

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, HandoffEvent
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation, _safe_id
from .workstation_harness import WorkstationContinuationHarness

COMPONENTS = frozenset({
    "system-prompt", "guardrails", "memory", "tool-guidance",
    "subagents", "skills", "scripts", "plugins",
})
_VERDICTS = frozenset({"IMPROVED", "REGRESSED", "EQUIVALENT", "INCOMPARABLE"})
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_EVENT = "WORKSTATION_HARNESS_CONTRAST"


@dataclass(frozen=True)
class Probe:
    """A locator for an already executed, independently checkable native job."""

    job_id: str
    worker_id: str
    version_id: str
    task_id: str
    input_sha256: str
    source_sha256: str
    result_sha256: str
    witness_ref: str
    model_id: str
    execution_mode: str
    agent_profile_sha256: str
    execution_surface: str = "ab-workstation"


@dataclass(frozen=True)
class Verdict:
    """A separate, supplied comparison witness; not an inferred score."""

    outcome: str
    witness_ref: str
    scope: str


def _nonblank(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 300:
        raise ValueError(f"{field} must be bounded, nonblank text")
    if "\n" in value or "\r" in value:
        raise ValueError(f"{field} must be one line")


def _sha(value: str, field: str) -> None:
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise ValueError(f"{field} must be a recorded sha256 digest")


def _probe(p: Probe) -> None:
    if not isinstance(p, Probe):
        raise TypeError("expected a Probe receipt")
    for field in ("job_id", "worker_id", "version_id", "task_id"):
        _safe_id(getattr(p, field))
    for field in ("input_sha256", "source_sha256", "result_sha256"):
        _sha(getattr(p, field), field)
    _nonblank(p.witness_ref, "probe witness")
    _nonblank(p.model_id, "model identity")
    _nonblank(p.execution_mode, "execution mode")
    _sha(p.agent_profile_sha256, "agent profile")
    if p.execution_surface != "ab-workstation":
        raise ValueError("foreign agent substrate is not admissible in this A/B lane")


def _fingerprint(desk: ProcessWorkstation, worker_id: str, version_id: str) -> str:
    return desk.inspect(worker_id=worker_id, version_id=version_id)["current_fingerprint"]


def contrast_and_record(
    *,
    data_dir: str | Path,
    lane_id: str,
    worker_id: str,
    base_version: str,
    candidate_version: str,
    component: str,
    base: Probe,
    candidate: Probe,
    verify_probe: Callable[[Probe], bool],
    compare_native: Callable[[Probe, Probe], Verdict],
) -> dict:
    """Compare one task on two native source editions; append one scoped observation.

    Both probes must have their own native job IDs, equal task/input identities,
    the SAME independently verified agent identity / execution mode / executor
    surface, source bytes matching the currently inspected editions, and freshly pass
    caller-supplied native verification. Supplied metadata alone does not
    authenticate the executor: the native verifier must attest the recorded
    configuration. The independent comparator is invoked
    *only after* both probes pass. UNKNOWN is not counted as an improvement.

    Existing RuntimeJournal is the sole durable record. No source is modified,
    no worker is launched, and no edition is promoted by this method.
    """
    for item in (worker_id, base_version, candidate_version, lane_id):
        _safe_id(item)
    if component not in COMPONENTS:
        raise ValueError("unsupported editable harness component")
    if base_version == candidate_version:
        raise ValueError("contrast needs two distinct editions")
    if not callable(verify_probe) or not callable(compare_native):
        raise ValueError("native probe verifier and separate comparator required")
    _probe(base)
    _probe(candidate)
    if (base.worker_id != worker_id or candidate.worker_id != worker_id
            or base.version_id != base_version
            or candidate.version_id != candidate_version):
        raise ValueError("probe source-edition identity mismatch")
    if base.job_id == candidate.job_id:
        raise ValueError("cannot compare one job with itself")
    # The proposed harness edit is the variable being investigated. The
    # surrounding model, agent identity, executor surface and mode must not
    # silently change between probe runs. Keep Codex/build-mode switches out.
    if (base.model_id != candidate.model_id
            or base.execution_mode != candidate.execution_mode
            or base.agent_profile_sha256 != candidate.agent_profile_sha256
            or base.execution_surface != candidate.execution_surface):
        raise ValueError("agent/execution configuration changed between probes")
    if any("codex" in value.casefold() for value in (
            base.model_id, base.execution_mode, candidate.model_id,
            candidate.execution_mode)):
        raise ValueError("Codex mode is not part of this A/B workstation lane")
    if base.task_id != candidate.task_id or base.input_sha256 != candidate.input_sha256:
        raise ValueError("different tasks or inputs cannot support a paired contrast")

    root = Path(data_dir)
    desk = ProcessWorkstation(root / "workstation")
    _, candidate_manifest = desk._read(worker_id, candidate_version)
    _, base_manifest = desk._read(worker_id, base_version)
    if (candidate_manifest["parent_version"] != base_version
            or candidate_manifest["source_locator"] != base_manifest["source_locator"]):
        raise ValueError("candidate must be a branch of this source-owned base")
    before_fp = _fingerprint(desk, worker_id, base_version)
    after_fp = _fingerprint(desk, worker_id, candidate_version)
    if base.source_sha256 != before_fp or candidate.source_sha256 != after_fp:
        raise ValueError("probe is stale: source changed since its recorded execution")
    if before_fp == after_fp:
        raise ValueError("no changed harness source to contrast")

    native_base = verify_probe(base)
    native_candidate = verify_probe(candidate)
    if type(native_base) is not bool or type(native_candidate) is not bool:
        raise TypeError("native verifier must return an explicit bool")
    if native_base and native_candidate:
        verdict = compare_native(base, candidate)
        if not isinstance(verdict, Verdict) or verdict.outcome not in _VERDICTS:
            raise ValueError("separate comparator must return a supported Verdict")
        _nonblank(verdict.witness_ref, "comparison witness")
        _nonblank(verdict.scope, "comparison scope")
        if verdict.witness_ref in (base.witness_ref, candidate.witness_ref):
            raise ValueError("contrast witness must be separate from probe witnesses")
        outcome = verdict.outcome
        comparison = asdict(verdict)
        status = "SUPPORTED" if outcome == "IMPROVED" else "NO_PREFERENCE"
    else:
        outcome = "UNVERIFIED"
        comparison = None
        status = "UNKNOWN"

    # Refuse a race between verification and journal admission.
    if (before_fp != _fingerprint(desk, worker_id, base_version)
            or after_fp != _fingerprint(desk, worker_id, candidate_version)):
        raise ValueError("edition source moved during native verification")

    seed = {
        "worker_id": worker_id, "base_version": base_version,
        "candidate_version": candidate_version, "component": component,
        "base": asdict(base), "candidate": asdict(candidate),
        "outcome": outcome, "comparison": comparison, "status": status,
        "scope": "one-matched-task", "execution_started": False,
        "selection_performed": False,
    }
    digest = sha256(json.dumps(seed, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = {"contrast_id": "whcontrast-" + digest[:24], **seed}

    runtime = HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl"))
    handoff = WorkstationContinuationHarness._resolve_lane(runtime, lane_id)
    old = [e for e in runtime.event_store.for_handoff(handoff.handoff_id)
           if e.event_type == _EVENT and e.data.get("contrast_id") == result["contrast_id"]]
    if old:
        if len(old) != 1 or old[0].data != result:
            raise ValueError("conflicting or duplicated contrast journal identity")
        return {**result, "already_recorded": True}
    prior = runtime.state(handoff.handoff_id).last_event_id
    runtime.event_store.append(HandoffEvent.create(
        handoff_id=handoff.handoff_id, event_type=_EVENT,
        actor_id="workstation-harness-comparison",
        data=result,
        evidence=(
            EvidenceRecord(condition="baseline native probe", kind="source",
                           source="harness-contrast-intake", ref=base.witness_ref,
                           depth="reported"),
            EvidenceRecord(condition="candidate native probe", kind="source",
                           source="harness-contrast-intake", ref=candidate.witness_ref,
                           depth="reported"),
        ) + ((
            EvidenceRecord(condition="separate comparative witness", kind="source",
                           source="harness-contrast-intake",
                           ref=comparison["witness_ref"], depth="reported"),
        ) if comparison else ()),
        parents=(prior,) if prior else (),
    ))
    return {**result, "already_recorded": False}


def pin_supported_candidate(*, approved: bool, actor_id: str, **contrast_args) -> dict:
    """Freshly recheck the contrast, then use EXISTING native promotion controls.

    Supported comparisons are only candidates. This gate cannot pin a generic
    unregistered model worker, a READY job, or a fabricated native witness.
    """
    if approved is not True:
        raise PermissionError("operator must explicitly approve this exact pin")
    _safe_id(actor_id)
    report = contrast_and_record(**contrast_args)
    if report["status"] != "SUPPORTED":
        raise ValueError("only freshly supported contrasts can request a pin")
    from .controls import promote_edition

    pin = promote_edition(
        data_dir=contrast_args["data_dir"],
        worker_id=contrast_args["worker_id"],
        version_id=contrast_args["candidate_version"],
        supporting_job_id=contrast_args["candidate"].job_id,
        confirm_version=contrast_args["candidate_version"],
        confirm_fingerprint=contrast_args["candidate"].source_sha256,
        actor_id=actor_id,
    )
    return {"contrast_id": report["contrast_id"], "pin": pin}
