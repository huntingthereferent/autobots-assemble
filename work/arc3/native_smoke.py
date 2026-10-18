"""Run the original 48-law experimental MyAgent on native public ARC games.

This is a bounded experiment, not a competition result, submission, solver,
new game implementation, or restored saved route. Native SDK required.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AGENT_SOURCE = ROOT / "work/arc3/agent/my_agent.py"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default="sk48")
    parser.add_argument("--max-actions", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("runtime/data/arc3/window48-native-smoke.json"))
    args = parser.parse_args()
    if args.max_actions < 1 or args.max_actions > 50:
        raise ValueError("smoke run is bounded to 1..50 actual environment actions")
    framework = os.environ.get("ARC3_FRAMEWORK")
    if framework:
        sys.path.insert(0, str(Path(framework).resolve()))

    import arc_agi
    from arc_agi import OperationMode

    spec = importlib.util.spec_from_file_location("arc3_f3_native_entry", AGENT_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("F3 agent source inaccessible")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    infos = arcade.get_environments()
    game_ids = {i.game_id.split("-", 1)[0] for i in infos}
    if args.game not in game_ids:
        raise ValueError("game not available in native SDK public roster")
    env = arcade.make(args.game)
    if env is None:
        raise RuntimeError("official ARC environment unavailable")
    # The official ARC Agent.main calls choose_action before testing
    # is_done in some paths. An ACTION6-only game therefore cannot be
    # safely run by a two-generator native agent. Observe its REAL native
    # reset and persist the explicit wall without sending a fake click.
    root_obs = env.reset()
    root_advertised = [
        int(getattr(a, "value", a))
        for a in (getattr(root_obs, "available_actions", ()) or ())
    ]
    if len([n for n in root_advertised if n in (1, 2, 3, 4, 5)]) < 2:
        root_grid = np.asarray(getattr(root_obs, "frame"))
        if root_grid.size != 4096:
            raise ValueError("native click-only reset has no complete frame")
        root_grid = root_grid.reshape(-1, 64, 64)[-1].astype(np.uint8)
        result = {
            "kind": "ORIGINAL_WINDOW48_NATIVE_INTERFACE_WALL",
            "source_agent_sha256": sha256(AGENT_SOURCE.read_bytes()).hexdigest(),
            "source_mathematical_family": "work/arc_like_maze/window_combined.py",
            "source_original_law_count": len(module.WINDOW48),
            "source_rooted_class_count": module.ROOTED_CLASS_COUNT,
            "source_full_state_class_count": module.FULL_STATE_CLASS_COUNT,
            "game": args.game,
            "environment_provider": "official arc-agi Arcade NORMAL",
            "native_root_advertised_actions": root_advertised,
            "native_root_frame_hash": module.observation_key(root_obs).hex(),
            "native_environment_actions": 0,
            "levels_completed": int(getattr(root_obs, "levels_completed", 0)),
            "stopped_at_mathematical_or_interface_wall": True,
            "status": "WALL_NO_OBSERVED_NATIVE_A_B_GENERATORS",
            "window48_evidence": None,
            "boundary": "The real game was reset and observed. No native clicks were issued, no coordinates were invented, and no F3 A/B correspondence or ARC win is claimed.",
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        np.savez_compressed(args.out.with_suffix(".npz"), root=root_grid)
        print("WINDOW48_NATIVE_RESULT "+json.dumps({
            "game":args.game,
            "native_environment_actions":0,
            "levels_completed":result["levels_completed"],
            "root_available_actions":root_advertised,
            "status":result["status"],
            "stopped_at_wall":True,
            "manifest":str(args.out),
            "raw_frames":str(args.out.with_suffix(".npz")),
        },sort_keys=True))
        return

    agent = module.MyAgent(
        card_id="window48-native-smoke",
        game_id=args.game,
        agent_name=f"Window48NativeSmoke.{args.game}",
        ROOT_URL="http://localhost",
        record=False,
        arc_env=env,
        tags=["f3-window48", "native-observation", "experimental"],
    )
    # Official Agent.main uses <= MAX_ACTIONS; 0-index accordingly.
    agent.MAX_ACTIONS = args.max_actions - 1
    agent.main()

    actual = agent.frames[1:]  # official framework seeds frames[0] with empty bookkeeping
    rows = []
    for i, frame in enumerate(actual):
        try:
            frame_hash = module.observation_key(frame).hex()
        except ValueError:
            frame_hash = None
        rows.append({
            "native_response_index": i,
            "exact_frame_hash": frame_hash,
            "levels_completed": int(getattr(frame, "levels_completed", 0)),
            "state": str(getattr(frame, "state", "UNKNOWN")),
            "available_actions": [
                int(getattr(a, "value", a))
                for a in (getattr(frame, "available_actions", ()) or ())
            ],
        })

    # The official SDK may stop at the action budget before consuming
    # the final native response. Record that response at most once.
    if actual and agent.pending_letter is not None:
        agent._consume_pending_native_response(actual[-1])
    evidence = agent.f3_48
    result = {
        "kind": "ORIGINAL_WINDOW48_ON_NATIVE_ARC_PUBLIC_GAME_SMOKE",
        "source_agent_sha256": sha256(AGENT_SOURCE.read_bytes()).hexdigest(),
        "source_mathematical_family": "work/arc_like_maze/window_combined.py",
        "source_original_law_count": len(module.WINDOW48),
        "source_rooted_class_count": module.ROOTED_CLASS_COUNT,
        "source_full_state_class_count": module.FULL_STATE_CLASS_COUNT,
        "game": args.game,
        "environment_provider": "official arc-agi Arcade NORMAL",
        "native_environment_actions": int(agent.action_counter),
        "returned_native_frames": len(actual),
        "last_state": str(getattr(actual[-1], "state", "UNKNOWN")) if actual else None,
        "levels_completed": int(getattr(actual[-1], "levels_completed", 0)) if actual else 0,
        "per_response": rows,
        "stopped_at_mathematical_or_interface_wall": bool(agent.stopped_at_wall),
        "window48_evidence": None if evidence is None else {
            "provisional_native_actions": list(evidence.native_actions),
            "status": evidence.report().status,
            "remaining_source_law_indices": list(evidence.candidates),
            "remaining_original_window_parameters": [
                list(module.WINDOW48[i]) for i in evidence.candidates],
            "remaining_rooted_class_keys": [
                list(x) for x in evidence.report().rooted_class_keys],
            "source_full_state_classes_not_inferred_from_rooted_evidence": 14,
            "native_rooted_action_word_frame_hashes": {
                word: key.hex() for word, key in evidence.words.items()
            },
            "observed_visible_distinctions": evidence.visible_distinctions,
            "observed_visible_equalities": evidence.visible_collisions,
        },
        "boundary": (
            "The official native interactions test a PROVISIONAL pairing "
            "of two advertised simple controls only. No native-F3 state "
            "correspondence has been established; all native pixels remain "
            "unchanged and full-state versus origin-preserving mathematical "
            "conjugacy remain distinct. No competition win is claimed."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    # Preserve raw frame arrays for independent pixel recheck, not only hashes.
    frames = []
    for f in actual:
        a = np.asarray(getattr(f, "frame", ()))
        if a.size == 64 * 64:
            frames.append(a.reshape(-1,64,64)[-1].astype(np.uint8))
    if frames:
        np.savez_compressed(args.out.with_suffix(".npz"), *frames)
    print("WINDOW48_NATIVE_RESULT " + json.dumps({
        "source_sha256": result["source_agent_sha256"],
        "game": result["game"],
        "native_environment_actions": result["native_environment_actions"],
        "levels_completed": result["levels_completed"],
        "state": result["last_state"],
        "window48_evidence": result["window48_evidence"],
        "stopped_at_wall": result["stopped_at_mathematical_or_interface_wall"],
        "manifest": str(args.out),
        "raw_frames": str(args.out.with_suffix(".npz")) if frames else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
