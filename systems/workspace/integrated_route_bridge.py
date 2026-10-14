"""Source-pinned, fixture-only CP30 fresh route/task audit worker.

This executes recovered CP30 owner/pin *synthetic fixtures*, and compares the
reported outcome to a second execution of hash-checked canonical archive bytes.
It does not authenticate external owners, source enrollment or production use.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .integrated_source import WORKER_ID, MANIFEST_REL, verify_archive_source
from .integrated_route_runner import run_route_fixture
from .integrated_route_verifier import validate_route_request, verify_report_shape
from .workstation import ProcessWorkstation, _safe_id

VERIFIER = "integrated-cp30-synthetic-route-audit-v1"
RELATION = "fresh CP30 synthetic selected-route audit and exact task check"
WITNESS = "CP30 fixture route report matched fresh canonical source replay"
SOURCE = "host canonical historical CP30 fixture replay"
REQUIRED = ("ab_chatbot_independent_process_identity.py", "ab_chatbot_certificate_handoff.py",
            "test_ab_chatbot_route_bound_task.py", "test_ab_chatbot_multi_task_dependency.py",
            "finite_process_attestation.py")


def canonical_report(inputs: dict, *, repo_root: Path | None = None) -> dict:
    """Reconstruct trusted ORIGINAL bytes in a separate temporary tree and replay.

    This is intentionally a SAME-ALGORITHM reference test rather than an
    independent proof of the underlying mathematical claim.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    checked = verify_archive_source(root, 30)
    with TemporaryDirectory(prefix="cp30-canonical-replay-") as temp:
        folder = Path(temp)
        for name, (payload, _) in checked["files"].items():
            (folder / name).write_bytes(payload)
        result = run_route_fixture(folder, inputs)
    return result["payload"]


@dataclass(frozen=True)
class IntegratedRouteWorker:
    bridge: "IntegratedRouteBridge"
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff: Handoff) -> bool:
        return (handoff.handoff_id == self.job_id and handoff.to_actor == self.actor_id
                and handoff.required_relation == RELATION)

    def execute(self, handoff: Handoff) -> ExecutionResult:
        if not self.can_execute(handoff):
            raise ValueError("worker does not own CP30 route job")
        selected = self.bridge._edition(handoff)
        outcome = run_route_fixture(selected, handoff.inputs)
        fp = handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE",
            output={"kind":"cp30-synthetic-route-audit-v1", "report":outcome["payload"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"child_pid":outcome["child_pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",source=SOURCE,
                     ref=fp,depth="synthetic-canonical-replay"),))


class IntegratedRouteBridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _edition(self, handoff: Handoff) -> Path:
        md=handoff.metadata
        if (md.get("worker_id") != WORKER_ID or md.get("native_evidence_verifier") != VERIFIER
                or md.get("source_system") != "process-workstation"
                or md.get("historical_stage") != 30):
            raise ValueError("not an integrated CP30 fixture route handoff")
        version=md.get("worker_version")
        folder,manifest=self.workstation._read(WORKER_ID,version)
        if (manifest["source_locator"] != f"repo:{MANIFEST_REL.as_posix()}#CP-30"
                or len(manifest["baseline"]) != 281
                or not set(REQUIRED).issubset(manifest["baseline"])):
            raise ValueError("missing original integrated CP30 edition provenance")
        info=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)
        if info["current_fingerprint"] != md.get("edition_fingerprint"):
            raise ValueError("CP30 route edition source changed since job admission")
        if not set(REQUIRED).issubset(self.workstation._inventory_edition(folder)):
            raise ValueError("CP30 fixture owner route modules missing")
        return folder

    def admit(self, *, version_id: str, inputs: dict, from_actor: str,
              job_id: str | None = None, lane_id: str = "") -> Handoff:
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("explicit submitting actor required")
        if not isinstance(lane_id,str) or (lane_id and not lane_id.strip()):
            raise ValueError("invalid lane")
        if job_id is not None:_safe_id(job_id)
        canonical=validate_route_request(inputs)
        info=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)
        handoff=Handoff(
            handoff_id=job_id or "cp30-route-"+uuid4().hex,
            referent=f"Integrated CP30 / synthetic route audit / {version_id}",
            from_actor=from_actor.strip(), to_actor=f"integrated-cp30-route:{version_id}",
            required_relation=RELATION, inputs=canonical,
            expected_output={"kind":"cp30-synthetic-route-audit-v1", "task_statuses":"one per task"},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            provenance=(f"worker-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{info['current_fingerprint']}",
                        *((f"workspace-lane:{lane_id}",) if lane_id else ())),
            boundaries=("Owner and pin fixtures are synthetic, not live owner authentication.",
                        "Every receiver performs a fresh two-pass selected-route audit.",
                        "A task with an unproved required edge is not completed.",
                        "A COMPLETE handoff records the computation, not proof for all tasks.",
                        "Canonical replay uses the same historical algorithms; not independent math proof.",
                        "Running local source in Python -I does not create an OS sandbox."),
            metadata={"title":"CP30 synthetic route audit and exact tasks",
                      "source_system":"process-workstation", "worker_id":WORKER_ID,
                      "worker_version":version_id, "edition_fingerprint":info["current_fingerprint"],
                      "native_evidence_verifier":VERIFIER,"historical_stage":30},
        )
        self._edition(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult) -> None:
        self._edition(handoff)
        if result.status != "COMPLETE":
            raise ValueError("CP30 fixture needs a completed recorded computation")
        fp=handoff.metadata["edition_fingerprint"]
        expected=(EvidenceRecord(condition=WITNESS,kind="computation",source=SOURCE,
                  ref=fp,depth="synthetic-canonical-replay"),)
        if result.evidence != expected:
            raise ValueError("CP30 fixture evidence mismatches pinned source")
        out=result.output
        if (type(out) is not dict or set(out) != {"kind","report","worker_version",
                          "edition_fingerprint","child_pid"} or
                out["kind"]!="cp30-synthetic-route-audit-v1" or
                out["edition_fingerprint"]!=fp or
                out["worker_version"]!=handoff.metadata["worker_version"] or
                type(out["child_pid"]) is not int or out["child_pid"]<=0):
            raise ValueError("CP30 fixture result shape/source invalid")
        verify_report_shape(out["report"],handoff.inputs)
        if out["report"] != canonical_report(handoff.inputs):
            raise ValueError("CP30 fixture verdict does not match canonical historical replay")

    def execute(self,job_id:str,*,allow_local_execution:bool=False):
        if not allow_local_execution:
            raise PermissionError("explicit CP30 fixture execution approval required")
        handoff=self.runtime.get(job_id)
        self._edition(handoff)
        return self.runtime.run(job_id,IntegratedRouteWorker(self,job_id))

    def reverify(self,job_id:str)->bool:
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("only completed CP30 fixture computations can reverify")
        self._verify(self.runtime.get(job_id),ExecutionResult(status="COMPLETE",
                          output=state.output,evidence=state.evidence))
        return True
