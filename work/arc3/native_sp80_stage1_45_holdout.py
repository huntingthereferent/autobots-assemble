"""New original-native SP80 stage1 steps 35--45 held-out falsification.

Previous official real-game SP80 run #39215981810 measured 240/240 stage0
and 272/272 stage1 full 64x64 effects using the prospectively frozen
stage-specific interior ACTION4 masks and two empirical rational rates:
stage0 cumulative y0 native 14->0 = round_half_up(64*t/30),
stage1 cumulative y63 native 14->0 = round_half_up(64*t/45).

DO NOT refit either rate or block mask. Reuse the exact source module.
Use NEW 48-action real native trajectories to attempt the previously
unwitnessed stage1 native action steps 35--45. Record attempted steps
46--48 but never presume that the game still permits them. State0 may
reach a native terminal nonstandard frame after step30; these omissions
are UNKNOWN, not victories or falsifications. No game clone or bot.
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
from .native_sp80_quantized_boundary import (
    PERIOD, rounded_progress, frozen_width, proposed_boundary, score_native_word)

# Literal and deterministic native words, all committed before run.
WORDS=(
    "4"*48,
    "5"*8+"4"*40,
    "45"*24,
    "4"*20+"5"*8+"4"*20,
)
RESETS=2
NEW_RANGE=(35,45)
assert len(WORDS)==len(set(WORDS))==4
assert all(len(w)==48 and set(w)<={"4","5"} for w in WORDS)
assert PERIOD=={0:30,1:45}
assert rounded_progress(1,45)==64 and rounded_progress(1,34)==48
assert all(frozen_width(1,s) in (1,2) for s in range(35,46))


def summarize_stage(trials,stage):
    samples=[(t,r) for t in trials for r in t[f"admitted_stage{stage}_actions"]]
    buckets={
        "historical_context_1_to_34":lambda step:1<=step<=34,
        "NEW_UNSEEN_STAGE1_STEPS_35_TO_45":lambda step:35<=step<=45,
        "post_boundary_steps_46_to_48":lambda step:46<=step<=48,
        "all_admitted":lambda step:True,
    }
    output={}
    for label,eligible in buckets.items():
        counter=Counter()
        controls={}
        counterexamples=[]
        for trial,row in samples:
            step=row["word_step"]
            if not eligible(step):continue
            contract=row["prior_native_frontier_rate_prediction"]
            counter["admitted"]+=1
            counter["ACTION"+str(row["native_action"])]+=1
            counter["width_exact"]+=int(row["exact_boundary_width_predicted"])
            counter["preaction_position_agrees"]+=int(contract["preaction_position_alignment"])
            counter["native_color_precondition"]+=int(contract["preaction_native_color_precondition"])
            for name,s in row["exact_full_native_64x64_color_map"].items():
                c=controls.setdefault(name,Counter())
                c["admitted"]+=1
                c["exact"]+=int(s["complete_exact_native_pixel_color_changes"])
                c["extra"]+=len(s["false_positive_native_changes"])
                c["missed"]+=len(s["missing_native_changes"])
                c["wrong_original_colors"]+=len(s["same_position_but_different_native_colors"])
            primary=row["exact_full_native_64x64_color_map"]["QUANTIZED_RATE_FULL_GRID"]
            if (not primary["complete_exact_native_pixel_color_changes"]
                or not contract["preaction_position_alignment"]
                or not contract["preaction_native_color_precondition"]):
                counterexamples.append({
                    "word":trial["word"],"replicate":trial["replicate"],
                    "original_stage":stage,"step":step,
                    "native_action":row["native_action"],"contract":contract,
                    "actual_width":row["observed_boundary_width"],
                    "actual_native_changes":row["actual_native_boundary_color_changes"],
                    "source_score":primary,
                })
        output[label]={
            "observations":dict(counter),
            "frozen_full_native_models":{name:dict(v) for name,v in controls.items()},
            "all_counterexamples":counterexamples,
        }
    # Word-scoped availability guards against a single lucky surviving sequence.
    output["native_per_word_new_horizon_admissions"]=[
        {"word":t["word"],"replicate":t["replicate"],
         "admitted_steps":[r["word_step"] for r in t[f"admitted_stage{stage}_actions"]
                            if NEW_RANGE[0]<=r["word_step"]<=NEW_RANGE[1]],
         "native_status":t["original_native_records"][stage]["status"],
         "native_real_actions":t["original_native_records"][stage]["real_native_actions"],
         "unknown_original_steps":t["unknown_original_actions"][stage]}
        for t in trials
    ]
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials,frames_saved=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            records,rows,unknown={},{},{}
            for stage in (0,1):
                record,frames=steps_on_real_game(arcade,word,stage,replicate)
                records[stage]=record
                frames_saved[f"{word}_{replicate}_stage{stage}"]=frames
                rows[stage],unknown[stage]=score_native_word(
                    word,replicate,stage,record,frames)
            trials.append({
                "word":word,"replicate":replicate,
                "original_native_records":records,
                "admitted_stage0_actions":rows[0],
                "admitted_stage1_actions":rows[1],
                "unknown_original_actions":unknown,
                "actual_native_actions":sum(x["real_native_actions"] for x in records.values()),
            })
    result={
        "kind":"SP80_NATIVE_STAGE1_FROZEN_64_OVER_45_HORIZON_35_TO_45",
        "native_new_words_fixed_before_execution":WORDS,
        "new_untested_action_steps":[35,45],
        "original_native_resets":len(trials)*2,
        "actual_native_actions":sum(t["actual_native_actions"] for t in trials),
        "frozen_periods":PERIOD,
        "stage0":summarize_stage(trials,0),
        "stage1":summarize_stage(trials,1),
        "trials":trials,
        "limitations":"Real original game native ACTION4/ACTION5 only; each proposed next pixel/color transition uses original pre-action frame, native stage, prior action history, no present after-frame. Unavailable terminal frames UNKNOWN. Fixed rational rates are empirical. Does not solve game or identify hidden state or F3 mathematical generator.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames_saved)
    print("SP80_STAGE1_35_45 "+json.dumps({
        k:v for k,v in result.items() if k!="trials"},sort_keys=True))
    novel=result["stage1"]["NEW_UNSEEN_STAGE1_STEPS_35_TO_45"]["observations"].get("admitted",0)
    if novel==0: raise RuntimeError("No real original-game stage1 observations for unseen steps35-45")
    if novel<20: raise RuntimeError("Insufficient independent genuine stage1 new-horizon observations; retain evidence as partial")
    # A scientific counterexample must not fail CI automatically. Preserve the
    # native data and report a falsified hypothesis as a successful execution.


if __name__=="__main__":
    main()
