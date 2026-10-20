"""Authentic original SP80 stage2 corridor: four bars translated inward.

The first genuine stage2 four-bar source-native pairwise movement study
confirmed actual SDK selection, all requested positions and 0/72 level3
for (-1,0,+1) native horizontal steps. This independent frozen TEST
places two left-origin bars U/L right by 2/3/4 source ACTION4 steps and
two right-origin bars M/B left by 2/3/4 ACTION3 steps. These arrange
original bars in a shared horizontal corridor; this is an EXPERIMENTAL
geometric contrast, NOT a decoded game target, beam/physics hypothesis
or source-native win condition.

27 balanced pairwise combinations plus nine precommitted controls;
each program is executed on separate genuine original SDK resets
through independently verified stage0->1 and stage1->2 witnesses A/B.
Preserve every native returned 64x64 frame and source action/click
pixel/level evidence. Only actual levels_completed>=3 or WIN is progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as original_native_trial
from .native_sp80_stage2_fourbar_pairwise import (
    original_word,actual_bar_positions,source_stage2_commit,BARS
)

U=(2,3,4)
M=(-2,-3,-4)
LL=(2,3,4)
BOTTOM=(-2,-3,-4)
MAIN=tuple(
    (U[i],M[j],LL[k],BOTTOM[(i+j+k)%3])
    for i,j,k in product(range(3),repeat=3)
)
CONTROLS=(
    (2,-2,2,-3),
    (3,-3,3,-3),
    (4,-4,4,-4),
    (2,-4,4,-2),
    (4,-2,2,-3),
    (2,-3,4,-4),
    (4,-3,2,-3),
    (3,-2,4,-3),
    (3,-4,2,-3),
)
OFFSETS=MAIN+CONTROLS

def label(row):
    return "U%d_M%d_L%d_B%d"%tuple(row)

PROGRAMS=tuple((label(s),s,original_word(s)) for s in OFFSETS)
assert len(MAIN)==27 and len(CONTROLS)==9
assert len(OFFSETS)==len(set(OFFSETS))==36
assert len(PROGRAMS)==len({name for name,_,_ in PROGRAMS})==36
assert len(STAGE1_WITNESSES)==2
for a in range(4):
  for b in range(a+1,4):
    assert set((x[a],x[b]) for x in MAIN)==set(product(
       (U,M,LL,BOTTOM)[a],(U,M,LL,BOTTOM)[b]))

# All four source objects stay within 64×64 for the frozen bounds:
# upper 16×4 x8..23 => x16..39, middle20×4 x40..59 => x24..51,
# lower24×4 x8..31 => x16..47, bottom24×4 x36..59 => x20..51.
ROOT={
  "U":[8,20,23,23],
  "M":[40,28,59,31],
  "L":[8,32,31,35],
  "B":[36,40,59,43],
}

def verify_precommit(observation,steps):
    observed=observation.get("actual_source_pre_ACTION5_bar_positions")
    if observed is None:
        return {"admitted":False,"reason":"UNKNOWN_REAL_NATIVE_ACTION5_COMMIT_NOT_REACHED"}
    diffs={}
    for bar,delta in zip(BARS,steps):
       base=ROOT[bar]
       expected=[base[0]+4*delta,base[1],base[2]+4*delta,base[3]]
       actual=observed[bar]["actual_native_bbox"]
       diffs[bar]={
         "expected_source_visible_bar_bbox":expected,
         "observed_real_original_native_bbox":actual,
         "observed_matches_predeclared_displacement":bool(actual==expected),
       }
    return {
       "admitted":True,"native_actual_bar_verification":diffs,
       "all_actual_native_source_bar_bboxes_match":all(
           z["observed_matches_predeclared_displacement"] for z in diffs.values())
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows,frame_arrays=[],{}
    for name,offset,word in PROGRAMS:
      for witness,witness_word in STAGE1_WITNESSES:
        result,raw=original_native_trial(witness,witness_word,name,word,0)
        result["native_predeclared_4_bar_offsets"]=dict(zip(BARS,offset))
        result["stage2_SOURCE_ACTION5_precommit_observation"]=source_stage2_commit(result,raw)
        result["source_geometry_admission"]=verify_precommit(
           result["stage2_SOURCE_ACTION5_precommit_observation"],offset)
        rows.append(result)
        for phase,arr in raw.items():
           frame_arrays[f"{name}_{witness}_rep0_{phase}"]=arr

    by_program={}
    for name,steps,word in PROGRAMS:
        group=[x for x in rows if x["frozen_level2_control"]==name]
        by_program[name]={
           "original_frozen_bar_offsets":dict(zip(BARS,steps)),
           "original_source_stage2_program":word,
           "real_independent_entry_witnesses":[x["witness"] for x in group],
           "actual_source_levels":[x["original_source_final_level"] for x in group],
           "actual_source_states":[x["original_source_final_state"] for x in group],
           "genuine_level3_or_WIN":[x["source_level3_or_WIN"] for x in group],
           "true_native_dispositions":[x["source_stage2_control_disposition"] for x in group],
           "source_actual_precommit_bars":[
              x["source_geometry_admission"] for x in group],
           "native_ACTION5_actual_returned_frame_counts":[
              x["stage2_SOURCE_ACTION5_precommit_observation"].get(
                  "real_original_sdk_returned_frames") for x in group],
           "source_stage2_click_xy_colors":[[
              [ev["native_click_xy"],ev["original_native_preclick_color"]]
              for ev in x["stage2_native_observations"] if ev["native_action"]==6
           ] for x in group],
        }
    result={
       "kind":"GENUINE_ORIGINAL_SP80_STAGE2_INWARD_FOUR_BAR_CORRIDOR_SOURCE_SEARCH",
       "frozen_27_pairwise_source_offsets":MAIN,
       "frozen_9_additional_source_controls":CONTROLS,
       "true_original_source_stage2_words":PROGRAMS,
       "original_level1_to2_source_witnesses":STAGE1_WITNESSES,
       "genuine_fresh_original_SP80_resets":len(rows),
       "real_native_SDK_actions_accepted":sum(r["source_SDK_actions_accepted"] for r in rows),
       "native_stage2_real_coordinate_clicks":sum(int(e["native_action"]==6)
           for r in rows for e in r["stage2_native_observations"]),
       "source_true_level3_or_WIN":sum(int(r["source_level3_or_WIN"]) for r in rows),
       "true_original_SDK_dispositions":dict(Counter(r["source_stage2_control_disposition"] for r in rows)),
       "source_precommit_bboxes_match":sum(int(r["source_geometry_admission"].get(
           "all_actual_native_source_bar_bboxes_match",False)) for r in rows),
       "source_actual_per_program":by_program,
       "original_unfiltered_SDK_native_records":rows,
       "limitations":"Authentic Arcade.NORMAL source only. The central corridor is a prospectively chosen geometric contrast, NOT decoded source objective. Original SDK levels_completed>=3 or WIN alone establishes level3 progress; all original returned native frames preserved, correct source coordinate x/y clicks, previous mathematical F3 untouched.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frame_arrays)
    print("SP80_STAGE2_CENTRAL_CORRIDOR "+json.dumps({
      k:v for k,v in result.items()
      if k not in ("source_actual_per_program","original_unfiltered_SDK_native_records")
    },sort_keys=True))
    print("SP80_STAGE2_CENTRAL_CORRIDOR_ADVANCES "+json.dumps({
      name:{
        "bar_offsets":v["original_frozen_bar_offsets"],
        "original_levels":v["actual_source_levels"],
        "original_states":v["actual_source_states"],
        "precommit":v["source_actual_precommit_bars"],
      } for name,v in by_program.items() if any(v["genuine_level3_or_WIN"])
    },sort_keys=True))
    if len(rows)!=len(PROGRAMS)*len(STAGE1_WITNESSES):
       raise RuntimeError("Missing native source independent SP80 stage2 trials")

if __name__=="__main__":main()
