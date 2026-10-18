"""Official native ARC suffix test for identical-looking but differently reached frames.

Predeclared source observations:
  34 = 43 and 23 = 32 on LS20 full visible frame;
  12 != 21 is a negative control.
Execute the SAME suffix from each independently reached state; compare raw
frames and observable glyph/trace masks, without replacing ARC or inventing
an F3 projection. Equal observations never prove equal hidden engine states.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np

from .native_relation_scan import grid
from .native_mixed_relation_probe import snapshot

# Must be declared BEFORE seeing this experiment's native outcomes.
PREFIX_PAIRS = (
    ("34", "43", True),
    ("23", "32", True),
    ("12", "21", False),
)
SUFFIXES = ("1", "2", "3", "4", "12", "21")


def take_word(arcade, game: str, word: str):
    """Capture every actual native transition, not a saved route or simulation."""
    env = arcade.make(game)
    if env is None:
        raise RuntimeError(f"native ARC environment {game!r} not available")
    obs = env.reset()
    if obs is None or getattr(obs, "frame", None) is None:
        raise RuntimeError("missing actual native reset frame")
    level = int(getattr(obs, "levels_completed", 0))
    frames = [grid(obs).copy()]
    states = [{"index": 0, "action": None, "levels_completed": level,
               "state": str(getattr(obs, "state", None)), "observation": snapshot(frames[0])}]
    for i, action_id in enumerate(word, 1):
        legal = {int(getattr(a, "value", a)) for a in
                 (getattr(obs, "available_actions", None) or ())}
        if int(action_id) not in legal:
            return {"word":word, "completed":False, "interruption":"action_unavailable",
                    "steps":i-1, "states":states}, frames
        obs = env.step(getattr(GameAction, "ACTION"+action_id))
        if obs is None or getattr(obs, "frame", None) is None:
            return {"word":word, "completed":False, "interruption":"frameless_terminal",
                    "steps":i, "states":states}, frames
        g = grid(obs).copy()
        frames.append(g)
        state = {"index": i, "action": int(action_id),
                 "levels_completed": int(getattr(obs, "levels_completed", 0)),
                 "state": str(getattr(obs, "state", None)), "observation":snapshot(g)}
        states.append(state)
        if state["levels_completed"] != level:
            return {"word":word, "completed":False, "interruption":"level_changed",
                    "steps":i, "states":states}, frames
    return {"word": word,"completed":True,"interruption":None,
            "steps":len(word),"states":states},frames


def outcome(left: dict, right: dict, *, boundary: int, expected_prefix_equal: bool):
    """One native continuation from one independent-reset prefix pair."""
    if not left["completed"] or not right["completed"]:
        return {"status":"UNKNOWN_INTERRUPTED", "left":left["interruption"],
                "right":right["interruption"]}
    la, ra = left["states"][boundary]["observation"],right["states"][boundary]["observation"]
    lb, rb = left["states"][-1]["observation"],right["states"][-1]["observation"]
    before = (la["whole"] == ra["whole"])
    after = (lb["whole"] == rb["whole"])
    return {
        "previously_observed_prefix_relation_reproduced": before == expected_prefix_equal,
        "observed_equal_prefix_frames":before,
        "observed_equal_suffix_frames":after,
        "observed_equal_suffix_glyph_masks":lb["glyph"]==rb["glyph"],
        "observed_equal_suffix_trace_masks":lb["trace"]==rb["trace"],
        "left_prefix_frame":la["whole"], "right_prefix_frame":ra["whole"],
        "left_after_frame":lb["whole"], "right_after_frame":rb["whole"],
        "classification": (
            "VISIBLE_EQUAL_PREFIX_SPLIT_BY_SAME_SUFFIX" if before and not after
            else "VISIBLE_EQUAL_PREFIX_PRESERVED_ONE_SUFFIX" if before and after
            else "VISIBLE_UNEQUAL_PREFIX_CONVERGED_ONE_SUFFIX" if not before and after
            else "VISIBLE_UNEQUAL_PREFIX_REMAINS_UNEQUAL"
        )
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--game",default="ls20")
    p.add_argument("--out",type=Path,default=Path("runtime/data/arc3/f3-native-suffix.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    results=[]
    raw_grids={}
    actual_actions=0
    root_hashes=set()
    for a,b,expect_equal in PREFIX_PAIRS:
        for suffix in SUFFIXES:
            left, frames_l=take_word(arcade,args.game,a+suffix)
            right,frames_r=take_word(arcade,args.game,b+suffix)
            root_hashes.update((left["states"][0]["observation"]["whole"],
                                right["states"][0]["observation"]["whole"]))
            key=f"{a}_{b}_suffix_{suffix}"
            raw_grids[key+"_a"]=np.stack(frames_l)
            raw_grids[key+"_b"]=np.stack(frames_r)
            actual_actions+=left["steps"]+right["steps"]
            result=outcome(left,right,boundary=len(a),expected_prefix_equal=expect_equal)
            results.append({"prefix_pair":[a,b],"suffix":suffix,
                            "previous_relation":"VISIBLE_EQUAL" if expect_equal else "VISIBLE_UNEQUAL",
                            "comparison":result,"native_left":left,"native_right":right})
    classification={}
    for row in results:
        status=row["comparison"]["status"] if "status" in row["comparison"] else row["comparison"]["classification"]
        classification[status]=classification.get(status,0)+1

    result={"kind":"ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION",
            "game":args.game,
            "predeclared_prefixes":PREFIX_PAIRS,"predeclared_suffixes":SUFFIXES,
            "all_runs_start_at_identical_root_frame":len(root_hashes)==1,
            "distinct_native_root_hashes":sorted(root_hashes),
            "native_actions_including_independent_repetitions":actual_actions,
            "comparisons":results,
            "classification_counts":classification,
            "meaning":"Equal full visible frames can be tested for identical next-action visible outcomes; finite suffix agreements do not prove hidden-state identity or F3 conjugacy.",
            "F3_boundary":"No 3-cycle or native-F3 generator established; original A^3 counterexamples preserved; no color values mapped modulo 3."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_grids)
    print("ARC3_NATIVE_SUFFIX_RESULT "+json.dumps({
        "game":args.game,
        "root_identical":result["all_runs_start_at_identical_root_frame"],
        "total_actions":actual_actions,
        "classification_counts":classification,
        "pairs":[{
            "prefix":r["prefix_pair"],"suffix":r["suffix"],
            "before_equal":r["comparison"].get("observed_equal_prefix_frames"),
            "after_equal":r["comparison"].get("observed_equal_suffix_frames"),
            "glyph_equal":r["comparison"].get("observed_equal_suffix_glyph_masks"),
            "trace_equal":r["comparison"].get("observed_equal_suffix_trace_masks"),
            "reproduced":r["comparison"].get("previously_observed_prefix_relation_reproduced"),
            "status":r["comparison"].get("status",r["comparison"].get("classification"))
        } for r in results],
        "json":str(args.out),"npz":str(args.out.with_suffix(".npz"))
    },sort_keys=True))


if __name__=="__main__":
    main()
