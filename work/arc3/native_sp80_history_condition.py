"""Predeclared position-only falsification; not a native mechanism or solver.

Before collecting this run: remove predicted native (9,12) changes at
context steps >=7. Keep earlier geometry, border and pre-color baseline.
New words deliberately place ACTION4 at steps 6/7/8 with ACTION5 history.
Two fresh level pairs per word. A mismatch refutes sufficiency on that
observed state. Interrupted comparisons remain UNKNOWN. No F3 changes.
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
    FROZEN_MAPS, steps_on_real_game, changed_triplets,
)
from .native_sp80_boundary_prediction import projected_with_frozen_boundary, score
from .native_sp80_occupancy_gate import gate_using_target_pre_state
from .native_sp80_occupancy_long_history import evaluate_pair

WORDS = ("55555544", "55555444", "44555544", "55445544")
RESETS = 2
CONDITION_DESCRIPTION = "suppress predicted native 9->12 at context step >=7"


def condition(predicted, step):
    return {p: colors for p, colors in predicted.items()
            if not (step >= 7 and colors == (9, 12))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    raw, trials, counters = {}, [], {}
    for word in WORDS:
        for replicate in range(RESETS):
            records, frames = {}, {}
            for level in (0, 1):
                records[level], frames[level] = steps_on_real_game(
                    arcade, word, level, replicate)
                raw[f"{word}_{replicate}_{level}"] = frames[level]
            admitted, omissions = evaluate_pair(
                records[0], records[1], frames[0], frames[1])
            rows = []
            for step in admitted:
                index = step["word_step"] - 1
                i0 = records[0]["stage_root_index"] + index
                i1 = records[1]["stage_root_index"] + index
                source = changed_triplets(frames[0][i0], frames[0][i0+1])
                actual = changed_triplets(frames[1][i1], frames[1][i1+1])
                for rule in FROZEN_MAPS:
                    predicted, _, _ = projected_with_frozen_boundary(
                        source, rule, index+1)
                    baseline, _ = gate_using_target_pre_state(
                        predicted, frames[1][i1])
                    candidate = condition(baseline, index+1)
                    scores = {"baseline": score(baseline, actual),
                              "candidate_condition": score(candidate, actual)}
                    rows.append({"step": index+1, "model": rule[0],
                                 "removed": len(baseline)-len(candidate),
                                 "scores": scores})
                    for variant, measured in scores.items():
                        key = rule[0] + "/" + variant
                        total = counters.setdefault(key, Counter())
                        total["comparisons"] += 1
                        total["exact"] += int(measured[
                            "complete_exact_native_pixel_color_changes"])
                        total["extra"] += len(measured["false_positive_native_changes"])
                        total["missed"] += len(measured["missing_native_changes"])
                        total["wrong_colors"] += len(measured[
                            "same_position_but_different_native_colors"])
            trials.append({"word": word, "replicate": replicate,
                           "native_records": records, "omissions": omissions,
                           "comparisons": rows})
    result = {
        "kind": "SP80_PREDECLARED_CONDITION",
        "condition": CONDITION_DESCRIPTION,
        "predeclared_words": WORDS, "resets_per_word_per_level": RESETS,
        "native_resets": len(trials)*2,
        "native_actions": sum(r["real_native_actions"] for t in trials
                              for r in t["native_records"].values()),
        "summary": counters, "trials": trials,
        "limits": "Conditioned stage transfer, not autonomous prediction, F3 mapping or game win.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **raw)
    print("SP80_HISTORY_CONDITION " + json.dumps({k: v for k, v in result.items()
                                                 if k != "trials"}))
    if not counters:
        raise RuntimeError("No comparable native transitions; result remains UNKNOWN")


if __name__ == "__main__":
    main()
