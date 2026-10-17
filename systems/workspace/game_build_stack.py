"""WORLD -> existing workstation BUILD -> independent native WITNESS -> artifact.

This is an invoked end-to-end game *construction*, not a fixed replay.
Browser WITNESS runs separately and is not inferred from the native PASS.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .game_build_bridge import GameBuildBridge, copy_builder_source, WORKER_ID
from .game_build_native import check_world, verify_build
from .workstation import ProcessWorkstation
from .controls import prepare, run_job, reverify_job

VERSION = "first-playable-build-v1"
WORKER_VERSION = "source-v1"
JOB_ID = "build-game-room-v1"


def construct(*, data_dir: Path, world: dict, output_dir: Path) -> dict:
    """Let registered bounded BUILD process create the game; host only witnesses it."""
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    check_world(world)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    original = data_dir / "world-request.json"
    serialized = json.dumps(world, sort_keys=True, indent=2) + "\n"
    if original.exists() and original.read_text() != serialized:
        raise ValueError("WORLD changed after first admitted construction")
    original.write_text(serialized)
    desk = ProcessWorkstation(data_dir / "workstation")
    try:
        source = desk.inspect(worker_id=WORKER_ID, version_id=WORKER_VERSION)
    except KeyError:
        copy_builder_source(data_dir, version_id=WORKER_VERSION, allow_copy=True)
        source = desk.inspect(worker_id=WORKER_ID, version_id=WORKER_VERSION)
    prepared = prepare(data_dir=data_dir, worker_id=WORKER_ID,
                       version_id=WORKER_VERSION, inputs_file=original)
    if prepared["fingerprint"] != source["current_fingerprint"]:
        raise ValueError("native BUILDER source changed")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    bridge = GameBuildBridge(runtime=runtime, workstation=desk)
    if JOB_ID not in runtime.snapshot():
        bridge.admit(version_id=WORKER_VERSION, world=world,
                     from_actor="WORLD-coordinator", job_id=JOB_ID)
    else:
        if runtime.get(JOB_ID).inputs != world:
            raise ValueError("existing game BUILD job has different WORLD inputs")
    # The source-owned worker, NOT coordinator, constructs the playable game.
    moved = run_job(data_dir=data_dir, job_id=JOB_ID, confirm_execute=JOB_ID)
    independent = reverify_job(data_dir=data_dir, job_id=JOB_ID)
    if moved["status"] != "COMPLETE" or independent["reverified"] is not True:
        raise ValueError("game BUILD did not complete independent native witness")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    result = runtime.state(JOB_ID).output["build"]
    native = verify_build(world, result)
    playable = output_dir / "built-world-room.html"
    if playable.exists() and playable.read_text(encoding="utf8") != result["html"]:
        raise ValueError("existing published build differs from source-owned result")
    playable.write_text(result["html"], encoding="utf8")
    report = {
        "schema": "world-build-witness-station/v1",
        "worker": WORKER_ID, "worker_version": WORKER_VERSION,
        "job_id": JOB_ID, "source_fingerprint": prepared["fingerprint"],
        "world_id": world["world_id"], "WORLD_input": world,
        "BUILD_native_execution": "COMPLETE",
        "WITNESS_native_w12": native["w12_native_replay"],
        "WITNESS_browser": "SEPARATE_REQUIRED",
        "artifact": playable.name,
        "html_sha256": native["html_sha256"],
        "plan": result["plan"],
        "plan_length": native["shortest_solve_actions"],
        "construction_not_fixed_W13_replay": True,
        "model_ai_helpers": False,
        "subprocess_did_build_new_artifact": True,
    }
    (output_dir / "build-report.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--world-file", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.world_file.is_file() or args.world_file.is_symlink() or args.world_file.stat().st_size > 4096:
        raise ValueError("WORLD file is missing or unsafe")
    world = json.loads(args.world_file.read_text(encoding="utf8"))
    print(json.dumps(construct(data_dir=args.data_dir, world=world,
                               output_dir=args.output_dir), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
