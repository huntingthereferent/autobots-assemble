"""GAME-W13-WORLDS CP-native worker on the existing Process Workstation.

Copy/admit/execute/reverify are separate operator-controlled boundaries.
Worker executes copied finite source; host independently replays original W12
without importing the source subprocess or BUILD's W13 verifier.
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
from .game_w13_native import (
    CP_ID, WORKER_ROLE, VERIFIER, REPORT_KIND,
    validate_game_request, verify_native_report,
)
from .workstation import ProcessWorkstation

WORKER_ID = "game-worlds-w13"
SOURCE_FILE = "game_worlds_worker.py"
SOURCE_DIRECTORY = Path(__file__).resolve().parent / "game_w13_worker_source"
LOCATOR = "repo:systems/workspace/game_w13_worker_source/game_worlds_worker.py"
RELATION = "execute exact two-room WORLD W13 native path from preserved W12 rules"
WITNESS = "host W12 native replay matches finite W13 source-owned two-room result"
EVIDENCE_SOURCE = "game-w13-cp-independent-native-w12-replay"


def copy_game_source(data_dir: str | Path, *, version_id: str, allow_copy: bool = False) -> dict:
    if not allow_copy:
        raise PermissionError("explicit game worker source-copy confirmation required")
    desk = ProcessWorkstation(Path(data_dir) / "workstation")
    return desk.copy_source(SOURCE_DIRECTORY, worker_id=WORKER_ID,
                            version_id=version_id, source_locator=LOCATOR)


def run_source(edition: Path, payload: dict) -> dict:
    canonical = validate_game_request(payload)
    try:
        run = subprocess.run(
            [sys.executable, "-I", str(edition / SOURCE_FILE)],
            cwd=edition, input=json.dumps(canonical, sort_keys=True),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            text=True, timeout=8,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("game W13 source subprocess exceeded finite bound") from exc
    if run.returncode != 0 or len(run.stdout) > 12000 or len(run.stderr) > 4096:
        raise ValueError("game W13 source failed bounded subprocess contract")
    try:
        value = json.loads(run.stdout)
    except ValueError as exc:
        raise ValueError("game W13 source returned invalid JSON") from exc
    verify_native_report(canonical, value)
    return value


@dataclass(frozen=True)
class GameW13NativeWorker:
    bridge: "GameW13NativeBridge"
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff: Handoff):
        return (handoff.handoff_id == self.job_id
                and handoff.to_actor == self.actor_id
                and handoff.required_relation == RELATION)

    def execute(self, handoff: Handoff):
        if not self.can_execute(handoff):
            raise ValueError("wrong native W13 game handoff")
        edition = self.bridge._pinned(handoff)
        native = run_source(edition, handoff.inputs)
        fingerprint = handoff.metadata["edition_fingerprint"]
        return ExecutionResult(status="COMPLETE", output={
            "kind": REPORT_KIND,
            "checkpoint_contract": CP_ID,
            "checkpoint_verdict": "PASS",
            "checkpoint_worker_role": WORKER_ROLE,
            "native_verifier": VERIFIER,
            "report": native,
            "worker_version": handoff.metadata["worker_version"],
            "edition_fingerprint": fingerprint,
        }, evidence=(EvidenceRecord(
            condition=WITNESS, kind="computation", source=EVIDENCE_SOURCE,
            ref=fingerprint, depth="independent-original-W12-native-session-replay",
        ),))


class GameW13NativeBridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime, self.workstation = runtime, workstation
        runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _pinned(self, handoff: Handoff) -> Path:
        metadata = handoff.metadata
        if (metadata.get("source_system") != "process-workstation"
                or metadata.get("worker_id") != WORKER_ID
                or metadata.get("checkpoint_contract") != CP_ID
                or metadata.get("native_evidence_verifier") != VERIFIER):
            raise ValueError("not the admitted W13 source-owned game CP")
        edition, recorded = self.workstation._read(
            WORKER_ID, metadata.get("worker_version"))
        checked = self.workstation.inspect(
            worker_id=WORKER_ID, version_id=metadata.get("worker_version"))
        files = self.workstation._inventory_edition(edition)
        if (recorded["source_locator"] != LOCATOR
                or checked["current_fingerprint"] != metadata.get("edition_fingerprint")
                or set(files) != {SOURCE_FILE}):
            raise ValueError("W13 native game source changed, missing or unsafe")
        validate_game_request(handoff.inputs)
        if handoff.expected_output != {"kind": REPORT_KIND, "two_declared_worlds_only": True}:
            raise ValueError("W13 exact native source-bound expectation changed")
        return edition

    def admit(self, *, version_id: str, inputs: dict, from_actor: str,
              job_id: str | None = None, lane_id: str = "game") -> Handoff:
        if not isinstance(from_actor, str) or not from_actor.strip():
            raise ValueError("explicit W13 game operator admission actor required")
        payload = validate_game_request(inputs)
        inspected = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)
        fingerprint = inspected["current_fingerprint"]
        handoff = Handoff(
            handoff_id=job_id or "game-w13-" + uuid4().hex,
            referent=f"WORLD W13 / native two-room game / {version_id}",
            from_actor=from_actor.strip(),
            to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,
            inputs=payload,
            expected_output={"kind": REPORT_KIND, "two_declared_worlds_only": True},
            required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS: ("computation",)},
            boundaries=(
                "Exact two WORLD W13 rooms and five global actions only.",
                "Original W12 native transition source must remain unchanged.",
                "No browser-origin authentication or arbitrary world generator.",
                "A game CP PASS proves only this finite source-owned computation.",
                "Source copy, admission and run require separate operator confirmation.",
                "Copied Python worker is not OS-sandboxed.",
            ),
            provenance=(
                f"worker-edition:{WORKER_ID}:{version_id}",
                f"source-fingerprint:{fingerprint}",
                f"workspace-lane:{lane_id}",
            ),
            metadata={
                "title": "WORLD W13 native two-room source-owned checkpoint",
                "source_system": "process-workstation",
                "worker_id": WORKER_ID,
                "worker_version": version_id,
                "edition_fingerprint": fingerprint,
                "checkpoint_contract": CP_ID,
                "native_evidence_verifier": VERIFIER,
            },
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult):
        self._pinned(handoff)
        if result.status != "COMPLETE":
            raise ValueError("W13 native game computation not COMPLETE")
        fingerprint = handoff.metadata["edition_fingerprint"]
        expected = (EvidenceRecord(
            condition=WITNESS, kind="computation", source=EVIDENCE_SOURCE,
            ref=fingerprint, depth="independent-original-W12-native-session-replay",
        ),)
        if result.evidence != expected:
            raise ValueError("W13 host verification evidence changed")
        value = result.output
        keys = {
            "kind", "checkpoint_contract", "checkpoint_verdict",
            "checkpoint_worker_role", "native_verifier", "report",
            "worker_version", "edition_fingerprint",
        }
        if (type(value) is not dict or set(value) != keys
                or value["kind"] != REPORT_KIND
                or (value["checkpoint_contract"], value["checkpoint_verdict"],
                    value["checkpoint_worker_role"], value["native_verifier"])
                   != (CP_ID, "PASS", WORKER_ROLE, VERIFIER)
                or value["worker_version"] != handoff.metadata["worker_version"]
                or value["edition_fingerprint"] != fingerprint):
            raise ValueError("W13 source-owned CP output contract mismatch")
        verify_native_report(handoff.inputs, value["report"])

    def execute(self, job_id: str, *, allow_local_execution: bool = False):
        if not allow_local_execution:
            raise PermissionError("W13 native game execution requires explicit exact-job authorization")
        handoff = self.runtime.get(job_id)
        self._pinned(handoff)
        return self.runtime.run(job_id, GameW13NativeWorker(self, job_id))

    def reverify(self, job_id: str) -> bool:
        state = self.runtime.state(job_id)
        if state.status != "COMPLETE":
            raise ValueError("W13 source-owned game job must be COMPLETE for fresh replay")
        self._verify(
            self.runtime.get(job_id),
            ExecutionResult(status="COMPLETE", output=state.output, evidence=state.evidence),
        )
        return True
