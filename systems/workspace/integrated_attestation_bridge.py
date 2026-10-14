"""CP30 recovered integrated edition -> one bounded source-pinned verification job.

The exact selected historical Python verifier executes in a local child process.
A separate host-owned Ed25519 implementation replays its verdict before the
existing HandoffRuntime records RESULT. Never identifies external owners.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .integrated_source import WORKER_ID
from .integrated_attestation_verifier import validate_request, native_verdict
from .workstation import ProcessWorkstation

VERIFIER = "integrated-cp30-three-scope-attestation-v1"
RELATION = "verify CP30 three signed route-source scopes"
WITNESS = "three-scope CP30 signature verdict locally rechecked"
SOURCE = "host-independent cp30 ed25519 replay"
MODULE = "finite_process_attestation.py"


def _run_verified_source(edition: Path, inputs: dict) -> dict:
    """Only trusted local source; Python -I is NOT an operating-system sandbox."""
    try:
        proc = subprocess.run([sys.executable, "-I", str(edition / MODULE), "verify"],
                              cwd=edition, input=json.dumps(inputs, sort_keys=True),
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=12, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("CP30 verifier subprocess timed out") from exc
    if proc.returncode or len(proc.stdout) > 8192 or len(proc.stderr) > 8192:
        raise RuntimeError("CP30 verifier child failed; no result recorded")
    try:
        value = json.loads(proc.stdout)
    except ValueError as exc:
        raise ValueError("CP30 verifier returned invalid JSON") from exc
    if (type(value) is not dict or set(value) != {"status", "pid", "verified_scopes"} or
            type(value["status"]) is not str or type(value["pid"]) is not int or
            value["pid"] <= 0 or type(value["verified_scopes"]) is not list):
        raise ValueError("CP30 verifier subprocess output contract mismatch")
    return value


@dataclass(frozen=True)
class IntegratedCP30Worker:
    bridge: "IntegratedCP30Bridge"
    job_id: str

    @property
    def actor_id(self) -> str:
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff: Handoff) -> bool:
        return (handoff.handoff_id == self.job_id and handoff.to_actor == self.actor_id and
                handoff.required_relation == RELATION)

    def execute(self, handoff: Handoff) -> ExecutionResult:
        if not self.can_execute(handoff):
            raise ValueError("CP30 task and selected edition mismatch")
        folder = self.bridge._edition(handoff)
        result = _run_verified_source(folder, handoff.inputs)
        fingerprint = handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE", output={
                "kind": "cp30-ed25519-three-scope-verification-v1",
                "signature_verdict": result["status"],
                "verified_scopes": result["verified_scopes"],
                "edition_fingerprint": fingerprint,
                "worker_version": handoff.metadata["worker_version"],
                "child_pid": result["pid"],
            }, evidence=(EvidenceRecord(
                condition=WITNESS, kind="computation", source=SOURCE,
                ref=fingerprint, depth="local-cryptographic-replay"),))


class IntegratedCP30Bridge:
    """Admit, execute and natively reverify the CP30 signature check only."""
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime, self.workstation = runtime, workstation
        runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _edition(self, handoff: Handoff) -> Path:
        m = handoff.metadata
        if (m.get("worker_id") != WORKER_ID or m.get("native_evidence_verifier") != VERIFIER or
                m.get("source_system") != "process-workstation"):
            raise ValueError("handoff does not belong to integrated CP30 verifier")
        version = m.get("worker_version")
        folder, ancestry = self.workstation._read(WORKER_ID, version)
        if (ancestry["source_locator"] !=
                "repo:work/arc_like_maze/chatbot/research/integrated/MANIFEST.json#CP-30" or
                len(ancestry["baseline"]) != 281 or MODULE not in ancestry["baseline"]):
            raise ValueError("selected edition lacks CP30 source provenance")
        info = self.workstation.inspect(worker_id=WORKER_ID, version_id=version)
        if info["current_fingerprint"] != m.get("edition_fingerprint"):
            raise ValueError("CP30 edition source changed since admission")
        if MODULE not in self.workstation._inventory_edition(folder):
            raise ValueError("CP30 historical verifier source missing")
        return folder

    def admit(self, *, version_id: str, inputs: dict, from_actor: str,
              job_id: str | None = None, lane_id: str = "") -> Handoff:
        if not isinstance(from_actor, str) or not from_actor.strip():
            raise ValueError("CP30 requires explicit source actor")
        if not isinstance(lane_id, str) or (lane_id and not lane_id.strip()):
            raise ValueError("invalid workstation lane")
        inputs = validate_request(inputs)
        info = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)
        handoff = Handoff(
            handoff_id=job_id or ("cp30-verify-" + uuid4().hex),
            referent=f"Integrated CP30 / signed scope verification / {version_id}",
            from_actor=from_actor.strip(), to_actor=f"integrated-cp30:{version_id}",
            required_relation=RELATION, inputs=inputs,
            expected_output={"kind": "cp30-ed25519-three-scope-verification-v1",
                             "scope": "cryptographic signatures only"},
            required_witnesses=(WITNESS,), admissible_evidence={WITNESS: ("computation",)},
            boundaries=("Caller-supplied public keys are not independently enrolled owner identities.",
                        "Signature validation does not perform CP30 fresh route auditing.",
                        "COMPLETE means a replayed verification computation, including negative verdicts.",
                        "Selected Python executes locally without an OS sandbox."),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{info['current_fingerprint']}",
                        *((f"workspace-lane:{lane_id}",) if lane_id else ())),
            metadata={"title": "CP30 Ed25519 source attestation verification",
                      "source_system": "process-workstation", "worker_id": WORKER_ID,
                      "worker_version": version_id, "edition_fingerprint": info["current_fingerprint"],
                      "native_evidence_verifier": VERIFIER, "historical_stage": 30},
        )
        # Check installed historical edition BEFORE emitting a CREATED event.
        self._edition(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult) -> None:
        self._edition(handoff)
        if result.status != "COMPLETE":
            raise ValueError("CP30 task requires a complete verification computation")
        expected_evidence = EvidenceRecord(condition=WITNESS, kind="computation", source=SOURCE,
                                           ref=handoff.metadata["edition_fingerprint"],
                                           depth="local-cryptographic-replay")
        if result.evidence != (expected_evidence,):
            raise ValueError("CP30 verification evidence binding mismatch")
        out = result.output
        if (type(out) is not dict or
                set(out) != {"kind", "signature_verdict", "verified_scopes",
                             "edition_fingerprint", "worker_version", "child_pid"} or
                out["kind"] != "cp30-ed25519-three-scope-verification-v1" or
                out["edition_fingerprint"] != handoff.metadata["edition_fingerprint"] or
                out["worker_version"] != handoff.metadata["worker_version"] or
                type(out["child_pid"]) is not int or out["child_pid"] <= 0):
            raise ValueError("CP30 result shape or selected source mismatch")
        status, scopes = native_verdict(handoff.inputs)
        if (out["signature_verdict"], out["verified_scopes"]) != (status, scopes):
            raise ValueError("host-owned CP30 signature replay rejected worker verdict")

    def execute(self, job_id: str, *, allow_local_execution: bool = False):
        if not allow_local_execution:
            raise PermissionError("CP30 local source execution requires explicit approval")
        handoff = self.runtime.get(job_id)
        self._edition(handoff)
        return self.runtime.run(job_id, IntegratedCP30Worker(self, job_id))

    def reverify(self, job_id: str) -> bool:
        state = self.runtime.state(job_id)
        if state.status != "COMPLETE":
            raise ValueError("only complete CP30 checks can be reverified")
        self._verify(self.runtime.get(job_id), ExecutionResult(
            status="COMPLETE", output=state.output, evidence=state.evidence))
        return True
