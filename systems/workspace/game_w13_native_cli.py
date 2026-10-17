"""GAME W13 CP-native operator entrance: copy, prepare, admit, never auto-run.

The existing controls.run_job/reverify_job and coordinator_window bind-job
are the ONLY execution / slot binding paths. No new scheduler or job runner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .game_w13_native import validate_game_request
from .game_w13_native_bridge import (
    GameW13NativeBridge, WORKER_ID, copy_game_source,
)
from .controls import prepare as native_prepare


def bounded_input(path: Path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 4096:
        raise ValueError("exact W13 game request must be a safe <=4 KiB JSON file")
    return validate_game_request(json.loads(path.read_text(encoding="utf8")))


def main(argv=None):
    p = argparse.ArgumentParser(description="Source-owned game W13 CP explicit admission, not execution")
    p.add_argument("--data-dir", type=Path, required=True)
    subs = p.add_subparsers(dest="command", required=True)
    copy = subs.add_parser("copy")
    copy.add_argument("--version", required=True)
    copy.add_argument("--confirm-copy", action="store_true")
    pre = subs.add_parser("prepare")
    pre.add_argument("--version", required=True)
    pre.add_argument("--inputs-file", type=Path, required=True)
    admit = subs.add_parser("admit")
    admit.add_argument("--version", required=True)
    admit.add_argument("--inputs-file", type=Path, required=True)
    admit.add_argument("--job-id", required=True)
    admit.add_argument("--confirm-admit", required=True)
    admit.add_argument("--from-actor", required=True)
    a = p.parse_args(argv)
    data = a.data_dir.resolve()
    root = Path(__file__).resolve().parents[2]
    if data == root or root.is_relative_to(data):
        raise ValueError("workstation data must not contain repository source")
    if a.command == "copy":
        report = copy_game_source(data, version_id=a.version, allow_copy=a.confirm_copy)
    else:
        payload = bounded_input(a.inputs_file)
        if a.command == "prepare":
            report = native_prepare(data_dir=data, worker_id=WORKER_ID,
                                    version_id=a.version, inputs_file=a.inputs_file)
        else:
            if a.confirm_admit != a.job_id:
                raise PermissionError("W13 confirm-admit must equal exact job ID")
            desk = ProcessWorkstation(data / "workstation")
            runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
            bridge = GameW13NativeBridge(runtime=runtime, workstation=desk)
            handoff = bridge.admit(version_id=a.version, inputs=payload,
                                   from_actor=a.from_actor, job_id=a.job_id)
            report = {
                "job_id": handoff.handoff_id,
                "status": runtime.state(handoff.handoff_id).status,
                "source_fingerprint": handoff.metadata["edition_fingerprint"],
                "worker_id": WORKER_ID,
                "admitted": True,
                "executed": False,
            }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
