"""Predeclared independent SP80 native frontier-width falsification.

Prior real public SP80 frontier experiment #39207477345 established
98/98 first-native-14 frontier advances and row progress of width 1/2,
but did not predict the width. Two SIMPLE fallible hypotheses are frozen
before this new independent 17-action sequence sample:

  X3: width=1 iff the pre-action frontier x is 0 mod 3, else width=2.
  ALT: width alternates 1/2 using the actual PREVIOUS native action's
       observed width; only root x=0 gets width=1 without predecessor.
  ONE: negative-control prediction of width=1 always.

X3 and ALT already have historical counterexamples and are NOT claimed
exact. Compare complete row-63 native changes to the original old clock
and the full frozen stage0->stage1 model, preserving every error.
No change to source 48 F3 laws or canonical ARC agent.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
import numpy as np

from .native_sp80_frozen_color_contexts import steps_on_real_game
from .native_sp80_frontier_probe import analyze_pair, count_results

WORDS = (
    "44444444444444444",
    "44444544444444444",
    "45444445444445444",
    "54444454444454444",
    "44554444455444444",
    "55544444445554444",
)
RESETS = 2
assert len(WORDS) == len(set(WORDS)) == 6
assert all(len(w) == 17 and set(w) <= {"4", "5"} for w in WORDS)


def width_candidates(x, previous_width):
    """Before-action values ONLY: pre-frame x + prior native observation."""
    return {
        "X3_frontier_coordinate": 1 if x % 3 == 0 else 2,
        "ALT_previous_observed_width": (
            1 if x == 0 and previous_width is None else
            1 if previous_width == 2 else
            2 if previous_width == 1 else None
        ),
        "ONE_negative_control": 1,
    }


def score_row(pre, observed, frontier_x, width):
    if width is None or frontier_x < 0 or frontier_x + width > 64:
        return {"admissible": False, "reason": "NO_PRE_ACTION_WIDTH_OR_BOUNDS"}
    if not np.all(pre[63, :frontier_x] == 0):
        return {"admissible": False, "reason": "NONZERO_NATIVE_PREFIX"}
    if not np.all(pre[63, frontier_x:frontier_x+width] == 14):
        return {"admissible": False, "reason": "PRE_NATIVE_CELLS_NOT_14"}
    expected = {(x, 63): (14, 0)
                for x in range(frontier_x, frontier_x + width)}
    exact = expected == observed
    return {
        "admissible": True, "predicted_width": width, "exact": exact,
        "missing": [
            {"xy": list(p), "native_colors": list(observed[p])}
            for p in sorted(set(observed) - set(expected))
        ],
        "extra": [
            {"xy": list(p), "native_colors": list(expected[p])}
            for p in sorted(set(expected) - set(observed))
        ],
        "wrong_color": [
            {"xy": list(p), "predicted": list(expected[p]),
             "observed": list(observed[p])}
            for p in sorted(set(observed) & set(expected))
            if observed[p] != expected[p]
        ],
    }


def append_independent_width_evidence(entries, level1_frames, root_index):
    previous_width = None
    previous_step = 0
    for row in entries:
        step = row["word_step"]
        # An interruption/omission cannot furnish a predecessor width.
        if step != previous_step + 1:
            previous_width = None
        idx = root_index + step - 1
        pre = level1_frames[idx]
        d = row["frontier_test"]
        x = int(d["pre_frontier_x"])
        observed = {(int(r["xy"][0]), int(r["xy"][1])):
                    (int(r["old"]), int(r["new"]))
                    for r in d["observed_native_row63_changes"]}
        variants = width_candidates(x, previous_width)
        row["width_predictions"] = {
            name: score_row(pre, observed, x, width)
            for name, width in variants.items()
        }
        row["width_inputs"] = {
            "native_pre_action_frontier_x": x,
            "previous_observed_native_width": previous_width,
            "current_action": row["actual_action"],
            "native_pre_action_frontier_first_two":
                [int(t) for t in pre[63, x:min(64,x+2)]],
        }
        # Previous observation is available to the *next* prediction only.
        delta = int(d["post_frontier_x"]) - x
        previous_width = delta if d["contiguous_1_or_2_cell_progress"] and delta in (1,2) else None
        previous_step = step


def summarize(trials):
    stats = {}
    previous = Counter()
    for t in trials:
        for row in t["admitted_stage1_actions"]:
            previous["all_stage1_admitted"] += 1
            previous["ACTION" + str(row["actual_action"])] += 1
            previous["observed_1_or_2_frontier"] += int(
                bool(row["frontier_test"]["contiguous_1_or_2_cell_progress"]))
            previous["old_clock_exact"] += int(
                row["frontier_test"]["old_absolute_clock_row_exact"])
            for name, rec in row["width_predictions"].items():
                bucket = stats.setdefault(name, Counter())
                if not rec["admissible"]:
                    bucket["unknown"] += 1
                else:
                    bucket["admitted"] += 1
                    bucket["exact"] += int(rec["exact"])
                    bucket["missing"] += len(rec["missing"])
                    bucket["extra"] += len(rec["extra"])
                    bucket["wrong_color"] += len(rec["wrong_color"])
    return {
        "native_frontier_observations": dict(previous),
        "width_hypotheses": {k: dict(v) for k, v in stats.items()},
        "full_stage_transfer": count_results(trials)["models"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials, arrays = [], {}
    for word in WORDS:
        for replicate in range(RESETS):
            records, frames = {}, {}
            for level in (0, 1):
                records[level], frames[level] = steps_on_real_game(
                    arcade, word, level, replicate)
                arrays[f"{word}_{replicate}_{level}"] = frames[level]
            admitted, omitted = analyze_pair(word, replicate, records, frames)
            if records[1]["stage_root_index"] is not None:
                append_independent_width_evidence(
                    admitted, frames[1], records[1]["stage_root_index"])
            trials.append({
                "word": word, "replicate": replicate,
                "native_records": records,
                "admitted_stage1_actions": admitted,
                "omitted_steps": omitted,
                "native_actions": sum(r["real_native_actions"]
                                      for r in records.values()),
            })
    result = {
        "kind": "SP80_ORIGINAL_NATIVE_HELDOUT_FRONTIER_WIDTH",
        "frozen_predeclared_words": WORDS,
        "resets_per_word_per_level": RESETS,
        "native_resets": 2 * len(trials),
        "actual_native_actions": sum(t["native_actions"] for t in trials),
        "hypotheses": "X3(x%3==0 => 1, else 2); ALT(root 1, else alternate previous genuine width); ONE(always 1) negative control",
        "metrics": summarize(trials),
        "trials": trials,
        "boundary": "All width predictions read only original pre-action pixels, native action ID and permitted previous observed width. Current outcome never enters its own prediction. Native level changes/interrupted steps remain UNKNOWN. 48-law F3 mathematics and canonical agent unchanged; no autonomous policy, native F3 mapping or game win.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **arrays)
    print("SP80_WIDTH_HELDOUT " + json.dumps({
        k: v for k, v in result.items() if k != "trials"}, sort_keys=True))
    if result["metrics"]["native_frontier_observations"].get("all_stage1_admitted", 0) == 0:
        raise RuntimeError("No actual native stage1 original-game comparisons")
    if not result["metrics"]["full_stage_transfer"]:
        raise RuntimeError("No original native stage0-stage1 ACTION4 comparisons")


if __name__ == "__main__":
    main()
