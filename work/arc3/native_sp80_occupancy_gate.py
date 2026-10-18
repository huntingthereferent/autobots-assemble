"""SP80 official native ARC: blind test of target pre-color occupancy gating.

PREVIOUS (actual public native SP80):
- Frozen level0->level1 geometry T = shift(+8,+20), R = reflect_y+shift(+8,-8).
- Empirical ACTION4 boundary changes: native 14->0 on y=63 by word step.
- In five heldout words both predictions covered 1070/1070 native changes,
  BUT 20 spurious projected 14->0 changes occurred near x=61..63.
- No native/F3 correspondence, no complete game win.

PREDECLARED NEW NECESSARY PRE-STATE CONDITION (NOT FITTED):
A native (before_color, after_color) prediction at target pixel (x,y)
is admissible ONLY IF the actual target-stage frame BEFORE acting has
before_color at (x,y), AND before_color differs from after_color.
This uses ONLY the actual target PRE-action pixels, never the result
after acting. It is not an independent prediction from a source frame.

Test this occupancy gate on six NEW length-six native words, each at actual
level 0 and actual level 1 after witnessed native prefix 454545, twice per
word. Preserve the OLD ungated prediction as a preregistered comparator.
Report whether eliminated extra predictions were merely already-zero vs
were 14->0 attempts blocked despite native color14 present.

No change to original 48 F3 window math, canonical agent, or game engine.
No pretending visible state is hidden-state identity or predicting wins.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode

from .native_sp80_frozen_color_contexts import (
    GAME, FROZEN_MAPS, steps_on_real_game, changed_triplets,
)
from .native_sp80_boundary_prediction import (
    projected_with_frozen_boundary, score,
)

# Fixed before any NEW real native data; none were in the previous five words.
NEW_CONTEXT_WORDS = (
    "444444", "445444", "554444", "455444", "545454", "544554",
)
RESETS_PER_WORD = 2


def gate_using_target_pre_state(predicted, native_before):
    """Check ONLY actual BEFORE-state native colors, not observed action effect."""
    retained = {}
    excluded = []
    for (x, y), (from_color, to_color) in sorted(predicted.items()):
        before = int(native_before[y, x])
        if before == from_color and from_color != to_color:
            retained[(x, y)] = (from_color, to_color)
        else:
            reason = (
                "ALREADY_AT_EXPECTED_NEW_COLOR" if before == to_color
                else "DIFFERENT_NATIVE_PRE_COLOR"
            )
            excluded.append({
                "xy": [x, y], "predicted": [from_color, to_color],
                "actual_pre_action_color": before, "reason": reason,
            })
    return retained, excluded


def native_action_context(arcade, word, replicate):
    trial = {}
    arrays = {}
    for level in (0, 1):
        record, frames = steps_on_real_game(arcade, word, level, replicate)
        trial[level] = record
        arrays[level] = frames
    complete = trial[0]["complete"] and trial[1]["complete"]
    row = {
        "word": word, "reset": replicate,
        "complete_pair": complete,
        "level0_status": trial[0]["status"],
        "level1_status": trial[1]["status"],
        "level1_start_hash": trial[1]["stage_root_hash"],
        "actual_native_actions": sum(
            rec["real_native_actions"] for rec in trial.values()),
        "action4_evaluations": [],
    }
    if not complete:
        return row, arrays

    a, b = arrays[0], arrays[1]
    start0, start1 = trial[0]["stage_root_index"], trial[1]["stage_root_index"]
    for j, action in enumerate(word):
        if action != "4":
            continue
        source = changed_triplets(a[start0+j], a[start0+j+1])
        native_before = b[start1+j]
        target = changed_triplets(native_before, b[start1+j+1])
        comparisons = []
        for rule in FROZEN_MAPS:
            original, clipped, conflicts = projected_with_frozen_boundary(
                source, rule, j+1)
            gated, excluded = gate_using_target_pre_state(
                original, native_before)
            ungated_quality = score(original, target)
            gated_quality = score(gated, target)
            original_fp = {
                tuple(p["xy"]) for p in ungated_quality[
                    "false_positive_native_changes"]
            }
            excluded_coord = {tuple(x["xy"]) for x in excluded}
            comparisons.append({
                "model": rule[0],
                "frozen_geometry": [rule[1], rule[2], rule[3]],
                "word_step": j+1,
                "original_model": ungated_quality,
                "pre_color_gate_model": gated_quality,
                "pre_color_gate_exclusions": excluded,
                "removed_ungated_false_positives":len(
                    excluded_coord & original_fp),
                "removed_ungated_true_positives":len(
                    excluded_coord - original_fp),
                "clipped_source_count":len(clipped),
                "boundary_prediction_collisions":conflicts,
                "ungated_false_positives_before_colors": [
                    {
                        "xy": p["xy"],
                        "expected_from_to": p["predicted"],
                        "actual_pre_color": int(
                            native_before[p["xy"][1], p["xy"][0]]),
                    }
                    for p in ungated_quality["false_positive_native_changes"]
                ],
            })
        row["action4_evaluations"].append({
            "word_step":j+1, "action":4,
            "native_target_frame_before_hash":trial[1][
                "transition_records"][
                (len("454545")+j)]["before_hash"],
            "source_changes":len(source), "native_target_changes":len(target),
            "models":comparisons,
        })
    return row, arrays


def aggregate(trials, model):
    items = [m for trial in trials
             for event in trial["action4_evaluations"]
             for m in event["models"] if m["model"] == model]
    def metric(key):
        return sum(len(m[key]) if isinstance(m[key],list) else m[key]
                   for m in items)
    return {
        "actual_NATIVE_ACTION4_effects":len(items),
        "exact_full_changes_before_gating":sum(
            m["original_model"]["complete_exact_native_pixel_color_changes"]
            for m in items),
        "exact_full_changes_after_gating":sum(
            m["pre_color_gate_model"]["complete_exact_native_pixel_color_changes"]
            for m in items),
        "native_actual_changes":sum(
            m["original_model"]["native_changed_observed_count"] for m in items),
        "native_actual_changes_matched_before":sum(
            m["original_model"]["exact_native_color_pair_matches"] for m in items),
        "native_actual_changes_matched_after":sum(
            m["pre_color_gate_model"]["exact_native_color_pair_matches"] for m in items),
        "ungated_false_positive_count":sum(
            len(m["original_model"]["false_positive_native_changes"])
            for m in items),
        "gated_false_positive_count":sum(
            len(m["pre_color_gate_model"]["false_positive_native_changes"])
            for m in items),
        "gated_false_negative_count":sum(
            len(m["pre_color_gate_model"]["missing_native_changes"])
            for m in items),
        "gated_wrong_native_color_count":sum(
            len(m["pre_color_gate_model"]["same_position_but_different_native_colors"])
            for m in items),
        "removed_false_predictions":sum(
            m["removed_ungated_false_positives"] for m in items),
        "incorrectly_removed_actual_changes":sum(
            m["removed_ungated_true_positives"] for m in items),
        "occupancy_gate_exclusion_reasons":dict(Counter(
            x["reason"] for m in items
            for x in m["pre_color_gate_exclusions"])),
        "pre_action_native_color_of_all_ungated_false_positives":dict(
            sorted(Counter(
                x["actual_pre_color"] for m in items
                for x in m["ungated_false_positives_before_colors"]
            ).items())),
        "ungated_false_positives_expected_native_from_to":[
            {"from_color":int(pair[0]),"to_color":int(pair[1]),
             "occurrences":int(n)}
            for pair,n in sorted(Counter(
                tuple(x["expected_from_to"]) for m in items
                for x in m["ungated_false_positives_before_colors"]
            ).items())
        ],

        "remaining_gated_false_positives_with_actual_pre_colors":[
            {"word":row["word"],"reset":row["reset"],
             "action_step":effect["word_step"],
             "xy":p["xy"],"expected_from_to":p["predicted"],
             "actual_pre_color": next(
                 (x["actual_pre_color"] for x in m[
                     "ungated_false_positives_before_colors"]
                  if x["xy"]==p["xy"]),None)}
            for row in trials for effect in row["action4_evaluations"]
            for m in effect["models"] if m["model"]==model
            for p in m["pre_color_gate_model"]["false_positive_native_changes"]
        ][:100],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-native-color-occupancy-gate.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials=[]
    raw={}
    for word in NEW_CONTEXT_WORDS:
        for reset in range(RESETS_PER_WORD):
            record, frames=native_action_context(arcade,word,reset)
            trials.append(record)
            for level, arr in frames.items():
                raw[f"{word}_reset{reset}_level{level}"]=arr
    result={
        "kind":"SP80_NATIVE_TARGET_PRE_COLOR_OCCUPANCY_BLIND_TEST",
        "official_environment":"arc-agi Arcade NORMAL public sp80",
        "new_words_predeclared":list(NEW_CONTEXT_WORDS),
        "fresh_resets_per_word_per_level":RESETS_PER_WORD,
        "native_action_count":sum(x["actual_native_actions"] for x in trials),
        "independent_root_pairs":len(trials),
        "complete_root_pairs":sum(x["complete_pair"] for x in trials),
        "frozen_models":[
            {"name":name,"symmetry":kind,"dx":dx,"dy":dy}
            for name,kind,dx,dy in FROZEN_MAPS],
        "frozen_boundary_hypothesis":"same native 14->0 y63 step-index rule",
        "new_pre_color_occupancy_gate":(
            "at a predicted native target position, accept predicted "
            "(from_color,to_color) ONLY when the observed level-1 "
            "PRE-action pixel equals from_color and from_color!=to_color; "
            "never consult post-action pixels to gate the prediction."),
        "model_aggregates":{
            name:aggregate(trials,name)
            for name,_,_,_ in FROZEN_MAPS},
        "all_native_evidence":trials,
        "boundary":(
            "Compares conditional prediction given both real level0 "
            "effect and real level1 pre-action board, NOT autonomous "
            "future action prediction. Same public SP80, not unseen "
            "ARC generalization. Does not identify native F3 A/B, "
            "prove 48-law rooted/full-state conjugacy, or solve ARC. "
            "Every false positive, missing change, and native-color "
            "disagreement retained. No fitted coordinate rules added."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    if raw:
        np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_NATIVE_OCCUPANCY_GATE "+json.dumps({
        "fresh_real_native_resets":len(trials)*2,
        "native_actions":result["native_action_count"],
        "root_pairs":len(trials),
        "complete_pairs":result["complete_root_pairs"],
        "models":result["model_aggregates"],
        "incomplete":[
            {"word":t["word"],"reset":t["reset"],
             "level0_status":t["level0_status"],
             "level1_status":t["level1_status"]}
            for t in trials if not t["complete_pair"]],
        "record":str(args.out),"raw":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if result["complete_root_pairs"]==0:
        raise RuntimeError("native occupancy comparison produced zero complete trials")


if __name__=="__main__":
    main()
