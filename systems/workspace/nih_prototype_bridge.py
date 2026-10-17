"""Exact source-owned Phase 2 temporal prototype BUILD in original workstation."""
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
from .nih_packet_bridge import NIHPacketBridge, WORKER_ID as PACKET_ID
from .nih_packet_native import CP_ID as PACKET_CP, VERIFIER as PACKET_VERIFIER
from .nih_reasoning_bridge import NIHReasoningBridge, WORKER_ID as REASON_ID
from .nih_reasoning_native import CP_ID as REASON_CP, VERIFIER as REASON_VERIFIER
from .nih_prototype_native import CP_ID,WORKER_ROLE,VERIFIER,validate_proto_request,verify_prototype

WORKER_ID="nih-temporal-prototype"
SOURCE_FILE="prototype_worker.py"
SOURCE_DIRECTORY=Path(__file__).resolve().parent/"nih_prototype_worker_source"
LOCATOR="repo:systems/workspace/nih_prototype_worker_source/prototype_worker.py"
RELATION="construct runnable as-known-at versus static snapshot prototype from original NIH parents"
WITNESS="host independently executed generated program on hidden temporal queries"
SOURCE="native-independent-executable-temporal-prototype"

def copy_proto_source(data_dir, *,version_id,allow_copy=False):
    if not allow_copy:
        raise PermissionError("explicit original source copy required")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)

def run_source(folder,inputs):
    try:
        child=subprocess.run([sys.executable,"-I",str(folder/SOURCE_FILE)],
                             input=json.dumps(inputs,sort_keys=True),text=True,
                             capture_output=True,cwd=folder,check=False,timeout=10)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("native prototype BUILD timed out") from e
    if child.returncode or len(child.stdout)>30000 or len(child.stderr)>4096:
        raise ValueError("native prototype builder failed")
    try:
        result=json.loads(child.stdout)
    except ValueError as e:
        raise ValueError("native prototype builder output invalid") from e
    if (type(result) is not dict or set(result)!={"pid","artifact"}
            or type(result["pid"]) is not int or result["pid"]<=0):
        raise ValueError("native prototype builder did not attest subprocess")
    return result

@dataclass(frozen=True)
class PrototypeWorker:
    bridge: "NIHPrototypeBridge"
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self,handoff):
        return (handoff.handoff_id==self.job_id
                and handoff.to_actor==self.actor_id
                and handoff.required_relation==RELATION)

    def execute(self,handoff):
        if not self.can_execute(handoff):
            raise ValueError("wrong BUILD handoff")
        source=self.bridge._pinned(handoff)
        result=run_source(source,handoff.inputs)
        fp=handoff.metadata["edition_fingerprint"]
        return ExecutionResult(
            status="COMPLETE",
            output={"kind":"nih-local-temporal-prototype-result/v1",
                    "checkpoint_contract":CP_ID,"checkpoint_verdict":"PASS",
                    "checkpoint_worker_role":WORKER_ROLE,"native_verifier":VERIFIER,
                    "prototype":result["artifact"],
                    "worker_version":handoff.metadata["worker_version"],
                    "edition_fingerprint":fp,"child_pid":result["pid"]},
            evidence=(EvidenceRecord(condition=WITNESS,kind="computation",
                     source=SOURCE,ref=fp,depth="host-ran-hidden-temporal-queries"),),
        )

class NIHPrototypeBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        self.packet_bridge=NIHPacketBridge(runtime=runtime,workstation=workstation)
        self.reason_bridge=NIHReasoningBridge(runtime=runtime,workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parents(self,request):
        req=validate_proto_request(request)
        reason=self.runtime.get(req["reasoning_job_id"])
        packet=self.runtime.get(req["packet_job_id"])
        rm,pm=reason.metadata,packet.metadata
        if (rm.get("worker_id")!=REASON_ID or rm.get("checkpoint_contract")!=REASON_CP
                or rm.get("native_evidence_verifier")!=REASON_VERIFIER
                or pm.get("worker_id")!=PACKET_ID or pm.get("checkpoint_contract")!=PACKET_CP
                or pm.get("native_evidence_verifier")!=PACKET_VERIFIER
                or packet.dependencies!=(reason.handoff_id,)
                or self.runtime.state(reason.handoff_id).status!="COMPLETE"
                or self.runtime.state(packet.handoff_id).status!="COMPLETE"):
            raise ValueError("exact completed Phase 1 packet and reasoning ancestors required")
        self.packet_bridge.reverify(packet.handoff_id)
        self.reason_bridge.reverify(reason.handoff_id)
        return reason,packet

    def _inputs(self,request):
        req=validate_proto_request(request)
        reason,packet=self._parents(req)
        packet_data=self.runtime.state(packet.handoff_id).output["packet"]["summary"]
        return {"request":req,"scope":reason.inputs["scope"],
                "reasoning_request":reason.inputs["request"],
                "reasoning_report":self.runtime.state(reason.handoff_id).output["report"],
                "packet_summary":packet_data,
                "ontology_sha256":packet_data["ontology_sha256"]}

    def _pinned(self,handoff):
        md=handoff.metadata
        if (md.get("source_system")!="process-workstation"
                or md.get("worker_id")!=WORKER_ID
                or md.get("checkpoint_contract")!=CP_ID
                or md.get("native_evidence_verifier")!=VERIFIER):
            raise ValueError("not original source-owned temporal prototype")
        folder,record=self.workstation._read(WORKER_ID,md["worker_version"])
        current=self.workstation.inspect(worker_id=WORKER_ID,version_id=md["worker_version"])
        if (record.get("source_locator")!=LOCATOR or
                current["current_fingerprint"]!=md["edition_fingerprint"]
                or set(self.workstation._inventory_edition(folder))!={SOURCE_FILE}):
            raise ValueError("prototype source edition mutated or untracked")
        expected=self._inputs(handoff.inputs["request"])
        if (handoff.inputs!=expected or
                handoff.dependencies!=(expected["request"]["reasoning_job_id"],
                                       expected["request"]["packet_job_id"])
                or handoff.expected_output!={"kind":"nih-local-temporal-prototype-result/v1",
                                             "official_submission":False}):
            raise ValueError("prototype original parent relationship changed")
        return folder

    def admit(self,*,version_id,inputs,from_actor,job_id,lane_id="nih"):
        if type(from_actor) is not str or not from_actor.strip():
            raise ValueError("explicit temporal BUILD coordinator required")
        payload=self._inputs(inputs)
        fp=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)["current_fingerprint"]
        req=payload["request"]
        handoff=Handoff(
            handoff_id=job_id,
            referent="NIH Phase 2 runnable local bitemporal query prototype",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,inputs=payload,
            expected_output={"kind":"nih-local-temporal-prototype-result/v1","official_submission":False},
            dependencies=(req["reasoning_job_id"],req["packet_job_id"]),
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:("computation",)},
            boundaries=(
                "Only validated synthetic dataset. No live medical inference or patient identifiers.",
                "Worker returns executable source: host only launches it in native test context, not OS-sandboxed.",
                "Query correctness checked independently on NEW hidden time cutoffs.",
                "Prototype pass does not imply Phase 2 game-backed test, external benchmark, or NIH submission.",
            ),
            provenance=(f"source-edition:{WORKER_ID}:{version_id}",f"source-fingerprint:{fp}",
                        f"reasoning-job:{req['reasoning_job_id']}",
                        f"packet-job:{req['packet_job_id']}",f"workspace-lane:{lane_id}"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                      "worker_version":version_id,"edition_fingerprint":fp,
                      "checkpoint_contract":CP_ID,"native_evidence_verifier":VERIFIER,
                      "title":"Local runnable synthetic bitemporal prototype"},
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff,result):
        self._pinned(handoff)
        fp=handoff.metadata["edition_fingerprint"]
        expected=(EvidenceRecord(condition=WITNESS,kind="computation",
                  source=SOURCE,ref=fp,depth="host-ran-hidden-temporal-queries"),)
        if result.status!="COMPLETE" or result.evidence!=expected:
            raise ValueError("native prototype result has no independent witness")
        out=result.output
        keys={"kind","checkpoint_contract","checkpoint_verdict","checkpoint_worker_role",
              "native_verifier","prototype","worker_version","edition_fingerprint","child_pid"}
        if (type(out) is not dict or set(out)!=keys or
                out["kind"]!="nih-local-temporal-prototype-result/v1" or
                (out["checkpoint_contract"],out["checkpoint_verdict"],
                 out["checkpoint_worker_role"],out["native_verifier"])!=
                  (CP_ID,"PASS",WORKER_ROLE,VERIFIER) or
                out["worker_version"]!=handoff.metadata["worker_version"] or
                out["edition_fingerprint"]!=fp or
                type(out["child_pid"]) is not int or out["child_pid"]<=0):
            raise ValueError("prototype result is not source-owned")
        data=handoff.inputs
        verify_prototype(out["prototype"],request=data["request"],scope=data["scope"],
                         reasoning_request=data["reasoning_request"],
                         packet_summary=data["packet_summary"],
                         ontology_sha256=data["ontology_sha256"])

    def execute(self,job_id,*,allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("explicit exact native BUILD authorization required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,PrototypeWorker(self,job_id))

    def reverify(self,job_id):
        state=self.runtime.state(job_id)
        if state.status!="COMPLETE":
            raise ValueError("prototype build not completed")
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True
