"""Native SP80 late-single-ACTION5 intervention at stage1.

Previously observed original-native 48-context stage1 all-ACTION4:
45 admitted visual transitions, then next native action returned
GameState.GAME_OVER with nonstandard empty frame (NOT a witnessed win).
Mixed earlier ACTION5-heavy words terminated earlier.
The unchanged empirical stage1 64/45 + ACTION4 ordinal source mask was
pixel/color exact on 170/170 prior admitted real stage1 actions, but
only 22/22 newly witnessed steps35--45, ALL from two all-ACTION4 runs.

Freeze ONE ACTION5 at original context action 33, 35, 39 or 43.
Keep an original all-ACTION4 control, two fresh genuine stage1 resets per
word, retain actual original SDK level/state, final frame availability,
and all color-mask counterexamples. Reuse old prediction source UNCHANGED.
No game clone, source F3 law edits, bots or win claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode

from .native_sp80_frozen_color_contexts import steps_on_real_game
from .native_sp80_quantized_boundary import PERIOD, score_native_word, rounded_progress
from .native_sp80_stage1_45_holdout import summarize_stage as old_summary

RESETS=2
WORD_LENGTH=48
WORDS=(
    "4"*WORD_LENGTH,
    "4"*32+"5"+"4"*15,
    "4"*34+"5"+"4"*13,
    "4"*38+"5"+"4"*9,
    "4"*42+"5"+"4"*5,
)
CONTROL="4"*WORD_LENGTH
INTERVENTIONS={33,35,39,43}
assert len(WORDS)==len(set(WORDS))==5
assert all(len(w)==WORD_LENGTH and set(w)<={"4","5"} for w in WORDS)
assert {w.index("5")+1 for w in WORDS[1:]}==INTERVENTIONS
assert all(w.count("5")==1 for w in WORDS[1:])
assert PERIOD[1]==45 and rounded_progress(1,45)==64


def describe_terminal(record,last_admitted):
    errors=record.get("errors") or []
    result={
        "sdk_record_status":record["status"],
        "completed_context_steps":last_admitted,
        "native_total_real_actions":record["real_native_actions"],
        "sdk_frame_count":record["frame_count"],
        "native_errors":errors,
    }
    if errors:
        first=errors[0]
        # SDK 'at' counts the six actual stage1-entry prefix actions.
        attempt=int(first["at"])
        result["terminal_native_attempt_number_including_entry"]=attempt
        result["terminal_context_action_attempt"]=attempt-6
        result["sdk_terminal_state"]=first.get("state")
        result["source_shape"]=first.get("source_shape")
    return result


def native_trials_summary(trials):
    stats=old_summary(trials,1)
    summary=[]
    by_action=Counter()
    for t in trials:
        intervention=t["insertion_step"]
        allrows=t["admitted_stage1_actions"]
        last=max((r["word_step"] for r in allrows),default=0)
        terminal=describe_terminal(t["original_native_record"],last)
        by_action["control" if intervention is None else str(intervention)]+=1
        summary.append({
            "ACTION5_context_position":intervention,
            "replicate":t["replicate"],
            "last_complete_native_stage1_context_step":last,
            "admitted_novel_steps_35_to_45":[r["word_step"] for r in allrows
                                             if 35<=r["word_step"]<=45],
            "first_native_terminal_observation":terminal,
            "frozen_full_frame_exact_before_native_terminal":sum(
                int(r["exact_full_native_64x64_color_map"]["QUANTIZED_RATE_FULL_GRID"]["complete_exact_native_pixel_color_changes"])
                for r in allrows),
            "all_native_admitted_preterminal":len(allrows),
        })
    return {"per_original_native_trial":summary,
            "counts":dict(by_action),
            "frozen_full_native_score":stats}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials,raw=[],{}
    for word in WORDS:
        intervention=None if word==CONTROL else word.index("5")+1
        for replicate in range(RESETS):
            record,frames=steps_on_real_game(arcade,word,1,replicate)
            raw[f"{word}_{replicate}_stage1"]=frames
            rows,unknown=score_native_word(word,replicate,1,record,frames)
            trials.append({
                "word":word,
                "insertion_step":intervention,
                "replicate":replicate,
                "original_native_record":record,
                "original_native_records":{1:record},
                # old_summary expects stage0/1 buckets and pairs. No fake stage0.
                "admitted_stage1_actions":rows,
                "unknown_original_actions":{1:unknown},
                "actual_native_actions":record["real_native_actions"],
            })
    summary=native_trials_summary(trials)
    evidence={
        "kind":"SP80_ORIGINAL_NATIVE_LATE_ACTION5_TERMINAL_AND_FULLFRAME_CONTRAST",
        "frozen_action5_insertions":sorted(INTERVENTIONS),
        "original_native_control":"ALL_ACTION4",
        "words_precommitted":WORDS,
        "native_stage1_resets":len(trials),
        "real_original_native_actions":sum(t["actual_native_actions"] for t in trials),
        "prior_frozen_stage1_boundary_period":PERIOD[1],
        "summary":summary,
        "source_owned_native_trials":trials,
        "limits":"All actual effects are original public SP80 native stage1 and observed SDK original frames; GAME_OVER with empty frame cannot by itself identify a win. ACTION5 insertion and all unobserved steps are source-recorded. Frozen original color effects only; no hidden state or F3 48-law correspondence.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(evidence,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_LATE_ACTION5 "+json.dumps(
        {k:v for k,v in evidence.items() if k!="source_owned_native_trials"},
        sort_keys=True))
    if summary["frozen_full_native_score"]["all_admitted"]["observations"].get("admitted",0)==0:
        raise RuntimeError("No authentic stage1 observations admitted")


if __name__=="__main__":
    main()
