"""Actual bounded BUILD worker on the EXISTING ProcessWorkstation/HandoffRuntime."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, EvidenceRecord, ExecutionResult
from .workstation import ProcessWorkstation
from .game_build_native import WORKER_ID, VERIFIER, check_world, verify_build

SOURCE_FILE = "room_builder.py"
SOURCE_DIRECTORY = Path(__file__).resolve().parent / "game_build_worker_source"
LOCATOR = "repo:systems/workspace/game_build_worker_source/room_builder.py"
RELATION = "BUILD new playable room from WORLD geometry; independently verify against W12"
WITNESS = "independent original W12 replay validates newly constructed playable room"
SOURCE = "game-room-construction-v1"
RESULT_KIND = "game-built-room-artifact/v1"


def copy_builder_source(data_dir, *, version_id, allow_copy=False):
    if not allow_copy:
        raise PermissionError("exact source edition copy approval required")
    return ProcessWorkstation(Path(data_dir) / "workstation").copy_source(
        SOURCE_DIRECTORY, worker_id=WORKER_ID, version_id=version_id,
        source_locator=LOCATOR)


def run_builder(edition: Path, world: dict) -> dict:
    checked = check_world(world)
    try:
        child = subprocess.run(
            [sys.executable, "-I", str(edition / SOURCE_FILE)],
            cwd=edition, input=json.dumps(checked, sort_keys=True),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False, timeout=8,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("bounded BUILD subprocess timed out") from exc
    if child.returncode != 0 or len(child.stdout) > 25000 or len(child.stderr) > 4096:
        raise ValueError("bounded BUILD subprocess failed")
    try:
        result = json.loads(child.stdout)
    except ValueError as exc:
        raise ValueError("BUILD returned malformed JSON") from exc
    verify_build(world, result)
    return result


@dataclass(frozen=True)
class NativeBuildWorker:
    bridge: "GameBuildBridge"
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff):
        return (handoff.handoff_id == self.job_id and handoff.to_actor == self.actor_id
                and handoff.required_relation == RELATION)

    def execute(self, handoff):
        if not self.can_execute(handoff):
            raise ValueError("not admitted to this WORLD build")
        edition = self.bridge._pinned(handoff)
        built = run_builder(edition, handoff.inputs)
        return ExecutionResult(
            status="COMPLETE",
            output={"kind": RESULT_KIND, "build": built,
                    "worker_version": handoff.metadata["worker_version"],
                    "edition_fingerprint": handoff.metadata["edition_fingerprint"]},
            evidence=(EvidenceRecord(
                condition=WITNESS, kind="computation", source=VERIFIER,
                ref=handoff.metadata["edition_fingerprint"],
                depth="fresh-native-W12-independent-replay"),),
        )


class GameBuildBridge:
    """Version, admit, execute and reverify real BUILD in existing native journal."""

    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime, self.workstation = runtime, workstation
        self.runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _pinned(self, handoff):
        md = handoff.metadata
        if (md.get("source_system") != "process-workstation"
                or md.get("worker_id") != WORKER_ID
                or md.get("native_evidence_verifier") != VERIFIER):
            raise ValueError("not a source-owned game BUILD handoff")
        folder, record = self.workstation._read(WORKER_ID, md["worker_version"])
        inspected = self.workstation.inspect(worker_id=WORKER_ID, version_id=md["worker_version"])
        if (record["source_locator"] != LOCATOR
                or inspected["current_fingerprint"] != md["edition_fingerprint"]
                or set(self.workstation._inventory_edition(folder)) != {SOURCE_FILE}):
            raise ValueError("BUILD source edition is missing or changed")
        check_world(handoff.inputs)
        if handoff.expected_output != {"kind": RESULT_KIND, "new_playable_room": True}:
            raise ValueError("BUILD expected output altered")
        return folder

    def admit(self, *, version_id, world, from_actor, job_id):
        if not isinstance(from_actor, str) or not from_actor.strip():
            raise ValueError("explicit WORLD coordinator required")
        checked = check_world(world)
        inspected = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)
        fp = inspected["current_fingerprint"]
        handoff = Handoff(
            handoff_id=job_id,
            referent="WORLD -> BUILD new playable room " + world["world_id"],
            from_actor=from_actor, to_actor=f"{WORKER_ID}:{version_id}",
            required_relation=RELATION,
            inputs=checked, expected_output={"kind": RESULT_KIND, "new_playable_room": True},
            required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS: ("computation",)},
            boundaries=(
                "BUILD makes a new playable artifact, not a fixed W13 trace replay.",
                "W12 native transitions remain byte-preserved and independently verified.",
                "Browser WITNESS is separate from BUILD's source-owned native result.",
                "Source copy, admission, execution remain explicit native controls.",
                "Worker subprocess has no OS-level sandbox guarantee.",
            ),
            provenance=(f"source-edition:{WORKER_ID}:{version_id}",
                        f"source-fingerprint:{fp}", f"WORLD:{world['world_id']}"),
            metadata={
                "source_system": "process-workstation",
                "worker_id": WORKER_ID,
                "worker_version": version_id,
                "edition_fingerprint": fp,
                "native_evidence_verifier": VERIFIER,
                "stack_role": "BUILD",
            },
        )
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff, result):
        self._pinned(handoff)
        if result.status != "COMPLETE":
            raise ValueError("BUILD has not completed")
        expected = (EvidenceRecord(
            condition=WITNESS, kind="computation", source=VERIFIER,
            ref=handoff.metadata["edition_fingerprint"],
            depth="fresh-native-W12-independent-replay"),)
        if result.evidence != expected:
            raise ValueError("BUILD witness evidence altered")
        o = result.output
        if (type(o) is not dict or set(o) != {"kind", "build", "worker_version", "edition_fingerprint"}
                or o["kind"] != RESULT_KIND
                or o["worker_version"] != handoff.metadata["worker_version"]
                or o["edition_fingerprint"] != handoff.metadata["edition_fingerprint"]):
            raise ValueError("BUILD result is not the source-owned artifact")
        verify_build(handoff.inputs, o["build"])

    def execute(self, job_id, *, allow_local_execution=False):
        if not allow_local_execution:
            raise PermissionError("explicit exact native execution authorization required")
        self._pinned(self.runtime.get(job_id))
        return self.runtime.run(job_id, NativeBuildWorker(self, job_id))

    def reverify(self, job_id):
        s = self.runtime.state(job_id)
        if s.status != "COMPLETE":
            raise ValueError("BUILD still awaiting a source-owned result")
        self._verify(self.runtime.get(job_id), ExecutionResult(
            status="COMPLETE", output=s.output, evidence=s.evidence))
        return True
