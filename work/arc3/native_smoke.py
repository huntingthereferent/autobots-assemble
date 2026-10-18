"""Run the existing F3 my_agent.py against ONE official native ARC public game.

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
    parser.add_argument("--game", default="ls20")
    parser.add_argument("--max-actions", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("runtime/data/arc3/f3-native-smoke.json"))
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
    agent = module.MyAgent(
        card_id="f3-native-smoke",
        game_id=args.game,
        agent_name=f"F3NativeSmoke.{args.game}",
        ROOT_URL="http://localhost",
        record=False,
        arc_env=env,
        tags=["f3", "native-first-run", "experimental"],
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

    evidence = agent.f3
    # The last native response has not necessarily been processed by the next
    # choose_action call. Admit it only if the same level/role context survives.
    if (evidence is not None and agent.last_letter is not None and actual
            and int(getattr(actual[-1], "levels_completed", -1)) == agent.last_level
            and rows[-1]["exact_frame_hash"] is not None):
        evidence.record(agent.last_letter, bytes.fromhex(rows[-1]["exact_frame_hash"]))
        agent.last_letter = None

    result = {
        "kind": "F3_ON_NATIVE_ARC_PUBLIC_GAME_SMOKE",
        "source_agent_sha256": sha256(AGENT_SOURCE.read_bytes()).hexdigest(),
        "mathematical_source": "work/arc_like_maze/math.py",
        "game": args.game,
        "environment_provider": "arc-agi Arcade NORMAL local native engine",
        "native_environment_actions": int(agent.action_counter),
        "returned_native_frames": len(actual),
        "last_state": str(getattr(actual[-1], "state", "UNKNOWN")) if actual else None,
        "levels_completed": int(getattr(actual[-1], "levels_completed", 0)) if actual else 0,
        "per_response": rows,
        "f3_evidence": None if evidence is None else {
            "provisional_native_generators": list(evidence.native_actions),
            "status": evidence.report().status,
            "surviving_candidate_indices": list(evidence.candidates),
            "source_phi_values": [list(module.PHIS[i]) for i in evidence.candidates],
            "rooted_action_words_and_frame_hashes": {
                word: key.hex() for word, key in evidence.words.items()
            },
            "observed_distinctions": evidence.observed_distinctions,
            "visible_equalities": evidence.visible_equalities,
            "bounds": "single rooted path, first two advertised simple actions",
        },
        "boundary": (
            "native frames and actions, but provisional F3 action-role pairing; "
            "surviving candidates do not prove ARC correspondence; no hidden-state "
            "equality or competition score claimed"
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
    print("F3_NATIVE_RESULT " + json.dumps({
        "source_sha256": result["source_agent_sha256"],
        "game": result["game"],
        "native_environment_actions": result["native_environment_actions"],
        "levels_completed": result["levels_completed"],
        "state": result["last_state"],
        "f3_evidence": result["f3_evidence"],
        "manifest": str(args.out),
        "raw_frames": str(args.out.with_suffix(".npz")) if frames else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
