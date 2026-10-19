"""Prospective native SP80 exact outside-row63 ACTION4 mask/color test.

Discovery in original PR #163 real stage1 frames (not these new words):
first six genuine ACTION4 ordinals k=1..6 move TWO 4x4 native blocks:
  x=16+4*k .. 19+4*k, y=36..39: native 9->12
  x=36+4*k .. 39+4*k, y=36..39: native 12->9
Later ACTION4 and all ACTION5 show no outside-row63 change.

Freeze this exact empirical pixel+color hypothesis before six NEW native
18-action words. Compare with absolute word-step prediction and ZERO
control using original real Arcade NORMAL source only. No game clone,
hidden state or F3 mathematical equivalence is asserted.
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
    steps_on_real_game, changed_triplets)
from .native_sp80_boundary_prediction import score

WORDS = (
    "444444554444444444",
    "555544444444444444",
    "454454454444444444",
    "544544544444444444",
    "444544444554444444",
    "555555444444444444",
)
RESETS = 2
STAGE1_PREFIX = 6
assert len(set(WORDS)) == 6
assert all(len(w)==18 and set(w)<=set("45") for w in WORDS)


def ordinal_exact_prediction(ordinal, action):
    if action != 4 or not 1 <= ordinal <= 6:
        return {}
    left, right = 16+4*ordinal, 36+4*ordinal
    predicted = {}
    for y in (36,37,38,39):
        for x in range(left,left+4):
            predicted[(x,y)] = (9,12)
        for x in range(right,right+4):
            predicted[(x,y)] = (12,9)
    assert len(predicted)==32
    return predicted


def original_admissible_stage1(word, record, frames):
    root = record["stage_root_index"]
    rows, omissions = [], Counter()
    if root is None:
        return [], {"UNKNOWN_NO_NATIVE_STAGE1_ROOT": len(word)}
    for index, char in enumerate(word):
        step=index+1
        frame_index=root+index
        transition_index=STAGE1_PREFIX+index
        if (len(frames)<=frame_index+1 or
                len(record["transition_records"])<=transition_index):
            omissions["UNKNOWN_NO_FULL_NATIVE_FRAME"]+=1
            continue
        t=record["transition_records"][transition_index]
        if t["action"] != int(char) or t["level"]!=1:
            omissions["UNKNOWN_LEVEL_CHANGE_OR_ACTION_MISMATCH"]+=1
            continue
        before,after=frames[frame_index],frames[frame_index+1]
        actual=changed_triplets(before[:63],after[:63])
        ordinal=word[:step].count("4")
        predictions={
            "ORDINAL_EXACT_NATIVE_MASK":ordinal_exact_prediction(ordinal,int(char)),
            "ABSOLUTE_STEP_EXACT_BASELINE":ordinal_exact_prediction(step,int(char)),
            "EMPTY_NEGATIVE_CONTROL":{},
        }
        evaluations={name:score(proposal,actual)
                     for name,proposal in predictions.items()}
        rows.append({
            "word_step":step,
            "native_action":int(char),
            "native_ACTION4_ordinal":ordinal,
            "actual_native_level":t["level"],
            "before_hash":t["before_hash"],
            "after_hash":t["after_hash"],
            "real_native_nonbottom_changes":[
                {"xy":list(p),"before_native_color":pair[0],"after_native_color":pair[1]}
                for p,pair in sorted(actual.items())
            ],
            "pre_registered_exact_pixel_color_models":evaluations,
        })
    return rows,dict(omissions)


def tally(trials):
    s={}
    for t in trials:
        for row in t["admitted_stage1_actions"]:
            for name,result in row["pre_registered_exact_pixel_color_models"].items():
                c=s.setdefault(name,Counter())
                c["evaluated"]+=1
                c["exact"]+=int(result["complete_exact_native_pixel_color_changes"])
                c["extra"]+=len(result["false_positive_native_changes"])
                c["missed"]+=len(result["missing_native_changes"])
                c["wrong_color"]+=len(result["same_position_but_different_native_colors"])
    return {k:dict(v) for k,v in s.items()}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials,raw=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            native,frames={},{}
            for stage in (0,1):
                native[stage],frames[stage]=steps_on_real_game(
                    arcade,word,stage,replicate)
                raw[f"{word}_{replicate}_{stage}"]=frames[stage]
            entries,unknown=original_admissible_stage1(word,native[1],frames[1])
            trials.append({
                "word":word,"replicate":replicate,
                "actual_native_records":native,
                "admitted_stage1_actions":entries,
                "unknown_stage1_steps":unknown,
                "actual_native_actions":sum(v["real_native_actions"] for v in native.values()),
            })
    result={
        "kind":"SP80_PREDECLARED_EXACT_ACTION4_PIXEL_COLOR_MASK",
        "frozen_new_words":WORDS,
        "native_resets":2*len(trials),
        "original_native_actions":sum(t["actual_native_actions"] for t in trials),
        "native_model_summary":tally(trials),
        "trials":trials,
        "boundary":"Original 64x64 before/after native frames preserved, native level and ACTION4 ordinal verified. Mask refers to visible outside-row63 pixels only; unknown steps not successes. No original F3 mathematical source mapping, hidden-state proof, autonomous policy or ARC game win.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_EXACT_MASK_HOLDOUT "+json.dumps({k:v for k,v in result.items() if k!="trials"},sort_keys=True))
    if not result["native_model_summary"]:
        raise RuntimeError("No actual native paired observation admitted")


if __name__=="__main__":
    main()
