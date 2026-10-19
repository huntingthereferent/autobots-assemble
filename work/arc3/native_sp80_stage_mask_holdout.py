"""Official native SP80 stage-specific exact interior color-mask holdout.

The previous original NPZ stage comparisons revealed a falsifiable
relationship: stage0 block movements at ACTION4 ordinals 1..8 in native
rows16..19, and independently-entered stage1 movements at ordinals 1..6
in rows36..39. Both are 2x(4x4) color exchanges 9->12 and 12->9.
Stage1 masks for matched ordinal k<=6 appear to be stage0 masks
translated by (+8,+20). This has NOT been independently validated.

Freeze all equations and fresh words BEFORE the new native actions.
Explicitly EXCLUDE boundary y=0 and y=63 from the exact interior
prediction, BUT retain the genuine native boundary pixel changes and
complete 64x64 before/after frames for independent analysis. Native
frame unavailable/level-changing transitions remain UNKNOWN. Never
infer hidden-state identity or mathematical source F3 conjugacy.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode

from .native_sp80_frozen_color_contexts import steps_on_real_game, changed_triplets
from .native_sp80_boundary_prediction import score

WORDS = (
    "5544444444444444",
    "4455444444444444",
    "4545454444444444",
    "4444555444444444",
    "5445454444444444",
    "5555444444444444",
)
RESETS = 2
PREFIX_STAGE1 = 6
assert len(set(WORDS)) == 6
assert all(len(w) == 16 and set(w) <= {"4","5"} for w in WORDS)


def predeclared_interior_mask(stage, action, ordinal):
    if action != 4 or ordinal < 1:
        return {}
    if stage == 0:
        if ordinal > 8: return {}
        rows, left, right = range(16,20), 8+4*ordinal, 28+4*ordinal
    elif stage == 1:
        if ordinal > 6: return {}
        rows, left, right = range(36,40), 16+4*ordinal, 36+4*ordinal
    else:
        raise ValueError("Only observed native stage0/1 evaluated")
    out = {}
    for y in rows:
        for x in range(left,left+4):
            out[(x,y)] = (9,12)
        for x in range(right,right+4):
            out[(x,y)] = (12,9)
    assert len(out)==32 and all(1<=y<=62 for x,y in out)
    return out


def stage0_to_stage1_translation(mask):
    predicted = {}
    for (x,y), native_color_pair in mask.items():
        xx, yy = x+8, y+20
        if 0 <= xx < 64 and 1 <= yy <= 62:
            predicted[(xx,yy)] = native_color_pair
    return predicted


def extract_stage(word, stage, record, frames):
    root=record["stage_root_index"]
    admitted, omissions=[], Counter()
    if root is None:
        return [], {"UNKNOWN_NO_WITNESSED_STAGE_ROOT":len(word)}
    for index, letter in enumerate(word):
        step=index+1
        action=int(letter)
        ordinal=word[:step].count("4")
        i=root+index
        transition_i=index + (PREFIX_STAGE1 if stage == 1 else 0)
        if len(frames)<=i+1 or len(record["transition_records"])<=transition_i:
            omissions["UNKNOWN_ORIGINAL_NATIVE_FRAME_UNAVAILABLE"]+=1
            continue
        t=record["transition_records"][transition_i]
        if t["action"]!=action or t["level"]!=stage:
            omissions["UNKNOWN_DIFFERENT_NATIVE_ACTION_OR_LEVEL"]+=1
            continue
        before,after=frames[i],frames[i+1]
        whole=changed_triplets(before,after)
        interior={p:c for p,c in whole.items() if 1<=p[1]<=62}
        boundary={p:c for p,c in whole.items() if p[1] in (0,63)}
        frozen=predeclared_interior_mask(stage,action,ordinal)
        absolute_step_baseline=predeclared_interior_mask(stage,action,step)
        always_stage1_baseline=predeclared_interior_mask(1,action,ordinal)
        controls={
            "STAGE_SPECIFIC_ORDINAL_MASK":frozen,
            "ABSOLUTE_WORD_STEP_MASK":absolute_step_baseline,
            "STAGE1_MASK_ALL_STAGES":always_stage1_baseline,
            "ZERO_NEGATIVE_CONTROL":{},
        }
        scores={name:score(predicted,interior)
                for name,predicted in controls.items()}
        admitted.append({
            "stage":stage,
            "word_step":step,
            "native_action":action,
            "native_ACTION4_ordinal":ordinal,
            "genuine_native_before_hash":t["before_hash"],
            "genuine_native_after_hash":t["after_hash"],
            "whole_native_color_change_count":len(whole),
            "actual_interior_native_pixel_color_changes":[
                {"xy":list(p),"from":v[0],"to":v[1]}
                for p,v in sorted(interior.items())],
            "separate_boundary_rows_native_pixel_color_changes":[
                {"xy":list(p),"from":v[0],"to":v[1]}
                for p,v in sorted(boundary.items())],
            "scores":scores,
        })
    return admitted,dict(omissions)


def tally(rows):
    stats={}
    for row in rows:
        for key,s in row["scores"].items():
            q=stats.setdefault(key,Counter())
            q["admitted"]+=1
            q["exact"]+=int(s["complete_exact_native_pixel_color_changes"])
            q["extra"]+=len(s["false_positive_native_changes"])
            q["missed"]+=len(s["missing_native_changes"])
            q["wrong_native_color"]+=len(s["same_position_but_different_native_colors"])
    return {k:dict(v) for k,v in stats.items()}


def transfer_evidence(rows0,rows1):
    idx0={row["word_step"]:row for row in rows0}
    idx1={row["word_step"]:row for row in rows1}
    out=[]
    for step in sorted(set(idx0) & set(idx1)):
        a,b=idx0[step],idx1[step]
        if a["native_action"] != 4 or b["native_action"] != 4:
            continue
        src={(r["xy"][0],r["xy"][1]):(r["from"],r["to"])
             for r in a["actual_interior_native_pixel_color_changes"]}
        dst={(r["xy"][0],r["xy"][1]):(r["from"],r["to"])
             for r in b["actual_interior_native_pixel_color_changes"]}
        if a["native_ACTION4_ordinal"] != b["native_ACTION4_ordinal"]:
            raise AssertionError("Native matched-word ACTION4 ordinals differ")
        # Source-based translation only within its predeclared both-stage
        # ordinal 1..6 domain. No source color changes in other bands.
        k=a["native_ACTION4_ordinal"]
        if k>6:
            continue
        translated=stage0_to_stage1_translation(src)
        out.append({
            "word_step":step,"ordinal":k,
            "stage0_real_source_change_count":len(src),
            "stage1_real_target_change_count":len(dst),
            "translation_xy":[8,20],
            "full_native_color_pair_score":score(translated,dst),
        })
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    experiments,raw=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            actual={},{}
            records={}
            frames={}
            observed={}
            omissions={}
            for stage in (0,1):
                records[stage], frames[stage]=steps_on_real_game(
                    arcade,word,stage,replicate)
                raw[f"{word}_{replicate}_stage{stage}"]=frames[stage]
                observed[stage],omissions[stage]=extract_stage(
                    word,stage,records[stage],frames[stage])
            paired=transfer_evidence(observed[0],observed[1])
            experiments.append({
                "word":word,"replicate":replicate,
                "original_native_records":records,
                "admitted_genuine_stage0_actions":observed[0],
                "admitted_genuine_stage1_actions":observed[1],
                "unknown_step_reasons":omissions,
                "paired_action4_stage_translation":paired,
                "real_native_actions":sum(x["real_native_actions"]
                                          for x in records.values()),
            })
    bystage={
        "stage0":tally([row for t in experiments for row in t["admitted_genuine_stage0_actions"]]),
        "stage1":tally([row for t in experiments for row in t["admitted_genuine_stage1_actions"]]),
    }
    transfers=[row for t in experiments for row in t["paired_action4_stage_translation"]]
    transfer_counts={
        "admitted":len(transfers),
        "exact":sum(int(r["full_native_color_pair_score"]["complete_exact_native_pixel_color_changes"])
                     for r in transfers),
        "extra":sum(len(r["full_native_color_pair_score"]["false_positive_native_changes"])
                    for r in transfers),
        "missed":sum(len(r["full_native_color_pair_score"]["missing_native_changes"])
                     for r in transfers),
        "wrong_native_color":sum(len(r["full_native_color_pair_score"]["same_position_but_different_native_colors"])
                               for r in transfers)
    }
    result={
        "kind":"SP80_NATIVE_STAGE0_STAGE1_INDEPENDENT_INTERIOR_COLOR_MASKS",
        "predeclared_original_words":WORDS,
        "reset_pairs_per_word":RESETS,
        "independent_native_resets":2*len(experiments),
        "real_native_actions":sum(t["real_native_actions"] for t in experiments),
        "stage_specific_model_scores":bystage,
        "stage0_to_stage1_translation":transfer_counts,
        "trials":experiments,
        "limits":"Exact predictions and stage transfer are limited to original visible pixel/color transitions y=1..62. Actual y0/y63 boundary changes are preserved separately in original JSON/NPZ. Unknown native transitions excluded, not scored. No F3 native action mapping, hidden-state mechanism, game policy or full game win."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_STAGE_MASK_HOLDOUT "+json.dumps(
        {k:v for k,v in result.items() if k!="trials"},sort_keys=True))
    if (not bystage["stage0"] or not bystage["stage1"]
            or transfer_counts["admitted"]==0):
        raise RuntimeError("Insufficient independent real native stage observations")


if __name__=="__main__":
    main()
