"""Owner-native readiness through existing controls, with an external source input.

The temporal journal is never imported into the owner runtime. Its original ZIP
is digest-pinned and independently unpacked/reverified for every admission and
result verification. Only the new readiness job is admitted in the owner journal.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

WORKER_ID = "game-worker-ready"
VERSION = "owner-adapter-v1"
JOB_ID = "game-worker-ready-owner-001"
CP = "GAME-WORKER-READY"
VERIFIER = "cp-checker:GAME-WORKER-READY"
PARENT = "game-w13-github-001"
CHILD = "game-native-verifier-github-001"
FILE = "ready_worker.py"
SOURCE = Path(__file__).resolve().parent/"owner_game_ready_source"
LOCATOR = "repo:systems/workspace/owner_game_ready_source/ready_worker.py"
WITNESS = "fresh owner parents and authenticated external temporal input"
RELATION = "verify owner W13 controls adapter with separately witnessed temporal source"
KIND = "owner-w13-adapter-readiness-result/v1"
TEMPORAL_EVENT = "evt_05b1d2037e5142e5bde09a3eabaf880a"
BROWSER_EVENT = "evt_1ee9120f85164932b7fc778cd46dbcdc"


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def expected_receipt(data):
    if type(data) is not dict or set(data) != {"kind","source_pair","adapter"}:
        raise ValueError("exact owner readiness envelope required")
    from .owner_temporal_handoff import CHILD_EVENT, SOURCES
    pair = data["source_pair"]
    if (data["kind"] != "owner-w13-adapter-readiness/v1"
            or pair["schema"] != "owner-temporal-source-pair/v1"
            or pair["state"] != "BOTH_NATIVE_HISTORIES_FRESHLY_REVERIFIED_SEPARATELY"
            or pair["owner_child_event"] != CHILD_EVENT
            or pair["owner_parent_event"] != "evt_208f2fbdb380437eb59790a9a704c0b9"
            or pair["temporal_result_event"] != TEMPORAL_EVENT
            or pair["temporal_browser_event"] != BROWSER_EVENT
            or pair["source_artifacts"] != SOURCES
            or pair["temporal_live_queries"] < 5
            or pair["journal_hashes_unchanged"] is not True
            or pair["owner_runtime_contains_temporal_source"] is not False
            or pair["native_dependency_join_witnessed"] is not False
            or pair["game_worker_ready_witnessed"] is not False
            or data["adapter"] != {"route":"controls.run_job", "exact_confirmation":PARENT,
                                    "wrong_confirmation_rejected":True}):
        raise ValueError("owner adapter source identity or controls route differs")
    return {"kind":"owner-w13-adapter-ready-receipt/v1", "input_sha256":digest(data),
        "owner_parent_event":pair["owner_parent_event"],
        "owner_child_event":pair["owner_child_event"],
        "external_temporal_result_event":TEMPORAL_EVENT,
        "external_temporal_browser_event":BROWSER_EVENT,
        "external_temporal_source_consumed":True, "histories_remain_separate":True,
        "adapter_route":"controls.run_job",
        "scope":"owner-W13-adapter-with-external-synthetic-temporal-source"}


class OwnerGameReadyBridge:
    def __init__(self, *, runtime, workstation):
        self.runtime, self.workstation = runtime, workstation
        runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _inputs(self):
        from .owner_temporal_handoff import unpack_zip, unpack_temporal, witness_pair, SOURCES
        from .controls import run_job, prepare
        root = self.workstation.root.parent
        archive = root/"external-temporal.zip"
        if archive.is_symlink() or not archive.is_file() or archive.stat().st_size > 8*1024*1024:
            raise ValueError("authenticated external temporal ZIP required")
        with TemporaryDirectory(prefix="ready-temporal-") as tmp:
            scratch = Path(tmp)
            unpack_zip(archive.read_bytes(),scratch/"artifact",SOURCES["temporal"]["digest"])
            unpack_temporal(scratch/"artifact", scratch/"native")
            pair = witness_pair(owner_dir=root,temporal_dir=scratch/"native",
                                temporal_artifacts=scratch/"artifact")
        before = (root/"runtime.jsonl").read_bytes()
        try:
            run_job(data_dir=root,job_id=PARENT,confirm_execute="not-"+PARENT)
        except PermissionError:
            pass
        else:
            raise ValueError("wrong owner controls confirmation was accepted")
        if before != (root/"runtime.jsonl").read_bytes():
            raise ValueError("negative controls route changed owner journal")
        prepare(data_dir=root,worker_id="game-worlds-w13",version_id="w13-github-v1",
                inputs_file=Path(__file__).resolve().parents[2]/
                    "network/tests/fixtures/game_w13_native_cp_example.json")
        data = {"kind":"owner-w13-adapter-readiness/v1", "source_pair":pair,
                "adapter":{"route":"controls.run_job", "exact_confirmation":PARENT,
                           "wrong_confirmation_rejected":True}}
        expected_receipt(data)
        return data

    def _pinned(self, handoff):
        md = handoff.metadata
        if (handoff.handoff_id != JOB_ID or handoff.dependencies != (PARENT,CHILD)
                or handoff.required_relation != RELATION
                or md.get("source_system") != "process-workstation"
                or md.get("worker_id") != WORKER_ID or md.get("worker_version") != VERSION
                or md.get("checkpoint_contract") != CP
                or md.get("native_evidence_verifier") != VERIFIER
                or md.get("owner_temporal_scope") != "separate-authenticated-input/v1"
                or handoff.expected_output != {"kind":KIND,"official_NIH_test":False}):
            raise ValueError("owner readiness native contract differs")
        folder, record = self.workstation._read(WORKER_ID,VERSION)
        edition = self.workstation.inspect(worker_id=WORKER_ID,version_id=VERSION)
        if (record.get("source_locator") != LOCATOR
                or set(self.workstation._inventory_edition(folder)) != {FILE}
                or edition["current_fingerprint"] != md.get("edition_fingerprint")
                or edition["added"] or edition["deleted"] or edition["modified"]
                or handoff.inputs != self._inputs()):
            raise ValueError("owner readiness edition or freshly verified inputs changed")
        return folder

    def admit(self, *, from_actor):
        from runtime.handoff import Handoff
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError("source owner actor required")
        data = self._inputs()
        fp = self.workstation.inspect(worker_id=WORKER_ID,version_id=VERSION)["current_fingerprint"]
        handoff = Handoff(handoff_id=JOB_ID,
            referent="Owner W13 native adapter readiness with external temporal source",
            from_actor=from_actor,to_actor=f"{WORKER_ID}:{VERSION}",
            required_relation=RELATION,inputs=data,expected_output={"kind":KIND,"official_NIH_test":False},
            dependencies=(PARENT,CHILD),required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS:("computation",)},
            boundaries=("Temporal history is an authenticated external input, not an imported native parent.",
                        "Readiness does not execute NIH-P2-TEST or establish official performance."),
            provenance=(f"owner-parent:{PARENT}",f"owner-child:{CHILD}",
                        f"external-temporal-result:{TEMPORAL_EVENT}",f"source-fingerprint:{fp}"),
            metadata={"source_system":"process-workstation","worker_id":WORKER_ID,
                "worker_version":VERSION,"edition_fingerprint":fp,"checkpoint_contract":CP,
                "native_evidence_verifier":VERIFIER,"owner_temporal_scope":"separate-authenticated-input/v1"})
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _evidence(self, handoff):
        from runtime.handoff import EvidenceRecord
        return (EvidenceRecord(condition=WITNESS,kind="computation",source="owner-adapter-native/v1",
            ref=handoff.metadata["edition_fingerprint"],depth="fresh-two-source-controls-verification"),)

    def _verify(self, handoff, result):
        self._pinned(handoff)
        out = result.output
        if (result.status != "COMPLETE" or result.evidence != self._evidence(handoff)
                or type(out) is not dict or set(out) != {"kind","checkpoint_contract",
                    "checkpoint_verdict","checkpoint_worker_role","native_verifier","report",
                    "worker_version","edition_fingerprint","pid"}
                or out["kind"] != KIND or out["checkpoint_contract"] != CP
                or out["checkpoint_verdict"] != "PASS" or out["checkpoint_worker_role"] != "game-adapter"
                or out["native_verifier"] != VERIFIER or out["worker_version"] != VERSION
                or out["edition_fingerprint"] != handoff.metadata["edition_fingerprint"]
                or type(out["pid"]) is not int or out["pid"] <= 0
                or out["report"] != expected_receipt(handoff.inputs)):
            raise ValueError("owner readiness lacks independent native host witness")

    def execute(self, job_id, *, allow_local_execution=False):
        if not allow_local_execution or job_id != JOB_ID:
            raise PermissionError("exact owner readiness confirmation required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id,OwnerReadyWorker(self))

    def reverify(self, job_id):
        from runtime.handoff import ExecutionResult
        if job_id != JOB_ID or self.runtime.state(job_id).status != "COMPLETE":
            raise ValueError("owner readiness not complete")
        state = self.runtime.state(job_id)
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status="COMPLETE",output=state.output,evidence=state.evidence))
        return True


@dataclass(frozen=True)
class OwnerReadyWorker:
    bridge: OwnerGameReadyBridge

    @property
    def actor_id(self):
        return self.bridge.runtime.get(JOB_ID).to_actor

    def can_execute(self, handoff):
        return handoff.handoff_id == JOB_ID and handoff.to_actor == self.actor_id

    def execute(self, handoff):
        from runtime.handoff import ExecutionResult
        if not self.can_execute(handoff):
            raise ValueError("wrong owner readiness handoff")
        folder = self.bridge._pinned(handoff)
        proc = subprocess.run([sys.executable,"-I",str(folder/FILE)],
            input=json.dumps(handoff.inputs),capture_output=True,text=True,cwd=folder,timeout=8,check=False)
        if proc.returncode or len(proc.stdout)>8000 or len(proc.stderr)>4096:
            raise ValueError("bounded owner readiness subprocess failed")
        returned = json.loads(proc.stdout)
        if type(returned) is not dict or set(returned) != {"receipt","pid"}:
            raise ValueError("owner worker process report differs")
        return ExecutionResult(status="COMPLETE",evidence=self.bridge._evidence(handoff),output={
            "kind":KIND,"checkpoint_contract":CP,"checkpoint_verdict":"PASS",
            "checkpoint_worker_role":"game-adapter","native_verifier":VERIFIER,
            "worker_version":VERSION,"edition_fingerprint":handoff.metadata["edition_fingerprint"],
            "report":returned["receipt"],"pid":returned["pid"]})
