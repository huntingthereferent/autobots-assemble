"""Prospective quantized native SP80 boundary-rate experiment.

Earlier original SP80 public native frame studies (up to 26 actions)
suggested, but did not establish, an exact width rule:
  stage0 row0 right-to-left cumulative 14->0 = round_half_up(64*t/30);
  stage1 row63 left-to-right cumulative 14->0 = round_half_up(64*t/45);
where t counts ALL genuine ACTION4/ACTION5 context steps since stage root.

This freezes the literal two rational-rate candidates and native words
BEFORE new 34-step original-game execution. Evaluate PRE-ACTION endpoint
alignment, exact next width, and full native 64x64 pixel/color maps,
separately for genuinely novel steps t>=27. Prior stage-specific ACTION4
interior masks remain untouched. Do not relabel any original F3 laws.
Unknown native frames/levels are not success or negative evidence.
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
    changed_triplets, steps_on_real_game)
from .native_sp80_stage_mask_holdout import predeclared_interior_mask
from .native_sp80_boundary_prediction import score
from .native_sp80_opposite_boundaries import (
    native_boundary_before, frozen_frontier_mask, observe_native_stage)

WORDS=(
    "4444444444444444444444444444444444",
    "4444444445444444444445444444444444",
    "5555444444444444444444444444444444",
    "4444444444444444444455554444444444",
)
RESETS=2
STAGE1_PREFIX=6
NOVEL_STEP_MIN=27
PERIOD={0:30,1:45}
assert len(WORDS)==len(set(WORDS))==4
assert all(len(w)==34 and set(w)<={"4","5"} for w in WORDS)


def rounded_progress(stage,elapsed):
    """Integer half-up rounding; not a hidden clock or inferred game state."""
    period=PERIOD[stage]
    if elapsed<0:raise ValueError("negative elapsed")
    return min(64,(128*elapsed+period)//(2*period))


def frozen_width(stage,step):
    return rounded_progress(stage,step)-rounded_progress(stage,step-1)


def proposed_boundary(stage,pre,step):
    y,actual_x,actual_color=native_boundary_before(stage,pre)
    before_count=rounded_progress(stage,step-1)
    expected_x=(63-before_count) if stage==0 and before_count<64 else (
        before_count if stage==1 and before_count<64 else None
    )
    width=frozen_width(stage,step)
    if width==0:
        predicted={}
        usable=actual_x is None
    else:
        predicted,metadata=frozen_frontier_mask(stage,pre,width)
        usable=bool(metadata["precondition_admitted"])
    return predicted,{
        "original_native_stage":stage,
        "elapsed_actual_native_context_step":step,
        "quantized_period":PERIOD[stage],
        "predeclared_before_cumulative":before_count,
        "predeclared_after_cumulative":rounded_progress(stage,step),
        "predeclared_exact_width":width,
        "expected_preaction_frontier_x":expected_x,
        "actual_native_preaction_frontier_x":actual_x,
        "actual_native_preaction_color":actual_color,
        "preaction_position_alignment":actual_x==expected_x,
        "preaction_native_color_precondition":usable,
    }


def score_native_word(word,replicate,stage,record,frames):
    admitted,omissions=observe_native_stage(stage,word,record,frames)
    root=record["stage_root_index"]
    if root is None:return [],omissions
    output=[]
    for row in admitted:
        step=row["word_step"]
        index=root+step-1
        pre,after=frames[index],frames[index+1]
        original=changed_triplets(pre,after)
        interior=predeclared_interior_mask(
            stage,row["native_action"],row["native_ACTION4_ordinal"])
        quantized,contract=proposed_boundary(stage,pre,step)
        minimum=min(frozen_width(stage,step),1)
        if minimum:
            min_pred,_=frozen_frontier_mask(stage,pre,1)
        else:
            min_pred={}
        fixed_min=2 if stage==0 else 1
        fixed_max=3 if stage==0 else 2
        min_fixed,_=frozen_frontier_mask(stage,pre,fixed_min)
        max_fixed,_=frozen_frontier_mask(stage,pre,fixed_max)
        frozen_proposals={
            "QUANTIZED_RATE_FULL_GRID":{**interior,**quantized},
            "INTERIOR_PLUS_FIXED_MIN_WIDTH":{**interior,**min_fixed},
            "INTERIOR_PLUS_FIXED_MAX_WIDTH":{**interior,**max_fixed},
            "INTERIOR_PLUS_FIRST_ONLY":{**interior,**min_pred},
            "INTERIOR_ONLY_NEGATIVE_CONTROL":interior,
        }
        y=0 if stage==0 else 63
        actual_boundary={p:cs for p,cs in original.items() if p[1]==y}
        actual_width=len(actual_boundary)
        observed_colors_ok=all(cs==(14,0) for cs in actual_boundary.values())
        native_score={name:score(predicted,original)
                      for name,predicted in frozen_proposals.items()}
        output.append({
            "original_native_stage":stage,
            "word_step":step,
            "native_action":row["native_action"],
            "native_ACTION4_ordinal":row["native_ACTION4_ordinal"],
            "real_native_before_hash":row["genuine_before_hash"],
            "real_native_after_hash":row["genuine_after_hash"],
            "prior_native_frontier_rate_prediction":contract,
            "observed_boundary_width":actual_width,
            "observed_boundary_native14_to0_only":observed_colors_ok,
            "exact_boundary_width_predicted":contract["predeclared_exact_width"]==actual_width,
            "exact_full_native_64x64_color_map":native_score,
            "actual_native_boundary_color_changes":row["actual_native_boundary_changes"],
            "actual_opposite_row_color_changes":row["actual_opposite_native_row_changes"],
        })
    return output,omissions


def summarize(experiments):
    aggregate={}
    for stage in (0,1):
        allrows=[r for t in experiments for r in t[f"admitted_stage{stage}_actions"]]
        stages={}
        for label,rows in [
            ("all_admitted",allrows),
            ("previous_horizon_1_to_26",[r for r in allrows if r["word_step"]<NOVEL_STEP_MIN]),
            ("prospective_new_horizon_27_to_34",[r for r in allrows if r["word_step"]>=NOVEL_STEP_MIN]),
        ]:
            c=Counter()
            model={}
            counterexamples=[]
            for row in rows:
                c["admitted"]+=1
                c["exact_width"]+=int(row["exact_boundary_width_predicted"])
                c["preaction_frontier_aligned"]+=int(row["prior_native_frontier_rate_prediction"]["preaction_position_alignment"])
                c["preaction_original_color_allowed"]+=int(row["prior_native_frontier_rate_prediction"]["preaction_native_color_precondition"])
                if not row["exact_boundary_width_predicted"] or not row["prior_native_frontier_rate_prediction"]["preaction_position_alignment"]:
                    counterexamples.append({
                        "step":row["word_step"],"stage":stage,
                        "native_action":row["native_action"],
                        "expected":row["prior_native_frontier_rate_prediction"],
                        "actual_width":row["observed_boundary_width"],
                        "actual_boundary_changes":row["actual_native_boundary_color_changes"]})
                for name,s in row["exact_full_native_64x64_color_map"].items():
                    m=model.setdefault(name,Counter())
                    m["evaluated"]+=1
                    m["exact"]+=int(s["complete_exact_native_pixel_color_changes"])
                    m["extras"]+=len(s["false_positive_native_changes"])
                    m["misses"]+=len(s["missing_native_changes"])
                    m["wrong_color_pairs"]+=len(s["same_position_but_different_native_colors"])
            stages[label]={
                "measurements":dict(c),
                "full_native_64x64_controls":{name:dict(v) for name,v in model.items()},
                "counterexamples":counterexamples[:50],
            }
        aggregate["stage"+str(stage)]=stages
    return aggregate


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    experiments,frames_saved=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            records,original_frames,rows,unknown={},{},{},{}
            for stage in (0,1):
                record,frames=steps_on_real_game(arcade,word,stage,replicate)
                records[stage],original_frames[stage]=record,frames
                frames_saved[f"{word}_{replicate}_stage{stage}"]=frames
                rows[stage],unknown[stage]=score_native_word(
                    word,replicate,stage,record,frames)
            experiments.append({
                "word":word,"replicate":replicate,
                "original_native_records":records,
                "admitted_stage0_actions":rows[0],
                "admitted_stage1_actions":rows[1],
                "unknown_original_actions":unknown,
                "actual_native_actions":sum(v["real_native_actions"] for v in records.values()),
            })
    stats=summarize(experiments)
    outcome={
        "kind":"SP80_PREDECLARED_NATIVE_BOUNDARY_RATIONAL_RATE_HOLDOUT",
        "fixed_new_native_words":WORDS,
        "novel_native_elapsed_horizon_min":NOVEL_STEP_MIN,
        "quantized_stage0_period":30,
        "quantized_stage1_period":45,
        "resets_per_word_per_stage":RESETS,
        "native_resets":2*len(experiments),
        "actual_native_actions":sum(x["actual_native_actions"] for x in experiments),
        "stage_specific_heldout":stats,
        "trials":experiments,
        "limits":"Exact native visible-state pixel/color prediction only; stage0/1 pre-action frontier rate inferred from earlier samples, not a proven internal timer, F3 mapping or full game solve. Missing/unavailable actions remain UNKNOWN.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames_saved)
    print("SP80_QUANTIZED_BOUNDARY_HOLDOUT "+json.dumps(
        {k:v for k,v in outcome.items() if k!="trials"},sort_keys=True))
    if not any(stats["stage"+str(s)]["prospective_new_horizon_27_to_34"]["measurements"].get("admitted",0)
               for s in (0,1)):
        raise RuntimeError("No untouched original native observations beyond step26")


if __name__=="__main__":
    main()
