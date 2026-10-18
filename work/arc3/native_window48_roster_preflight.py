"""Source-derived F3-48 A^3 necessary-condition screen over PUBLIC NATIVE ARC games.

The original 48 CombinedWorld laws ALL require mathematical A^3(state)=state
and, at the marked root, a strict three-state orbit under A. Do not assume
any native action is A; independently reset each official native game for
each advertised simple action 1..5 and examine its exact 64x64 frames.

A changed frame after three identical native actions REFUTES a proposed
direct complete-visible-state action-preserving A mapping. A nontrivial
visible return only qualifies for further probes; it is NOT a hidden-state
identity, F3 realization or ARC solution. Native click coordinates are NOT
invented. Every exception, level transition, absence of advertised control
or incomplete observation remains UNKNOWN rather than a counterexample.

This is preflight evidence gathering, not the canonical competition policy,
ARC imitation, heuristic solver, or a claim about the complete mathematical
F3-48 family beyond its proved source requirements.
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

from work.arc_like_maze.window_combined import family


SIMPLE_NATIVE_IDS = (1, 2, 3, 4, 5)
MAX_FOLLOWUP_ACTIONS = 6


def native_grid(frame):
    a = np.asarray(frame.frame)
    if a.ndim == 3:
        a = a[-1]
    if a.size != 4096:
        raise ValueError("native frame is not complete 64x64")
    a = a.reshape(64, 64)
    if np.any(a < 0) or np.any(a > 15):
        raise ValueError("native color outside 0..15")
    return a.astype(np.uint8).copy()


def digest(frame):
    return blake2b(np.ascontiguousarray(frame).tobytes(),
                   digest_size=16).hexdigest()


def legal_ids(obs):
    return sorted({int(getattr(a, "value", a))
                   for a in (getattr(obs, "available_actions", None) or ())})


def frame_state(obs):
    return {
        "frame_hash": digest(native_grid(obs)),
        "state": str(getattr(obs, "state", None)),
        "levels_completed": int(getattr(obs, "levels_completed", 0)),
        "advertised_native_actions": legal_ids(obs),
    }


def source_order_three():
    math = family()
    if len(math) != 48:
        raise AssertionError("source F3 family is not 48")
    root = (0, 0, 0)
    for w in math:
        a = w.apply(root, "A")
        aa = w.apply(root, "AA")
        aaa = w.apply(root, "AAA")
        if (len({root, a, aa}) != 3 or aaa != root):
            raise AssertionError("source-rooted strict A^3 requirement changed")
    return {"law_count": 48, "source": "work/arc_like_maze/window_combined.py",
            "source_rooted_A_orbit": "strict period-three in every law",
            "source_full_state_A_cube": "identity (source A adds 1 mod 3)"}


def roster(arcade):
    # Discovery only. We do not query or read game implementations or
    # select games based on observed performance.
    found = []
    for info in arcade.get_environments():
        value = str(info.game_id).split("-", 1)[0]
        if value and value not in found:
            found.append(value)
    return sorted(found)


def probe(arcade, game, native_id, raw):
    row = {
        "game": game,
        "provisional_native_A": native_id,
        "interpretation": "single native control, literal complete visible frame",
        "states": [],
        "status": "UNKNOWN_NOT_STARTED",
        "native_actions": 0,
    }
    frames = []
    key = f"{game}_action{native_id}"
    try:
        env = arcade.make(game)
        if env is None:
            row["status"] = "UNKNOWN_NATIVE_GAME_MISSING"
            return row
        obs = env.reset()
        if obs is None or getattr(obs, "frame", None) is None:
            row["status"] = "UNKNOWN_NATIVE_ROOT_MISSING"
            return row
        first = native_grid(obs)
        frames.append(first)
        row["states"].append(frame_state(obs))
        root_level = row["states"][0]["levels_completed"]
        if native_id not in legal_ids(obs):
            row["status"] = "UNKNOWN_ACTION_NOT_ADVERTISED_AT_ROOT"
            return row
        for i in range(1, MAX_FOLLOWUP_ACTIONS + 1):
            if native_id not in legal_ids(obs):
                row["status"] = "UNKNOWN_ACTION_WITHDRAWN"
                row["interrupted_at_action"] = i
                break
            action = getattr(GameAction, f"ACTION{native_id}")
            obs = env.step(action)
            row["native_actions"] += 1
            if obs is None or getattr(obs, "frame", None) is None:
                row["status"] = "UNKNOWN_FRAMELESS_RESPONSE"
                break
            pixels = native_grid(obs)
            frames.append(pixels)
            item = frame_state(obs)
            row["states"].append(item)
            if item["levels_completed"] != root_level:
                row["status"] = "UNKNOWN_LEVEL_TRANSITION"
                break

            if i == 3:
                hashes = [s["frame_hash"] for s in row["states"]]
                row["root_full_frame_3_return"] = hashes[0] == hashes[3]
                row["visible_strict_3_orbit"] = (
                    len(set(hashes[:3])) == 3 and hashes[0] == hashes[3])
                if not row["root_full_frame_3_return"]:
                    row["status"] = "DIRECT_VISIBLE_A_CUBE_REFUTED"
                    break  # 3 is sufficient for a strict negative result
                if not row["visible_strict_3_orbit"]:
                    row["status"] = "VISIBLE_RETURN_DEGENERATE_NOT_A_WITNESS"
                    break  # could be stationary/period one; do not claim F3
            if i == 6:
                hashes = [s["frame_hash"] for s in row["states"]]
                row["visible_second_three_step_return"] = (
                    hashes[0] == hashes[3] == hashes[6] and
                    hashes[1] == hashes[4] and
                    hashes[2] == hashes[5])
                row["status"] = (
                    "VISIBLE_STRICT_THREE_CYCLE_CANDIDATE_TWO_ORBITS"
                    if row["visible_second_three_step_return"]
                    else "VISIBLE_THREE_RETURN_NOT_REPEATED")
        else:
            if row["status"] == "UNKNOWN_NOT_STARTED":
                row["status"] = "UNKNOWN_NO_CLASSIFICATION"
    except Exception as exc:
        row["status"] = "UNKNOWN_NATIVE_EXCEPTION"
        row["error_class"] = type(exc).__name__
        row["error_message"] = str(exc)[:240]
    finally:
        if frames:
            raw[key] = np.stack(frames)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(
        "runtime/data/arc3/window48-native-A3-preflight.json"))
    args = parser.parse_args()
    original = source_order_three()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    names = roster(arcade)
    if not names:
        raise RuntimeError("official public native ARC roster is empty")

    runs = []
    interfaces = []
    raw = {}
    for game in names:
        try:
            env = arcade.make(game)
            if env is None:
                interfaces.append({"game":game,"status":"UNKNOWN_NO_GAME"})
                continue
            obs = env.reset()
            if obs is None or getattr(obs,"frame",None) is None:
                interfaces.append({"game":game,"status":"UNKNOWN_NO_ROOT"})
                continue
            native = legal_ids(obs)
            frame = native_grid(obs)
            interfaces.append({
                "game":game,
                "status":"NATIVE_ROOT_OBSERVED",
                "native_advertised_actions":native,
                "native_root_hash":digest(frame),
                "simple_actions_available":[a for a in SIMPLE_NATIVE_IDS if a in native],
                "click_only_or_other_no_simple":not any(
                    a in native for a in SIMPLE_NATIVE_IDS),
            })
            raw[f"{game}_interface_root"] = frame
            for native_id in SIMPLE_NATIVE_IDS:
                if native_id in native:
                    runs.append(probe(arcade,game,native_id,raw))
        except Exception as exc:
            interfaces.append({"game":game,"status":"UNKNOWN_NATIVE_EXCEPTION",
                               "error_class":type(exc).__name__,
                               "message":str(exc)[:240]})
            continue

    counts = {}
    for x in runs:
        counts[x["status"]] = counts.get(x["status"],0)+1
    result = {
        "kind":"F3_WINDOW48_SOURCE_A3_NATIVE_ROSTER_PREFLIGHT",
        "original_math":original,
        "arcade":"official public arc-agi Arcade NORMAL",
        "roster_game_count":len(names),
        "roster_game_ids":names,
        "interface_roots":interfaces,
        "independently_reset_native_simple_action_probes":runs,
        "native_actions_issued":sum(r["native_actions"] for r in runs),
        "status_counts":counts,
        "scope":(
            "Probes only source A^3 necessary relation for single advertised "
            "native simple-action IDs in public games. Distinct frames after "
            "3 actions refute that direct visible-state mapping; equal frames "
            "are NOT hidden-state equality or source F3 correspondence. "
            "No native ACTION6 click coordinates were invented. "
            "No competition solves, hidden state, or game source inspected."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    if raw:
        np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("WINDOW48_NATIVE_A3_PREFLIGHT "+json.dumps({
        "games_in_official_roster":len(names),
        "roots_observed":sum(x["status"]=="NATIVE_ROOT_OBSERVED" for x in interfaces),
        "click_only_or_no_simple_games":[x["game"] for x in interfaces
            if x.get("click_only_or_other_no_simple")],
        "probe_count":len(runs),
        "native_environment_actions":result["native_actions_issued"],
        "status_counts":counts,
        "positive_visible_three_cycle_candidates":[{
            "game":x["game"],
            "action":x["provisional_native_A"],
            "states":x["states"],
        } for x in runs if x["status"].startswith("VISIBLE_STRICT_THREE_CYCLE")],
        "incomplete_probes":[{
            "game":x["game"],"action":x["provisional_native_A"],
            "status":x["status"],"error":x.get("error_message")
        } for x in runs if x["status"].startswith("UNKNOWN")],
        "record":str(args.out),
        "raw_native_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if not any(x["status"]=="NATIVE_ROOT_OBSERVED" for x in interfaces):
        raise RuntimeError("no native root observations produced; artifact still preserved")


if __name__=="__main__":
    main()
