"""Predeclared native SP80 frontier test, independent of old timing fit.

Read the genuine stage-1 *pre-action* row-63 frontier BEFORE each original
ACTION4/ACTION5. Hypothesis: its leftmost uncleared native 14 pixel
changes to 0 at every admitted stage-1 action, with an intact contiguous
zero prefix and an observed 1- or 2-cell frontier advance. This is
a minimal falsifiable predictor, not a full native state prediction.
Never derive a prediction from the after-frame.

Four frozen controls stay separate: previously frozen spatial/timing
condition, unaltered geometry/occupancy baseline, original absolute
step-clock boundary, and identity negative control.
Words / resets are fixed before observing any frames of this new run.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
import numpy as np

from .native_sp80_frozen_color_contexts import (
    FROZEN_MAPS, changed_triplets, steps_on_real_game
)
from .native_sp80_boundary_prediction import (
    boundary_positions, projected_with_frozen_boundary, score
)
from .native_sp80_occupancy_gate import gate_using_target_pre_state
from .native_sp80_boundary_timing import boundary_condition

WORDS = (
    "4444444444444",  # continued 4 trajectory
    "5555555555555",  # ACTION5 negative-control trajectory
    "4455454544454",  # changed 4/5 ordering
    "5544554455445",  # different 5 density
    "4544545545454",  # changes before and after step 10
)
RESETS = 2
PREFIX_LEN = 6
assert len(WORDS) == len(set(WORDS)) == 5
assert all(len(w) == 13 and set(w) <= {"4", "5"} for w in WORDS)


def frontier_index(row):
    # Raw native values; no palette mapping or fitted transformation.
    return next((x for x, c in enumerate(row) if int(c) != 0), len(row))


def observe_frontier(before, after, step):
    """Predict from pre-frame, then evaluate against original native after-frame."""
    row_before = before[63]
    row_after = after[63]
    x = frontier_index(row_before)
    color = int(row_before[x]) if x < 64 else None
    # UNKNOWN/nonapplicable if no valid 14 frontier.
    prediction = {(x, 63): (14, 0)} if color == 14 else {}
    observed = {p: colors for p, colors in changed_triplets(before, after).items()
                if p[1] == 63}
    y = frontier_index(row_after)
    before_prefix = all(int(c) == 0 for c in row_before[:x])
    after_prefix = all(int(c) == 0 for c in row_after[:y])
    frontier_cells = [(i, 63) for i in range(x, y)] if y >= x else []
    exact_frontier_run = (
        bool(prediction) and before_prefix and after_prefix and y - x in (1, 2)
        and observed == {p: (14, 0) for p in frontier_cells}
    )
    # The frozen old clock is compared with the same exact row-change map.
    old_clock = {(px, py): (14, 0) for px, py in boundary_positions(step)
                 if int(before[py, px]) == 14}
    return {
        "pre_frontier_x": x,
        "post_frontier_x": y,
        "pre_frontier_native_color": color,
        "pre_zero_prefix": before_prefix,
        "post_zero_prefix": after_prefix,
        "predicted_minimum_native_change": [
            {"xy": [px, py], "old": pair[0], "new": pair[1]}
            for (px, py), pair in sorted(prediction.items())
        ],
        "observed_native_row63_changes": [
            {"xy": [px, py], "old": pair[0], "new": pair[1]}
            for (px, py), pair in sorted(observed.items())
        ],
        "frontier_14_to_0_minimum_hit": (
            prediction and all(observed.get(p) == v
                               for p, v in prediction.items())
        ) if prediction else None,
        "contiguous_1_or_2_cell_progress": exact_frontier_run if prediction else None,
        "old_absolute_clock_row_exact": old_clock == observed,
        "old_clock_expected_positions": [list(p) for p in sorted(old_clock)],
        "row_change_count": len(observed),
    }


def analyze_pair(word, replicate, records, frames):
    src_record, dst_record = records[0], records[1]
    src_frames, dst_frames = frames[0], frames[1]
    sr = src_record["stage_root_index"]
    tr = dst_record["stage_root_index"]
    admitted = []
    omissions = Counter()
    if tr is None:
        return admitted, {"NO_ACTUAL_NATIVE_STAGE1_ENTRY": len(word)}
    for idx, letter in enumerate(word):
        step = idx + 1
        ti = tr + idx
        if len(dst_frames) <= ti + 1 or len(dst_record["transition_records"]) <= PREFIX_LEN + idx:
            omissions["NATIVE_STAGE1_STEP_UNAVAILABLE"] += 1
            continue
        td = dst_record["transition_records"][PREFIX_LEN + idx]
        if td["action"] != int(letter) or td["level"] != 1:
            omissions["NATIVE_STAGE1_LEVEL_OR_ACTION_MISMATCH"] += 1
            continue
        before, after = dst_frames[ti], dst_frames[ti + 1]
        frontier = observe_frontier(before, after, step)
        row = {
            "word": word, "replicate": replicate, "word_step": step,
            "actual_action": int(letter), "native_level": td["level"],
            "native_before_hash": td["before_hash"],
            "native_after_hash": td["after_hash"],
            "frontier_test": frontier,
            "stage0_to_stage1_ACTION4_comparison": None,
        }
        if letter == "4":
            si = (sr + idx) if sr is not None else -1
            if (sr is None or len(src_frames) <= si + 1
                    or len(src_record["transition_records"]) <= idx):
                omissions["STAGE0_ACTION4_UNAVAILABLE"] += 1
            else:
                ts = src_record["transition_records"][idx]
                if ts["action"] != 4 or ts["level"] != 0:
                    omissions["STAGE0_LEVEL_OR_ACTION_MISMATCH"] += 1
                else:
                    source = changed_triplets(src_frames[si], src_frames[si + 1])
                    actual = changed_triplets(before, after)
                    comparisons = {}
                    for rule in FROZEN_MAPS:
                        name = rule[0]
                        projected, _, _ = projected_with_frozen_boundary(source, rule, step)
                        baseline, _ = gate_using_target_pre_state(projected, before)
                        frozen_candidate = boundary_condition(baseline, step)
                        comparisons[name] = {
                            "baseline": score(baseline, actual),
                            "frozen_11step_candidate": score(frozen_candidate, actual),
                        }
                    row["stage0_to_stage1_ACTION4_comparison"] = comparisons
        admitted.append(row)
    return admitted, dict(omissions)


def count_results(trials):
    summary = {"frontier": dict(Counter()), "models": {}}
    f = Counter()
    models = {}
    for trial in trials:
        for entry in trial["admitted_stage1_actions"]:
            datum = entry["frontier_test"]
            f["admitted_actions"] += 1
            f["ACTION_" + str(entry["actual_action"])] += 1
            if datum["frontier_14_to_0_minimum_hit"] is not None:
                f["frontier_prediction_admissible"] += 1
                f["frontier_minimum_hit"] += int(datum["frontier_14_to_0_minimum_hit"])
                f["contiguous_1_or_2_cell_progress"] += int(
                    datum["contiguous_1_or_2_cell_progress"])
                f["old_clock_row_exact"] += int(datum["old_absolute_clock_row_exact"])
                if not datum["contiguous_1_or_2_cell_progress"]:
                    f["frontier_counterexamples"] += 1
            record = entry["stage0_to_stage1_ACTION4_comparison"]
            if record is None:
                continue
            for name, measured in record.items():
                for variant, scorecard in measured.items():
                    stats = models.setdefault(name + "/" + variant, Counter())
                    stats["admitted_effects"] += 1
                    stats["exact"] += int(scorecard[
                        "complete_exact_native_pixel_color_changes"])
                    stats["extra"] += len(scorecard["false_positive_native_changes"])
                    stats["missed"] += len(scorecard["missing_native_changes"])
                    stats["wrong_colors"] += len(scorecard[
                        "same_position_but_different_native_colors"])
    summary["frontier"] = dict(f)
    summary["models"] = {k: dict(v) for k, v in models.items()}
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials, raw = [], {}
    for word in WORDS:
        for replicate in range(RESETS):
            records, frames = {}, {}
            for level in (0, 1):
                records[level], frames[level] = steps_on_real_game(
                    arcade, word, level, replicate)
                raw[f"{word}_{replicate}_{level}"] = frames[level]
            evidence, omissions = analyze_pair(word, replicate, records, frames)
            trials.append({
                "word": word, "replicate": replicate,
                "source_record": records[0], "target_record": records[1],
                "native_actions": sum(r["real_native_actions"] for r in records.values()),
                "admitted_stage1_actions": evidence,
                "omitted_steps": omissions,
            })
    summary = count_results(trials)
    result = {
        "kind": "SP80_ORIGINAL_NATIVE_PRE_ACTION_FRONTIER_FALSIFICATION",
        "hypothesis": "Before genuine level1 ACTION4/5, the leftmost uncleared"
                      " row63 native 14 changes to 0, and the frontier advances"
                      " one or two contiguous native 14->0 pixels.",
        "words_predeclared": WORDS, "replicates_per_word_per_stage": RESETS,
        "fresh_native_resets": len(trials) * 2,
        "real_native_actions": sum(x["native_actions"] for x in trials),
        "summary": summary, "trials": trials,
        "limits": "Pre-action visible frontier hypothesis only; native ARC public "
                  "SP80, not an autonomous policy, hidden-state mechanism, F3 mapping "
                  "or game win. Unknown steps are excluded, never counted as negative.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **raw)
    print("SP80_FRONTIER_PROBE " + json.dumps({k: v for k, v in result.items()
                                            if k != "trials"}, sort_keys=True))
    if summary["frontier"].get("frontier_prediction_admissible", 0) == 0:
        raise RuntimeError("No admissible original native stage1 frontier observations")
    if not summary["models"]:
        raise RuntimeError("No matched native ACTION4 comparisons")


if __name__ == "__main__":
    main()
