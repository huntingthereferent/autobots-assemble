"""Native public SP80 held-out test of ACTION4-specific visible saturation.

Discovery: in retained authentic 26-step stage-1 frames, the first six
ACTUAL ACTION4 uses each changed 32 native pixels outside bottom row,
all at y=36..39, whereas later ACTION4 and all ACTION5 changed zero
outside bottom row. Freeze this empirical claim before new executions.
Test cumulative ACTION4 count versus absolute word step using new
interleaved ACTION4/ACTION5 words. Preserve unknowns, original colors,
native before/after frame arrays and exact actual levels.

This is visible-state falsification, not a game win, hidden-state
explanation, or mathematical F3 action identification.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
import numpy as np

from .native_sp80_frozen_color_contexts import steps_on_real_game, changed_triplets

# New original native action histories, frozen before execution.
WORDS = (
    "4444444444444444",
    "5544444444444444",
    "4445554444444444",
    "4444455544444444",
    "5454454454444444",
    "4545454545444444",
)
RESETS = 2
assert len(set(WORDS)) == 6
assert all(len(w) == 16 and set(w) <= {"4", "5"} for w in WORDS)
STAGE1_PREFIX_ACTIONS = 6
MOVING_ROWS = frozenset((36, 37, 38, 39))


def predict_nonbottom(action, ordinal4, word_step):
    return {
        "ACTION4_ORDINAL_SATURATION": (
            32 if action == 4 and ordinal4 <= 6 else 0
        ),
        "ABSOLUTE_STEP_BASELINE": (
            32 if action == 4 and word_step <= 6 else 0
        ),
        "ZERO_NEGATIVE_CONTROL": 0,
    }


def admitted_stage1_steps(word, record, frames):
    start = record["stage_root_index"]
    observations, omissions = [], Counter()
    if start is None:
        return [], {"NO_REAL_NATIVE_LEVEL1_ROOT": len(word)}
    for index, char in enumerate(word):
        word_step = index + 1
        before_index = start + index
        transition_index = STAGE1_PREFIX_ACTIONS + index
        if (len(frames) <= before_index + 1
                or len(record["transition_records"]) <= transition_index):
            omissions["NO_ADMISSIBLE_ORIGINAL_NATIVE_AFTER_FRAME"] += 1
            continue
        action = record["transition_records"][transition_index]
        if action["level"] != 1 or action["action"] != int(char):
            omissions["REAL_NATIVE_LEVEL_OR_ACTION_DISAGREEMENT"] += 1
            continue
        before, after = frames[before_index], frames[before_index + 1]
        outside = changed_triplets(before[:63], after[:63])
        bottom = {p: colors for p, colors in changed_triplets(before, after).items()
                  if p[1] == 63}
        actual_count = len(outside)
        actual_rows = sorted({p[1] for p in outside})
        ordinal4 = word[:word_step].count("4")
        predictions = predict_nonbottom(int(char), ordinal4, word_step)
        measured = {
            name: {
                "expected_nonbottom_changed_pixel_count": expected,
                "observed_nonbottom_changed_pixel_count": actual_count,
                "exact_changed_pixel_count": expected == actual_count,
                "region_36_to_39_only": set(actual_rows) <= MOVING_ROWS,
                "claimed_32_pixel_moving_zone_exact": (
                    expected != 32 or (
                        actual_count == 32 and set(actual_rows) == MOVING_ROWS
                    )
                ),
            }
            for name, expected in predictions.items()
        }
        observations.append({
            "word_step": word_step,
            "native_action_id": action["action"],
            "native_ACTION4_ordinal": ordinal4,
            "real_native_level": action["level"],
            "native_before_hash": action["before_hash"],
            "native_after_hash": action["after_hash"],
            "actual_nonbottom_changed_pixels": [
                {"xy": list(p), "old": colors[0], "new": colors[1]}
                for p, colors in sorted(outside.items())
            ],
            "actual_bottom_row_changed_pixels": [
                {"xy": list(p), "old": colors[0], "new": colors[1]}
                for p, colors in sorted(bottom.items())
            ],
            "actual_nonbottom_changed_rows": actual_rows,
            "predictions": measured,
        })
    return observations, dict(omissions)


def summary(trials):
    c = {name: Counter() for name in (
        "ACTION4_ORDINAL_SATURATION", "ABSOLUTE_STEP_BASELINE",
        "ZERO_NEGATIVE_CONTROL"
    )}
    classes = {}
    for trial in trials:
        for row in trial["admitted_native_level1_steps"]:
            action, ordinal = row["native_action_id"], row["native_ACTION4_ordinal"]
            class_key = f"ACTION{action}/ordinal4_{ordinal}"
            info = classes.setdefault(class_key, Counter())
            info["admitted"] += 1
            info["actual_nonbottom_zero"] += row["actual_nonbottom_changed_rows"] == []
            info["actual_nonbottom_32"] += len(row["actual_nonbottom_changed_pixels"]) == 32
            for name, measured in row["predictions"].items():
                a = c[name]
                a["admitted"] += 1
                a["exact"] += measured["exact_changed_pixel_count"]
                a["wrong_count"] += not measured["exact_changed_pixel_count"]
                a["wrong_32_pixel_region"] += not measured["claimed_32_pixel_moving_zone_exact"]
    return {"models": {k: dict(v) for k, v in c.items()},
            "by_actual_action_and_ACTION4_ordinal": {
                k: dict(v) for k, v in sorted(classes.items())
            }}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials, raw = [], {}
    for word in WORDS:
        for replicate in range(RESETS):
            records, frames = {}, {}
            for level in (0, 1):
                records[level], frames[level] = steps_on_real_game(
                    arcade, word, level, replicate)
                raw[f"{word}_{replicate}_{level}"] = frames[level]
            steps, omission = admitted_stage1_steps(word, records[1], frames[1])
            trials.append({
                "word": word, "replicate": replicate,
                "native_records": records,
                "native_actions": sum(x["real_native_actions"] for x in records.values()),
                "omitted_real_native_level1_steps": omission,
                "admitted_native_level1_steps": steps,
            })
    result = {
        "kind": "SP80_PREDECLARED_ACTION4_VISIBLE_SATURATION",
        "predeclared_words": WORDS,
        "native_resets": len(trials) * 2,
        "real_native_actions": sum(t["native_actions"] for t in trials),
        "summary": summary(trials),
        "trials": trials,
        "limits": "Only original visible native pixel-color transitions are tested."
                  " No hidden-state identity, solver, source-F3 law assignment or ARC win."
                  " Native interrupted/level changing steps remain UNKNOWN.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **raw)
    print("SP80_ACTION4_SATURATION " + json.dumps(
        {k: v for k, v in result.items() if k != "trials"}, sort_keys=True))
    if not result["summary"]["models"]["ACTION4_ORDINAL_SATURATION"]["admitted"]:
        raise RuntimeError("No genuine native stage1 observations admitted")


if __name__ == "__main__":
    main()
