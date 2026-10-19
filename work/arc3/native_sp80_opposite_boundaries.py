"""Prospective original-native SP80 stage-specific *boundary* holdout.

Prior authentic stage-mask run #39213286441 discovered stage0 row0
right-edge native 14->0 contiguous 2/3 advances, versus stage1 row63
left-edge 14->0 contiguous 1/2 advances under actual ACTION4 and ACTION5.
This next independent sample freezes:
  * minimum first frontier cell (from PRE action frame only);
  * stage0 rightward boundary y0 advancing left by width in {2,3};
  * stage1 leftward boundary y63 advancing right by width in {1,2};
  * opposite boundary has no changed pixels;
  * previous stage-specific exact interior ordinal color mask unchanged.
No claim that a width *range* predicts which actual width occurs.
Compare exact full 64x64 predictions using fixed native widths and
interior-only, and retain every miss, additional observed cell, color and
interruption. No F3 source mapping, hidden mechanism, bot or solver.
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
from .native_sp80_boundary_prediction import score
from .native_sp80_stage_mask_holdout import predeclared_interior_mask

WORDS=(
    "44444444444444444444",
    "55554444444444444444",
    "44555544444444444444",
    "54544544544445444444",
    "44454555444445544444",
    "55555555554444444444",
)
RESETS=2
LEVEL1_PREFIX=6
assert len(WORDS)==len(set(WORDS))==6
assert all(len(w)==20 and set(w)<={"4","5"} for w in WORDS)


def native_boundary_before(stage, frame):
    """Return original pre-action frontier, or None for an empty boundary."""
    y=0 if stage==0 else 63
    xs=np.flatnonzero(frame[y]!=0)
    if len(xs)==0:
        return y,None,None
    x=int(xs[-1] if stage==0 else xs[0])
    return y,x,int(frame[y,x])


def frozen_frontier_mask(stage, before, width):
    """No after-frame reads. A failed original precondition is recorded."""
    y,x,color=native_boundary_before(stage,before)
    if x is None or color!=14:
        return {},{"precondition_admitted":False,"frontier_x":x,
                    "native_color":color,"boundary_y":y,
                    "reason":"NO_PRE_ACTION_NATIVE_14_FRONTIER"}
    candidates=[x-i for i in range(width)] if stage==0 else [x+i for i in range(width)]
    if any(a<0 or a>=64 or int(before[y,a])!=14 for a in candidates):
        return {},{"precondition_admitted":False,"frontier_x":x,
                    "native_color":color,"boundary_y":y,
                    "reason":"PRE_ACTION_14_CELLS_NOT_CONTIGUOUS_FOR_PROPOSED_WIDTH"}
    return {(p,y):(14,0) for p in candidates},{
        "precondition_admitted":True,"frontier_x":x,
        "native_color":color,"boundary_y":y,"predicted_width":width}


def observe_native_stage(stage, word, record, frames):
    root=record["stage_root_index"]
    rows,unknown=[],Counter()
    if root is None:
        return [],{"UNKNOWN_NO_ORIGINAL_STAGE_ROOT":len(word)}
    for index,letter in enumerate(word):
        step=index+1
        frame_index=root+index
        native_idx=index+(LEVEL1_PREFIX if stage==1 else 0)
        if (len(frames)<=frame_index+1 or
                len(record["transition_records"])<=native_idx):
            unknown["UNKNOWN_UNAVAILABLE_NATIVE_AFTER_FRAME"]+=1
            continue
        original_record=record["transition_records"][native_idx]
        if original_record["action"]!=int(letter) or original_record["level"]!=stage:
            unknown["UNKNOWN_STAGE_CHANGE_OR_ACTION_DIFFERENCE"]+=1
            continue
        pre,after=frames[frame_index],frames[frame_index+1]
        actual=changed_triplets(pre,after)
        ordinal=word[:step].count("4")
        interior=predeclared_interior_mask(stage,int(letter),ordinal)
        boundary_row=0 if stage==0 else 63
        opposite_row=63 if stage==0 else 0
        changed_boundary={p:cs for p,cs in actual.items() if p[1]==boundary_row}
        changed_opposite={p:cs for p,cs in actual.items() if p[1]==opposite_row}
        minimum,minimum_meta=frozen_frontier_mask(stage,pre,1)
        fixed_width=2 if stage==0 else 1
        other_width=3 if stage==0 else 2
        fixed,fixed_meta=frozen_frontier_mask(stage,pre,fixed_width)
        alternate,alt_meta=frozen_frontier_mask(stage,pre,other_width)
        models={
            "FROZEN_INTERIOR_PLUS_FIRST_FRONTIER":{**interior,**minimum},
            "FROZEN_INTERIOR_PLUS_FIXED_MIN_WIDTH":{**interior,**fixed},
            "FROZEN_INTERIOR_PLUS_FIXED_MAX_WIDTH":{**interior,**alternate},
            "FROZEN_INTERIOR_ONLY":interior,
            "ZERO_ALL_NATIVE_PIXELS_CONTROL":{},
        }
        predicted_scores={name:score(m,actual) for name,m in models.items()}
        changed_coords=sorted(p[0] for p in changed_boundary)
        y,x,color=native_boundary_before(stage,pre)
        candidate_region=(
            list(range(x-len(changed_coords)+1,x+1))
            if stage==0 and x is not None else
            list(range(x,x+len(changed_coords)))
            if stage==1 and x is not None else []
        )
        contiguous=bool(changed_coords) and changed_coords==candidate_region
        frontier_first_hit=bool(minimum) and all(
            changed_boundary.get(p)==cs for p,cs in minimum.items())
        correct_colors=all(cs==(14,0) for cs in changed_boundary.values())
        # Complete boundary-range claim is tested on every admitted original
        # native transition, including a failed precondition or zero width.
        lower,upper=(2,3) if stage==0 else (1,2)
        boundary_hypothesis_exact=bool(
            minimum_meta["precondition_admitted"] and
            lower<=len(changed_boundary)<=upper and
            contiguous and correct_colors and frontier_first_hit and
            not changed_opposite)
        rows.append({
            "native_stage":stage,"word_step":step,
            "native_action":int(letter),"native_ACTION4_ordinal":ordinal,
            "genuine_before_hash":original_record["before_hash"],
            "genuine_after_hash":original_record["after_hash"],
            "pre_action_frontier":minimum_meta,
            "fixed_width_precondition":fixed_meta,
            "alternate_width_precondition":alt_meta,
            "observed_boundary_width":len(changed_boundary),
            "boundary_stage_specific_direction_contiguous":contiguous,
            "boundary_stage_specific_original_color14_to0":correct_colors,
            "minimum_frontier_hit":bool(frontier_first_hit),
            "opposite_original_boundary_row_static":not bool(changed_opposite),
            "stage_boundary_width_range_and_direction_hypothesis":boundary_hypothesis_exact,
            "actual_native_boundary_changes":[
                {"xy":list(p),"from":cs[0],"to":cs[1]}
                for p,cs in sorted(changed_boundary.items())],
            "actual_opposite_native_row_changes":[
                {"xy":list(p),"from":cs[0],"to":cs[1]}
                for p,cs in sorted(changed_opposite.items())],
            "actual_full_native_changed_pixel_count":len(actual),
            "full_original_64x64_native_scores":predicted_scores,
        })
    return rows,dict(unknown)


def summarize(trials):
    result={}
    for stage in (0,1):
        c=Counter()
        model_counts={}
        exceptions=[]
        for t in trials:
            for row in t[f"admitted_stage{stage}_actions"]:
                c["admitted"]+=1
                c["ACTION"+str(row["native_action"])]+=1
                c["frontier_first_hit"]+=int(row["minimum_frontier_hit"])
                c["width_range_and_direction_exact"]+=int(row["stage_boundary_width_range_and_direction_hypothesis"])
                c["opposite_boundary_static"]+=int(row["opposite_original_boundary_row_static"])
                c["contiguous"]+=int(row["boundary_stage_specific_direction_contiguous"])
                c["width_"+str(row["observed_boundary_width"])]+=1
                if not row["stage_boundary_width_range_and_direction_hypothesis"]:
                    exceptions.append({"word":t["word"],"reset":t["replicate"],
                                       "step":row["word_step"],"action":row["native_action"],
                                       "frontier":row["pre_action_frontier"],
                                       "observed":row["actual_native_boundary_changes"],
                                       "opposite":row["actual_opposite_native_row_changes"]})
                for name,v in row["full_original_64x64_native_scores"].items():
                    m=model_counts.setdefault(name,Counter())
                    m["admitted"]+=1
                    m["exact_full_64x64"]+=int(v["complete_exact_native_pixel_color_changes"])
                    m["extra"]+=len(v["false_positive_native_changes"])
                    m["missed"]+=len(v["missing_native_changes"])
                    m["wrong_color"]+=len(v["same_position_but_different_native_colors"])
        result["stage"+str(stage)]={
            "native_boundary_admissions":dict(c),
            "frozen_full_64x64_models":{k:dict(v) for k,v in model_counts.items()},
            "boundary_counterexamples":exceptions,
        }
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    trials,raw=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            records,frames,rows,unknown={},{},{},{}
            for stage in (0,1):
                records[stage],frames[stage]=steps_on_real_game(
                    arcade,word,stage,replicate)
                raw[f"{word}_{replicate}_stage{stage}"]=frames[stage]
                rows[stage],unknown[stage]=observe_native_stage(
                    stage,word,records[stage],frames[stage])
            trials.append({
                "word":word,"replicate":replicate,
                "native_records":records,
                "admitted_stage0_actions":rows[0],
                "admitted_stage1_actions":rows[1],
                "unknown_native_actions_by_stage":unknown,
                "actual_native_actions":sum(x["real_native_actions"] for x in records.values()),
            })
    result={
        "kind":"SP80_PREDECLARED_OPPOSITE_NATIVE_BOUNDARY_FRONTS",
        "words_fixed_before_native_run":WORDS,
        "resets_per_word_per_stage":RESETS,
        "native_resets":len(trials)*2,
        "actual_native_actions":sum(t["actual_native_actions"] for t in trials),
        "frozen_hypothesis":"stage0 original y0 rightmost pre-action nonzero native14 clears contiguously 2 or3 x left; stage1 original y63 leftmost pre-action nonzero native14 clears contiguously 1 or2 x right; opposite boundary unchanged. Width exact unknown. Interior ordinal masks frozen.",
        "summary":summarize(trials),
        "trials":trials,
        "limits":"Observed original-stage visible native pixel/colors, NOT guaranteed exact frontier width, F3 source mapping, hidden mechanism or game win. Nonstandard native frames and changed levels are UNKNOWN.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_OPPOSITE_NATIVE_FRONTS "+json.dumps(
        {k:v for k,v in result.items() if k!="trials"},sort_keys=True))
    if not all(result["summary"]["stage"+str(s)]["native_boundary_admissions"].get("admitted",0)
               for s in (0,1)):
        raise RuntimeError("No original native evidence for one of the stages")


if __name__=="__main__":
    main()
