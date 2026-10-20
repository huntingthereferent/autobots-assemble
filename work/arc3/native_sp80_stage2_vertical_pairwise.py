"""Genuine original SP80 stage2 single-step vertical four-bar experiment.

Previous native source SDK studies: all four stage2 bars independently
selectable via coordinate ACTION6; genuine horizontal 4-bar pairwise
-1/0/+1 and larger inward 2..4 placements were source-level2 negatives.
No source level3 objective, laser physics, or vertical motion predicate
has been established. This NEW experiment prospectively freezes 27
balanced pairwise four-bar vertical offsets UP(-1), stationary(0),
DOWN(+1), plus nine independently fixed extrema and controls.

Use authentic original Arcade.NORMAL SDK games, source stage0->1 prefix,
and each of two independent actual stage1->2 success witnesses; no
fabricated scenes. Every clicked pixel/available control/native frame
is retained and source levels_completed>=3/WIN alone counts progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as original_native_trial

BARS=("U","M","L","B")
CLICKS={"U":"6@12,21","M":"6@44,29","L":"6@12,33","B":"6@40,41"}
ROOT={
    "U":(8,20,23,23),
    "M":(40,28,59,31),
    "L":(8,32,31,35),
    "B":(36,40,59,43),
}
VALUES=(-1,0,1)
MAIN=tuple((a,b,c,((a+1+b+1+c+1)%3)-1)
           for a,b,c in product(VALUES,repeat=3))
CONTROLS=(
    (-1,-1,-1,0),
    (0,0,0,0),
    (1,1,1,1),
    (-1,0,1,1),
    (1,0,-1,1),
    (0,-1,1,0),
    (0,1,-1,0),
    (1,-1,1,-1),
    (-1,1,-1,0),
)
OFFSETS=MAIN+CONTROLS

def word(offsets):
    steps=[]
    for bar,shift in zip(BARS,offsets):
        steps.append(CLICKS[bar])
        if shift<0:steps.extend(["1"]*abs(shift))
        if shift>0:steps.extend(["2"]*abs(shift))
    steps.append("5")
    return " ".join(steps)

def label(vals):
    return "U%s_M%s_L%s_B%s"%tuple(
      "N" if x==-1 else "Z" if x==0 else "P" for x in vals)
PROGRAMS=tuple((label(s),s,word(s)) for s in OFFSETS)
assert len(MAIN)==27 and len(CONTROLS)==9
assert len(OFFSETS)==len(set(OFFSETS))==36
assert len({n for n,_,_ in PROGRAMS})==36
assert len(STAGE1_WITNESSES)==2
for i in range(4):
    for j in range(i+1,4):
        assert set((s[i],s[j]) for s in MAIN)==set(product(VALUES,repeat=2))

def source_precommit(trial,raw,offsets):
    for e in trial["stage2_native_observations"]:
      if e["native_action"]!=5:continue
      step=e["phase_step"]
      if step==1:return {"admitted":False,"reason":"NO_SOURCE_PREVIOUS_NATIVE_ACTION"}
      actual=raw["stage2_"+str(step-1)][-1]
      matches={}; observed={}
      for bar,shift in zip(BARS,offsets):
          x0,y0,x1,y1=ROOT[bar]
          yy0=y0+4*shift; yy1=y1+4*shift
          patch=actual[yy0:yy1+1,x0:x1+1]
          # The original source selected/unselected-bar pixels are
          # recognized by actual palette, not predicted pixel synthesis.
          count=int(np.count_nonzero(np.isin(patch,[8,9])))
          expected=(x1-x0+1)*4
          observed[bar]={
             "native_expected_bbox":[x0,yy0,x1,yy1],
             "original_native_pixels_8_or9_in_expected_bbox":count,
             "actual_native_selected_color9_pixels":int(np.count_nonzero(patch==9)),
             "expected_native_rectangle_pixel_count":expected,
          }
          matches[bar]=count==expected
      return {
          "admitted":True,
          "sdk_level_before":e["source_SDK_level_before"],
          "sdk_level_after":e["source_SDK_level_after"],
          "sdk_original_state_after":e["source_SDK_state_after"],
          "original_returned_ACTION5_images":e.get(
             "full_original_SDK_frame_ledger",{}).get("true_original_returned_frames"),
          "native_original_precommit_source_patches":observed,
          "all_expected_native_vertical_bar_rectangles_observed":all(matches.values()),
      }
    return {"admitted":False,"reason":"UNKNOWN_NATIVE_ACTION5_NOT_REACHED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,source_arrays=[],{}
    for name,offsets,plan in PROGRAMS:
      for witness,witness_word in STAGE1_WITNESSES:
        row,arrays=original_native_trial(witness,witness_word,name,plan,0)
        row["predeclared_native_vertical_offsets"]=dict(zip(BARS,offsets))
        row["real_original_stage2_precommit"]=source_precommit(row,arrays,offsets)
        trials.append(row)
        for phase,stack in arrays.items():
            source_arrays[f"{name}_{witness}_rep0_{phase}"]=stack
    per={}
    for name,offsets,plan in PROGRAMS:
        group=[t for t in trials if t["frozen_level2_control"]==name]
        per[name]={
            "predeclared_original_bar_vertical_steps":dict(zip(BARS,offsets)),
            "native_stage2_action_plan":plan,
            "genuine_level2_source_witnesses":[t["witness"] for t in group],
            "actual_sdk_end_levels":[t["original_source_final_level"] for t in group],
            "actual_sdk_end_states":[t["original_source_final_state"] for t in group],
            "genuine_sdk_level3_or_WIN":[t["source_level3_or_WIN"] for t in group],
            "original_source_dispositions":[t["source_stage2_control_disposition"] for t in group],
            "source_precommit_native_bar_patches":[
                t["real_original_stage2_precommit"] for t in group],
            "source_stage2_actual_native_clicks":[[
                [e["native_click_xy"],e["original_native_preclick_color"]]
                for e in t["stage2_native_observations"] if e["native_action"]==6
            ] for t in group],
        }
    out={
       "kind":"ORIGINAL_SP80_GENUINE_STAGE2_FOUR_BAR_VERTICAL_PAIRWISE_NATIVE_ACTIONS",
       "prospectively_frozen_source_27_orthogonal_offset_cases":MAIN,
       "prospectively_frozen_9_vertical_controls":CONTROLS,
       "actual_native_four_bar_action_words":PROGRAMS,
       "true_source_stage2_entry_witnesses":STAGE1_WITNESSES,
       "original_genuine_independent_sdk_games":len(trials),
       "accepted_original_SDK_actions":sum(t["source_SDK_actions_accepted"] for t in trials),
       "original_stage2_native_coordinate_clicks":sum(int(e["native_action"]==6)
           for t in trials for e in t["stage2_native_observations"]),
       "actual_official_level3_or_WIN":sum(int(t["source_level3_or_WIN"]) for t in trials),
       "native_SDK_dispositions":dict(Counter(t["source_stage2_control_disposition"] for t in trials)),
       "native_original_source_expected_bars_admitted":sum(int(
           t["real_original_stage2_precommit"].get("all_expected_native_vertical_bar_rectangles_observed",False)) for t in trials),
       "genuine_source_per_program":per,
       "all_original_native_source_trial_records":trials,
       "limits":"Stage2 vertical control source experiment on genuine original Arcade.NORMAL SDK, no inferred hidden goal, engine physics or six-level WIN. Every ACTION6 coordinate native pixel and entire original obs.frame stack recorded. Real levels_completed>=3 or explicit WIN alone counts progression. Preserve original F3 mathematical referent and earlier source negatives.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_arrays)
    print("SP80_STAGE2_VERTICAL_PAIRWISE "+json.dumps({
       k:v for k,v in out.items()
       if k not in ("genuine_source_per_program","all_original_native_source_trial_records")
    },sort_keys=True))
    print("SP80_STAGE2_VERTICAL_ADVANCES "+json.dumps({
       name:{
           "offsets":v["predeclared_original_bar_vertical_steps"],
           "actual_levels":v["actual_sdk_end_levels"],
           "real_source_patches":v["source_precommit_native_bar_patches"]
       } for name,v in per.items() if any(v["genuine_sdk_level3_or_WIN"])
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*len(STAGE1_WITNESSES):
        raise RuntimeError("Missing true original independent SP80 game resets")
if __name__=="__main__":main()
