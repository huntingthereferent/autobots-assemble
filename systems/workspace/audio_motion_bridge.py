"""Real ProcessWorkstation -> HandoffRuntime -> native audio verifier.

Local and explicitly invoked. The public workstation remains read-only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff, SimulatedActor
from runtime.journal import RuntimeJournal

from .audio_motion_native import (SOURCE_LOCATOR, VERIFIER, WITNESS, content_sha,
                                  expected_result, read_wav_request, validate_input,
                                  write_verified_wav)
from .store import WorkspaceStore
from .workstation import ProcessWorkstation

WORKER_ID = "audio-pcm-motion"
SOURCE_FILE = "motion_worker.py"
SOURCE_DIRECTORY = Path(__file__).parent / "audio_motion_worker_source"
RELATION = "move user-supplied PCM16 samples and independently replay"
LANE_ID = "creative-audio-motion"


def copy_audio_source(data_dir: str | Path, version_id: str, *, allow_copy: bool = False) -> dict:
    if not allow_copy:
        raise PermissionError("copy requires explicit allow_copy")
    return ProcessWorkstation(Path(data_dir)/"workstation").copy_source(
        SOURCE_DIRECTORY, worker_id=WORKER_ID, version_id=version_id, source_locator=SOURCE_LOCATOR)


def _run_child(edition: Path, inputs: dict) -> dict:
    try:
        run = subprocess.run([sys.executable, "-I", str(edition/SOURCE_FILE)],
                             cwd=edition, input=json.dumps(inputs, separators=(",", ":")),
                             text=True, capture_output=True, timeout=10, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("audio worker time limit") from exc
    if run.returncode or len(run.stdout) > 180000 or len(run.stderr) > 4096:
        raise RuntimeError("native audio source failed; no result accepted")
    try:
        observed = json.loads(run.stdout)
    except ValueError as exc:
        raise ValueError("invalid child JSON") from exc
    if (type(observed) is not dict or set(observed) != {"result", "pid"}
            or type(observed["pid"]) is not int or observed["pid"] <= 0):
        raise ValueError("unexpected native child output")
    return observed


class AudioMotionBridge:
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.workstation = ProcessWorkstation(self.data_dir/"workstation")
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.data_dir/"runtime.jsonl"))
        self.runtime.register_evidence_verifier(VERIFIER, self._verify)

    def _pinned(self, handoff: Handoff) -> Path:
        metadata = handoff.metadata
        if (metadata.get("source_system") != "process-workstation"
                or metadata.get("worker_id") != WORKER_ID
                or metadata.get("native_evidence_verifier") != VERIFIER
                or handoff.required_relation != RELATION):
            raise ValueError("not an audio workstation native handoff")
        version = metadata.get("worker_version")
        folder, record = self.workstation._read(WORKER_ID, version)
        report = self.workstation.inspect(worker_id=WORKER_ID, version_id=version)
        if (record["source_locator"] != SOURCE_LOCATOR or
                report["current_fingerprint"] != metadata.get("edition_fingerprint") or
                SOURCE_FILE not in self.workstation._inventory_edition(folder)):
            raise ValueError("audio worker source changed or unpinned")
        return folder

    def admit(self, version_id: str, inputs: dict, *, from_actor: str,
              job_id: str | None = None) -> Handoff:
        if not isinstance(from_actor, str) or not from_actor.strip():
            raise ValueError("explicit caller identity needed")
        canonical = validate_input(inputs)
        fp = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)["current_fingerprint"]
        handoff = Handoff(
            handoff_id=job_id or "audio-motion-"+uuid4().hex,
            referent="user-provided PCM16 audio / finite pitch movement",
            from_actor=from_actor, to_actor="audio-motion:"+version_id,
            required_relation=RELATION, inputs=canonical,
            expected_output={"schema": "ab-audio-motion-result/v1"},
            required_witnesses=(WITNESS,),
            admissible_evidence={WITNESS: ("computation",)},
            boundaries=("Actual local PCM only; no Suno account, trained model, or API.",
                        "A moved sample is not new AI-generated music.",
                        "Worker code is trusted local Python, not OS-sandboxed."),
            provenance=("workspace-lane:"+LANE_ID, "worker-edition:"+WORKER_ID+":"+version_id,
                        "source-fingerprint:"+fp, "audio-input:"+canonical["source_sha256"]),
            metadata={"title": "Finite audio movement", "source_system": "process-workstation",
                      "worker_id": WORKER_ID, "worker_version": version_id,
                      "edition_fingerprint": fp, "native_evidence_verifier": VERIFIER})
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, returned: ExecutionResult) -> None:
        self._pinned(handoff)
        if returned.status != "COMPLETE":
            raise ValueError("only complete audio movement admitted as result")
        fp = handoff.metadata["edition_fingerprint"]
        expected_evidence = EvidenceRecord(condition=WITNESS, kind="computation",
                                           source="host-owned native audio replay",
                                           ref=fp, depth="independent-host-replay")
        if returned.evidence != (expected_evidence,):
            raise ValueError("audio evidence did not match exact native witness")
        out = returned.output
        if (type(out) is not dict or set(out) != {"result", "pid", "worker_version", "edition_fingerprint"}
                or type(out["pid"]) is not int or out["pid"] <= 0
                or out["worker_version"] != handoff.metadata["worker_version"]
                or out["edition_fingerprint"] != fp
                or type(out["result"]) is not dict
                or out["result"] != expected_result(handoff.inputs)):
            raise ValueError("native independent audio replay disagrees")

    def execute(self, job_id: str, *, allow_local_execution: bool = False):
        if not allow_local_execution:
            raise PermissionError("execution requires allow_local_execution")
        handoff = self.runtime.get(job_id)
        edition = self._pinned(handoff)
        def execute_worker(h: Handoff) -> ExecutionResult:
            row = _run_child(edition, h.inputs)
            return ExecutionResult(status="COMPLETE",
                                   output={**row, "worker_version": h.metadata["worker_version"],
                                           "edition_fingerprint": h.metadata["edition_fingerprint"]},
                                   evidence=(EvidenceRecord(condition=WITNESS, kind="computation",
                                       source="host-owned native audio replay",
                                       ref=h.metadata["edition_fingerprint"],
                                       depth="independent-host-replay"),))
        actor = SimulatedActor(actor_id=handoff.to_actor, capabilities=(RELATION,), handler=execute_worker)
        return self.runtime.run(job_id, actor)

    def reverify(self, job_id: str) -> dict:
        state = self.runtime.state(job_id)
        if state.status != "COMPLETE":
            raise ValueError("cannot reverify incomplete audio job")
        self._verify(self.runtime.get(job_id),
                     ExecutionResult(status="COMPLETE", output=state.output, evidence=state.evidence))
        result = state.output["result"]
        return {"job_id": job_id, "reverified": True, "worker_version": state.output["worker_version"],
                "source_sha256": result["source_sha256"],
                "pcm_sha256": content_sha(result["pcm"]), "frames": len(result["pcm"]),
                "note": result["target_note"]}

    def record_movement(self, job_id: str) -> dict:
        """Only record a returned movement after fresh native re-verification."""
        report = self.reverify(job_id)
        store = WorkspaceStore(self.data_dir/"workspace.jsonl")
        try:
            lane = store.get_lane(LANE_ID)
        except KeyError:
            lane = store.open_lane(LANE_ID, label="Creative audio motion",
                                   referent="user-supplied PCM waveform transformations",
                                   actor_id="workstation-operator",
                                   sources=(SOURCE_LOCATOR, "work/projects/suno-export-intake/README.md"))
        if any("job:"+job_id in evt["data"].get("evidence_refs", []) for evt in store.history(LANE_ID)):
            return report | {"movement_recorded": False, "return_event": lane.latest_event_id}
        new = store.record_movement(
            LANE_ID,
            changes="PCM resampling moved "+str(report["frames"])+" frames to MIDI note "+str(report["note"]),
            preserved="original source SHA-256 "+report["source_sha256"],
            next_movement="inspect audible result against selected source and choose next finite movement",
            evidence_refs=("job:"+job_id, "pcm-sha256:"+report["pcm_sha256"],
                           "source-sha256:"+report["source_sha256"]))
        return report | {"movement_recorded": True, "return_event": new.latest_event_id}

    def export(self, job_id: str, destination: str | Path) -> dict:
        self.reverify(job_id)
        return write_verified_wav(destination, self.runtime.state(job_id).output["result"])


def main():
    parser = argparse.ArgumentParser(description="Execute one source-pinned audio motion in the native workstation")
    parser.add_argument("--data-dir", default="runtime/data")
    parser.add_argument("--source-wav", required=True)
    parser.add_argument("--version", default="audio-v1")
    parser.add_argument("--root-note", type=int, default=60)
    parser.add_argument("--note", type=int, required=True)
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--copy-source", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not args.copy_source or not args.execute:
        parser.error("explicit --copy-source and --execute required for first-run local operation")
    copy_audio_source(args.data_dir, args.version, allow_copy=True)
    bridge = AudioMotionBridge(args.data_dir)
    inputs = read_wav_request(args.source_wav, root_note=args.root_note,
                              target_note=args.note, reverse=args.reverse)
    job = bridge.admit(args.version, inputs, from_actor="workstation-operator")
    state = bridge.execute(job.handoff_id, allow_local_execution=True)
    report = bridge.record_movement(job.handoff_id)
    manifest = bridge.export(job.handoff_id, args.out)
    print(json.dumps({"job": job.handoff_id, "status": state.status, "verification": report,
                      "export": manifest}, sort_keys=True))


if __name__ == "__main__":
    main()
