"""Source-owned NIH Phase 1 packet BUILD via EXISTING HandoffRuntime and workstation.

Consumes exact reverified scope -> ontology -> reasoning ancestry. The separate
bounded child process writes the proposal; host independently checks its cases,
provenance and scientific scope. NOT an official NIH submission.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .workstation import ProcessWorkstation
from .nih_reasoning_bridge import NIHReasoningBridge, WORKER_ID as REASON_ID
from .nih_reasoning_native import CP_ID as REASON_CP, VERIFIER as REASON_VERIFIER
from .nih_packet_native import CP_ID, WORKER_ROLE, VERIFIER, validate_packet_request, verify_packet

WORKER_ID = "nih-phase1-packet"
SOURCE_FILE = "packet_worker.py"
SOURCE_DIRECTORY = Path(__file__).resolve().parent / "nih_packet_worker_source"
LOCATOR = "repo:systems/workspace/nih_packet_worker_source/packet_worker.py"
RELATION = "build local Phase 1 research packet from source-owned temporal reasoning"
WITNESS = "host independently reconciled packet with native scope ontology and reasoning"
SOURCE = "native-local-temporal-design-packet"

def copy_packet_source(data_dir, *, version_id, allow_copy=False):
    if not allow_copy:
        raise PermissionError("explicit source-copy required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY, worker_id=WORKER_ID, version_id=version_id,
        source_locator=LOCATOR)

def run_source(folder: Path, inputs: dict):
    try:
        child = subprocess.run(
            [sys.executable, "-I", str(folder/SOURCE_FILE)],
            input=json.dumps(inputs, sort_keys=True), text=True, cwd=folder,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=12)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("packet BUILD subprocess exceeded its bounds") from exc
    if child.returncode != 0 or len(child.stdout) > 21000 or len(child.stderr) > 4096:
        raise ValueError("packet BUILD source failed")
    try:
        result = json.loads(child.stdout)
    except ValueError as exc:
        raise ValueError("packet BUILD returned invalid JSON") from exc
    if (type(result) is not dict or set(result) != {"packet","pid"}
            or type(result["pid"]) is not int or result["pid"] <= 0):
        raise ValueError("packet BUILD returned invalid process evidence")
    return result

@dataclass(frozen=True)
class PacketWorker:
    bridge: "NIHPacketBridge"
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff):
        return handoff.handoff_id == self.job_id and handoff.to_actor == self.actor_id and handoff.required_relation == RELATION

    def execute(self, handoff):
        if not self.can_execute(handoff):
            raise ValueError("packet BUILD handoff not addressed to this source")
        source = self.bridge._pinned(handoff)
        observed = run_source(source, handoff.inputs)
        fp = handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE",
            output={
                "kind":"nih-synthetic-packet-artifact/v1",
                "checkpoint_contract":CP_ID,"checkpoint_verdict":"PASS",
                "checkpoint_worker_role":WORKER_ROLE,"native_verifier":VERIFIER,
                "reasoning_job_id":handoff.inputs["request"]["reasoning_job_id"],
                "packet":observed["packet"],
                "worker_version":handoff.metadata["worker_version"],
                "edition_fingerprint":fp, "child_pid":observed["pid"],
            },
            evidence=(EvidenceRecord(
                condition=WITNESS,kind="computation",source=SOURCE,
                ref=fp,depth="fresh-host-temporal-summary-reconstruction"),),
        )

class NIHPacketBridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation,
                 reasoning_bridge: NIHReasoningBridge | None = None):
        self.runtime,self.workstation=runtime,workstation
        self.reasoning_bridge = reasoning_bridge or NIHReasoningBridge(
            runtime=runtime, workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parent(self, req: dict):
        reasoning = self.runtime.get(req["reasoning_job_id"])
        meta = reasoning.metadata
        if (meta.get("worker_id") != REASON_ID or
                meta.get("checkpoint_contract") != REASON_CP or
                meta.get("native_evidence_verifier") != REASON_VERIFIER or
                self.runtime.state(reasoning.handoff_id).status != "COMPLETE"):
            raise ValueError("packet requires exact completed Phase 1 reasoning parent")
        self.reasoning_bridge.reverify(reasoning.handoff_id)
        return reasoning

    def _inputs(self, request):
        req = validate_packet_request(request)
        reason = self._parent(req)
        ontology = self.runtime.get(reason.dependencies[0])
        parent_report = self.runtime.state(ontology.handoff_id).output["report"]
        turtle = parent_report["turtle"]
        return {
            "request":req,
            "scope":reason.inputs["scope"],
            "reasoning_report":self.runtime.state(reason.handoff_id).output["report"],
            "ontology_sha256":sha256(turtle.encode("utf8")).hexdigest(),
            "ontology_triples":parent_report["triple_count"],
        }

    def _pinned(self, handoff):
        meta = handoff.metadata
        if (meta.get("source_system") != "process-workstation"
                or meta.get("worker_id") != WORKER_ID
                or meta.get("checkpoint_contract") != CP_ID
                or meta.get("native_evidence_verifier") != VERIFIER):
            raise ValueError("not a source-owned Phase 1 packet job")
        folder,record = self.workstation._read(WORKER_ID, meta["worker_version"])
        actual = self.workstation.inspect(worker_id=WORKER_ID,version_id=meta["worker_version"])
        if (record.get("source_locator") != LOCATOR
                or actual["current_fingerprint"] != meta["edition_fingerprint"]
                or set(self.workstation._inventory_edition(folder)) != {SOURCE_FILE}):
            raise ValueError("packet BUILD source edition changed or provenance missing")
        expected = self._inputs(handoff.inputs["request"])
        if handoff.inputs != expected or handoff.dependencies != (
            handoff.inputs["request"]["reasoning_job_id"],):
            raise ValueError("packet lost exact source-owned reasoning ancestry")
        if handoff.expected_output != {
            "kind":"nih-synthetic-packet-artifact/v1","official_submission":False}:
            raise ValueError("packet expected output scope altered")
        return folder

    def admit(self, *, version_id, inputs, from_actor, job_id, lane_id="nih"):
        if type(from_actor) is not str or not from_actor.strip():
            raise ValueError("explicit packet BUILD actor required")
        data = self._inputs(inputs)
        fingerprint = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)["current_fingerprint"]
        handoff = Handoff(
            handoff_id=job_id,
            referent="NIH Phase 1 / source-owned local research design packet",
            from_actor=from_actor, to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION, inputs=data,
            expected_output={"kind":"nih-synthetic-packet-artifact/v1","official_submission":False},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            dependencies=(data["request"]["reasoning_job_id"],),
            boundaries=(
                "Synthetic examples only; never patient data or clinical claims.",
                "Local design artifact is not competition submission or official eligibility.",
                "Build must preserve independent ontology and temporal source evidence.",
                "The bounded copied Python subprocess is not OS-sandboxed.",
            ),
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{fingerprint}",
                        f"reasoning-job:{data['request']['reasoning_job_id']}",
                        f"workspace-lane:{lane_id}"),
            metadata={
                "title":"NIH Phase 1 local synthetic temporal design packet",
                "source_system":"process-workstation","worker_id":WORKER_ID,
                "worker_version":version_id, "edition_fingerprint":fingerprint,
                "checkpoint_contract":CP_ID,"native_evidence_verifier":VERIFIER,
            },
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff, result):
        self._pinned(handoff)
        fp = handoff.metadata["edition_fingerprint"]
        expected_evidence = (EvidenceRecord(
            condition=WITNESS,kind="computation",source=SOURCE,ref=fp,
            depth="fresh-host-temporal-summary-reconstruction"),)
        if result.status != "COMPLETE" or result.evidence != expected_evidence:
            raise ValueError("packet result missing native independent witness")
        output = result.output
        keys = {"kind","checkpoint_contract","checkpoint_verdict",
                "checkpoint_worker_role","native_verifier","reasoning_job_id",
                "packet","worker_version","edition_fingerprint","child_pid"}
        if (type(output) is not dict or set(output) != keys
                or output["kind"] != "nih-synthetic-packet-artifact/v1"
                or (output["checkpoint_contract"],output["checkpoint_verdict"],
                    output["checkpoint_worker_role"],output["native_verifier"]) != (
                    CP_ID,"PASS",WORKER_ROLE,VERIFIER)
                or output["reasoning_job_id"] != handoff.inputs["request"]["reasoning_job_id"]
                or output["worker_version"] != handoff.metadata["worker_version"]
                or output["edition_fingerprint"] != fp
                or type(output["child_pid"]) is not int or output["child_pid"] <= 0):
            raise ValueError("packet source result contract mismatch")
        inputs = handoff.inputs
        verify_packet(output["packet"], request=inputs["request"],
                      scope=inputs["scope"],
                      reasoning_request=self.runtime.get(
                          inputs["request"]["reasoning_job_id"]).inputs["request"],
                      ontology_sha256=inputs["ontology_sha256"],
                      ontology_triples=inputs["ontology_triples"])

    def execute(self, job_id, *, allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("explicit native packet execution required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,PacketWorker(self,job_id))

    def reverify(self, job_id):
        state = self.runtime.state(job_id)
        if state.status != "COMPLETE":
            raise ValueError("packet BUILD has not returned")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True
