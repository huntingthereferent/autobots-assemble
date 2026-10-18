"""SP80 public native: FROZEN boundary-completion prediction in new words.

From a different real native experiment (native_sp80_frozen_color_contexts):
  - Both already-frozen geometry maps perfectly explained the original
    native color transitions of 704 overlapping ACTION4 pixels.
  - Remaining 34 target changes all had native color 14 -> 0, on y=63,
    and tracked the ACTION'S POSITION in the level-1 context word.
  - Clipped source pixels also had native color 14 -> 0.
Before any NEW game action, hypothesize a residual at the bottom row:
    ACTION4 at word step 1: x=0
    step 2: x=1,2
    step 3: x=3
    step 4: x=4,5
    step 5: x=6
    step 6: x=7,8.
This is an *empirical native-action-history prediction*, not a F3 world law.

FROZEN TEST: five never-before-used native action-context words, 2 clean
resets per word per native level. For every native ACTION4, use each prior
frozen geometric map to project the native level-0 (old_color,new_color)
transition pixels to the level-1 board (dropping out-of-bounds), then add
the above native boundary color-transition(s). Compare the COMPLETE exact
64x64 changed-pixel + color-transition dictionary to actual native level1.
Record false positives, missing changes and color mismatches. Do not fit
the resulting rule to a failed observation. ACTION5 remains a control, not
a mathematical "B".

This is native public-game evidence, not source Window48 conjugacy or a
general ARC solution. Original mathematics and canonical agent unchanged.
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
    GAME, FROZEN_MAPS, steps_on_real_game, changed_triplets
)
from .native_sp80_stage_geometry import d4

# Frozen independently of this new official native run.
NEW_CONTEXT_WORDS=("4444","5544","45444","54454","54544")
RESETS=2
EXPECTED_BOUNDARY_COLOR=(14,0)
EXPECTED_BOUNDARY_ROW=63


def boundary_positions(word_step):
    if word_step<1:
        raise ValueError("word step must be positive")
    if word_step%2:
        return ((3*((word_step-1)//2), EXPECTED_BOUNDARY_ROW),)
    left=3*((word_step-2)//2)+1
    return ((left,EXPECTED_BOUNDARY_ROW),
            (left+1,EXPECTED_BOUNDARY_ROW))


def projected_with_frozen_boundary(src,rule,step):
    name,kind,dx,dy=rule
    predicted={}
    source_clipped=[]
    for p,colors in sorted(src.items()):
        x,y=d4(p,kind)
        to=(x+dx,y+dy)
        if 0<=to[0]<64 and 0<=to[1]<64:
            predicted[to]=colors
        else:
            source_clipped.append({"source_xy":list(p),
                                   "projected_xy":list(to),
                                   "native_change":list(colors)})
    collision=[]
    for p in boundary_positions(step):
        if p in predicted and predicted[p]!=EXPECTED_BOUNDARY_COLOR:
            collision.append({"xy":list(p),
                              "projected_native_colors":list(predicted[p])})
        predicted[p]=EXPECTED_BOUNDARY_COLOR
    return predicted,source_clipped,collision


def score(predict,actual):
    keys=set(predict)
    observed=set(actual)
    common=keys&observed
    pair_matching=sum(predict[p]==actual[p] for p in common)
    mismatches=[
        {"xy":list(p),
         "predicted":list(predict[p]),
         "observed":list(actual[p])}
        for p in sorted(common) if predict[p]!=actual[p]
    ]
    false_positive=[
        {"xy":list(p),"predicted":list(predict[p])}
        for p in sorted(keys-observed)]
    false_negative=[
        {"xy":list(p),"observed":list(actual[p])}
        for p in sorted(observed-keys)]
    return {
        "complete_exact_native_pixel_color_changes":predict==actual,
        "native_changed_predicted_count":len(predict),
        "native_changed_observed_count":len(actual),
        "geometry_intersection_count":len(common),
        "exact_native_color_pair_matches":pair_matching,
        "same_position_but_different_native_colors":mismatches,
        "false_positive_native_changes":false_positive,
        "missing_native_changes":false_negative,
        "exact_frame_change_mask_match":keys==observed,
    }


def trial(arcade,word,reset):
    records={}
    arrays={}
    for stage in (0,1):
        record,arr=steps_on_real_game(arcade,word,stage,reset)
        records[stage]=record
        arrays[stage]=arr
    complete=records[0]["complete"] and records[1]["complete"]
    result={
        "word":word,"reset":reset,"completed_pair":complete,
        "native_actions_issued":sum(r["real_native_actions"]
                                     for r in records.values()),
        "level0_status":records[0]["status"],
        "level1_status":records[1]["status"],
        "stage1_root_hash":records[1]["stage_root_hash"],
        "action4_predictions":[],
    }
    if complete:
        a=arrays[0];b=arrays[1]
        start0=records[0]["stage_root_index"]
        start1=records[1]["stage_root_index"]
        for index,letter in enumerate(word):
            if letter!="4":
                continue
            src=changed_triplets(a[start0+index],a[start0+index+1])
            dst=changed_triplets(b[start1+index],b[start1+index+1])
            model_evidence=[]
            for rule in FROZEN_MAPS:
                predicted,clipped,conflicts=projected_with_frozen_boundary(
                    src,rule,index+1)
                quality=score(predicted,dst)
                model_evidence.append({
                    "model":rule[0],
                    "frozen_geometry":[rule[1],rule[2],rule[3]],
                    "predicted_bottom_row_xy":[list(x) for x in
                                               boundary_positions(index+1)],
                    "native_bottom_row_color_change":
                        list(EXPECTED_BOUNDARY_COLOR),
                    "clipped_original_color_changes":clipped,
                    "boundary_conflicts_with_geometry":conflicts,
                    **quality,
                })
            result["action4_predictions"].append({
                "action_word_step":index+1,
                "native_actual_color_change_count":len(dst),
                "source_actual_change_count":len(src),
                "model_results":model_evidence,
            })
    return result,arrays


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-native-boundary-prediction.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials=[]
    raw={}
    for word in NEW_CONTEXT_WORDS:
        for reset in range(RESETS):
            record,frames=trial(arcade,word,reset)
            trials.append(record)
            for stage,images in frames.items():
                raw[f"word_{word}_reset_{reset}_level{stage}"]=images
    per_model={}
    for name,_,_,_ in FROZEN_MAPS:
        parts=[x for row in trials
               for effect in row["action4_predictions"]
               for x in effect["model_results"] if x["model"]==name]
        per_model[name]={
            "evaluated_native_ACTION4_effects":len(parts),
            "full_transition_predictions_exact":sum(
                x["complete_exact_native_pixel_color_changes"] for x in parts),
            "complete_mask_predictions_exact":sum(
                x["exact_frame_change_mask_match"] for x in parts),
            "total_color_pair_matches":sum(
                x["exact_native_color_pair_matches"] for x in parts),
            "total_actual_changed_cells":sum(
                x["native_changed_observed_count"] for x in parts),
            "total_missing_changes":sum(
                len(x["missing_native_changes"]) for x in parts),
            "total_false_positive_changes":sum(
                len(x["false_positive_native_changes"]) for x in parts),
            "total_wrong_native_color_transitions":sum(
                len(x["same_position_but_different_native_colors"])
                for x in parts),
        }
    record={
        "kind":"SP80_FROZEN_BOUNDARY_COLOR_RULE_BLIND_NATIVE_CONTEXT_TEST",
        "original_source_laws":48,
        "math_claim":"none: empirical native pixel-action history hypothesis",
        "game":GAME,"provider":"official native arc-agi Arcade NORMAL",
        "new_words_predeclared":list(NEW_CONTEXT_WORDS),
        "native_resets_per_word_stage":RESETS,
        "frozen_geometry":[{"name":r[0],"symmetry":r[1],
                            "dx":r[2],"dy":r[3]} for r in FROZEN_MAPS],
        "frozen_bottom_row_rule":(
            "native ACTION4 at word step n: 14->0 at y=63; odd n "
            "x=3*(n-1)//2; even n x=3*(n-2)//2+1 and +2."),
        "per_word_per_reset_results":trials,
        "native_actions":sum(x["native_actions_issued"] for x in trials),
        "complete_level0_level1_pairs":sum(x["completed_pair"] for x in trials),
        "model_summary":per_model,
        "boundary":(
            "Parameters and residual row rule predeclared before new native "
            "contexts; exact original 0..15 colors and pixel locations; "
            "native color pair equality is not hidden-state identity, "
            "Window48 F3 conjugacy, native A/B role, or game completion. "
            "Any failed case is recorded and not silently fitted away."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_BOUNDARY_RULE_HELDOUT "+json.dumps({
        "new_words":list(NEW_CONTEXT_WORDS),
        "independent_stage_pairs":len(trials),
        "full_native_resets":len(trials)*2,
        "real_native_actions":record["native_actions"],
        "complete_stage_pairs":record["complete_level0_level1_pairs"],
        "model_summary":per_model,
        "failures":[{
            "word":trial["word"],"reset":trial["reset"],
            "step":e["action_word_step"],
            "models":[{
                "name":v["model"],
                "exact":v["complete_exact_native_pixel_color_changes"],
                "misses":v["missing_native_changes"][:8],
                "extra":v["false_positive_native_changes"][:8],
                "wrong_colors":v["same_position_but_different_native_colors"][:8],
            } for v in e["model_results"]]
        } for trial in trials for e in trial["action4_predictions"]
          if not all(x["complete_exact_native_pixel_color_changes"]
                     for x in e["model_results"] if x["model"]!="identity_baseline")],
        "incomplete":[{"word":x["word"],"reset":x["reset"],
                       "level0_status":x["level0_status"],
                       "level1_status":x["level1_status"]}
                      for x in trials if not x["completed_pair"]],
        "json":str(args.out),"native_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if not any(t["completed_pair"] for t in trials):
        raise RuntimeError("no complete native stage-to-stage trials")


if __name__=="__main__":
    main()
