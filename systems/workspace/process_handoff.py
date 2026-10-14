"""Explicit Finite Correspondence Process edition -> existing HandoffRuntime.

One bounded finite required-edge prefilter is executed in a real local child
process. The runtime's native verifier independently recomputes its verdicts.
No new scheduler, simulated physical claims, or A/B ontology is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .finite_runner import run_edition
from .finite_verifier import validate_inputs, verdicts
from .workstation import ProcessWorkstation

RELATION = "finite required-edge prefilter"
VERIFIER = "finite-correspondence-prefilter-v1"
WITNESS = "finite prefilter independently reproduced"
SOURCE = "local finite correspondence process edition"
WORKER_ID = "finite-correspondence-process"
_FILES = ("finite_goal_priority.py", "finite_required_edge_guard.py")


def _source_fingerprint(files: dict[str, str]) -> str:
    return sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class CorrespondenceWorker:
    """One edition-specific local worker adapter for an admitted handoff."""
    bridge: "CorrespondenceWorkBridge"
    handoff_id: str

    @property
    def actor_id(self) -> str:
        return self.bridge.runtime.get(self.handoff_id).to_actor

    def can_execute(self, handoff: Handoff) -> bool:
        return handoff.handoff_id == self.handoff_id and handoff.to_actor == self.actor_id and handoff.required_relation == RELATION

    def execute(self, handoff: Handoff) -> ExecutionResult:
        if not self.can_execute(handoff):
            raise ValueError("wrong worker or task")
        edition = self.bridge._pinned_edition(handoff)
        data = run_edition(edition, handoff.inputs)
        return ExecutionResult(status="COMPLETE", output={
            "kind": "finite-prefilter-v1", "verdicts": data["verdicts"],
            "edition_fingerprint": handoff.metadata["edition_fingerprint"],
            "worker_version": handoff.metadata["worker_version"],
            "child_pid": data["child_pid"],
        }, evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
            source=SOURCE,ref=handoff.metadata["edition_fingerprint"],depth="local-replay"),))


class CorrespondenceWorkBridge:
    """Submit explicitly selected finite jobs, then execute and reverify them."""
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime, self.workstation = runtime, workstation
        runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _pinned_edition(self, handoff: Handoff) -> Path:
        m = handoff.metadata
        if m.get("native_evidence_verifier") != VERIFIER or m.get("worker_id") != WORKER_ID:
            raise ValueError("not a finite correspondence handoff")
        version = m.get("worker_version")
        info = self.workstation.inspect(worker_id=WORKER_ID, version_id=version)
        if info["current_fingerprint"] != m.get("edition_fingerprint"):
            raise ValueError("edition source changed since admission")
        edition = Path(info["path"])
        for file in _FILES:
            if file not in self.workstation._inventory_edition(edition):
                raise ValueError(f"edition missing required source: {file}")
        return edition

    def admit(self, *, version_id: str, inputs: dict, from_actor: str,
              lane_id: str = "", job_id: str | None = None) -> Handoff:
        """An explicit call admits one job. Merely copying a version never does."""
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("from_actor required")
        if not isinstance(lane_id,str) or (lane_id and not lane_id.strip()):
            raise ValueError("invalid lane")
        canonical = validate_inputs(inputs)
        info = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)
        edition = Path(info["path"])
        entries = self.workstation._inventory_edition(edition)
        if any(f not in entries for f in _FILES):
            raise ValueError("selected edition lacks required finite modules")
        fingerprint = _source_fingerprint(entries)
        handoff = Handoff(
            handoff_id=job_id or ("fcp-job-" + uuid4().hex),
            referent=f"Finite Correspondence Process / required-edge prefilter / {version_id}",
            from_actor=from_actor.strip(),to_actor=f"correspondence-worker:{version_id}",
            required_relation=RELATION, inputs=canonical,
            expected_output={"kind":"finite-prefilter-v1", "verdicts":"one per candidate"},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",f"source-fingerprint:{fingerprint}",
                        *((f"workspace-lane:{lane_id}",) if lane_id else ())),
            boundaries=("NOT_CONTRADICTED is not a proven admitted edge.",
                        "UNDECIDED is not a successful correspondence.",
                        "Local computation is not independently authenticated ownership.",
                        "Worker subprocess is not an OS security sandbox."),
            metadata={"title":"Finite required-edge prefilter", "source_system":"process-workstation",
                      "native_evidence_verifier":VERIFIER,"worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fingerprint},
        )
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult) -> None:
        """Independent source-free finite replay, before the RESULT is journaled."""
        self._pinned_edition(handoff)
        if result.status != "COMPLETE":
            raise ValueError("finite worker only admits successful, reverified computation")
        if len(result.evidence) != 1 or result.evidence[0] != EvidenceRecord(
              condition=WITNESS,kind="computation",source=SOURCE,
              ref=handoff.metadata["edition_fingerprint"],depth="local-replay"):
            raise ValueError("worker evidence does not match pinned edition")
        obj = result.output
        if not isinstance(obj,dict) or set(obj) != {"kind","verdicts","edition_fingerprint","worker_version","child_pid"}:
            raise ValueError("unexpected finite worker result")
        if obj["kind"] != "finite-prefilter-v1" or obj["edition_fingerprint"] != handoff.metadata["edition_fingerprint"] or obj["worker_version"] != handoff.metadata["worker_version"] or type(obj["child_pid"]) is not int or obj["child_pid"] <= 0:
            raise ValueError("worker output source binding invalid")
        if obj["verdicts"] != verdicts(handoff.inputs):
            raise ValueError("native finite verifier rejected worker result")

    def execute(self, job_id: str, *, allow_local_execution: bool = False):
        """A positive execution flag is required; no automatic worker activation."""
        if not allow_local_execution:
            raise PermissionError("local edition execution requires explicit approval")
        handoff = self.runtime.get(job_id)
        self._pinned_edition(handoff)
        return self.runtime.run(job_id, CorrespondenceWorker(self, job_id))

    def reverify(self, job_id: str) -> bool:
        """Re-check a journal-restored COMPLETE without executing the worker."""
        state = self.runtime.state(job_id)
        if state.status != "COMPLETE":
            raise ValueError("only completed jobs have results to reverify")
        self._verify(self.runtime.get(job_id), ExecutionResult(
            status="COMPLETE", output=state.output, evidence=state.evidence))
        return True

    def inspect(self, job_id: str) -> dict:
        handoff = self.runtime.get(job_id)
        state = self.runtime.state(job_id)
        return {"job_id":job_id,"version":handoff.metadata.get("worker_version"),
                "source_fingerprint":handoff.metadata.get("edition_fingerprint"),
                "status":state.status,"verdicts":state.output.get("verdicts", []),
                "missing_witnesses":list(state.missing_witnesses),
                "lane_refs":[p for p in handoff.provenance if p.startswith("workspace-lane:")]}
