"""Official SP80 longer-history falsification of frozen pre-color transition transfer.

Previous independent native tests (see WINDOW48_SP80_NATIVE_OCCUPANCY):
  T: original frame shift (+8,+20), unchanged native palette
  R: vertical reflection + shift (+8,-8)
  Both: original position-dependent row-63 native 14->0 completion
  Both: admit native predicted (old,new) ONLY if target PRE-ACTION
        frame contains old at the predicted position and old!=new.

No fitting or source F3 modification in this test. The eight NEW action
histories below were declared before any observations from this new run.
They differ from prior <=6 action words in length and combinations.
Test each on genuine public native SP80 level0 and real level1 reached
independently by witnessed 454545; 2 fresh resets per history/level.

Some longer trajectories may complete/change levels or return nonstandard
frames. Retain these as INTERRUPTED. Crucially, compare EACH matched
ACTION4 step where BOTH levels remained unchanged, even if the rest of
a trial was interrupted; never turn missing frames into negative results.

Compare exact native changed-cell and (before_color,after_color) maps,
ungated vs frozen pre-color-gated T/R vs no-shift negative control.
Explicitly audit whether the two candidate maps predict the SAME native
pixels/color changes after occupancy gating. Preserve first counterexample
unchanged, not adjust rule post hoc.

This is an empirically conditioned stage0->stage1 experiment, not a
Window48 F3 A/B action correspondence, native hidden state proof or solver.
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
    FROZEN_MAPS, GAME, changed_triplets, steps_on_real_game,
)
from .native_sp80_boundary_prediction import (
    projected_with_frozen_boundary, score,
)
from .native_sp80_occupancy_gate import gate_using_target_pre_state

# Written before this native run. Earlier heldout words had length <=6.
NEW_WORDS = (
    "44444444",       # longer block of a single tested control
    "54545454",       # reversed alternation
    "55554444",       # changed early context with a later ACTION4 block
    "44554544",       # ACTION4 after two ACTION5 controls
    "4544544544",     # 10 native controls
    "5445544454",     # 10 varied native controls
    "55445454444",    # 11 varied native controls
    "444545554444",   # 12 varied native controls
)
FRESH_RESETS_PER_WORD_AND_LEVEL = 2
LEVEL1_NATIVE_PREFIX_LENGTH = 6


def evaluate_pair(level0, level1, stage0_frames, stage1_frames):
    """Admit only source/target transitions that remained at level0/1."""
    evidence = []
    reasons = Counter()
    for idx, letter in enumerate(level0["word"]):
        if letter != "4":
            continue
        if (level1["stage_root_index"] is None
                or level0["stage_root_index"] is None):
            reasons["NO_WITNESSED_STAGE1_ROOT"] += 1
            continue
        i0=level0["stage_root_index"]+idx
        i1=level1["stage_root_index"]+idx
        t0=level0["transition_records"]
        t1=level1["transition_records"]
        if (len(stage0_frames) <= i0+1 or len(stage1_frames) <= i1+1
                or len(t0) <= idx or len(t1) <= LEVEL1_NATIVE_PREFIX_LENGTH+idx):
            reasons["NATIVE_SEQUENCE_INTERRUPTED_BEFORE_STEP"] += 1
            continue
        action0=t0[idx]
        action1=t1[LEVEL1_NATIVE_PREFIX_LENGTH+idx]
        if (action0["action"]!=4 or action1["action"]!=4
                or action0["level"]!=0 or action1["level"]!=1):
            reasons["NATIVE_LEVEL_TRANSITION_OR_DIFFERENT_CONTROL"] += 1
            continue

        before0,after0=stage0_frames[i0],stage0_frames[i0+1]
        before1,after1=stage1_frames[i1],stage1_frames[i1+1]
        src=changed_triplets(before0,after0)
        actual=changed_triplets(before1,after1)
        candidate_results=[]
        raw_predictions={}
        for rule in FROZEN_MAPS:
            prediction,clipped,collision=projected_with_frozen_boundary(
                src,rule,idx+1)
            gated,excluded=gate_using_target_pre_state(prediction,before1)
            ungated_result=score(prediction,actual)
            gated_result=score(gated,actual)
            raw_predictions[rule[0]]=gated
            candidate_results.append({
                "model":rule[0],
                "ungated":ungated_result,
                "gated":gated_result,
                "gate_removed":len(excluded),
                "gated_out_before_colors":dict(Counter(
                    str(x["actual_pre_action_color"]) for x in excluded)),
                "gated_out_details":excluded,
                "clipped_source_cells":len(clipped),
                "boundary_rule_collision":collision,
            })
        t=raw_predictions["translation_only"]
        r=raw_predictions["reflection_plus_shift"]
        differing_positions={p for p in set(t)|set(r)
                             if t.get(p)!=r.get(p)}
        evidence.append({
            "word_step":idx+1,
            "word_prefix_before":level0["word"][:idx],
            "native_action":4,
            "level0_before_hash":action0["before_hash"],
            "level1_before_hash":action1["before_hash"],
            "level0_source_changed_pixels":len(src),
            "level1_actual_changed_pixels":len(actual),
            "frozen_models_identical_predictions":t==r,
            "model_prediction_disagreement_count":len(differing_positions),
            "model_prediction_disagreement_xy":[
                list(p) for p in sorted(differing_positions)[:20]],
            "model_evidence":candidate_results,
        })
    return evidence,dict(reasons)


def totals(experiments, model):
    items=[
        (run,step,m)
        for run in experiments for step in run["comparable_ACTION4_steps"]
        for m in step["model_evidence"] if m["model"]==model
    ]
    totals=Counter()
    counterexamples=[]
    for run,step,m in items:
        u,g=m["ungated"],m["gated"]
        totals["evaluated_action4_steps"]+=1
        totals["actual_native_color_changes"]+=g["native_changed_observed_count"]
        totals["source_only_exact_effects"]+=int(
            u["complete_exact_native_pixel_color_changes"])
        totals["occupancy_exact_effects"]+=int(
            g["complete_exact_native_pixel_color_changes"])
        totals["native_changed_colors_correct_after_gate"]+=(
            g["exact_native_color_pair_matches"])
        totals["false_positives_ungated"]+=len(u["false_positive_native_changes"])
        totals["false_positives_gated"]+=len(g["false_positive_native_changes"])
        totals["false_negatives_gated"]+=len(g["missing_native_changes"])
        totals["wrong_color_pairs_gated"]+=len(
            g["same_position_but_different_native_colors"])
        totals["excluded_before_color_cells"]+=m["gate_removed"]
        if not g["complete_exact_native_pixel_color_changes"]:
            counterexamples.append({
                "word":run["word"],"reset":run["reset"],
                "step":step["word_step"],
                "model":model,
                "actual_change_count":g["native_changed_observed_count"],
                "missing_native_changes":g["missing_native_changes"][:32],
                "false_positive_native_changes":g["false_positive_native_changes"][:32],
                "wrong_color_pairs":g["same_position_but_different_native_colors"][:32],
            })
    return {**dict(totals),
            "first_counterexamples":counterexamples[:20]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-occupancy-long-history.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    experiments=[]
    raw={}
    for word in NEW_WORDS:
        for reset in range(FRESH_RESETS_PER_WORD_AND_LEVEL):
            records={}
            frames={}
            for level in (0,1):
                row,arrays=steps_on_real_game(arcade,word,level,reset)
                records[level]=row
                frames[level]=arrays
                raw[f"{word}_reset{reset}_level{level}"]=arrays
            steps,omissions=evaluate_pair(records[0],records[1],
                                          frames[0],frames[1])
            experiments.append({
                "word":word,"reset":reset,
                "stage0_status":records[0]["status"],
                "stage1_status":records[1]["status"],
                "stage1_entry_witnessed":records[1]["stage_root_index"] is not None,
                "native_actions":sum(x["real_native_actions"]
                                     for x in records.values()),
                "comparable_ACTION4_steps":steps,
                "uncomparable_ACTION4_reasons":omissions,
                "both_stage_words_complete":all(x["complete"]
                                                  for x in records.values()),
            })
    stats={r[0]:totals(experiments,r[0]) for r in FROZEN_MAPS}
    model_tie=Counter()
    for run in experiments:
        for step in run["comparable_ACTION4_steps"]:
            model_tie["evaluated"]+=1
            model_tie["identical_prediction"]+=int(
                step["frozen_models_identical_predictions"])
            if not step["frozen_models_identical_predictions"]:
                t=next(x for x in step["model_evidence"]
                       if x["model"]=="translation_only")
                r=next(x for x in step["model_evidence"]
                       if x["model"]=="reflection_plus_shift")
                model_tie["translation_exact_when_distinguished"]+=int(
                    t["gated"]["complete_exact_native_pixel_color_changes"])
                model_tie["reflection_exact_when_distinguished"]+=int(
                    r["gated"]["complete_exact_native_pixel_color_changes"])
    result={
        "kind":"SP80_FROZEN_OCCUPANCY_NATIVE_LONG_HISTORY_FALSIFICATION",
        "native_source":"official arc-agi Arcade NORMAL public sp80",
        "math_referent":"original 48-law F3 WindowCombined remains UNMAPPED",
        "predeclared_new_words":list(NEW_WORDS),
        "new_word_lengths":[len(s) for s in NEW_WORDS],
        "independent_resets_per_word_per_level":
            FRESH_RESETS_PER_WORD_AND_LEVEL,
        "independently_reset_native_game_count":len(experiments)*2,
        "native_actions_executed":sum(x["native_actions"] for x in experiments),
        "pair_count":len(experiments),
        "fully_completed_pairs":sum(x["both_stage_words_complete"]
                                     for x in experiments),
        "paired_steps_evaluated":sum(len(x["comparable_ACTION4_steps"])
                                     for x in experiments),
        "stage1_entered_pairs":sum(x["stage1_entry_witnessed"]
                                    for x in experiments),
        "status_pairs":[{"word":r["word"],"reset":r["reset"],
                         "stage0_status":r["stage0_status"],
                         "stage1_status":r["stage1_status"],
                         "comparable_steps":len(r["comparable_ACTION4_steps"]),
                         "omissions":r["uncomparable_ACTION4_reasons"]}
                        for r in experiments],
        "frozen_models":{
            name:{"d4":kind,"dx":dx,"dy":dy}
            for name,kind,dx,dy in FROZEN_MAPS
        },
        "summary":stats,
        "model_distinction":dict(model_tie),
        "source_owned_native_evidence":experiments,
        "limits":(
            "This is an independent longer-history same-PUBLIC-SP80 "
            "native falsification screen, not an unseen ARC game or "
            "future-state prediction without the genuine level0 "
            "action-effect observation and level1 PRE-action frame. "
            "Incomplete trajectories remain unknown; only matched "
            "native non-level-changing ACTION4 steps enter totals. "
            "No fitted geometry or bottom-row rule changed. "
            "Original source 48-law F3 and canonical agent unchanged; "
            "no mathematical F3 correspondence or ARC game win."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_OCCUPANCY_LONG_HISTORY "+json.dumps({
        "new_words":list(NEW_WORDS),
        "independent_native_resets":result[
            "independently_reset_native_game_count"],
        "native_actions":result["native_actions_executed"],
        "paired_trials":result["pair_count"],
        "fully_complete":result["fully_completed_pairs"],
        "stage1_confirmed":result["stage1_entered_pairs"],
        "action4_steps_evaluated":result["paired_steps_evaluated"],
        "native_statuses":result["status_pairs"],
        "model_stats":stats,
        "model_distinction":dict(model_tie),
        "record":str(args.out),
        "raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if not result["paired_steps_evaluated"]:
        raise RuntimeError("No comparable native ACTION4 transitions observed")


if __name__=="__main__":
    main()
