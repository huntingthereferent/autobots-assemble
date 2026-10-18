"""Second native SP80 experiment: ACTION4 streak vs word-step saturation.

PREVIOUS independently observed frozen model failed at longer histories:
  56/66 exact, zero missing real color changes, 72 extra predicted changes.
On a run of eight consecutive ACTION4, step seven predicted a native
9->12 change that did not occur although target PRE-color matched.

PREDECLARED competing descriptions:
  H1: accumulated uninterrupted ACTION4 streak controls the blockage.
  H2: elapsed word position controls the blockage.
Neither may be promoted to a mechanism without discriminating evidence.

Before any observations in THIS experiment, freeze eight new words to
independently vary consecutive ACTION4 streak and absolute word position.
Carry forward EXACT original stage0->stage1 geometry, native pre-color
gate and bottom-edge rule without adjusting any predicted pixel. Paired
native frame comparisons may stop at game level changes; native actual
game levels and truncations stay explicit.

No new ARC game solver, world model or 48-law mathematical correspondence.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode

from .native_sp80_frozen_color_contexts import (
    GAME, FROZEN_MAPS, steps_on_real_game,
)
from .native_sp80_occupancy_long_history import evaluate_pair, totals


PREDECLARED_WORDS = (
    "4444444",   # reaches seventh uninterrupted ACTION4
    "44444544",  # ACTION5 after five ACTION4, then fresh pair
    "44444454",  # break after six consecutive ACTION4
    "54444444",  # delay start, then seven consecutive ACTION4
    "45444444",  # initial 4,5 then six consecutive ACTION4
    "45544444",  # two ACTION5 controls before later four-streak
    "44445444",  # interrupt after four ACTION4
    "545454544", # high word position but short ACTION4 streak
)
RESETS_PER_WORD = 2


def streak_at(word, index):
    if word[index]!="4":
        return 0
    n=0
    for i in range(index,-1,-1):
        if word[i]!="4":
            break
        n+=1
    return n


def native_game_levels(record):
    return {
        "native_final_observed_level":(
            record["transition_records"][-1]["level"]
            if record["transition_records"] else None),
        "native_actions_issued":record["real_native_actions"],
        "status":record["status"],
        "first_level_change_at_action":next((
            x["step"] for x in record["transition_records"]
            if (x["level"] != (0 if record["level"]==0 else (
                0 if x["step"]<=6 else 1)))
        ),None),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-action4-streak-vs-wordstep.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    observations=[]
    frames={}
    for word in PREDECLARED_WORDS:
        for reset in range(RESETS_PER_WORD):
            reports={}
            arrays={}
            for level in (0,1):
                native,raw=steps_on_real_game(arcade,word,level,reset)
                reports[level]=native
                arrays[level]=raw
                frames[f"{word}_reset{reset}_level{level}"]=raw
            measured,unknown=evaluate_pair(
                reports[0],reports[1],arrays[0],arrays[1])
            for step in measured:
                step["consecutive_ACTION4_streak"]=streak_at(
                    word,step["word_step"]-1)
                step["absolute_word_step"]=step["word_step"]
            observations.append({
                "word":word,"reset":reset,
                "real_native_actions":sum(x["real_native_actions"]
                                          for x in reports.values()),
                "level0_native_status":native_game_levels(reports[0]),
                "level1_native_status":native_game_levels(reports[1]),
                "native_level1_root_observed":reports[1][
                    "stage_root_index"] is not None,
                "comparable_ACTION4_steps":measured,
                "uncompared_steps":unknown,
                "full_pair_complete":all(x["complete"] for x in reports.values()),
            })
    grouped=defaultdict(lambda:{
        "action4_effects":0,"exact_frozen_predictions":0,
        "total_extra_predicted_changes":0,"total_missing_actual_changes":0,
        "actually_observed_change_count":0,
    })
    for row in observations:
        for step in row["comparable_ACTION4_steps"]:
            m=next(x for x in step["model_evidence"]
                   if x["model"]=="translation_only")
            q=m["gated"]
            for group in (f"streak_{step['consecutive_ACTION4_streak']}",
                          f"wordstep_{step['absolute_word_step']}"):
                x=grouped[group]
                x["action4_effects"]+=1
                x["exact_frozen_predictions"]+=int(
                    q["complete_exact_native_pixel_color_changes"])
                x["total_extra_predicted_changes"]+=len(
                    q["false_positive_native_changes"])
                x["total_missing_actual_changes"]+=len(
                    q["missing_native_changes"])
                x["actually_observed_change_count"]+=q[
                    "native_changed_observed_count"]
    totals_by_model={name:totals(observations,name)
                     for name,_,_,_ in FROZEN_MAPS}
    result={
        "kind":"SP80_NATIVE_ACTION4_STREAK_VS_ABSOLUTE_WORDSTEP",
        "environment":"official native public SP80 Arcade NORMAL",
        "previous_checkpoint":
            "WINDOW48_SP80_NATIVE_OCCUPANCY_2026-10-18.md",
        "predeclared_word_set":list(PREDECLARED_WORDS),
        "independent_native_resets_per_word_per_level":RESETS_PER_WORD,
        "actual_native_actions":sum(x["real_native_actions"] for x in observations),
        "actual_native_resets":len(observations)*2,
        "native_paired_trials":len(observations),
        "complete_native_pairs":sum(x["full_pair_complete"] for x in observations),
        "comparable_ACTION4_effects":sum(
            len(x["comparable_ACTION4_steps"]) for x in observations),
        "models":totals_by_model,
        "grouped_by_streak_and_absolute_position":dict(sorted(grouped.items())),
        "native_reset_observations":observations,
        "boundary":(
            "Two competing exploratory native-history descriptions tested "
            "without modifying geometry, occupancy or border rule. "
            "Classify observations, not game internals: identical partial "
            "visible histories do not prove hidden-state equality, "
            "causation or universal transition mechanisms. "
            "No original 48 F3 source modification, native mathematical "
            "generator role, full ARC game win or autonomous solver."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    compact_models={
        name:{k:v for k,v in info.items() if k!="first_counterexamples"}
        for name,info in totals_by_model.items()
    }
    print("SP80_STREAK_VS_WORDSTEP "+json.dumps({
        "words":list(PREDECLARED_WORDS),
        "native_actions":result["actual_native_actions"],
        "native_resets":result["actual_native_resets"],
        "complete_pairs":result["complete_native_pairs"],
        "comparable_ACTION4_effects":result["comparable_ACTION4_effects"],
        "model_summary":compact_models,
        "grouped":result["grouped_by_streak_and_absolute_position"],
        "native_level_changes":[{
            "word":r["word"],"reset":r["reset"],
            "stage0":r["level0_native_status"],
            "stage1":r["level1_native_status"],
        } for r in observations if not r["full_pair_complete"]],
        "record":str(args.out),
        "raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if result["comparable_ACTION4_effects"]==0:
        raise RuntimeError("No native effect comparisons at either history depth")


if __name__=="__main__":
    main()
