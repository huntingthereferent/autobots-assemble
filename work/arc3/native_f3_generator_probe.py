"""Independent native A^3 equality probe for all advertised simple ARC controls.

Tests a necessary order-three relationship of the ORIGINAL F3 A operator.
It cannot infer hidden-state equality from equal frames or rule out nonlinear
observation correspondences; it is a counterexample check for direct mappings.
"""
from __future__ import annotations

import argparse
from hashlib import blake2b
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction


def frame_bytes(obs) -> bytes:
    a = np.asarray(obs.frame)
    if a.ndim == 3:
        a = a[-1]
    if a.size != 4096:
        raise ValueError("native frame unexpectedly not 64x64")
    g = a.reshape(64,64)
    if np.any(g < 0) or np.any(g > 15):
        raise ValueError("native frame contains unsupported colors")
    return g.astype(np.uint8).tobytes()


def compact(obs) -> dict:
    b = frame_bytes(obs)
    return {
        "hash": blake2b(b, digest_size=16).hexdigest(),
        "levels_completed": int(getattr(obs, "levels_completed", 0)),
        "state": str(getattr(obs, "state", "UNKNOWN")),
        "available": [int(getattr(a,"value",a)) for a in
                      (getattr(obs,"available_actions",[]) or [])],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--game", default="ls20")
    p.add_argument("--out", type=Path, default=Path("runtime/data/arc3/f3-generator-probe.json"))
    args = p.parse_args()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    rows = []
    grids = {}
    for n in (1, 2, 3, 4, 5):
        env = arcade.make(args.game)
        if env is None:
            raise RuntimeError("official native ARC environment unavailable")
        initial = env.reset()
        if n not in compact(initial)["available"]:
            continue
        root = compact(initial)
        observations = [root]
        frames = [np.frombuffer(frame_bytes(initial), dtype=np.uint8).reshape(64,64)]
        action = getattr(GameAction, f"ACTION{n}")
        for step in range(3):
            observed = env.step(action)
            if observed is None or getattr(observed, "frame", None) is None:
                observations.append({"no_frame_after_action": step + 1})
                break
            observations.append(compact(observed))
            frames.append(np.frombuffer(frame_bytes(observed), dtype=np.uint8).reshape(64,64))
            if int(getattr(observed, "levels_completed", 0)) != root["levels_completed"]:
                break

        frame_test = len(observations) == 4 and all("hash" in q for q in observations)
        same_level = frame_test and all(q["levels_completed"] == root["levels_completed"] for q in observations)
        root_return = bool(same_level and observations[0]["hash"] == observations[-1]["hash"])
        rows.append({
            "provisional_A_native_action": n,
            "predicted_by_original_F3": "A^3(root) = root",
            "result": (
                "VISIBLE_ROOT_RETURN_CONDITIONAL" if root_return
                else "DIRECT_F3_A_CONTRADICTED" if same_level
                else "UNKNOWN_INTERRUPTED"
            ),
            "observations": observations,
        })
        grids[f"action{n}"] = np.stack(frames)

    if not rows:
        raise RuntimeError("no simple native controls advertised")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "kind": "ARC3_NATIVE_F3_A_CUBE_DIRECT_MAPPING_TEST",
        "game": args.game,
        "mathematical_source": "work/arc_like_maze/math.py",
        "environment_provider": "official arc-agi Arcade NORMAL local game runtime",
        "independent_reset_per_candidate": True,
        "probes": rows,
        "interpretation_boundary": (
            "Distinct exact native frames after three identical controls refute a "
            "direct full-visible-state representation of that control as F3 A. "
            "Identical visible frames cannot prove identical hidden states, "
            "conjugacy, or ARC generalization. No winning routes used."
        ),
    }
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **grids)
    print("F3_GENERATOR_PROBE_RESULT " + json.dumps({
        "game": args.game,
        "results": [{ "action": row["provisional_A_native_action"],
                      "status": row["result"],
                      "frame_hashes": [o.get("hash") for o in row["observations"]]}
                    for row in rows],
        "manifest": str(args.out),
        "raw_frames": str(args.out.with_suffix(".npz")),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
